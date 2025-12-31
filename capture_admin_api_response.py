"""
专门捕获 /admin/api.php 的响应内容
用于分析 token 的生成方式
"""

import asyncio
import json
import subprocess
import tempfile
import socket
import time
import os
import shutil
from playwright.async_api import async_playwright
from urllib.parse import urlparse


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
            print("[ERROR] 未找到Chrome浏览器")
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
        shutil.rmtree(user_data_dir, ignore_errors=True)


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


async def capture_admin_api_response(video_url: str):
    """捕获 /admin/api.php 的响应内容"""
    print("=" * 60)
    print("捕获 /admin/api.php 响应内容")
    print("=" * 60)
    print(f"目标视频: {video_url}")
    
    chrome_process = None
    user_data_dir = None
    
    try:
        # 启动独立浏览器
        print(f"\n[步骤0] 启动独立Chrome浏览器...")
        chrome_process, debug_port, user_data_dir = launch_chrome()
        if not chrome_process or not debug_port:
            print("[ERROR] 启动独立Chrome浏览器失败")
            return None
        print(f"   [OK] Chrome浏览器已启动，调试端口: {debug_port}")
        
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{debug_port}")
            print(f"   [OK] 成功连接到Chrome浏览器")
            
            # 创建上下文
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='zh-CN',
            )
            
            # 添加反爬虫脚本
            await add_stealth_script(context)
            
            page = await context.new_page()
            
            # 存储API响应
            api_responses = []
            m3u8_urls = []
            
            # 监听响应
            async def handle_response(response):
                url = response.url
                
                # 特别关注 /admin/api.php
                if '/admin/api.php' in url:
                    try:
                        status = response.status
                        content_type = response.headers.get('content-type', '')
                        
                        print(f"\n[响应] /admin/api.php")
                        print(f"   URL: {url}")
                        print(f"   状态码: {status}")
                        print(f"   Content-Type: {content_type}")
                        
                        # 读取响应内容
                        try:
                            content = await response.text()
                            print(f"   响应长度: {len(content)} 字符")
                            
                            # 保存响应
                            response_data = {
                                'url': url,
                                'status': status,
                                'content_type': content_type,
                                'headers': dict(response.headers),
                                'content': content
                            }
                            api_responses.append(response_data)
                            
                            # 尝试解析JSON
                            if content.strip().startswith('{') or content.strip().startswith('['):
                                try:
                                    json_data = json.loads(content)
                                    print(f"   [OK] JSON解析成功")
                                    print(f"   JSON内容:")
                                    print(json.dumps(json_data, indent=4, ensure_ascii=False)[:500])
                                    response_data['json'] = json_data
                                except json.JSONDecodeError as e:
                                    print(f"   [WARN] JSON解析失败: {e}")
                            
                            # 显示内容预览
                            preview = content[:500].replace('\n', '\\n')
                            print(f"   内容预览: {preview}...")
                            
                        except Exception as e:
                            print(f"   [ERROR] 读取响应失败: {e}")
                            response_data = {
                                'url': url,
                                'status': status,
                                'content_type': content_type,
                                'error': str(e)
                            }
                            api_responses.append(response_data)
                    
                    except Exception as e:
                        print(f"   [ERROR] 处理响应失败: {e}")
                
                # 捕获 m3u8 URL
                if '.m3u8' in url:
                    m3u8_urls.append(url)
                    print(f"\n[发现] m3u8 URL: {url}")
            
            page.on('response', handle_response)
            
            # 访问解析网站
            parser_url = f"https://jx.2s0.cn/player/?url={video_url}"
            print(f"\n[步骤1] 访问解析网站...")
            print(f"   URL: {parser_url}")
            
            await page.goto(parser_url, wait_until='domcontentloaded', timeout=60000)
            print(f"   [OK] 页面加载完成")
            
            # 等待JavaScript执行和API调用
            print(f"\n[步骤2] 等待JavaScript执行和API调用...")
            await asyncio.sleep(15)
            
            # 尝试从页面中提取信息
            print(f"\n[步骤3] 提取页面信息...")
            try:
                # 检查是否有 ConFig 对象
                config = await page.evaluate("() => window.ConFig || null")
                if config:
                    print(f"   [OK] 找到 ConFig 对象")
                    print(f"   ConFig: {json.dumps(config, indent=4, ensure_ascii=False)[:500]}")
                
                # 检查是否有其他全局变量
                global_vars = await page.evaluate("""
                    () => {
                        return {
                            config: window.config || null,
                            apiUrl: window.apiUrl || null,
                            baseUrl: window.baseUrl || null
                        };
                    }
                """)
                if any(global_vars.values()):
                    print(f"   全局变量: {json.dumps(global_vars, indent=4, ensure_ascii=False)}")
            
            except Exception as e:
                print(f"   [WARN] 提取页面信息失败: {e}")
            
            # 等待更多API调用
            print(f"\n[步骤4] 继续等待API调用...")
            await asyncio.sleep(10)
            
            # 保存结果
            result = {
                'video_url': video_url,
                'parser_url': parser_url,
                'api_responses': api_responses,
                'm3u8_urls': list(set(m3u8_urls))
            }
            
            output_file = 'admin_api_response.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)
            print(f"\n[OK] 结果已保存到: {output_file}")
            
            # 打印总结
            print("\n" + "=" * 60)
            print("[总结]")
            print("=" * 60)
            
            if api_responses:
                print(f"\n[OK] 成功捕获 {len(api_responses)} 个 /admin/api.php 响应")
                for i, resp in enumerate(api_responses, 1):
                    print(f"\n[响应 {i}]")
                    print(f"   URL: {resp['url']}")
                    print(f"   状态码: {resp['status']}")
                    if 'json' in resp:
                        print(f"   JSON数据: {json.dumps(resp['json'], indent=4, ensure_ascii=False)[:300]}...")
                    elif 'content' in resp:
                        print(f"   内容: {resp['content'][:300]}...")
            else:
                print(f"\n[WARN] 未捕获到 /admin/api.php 响应")
                print(f"   可能的原因:")
                print(f"   1. API调用被拦截")
                print(f"   2. 需要更长的等待时间")
                print(f"   3. 需要手动操作页面")
            
            if m3u8_urls:
                print(f"\n[OK] 找到 {len(m3u8_urls)} 个m3u8链接:")
                for i, url in enumerate(m3u8_urls[:3], 1):
                    print(f"   [{i}] {url[:100]}...")
            
            # 保持浏览器打开一段时间
            print(f"\n[等待] 浏览器将保持打开20秒，您可以手动检查...")
            await asyncio.sleep(20)
            
            await context.close()
            await browser.close()
            
            return result
    
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
            cleanup_user_data(user_data_dir)


async def main():
    """主函数"""
    video_url = "https://v.youku.com/v_show/id_XMTA0MTc5NzI4.html"
    result = await capture_admin_api_response(video_url)
    
    if result and result.get('api_responses'):
        print("\n[成功] API响应已捕获！")
        print("\n[下一步]")
        print("   1. 查看 admin_api_response.json 文件")
        print("   2. 分析响应内容，查找 token 生成逻辑")
        print("   3. 检查响应中是否包含 m3u8 URL 或相关参数")
    else:
        print("\n[失败] 未能捕获API响应")
        print("   请检查网络连接和网站状态")


if __name__ == '__main__':
    asyncio.run(main())


