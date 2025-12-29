"""
测试 jx.2s0.cn 解密逻辑
使用浏览器执行JavaScript来测试解密
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
            print("❌ 未找到Chrome浏览器，请手动指定chrome_path")
            return None, None, None
    
    debug_port = get_free_port()
    temp_user_data_dir = tempfile.mkdtemp(prefix="chrome_automation_")
    
    print(f"🚀 启动独立Chrome浏览器...")
    print(f"   调试端口: {debug_port}")
    
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
        
        print(f"⏳ 等待Chrome调试端口 {debug_port} 开放...")
        for i in range(30):
            try:
                s = socket.create_connection(('127.0.0.1', debug_port), timeout=1.0)
                s.close()
                print(f"✅ 端口 {debug_port} 已开放")
                return chrome_process, debug_port, temp_user_data_dir
            except Exception:
                if chrome_process.poll() is not None:
                    print("❌ Chrome进程已退出")
                    return None, None, None
                time.sleep(1)
        
        print(f"❌ 端口 {debug_port} 在30秒内未开放")
        chrome_process.terminate()
        return None, None, None
        
    except Exception as e:
        print(f"❌ 启动Chrome失败: {e}")
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
        const originalDebugger = window.debugger;
        window.debugger = function() {};
        console.debug = () => {};
    })();
    """
    await context.add_init_script(script=stealth_script)


async def test_decrypt_in_browser(page: Page, encrypted_url: str, config_id: str) -> Optional[dict]:
    """在浏览器中测试解密"""
    print(f"\n[步骤1] 加载7zl.js脚本...")
    
    try:
        # 读取7zl.js文件
        js_file_path = os.path.join(os.path.dirname(__file__), '7zl.js')
        if not os.path.exists(js_file_path):
            print(f"   ⚠️ 未找到7zl.js文件: {js_file_path}")
            return None
        
        with open(js_file_path, 'r', encoding='utf-8') as f:
            js_code = f.read()
        
        # 在页面中执行7zl.js
        await page.evaluate(js_code)
        print(f"   ✅ 7zl.js已加载")
        
        # 等待一下确保代码执行完成
        await asyncio.sleep(2)
        
        # 测试解密
        print(f"\n[步骤2] 测试解密...")
        print(f"   加密URL长度: {len(encrypted_url)}")
        print(f"   config.id: {config_id}")
        
        # 尝试多种可能的密钥
        possible_keys = [
            config_id,  # 直接使用id
            f"{config_id} P",  # id + " P"
            config_id.replace('-', ''),  # 去掉连字符
        ]
        
        decrypt_result = await page.evaluate(f"""
            (function() {{
                const encrypted_url = {json.dumps(encrypted_url)};
                const config_id = {json.dumps(config_id)};
                const possible_keys = {json.dumps(possible_keys)};
                
                const results = [];
                
                // 尝试每个可能的密钥
                for (const key of possible_keys) {{
                    try {{
                        // 调用rc4函数解密
                        const decrypted = rc4(encrypted_url, key, 1);
                        results.push({{
                            key: key,
                            success: true,
                            decrypted: decrypted,
                            is_url: decrypted.startsWith('http'),
                            has_m3u8: decrypted.includes('.m3u8')
                        }});
                    }} catch (e) {{
                        results.push({{
                            key: key,
                            success: false,
                            error: e.toString()
                        }});
                    }}
                }}
                
                return results;
            }})();
        """)
        
        print(f"\n   📊 解密测试结果:")
        for i, result in enumerate(decrypt_result, 1):
            print(f"\n   测试 {i}: 密钥 = '{result['key']}'")
            if result.get('success'):
                decrypted = result['decrypted']
                print(f"      ✅ 解密成功")
                print(f"      解密后长度: {len(decrypted)}")
                print(f"      是URL: {result.get('is_url', False)}")
                print(f"      包含m3u8: {result.get('has_m3u8', False)}")
                print(f"      解密内容预览: {decrypted[:200]}...")
                
                if result.get('is_url') or result.get('has_m3u8'):
                    print(f"\n      🎯 找到有效解密结果!")
                    return {
                        'key': result['key'],
                        'decrypted_url': decrypted
                    }
            else:
                print(f"      ❌ 解密失败: {result.get('error', '未知错误')}")
        
        # 如果上面的密钥都不行，尝试从YKQ对象获取
        print(f"\n[步骤3] 尝试从YKQ对象获取密钥...")
        
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
        
        if ykq_info.get('has_ykq'):
            ykq_id = ykq_info.get('ykq_id')
            print(f"   ✅ 找到YKQ.id: {ykq_id}")
            
            # 使用YKQ.id作为密钥测试
            decrypt_with_ykq = await page.evaluate(f"""
                (function() {{
                    const encrypted_url = {json.dumps(encrypted_url)};
                    const key = {json.dumps(ykq_id)};
                    
                    try {{
                        const decrypted = rc4(encrypted_url, key, 1);
                        return {{
                            success: true,
                            decrypted: decrypted,
                            is_url: decrypted.startsWith('http'),
                            has_m3u8: decrypted.includes('.m3u8')
                        }};
                    }} catch (e) {{
                        return {{
                            success: false,
                            error: e.toString()
                        }};
                    }}
                }})();
            """)
            
            if decrypt_with_ykq.get('success'):
                decrypted = decrypt_with_ykq['decrypted']
                print(f"   ✅ 使用YKQ.id解密成功!")
                print(f"   解密内容: {decrypted[:200]}...")
                return {
                    'key': ykq_id,
                    'decrypted_url': decrypted
                }
        
        return None
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_decrypt_from_analysis_page(page: Page, url: str) -> Optional[dict]:
    """从analysis.php页面测试解密"""
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
                            config_id: config.id || null
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
        
        if ykq_info.get('has_ykq'):
            ykq_id = ykq_info.get('ykq_id')
            print(f"   ✅ YKQ.id: {ykq_id}")
        else:
            print(f"   ⚠️ 未找到YKQ.id，使用config.id作为密钥")
            ykq_id = config_id
        
        # 测试解密
        print(f"\n[步骤4] 测试解密...")
        decrypt_result = await page.evaluate(f"""
            (function() {{
                const encrypted_url = {json.dumps(encrypted_url)};
                const key = {json.dumps(ykq_id)};
                
                try {{
                    // 确保rc4函数存在
                    if (typeof rc4 === 'undefined') {{
                        return {{
                            success: false,
                            error: 'rc4函数未定义'
                        }};
                    }}
                    
                    const decrypted = rc4(encrypted_url, key, 1);
                    return {{
                        success: true,
                        decrypted: decrypted,
                        is_url: decrypted.startsWith('http'),
                        has_m3u8: decrypted.includes('.m3u8'),
                        length: decrypted.length
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
            print(f"   密钥: {ykq_id}")
            print(f"   解密后长度: {decrypt_result.get('length', 0)}")
            print(f"   是URL: {decrypt_result.get('is_url', False)}")
            print(f"   包含m3u8: {decrypt_result.get('has_m3u8', False)}")
            print(f"   解密内容: {decrypted[:300]}...")
            
            return {
                'encrypted_url': encrypted_url,
                'key': ykq_id,
                'decrypted_url': decrypted,
                'config_id': config_id
            }
        else:
            print(f"   ❌ 解密失败: {decrypt_result.get('error', '未知错误')}")
            
            # 尝试其他可能的密钥
            print(f"\n[步骤5] 尝试其他可能的密钥...")
            alternative_keys = [
                config_id,
                f"{config_id} P",
                config_id.replace('-', ''),
            ]
            
            for alt_key in alternative_keys:
                if alt_key == ykq_id:
                    continue
                    
                alt_result = await page.evaluate(f"""
                    (function() {{
                        const encrypted_url = {json.dumps(encrypted_url)};
                        const key = {json.dumps(alt_key)};
                        
                        try {{
                            const decrypted = rc4(encrypted_url, key, 1);
                            return {{
                                success: true,
                                decrypted: decrypted,
                                is_url: decrypted.startsWith('http'),
                                has_m3u8: decrypted.includes('.m3u8')
                            }};
                        }} catch (e) {{
                            return {{
                                success: false,
                                error: e.toString()
                            }};
                        }}
                    }})();
                """)
                
                if alt_result.get('success'):
                    decrypted = alt_result['decrypted']
                    print(f"   ✅ 使用密钥 '{alt_key}' 解密成功!")
                    print(f"   解密内容: {decrypted[:300]}...")
                    return {
                        'encrypted_url': encrypted_url,
                        'key': alt_key,
                        'decrypted_url': decrypted,
                        'config_id': config_id
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
    print("测试 jx.2s0.cn 解密逻辑")
    print("=" * 60)
    
    # 从分析结果中读取数据
    try:
        with open('jx2s0_analysis_result.json', 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
        
        config_data = analysis_data.get('iframe_info', {}).get('config_data', {}).get('window.config', {})
        encrypted_url = config_data.get('url')
        config_id = None
        
        # 从full字段中提取id
        full_str = config_data.get('full', '')
        if full_str:
            try:
                import json as json_module
                full_obj = json_module.loads(full_str)
                config_id = full_obj.get('id')
            except:
                pass
        
        if not encrypted_url:
            print("❌ 未找到加密URL，请先运行 analyze_jx2s0_parser.py")
            return
        
        if not config_id:
            print("❌ 未找到config.id，尝试从URL中提取...")
            # 从分析结果中查找id
            dmku_url = None
            for item in analysis_data.get('network_info', {}).get('network_data', []):
                if 'dmku' in item.get('url', ''):
                    dmku_url = item.get('url', '')
                    break
            
            if dmku_url and 'id=' in dmku_url:
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(dmku_url)
                params = parse_qs(parsed.query)
                if 'id' in params:
                    config_id = params['id'][0].replace(' P', '').strip()
                    print(f"   ✅ 从dmku URL中提取到id: {config_id}")
        
        if not config_id:
            print("❌ 无法获取config.id")
            return
        
        print(f"\n📋 提取的数据:")
        print(f"   加密URL长度: {len(encrypted_url)}")
        print(f"   config.id: {config_id}")
        
    except FileNotFoundError:
        print("❌ 未找到分析结果文件，使用默认值测试...")
        # 使用从输出中看到的值
        encrypted_url = "O/zpjS4gC4ztyL9ve/+wx/3Lmpl7X/QAEOuqmTie93atrwDjwxRosEpoaXZw0TRD/AGtcvvIxMxgcxsQWcHumCqsvuIlf3lGXkqJgVWIsvPYgh8+Nsu4r36vZQ6fs/7edsA0WFSEDE16nQGeuSgCzC9HRMXafpabTanng2B2TaMPVJwkEAP24qZ8LdQvO/xA28+7iJ4Llj55cOlCqDSNg7g0Qvlc35/ngUrCRpXCxyQLod1GyL81cUTuDcOJTHe+cay4ZVB89fiZ48vYKwhA14o/IBdKo38EPHHj0XVLvf9VzCjgzdu8sBzAskD2i+923XStnQr8znCRh9bk+LR0sTvL69vQo8bTPLxHe2bqqyun0Qd0Qw=="
        config_id = "b664f44e3be2ad57fdb6"
    
    # 启动Chrome
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
                # 方法1: 直接访问analysis.php页面
                analysis_url = f"https://jx.2s0.cn/player/analysis.php?v=https://www.iqiyi.com/v_1c168e2yzbk.html"
                result = await test_decrypt_from_analysis_page(page, analysis_url)
                
                if result:
                    print("\n" + "=" * 60)
                    print("✅ 解密成功！")
                    print("=" * 60)
                    print(f"\n🔑 密钥: {result['key']}")
                    print(f"\n📥 解密后的URL:")
                    print(f"   {result['decrypted_url']}")
                    
                    # 保存结果
                    with open('jx2s0_decrypt_result.json', 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                    print(f"\n💾 结果已保存到: jx2s0_decrypt_result.json")
                else:
                    print("\n❌ 解密失败")
                    print("\n💡 建议:")
                    print("   1. 检查rc4函数是否正确加载")
                    print("   2. 检查密钥是否正确")
                    print("   3. 在浏览器控制台中手动测试")
                
                print(f"\n⏸️ 浏览器将保持打开10秒，您可以手动检查...")
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

