"""
捕获运行时JavaScript代码
使用Playwright执行JavaScript，捕获z参数生成逻辑
"""

import asyncio
import json
import re
from playwright.async_api import async_playwright


async def capture_runtime_javascript(video_url: str):
    """捕获运行时执行的JavaScript代码"""
    print("=" * 60)
    print("捕获运行时JavaScript代码")
    print("=" * 60)
    
    parser_url = f"https://videocdn.ihelpy.net/jiexi/m1907.html?m1907jx={video_url}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        )
        
        page = await context.new_page()
        
        # 捕获所有执行的JavaScript代码
        executed_scripts = []
        api_calls = []
        
        # Hook console.log来捕获调试信息
        await page.evaluate("""
            const originalLog = console.log;
            console.log = function(...args) {
                originalLog.apply(console, args);
                window._capturedLogs = window._capturedLogs || [];
                window._capturedLogs.push(args.join(' '));
            };
        """)
        
        # 监听网络请求
        async def handle_request(request):
            url = request.url
            if 'api/v' in url or 'm1-a1.cloud' in url:
                api_calls.append({
                    'url': url,
                    'method': request.method,
                    'headers': dict(request.headers)
                })
                print(f"\n🔍 捕获API调用: {url}")
        
        page.on('request', handle_request)
        
        # 注入代码捕获脚本
        await page.add_init_script("""
            // 捕获所有函数定义
            window._capturedFunctions = {};
            
            // Hook Function构造函数
            const originalFunction = window.Function;
            window.Function = function(...args) {
                const func = originalFunction.apply(this, args);
                const funcStr = func.toString();
                if (funcStr.includes('z') || funcStr.includes('api') || funcStr.includes('fetch')) {
                    window._capturedFunctions[Date.now()] = funcStr;
                }
                return func;
            };
            
            // Hook eval
            const originalEval = window.eval;
            window.eval = function(code) {
                if (code.includes('z') || code.includes('api') || code.includes('fetch')) {
                    window._capturedFunctions['eval_' + Date.now()] = code;
                }
                return originalEval.apply(this, arguments);
            };
            
            // Hook fetch
            const originalFetch = window.fetch;
            window.fetch = function(...args) {
                const url = args[0];
                if (typeof url === 'string' && (url.includes('api/v') || url.includes('m1-a1.cloud'))) {
                    console.log('🔍 [Fetch] URL:', url);
                    // 获取调用栈
                    const stack = new Error().stack;
                    window._capturedFunctions['fetch_stack_' + Date.now()] = stack;
                }
                return originalFetch.apply(this, args);
            };
        """)
        
        print(f"\n[步骤1] 访问页面...")
        print(f"   URL: {parser_url}")
        
        await page.goto(parser_url, wait_until='domcontentloaded', timeout=60000)
        print(f"   ✅ 页面加载完成")
        
        # 等待JavaScript执行
        print(f"\n[步骤2] 等待JavaScript执行...")
        await asyncio.sleep(10)
        
        # 尝试触发视频加载
        try:
            play_button = await page.query_selector('button, .play-btn, [class*="play"], video')
            if play_button:
                await play_button.click()
                await asyncio.sleep(5)
        except:
            pass
        
        # 等待API调用
        await asyncio.sleep(10)
        
        # 提取捕获的信息
        print(f"\n[步骤3] 提取捕获的信息...")
        
        captured_data = await page.evaluate("""
            () => {
                return {
                    functions: window._capturedFunctions || {},
                    logs: window._capturedLogs || [],
                    scripts: Array.from(document.querySelectorAll('script')).map((s, i) => ({
                        index: i,
                        src: s.src || null,
                        content: s.textContent || s.innerHTML || '',
                        length: (s.textContent || s.innerHTML || '').length
                    }))
                };
            }
        """)
        
        # 查找z参数生成相关代码
        print(f"\n[步骤4] 分析代码...")
        
        findings = []
        
        # 分析捕获的函数
        for key, code in captured_data.get('functions', {}).items():
            if 'z' in code.lower() or 'api' in code.lower():
                findings.append({
                    'type': 'function',
                    'key': key,
                    'code': code[:1000],  # 限制长度
                    'full_code': code
                })
        
        # 分析script标签
        for script in captured_data.get('scripts', []):
            content = script.get('content', '')
            if 'z' in content.lower() or 'api' in content.lower():
                findings.append({
                    'type': 'script',
                    'index': script.get('index'),
                    'src': script.get('src'),
                    'code': content[:1000],
                    'full_code': content
                })
        
        # 保存结果
        output = {
            'video_url': video_url,
            'parser_url': parser_url,
            'api_calls': api_calls,
            'captured_functions': captured_data.get('functions', {}),
            'captured_logs': captured_data.get('logs', []),
            'scripts': captured_data.get('scripts', []),
            'findings': findings
        }
        
        with open('captured_runtime_js.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n✅ 捕获完成")
        print(f"   💾 保存到: captured_runtime_js.json")
        print(f"   📋 找到 {len(findings)} 处相关代码")
        print(f"   📡 捕获 {len(api_calls)} 个API调用")
        
        # 显示关键发现
        if findings:
            print(f"\n🔍 关键发现:")
            for i, finding in enumerate(findings[:5], 1):
                print(f"\n[{i}] {finding.get('type')}")
                if finding.get('src'):
                    print(f"   URL: {finding['src']}")
                print(f"   代码预览: {finding.get('code', '')[:200]}...")
        
        # 保持浏览器打开以便检查
        print(f"\n⏸️ 浏览器将保持打开30秒，您可以手动检查...")
        await asyncio.sleep(30)
        
        await browser.close()
        
        return output


async def main():
    video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    result = await capture_runtime_javascript(video_url)
    
    if result and result.get('findings'):
        print("\n💡 下一步:")
        print("   1. 查看 captured_runtime_js.json")
        print("   2. 分析找到的JavaScript代码")
        print("   3. 提取z参数生成逻辑")
        print("   4. 在Cloudflare Worker中实现")


if __name__ == '__main__':
    asyncio.run(main())

