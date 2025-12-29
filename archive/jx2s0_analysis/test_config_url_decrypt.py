"""
测试 config.url 解密 - 在浏览器中实际测试
验证解密后的结果是否是m3u8链接
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


async def test_config_url_decrypt(page: Page, url: str) -> Optional[dict]:
    """测试config.url解密"""
    print(f"\n[步骤1] 访问analysis.php页面...")
    print(f"   URL: {url}")
    
    try:
        await page.goto(url, wait_until='domcontentloaded', timeout=90000)
        await asyncio.sleep(10)  # 等待JavaScript执行
        
        # 提取config对象
        print(f"\n[步骤2] 提取config对象...")
        config_info = await page.evaluate("""
            (function() {
                try {
                    if (typeof config !== 'undefined') {
                        return {
                            has_config: true,
                            config_url: config.url || null,
                            config_id: config.id || null,
                            config_api: config.api || null
                        };
                    }
                    return { has_config: false };
                } catch (e) {
                    return { has_config: false, error: e.toString() };
                }
            })();
        """)
        
        if not config_info.get('has_config'):
            print(f"   ❌ 未找到config对象")
            return None
        
        encrypted_url = config_info.get('config_url')
        config_id = config_info.get('config_id')
        
        if not encrypted_url:
            print(f"   ❌ config.url为空")
            return None
        
        print(f"   ✅ 找到config对象")
        print(f"   config.url长度: {len(encrypted_url) if encrypted_url else 0}")
        print(f"   config.id: {config_id}")
        
        # 提取YKQ.id
        print(f"\n[步骤3] 提取YKQ.id...")
        ykq_info = await page.evaluate("""
            (function() {
                try {
                    if (typeof YKQ !== 'undefined' && YKQ.id) {
                        return {
                            has_ykq: true,
                            ykq_id: YKQ.id
                        };
                    }
                    return { has_ykq: false };
                } catch (e) {
                    return { has_ykq: false, error: e.toString() };
                }
            })();
        """)
        
        if not ykq_info.get('has_ykq'):
            print(f"   ⚠️ 未找到YKQ.id")
            return None
        
        ykq_id = ykq_info.get('ykq_id')
        print(f"   ✅ YKQ.id: {ykq_id}")
        
        # 测试解密
        print(f"\n[步骤4] 测试解密config.url...")
        decrypt_result = await page.evaluate(f"""
            (function() {{
                const encrypted = {json.dumps(encrypted_url)};
                const key = {json.dumps(ykq_id)};
                
                try {{
                    // 确保rc4函数存在
                    if (typeof rc4 === 'undefined') {{
                        return {{
                            success: false,
                            error: 'rc4函数未定义'
                        }};
                    }}
                    
                    const decrypted = rc4(encrypted, key, 1);
                    
                    // 检查解密结果
                    const is_url = decrypted.startsWith('http');
                    const has_m3u8 = decrypted.includes('.m3u8');
                    const has_cachem3u8 = decrypted.includes('cachem3u8');
                    const has_cache = decrypted.includes('Cache');
                    const is_printable = /^[\\x20-\\x7E\\n\\r\\t]*$/.test(decrypted.substring(0, 200));
                    
                    // 检查是否是有效的URL格式
                    let is_valid_url = false;
                    try {{
                        if (is_url) {{
                            new URL(decrypted);
                            is_valid_url = true;
                        }}
                    }} catch (e) {{
                        is_valid_url = false;
                    }}
                    
                    return {{
                        success: true,
                        decrypted: decrypted,
                        length: decrypted.length,
                        is_url: is_url,
                        has_m3u8: has_m3u8,
                        has_cachem3u8: has_cachem3u8,
                        has_cache: has_cache,
                        is_printable: is_printable,
                        is_valid_url: is_valid_url,
                        preview: decrypted.substring(0, 500),
                        first_chars: Array.from(decrypted.substring(0, 100)).map(c => c.charCodeAt(0))
                    }};
                }} catch (e) {{
                    return {{
                        success: false,
                        error: e.toString()
                    }};
                }}
            }})();
        """)
        
        if decrypt_result.get('success'):
            decrypted = decrypt_result['decrypted']
            print(f"   ✅ 解密成功!")
            print(f"   解密后长度: {decrypt_result.get('length', 0)}")
            print(f"   是URL: {decrypt_result.get('is_url', False)}")
            print(f"   包含.m3u8: {decrypt_result.get('has_m3u8', False)}")
            print(f"   包含cachem3u8: {decrypt_result.get('has_cachem3u8', False)}")
            print(f"   包含Cache: {decrypt_result.get('has_cache', False)}")
            print(f"   可打印字符: {decrypt_result.get('is_printable', False)}")
            print(f"   有效URL: {decrypt_result.get('is_valid_url', False)}")
            print(f"\n   解密内容预览:")
            print(f"   {decrypt_result.get('preview', '')[:300]}")
            
            if decrypt_result.get('has_m3u8') or decrypt_result.get('has_cachem3u8'):
                print(f"\n   🎯 找到m3u8链接!")
                return {
                    'encrypted_url': encrypted_url,
                    'key': ykq_id,
                    'decrypted_url': decrypted,
                    'config_id': config_id,
                    'is_m3u8': True
                }
            elif decrypt_result.get('is_url'):
                print(f"\n   ⚠️ 解密结果是URL，但不是m3u8格式")
                return {
                    'encrypted_url': encrypted_url,
                    'key': ykq_id,
                    'decrypted_url': decrypted,
                    'config_id': config_id,
                    'is_m3u8': False
                }
            else:
                print(f"\n   ⚠️ 解密结果不是URL格式")
                print(f"   前100字符码: {decrypt_result.get('first_chars', [])[:50]}")
                return {
                    'encrypted_url': encrypted_url,
                    'key': ykq_id,
                    'decrypted_url': decrypted,
                    'config_id': config_id,
                    'is_m3u8': False,
                    'is_printable': decrypt_result.get('is_printable', False)
                }
        else:
            print(f"   ❌ 解密失败: {decrypt_result.get('error', '未知错误')}")
            return None
        
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """主函数"""
    print("=" * 60)
    print("测试 config.url 解密")
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
                result = await test_config_url_decrypt(page, analysis_url)
                
                if result:
                    print("\n" + "=" * 60)
                    print("📊 测试结果")
                    print("=" * 60)
                    print(f"\n🔑 密钥: {result.get('key', '')}")
                    print(f"\n📥 解密后的内容:")
                    decrypted = result.get('decrypted_url', '')
                    print(f"   长度: {len(decrypted)}")
                    print(f"   完整内容: {decrypted}")
                    
                    if result.get('is_m3u8'):
                        print(f"\n✅ 确认：config.url解密后是m3u8链接!")
                    else:
                        print(f"\n⚠️ 解密结果不是m3u8链接")
                        if not result.get('is_printable', True):
                            print(f"   解密结果是二进制数据，可能需要进一步处理")
                    
                    # 保存结果
                    with open('config_url_decrypt_result.json', 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
                    print(f"\n💾 结果已保存到: config_url_decrypt_result.json")
                else:
                    print("\n❌ 测试失败")
                
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

