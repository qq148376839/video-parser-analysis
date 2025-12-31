#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用浏览器自动化分析付费key
因为config对象可能是JavaScript动态生成的，需要使用浏览器执行JavaScript
"""

import asyncio
import subprocess
import tempfile
import socket
import time
import os
import shutil
from playwright.async_api import async_playwright
import json
import re

def get_free_port():
    """获取一个未被占用的端口"""
    s = socket.socket()
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

def launch_chrome(chrome_path=None):
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
        'about:blank'
    ]
    
    chrome_process = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding='utf-8',
        errors='ignore'
    )
    
    # 等待浏览器启动
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

async def add_stealth_script(context):
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

async def analyze_paid_key_browser(uid, key, video_url):
    """使用浏览器自动化分析付费key"""
    print("="*80)
    print("使用浏览器自动化分析付费key")
    print("="*80)
    print(f"uid: {uid}")
    print(f"key: {key}")
    print(f"video_url: {video_url}")
    print()
    
    chrome_process = None
    user_data_dir = None
    
    try:
        # 启动独立浏览器
        print("步骤1: 启动Chrome浏览器...")
        chrome_process, debug_port, user_data_dir = launch_chrome()
        if not chrome_process:
            print("❌ 启动浏览器失败")
            return None
        
        print(f"✅ 浏览器已启动，调试端口: {debug_port}")
        print()
        
        # 连接到浏览器
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{debug_port}")
            
            # 创建上下文
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            )
            await add_stealth_script(context)
            
            page = await context.new_page()
            
            # 构建URL
            from urllib.parse import quote
            url = f"https://json.2s0.cn:5678/player/analysis.php/?uid={uid}&key={key}&url={quote(video_url)}"
            print(f"步骤2: 访问URL...")
            print(f"URL: {url}")
            print()
            
            # 监听网络请求
            m3u8_urls = []
            api_responses = []
            
            def handle_response(response):
                url = response.url
                if '.m3u8' in url or 'cachem3u8' in url:
                    m3u8_urls.append(url)
                    print(f"🎬 发现m3u8请求: {url}")
                if '/admin/api.php' in url:
                    try:
                        text = response.text()
                        api_responses.append({'url': url, 'text': text})
                        print(f"📡 API响应: {url}")
                    except:
                        pass
            
            page.on('response', handle_response)
            
            # 访问页面
            await page.goto(url, wait_until='domcontentloaded', timeout=60000)
            print("✅ 页面已加载")
            print()
            
            # 等待JavaScript执行
            print("步骤3: 等待JavaScript执行...")
            await asyncio.sleep(5)  # 等待5秒
            
            # 尝试提取config对象
            print("步骤4: 提取config对象...")
            try:
                config = await page.evaluate('''() => {
                    if (typeof config !== 'undefined') {
                        return {
                            url: config.url,
                            id: config.id,
                            api: config.api,
                            av: config.av
                        };
                    }
                    return null;
                }''')
                
                if config:
                    print("✅ 找到config对象:")
                    print(f"   config.url: {config.get('url', 'N/A')[:100]}...")
                    print(f"   config.id: {config.get('id', 'N/A')}")
                    print(f"   config.api: {config.get('api', 'N/A')}")
                    print(f"   config.av: {config.get('av', 'N/A')}")
                    print()
                    
                    # 保存结果
                    output_dir = os.path.dirname(os.path.abspath(__file__))
                    result_file = os.path.join(output_dir, 'paid_key_config.json')
                    with open(result_file, 'w', encoding='utf-8') as f:
                        json.dump(config, f, indent=2, ensure_ascii=False)
                    print(f"✅ Config已保存到: {result_file}")
                    print()
                    
                    # 对比免费版本
                    print("步骤5: 对比免费版本...")
                    free_config = {
                        'url': 'O/zpjS4gC4ztyL9ve/+wx/3Lmpl7X/QAEOuqmTie93atrwDjwxRosEpoaXZw0TRD/AGtcvvIxMxgcxsQWcHumCqsvuIlf3lGXkqJgVWIsvPYgh8+Nsu4r36vZQ6fs/7edsA0WFSEDE16mwOTvC8ByCxFQJXZcJaeTf7igGItTKkNAp5yEF325qV9KNQuP/wR3si83JgFlTJ5d+hDqD6PjLpnQa9dj5jhhU3CRZaUxnIK9d1Gy+UxI0HhDsyLRnS+c6C7NFAu8aOZ48zeKlJH14o6IB9Io39UOiPh13dLuq9QmSqwzty7th+dt0Pz3O5w3nOvyQn+yieU0tPg+eNwujrN79nX+8bTPr5FdGfgqCyn0wMhRA==',
                        'id': 'b664f44e3be2ad57fdb6'
                    }
                    
                    print("付费版本:")
                    print(f"  config.url: {config.get('url', 'N/A')[:100]}...")
                    print(f"  config.id: {config.get('id', 'N/A')}")
                    print()
                    
                    print("免费版本:")
                    print(f"  config.url: {free_config['url'][:100]}...")
                    print(f"  config.id: {free_config['id']}")
                    print()
                    
                    print("对比结果:")
                    if config.get('url') and config['url'] != free_config['url']:
                        print("  ✅ config.url 不同（可能基于uid/key生成）")
                    else:
                        print("  ⚠️ config.url 相同（可能不基于uid/key生成）")
                    
                    if config.get('id') and config['id'] != free_config['id']:
                        print("  ✅ config.id 不同（可能基于uid/key生成）")
                    else:
                        print("  ⚠️ config.id 相同（可能不基于uid/key生成）")
                    print()
                    
                    # 分析加密算法
                    print("步骤6: 分析加密算法...")
                    analyze_encryption_algorithm(uid, key, video_url, config)
                    
                    return config
                else:
                    print("❌ 未找到config对象")
                    print("   尝试从页面HTML中提取...")
                    
                    # 获取页面HTML
                    html = await page.content()
                    
                    # 查找config
                    config_pattern = r'var\s+config\s*=\s*({[^}]+})'
                    match = re.search(config_pattern, html, re.DOTALL)
                    if match:
                        print("✅ 在HTML中找到config对象")
                        config_str = match.group(1)
                        print(f"   {config_str[:200]}...")
                    else:
                        print("❌ HTML中也没有找到config对象")
                        print("   可能config是通过API动态获取的")
                    
                    # 保存HTML
                    output_dir = os.path.dirname(os.path.abspath(__file__))
                    html_file = os.path.join(output_dir, 'paid_key_analysis_browser.html')
                    with open(html_file, 'w', encoding='utf-8') as f:
                        f.write(html)
                    print(f"✅ HTML已保存到: {html_file}")
                    
            except Exception as e:
                print(f"❌ 提取config失败: {e}")
                import traceback
                traceback.print_exc()
            
            # 等待更多网络请求
            print()
            print("步骤7: 等待网络请求...")
            await asyncio.sleep(10)
            
            if m3u8_urls:
                print(f"✅ 发现 {len(m3u8_urls)} 个m3u8请求")
                for m3u8_url in m3u8_urls:
                    print(f"   {m3u8_url}")
            
            await context.close()
            await browser.close()
            
    finally:
        # 清理资源
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
            try:
                shutil.rmtree(user_data_dir, ignore_errors=True)
            except:
                pass
    
    print()
    print("="*80)
    print("分析完成！")
    print("="*80)

def analyze_encryption_algorithm(uid, key, video_url, config):
    """分析加密算法"""
    import base64
    import hashlib
    
    config_url = config.get('url')
    config_id = config.get('id')
    
    if not config_url:
        print("❌ 无法分析：缺少config.url")
        return
    
    print(f"输入参数:")
    print(f"  uid: {uid}")
    print(f"  key: {key}")
    print(f"  video_url: {video_url}")
    print()
    
    print(f"输出:")
    print(f"  config.url: {config_url[:100]}...")
    print(f"  config.id: {config_id}")
    print()
    
    # 分析config.url格式
    print("config.url格式分析:")
    print(f"  长度: {len(config_url)} 字符")
    
    # 检查是否是Base64
    try:
        decoded = base64.b64decode(config_url)
        print(f"  ✅ 是Base64编码")
        print(f"  解码后长度: {len(decoded)} 字节")
        print(f"  前20字节（十六进制）: {decoded[:20].hex()}")
    except:
        print(f"  ❌ 不是Base64编码")
    
    print()
    
    # 测试不同的加密算法
    print("测试不同的加密算法:")
    test_strings = [
        f"{uid}{key}{video_url}",
        f"{uid}{key}",
        f"{key}{video_url}",
        f"{uid}{video_url}",
    ]
    
    for test_str in test_strings:
        print(f"\n测试字符串: {test_str[:50]}...")
        
        # MD5
        md5_hash = hashlib.md5(test_str.encode()).hexdigest()
        print(f"  MD5: {md5_hash}")
        
        # SHA1
        sha1_hash = hashlib.sha1(test_str.encode()).hexdigest()
        print(f"  SHA1: {sha1_hash[:40]}...")
        
        # Base64
        b64_encoded = base64.b64encode(test_str.encode()).decode()
        print(f"  Base64: {b64_encoded[:50]}...")
        
        # 检查是否匹配config.url的开头
        if config_url.startswith(b64_encoded[:20]):
            print(f"  🎯 可能匹配！Base64编码的开头与config.url匹配")

def main():
    """主函数"""
    uid = "4059917"
    key = "cgklotuyDGHILOTW38"
    video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    
    asyncio.run(analyze_paid_key_browser(uid, key, video_url))

if __name__ == "__main__":
    main()

