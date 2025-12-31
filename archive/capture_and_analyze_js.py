"""
捕获并分析JavaScript代码，查找z参数生成逻辑
增强版：捕获运行时JS代码，分析z参数生成
"""

import asyncio
import json
import re
import hashlib
from typing import Dict, List, Optional
from playwright.async_api import async_playwright


class ZParamAnalyzer:
    """z参数分析器"""
    
    def __init__(self, captured_z: str = None, video_url: str = None):
        self.captured_z = captured_z
        self.video_url = video_url
        self.findings = []
    
    def search_z_in_code(self, code: str, file_info: Dict = None) -> List[Dict]:
        """在代码中搜索z参数相关逻辑"""
        findings = []
        
        if not code:
            return findings
        
        # 模式1: z参数赋值（各种格式）
        z_patterns = [
            # z = "xxx" 或 z: "xxx"
            (r'[zZ]\s*[:=]\s*["\']([a-f0-9]{32})["\']', 'z参数直接赋值'),
            # var/let/const z = ...
            (r'(?:var|let|const)\s+[zZ]\s*=\s*([^;]+)', 'z变量声明'),
            # z = md5(...)
            (r'[zZ]\s*[:=]\s*md5\s*\(([^)]+)\)', 'z参数MD5计算'),
            # z = hash(...)
            (r'[zZ]\s*[:=]\s*hash\s*\(([^)]+)\)', 'z参数哈希计算'),
            # z = xxx.md5()
            (r'[zZ]\s*[:=]\s*([^=]+)\.md5\s*\([^)]*\)', 'z参数MD5方法调用'),
            # z = function(...)
            (r'[zZ]\s*[:=]\s*function\s*\([^)]*\)\s*\{', 'z参数函数定义'),
            # URL中的z参数
            (r'[?&]z=([a-f0-9]{32})', 'URL中的z参数'),
            # API调用
            (r'(?:fetch|XMLHttpRequest|ajax)\s*\([^)]*z[=:]([a-f0-9]{32})', 'HTTP请求中的z参数'),
        ]
        
        for pattern, description in z_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                context_start = max(0, match.start() - 300)
                context_end = min(len(code), match.end() + 300)
                context = code[context_start:context_end]
                
                findings.append({
                    'type': description,
                    'pattern': pattern,
                    'match': match.group(0),
                    'line': line_num,
                    'context': self._clean_context(context),
                    'file': file_info
                })
        
        # 模式2: 如果提供了捕获的z值，搜索该值
        if self.captured_z and self.captured_z in code:
            positions = []
            start = 0
            while True:
                pos = code.find(self.captured_z, start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1
            
            for pos in positions[:3]:  # 只取前3个
                line_num = code[:pos].count('\n') + 1
                context_start = max(0, pos - 500)
                context_end = min(len(code), pos + len(self.captured_z) + 500)
                context = code[context_start:context_end]
                
                findings.append({
                    'type': 'z参数值出现',
                    'pattern': 'exact_match',
                    'match': self.captured_z,
                    'line': line_num,
                    'context': self._clean_context(context),
                    'file': file_info
                })
        
        # 模式3: MD5函数定义
        md5_patterns = [
            r'function\s+md5\s*\([^)]*\)\s*\{[\s\S]{0,1000}\}',
            r'const\s+md5\s*=\s*function\s*\([^)]*\)\s*\{[\s\S]{0,1000}\}',
            r'const\s+md5\s*=\s*\([^)]*\)\s*=>\s*\{[\s\S]{0,1000}\}',
        ]
        
        for pattern in md5_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                findings.append({
                    'type': 'MD5函数定义',
                    'pattern': pattern,
                    'match': match.group(0)[:500],
                    'line': line_num,
                    'context': self._clean_context(match.group(0)),
                    'file': file_info
                })
        
        return findings
    
    def _clean_context(self, context: str, max_length: int = 500) -> str:
        """清理上下文，移除多余空白"""
        # 移除多余的换行和空白
        context = re.sub(r'\n{3,}', '\n\n', context)
        context = re.sub(r' {3,}', '  ', context)
        
        if len(context) > max_length:
            context = context[:max_length] + '...'
        
        return context
    
    def analyze_api_call(self, url: str) -> Dict:
        """分析API调用URL"""
        result = {
            'url': url,
            'z_param': None,
            'other_params': {}
        }
        
        # 提取z参数
        z_match = re.search(r'[?&]z=([a-f0-9]{32})', url)
        if z_match:
            result['z_param'] = z_match.group(1)
        
        # 提取其他参数
        if '?' in url:
            query_string = url.split('?', 1)[1]
            for pair in query_string.split('&'):
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    if key != 'z':
                        result['other_params'][key] = value
        
        return result


async def capture_and_analyze(video_url: str, captured_z: str = None):
    """捕获并分析JavaScript代码"""
    print("=" * 60)
    print("捕获并分析z参数生成逻辑")
    print("=" * 60)
    
    parser_url = f"https://videocdn.ihelpy.net/jiexi/m1907.html?m1907jx={video_url}"
    analyzer = ZParamAnalyzer(captured_z=captured_z, video_url=video_url)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        )
        
        page = await context.new_page()
        
        # 存储捕获的数据
        executed_scripts = []
        api_calls = []
        all_findings = []
        
        # Hook console.log
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
            if 'api/v' in url or 'm1-a1.cloud' in url or 'm1-z2.cloud' in url:
                api_info = analyzer.analyze_api_call(url)
                api_calls.append({
                    'url': url,
                    'method': request.method,
                    'z_param': api_info.get('z_param'),
                    'other_params': api_info.get('other_params'),
                    'headers': dict(request.headers)
                })
                print(f"\n🔍 捕获API调用: {url}")
                if api_info.get('z_param'):
                    print(f"   ✅ z参数: {api_info['z_param']}")
        
        page.on('request', handle_request)
        
        # 注入代码捕获脚本
        await page.add_init_script("""
            // 捕获所有执行的代码
            window._capturedCode = {
                functions: {},
                variables: {},
                apiCalls: []
            };
            
            // Hook Function构造函数
            const originalFunction = window.Function;
            window.Function = function(...args) {
                const func = originalFunction.apply(this, args);
                const funcStr = func.toString();
                if (funcStr.includes('z') || funcStr.includes('api') || funcStr.includes('md5')) {
                    window._capturedCode.functions[Date.now()] = {
                        code: funcStr,
                        args: args
                    };
                }
                return func;
            };
            
            // Hook eval
            const originalEval = window.eval;
            window.eval = function(code) {
                if (code.includes('z') || code.includes('api') || code.includes('md5')) {
                    window._capturedCode.functions['eval_' + Date.now()] = {
                        code: code,
                        type: 'eval'
                    };
                }
                return originalEval.apply(this, arguments);
            };
            
            // Hook fetch
            const originalFetch = window.fetch;
            window.fetch = function(...args) {
                const url = args[0];
                if (typeof url === 'string' && (url.includes('api/v') || url.includes('m1-a1.cloud'))) {
                    const stack = new Error().stack;
                    window._capturedCode.apiCalls.push({
                        url: url,
                        stack: stack,
                        timestamp: Date.now()
                    });
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
        print(f"\n[步骤3] 提取并分析代码...")
        
        captured_data = await page.evaluate("""
            () => {
                return {
                    functions: window._capturedCode?.functions || {},
                    apiCalls: window._capturedCode?.apiCalls || [],
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
        
        # 分析所有脚本
        print(f"\n[步骤4] 分析JavaScript代码...")
        
        # 分析内联脚本
        for script in captured_data.get('scripts', []):
            if script.get('content'):
                content = script['content']
                file_info = {
                    'type': 'inline',
                    'index': script.get('index'),
                    'src': script.get('src')
                }
                findings = analyzer.search_z_in_code(content, file_info)
                if findings:
                    all_findings.extend(findings)
                    print(f"\n   📄 内联脚本 [{script.get('index')}]: 找到 {len(findings)} 处相关代码")
        
        # 分析捕获的函数
        for key, func_data in captured_data.get('functions', {}).items():
            code = func_data.get('code', '')
            file_info = {
                'type': 'captured_function',
                'key': key,
                'func_type': func_data.get('type', 'function')
            }
            findings = analyzer.search_z_in_code(code, file_info)
            if findings:
                all_findings.extend(findings)
                print(f"\n   📄 捕获函数 [{key}]: 找到 {len(findings)} 处相关代码")
        
        # 分析API调用栈
        for api_call in captured_data.get('apiCalls', []):
            stack = api_call.get('stack', '')
            if stack:
                # 从调用栈中提取文件名和行号
                stack_lines = stack.split('\n')[:10]
                print(f"\n   📡 API调用栈:")
                for line in stack_lines[:5]:
                    print(f"      {line.strip()}")
        
        # 保存结果
        output = {
            'video_url': video_url,
            'parser_url': parser_url,
            'captured_z': captured_z,
            'api_calls': api_calls,
            'captured_functions': captured_data.get('functions', {}),
            'captured_logs': captured_data.get('logs', []),
            'scripts': captured_data.get('scripts', []),
            'findings': all_findings
        }
        
        output_file = 'z_param_analysis_results.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n✅ 分析完成")
        print(f"   💾 保存到: {output_file}")
        print(f"   📋 找到 {len(all_findings)} 处相关代码")
        print(f"   📡 捕获 {len(api_calls)} 个API调用")
        
        # 显示关键发现
        if all_findings:
            print(f"\n🔍 关键发现:")
            for i, finding in enumerate(all_findings[:10], 1):
                print(f"\n[{i}] {finding.get('type')}")
                if finding.get('file'):
                    file_info = finding['file']
                    if file_info.get('src'):
                        print(f"   文件: {file_info['src']}")
                    elif file_info.get('type'):
                        print(f"   类型: {file_info['type']}")
                print(f"   行号: {finding.get('line', 'N/A')}")
                print(f"   匹配: {finding['match'][:150]}...")
                print(f"   上下文: {finding['context'][:300]}...")
        
        # 提供搜索建议
        print(f"\n💡 搜索建议:")
        print(f"   1. 在浏览器开发者工具中，打开Sources标签页")
        print(f"   2. 按Ctrl+Shift+F（Windows）或Cmd+Option+F（Mac）打开全局搜索")
        print(f"   3. 搜索以下关键词:")
        print(f"      - \"{captured_z}\" (如果提供了z值)")
        print(f"      - \"z=\" 或 \"z:\"")
        print(f"      - \"md5\"")
        print(f"      - \"api/v\"")
        print(f"   4. 重点关注网站自己的JS文件（非Chrome扩展）")
        print(f"   5. 在找到的代码处设置断点，观察z参数的生成过程")
        
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
            latest = captured_params[-1]
            captured_z = latest.get('z')
            video_url = latest.get('jx')
        else:
            captured_z = None
            video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    except:
        captured_z = "4bbcd9c68c6625b5432721b6290ec694"
        video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    
    result = await capture_and_analyze(video_url, captured_z)
    
    if result and result.get('findings'):
        print("\n💡 下一步:")
        print("   1. 查看 z_param_analysis_results.json")
        print("   2. 在浏览器中打开找到的JS文件")
        print("   3. 使用全局搜索查找z参数生成逻辑")
        print("   4. 设置断点，观察z参数的生成过程")


if __name__ == '__main__':
    asyncio.run(main())

