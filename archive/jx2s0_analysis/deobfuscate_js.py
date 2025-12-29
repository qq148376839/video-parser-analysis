"""
JavaScript反混淆脚本
将混淆的JavaScript代码还原为可读形式，方便搜索和分析
"""

import re
import os
from typing import List, Tuple


class JavaScriptDeobfuscator:
    """JavaScript反混淆器"""
    
    def __init__(self):
        self.replacements = []
    
    def decode_hex_strings(self, content: str) -> str:
        """解码十六进制编码的字符串"""
        def decode_hex_sequence(hex_str: str) -> str:
            """解码十六进制序列"""
            decoded = ''
            hex_parts = re.findall(r'\\x([0-9a-fA-F]{2})', hex_str)
            for hex_part in hex_parts:
                try:
                    decoded += chr(int(hex_part, 16))
                except:
                    decoded += f'\\x{hex_part}'
            return decoded
        
        # 模式1: 字符串字面量 '\x6f\x70\x65\x6e' 或 "\x6f\x70\x65\x6e"
        pattern1 = r'(["\'])((?:\\x[0-9a-fA-F]{2})+)\1'
        def decode_match1(match):
            quote = match.group(1)
            hex_str = match.group(2)
            decoded = decode_hex_sequence(hex_str)
            return f'{quote}{decoded}{quote}'
        content = re.sub(pattern1, decode_match1, content)
        
        # 模式2: 属性访问 ['\x6f\x70\x65\x6e'] 或 ["\x6f\x70\x65\x6e"]
        pattern2 = r'\[(["\'])((?:\\x[0-9a-fA-F]{2})+)\1\]'
        def decode_match2(match):
            quote = match.group(1)
            hex_str = match.group(2)
            decoded = decode_hex_sequence(hex_str)
            return f'["{decoded}"]'
        content = re.sub(pattern2, decode_match2, content)
        
        return content
    
    def decode_unicode_strings(self, content: str) -> str:
        """解码Unicode编码的字符串"""
        # 匹配模式：'\u006f' 或 "\u006f"
        pattern = r'(["\'])((?:\\u[0-9a-fA-F]{4})+)\1'
        
        def decode_match(match):
            quote = match.group(1)
            unicode_str = match.group(2)
            
            # 解码Unicode序列
            decoded = ''
            unicode_parts = re.findall(r'\\u([0-9a-fA-F]{4})', unicode_str)
            for unicode_part in unicode_parts:
                decoded += chr(int(unicode_part, 16))
            
            return f'{quote}{decoded}{quote}'
        
        return re.sub(pattern, decode_match, content)
    
    def decode_octal_strings(self, content: str) -> str:
        """解码八进制编码的字符串"""
        # 匹配模式：'\141' 或 "\141"
        pattern = r'(["\'])((?:\\[0-7]{1,3})+)\1'
        
        def decode_match(match):
            quote = match.group(1)
            octal_str = match.group(2)
            
            # 解码八进制序列
            decoded = ''
            octal_parts = re.findall(r'\\([0-7]{1,3})', octal_str)
            for octal_part in octal_parts:
                decoded += chr(int(octal_part, 8))
            
            return f'{quote}{decoded}{quote}'
        
        return re.sub(pattern, decode_match, content)
    
    def replace_common_properties(self, content: str) -> str:
        """替换常见的混淆属性名（在已解码的字符串中）"""
        # 这个方法在decode_hex_strings之后调用，所以字符串已经被解码了
        # 这里主要是为了处理一些特殊情况
        return content
    
    def add_comments_for_common_patterns(self, content: str) -> str:
        """为常见模式添加注释"""
        # 这个方法可能会很慢，对于大文件可以跳过
        # 或者只在特定行添加注释
        return content
    
    def deobfuscate(self, content: str) -> str:
        """执行反混淆"""
        print("  [1/6] 解码十六进制字符串...")
        content = self.decode_hex_strings(content)
        
        print("  [2/6] 解码Unicode字符串...")
        content = self.decode_unicode_strings(content)
        
        print("  [3/6] 解码八进制字符串...")
        content = self.decode_octal_strings(content)
        
        print("  [4/6] 替换常见属性名...")
        content = self.replace_common_properties(content)
        
        print("  [5/6] 添加注释...")
        content = self.add_comments_for_common_patterns(content)
        
        print("  [6/6] 完成!")
        
        return content
    
    def deobfuscate_file(self, input_file: str, output_file: str = None) -> str:
        """反混淆文件"""
        print(f"\n处理文件: {input_file}")
        
        if not os.path.exists(input_file):
            print(f"  ❌ 文件不存在: {input_file}")
            return None
        
        # 读取文件
        print("  读取文件...")
        try:
            with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"  ❌ 读取文件失败: {e}")
            return None
        
        print(f"  文件大小: {len(content)} 字符")
        
        # 反混淆
        deobfuscated = self.deobfuscate(content)
        
        # 保存文件
        if output_file is None:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_deobfuscated.js"
        
        print(f"  保存到: {output_file}")
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(deobfuscated)
            print(f"  ✅ 保存成功")
            return output_file
        except Exception as e:
            print(f"  ❌ 保存失败: {e}")
            return None


def main():
    """主函数"""
    print("=" * 60)
    print("JavaScript反混淆工具")
    print("=" * 60)
    
    deobfuscator = JavaScriptDeobfuscator()
    
    # 要处理的文件列表
    files_to_process = [
        '7zl.js',
        '7zlplayer.js',
    ]
    
    results = []
    
    for file_name in files_to_process:
        if os.path.exists(file_name):
            output_file = deobfuscator.deobfuscate_file(file_name)
            if output_file:
                results.append({
                    'input': file_name,
                    'output': output_file,
                    'status': 'success'
                })
        else:
            print(f"\n⚠️  文件不存在: {file_name}")
            results.append({
                'input': file_name,
                'output': None,
                'status': 'not_found'
            })
    
    # 总结
    print("\n" + "=" * 60)
    print("处理完成")
    print("=" * 60)
    
    for result in results:
        if result['status'] == 'success':
            print(f"✅ {result['input']} -> {result['output']}")
        else:
            print(f"❌ {result['input']} - 文件不存在")
    
    print("\n💡 提示:")
    print("  - 反混淆后的文件可以更容易搜索关键字")
    print("  - 可以在反混淆后的文件中搜索: m3u8, cachem3u8, Cache, token等")
    print("  - 变量名仍然是混淆的，但字符串已经还原")


if __name__ == '__main__':
    main()

