"""
在JavaScript代码中搜索z参数生成逻辑
分析浏览器加载的JS文件，查找z参数的生成方式
"""

import re
import json
import hashlib
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs
from pathlib import Path


class ZParamSearcher:
    """z参数搜索器"""
    
    def __init__(self, captured_z: str = None, video_url: str = None):
        self.captured_z = captured_z
        self.video_url = video_url
        self.findings = []
    
    def search_patterns(self, js_code: str, file_path: str = None) -> List[Dict]:
        """搜索z参数相关的代码模式"""
        findings = []
        
        # 模式1: z参数赋值
        patterns = [
            # z = "xxx" 或 z: "xxx"
            (r'[zZ]\s*[:=]\s*["\']([a-f0-9]{32})["\']', 'z参数直接赋值'),
            # var z = "xxx"
            (r'(?:var|let|const)\s+[zZ]\s*=\s*["\']([a-f0-9]{32})["\']', 'z变量声明'),
            # z = md5(...)
            (r'[zZ]\s*[:=]\s*md5\s*\([^)]+\)', 'z参数MD5计算'),
            # z = hash(...)
            (r'[zZ]\s*[:=]\s*hash\s*\([^)]+\)', 'z参数哈希计算'),
            # z = encrypt(...)
            (r'[zZ]\s*[:=]\s*encrypt\s*\([^)]+\)', 'z参数加密计算'),
            # z = function(...)
            (r'[zZ]\s*[:=]\s*function\s*\([^)]*\)\s*\{[^}]*\}', 'z参数函数计算'),
            # z = xxx.md5() 或 xxx.hash()
            (r'[zZ]\s*[:=]\s*[^=]+\.(?:md5|hash|encrypt)\s*\([^)]*\)', 'z参数方法调用'),
            # URL中包含z参数
            (r'[?&]z=([a-f0-9]{32})', 'URL中的z参数'),
            # API调用中的z参数
            (r'api/v[^?]*[?&]z=([a-f0-9]{32})', 'API调用中的z参数'),
            # fetch或XMLHttpRequest中的z参数
            (r'(?:fetch|XMLHttpRequest|ajax)\s*\([^)]*z[=:]([a-f0-9]{32})', 'HTTP请求中的z参数'),
        ]
        
        for pattern, description in patterns:
            matches = re.finditer(pattern, js_code, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                line_num = js_code[:match.start()].count('\n') + 1
                context_start = max(0, match.start() - 200)
                context_end = min(len(js_code), match.end() + 200)
                context = js_code[context_start:context_end]
                
                findings.append({
                    'type': description,
                    'pattern': pattern,
                    'match': match.group(0),
                    'line': line_num,
                    'context': context,
                    'file': file_path
                })
        
        # 模式2: MD5相关函数定义
        md5_patterns = [
            r'function\s+md5\s*\([^)]*\)\s*\{[^}]{0,500}\}',
            r'const\s+md5\s*=\s*function\s*\([^)]*\)\s*\{[^}]{0,500}\}',
            r'const\s+md5\s*=\s*\([^)]*\)\s*=>\s*\{[^}]{0,500}\}',
            r'md5\s*[:=]\s*function\s*\([^)]*\)\s*\{[^}]{0,500}\}',
        ]
        
        for pattern in md5_patterns:
            matches = re.finditer(pattern, js_code, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            for match in matches:
                line_num = js_code[:match.start()].count('\n') + 1
                findings.append({
                    'type': 'MD5函数定义',
                    'pattern': pattern,
                    'match': match.group(0)[:500],
                    'line': line_num,
                    'context': match.group(0),
                    'file': file_path
                })
        
        # 模式3: 如果提供了捕获的z值，搜索该值
        if self.captured_z:
            if self.captured_z in js_code:
                # 找到z值出现的位置
                positions = []
                start = 0
                while True:
                    pos = js_code.find(self.captured_z, start)
                    if pos == -1:
                        break
                    positions.append(pos)
                    start = pos + 1
                
                for pos in positions[:5]:  # 只取前5个
                    line_num = js_code[:pos].count('\n') + 1
                    context_start = max(0, pos - 300)
                    context_end = min(len(js_code), pos + len(self.captured_z) + 300)
                    context = js_code[context_start:context_end]
                    
                    findings.append({
                        'type': 'z参数值出现',
                        'pattern': 'exact_match',
                        'match': self.captured_z,
                        'line': line_num,
                        'context': context,
                        'file': file_path
                    })
        
        return findings
    
    def analyze_md5_function(self, js_code: str) -> List[Dict]:
        """分析MD5函数的实现"""
        findings = []
        
        # 查找MD5函数定义
        md5_function_patterns = [
            r'function\s+md5\s*\([^)]*\)\s*\{[\s\S]{0,2000}\}',
            r'const\s+md5\s*=\s*function\s*\([^)]*\)\s*\{[\s\S]{0,2000}\}',
            r'const\s+md5\s*=\s*\([^)]*\)\s*=>\s*\{[\s\S]{0,2000}\}',
        ]
        
        for pattern in md5_function_patterns:
            matches = re.finditer(pattern, js_code, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            for match in matches:
                func_code = match.group(0)
                findings.append({
                    'type': 'MD5函数实现',
                    'code': func_code,
                    'file': None
                })
        
        return findings
    
    def search_api_call_patterns(self, js_code: str, file_path: str = None) -> List[Dict]:
        """搜索API调用相关的代码"""
        findings = []
        
        # 搜索包含api/v的URL
        api_patterns = [
            r'["\']https?://[^"\']*api/v[^"\']*["\']',
            r'["\']https?://[^"\']*m1-a1\.cloud[^"\']*["\']',
            r'["\']https?://[^"\']*m1-z2\.cloud[^"\']*["\']',
            r'fetch\s*\(\s*["\']https?://[^"\']*api/v[^"\']*["\']',
            r'XMLHttpRequest[^;]*open\s*\([^,]+,\s*["\']https?://[^"\']*api/v[^"\']*["\']',
        ]
        
        for pattern in api_patterns:
            matches = re.finditer(pattern, js_code, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                line_num = js_code[:match.start()].count('\n') + 1
                context_start = max(0, match.start() - 300)
                context_end = min(len(js_code), match.end() + 300)
                context = js_code[context_start:context_end]
                
                findings.append({
                    'type': 'API调用',
                    'pattern': pattern,
                    'match': match.group(0),
                    'line': line_num,
                    'context': context,
                    'file': file_path
                })
        
        return findings
    
    def extract_z_generation_logic(self, js_code: str, file_path: str = None) -> Dict:
        """提取z参数生成逻辑"""
        result = {
            'file': file_path,
            'z_assignments': [],
            'md5_functions': [],
            'api_calls': [],
            'z_value_occurrences': []
        }
        
        # 搜索z参数赋值
        result['z_assignments'] = self.search_patterns(js_code, file_path)
        
        # 搜索MD5函数
        result['md5_functions'] = self.analyze_md5_function(js_code)
        
        # 搜索API调用
        result['api_calls'] = self.search_api_call_patterns(js_code, file_path)
        
        # 如果提供了z值，搜索该值
        if self.captured_z:
            z_positions = []
            start = 0
            while True:
                pos = js_code.find(self.captured_z, start)
                if pos == -1:
                    break
                z_positions.append(pos)
                start = pos + 1
            
            for pos in z_positions[:3]:
                line_num = js_code[:pos].count('\n') + 1
                context_start = max(0, pos - 500)
                context_end = min(len(js_code), pos + len(self.captured_z) + 500)
                context = js_code[context_start:context_end]
                
                result['z_value_occurrences'].append({
                    'line': line_num,
                    'context': context
                })
        
        return result
    
    def search_in_file(self, file_path: str) -> Dict:
        """在文件中搜索"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return self.extract_z_generation_logic(content, file_path)
        except Exception as e:
            return {
                'file': file_path,
                'error': str(e),
                'z_assignments': [],
                'md5_functions': [],
                'api_calls': [],
                'z_value_occurrences': []
            }
    
    def search_in_urls(self, urls: List[str], download_dir: str = 'downloaded_js') -> List[Dict]:
        """从URL列表中搜索（需要先下载JS文件）"""
        results = []
        
        # 创建下载目录
        Path(download_dir).mkdir(exist_ok=True)
        
        import requests
        
        for url in urls:
            try:
                # 下载JS文件
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    # 保存文件
                    filename = url.split('/')[-1].split('?')[0]
                    if not filename.endswith('.js'):
                        filename += '.js'
                    
                    file_path = Path(download_dir) / filename
                    file_path.write_text(response.text, encoding='utf-8')
                    
                    # 搜索
                    result = self.extract_z_generation_logic(response.text, str(file_path))
                    results.append(result)
            except Exception as e:
                results.append({
                    'file': url,
                    'error': str(e)
                })
        
        return results


def analyze_captured_data():
    """分析捕获的数据"""
    try:
        with open('captured_api_params.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        captured_params = data.get('captured_params', [])
        if captured_params:
            latest = captured_params[-1]
            return latest.get('z'), latest.get('jx')
    except:
        pass
    
    return None, None


def main():
    """主函数"""
    print("=" * 60)
    print("在JavaScript代码中搜索z参数生成逻辑")
    print("=" * 60)
    
    # 从捕获数据中读取z参数
    captured_z, video_url = analyze_captured_data()
    
    if captured_z:
        print(f"\n📋 使用捕获的z参数: {captured_z}")
    else:
        captured_z = input("\n请输入z参数值（32位MD5格式）: ").strip()
    
    if video_url:
        print(f"📋 视频URL: {video_url}")
    
    searcher = ZParamSearcher(captured_z=captured_z, video_url=video_url)
    
    # 从图片中的URL列表（这些是Chrome扩展的JS文件）
    # 注意：这些文件通常无法直接下载，需要在浏览器中查看
    js_urls_from_image = [
        'chrome-extension://hehijbfgiekmjfkfjpbkbammjbdenadd/js/ietabapi_wp.js',
        'chrome-extension://jlpcnoohcpfgpbalhlggdhjocgnlgafn/assets/main-world.ts-4ed993c7.js',
        'https://m1-z2.cloud.nnpp.vip:2223/static/js/main.1336e445.js',
        'https://m1-cn-201.cloud.nnpp.vip:2223/z1/js/h-1-6.js',
    ]
    
    print(f"\n🔍 搜索策略:")
    print(f"   1. 重点关注网站JS文件（非Chrome扩展）")
    print(f"   2. 搜索z参数赋值和MD5计算")
    print(f"   3. 分析API调用代码")
    
    # 重点关注的URL（网站自己的JS，不是扩展）
    website_js_urls = [
        'https://m1-z2.cloud.nnpp.vip:2223/static/js/main.1336e445.js',
        'https://m1-cn-201.cloud.nnpp.vip:2223/z1/js/h-1-6.js',
    ]
    
    print(f"\n📥 下载并分析网站JS文件...")
    results = searcher.search_in_urls(website_js_urls)
    
    # 显示结果
    print(f"\n" + "=" * 60)
    print("📊 搜索结果")
    print("=" * 60)
    
    for result in results:
        if result.get('error'):
            print(f"\n❌ {result['file']}: {result['error']}")
            continue
        
        print(f"\n📄 文件: {result['file']}")
        
        if result.get('z_assignments'):
            print(f"   ✅ 找到 {len(result['z_assignments'])} 处z参数相关代码:")
            for i, finding in enumerate(result['z_assignments'][:5], 1):
                print(f"\n   [{i}] {finding['type']}")
                print(f"       行号: {finding.get('line', 'N/A')}")
                print(f"       匹配: {finding['match'][:100]}...")
                print(f"       上下文: {finding['context'][:200]}...")
        
        if result.get('md5_functions'):
            print(f"\n   ✅ 找到 {len(result['md5_functions'])} 个MD5函数定义")
            for i, func in enumerate(result['md5_functions'][:2], 1):
                print(f"\n   [{i}] MD5函数:")
                print(f"       {func['code'][:300]}...")
        
        if result.get('api_calls'):
            print(f"\n   ✅ 找到 {len(result['api_calls'])} 处API调用:")
            for i, call in enumerate(result['api_calls'][:3], 1):
                print(f"\n   [{i}] {call['match'][:150]}...")
        
        if result.get('z_value_occurrences'):
            print(f"\n   ✅ z参数值出现 {len(result['z_value_occurrences'])} 次:")
            for i, occ in enumerate(result['z_value_occurrences'][:2], 1):
                print(f"\n   [{i}] 行号: {occ['line']}")
                print(f"       上下文: {occ['context'][:300]}...")
    
    # 保存结果
    output_file = 'z_param_search_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n✅ 搜索结果已保存到: {output_file}")
    
    print(f"\n💡 下一步:")
    print(f"   1. 查看 {output_file} 文件")
    print(f"   2. 重点关注找到的MD5函数和z参数赋值代码")
    print(f"   3. 在浏览器中打开这些JS文件，查看完整代码")
    print(f"   4. 使用浏览器开发者工具，在z参数生成处设置断点")


if __name__ == '__main__':
    main()

