"""
捕获iframe中的JavaScript代码
解析网站使用iframe加载实际解析逻辑
"""

import asyncio
import json
from playwright.async_api import async_playwright


async def capture_iframe_javascript(video_url: str):
    """捕获iframe中的JavaScript代码"""
    print("=" * 60)
    print("捕获iframe中的JavaScript代码")
    print("=" * 60)
    
    parser_url = f"https://videocdn.ihelpy.net/jiexi/m1907.html?m1907jx={video_url}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        )
        
        page = await context.new_page()
        
        # 捕获所有网络请求和响应
        network_data = []
        api_calls = []
        
        async def handle_response(response):
            url = response.url
            if 'api/v' in url or 'm1-a1.cloud' in url or 'm1-z2.cloud' in url:
                try:
                    content = await response.text()
                    network_data.append({
                        'url': url,
                        'status': response.status,
                        'headers': dict(response.headers),
                        'content': content[:5000]  # 限制长度
                    })
                    
                    # 提取URL参数
                    from urllib.parse import urlparse, parse_qs
                    parsed = urlparse(url)
                    params = parse_qs(parsed.query)
                    
                    api_calls.append({
                        'url': url,
                        'params': {k: v[0] if v else '' for k, v in params.items()}
                    })
                    
                    print(f"\n🔍 捕获API响应:")
                    print(f"   URL: {url}")
                    print(f"   参数: {params}")
                    if 'z' in params:
                        print(f"   ✅ z参数: {params['z'][0]}")
                except:
                    pass
        
        page.on('response', handle_response)
        
        # 注入代码捕获脚本
        await page.add_init_script("""
            // 捕获所有执行的代码
            window._capturedCode = {
                functions: {},
                variables: {},
                apiCalls: []
            };
            
            // Hook fetch
            const originalFetch = window.fetch;
            window.fetch = function(...args) {
                const url = args[0];
                if (typeof url === 'string' && (url.includes('api/v') || url.includes('m1-a1.cloud'))) {
                    window._capturedCode.apiCalls.push({
                        url: url,
                        stack: new Error().stack
                    });
                }
                return originalFetch.apply(this, args);
            };
        """)
        
        print(f"\n[步骤1] 访问主页面...")
        print(f"   URL: {parser_url}")
        
        await page.goto(parser_url, wait_until='domcontentloaded', timeout=60000)
        print(f"   ✅ 主页面加载完成")
        
        # 等待iframe加载
        print(f"\n[步骤2] 等待iframe加载...")
        await asyncio.sleep(5)
        
        # 查找iframe
        iframe_element = await page.query_selector('iframe')
        if iframe_element:
            iframe_src = await iframe_element.get_attribute('src')
            print(f"   ✅ 找到iframe: {iframe_src}")
            
            # 获取iframe的frame对象
            iframe_frame = await iframe_element.content_frame()
            
            if iframe_frame:
                print(f"\n[步骤3] 访问iframe内容...")
                
                # 等待iframe加载
                await iframe_frame.wait_for_load_state('networkidle', timeout=30000)
                await asyncio.sleep(5)
                
                # 在iframe中注入捕获脚本
                await iframe_frame.evaluate("""
                    // 捕获iframe中的代码
                    window._iframeCapturedCode = {
                        functions: {},
                        variables: {},
                        scripts: []
                    };
                    
                    // 捕获所有script标签
                    const scripts = document.querySelectorAll('script');
                    scripts.forEach((script, index) => {
                        window._iframeCapturedCode.scripts.push({
                            index: index,
                            src: script.src || null,
                            content: script.textContent || script.innerHTML || '',
                            length: (script.textContent || script.innerHTML || '').length
                        });
                    });
                    
                    // Hook fetch in iframe
                    const originalFetch = window.fetch;
                    window.fetch = function(...args) {
                        const url = args[0];
                        if (typeof url === 'string' && (url.includes('api/v') || url.includes('m1-a1.cloud'))) {
                            window._iframeCapturedCode.apiCalls = window._iframeCapturedCode.apiCalls || [];
                            window._iframeCapturedCode.apiCalls.push({
                                url: url,
                                stack: new Error().stack
                            });
                        }
                        return originalFetch.apply(this, args);
                    };
                """)
                
                # 等待API调用
                print(f"\n[步骤4] 等待API调用...")
                await asyncio.sleep(15)
                
                # 提取iframe中的代码
                iframe_code = await iframe_frame.evaluate("""
                    () => {
                        return {
                            url: window.location.href,
                            scripts: window._iframeCapturedCode?.scripts || [],
                            apiCalls: window._iframeCapturedCode?.apiCalls || [],
                            // 尝试提取所有全局变量
                            globals: Object.keys(window).filter(key => {
                                try {
                                    const value = window[key];
                                    return typeof value === 'string' || typeof value === 'number' || typeof value === 'function';
                                } catch {
                                    return false;
                                }
                            })
                        };
                    }
                """)
                
                print(f"   ✅ iframe URL: {iframe_code.get('url')}")
                print(f"   📋 iframe中有 {len(iframe_code.get('scripts', []))} 个script标签")
                
                # 保存iframe中的脚本内容
                iframe_scripts = []
                for script in iframe_code.get('scripts', []):
                    content = script.get('content', '')
                    if content:
                        iframe_scripts.append({
                            'index': script.get('index'),
                            'src': script.get('src'),
                            'content': content,
                            'length': len(content)
                        })
        
        # 等待更多API调用
        await asyncio.sleep(10)
        
        # 提取主页面捕获的信息
        main_page_code = await page.evaluate("""
            () => {
                return {
                    url: window.location.href,
                    scripts: Array.from(document.querySelectorAll('script')).map((s, i) => ({
                        index: i,
                        src: s.src || null,
                        content: s.textContent || s.innerHTML || '',
                        length: (s.textContent || s.innerHTML || '').length
                    })),
                    apiCalls: window._capturedCode?.apiCalls || []
                };
            }
        """)
        
        # 保存结果
        output = {
            'video_url': video_url,
            'main_page': {
                'url': parser_url,
                'scripts': main_page_code.get('scripts', []),
                'api_calls': main_page_code.get('apiCalls', [])
            },
            'iframe': {
                'url': iframe_code.get('url') if 'iframe_code' in locals() else None,
                'scripts': iframe_scripts if 'iframe_scripts' in locals() else [],
                'api_calls': iframe_code.get('apiCalls', []) if 'iframe_code' in locals() else []
            },
            'network_data': network_data,
            'api_calls': api_calls
        }
        
        with open('captured_iframe_js.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False, default=str)
        
        # 保存iframe中的脚本到单独文件
        import os
        os.makedirs('extracted_iframe_js', exist_ok=True)
        
        for i, script in enumerate(iframe_scripts if 'iframe_scripts' in locals() else []):
            filename = f'iframe_script_{i}.js'
            if script.get('src'):
                filename = script['src'].split('/')[-1] or filename
            with open(f'extracted_iframe_js/{filename}', 'w', encoding='utf-8') as f:
                f.write(script.get('content', ''))
            print(f"   💾 保存iframe脚本: extracted_iframe_js/{filename}")
        
        print(f"\n✅ 捕获完成")
        print(f"   💾 保存到: captured_iframe_js.json")
        print(f"   📋 主页面: {len(main_page_code.get('scripts', []))} 个脚本")
        print(f"   📋 iframe: {len(iframe_scripts if 'iframe_scripts' in locals() else [])} 个脚本")
        print(f"   📡 捕获 {len(api_calls)} 个API调用")
        
        # 显示z参数
        if api_calls:
            print(f"\n🔍 捕获的z参数:")
            for call in api_calls:
                if 'z' in call.get('params', {}):
                    print(f"   z: {call['params']['z']}")
        
        print(f"\n⏸️ 浏览器将保持打开30秒，您可以手动检查...")
        await asyncio.sleep(30)
        
        await browser.close()
        
        return output


async def main():
    video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    result = await capture_iframe_javascript(video_url)
    
    if result:
        print("\n💡 下一步:")
        print("   1. 查看 captured_iframe_js.json")
        print("   2. 查看 extracted_iframe_js/ 目录中的JavaScript文件")
        print("   3. 分析z参数生成逻辑")
        print("   4. 在Cloudflare Worker中实现")


if __name__ == '__main__':
    asyncio.run(main())

