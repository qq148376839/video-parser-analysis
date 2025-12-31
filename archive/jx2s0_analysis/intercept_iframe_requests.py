"""
监听 iframe 中的所有网络请求，查找 token 获取接口
目标：找到 m3u8 URL 中 token 参数的来源
"""

import asyncio
import json
import subprocess
import tempfile
import socket
import time
import os
import re
from typing import Optional, Dict, List
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Frame
from urllib.parse import urlparse, parse_qs


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
    temp_user_data_dir = tempfile.mkdtemp(prefix="chrome_iframe_intercept_")
    
    print(f"🚀 启动独立Chrome浏览器...")
    print(f"   调试端口: {debug_port}")
    print(f"   临时目录: {temp_user_data_dir}")
    
    args = [
        chrome_path,
        f'--remote-debugging-port={debug_port}',
        f'--user-data-dir={temp_user_data_dir}',
        '--no-first-run',
        '--no-default-browser-check',
        '--disable-extensions',
        '--no-sandbox',
        '--disable-dev-shm-usage',
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
                    return None, None, None
                time.sleep(1)
        
        chrome_process.terminate()
        return None, None, None
    except Exception as e:
        print(f"❌ 启动Chrome失败: {e}")
        return None, None, None


def cleanup_user_data(user_data_dir):
    """清理临时用户数据目录"""
    if user_data_dir:
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


class IframeRequestInterceptor:
    """监听 iframe 中的所有网络请求"""
    
    def __init__(self):
        self.all_requests = []
        self.all_responses = []
        self.token_related_requests = []
        self.m3u8_requests = []
        self.api_requests = []
        self.frame_info = {}  # frame URL -> frame info
        
    def is_token_related(self, url: str, headers: dict = None, post_data: str = None, resource_type: str = None) -> bool:
        """判断请求是否与 token 相关"""
        url_lower = url.lower()
        
        # 排除静态资源
        if resource_type in ['image', 'stylesheet', 'font', 'media']:
            return False
        
        # 排除 playerapi 路径下的静态资源（这是路径名，不是真正的 API）
        if '/playerapi/' in url_lower and resource_type != 'xhr':
            return False
        
        # 检查 URL 中是否包含 token（真正的 token 参数）
        if 'token=' in url_lower or '?token' in url_lower or '&token' in url_lower:
            return True
        
        # 检查是否是真正的 API 请求（排除 playerapi 路径）
        api_patterns = ['/admin/api', '/api.php', '/api/', 'jiexi', 'parse', 'getm3u8', 'getvideo']
        if any(pattern in url_lower for pattern in api_patterns):
            # 确保不是 playerapi 路径
            if '/playerapi/' not in url_lower:
                return True
        
        # 检查请求头中是否有 token
        if headers:
            for key, value in headers.items():
                if 'token' in key.lower() or 'token' in str(value).lower():
                    return True
        
        # 检查 POST 数据中是否有 token
        if post_data:
            if 'token' in post_data.lower():
                return True
        
        return False
    
    def is_m3u8_related(self, url: str) -> bool:
        """判断请求是否与 m3u8 相关"""
        url_lower = url.lower()
        return '.m3u8' in url_lower or 'm3u8' in url_lower or 'cachem3u8' in url_lower
    
    async def setup_network_listeners(self, page: Page):
        """设置网络请求监听器（监听所有 frame）"""
        
        async def handle_request(request):
            """处理所有请求（包括主页面和所有 iframe）"""
            frame = request.frame
            frame_url = frame.url if frame else 'unknown'
            
            request_info = {
                'method': request.method,
                'url': request.url,
                'headers': request.headers,
                'post_data': request.post_data,
                'resource_type': request.resource_type,
                'frame_url': frame_url,
                'frame_name': frame.name if frame else 'main',
                'timestamp': time.time(),
                'request_id': id(request)
            }
            
            self.all_requests.append(request_info)
            
            # 记录 frame 信息
            if frame_url not in self.frame_info:
                self.frame_info[frame_url] = {
                    'url': frame_url,
                    'name': frame.name if frame else 'main',
                    'parent': frame.parent_frame.url if frame and frame.parent_frame else None,
                    'requests': []
                }
            self.frame_info[frame_url]['requests'].append(request_info)
            
            # 检查是否是 token 相关请求
            if self.is_token_related(request.url, request.headers, request.post_data, request.resource_type):
                self.token_related_requests.append(request_info)
                print(f"\n🔑 [TOKEN相关请求] {request.method} {request.url}")
                print(f"   Frame: {frame_url}")
                print(f"   资源类型: {request.resource_type}")
                if request.post_data:
                    print(f"   POST数据: {request.post_data[:500]}")
                # 只显示关键请求头
                if request.headers:
                    key_headers = {k: v for k, v in request.headers.items() 
                                 if k.lower() in ['x-requested-with', 'accept', 'content-type', 'authorization']}
                    if key_headers:
                        print(f"   关键请求头: {json.dumps(key_headers, indent=2, ensure_ascii=False)}")
            
            # 检查是否是 m3u8 相关请求
            if self.is_m3u8_related(request.url):
                self.m3u8_requests.append(request_info)
                print(f"\n🎬 [M3U8相关请求] {request.method} {request.url}")
                print(f"   Frame: {frame_url}")
            
            # 检查是否是真正的 API 请求（排除 playerapi 路径）
            url_lower = request.url.lower()
            if any(keyword in url_lower for keyword in ['/admin/api', '/api.php', 'jiexi', 'parse']) and '/playerapi/' not in url_lower:
                self.api_requests.append(request_info)
                print(f"\n📡 [API请求] {request.method} {request.url}")
                print(f"   Frame: {frame_url}")
                print(f"   资源类型: {request.resource_type}")
                if request.post_data:
                    print(f"   POST数据: {request.post_data[:500]}")
        
        async def handle_response(response):
            """处理所有响应（包括主页面和所有 iframe）"""
            frame = response.frame
            frame_url = frame.url if frame else 'unknown'
            
            response_info = {
                'status': response.status,
                'url': response.url,
                'headers': response.headers,
                'frame_url': frame_url,
                'frame_name': frame.name if frame else 'main',
                'timestamp': time.time(),
                'request_id': id(response.request) if response.request else None
            }
            
            self.all_responses.append(response_info)
            
            # 检查响应中是否包含 token 或 m3u8，或者是否是重要的 API 响应
            try:
                # 尝试获取响应文本（仅对文本类型）
                content_type = response.headers.get('content-type', '').lower()
                is_important_api = '/admin/api.php' in response.url.lower()
                
                if 'json' in content_type or 'text' in content_type or 'javascript' in content_type or is_important_api:
                    try:
                        text = await response.text()
                        response_info['response_text'] = text[:10000]  # 保存前10000字符
                        
                        # 检查是否包含 token 或 m3u8，或者是重要的 API
                        if 'token' in text.lower() or 'm3u8' in text.lower() or 'cachem3u8' in text.lower() or is_important_api:
                            if is_important_api:
                                print(f"\n📥 [重要API响应] {response.status} {response.url}")
                            else:
                                print(f"\n📥 [响应包含token/m3u8] {response.status} {response.url}")
                            print(f"   Frame: {frame_url}")
                            print(f"   Content-Type: {content_type}")
                            print(f"   内容预览: {text[:2000]}")
                            
                            # 如果是 JSON，尝试解析
                            if 'json' in content_type or is_important_api:
                                try:
                                    json_data = json.loads(text)
                                    print(f"   ✅ JSON解析成功:")
                                    print(f"   {json.dumps(json_data, indent=2, ensure_ascii=False)}")
                                    response_info['response_json'] = json_data
                                except Exception as e:
                                    if is_important_api:
                                        print(f"   ⚠️ JSON解析失败: {e}")
                                        print(f"   原始内容: {text[:2000]}")
                    except Exception as e:
                        if is_important_api:
                            print(f"\n❌ [重要API响应获取失败] {response.status} {response.url}")
                            print(f"   错误: {e}")
            except Exception as e:
                if '/admin/api.php' in response.url.lower():
                    print(f"\n❌ [重要API响应处理失败] {response.status} {response.url}")
                    print(f"   错误: {e}")
        
        # 监听所有请求和响应
        page.on('request', handle_request)
        page.on('response', handle_response)
        
        # 监听所有 frame 的请求和响应
        async def handle_frame_attached(frame: Frame):
            """当新的 frame 被附加时，也监听其请求"""
            print(f"\n📦 [新Frame] {frame.url}")
            frame.on('request', handle_request)
            frame.on('response', handle_response)
        
        page.on('frameattached', handle_frame_attached)
        
        # 对已存在的 frames 也设置监听
        for frame in page.frames:
            frame.on('request', handle_request)
            frame.on('response', handle_response)
    
    async def intercept_iframe_requests(self, parser_url: str, video_url: str):
        """监听 iframe 中的所有网络请求"""
        chrome_process = None
        user_data_dir = None
        
        try:
            # 启动独立浏览器
            chrome_process, debug_port, user_data_dir = launch_chrome()
            if not chrome_process:
                print("❌ 启动浏览器失败")
                return
            
            async with async_playwright() as p:
                # 连接到已启动的浏览器
                browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{debug_port}")
                
                # 创建上下文
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                )
                await add_stealth_script(context)
                
                page = await context.new_page()
                
                # 设置网络监听
                await self.setup_network_listeners(page)
                
                # 访问解析页面
                full_url = f"{parser_url}/player/?url={video_url}"
                print(f"\n🌐 访问页面: {full_url}")
                
                await page.goto(full_url, wait_until='domcontentloaded', timeout=60000)
                
                print(f"\n⏳ 等待页面加载和网络请求...")
                print(f"   等待时间: 30秒（请观察网络请求）")
                
                # 等待足够长的时间以捕获所有请求
                await asyncio.sleep(30)
                
                # 尝试等待所有 frame 加载完成
                print(f"\n📋 收集所有 frame 信息...")
                frames_info = []
                for frame in page.frames:
                    try:
                        frame_url = frame.url
                        frames_info.append({
                            'url': frame_url,
                            'name': frame.name,
                            'parent': frame.parent_frame.url if frame.parent_frame else None
                        })
                        print(f"   Frame: {frame_url}")
                    except:
                        pass
                
                # 打印统计信息
                print(f"\n" + "="*80)
                print(f"📊 网络请求统计")
                print(f"="*80)
                print(f"总请求数: {len(self.all_requests)}")
                print(f"Token相关请求: {len(self.token_related_requests)}")
                print(f"M3U8相关请求: {len(self.m3u8_requests)}")
                print(f"API请求: {len(self.api_requests)}")
                print(f"Frame数量: {len(self.frame_info)}")
                
                # 详细输出 token 相关请求
                if self.token_related_requests:
                    print(f"\n" + "="*80)
                    print(f"🔑 Token相关请求详情")
                    print(f"="*80)
                    for i, req in enumerate(self.token_related_requests, 1):
                        print(f"\n[{i}] {req['method']} {req['url']}")
                        print(f"    Frame: {req['frame_url']}")
                        print(f"    Frame名称: {req['frame_name']}")
                        if req['post_data']:
                            print(f"    POST数据: {req['post_data']}")
                        if req['headers']:
                            print(f"    请求头: {json.dumps(dict(req['headers']), indent=2, ensure_ascii=False)}")
                
                # 详细输出 m3u8 相关请求
                if self.m3u8_requests:
                    print(f"\n" + "="*80)
                    print(f"🎬 M3U8相关请求详情")
                    print(f"="*80)
                    for i, req in enumerate(self.m3u8_requests, 1):
                        print(f"\n[{i}] {req['method']} {req['url']}")
                        print(f"    Frame: {req['frame_url']}")
                        print(f"    Frame名称: {req['frame_name']}")
                        # 解析 URL 参数
                        parsed = urlparse(req['url'])
                        if parsed.query:
                            params = parse_qs(parsed.query)
                            if 'token' in params:
                                print(f"    Token参数: {params['token'][0][:100]}...")
                
                # 详细输出 API 请求
                if self.api_requests:
                    print(f"\n" + "="*80)
                    print(f"📡 API请求详情")
                    print(f"="*80)
                    for i, req in enumerate(self.api_requests, 1):
                        print(f"\n[{i}] {req['method']} {req['url']}")
                        print(f"    Frame: {req['frame_url']}")
                        print(f"    Frame名称: {req['frame_name']}")
                        if req['post_data']:
                            print(f"    POST数据: {req['post_data']}")
                        
                        # 查找对应的响应
                        req_id = req.get('request_id')
                        for resp in self.all_responses:
                            if resp.get('request_id') == req_id:
                                print(f"    ✅ 响应状态: {resp.get('status')}")
                                if 'response_json' in resp:
                                    print(f"    📦 JSON响应:")
                                    print(f"    {json.dumps(resp['response_json'], indent=4, ensure_ascii=False)}")
                                elif 'response_text' in resp:
                                    print(f"    📦 文本响应: {resp['response_text'][:500]}")
                                break
                
                # 保存结果到文件
                result_file = 'iframe_requests_intercept.json'
                # 提取重要 API 的响应
                important_responses = []
                for resp in self.all_responses:
                    if '/admin/api.php' in resp.get('url', '').lower():
                        important_responses.append(resp)
                
                result = {
                    'all_requests': self.all_requests,
                    'all_responses': self.all_responses,
                    'token_related_requests': self.token_related_requests,
                    'm3u8_requests': self.m3u8_requests,
                    'api_requests': self.api_requests,
                    'important_api_responses': important_responses,
                    'frame_info': self.frame_info,
                    'frames': frames_info
                }
                
                with open(result_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False, default=str)
                
                print(f"\n💾 结果已保存到: {result_file}")
                
                # 保持浏览器打开一段时间以便观察
                print(f"\n⏸️  浏览器将保持打开30秒，您可以手动检查...")
                await asyncio.sleep(30)
                
                await context.close()
                await browser.close()
        
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()
        
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


async def main():
    """主函数"""
    parser_url = "https://jx.2s0.cn"
    video_url = "https://www.iqiyi.com/v_19rr7qhfg0.html"  # 示例视频URL
    
    print("="*80)
    print("🔍 iframe 网络请求拦截器")
    print("="*80)
    print(f"解析网站: {parser_url}")
    print(f"视频URL: {video_url}")
    print("="*80)
    
    interceptor = IframeRequestInterceptor()
    await interceptor.intercept_iframe_requests(parser_url, video_url)


if __name__ == '__main__':
    asyncio.run(main())

