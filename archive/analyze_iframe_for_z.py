"""
分析iframe页面，查找z参数生成逻辑
关键发现：页面创建了iframe指向 z1.m1907.top，z参数可能在那里生成
"""

import asyncio
import json
import re
from typing import Dict, Optional
from playwright.async_api import async_playwright


async def analyze_iframe_page(video_url: str):
    """分析iframe页面，查找z参数生成逻辑"""
    print("=" * 60)
    print("分析iframe页面，查找z参数生成逻辑")
    print("=" * 60)
    
    # 关键发现：页面创建了iframe指向 z1.m1907.top
    iframe_url = f"https://z1.m1907.top/?jx={video_url}"
    
    print(f"\n🔍 关键发现:")
    print(f"   页面创建了iframe指向: {iframe_url}")
    print(f"   z参数很可能在这个iframe页面中生成！")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        )
        
        page = await context.new_page()
        
        # 存储捕获的数据
        api_calls = []
        scripts_content = []
        z_findings = []
        
        # Hook fetch来捕获API调用
        await page.add_init_script("""
            const originalFetch = window.fetch;
            window.fetch = function(...args) {
                const url = args[0];
                if (typeof url === 'string' && (url.includes('api/v') || url.includes('m1-a1.cloud'))) {
                    console.log('🔍 [Fetch] 捕获API调用:', url);
                    const zMatch = url.match(/[?&]z=([a-f0-9]{32})/);
                    if (zMatch) {
                        console.log('✅ z参数:', zMatch[1]);
                        // 获取调用栈
                        const stack = new Error().stack;
                        window._zParamCallStack = stack;
                        window._zParamValue = zMatch[1];
                    }
                }
                return originalFetch.apply(this, args);
            };
        """)
        
        # 监听网络请求
        async def handle_request(request):
            url = request.url
            if 'api/v' in url or 'm1-a1.cloud' in url:
                z_match = re.search(r'[?&]z=([a-f0-9]{32})', url)
                api_calls.append({
                    'url': url,
                    'method': request.method,
                    'z_param': z_match.group(1) if z_match else None,
                    'headers': dict(request.headers)
                })
                if z_match:
                    print(f"\n🔍 捕获API调用: {url}")
                    print(f"   ✅ z参数: {z_match.group(1)}")
        
        page.on('request', handle_request)
        
        print(f"\n[步骤1] 访问iframe页面...")
        print(f"   URL: {iframe_url}")
        
        await page.goto(iframe_url, wait_until='domcontentloaded', timeout=60000)
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
        
        # 提取所有脚本内容
        print(f"\n[步骤3] 提取并分析脚本...")
        
        scripts_data = await page.evaluate("""
            () => {
                return {
                    scripts: Array.from(document.querySelectorAll('script')).map((s, i) => ({
                        index: i,
                        src: s.src || null,
                        content: s.textContent || s.innerHTML || '',
                        length: (s.textContent || s.innerHTML || '').length
                    })),
                    zParamValue: window._zParamValue || null,
                    zParamCallStack: window._zParamCallStack || null,
                    allText: document.body ? document.body.innerText : ''
                };
            }
        """)
        
        scripts_content = scripts_data.get('scripts', [])
        z_param_value = scripts_data.get('zParamValue')
        z_param_call_stack = scripts_data.get('zParamCallStack')
        
        # 搜索z参数相关代码
        print(f"\n[步骤4] 搜索z参数生成逻辑...")
        
        # 搜索所有脚本
        for script in scripts_content:
            content = script.get('content', '')
            src = script.get('src', 'inline')
            
            if not content:
                continue
            
            # 搜索z参数相关模式
            patterns = [
                (r'[zZ]\s*[:=]\s*["\']([a-f0-9]{32})["\']', 'z参数直接赋值'),
                (r'(?:var|let|const)\s+[zZ]\s*=\s*["\']([a-f0-9]{32})["\']', 'z变量声明'),
                (r'[zZ]\s*[:=]\s*md5\s*\(([^)]+)\)', 'z参数MD5计算'),
                (r'[?&]z=([a-f0-9]{32})', 'URL中的z参数'),
                (r'["\'][^"\']*[?&]z=([a-f0-9]{32})[^"\']*["\']', '字符串中的z参数'),
            ]
            
            for pattern, description in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    z_value = match.group(1) if len(match.groups()) > 0 else None
                    line_num = content[:match.start()].count('\n') + 1
                    context_start = max(0, match.start() - 300)
                    context_end = min(len(content), match.end() + 300)
                    context = content[context_start:context_end]
                    
                    z_findings.append({
                        'type': description,
                        'script': src,
                        'z_value': z_value,
                        'line': line_num,
                        'match': match.group(0),
                        'context': context
                    })
        
        # 如果找到了z参数值，搜索该值
        if z_param_value:
            print(f"\n✅ 捕获到z参数值: {z_param_value}")
            
            for script in scripts_content:
                content = script.get('content', '')
                src = script.get('src', 'inline')
                
                if z_param_value in content:
                    pos = content.find(z_param_value)
                    line_num = content[:pos].count('\n') + 1
                    context_start = max(0, pos - 500)
                    context_end = min(len(content), pos + len(z_param_value) + 500)
                    context = content[context_start:context_end]
                    
                    z_findings.append({
                        'type': 'z参数值出现',
                        'script': src,
                        'z_value': z_param_value,
                        'line': line_num,
                        'context': context
                    })
        
        # 显示调用栈
        if z_param_call_stack:
            print(f"\n📋 z参数生成的调用栈:")
            stack_lines = z_param_call_stack.split('\n')[:15]
            for line in stack_lines:
                print(f"   {line}")
        
        # 保存结果
        output = {
            'video_url': video_url,
            'iframe_url': iframe_url,
            'z_param_value': z_param_value,
            'z_param_call_stack': z_param_call_stack,
            'api_calls': api_calls,
            'scripts': scripts_content,
            'z_findings': z_findings
        }
        
        output_file = 'iframe_z_param_analysis.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n✅ 分析完成")
        print(f"   💾 保存到: {output_file}")
        print(f"   📋 找到 {len(z_findings)} 处z参数相关代码")
        print(f"   📡 捕获 {len(api_calls)} 个API调用")
        
        # 显示关键发现
        if z_findings:
            print(f"\n🔍 关键发现:")
            for i, finding in enumerate(z_findings[:10], 1):
                print(f"\n[{i}] {finding.get('type')}")
                print(f"   脚本: {finding.get('script', 'N/A')}")
                if finding.get('z_value'):
                    print(f"   z值: {finding['z_value']}")
                print(f"   行号: {finding.get('line', 'N/A')}")
                print(f"   匹配: {finding.get('match', 'N/A')[:150]}...")
                print(f"   上下文: {finding['context'][:300]}...")
        
        # 提供建议
        print(f"\n💡 下一步:")
        print(f"   1. 查看 {output_file} 文件")
        print(f"   2. 重点关注找到的z参数生成代码")
        print(f"   3. 如果找到调用栈，查看调用栈中的函数")
        print(f"   4. 在浏览器中打开 {iframe_url}，使用开发者工具调试")
        
        # 保持浏览器打开
        print(f"\n⏸️ 浏览器将保持打开60秒，您可以手动检查...")
        await asyncio.sleep(60)
        
        await browser.close()
        
        return output


async def main():
    # 从捕获数据中读取
    try:
        with open('captured_api_params.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        captured_params = data.get('captured_params', [])
        if captured_params:
            video_url = captured_params[-1].get('jx')
        else:
            video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    except:
        video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    
    result = await analyze_iframe_page(video_url)
    
    if result:
        print("\n✅ 分析完成！")
        if result.get('z_param_value'):
            print(f"\n🎯 找到z参数: {result['z_param_value']}")
        if result.get('z_findings'):
            print(f"   找到 {len(result['z_findings'])} 处相关代码")


if __name__ == '__main__':
    asyncio.run(main())

