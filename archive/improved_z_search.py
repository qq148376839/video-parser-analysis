"""
改进的z参数搜索工具
搜索混淆代码中的z参数生成逻辑
"""

import re
import json
from typing import List, Dict


class ImprovedZParamSearcher:
    """改进的z参数搜索器，适用于混淆代码"""
    
    def __init__(self, captured_z: str = None):
        self.captured_z = captured_z
    
    def search_obfuscated_patterns(self, code: str) -> List[Dict]:
        """搜索混淆代码中的z参数模式"""
        findings = []
        
        if not code:
            return findings
        
        # 模式1: 32位MD5格式的字符串（可能是z参数）
        md5_pattern = r'["\']([a-f0-9]{32})["\']'
        md5_matches = re.finditer(md5_pattern, code, re.IGNORECASE)
        for match in md5_matches:
            md5_value = match.group(1)
            # 如果提供了捕获的z值，检查是否匹配
            if self.captured_z and md5_value.lower() == self.captured_z.lower():
                line_num = code[:match.start()].count('\n') + 1
                context_start = max(0, match.start() - 500)
                context_end = min(len(code), match.end() + 500)
                context = code[context_start:context_end]
                
                findings.append({
                    'type': 'z参数值匹配',
                    'value': md5_value,
                    'line': line_num,
                    'context': context,
                    'confidence': 'high'
                })
        
        # 模式2: URL参数中的z参数
        url_patterns = [
            r'[?&]z=([a-f0-9]{32})',
            r'["\'][^"\']*[?&]z=([a-f0-9]{32})[^"\']*["\']',
            r'\+["\']z=([a-f0-9]{32})["\']',
        ]
        
        for pattern in url_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                z_value = match.group(1)
                line_num = code[:match.start()].count('\n') + 1
                context_start = max(0, match.start() - 300)
                context_end = min(len(code), match.end() + 300)
                context = code[context_start:context_end]
                
                findings.append({
                    'type': 'URL中的z参数',
                    'value': z_value,
                    'line': line_num,
                    'context': context,
                    'confidence': 'high'
                })
        
        # 模式3: 变量赋值（可能是混淆后的变量名）
        # 搜索形如: var a = "4bbcd9c68c6625b5432721b6290ec694"
        var_patterns = [
            r'(?:var|let|const)\s+[a-zA-Z_$][a-zA-Z0-9_$]*\s*=\s*["\']([a-f0-9]{32})["\']',
            r'[a-zA-Z_$][a-zA-Z0-9_$]*\s*[:=]\s*["\']([a-f0-9]{32})["\']',
        ]
        
        for pattern in var_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                z_value = match.group(1)
                if self.captured_z and z_value.lower() == self.captured_z.lower():
                    line_num = code[:match.start()].count('\n') + 1
                    context_start = max(0, match.start() - 500)
                    context_end = min(len(code), match.end() + 500)
                    context = code[context_start:context_end]
                    
                    findings.append({
                        'type': '变量赋值（可能混淆）',
                        'value': z_value,
                        'line': line_num,
                        'context': context,
                        'confidence': 'high'
                    })
        
        # 模式4: 函数调用中的z参数
        # 搜索形如: fetch("...api/v/?z=...")
        fetch_patterns = [
            r'fetch\s*\(\s*["\']([^"\']*[?&]z=([a-f0-9]{32})[^"\']*)["\']',
            r'XMLHttpRequest[^;]*open\s*\([^,]+,\s*["\']([^"\']*[?&]z=([a-f0-9]{32})[^"\']*)["\']',
        ]
        
        for pattern in fetch_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                z_value = match.group(2) if len(match.groups()) > 1 else None
                if z_value:
                    line_num = code[:match.start()].count('\n') + 1
                    context_start = max(0, match.start() - 500)
                    context_end = min(len(code), match.end() + 500)
                    context = code[context_start:context_end]
                    
                    findings.append({
                        'type': 'API调用中的z参数',
                        'value': z_value,
                        'line': line_num,
                        'context': context,
                        'confidence': 'high'
                    })
        
        # 模式5: 字符串拼接（可能是动态生成）
        # 搜索形如: "api/v/?z=" + z
        concat_patterns = [
            r'["\'][^"\']*z=["\']\s*\+\s*[a-zA-Z_$][a-zA-Z0-9_$]*',
            r'[a-zA-Z_$][a-zA-Z0-9_$]*\s*\+\s*["\'][^"\']*z=([a-f0-9]{32})["\']',
        ]
        
        for pattern in concat_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                context_start = max(0, match.start() - 500)
                context_end = min(len(code), match.end() + 500)
                context = code[context_start:context_end]
                
                findings.append({
                    'type': '字符串拼接（z参数生成）',
                    'line': line_num,
                    'context': context,
                    'confidence': 'medium'
                })
        
        return findings
    
    def search_in_file(self, file_path: str) -> Dict:
        """在文件中搜索"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            findings = self.search_obfuscated_patterns(content)
            
            return {
                'file': file_path,
                'findings': findings,
                'total_findings': len(findings)
            }
        except Exception as e:
            return {
                'file': file_path,
                'error': str(e),
                'findings': [],
                'total_findings': 0
            }


def main():
    """主函数"""
    print("=" * 60)
    print("改进的z参数搜索工具（适用于混淆代码）")
    print("=" * 60)
    
    # 从捕获数据中读取z参数
    try:
        with open('captured_api_params.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        captured_params = data.get('captured_params', [])
        if captured_params:
            captured_z = captured_params[-1].get('z')
            print(f"\n📋 使用捕获的z参数: {captured_z}")
        else:
            captured_z = None
    except:
        captured_z = "4bbcd9c68c6625b5432721b6290ec694"
        print(f"\n📋 使用示例z参数: {captured_z}")
    
    searcher = ImprovedZParamSearcher(captured_z=captured_z)
    
    # 搜索已下载的JS文件
    import os
    js_files = []
    if os.path.exists('downloaded_js'):
        for file in os.listdir('downloaded_js'):
            if file.endswith('.js'):
                js_files.append(os.path.join('downloaded_js', file))
    
    if not js_files:
        print("\n⚠️ 未找到JS文件")
        print("💡 请先运行: python archive/search_z_param_in_js.py")
        return
    
    print(f"\n🔍 搜索 {len(js_files)} 个JS文件...")
    
    all_results = []
    for js_file in js_files:
        print(f"\n📄 搜索文件: {js_file}")
        result = searcher.search_in_file(js_file)
        all_results.append(result)
        
        if result.get('findings'):
            print(f"   ✅ 找到 {len(result['findings'])} 处相关代码")
            for i, finding in enumerate(result['findings'][:3], 1):
                print(f"\n   [{i}] {finding['type']}")
                if finding.get('value'):
                    print(f"      值: {finding['value']}")
                print(f"      行号: {finding.get('line', 'N/A')}")
                print(f"      上下文: {finding['context'][:200]}...")
        else:
            print(f"   ⚠️ 未找到相关代码")
    
    # 保存结果
    output_file = 'improved_z_search_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n✅ 搜索完成")
    print(f"   💾 保存到: {output_file}")
    
    # 统计
    total_findings = sum(r.get('total_findings', 0) for r in all_results)
    print(f"   📊 总共找到 {total_findings} 处相关代码")
    
    if total_findings == 0:
        print(f"\n💡 建议:")
        print(f"   1. z参数可能是动态生成的，不在静态JS文件中")
        print(f"   2. z参数可能从服务器获取（检查第一个API调用的响应）")
        print(f"   3. 使用浏览器开发者工具，在API调用处设置断点")
        print(f"   4. 运行: python archive/analyze_api_response_for_z.py")


if __name__ == '__main__':
    main()

