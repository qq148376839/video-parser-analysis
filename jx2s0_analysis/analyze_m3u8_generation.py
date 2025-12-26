"""
分析 m3u8 链接的生成方式
目标：找出 https://cachem3u8.2s0.cn:8899/Cache/Ff/{hash}.m3u8?token={token} 是如何生成的
"""

import asyncio
import json
import re
from typing import Optional, Dict, List
from playwright.async_api import async_playwright, Browser, BrowserContext, Page


class M3U8GenerationAnalyzer:
    """分析 m3u8 链接生成逻辑"""
    
    def __init__(self):
        self.network_requests = []
        self.network_responses = []
        self.m3u8_url = None
        self.api_calls = []
        
    async def setup_page(self, context: BrowserContext) -> Page:
        """设置页面和网络监听"""
        page = await context.new_page()
        
        # 监听所有网络请求
        async def handle_request(request):
            request_info = {
                'method': request.method,
                'url': request.url,
                'headers': request.headers,
                'post_data': request.post_data,
                'resource_type': request.resource_type,
                'timestamp': asyncio.get_event_loop().time()
            }
            self.network_requests.append(request_info)
            
            # 检查是否是API调用
            if 'api.php' in request.url or 'jiexi' in request.url or 'parse' in request.url:
                print(f"   🔍 API请求: {request.method} {request.url}")
                if request.post_data:
                    print(f"      POST数据: {request.post_data[:200]}")
                self.api_calls.append(request_info)
        
        async def handle_response(response):
            response_info = {
                'url': response.url,
                'status': response.status,
                'headers': response.headers,
                'timestamp': asyncio.get_event_loop().time()
            }
            self.network_responses.append(response_info)
            
            # 检查是否包含 m3u8
            if '.m3u8' in response.url or 'cachem3u8' in response.url:
                print(f"   ✅ 找到m3u8请求: {response.url}")
                self.m3u8_url = response.url
                
                # 尝试获取响应内容
                try:
                    content = await response.text()
                    if content.startswith('#EXTM3U'):
                        print(f"      ✅ 确认是m3u8文件")
                        print(f"      内容预览: {content[:300]}")
                except:
                    pass
            
            # 检查JSON响应
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    content = await response.text()
                    json_data = json.loads(content)
                    
                    # 检查是否包含 m3u8 或 video URL
                    content_str = json.dumps(json_data)
                    if '.m3u8' in content_str or 'cachem3u8' in content_str:
                        print(f"   ✅ JSON响应包含m3u8: {response.url}")
                        print(f"      内容: {json.dumps(json_data, indent=2, ensure_ascii=False)[:500]}")
                except:
                    pass
        
        page.on('request', handle_request)
        page.on('response', handle_response)
        
        return page
    
    async def analyze_m3u8_generation(self, video_url: str):
        """分析 m3u8 链接的生成方式"""
        print("=" * 60)
        print("分析 m3u8 链接生成方式")
        print("=" * 60)
        print(f"目标视频: {video_url}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            page = await self.setup_page(context)
            
            # 访问主页面
            main_url = f"https://jx.2s0.cn/player/?url={video_url}"
            print(f"\n[步骤1] 访问主页面...")
            print(f"   URL: {main_url}")
            
            await page.goto(main_url, wait_until='domcontentloaded', timeout=60000)
            await asyncio.sleep(3)
            
            # 等待iframe加载
            print(f"\n[步骤2] 等待iframe加载...")
            await asyncio.sleep(5)
            
            # 查找iframe
            iframe_element = await page.query_selector('iframe')
            if iframe_element:
                iframe_src = await iframe_element.get_attribute('src')
                print(f"   ✅ 找到iframe: {iframe_src}")
                
                # 获取iframe的frame对象
                iframe_frame = None
                for frame in page.frames:
                    if 'analysis.php' in frame.url:
                        iframe_frame = frame
                        break
                
                if iframe_frame:
                    print(f"\n[步骤3] 分析iframe中的JavaScript执行...")
                    
                    # 等待JavaScript执行
                    await asyncio.sleep(10)
                    
                    # 尝试在iframe中执行代码，监控关键对象
                    try:
                        # 监控 config 对象的变化
                        await iframe_frame.evaluate("""
                            (function() {
                                // 监控 config 对象
                                if (window.config) {
                                    console.log('config对象:', window.config);
                                }
                                
                                // 监控 YKQ 对象
                                if (window.YKQ) {
                                    console.log('YKQ对象:', window.YKQ);
                                    if (window.YKQ.id) {
                                        console.log('YKQ.id:', window.YKQ.id);
                                    }
                                }
                                
                                // 监控 player 对象
                                if (window.player) {
                                    console.log('player对象:', window.player);
                                }
                                
                                // 尝试拦截 XMLHttpRequest
                                const originalOpen = XMLHttpRequest.prototype.open;
                                const originalSend = XMLHttpRequest.prototype.send;
                                
                                XMLHttpRequest.prototype.open = function(method, url, ...args) {
                                    console.log('XHR请求:', method, url);
                                    if (url.includes('m3u8') || url.includes('cachem3u8')) {
                                        console.log('✅ 找到m3u8相关请求:', url);
                                    }
                                    return originalOpen.apply(this, [method, url, ...args]);
                                };
                                
                                XMLHttpRequest.prototype.send = function(...args) {
                                    this.addEventListener('load', function() {
                                        if (this.responseURL.includes('m3u8') || this.responseURL.includes('cachem3u8')) {
                                            console.log('✅ m3u8响应:', this.responseURL);
                                        }
                                    });
                                    return originalSend.apply(this, args);
                                };
                                
                                // 尝试拦截 fetch
                                const originalFetch = window.fetch;
                                window.fetch = function(...args) {
                                    const url = args[0];
                                    console.log('Fetch请求:', url);
                                    if (typeof url === 'string' && (url.includes('m3u8') || url.includes('cachem3u8'))) {
                                        console.log('✅ 找到m3u8相关Fetch请求:', url);
                                    }
                                    return originalFetch.apply(this, args);
                                };
                            })();
                        """)
                    except Exception as e:
                        print(f"   ⚠️ 执行监控代码失败: {e}")
                    
                    # 继续等待，让JavaScript执行
                    await asyncio.sleep(10)
                    
                    # 检查是否有m3u8链接生成
                    try:
                        # 检查页面中的video元素
                        video_src = await iframe_frame.evaluate("""
                            () => {
                                const videos = document.querySelectorAll('video');
                                if (videos.length > 0) {
                                    return videos[0].src || videos[0].currentSrc || '';
                                }
                                return '';
                            }
                        """)
                        
                        if video_src and '.m3u8' in video_src:
                            print(f"   ✅ 在video元素中找到m3u8: {video_src}")
                            self.m3u8_url = video_src
                        
                        # 检查window对象中的URL
                        window_urls = await iframe_frame.evaluate("""
                            () => {
                                const urls = [];
                                // 检查常见的对象
                                const objects = ['player', 'video', 'config', 'YKQ'];
                                objects.forEach(key => {
                                    try {
                                        const obj = window[key];
                                        if (obj && typeof obj === 'object') {
                                            const objStr = JSON.stringify(obj);
                                            if (objStr.includes('m3u8') || objStr.includes('cachem3u8')) {
                                                urls.push({key: key, data: objStr.substring(0, 500)});
                                            }
                                        }
                                    } catch (e) {}
                                });
                                return urls;
                            }
                        """)
                        
                        if window_urls:
                            print(f"   ✅ 在window对象中找到m3u8相关数据:")
                            for item in window_urls:
                                print(f"      {item['key']}: {item['data'][:200]}...")
                    
                    except Exception as e:
                        print(f"   ⚠️ 检查失败: {e}")
            
            # 等待更多网络请求
            print(f"\n[步骤4] 等待网络请求完成...")
            await asyncio.sleep(15)
            
            # 分析网络请求序列
            print(f"\n[步骤5] 分析网络请求序列...")
            print(f"   总请求数: {len(self.network_requests)}")
            print(f"   总响应数: {len(self.network_responses)}")
            print(f"   API调用数: {len(self.api_calls)}")
            
            # 找出 m3u8 请求之前的请求
            if self.m3u8_url:
                print(f"\n   ✅ 找到m3u8链接: {self.m3u8_url}")
                
                # 找出在m3u8请求之前的API调用
                m3u8_timestamp = None
                for resp in self.network_responses:
                    if resp['url'] == self.m3u8_url:
                        m3u8_timestamp = resp['timestamp']
                        break
                
                if m3u8_timestamp:
                    print(f"\n   📋 m3u8请求之前的API调用:")
                    for req in self.network_requests:
                        if req['timestamp'] < m3u8_timestamp:
                            if 'api.php' in req['url'] or 'jiexi' in req['url'] or 'parse' in req['url']:
                                print(f"      [{req['timestamp']:.2f}] {req['method']} {req['url']}")
                                if req.get('post_data'):
                                    print(f"         POST: {req['post_data'][:200]}")
            
            # 尝试提取m3u8链接的参数
            if self.m3u8_url:
                print(f"\n[步骤6] 分析m3u8链接结构...")
                # 解析URL
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(self.m3u8_url)
                print(f"   域名: {parsed.netloc}")
                print(f"   路径: {parsed.path}")
                print(f"   参数: {parsed.query}")
                
                # 提取hash和token
                path_parts = parsed.path.split('/')
                if len(path_parts) >= 3:
                    hash_value = path_parts[-1].replace('.m3u8', '')
                    print(f"   Hash: {hash_value}")
                
                query_params = parse_qs(parsed.query)
                if 'token' in query_params:
                    token = query_params['token'][0]
                    print(f"   Token: {token[:100]}...")
                    print(f"   Token长度: {len(token)}")
                    
                    # 分析token格式
                    if all(c in '0123456789abcdef' for c in token.lower()):
                        print(f"   Token格式: 十六进制字符串")
                    else:
                        print(f"   Token格式: 可能包含其他字符")
            
            # 保存分析结果
            result = {
                'video_url': video_url,
                'm3u8_url': self.m3u8_url,
                'api_calls': self.api_calls,
                'network_requests': self.network_requests[:50],  # 只保存前50个
                'network_responses': self.network_responses[:50],
            }
            
            with open('m3u8_generation_analysis.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"\n✅ 分析结果已保存到: m3u8_generation_analysis.json")
            
            # 保持浏览器打开以便检查
            print(f"\n⏸️ 浏览器将保持打开30秒，您可以手动检查...")
            await asyncio.sleep(30)
            
            await browser.close()


async def main():
    """主函数"""
    video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    
    analyzer = M3U8GenerationAnalyzer()
    await analyzer.analyze_m3u8_generation(video_url)


if __name__ == '__main__':
    asyncio.run(main())

