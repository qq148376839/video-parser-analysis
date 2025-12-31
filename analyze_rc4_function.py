"""
分析 7zl.js 中的 rc4 函数，判断是否用于 token 生成
"""

import re
import json


def extract_rc4_function(js_file_path: str):
    """提取 rc4 函数的完整代码"""
    with open(js_file_path, 'r', encoding='utf-8', errors='ignore') as f:
        js_code = f.read()
    
    # 查找 rc4 函数定义
    # 匹配 function rc4(...) { ... }
    pattern = r'function\s+rc4\s*\([^)]*\)\s*\{[^}]*\}'
    
    # 由于是单行文件，需要匹配多行
    matches = re.finditer(pattern, js_code, re.DOTALL)
    
    rc4_functions = []
    for match in matches:
        function_code = match.group(0)
        start = max(0, match.start() - 500)
        end = min(len(js_code), match.end() + 500)
        context = js_code[start:end]
        
        rc4_functions.append({
            'function': function_code,
            'position': match.start(),
            'context': context
        })
    
    return rc4_functions


def find_rc4_calls(js_file_path: str):
    """查找 rc4 函数的调用"""
    with open(js_file_path, 'r', encoding='utf-8', errors='ignore') as f:
        js_code = f.read()
    
    # 查找 rc4 函数调用
    pattern = r'rc4\s*\([^)]+\)'
    
    calls = []
    for match in re.finditer(pattern, js_code):
        call = match.group(0)
        start = max(0, match.start() - 300)
        end = min(len(js_code), match.end() + 300)
        context = js_code[start:end]
        
        calls.append({
            'call': call,
            'position': match.start(),
            'context': context
        })
    
    return calls


def analyze_rc4_usage(js_file_path: str):
    """分析 rc4 函数的使用情况"""
    print("=" * 60)
    print("分析 rc4 函数 - 判断是否用于 token 生成")
    print("=" * 60)
    
    # 提取 rc4 函数定义
    print("\n[步骤1] 提取 rc4 函数定义...")
    rc4_functions = extract_rc4_function(js_file_path)
    print(f"   [OK] 找到 {len(rc4_functions)} 个 rc4 函数定义")
    
    if rc4_functions:
        for i, func in enumerate(rc4_functions, 1):
            print(f"\n   [函数 {i}] 位置: {func['position']}")
            print(f"   函数代码长度: {len(func['function'])} 字符")
            print(f"   函数代码预览: {func['function'][:200]}...")
    
    # 查找 rc4 函数调用
    print("\n[步骤2] 查找 rc4 函数调用...")
    rc4_calls = find_rc4_calls(js_file_path)
    print(f"   [OK] 找到 {len(rc4_calls)} 个 rc4 函数调用")
    
    if rc4_calls:
        print(f"\n   [调用示例] (前5个):")
        for i, call in enumerate(rc4_calls[:5], 1):
            print(f"\n   [{i}] 位置: {call['position']}")
            print(f"   调用: {call['call'][:100]}...")
            print(f"   上下文: {call['context'][:200]}...")
    
    # 分析调用上下文，查找 token 相关
    print("\n[步骤3] 分析调用上下文，查找 token 相关...")
    token_related_calls = []
    
    for call in rc4_calls:
        context = call['context'].lower()
        # 检查是否与 token、m3u8、cachem3u8、config.url 相关
        if any(keyword in context for keyword in ['token', 'm3u8', 'cachem3u8', 'config', 'url', 'cache']):
            token_related_calls.append(call)
    
    print(f"   [OK] 找到 {len(token_related_calls)} 个可能与 token 相关的调用")
    
    if token_related_calls:
        print(f"\n   [Token相关调用]:")
        for i, call in enumerate(token_related_calls[:5], 1):
            print(f"\n   [{i}] 位置: {call['position']}")
            print(f"   调用: {call['call'][:100]}...")
            print(f"   上下文: {call['context'][:300]}...")
    
    # 查找 rc4 函数参数
    print("\n[步骤4] 分析 rc4 函数参数...")
    if rc4_functions:
        func_code = rc4_functions[0]['function']
        # 提取函数参数
        param_match = re.search(r'function\s+rc4\s*\(([^)]+)\)', func_code)
        if param_match:
            params = param_match.group(1)
            print(f"   参数: {params}")
            
            # 分析参数用途
            param_list = [p.strip() for p in params.split(',')]
            print(f"   参数数量: {len(param_list)}")
            for i, param in enumerate(param_list, 1):
                print(f"     参数{i}: {param}")
    
    # 查找 rc4 函数内部逻辑
    print("\n[步骤5] 分析 rc4 函数内部逻辑...")
    if rc4_functions:
        func_code = rc4_functions[0]['function']
        
        # 查找关键操作
        key_operations = {
            'return': len(re.findall(r'\breturn\b', func_code)),
            'config': len(re.findall(r'\bconfig\b', func_code, re.IGNORECASE)),
            'url': len(re.findall(r'\burl\b', func_code, re.IGNORECASE)),
            'token': len(re.findall(r'\btoken\b', func_code, re.IGNORECASE)),
            'm3u8': len(re.findall(r'\bm3u8\b', func_code, re.IGNORECASE)),
            'key': len(re.findall(r'\bkey\b', func_code, re.IGNORECASE)),
            'iv': len(re.findall(r'\biv\b', func_code, re.IGNORECASE)),
        }
        
        print(f"   关键操作统计:")
        for op, count in key_operations.items():
            if count > 0:
                print(f"     {op}: {count} 次")
    
    # 保存结果
    result = {
        'rc4_functions': rc4_functions,
        'rc4_calls': rc4_calls,
        'token_related_calls': token_related_calls
    }
    
    output_file = 'rc4_analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n[OK] 分析结果已保存到: {output_file}")
    
    # 总结
    print("\n" + "=" * 60)
    print("[总结]")
    print("=" * 60)
    
    if token_related_calls:
        print(f"\n[重要] 找到 {len(token_related_calls)} 个可能与 token 相关的 rc4 调用！")
        print(f"   建议查看: rc4_analysis.json 中的 'token_related_calls' 部分")
    else:
        print(f"\n[提示] 未找到明显的 token 相关调用")
        print(f"   rc4 函数可能用于解密 config.url，而不是生成 token")
    
    if rc4_functions:
        print(f"\n[提示] rc4 函数定义:")
        print(f"   位置: {rc4_functions[0]['position']}")
        print(f"   代码长度: {len(rc4_functions[0]['function'])} 字符")
        print(f"   建议查看完整函数代码以理解其用途")
    
    return result


if __name__ == '__main__':
    js_file = 'downloaded_js/7zl.js'
    analyze_rc4_usage(js_file)


