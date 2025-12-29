"""
捕获 videocdn.ihelpy.net API参数
使用Playwright监听网络请求，捕获最新的z、s1ig、g参数
"""

import asyncio
import json
import re
from typing import Optional, Dict, List
from playwright.async_api import async_playwright, Browser, BrowserContext, Page


class ApiParamsCapturer:
    """API参数捕获器"""
    
    def __init__(self):
        self.api_calls = []
        self.captured_params = []
    
    async def setup_page(self, page: Page):
        """设置页面，监听网络请求"""
        print("🔧 设置网络请求监听...")
        
        async def handle_request(request):
            """处理请求"""
            url = request.url
            
            # 检查是否是API请求
            if 'api/v' in url or 'm1-a1.cloud' in url or 'm1-z2.cloud' in url:
                try:
                    url_obj = request.url
                    # 提取URL参数
                    if '?' in url_obj:
                        query_string = url_obj.split('?', 1)[1]
                        params = {}
                        for pair in query_string.split('&'):
                            if '=' in pair:
                                key, value = pair.split('=', 1)
                                params[key] = value
                        
                        call_info = {
                            'url': url_obj,
                            'method': request.method,
                            'headers': request.headers,
                            'params': params,
                            'timestamp': asyncio.get_event_loop().time()
                        }
                        
                        self.api_calls.append(call_info)
                        
                        print(f"\n🔍 [请求] 捕获API调用:")
                        print(f"   URL: {url_obj}")
                        print(f"   参数: {json.dumps(params, indent=6, ensure_ascii=False)}")
                        
                        # 提取关键参数
                        if 'z' in params or 's1ig' in params or 'g' in params:
                            self.captured_params.append({
                                'z': params.get('z'),
                                's1ig': params.get('s1ig'),
                                'g': params.get('g'),
                                'jx': params.get('jx'),
                                'url': url_obj,
                                'timestamp': call_info['timestamp']
                            })
                            print(f"   ✅ 捕获到关键参数:")
                            if params.get('z'):
                                print(f"      z: {params['z']}")
                            if params.get('s1ig'):
                                print(f"      s1ig: {params['s1ig']}")
                            if params.get('g'):
                                print(f"      g: {params['g']}")
                
                except Exception as e:
                    print(f"   ⚠️ 处理请求失败: {e}")
        
        async def handle_response(response):
            """处理响应"""
            url = response.url
            
            if 'api/v' in url or 'm1-a1.cloud' in url:
                try:
                    status = response.status
                    content_type = response.headers.get('content-type', '')
                    
                    print(f"\n📡 [响应] API响应:")
                    print(f"   URL: {url}")
                    print(f"   状态码: {status}")
                    print(f"   Content-Type: {content_type}")
                    
                    # 尝试读取响应内容
                    try:
                        content = await response.text()
                        print(f"   响应长度: {len(content)} 字符")
                        print(f"   内容预览: {content[:200]}")
                        
                        # 检查是否是错误信息
                        if '联系QQ' in content or '获取json版api地址' in content:
                            print(f"   ⚠️ 检测到错误信息，参数可能已过期")
                        elif content.strip().startswith('{') or content.strip().startswith('['):
                            print(f"   ✅ 响应是JSON格式")
                            try:
                                json_data = json.loads(content)
                                print(f"   ✅ JSON解析成功")
                                
                                # 检查是否包含m3u8链接
                                def find_m3u8(obj):
                                    m3u8_urls = []
                                    if isinstance(obj, dict):
                                        for v in obj.values():
                                            m3u8_urls.extend(find_m3u8(v))
                                    elif isinstance(obj, list):
                                        for item in obj:
                                            m3u8_urls.extend(find_m3u8(item))
                                    elif isinstance(obj, str):
                                        if '.m3u8' in obj and obj.startswith('http'):
                                            m3u8_urls.append(obj)
                                    return m3u8_urls
                                
                                m3u8_urls = find_m3u8(json_data)
                                if m3u8_urls:
                                    print(f"   ✅ 找到 {len(m3u8_urls)} 个m3u8链接:")
                                    for m3u8_url in m3u8_urls:
                                        print(f"      - {m3u8_url}")
                            except:
                                pass
                    except Exception as e:
                        print(f"   ⚠️ 读取响应失败: {e}")
                
                except Exception as e:
                    print(f"   ⚠️ 处理响应失败: {e}")
        
        page.on('request', handle_request)
        page.on('response', handle_response)
    
    async def inject_analysis_script(self, page: Page):
        """注入参数分析脚本"""
        print("🔧 注入参数分析脚本...")
        
        analysis_script = """
        (function() {
            'use strict';
            
            console.log('🔍 参数分析脚本已注入');
            
            // Hook fetch
            const originalFetch = window.fetch;
            window.fetch = function(...args) {
                const url = args[0];
                if (typeof url === 'string' && (url.includes('api/v') || url.includes('m1-a1.cloud'))) {
                    console.log('\\n🔍 [Fetch Hook] 捕获API调用:', url);
                    
                    // 提取参数
                    try {
                        const urlObj = new URL(url);
                        const params = Object.fromEntries(urlObj.searchParams);
                        console.log('   参数:', params);
                        
                        // 保存到window对象供Python读取
                        if (!window._capturedApiParams) {
                            window._capturedApiParams = [];
                        }
                        window._capturedApiParams.push({
                            url: url,
                            params: params,
                            timestamp: new Date().toISOString()
                        });
                    } catch (e) {
                        console.error('   解析URL失败:', e);
                    }
                }
                return originalFetch.apply(this, args);
            };
            
            // Hook XMLHttpRequest
            const originalXHROpen = XMLHttpRequest.prototype.open;
            XMLHttpRequest.prototype.open = function(method, url, ...args) {
                if (typeof url === 'string' && (url.includes('api/v') || url.includes('m1-a1.cloud'))) {
                    console.log('\\n🔍 [XHR Hook] 捕获API调用:', url);
                    
                    try {
                        const urlObj = new URL(url);
                        const params = Object.fromEntries(urlObj.searchParams);
                        console.log('   参数:', params);
                        
                        if (!window._capturedApiParams) {
                            window._capturedApiParams = [];
                        }
                        window._capturedApiParams.push({
                            url: url,
                            params: params,
                            timestamp: new Date().toISOString()
                        });
                    } catch (e) {
                        console.error('   解析URL失败:', e);
                    }
                }
                return originalXHROpen.apply(this, [method, url, ...args]);
            };
            
            // 禁用debugger
            const originalDebugger = window.debugger;
            window.debugger = function() {};
            
            // 覆盖Function.prototype.toString以绕过检测
            const originalToString = Function.prototype.toString;
            Function.prototype.toString = function() {
                if (this === originalDebugger || this === window.debugger) {
                    return 'function debugger() { [native code] }';
                }
                return originalToString.apply(this, arguments);
            };
            
            console.log('✅ 参数分析脚本已就绪');
        })();
        """
        
        await page.add_init_script(analysis_script)
    
    async def analyze_js_code(self, page: Page) -> Dict:
        """分析JavaScript代码，查找参数生成逻辑"""
        print("\n🔍 分析JavaScript代码...")
        
        try:
            # 获取所有script标签的内容
            scripts_info = await page.evaluate("""
                () => {
                    const scripts = [];
                    
                    // 外部脚本
                    document.querySelectorAll('script[src]').forEach(script => {
                        scripts.push({
                            type: 'external',
                            src: script.src,
                            content: null
                        });
                    });
                    
                    // 内联脚本
                    document.querySelectorAll('script:not([src])').forEach(script => {
                        scripts.push({
                            type: 'inline',
                            src: null,
                            content: script.textContent
                        });
                    });
                    
                    return scripts;
                }
            """)
            
            print(f"   📋 找到 {len(scripts_info)} 个script标签")
            
            # 分析内联脚本
            param_patterns = {
                'z': r'[zZ]\s*[:=]\s*["\']?([a-f0-9]{32})["\']?',
                's1ig': r's1ig\s*[:=]\s*["\']?(\d+)["\']?',
                'g': r'[gG]\s*[:=]\s*["\']?([a-z0-9]+\.[a-z0-9]+)["\']?',
                'md5': r'md5\s*\([^)]+\)',
                'hash': r'hash\s*\([^)]+\)',
                'encrypt': r'encrypt\s*\([^)]+\)',
            }
            
            found_patterns = {}
            
            for script in scripts_info:
                if script['type'] == 'inline' and script['content']:
                    content = script['content']
                    
                    for pattern_name, pattern in param_patterns.items():
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            if pattern_name not in found_patterns:
                                found_patterns[pattern_name] = []
                            found_patterns[pattern_name].extend(matches)
                            
                            # 显示上下文
                            for match in matches[:3]:  # 只显示前3个
                                match_pos = content.find(match)
                                if match_pos >= 0:
                                    context_start = max(0, match_pos - 100)
                                    context_end = min(len(content), match_pos + len(match) + 100)
                                    context = content[context_start:context_end]
                                    print(f"   ✅ 找到{pattern_name}模式: {match}")
                                    print(f"      上下文: {context[:200]}...")
            
            return found_patterns
        
        except Exception as e:
            print(f"   ⚠️ 分析JavaScript代码失败: {e}")
            return {}
    
    async def capture_params(self, video_url: str, headless: bool = False) -> Optional[Dict]:
        """捕获API参数"""
        print("=" * 60)
        print("捕获 videocdn.ihelpy.net API参数")
        print("=" * 60)
        print(f"目标视频: {video_url}")
        
        async with async_playwright() as p:
            # 启动浏览器
            browser = await p.chromium.launch(
                headless=headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                ]
            )
            
            # 创建上下文
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='zh-CN',
            )
            
            page = await context.new_page()
            
            # 注入分析脚本
            await self.inject_analysis_script(page)
            
            # 设置网络监听
            await self.setup_page(page)
            
            try:
                # 访问解析网站
                parser_url = f"https://videocdn.ihelpy.net/jiexi/m1907.html?m1907jx={video_url}"
                print(f"\n[步骤1] 访问解析网站...")
                print(f"   URL: {parser_url}")
                
                await page.goto(parser_url, wait_until='domcontentloaded', timeout=60000)
                print(f"   ✅ 页面加载完成")
                
                # 等待页面执行
                print(f"\n[步骤2] 等待JavaScript执行...")
                await asyncio.sleep(10)
                
                # 尝试触发视频加载（如果有播放按钮）
                try:
                    # 查找播放按钮或视频元素
                    play_button = await page.query_selector('button, .play-btn, [class*="play"], video')
                    if play_button:
                        print(f"   💡 找到播放元素，尝试点击...")
                        await play_button.click()
                        await asyncio.sleep(5)
                except:
                    pass
                
                # 等待网络请求
                print(f"\n[步骤3] 等待API调用...")
                await asyncio.sleep(15)
                
                # 从window对象获取捕获的参数
                try:
                    captured_from_js = await page.evaluate("() => window._capturedApiParams || []")
                    if captured_from_js:
                        print(f"   ✅ 从JavaScript中获取到 {len(captured_from_js)} 个API调用")
                        for call in captured_from_js:
                            self.captured_params.append({
                                'z': call.get('params', {}).get('z'),
                                's1ig': call.get('params', {}).get('s1ig'),
                                'g': call.get('params', {}).get('g'),
                                'jx': call.get('params', {}).get('jx'),
                                'url': call.get('url'),
                                'timestamp': call.get('timestamp')
                            })
                except Exception as e:
                    print(f"   ⚠️ 从JavaScript获取参数失败: {e}")
                
                # 分析JavaScript代码
                js_analysis = await self.analyze_js_code(page)
                
                # 汇总结果
                result = {
                    'video_url': video_url,
                    'api_calls': self.api_calls,
                    'captured_params': self.captured_params,
                    'js_analysis': js_analysis
                }
                
                # 保存结果
                with open('captured_api_params.json', 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False, default=str)
                print(f"\n✅ 捕获结果已保存到: captured_api_params.json")
                
                # 打印总结
                print("\n" + "=" * 60)
                print("📊 捕获总结")
                print("=" * 60)
                
                if self.captured_params:
                    print(f"\n✅ 成功捕获 {len(self.captured_params)} 组参数:")
                    for i, params in enumerate(self.captured_params, 1):
                        print(f"\n[组 {i}]")
                        if params.get('z'):
                            print(f"   z: {params['z']}")
                        if params.get('s1ig'):
                            print(f"   s1ig: {params['s1ig']}")
                        if params.get('g'):
                            print(f"   g: {params['g']}")
                        if params.get('jx'):
                            print(f"   jx: {params['jx']}")
                    
                    # 提取最新的参数
                    latest_params = self.captured_params[-1] if self.captured_params else {}
                    if latest_params.get('z') or latest_params.get('s1ig'):
                        print(f"\n💡 最新参数（可用于更新脚本）:")
                        print(f"   z = \"{latest_params.get('z', 'N/A')}\"")
                        print(f"   s1ig = \"{latest_params.get('s1ig', 'N/A')}\"")
                        print(f"   g = \"{latest_params.get('g', 'N/A')}\"")
                else:
                    print(f"\n⚠️ 未捕获到参数")
                    print(f"   💡 可能的原因:")
                    print(f"      1. 页面未触发API调用")
                    print(f"      2. API调用被拦截")
                    print(f"      3. 需要手动操作页面")
                    print(f"\n   💡 建议:")
                    print(f"      1. 在浏览器中手动访问页面")
                    print(f"      2. 使用Tampermonkey脚本捕获")
                    print(f"      3. 检查浏览器Console中的网络请求")
                
                if js_analysis:
                    print(f"\n🔍 JavaScript代码分析结果:")
                    for pattern_name, matches in js_analysis.items():
                        if matches:
                            print(f"   {pattern_name}: 找到 {len(matches)} 个匹配")
                
                # 如果headless=False，保持浏览器打开
                if not headless:
                    print(f"\n⏸️ 浏览器将保持打开30秒，您可以手动检查...")
                    await asyncio.sleep(30)
                
                await context.close()
                await browser.close()
                
                return result
            
            except Exception as e:
                print(f"\n❌ 捕获过程中发生错误: {e}")
                import traceback
                traceback.print_exc()
                await context.close()
                await browser.close()
                return None


async def main():
    """主函数"""
    video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    
    capturer = ApiParamsCapturer()
    result = await capturer.capture_params(video_url, headless=False)
    
    if result and result.get('captured_params'):
        print("\n✅ 参数捕获成功！")
        print("\n💡 下一步:")
        print("   1. 查看 captured_api_params.json 文件")
        print("   2. 使用最新的参数更新 direct_videocdn_parser_simple.py")
        print("   3. 重新运行解析器测试")
    else:
        print("\n⚠️ 参数捕获失败，请检查:")
        print("   1. 网络连接是否正常")
        print("   2. 解析网站是否可以访问")
        print("   3. 是否需要手动操作页面触发API调用")


if __name__ == '__main__':
    asyncio.run(main())

