"""
调试 jx.2s0.cn 解密逻辑 - 详细调试版本
检查每一步的处理过程
"""

import asyncio
import json
import subprocess
import tempfile
import socket
import time
import os
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page


def get_free_port():
    """获取一个未被占用的端口"""
    s = socket.socket()
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port


def launch_chrome(url="about:blank", chrome_path=None):
    """启动独立的Chrome浏览器实例"""
    if not chrome_path:
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                chrome_path = path
                break
        
        if not chrome_path:
            print("❌ 未找到Chrome浏览器")
            return None, None, None
    
    debug_port = get_free_port()
    temp_user_data_dir = tempfile.mkdtemp(prefix="chrome_automation_")
    
    args = [
        chrome_path,
        f'--remote-debugging-port={debug_port}',
        f'--user-data-dir={temp_user_data_dir}',
        '--no-first-run',
        '--no-default-browser-check',
        '--disable-extensions',
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-web-security',
        '--disable-site-isolation-trials',
        '--disable-features=BlockInsecurePrivateNetworkRequests',
        '--disable-blink-features=AutomationControlled',
        url
    ]
    
    try:
        chrome_process = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',
            errors='ignore'
        )
        
        for i in range(30):
            try:
                s = socket.create_connection(('127.0.0.1', debug_port), timeout=1.0)
                s.close()
                return chrome_process, debug_port, temp_user_data_dir
            except Exception:
                if chrome_process.poll() is not None:
                    return None, None, None
                time.sleep(1)
        
        chrome_process.terminate()
        return None, None, None
        
    except Exception as e:
        return None, None, None


def cleanup_user_data(user_data_dir):
    """删除临时用户数据目录"""
    if user_data_dir and os.path.exists(user_data_dir):
        import shutil
        shutil.rmtree(user_data_dir, ignore_errors=True)


async def add_stealth_script(context: BrowserContext):
    """添加反爬虫脚本"""
    stealth_script = """
    (function() {
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        delete navigator.__proto__.webdriver;
        Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
        Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en'] });
        window.chrome = { runtime: {}, loadTimes: function() {}, csi: function() {}, app: {} };
        window.debugger = function() {};
        console.debug = () => {};
    })();
    """
    await context.add_init_script(script=stealth_script)


async def debug_decrypt_process(page: Page, url: str) -> Optional[dict]:
    """详细调试解密过程"""
    print(f"\n[步骤1] 访问analysis.php页面...")
    
    try:
        await page.goto(url, wait_until='domcontentloaded', timeout=90000)
        await asyncio.sleep(10)
        
        # 提取所有相关信息
        print(f"\n[步骤2] 提取所有相关信息...")
        debug_info = await page.evaluate("""
            (function() {
                const info = {};
                
                // 提取config对象
                if (typeof config !== 'undefined') {
                    info.config = {
                        url: config.url || null,
                        id: config.id || null,
                        api: config.api || null,
                        av: config.av || null
                    };
                }
                
                // 提取YKQ对象
                if (typeof YKQ !== 'undefined') {
                    info.ykq = {
                        id: YKQ.id || null,
                        has_player: typeof YKQ.player !== 'undefined',
                        has_video: typeof YKQ.video !== 'undefined'
                    };
                }
                
                // 检查rc4函数
                info.has_rc4 = typeof rc4 !== 'undefined';
                
                return info;
            })();
        """)
        
        print(f"   ✅ 提取完成")
        print(f"   config.url长度: {len(debug_info.get('config', {}).get('url', '') or '')}")
        print(f"   config.id: {debug_info.get('config', {}).get('id', 'N/A')}")
        print(f"   YKQ.id: {debug_info.get('ykq', {}).get('id', 'N/A')}")
        print(f"   rc4函数存在: {debug_info.get('has_rc4', False)}")
        
        encrypted_url = debug_info.get('config', {}).get('url')
        config_id = debug_info.get('config', {}).get('id')
        ykq_id = debug_info.get('ykq', {}).get('id')
        
        if not encrypted_url:
            print(f"   ❌ 未找到加密URL")
            return None
        
        # 测试Base64解码
        print(f"\n[步骤3] 测试Base64解码...")
        base64_test = await page.evaluate(f"""
            (function() {{
                const encrypted = {json.dumps(encrypted_url)};
                try {{
                    const decoded = atob(encrypted);
                    return {{
                        success: true,
                        decoded_length: decoded.length,
                        decoded_preview: decoded.substring(0, 50),
                        first_bytes: Array.from(decoded.substring(0, 20)).map(c => c.charCodeAt(0))
                    }};
                }} catch (e) {{
                    return {{
                        success: false,
                        error: e.toString()
                    }};
                }}
            }})();
        """)
        
        if base64_test.get('success'):
            print(f"   ✅ Base64解码成功")
            print(f"   解码后长度: {base64_test.get('decoded_length', 0)}")
            print(f"   前50字符: {base64_test.get('decoded_preview', '')}")
            print(f"   前20字节: {base64_test.get('first_bytes', [])}")
        else:
            print(f"   ❌ Base64解码失败: {base64_test.get('error', '未知错误')}")
            return None
        
        # 测试RC4解密（使用不同的密钥）
        print(f"\n[步骤4] 测试RC4解密（多种密钥）...")
        
        test_keys = []
        if config_id:
            test_keys.append(('config.id', config_id))
        if ykq_id:
            test_keys.append(('YKQ.id', ykq_id))
        if config_id:
            test_keys.append(('config.id + " P"', f"{config_id} P"))
        
        decrypt_results = []
        for key_name, key_value in test_keys:
            print(f"\n   测试密钥: {key_name} = '{key_value}'")
            
            result = await page.evaluate(f"""
                (function() {{
                    const encrypted = {json.dumps(encrypted_url)};
                    const key = {json.dumps(key_value)};
                    
                    try {{
                        const decrypted = rc4(encrypted, key, 1);
                        
                        // 检查是否是有效的URL
                        const is_url = decrypted.startsWith('http');
                        const has_m3u8 = decrypted.includes('.m3u8');
                        const is_printable = /^[\\x20-\\x7E\\n\\r\\t]*$/.test(decrypted.substring(0, 100));
                        
                        return {{
                            success: true,
                            key: key,
                            decrypted: decrypted,
                            length: decrypted.length,
                            is_url: is_url,
                            has_m3u8: has_m3u8,
                            is_printable: is_printable,
                            preview: decrypted.substring(0, 200),
                            first_chars: Array.from(decrypted.substring(0, 50)).map(c => c.charCodeAt(0))
                        }};
                    }} catch (e) {{
                        return {{
                            success: false,
                            error: e.toString()
                        }};
                    }}
                }})();
            """)
            
            if result.get('success'):
                decrypted = result['decrypted']
                print(f"      ✅ 解密成功")
                print(f"      长度: {result.get('length', 0)}")
                print(f"      是URL: {result.get('is_url', False)}")
                print(f"      包含m3u8: {result.get('has_m3u8', False)}")
                print(f"      可打印字符: {result.get('is_printable', False)}")
                print(f"      前200字符: {result.get('preview', '')[:100]}...")
                print(f"      前50字符码: {result.get('first_chars', [])[:20]}")
                
                decrypt_results.append({
                    'key_name': key_name,
                    'key': key_value,
                    'result': result
                })
                
                # 如果解密结果是URL，直接返回
                if result.get('is_url') or result.get('has_m3u8'):
                    print(f"\n      🎯 找到有效解密结果!")
                    return {
                        'encrypted_url': encrypted_url,
                        'key': key_value,
                        'key_name': key_name,
                        'decrypted_url': decrypted,
                        'config_id': config_id,
                        'ykq_id': ykq_id
                    }
            else:
                print(f"      ❌ 解密失败: {result.get('error', '未知错误')}")
        
        # 如果所有密钥都解密成功但结果不是URL，返回第一个结果
        if decrypt_results:
            best_result = decrypt_results[0]
            print(f"\n   ⚠️ 所有解密结果都不是URL格式")
            print(f"   使用第一个结果: {best_result['key_name']}")
            return {
                'encrypted_url': encrypted_url,
                'key': best_result['key'],
                'key_name': best_result['key_name'],
                'decrypted_url': best_result['result']['decrypted'],
                'config_id': config_id,
                'ykq_id': ykq_id,
                'all_results': decrypt_results
            }
        
        return None
        
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """主函数"""
    print("=" * 60)
    print("调试 jx.2s0.cn 解密逻辑")
    print("=" * 60)
    
    analysis_url = "https://jx.2s0.cn/player/analysis.php?v=https://www.iqiyi.com/v_1c168e2yzbk.html"
    
    chrome_process, debug_port, user_data_dir = launch_chrome()
    if not chrome_process or not debug_port:
        print("\n❌ 启动Chrome浏览器失败")
        return
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{debug_port}")
            print(f"✅ 成功连接到Chrome浏览器")
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            )
            
            await add_stealth_script(context)
            page = await context.new_page()
            
            try:
                result = await debug_decrypt_process(page, analysis_url)
                
                if result:
                    print("\n" + "=" * 60)
                    print("📊 调试结果")
                    print("=" * 60)
                    print(f"\n🔑 使用的密钥: {result.get('key_name', 'unknown')} = '{result.get('key', '')}'")
                    print(f"\n📥 解密后的内容:")
                    decrypted = result.get('decrypted_url', '')
                    print(f"   长度: {len(decrypted)}")
                    print(f"   前300字符: {decrypted[:300]}")
                    
                    # 检查是否是二进制数据
                    try:
                        decrypted_bytes = decrypted.encode('latin1')
                        print(f"\n   二进制数据预览:")
                        print(f"   前50字节: {decrypted_bytes[:50]}")
                        print(f"   十六进制: {decrypted_bytes[:50].hex()}")
                    except:
                        pass
                    
                    # 保存结果
                    with open('jx2s0_debug_result.json', 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
                    print(f"\n💾 调试结果已保存到: jx2s0_debug_result.json")
                else:
                    print("\n❌ 解密失败")
                
                print(f"\n⏸️ 浏览器将保持打开10秒...")
                await asyncio.sleep(10)
                
            finally:
                await context.close()
                await browser.close()
                
    finally:
        if chrome_process:
            try:
                chrome_process.terminate()
                chrome_process.wait(timeout=5)
            except:
                try:
                    chrome_process.kill()
                except:
                    pass
        
        if user_data_dir:
            cleanup_user_data(user_data_dir)


if __name__ == '__main__':
    asyncio.run(main())

