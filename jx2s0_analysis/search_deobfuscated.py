"""
在反混淆后的JavaScript文件中搜索关键字
"""

import re
import os
from deobfuscate_js import JavaScriptDeobfuscator


def search_in_file(file_path: str, keywords: list, deobfuscate: bool = True) -> dict:
    """在文件中搜索关键字"""
    print(f"\n搜索文件: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"  ❌ 文件不存在")
        return {'file': file_path, 'found': []}
    
    # 读取文件
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"  ❌ 读取失败: {e}")
        return {'file': file_path, 'found': []}
    
    # 反混淆（如果需要）
    if deobfuscate:
        print("  反混淆中...")
        deobfuscator = JavaScriptDeobfuscator()
        content = deobfuscator.decode_hex_strings(content)
        content = deobfuscator.decode_unicode_strings(content)
    
    # 搜索关键字
    results = {}
    for keyword in keywords:
        # 搜索关键字（不区分大小写）
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        matches = []
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            if pattern.search(line):
                # 提取上下文（前后各2行）
                start = max(0, line_num - 3)
                end = min(len(lines), line_num + 2)
                context = '\n'.join(lines[start:end])
                
                matches.append({
                    'line': line_num,
                    'content': line.strip(),
                    'context': context
                })
        
        if matches:
            results[keyword] = matches
            print(f"  ✅ 找到 '{keyword}': {len(matches)} 处")
        else:
            print(f"  ❌ 未找到 '{keyword}'")
    
    return {'file': file_path, 'found': results}


def main():
    """主函数"""
    print("=" * 60)
    print("在JavaScript文件中搜索关键字")
    print("=" * 60)
    
    # 要搜索的文件
    files_to_search = [
        '7zl.js',
        '7zlplayer.js',
    ]
    
    # 要搜索的关键字
    keywords = [
        'm3u8',
        'cachem3u8',
        'Cache',
        'token',
        'cachem3u8.2s0.cn',
        '8899',
        'Cache/Ff',
        'XMLHttpRequest',
        'fetch',
        '$.ajax',
        'config.url',
        'YKQ.video',
        'YKQ.player',
        '/admin/api.php',
        'rc4',
        'atob',
        'btoa',
    ]
    
    all_results = []
    
    for file_name in files_to_search:
        if os.path.exists(file_name):
            result = search_in_file(file_name, keywords, deobfuscate=True)
            all_results.append(result)
        else:
            print(f"\n⚠️  文件不存在: {file_name}")
    
    # 输出结果
    print("\n" + "=" * 60)
    print("搜索结果汇总")
    print("=" * 60)
    
    for result in all_results:
        file_name = os.path.basename(result['file'])
        print(f"\n📄 {file_name}:")
        
        if result['found']:
            for keyword, matches in result['found'].items():
                print(f"\n  🔍 '{keyword}' - 找到 {len(matches)} 处:")
                for i, match in enumerate(matches[:5], 1):  # 只显示前5处
                    print(f"    [{i}] 第 {match['line']} 行:")
                    print(f"        {match['content'][:100]}...")
                if len(matches) > 5:
                    print(f"    ... 还有 {len(matches) - 5} 处")
        else:
            print("  ❌ 未找到任何关键字")
    
    # 保存详细结果
    output_file = 'search_results.txt'
    print(f"\n💾 详细结果已保存到: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("JavaScript文件搜索结果\n")
        f.write("=" * 60 + "\n\n")
        
        for result in all_results:
            file_name = os.path.basename(result['file'])
            f.write(f"文件: {file_name}\n")
            f.write("-" * 60 + "\n\n")
            
            if result['found']:
                for keyword, matches in result['found'].items():
                    f.write(f"关键字: {keyword} - 找到 {len(matches)} 处\n")
                    f.write("-" * 40 + "\n")
                    for match in matches:
                        f.write(f"第 {match['line']} 行:\n")
                        f.write(f"{match['content']}\n")
                        f.write(f"\n上下文:\n{match['context']}\n")
                        f.write("\n" + "-" * 40 + "\n\n")
            else:
                f.write("未找到任何关键字\n\n")
            f.write("\n")


if __name__ == '__main__':
    main()

