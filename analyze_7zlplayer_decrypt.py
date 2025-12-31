"""
分析 7zlplayer.js 中的解密相关逻辑
处理混淆代码，查找token生成和解密函数
"""

import re
import json
import os
from typing import Dict, List, Optional, Tuple


class JSObfuscationAnalyzer:
    """JavaScript混淆代码分析器"""
    
    def __init__(self, js_file_path: str):
        """初始化分析器"""
        self.js_file_path = js_file_path
        self.js_code = ""
        self.decoded_strings = {}  # 存储解码后的字符串
        
    def load_js_file(self):
        """加载JavaScript文件"""
        try:
            with open(self.js_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                self.js_code = f.read()
            print(f"[OK] 成功加载文件: {self.js_file_path}")
            print(f"     文件大小: {len(self.js_code)} 字符")
            
            # 检查是否是单行文件（混淆压缩）
            lines = self.js_code.split('\n')
            if len(lines) <= 3:
                print(f"     [INFO] 这是单行压缩文件（混淆代码）")
                # 尝试格式化（添加换行）
                self.js_code = self.js_code.replace(';', ';\n').replace('{', '{\n').replace('}', '\n}\n')
                print(f"     [INFO] 已格式化代码以便分析")
            
            return True
        except Exception as e:
            print(f"[ERROR] 加载文件失败: {e}")
            return False
    
    def decode_hex_strings(self, code: str) -> str:
        """解码十六进制字符串（如 '\\x79\\x72\\x51\\x78\\x66'）"""
        def hex_replace(match):
            hex_str = match.group(1)
            try:
                # 解码十六进制字符串
                decoded = bytes.fromhex(hex_str.replace('\\x', '')).decode('utf-8', errors='ignore')
                return f'"{decoded}"'  # 用引号包裹以便识别
            except:
                return match.group(0)
        
        # 匹配 \xXX 格式的十六进制字符串
        pattern = r'["\']((?:\\x[0-9a-fA-F]{2})+)["\']'
        decoded_code = re.sub(pattern, hex_replace, code)
        return decoded_code
    
    def extract_hex_strings(self) -> List[Dict]:
        """提取所有十六进制字符串并解码"""
        hex_strings = []
        
        # 匹配十六进制字符串模式
        patterns = [
            r'["\']((?:\\x[0-9a-fA-F]{2})+)["\']',  # '\\x79\\x72\\x51\\x78\\x66'
            r'["\']((?:\\u[0-9a-fA-F]{4})+)["\']',  # Unicode转义
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, self.js_code)
            for match in matches:
                hex_str = match.group(1)
                try:
                    if '\\x' in hex_str:
                        # 解码十六进制
                        decoded = bytes.fromhex(hex_str.replace('\\x', '')).decode('utf-8', errors='ignore')
                    elif '\\u' in hex_str:
                        # 解码Unicode
                        decoded = hex_str.encode().decode('unicode_escape')
                    else:
                        decoded = hex_str
                    
                    hex_strings.append({
                        'original': match.group(0),
                        'hex': hex_str,
                        'decoded': decoded,
                        'position': match.start(),
                        'context': self.js_code[max(0, match.start()-50):min(len(self.js_code), match.end()+50)]
                    })
                except Exception as e:
                    pass
        
        return hex_strings
    
    def find_decrypt_functions(self) -> List[Dict]:
        """查找解密相关函数"""
        findings = []
        
        # 解密相关的关键字模式
        decrypt_patterns = [
            # 函数定义
            r'(?:function\s+)?[_$a-zA-Z][_$a-zA-Z0-9]*\s*[:=]\s*function\s*\([^)]*\)\s*{[^}]*decrypt[^}]*}',
            r'(?:function\s+)?[_$a-zA-Z][_$a-zA-Z0-9]*\s*[:=]\s*function\s*\([^)]*\)\s*{[^}]*\.decrypt[^}]*}',
            r'(?:function\s+)?[_$a-zA-Z][_$a-zA-Z0-9]*\s*[:=]\s*function\s*\([^)]*\)\s*{[^}]*AES[^}]*}',
            r'(?:function\s+)?[_$a-zA-Z][_$a-zA-Z0-9]*\s*[:=]\s*function\s*\([^)]*\)\s*{[^}]*CryptoJS[^}]*}',
            # 方法调用
            r'\.decrypt\s*\([^)]*\)',
            r'\.encrypt\s*\([^)]*\)',
            r'AES\.(?:encrypt|decrypt)\s*\(',
            r'CryptoJS\.AES\.(?:encrypt|decrypt)\s*\(',
            r'CryptoJS\.decrypt\s*\(',
            # RC4相关
            r'rc4\s*\([^)]*\)',
            r'RC4\s*\([^)]*\)',
        ]
        
        for pattern in decrypt_patterns:
            matches = re.finditer(pattern, self.js_code, re.IGNORECASE | re.DOTALL)
            for match in matches:
                start = max(0, match.start() - 200)
                end = min(len(self.js_code), match.end() + 200)
                context = self.js_code[start:end]
                
                findings.append({
                    'pattern': pattern,
                    'match': match.group(0),
                    'position': match.start(),
                    'context': context,
                    'line': self.js_code[:match.start()].count('\n') + 1
                })
        
        return findings
    
    def find_token_generation(self) -> List[Dict]:
        """查找token生成相关代码"""
        findings = []
        
        # Token相关模式
        token_patterns = [
            r'token\s*[:=]\s*["\']?([^"\';,}\]]+)["\']?',
            r'["\']token["\']\s*[:=]\s*["\']?([^"\';,}\]]+)["\']?',
            r'\?token=([^&\s"\']+)',
            r'cachem3u8[^"\']*token=([^&\s"\']+)',
            r'Cache/[^"\']*\.m3u8[^"\']*token=([^&\s"\']+)',
        ]
        
        for pattern in token_patterns:
            matches = re.finditer(pattern, self.js_code, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 300)
                end = min(len(self.js_code), match.end() + 300)
                context = self.js_code[start:end]
                
                findings.append({
                    'pattern': pattern,
                    'match': match.group(0),
                    'value': match.group(1) if match.groups() else None,
                    'position': match.start(),
                    'context': context,
                    'line': self.js_code[:match.start()].count('\n') + 1
                })
        
        return findings
    
    def find_crypto_functions(self) -> List[Dict]:
        """查找加密函数调用"""
        findings = []
        
        crypto_patterns = [
            # MD5
            r'md5\s*\([^)]*\)',
            r'MD5\s*\([^)]*\)',
            r'CryptoJS\.MD5\s*\(',
            r'hashlib\.md5',
            # SHA
            r'sha256\s*\([^)]*\)',
            r'SHA256\s*\([^)]*\)',
            r'CryptoJS\.SHA256\s*\(',
            r'sha1\s*\([^)]*\)',
            r'SHA1\s*\([^)]*\)',
            # AES
            r'AES\.(?:encrypt|decrypt|new)\s*\(',
            r'CryptoJS\.AES\.(?:encrypt|decrypt)\s*\(',
            # Base64
            r'base64\s*\([^)]*\)',
            r'Base64\s*\([^)]*\)',
            r'btoa\s*\(',
            r'atob\s*\(',
            # 其他
            r'encrypt\s*\([^)]*\)',
            r'decrypt\s*\([^)]*\)',
            r'CryptoJS\.[A-Za-z]+\s*\(',
        ]
        
        for pattern in crypto_patterns:
            matches = re.finditer(pattern, self.js_code, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 200)
                end = min(len(self.js_code), match.end() + 200)
                context = self.js_code[start:end]
                
                findings.append({
                    'pattern': pattern,
                    'match': match.group(0),
                    'position': match.start(),
                    'context': context,
                    'line': self.js_code[:match.start()].count('\n') + 1
                })
        
        return findings
    
    def find_config_usage(self) -> List[Dict]:
        """查找ConFig对象的使用"""
        findings = []
        
        config_patterns = [
            r'ConFig\s*\.\s*(url|id|uid|config|token)',
            r'config\s*\.\s*(url|id|uid|token)',
            r'window\.ConFig',
            r'ConFig\[["\'](url|id|uid|token)["\']\]',
        ]
        
        for pattern in config_patterns:
            matches = re.finditer(pattern, self.js_code, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 200)
                end = min(len(self.js_code), match.end() + 200)
                context = self.js_code[start:end]
                
                findings.append({
                    'pattern': pattern,
                    'match': match.group(0),
                    'property': match.group(1) if match.groups() else None,
                    'position': match.start(),
                    'context': context,
                    'line': self.js_code[:match.start()].count('\n') + 1
                })
        
        return findings
    
    def find_api_calls(self) -> List[Dict]:
        """查找API调用"""
        findings = []
        
        api_patterns = [
            r'["\'](/admin/api\.php[^"\']*)["\']',
            r'["\'](https?://[^"\']+api[^"\']+)["\']',
            r'fetch\s*\(\s*["\']([^"\']+api[^"\']+)["\']',
            r'\.get\s*\(\s*["\']([^"\']+api[^"\']+)["\']',
            r'\.post\s*\(\s*["\']([^"\']+api[^"\']+)["\']',
            r'ajax\s*\([^)]*["\']([^"\']+api[^"\']+)["\']',
        ]
        
        for pattern in api_patterns:
            matches = re.finditer(pattern, self.js_code, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 200)
                end = min(len(self.js_code), match.end() + 200)
                context = self.js_code[start:end]
                
                findings.append({
                    'pattern': pattern,
                    'match': match.group(0),
                    'url': match.group(1) if match.groups() else None,
                    'position': match.start(),
                    'context': context,
                    'line': self.js_code[:match.start()].count('\n') + 1
                })
        
        return findings
    
    def find_key_iv_patterns(self) -> List[Dict]:
        """查找密钥和IV相关的模式"""
        findings = []
        
        key_iv_patterns = [
            # 密钥相关（包括混淆后的十六进制）
            r'key\s*[:=]\s*["\']?([^"\';,}\]]+)["\']?',
            r'["\']key["\']\s*[:=]\s*["\']?([^"\';,}\]]+)["\']?',
            r'2890[^"\']*tB959C',  # 密钥生成模式
            r'\\x32\\x38\\x39\\x30',  # 2890的十六进制
            # IV相关
            r'iv\s*[:=]\s*["\']?([^"\';,}\]]+)["\']?',
            r'["\']iv["\']\s*[:=]\s*["\']?([^"\';,}\]]+)["\']?',
            r'2F131BE91247866E',  # IV值
            r'\\x32\\x46\\x31\\x33\\x31\\x42\\x45\\x39\\x31\\x32\\x34\\x37\\x38\\x36\\x36\\x45',  # IV的十六进制
            # 密钥生成
            r'md5\s*\([^)]*2890[^)]*\)',
            r'MD5\s*\([^)]*2890[^)]*\)',
            # 混淆后的模式
            r'\\x[0-9a-fA-F]{2}.*2890',
            r'\\x[0-9a-fA-F]{2}.*tB959C',
        ]
        
        for pattern in key_iv_patterns:
            matches = re.finditer(pattern, self.js_code, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 200)
                end = min(len(self.js_code), match.end() + 200)
                context = self.js_code[start:end]
                
                findings.append({
                    'pattern': pattern,
                    'match': match.group(0),
                    'value': match.group(1) if match.groups() else None,
                    'position': match.start(),
                    'context': context,
                    'line': self.js_code[:match.start()].count('\n') + 1
                })
        
        return findings
    
    def extract_function_bodies(self, function_name_pattern: str) -> List[Dict]:
        """提取特定函数的函数体"""
        findings = []
        
        # 匹配函数定义
        pattern = rf'(?:function\s+)?{function_name_pattern}\s*[:=]\s*function\s*\([^)]*\)\s*{{([^}}]*(?:{{[^}}]*}}[^}}]*)*)}}'
        
        matches = re.finditer(pattern, self.js_code, re.IGNORECASE | re.DOTALL)
        for match in matches:
            function_body = match.group(1)
            findings.append({
                'function': match.group(0)[:100],
                'body': function_body,
                'position': match.start(),
                'line': self.js_code[:match.start()].count('\n') + 1
            })
        
        return findings
    
    def analyze(self) -> Dict:
        """执行完整分析"""
        print("=" * 60)
        print("分析 7zlplayer.js 中的解密相关逻辑")
        print("=" * 60)
        
        if not self.load_js_file():
            return {}
        
        print("\n[步骤1] 提取十六进制字符串...")
        hex_strings = self.extract_hex_strings()
        print(f"   [OK] 找到 {len(hex_strings)} 个十六进制字符串")
        
        # 显示一些解码后的字符串
        if hex_strings:
            print(f"\n   解码示例（前10个）:")
            for i, hs in enumerate(hex_strings[:10], 1):
                if hs['decoded'] and len(hs['decoded']) > 0:
                    print(f"   [{i}] {hs['decoded'][:50]}...")
        
        print("\n[步骤2] 查找解密函数...")
        decrypt_functions = self.find_decrypt_functions()
        print(f"   [OK] 找到 {len(decrypt_functions)} 个解密相关函数/调用")
        
        if decrypt_functions:
            print(f"\n   解密函数示例（前5个）:")
            for i, df in enumerate(decrypt_functions[:5], 1):
                print(f"   [{i}] 行 {df['line']}: {df['match'][:80]}...")
        
        print("\n[步骤3] 查找token生成...")
        token_patterns = self.find_token_generation()
        print(f"   [OK] 找到 {len(token_patterns)} 个token相关模式")
        
        if token_patterns:
            print(f"\n   Token模式示例（前5个）:")
            for i, tp in enumerate(token_patterns[:5], 1):
                print(f"   [{i}] 行 {tp['line']}: {tp['match'][:80]}...")
        
        print("\n[步骤4] 查找加密函数...")
        crypto_functions = self.find_crypto_functions()
        print(f"   [OK] 找到 {len(crypto_functions)} 个加密函数调用")
        
        if crypto_functions:
            print(f"\n   加密函数示例（前5个）:")
            for i, cf in enumerate(crypto_functions[:5], 1):
                print(f"   [{i}] 行 {cf['line']}: {cf['match'][:80]}...")
        
        print("\n[步骤5] 查找ConFig使用...")
        config_usage = self.find_config_usage()
        print(f"   [OK] 找到 {len(config_usage)} 个ConFig使用")
        
        if config_usage:
            print(f"\n   ConFig使用示例（前5个）:")
            for i, cu in enumerate(config_usage[:5], 1):
                print(f"   [{i}] 行 {cu['line']}: {cu['match'][:80]}...")
        
        print("\n[步骤6] 查找API调用...")
        api_calls = self.find_api_calls()
        print(f"   [OK] 找到 {len(api_calls)} 个API调用")
        
        if api_calls:
            print(f"\n   API调用示例（前5个）:")
            for i, ac in enumerate(api_calls[:5], 1):
                print(f"   [{i}] 行 {ac['line']}: {ac.get('url', ac['match'])[:80]}...")
        
        print("\n[步骤7] 查找密钥和IV模式...")
        key_iv_patterns = self.find_key_iv_patterns()
        print(f"   [OK] 找到 {len(key_iv_patterns)} 个密钥/IV相关模式")
        
        if key_iv_patterns:
            print(f"\n   密钥/IV模式示例（前5个）:")
            for i, kiv in enumerate(key_iv_patterns[:5], 1):
                print(f"   [{i}] 行 {kiv['line']}: {kiv['match'][:80]}...")
        
        # 汇总结果
        result = {
            'file': self.js_file_path,
            'file_size': len(self.js_code),
            'hex_strings': hex_strings[:50],  # 只保存前50个
            'decrypt_functions': decrypt_functions,
            'token_patterns': token_patterns,
            'crypto_functions': crypto_functions,
            'config_usage': config_usage,
            'api_calls': api_calls,
            'key_iv_patterns': key_iv_patterns
        }
        
        return result
    
    def save_analysis_result(self, result: Dict, output_file: str = '7zlplayer_analysis.json'):
        """保存分析结果"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)
            print(f"\n[OK] 分析结果已保存到: {output_file}")
        except Exception as e:
            print(f"\n[ERROR] 保存分析结果失败: {e}")
    
    def extract_key_code_snippets(self, result: Dict) -> List[str]:
        """提取关键代码片段"""
        snippets = []
        
        # 合并所有找到的位置
        all_positions = []
        
        for category in ['decrypt_functions', 'token_patterns', 'crypto_functions', 'key_iv_patterns']:
            for item in result.get(category, []):
                all_positions.append({
                    'position': item['position'],
                    'category': category,
                    'match': item.get('match', ''),
                    'context': item.get('context', '')
                })
        
        # 按位置排序
        all_positions.sort(key=lambda x: x['position'])
        
        # 提取代码片段（每个片段500字符）
        for item in all_positions[:20]:  # 只提取前20个
            pos = item['position']
            start = max(0, pos - 250)
            end = min(len(self.js_code), pos + 250)
            snippet = self.js_code[start:end]
            snippets.append({
                'category': item['category'],
                'match': item['match'],
                'snippet': snippet,
                'position': pos
            })
        
        return snippets


def main():
    """主函数"""
    js_file = 'downloaded_js/7zlplayer.js'
    
    if not os.path.exists(js_file):
        print(f"[ERROR] 文件不存在: {js_file}")
        print(f"请确保文件存在于 downloaded_js/ 目录中")
        return
    
    analyzer = JSObfuscationAnalyzer(js_file)
    result = analyzer.analyze()
    
    if result:
        # 保存分析结果
        analyzer.save_analysis_result(result)
        
        # 提取关键代码片段
        snippets = analyzer.extract_key_code_snippets(result)
        
        # 保存关键代码片段
        snippets_file = '7zlplayer_key_snippets.json'
        with open(snippets_file, 'w', encoding='utf-8') as f:
            json.dump(snippets, f, indent=2, ensure_ascii=False, default=str)
        print(f"[OK] 关键代码片段已保存到: {snippets_file}")
        
        # 打印总结
        print("\n" + "=" * 60)
        print("[总结]")
        print("=" * 60)
        print(f"文件大小: {result['file_size']} 字符")
        print(f"十六进制字符串: {len(result['hex_strings'])} 个")
        print(f"解密函数: {len(result['decrypt_functions'])} 个")
        print(f"Token模式: {len(result['token_patterns'])} 个")
        print(f"加密函数: {len(result['crypto_functions'])} 个")
        print(f"ConFig使用: {len(result['config_usage'])} 个")
        print(f"API调用: {len(result['api_calls'])} 个")
        print(f"密钥/IV模式: {len(result['key_iv_patterns'])} 个")
        
        # 如果有重要发现，突出显示
        if result['decrypt_functions']:
            print(f"\n[重要] 找到 {len(result['decrypt_functions'])} 个解密相关函数！")
            print(f"   建议查看: 7zlplayer_analysis.json 中的 'decrypt_functions' 部分")
        
        if result['token_patterns']:
            print(f"\n[重要] 找到 {len(result['token_patterns'])} 个token相关模式！")
            print(f"   建议查看: 7zlplayer_analysis.json 中的 'token_patterns' 部分")
        
        if result['key_iv_patterns']:
            print(f"\n[重要] 找到 {len(result['key_iv_patterns'])} 个密钥/IV相关模式！")
            print(f"   建议查看: 7zlplayer_analysis.json 中的 'key_iv_patterns' 部分")


if __name__ == '__main__':
    main()

