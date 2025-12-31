"""
分析 jx.2s0.cn token 结构
分析已捕获的token，尝试理解其生成方式
"""

import json
import re
import hashlib
import base64
from urllib.parse import urlparse, parse_qs
from typing import Dict, Optional


class TokenStructureAnalyzer:
    """Token结构分析器"""
    
    def __init__(self, token: str, m3u8_url: Optional[str] = None):
        self.token = token
        self.m3u8_url = m3u8_url
        self.analysis_results = {}
    
    def analyze(self):
        """执行完整分析"""
        print("=" * 80)
        print("🔬 Token 结构分析")
        print("=" * 80)
        
        print(f"\n📋 Token信息:")
        print(f"   长度: {len(self.token)} 字符")
        print(f"   完整内容: {self.token}")
        
        # 1. 字符集分析
        self._analyze_charset()
        
        # 2. 编码分析
        self._analyze_encoding()
        
        # 3. 模式分析
        self._analyze_patterns()
        
        # 4. URL结构分析
        if self.m3u8_url:
            self._analyze_url_structure()
        
        # 5. 可能的生成方式推测
        self._suggest_generation_methods()
        
        return self.analysis_results
    
    def _analyze_charset(self):
        """分析字符集"""
        print("\n" + "=" * 80)
        print("1️⃣  字符集分析")
        print("=" * 80)
        
        token_chars = set(self.token)
        hex_chars = set('0123456789abcdefABCDEF')
        alnum_chars = set('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        
        is_hex = token_chars.issubset(hex_chars)
        is_alnum = token_chars.issubset(alnum_chars)
        
        print(f"\n   字符集特征:")
        print(f"   是否为十六进制: {is_hex}")
        print(f"   是否为字母数字: {is_alnum}")
        print(f"   唯一字符数: {len(token_chars)}")
        print(f"   字符集: {''.join(sorted(list(token_chars))[:50])}")
        
        # 字符频率分析
        char_freq = {}
        for char in self.token:
            char_freq[char] = char_freq.get(char, 0) + 1
        
        sorted_chars = sorted(char_freq.items(), key=lambda x: x[1], reverse=True)
        print(f"\n   字符频率 (前10):")
        for char, freq in sorted_chars[:10]:
            percentage = (freq / len(self.token)) * 100
            print(f"     '{char}': {freq} 次 ({percentage:.1f}%)")
        
        self.analysis_results['charset'] = {
            'is_hex': is_hex,
            'is_alnum': is_alnum,
            'unique_chars': len(token_chars),
            'charset': ''.join(sorted(list(token_chars))),
            'char_frequency': dict(sorted_chars[:20])
        }
    
    def _analyze_encoding(self):
        """分析编码方式"""
        print("\n" + "=" * 80)
        print("2️⃣  编码分析")
        print("=" * 80)
        
        # 尝试十六进制解码
        hex_chars = set('0123456789abcdefABCDEF')
        if set(self.token).issubset(hex_chars):
            try:
                decoded_bytes = bytes.fromhex(self.token)
                print(f"\n   十六进制解码:")
                print(f"   字节长度: {len(decoded_bytes)}")
                print(f"   前100字节 (hex): {decoded_bytes[:100].hex()}")
                
                # 尝试UTF-8解码
                try:
                    decoded_utf8 = decoded_bytes.decode('utf-8', errors='ignore')
                    print(f"   UTF-8解码结果: {decoded_utf8[:200]}")
                    self.analysis_results['hex_decoded_utf8'] = decoded_utf8[:500]
                except:
                    print(f"   UTF-8解码失败")
                
                # 尝试Base64编码
                try:
                    base64_encoded = base64.b64encode(decoded_bytes).decode('utf-8')
                    print(f"   Base64编码: {base64_encoded[:100]}...")
                except:
                    pass
                
                self.analysis_results['hex_decoded_bytes'] = {
                    'length': len(decoded_bytes),
                    'hex_preview': decoded_bytes[:100].hex()
                }
            except Exception as e:
                print(f"   十六进制解码失败: {e}")
        
        # 尝试Base64解码
        try:
            base64_decoded = base64.b64decode(self.token + '==')  # 添加padding
            print(f"\n   Base64解码:")
            print(f"   字节长度: {len(base64_decoded)}")
            print(f"   前100字节 (hex): {base64_decoded[:100].hex()}")
            
            try:
                decoded_utf8 = base64_decoded.decode('utf-8', errors='ignore')
                print(f"   UTF-8解码结果: {decoded_utf8[:200]}")
                self.analysis_results['base64_decoded_utf8'] = decoded_utf8[:500]
            except:
                print(f"   UTF-8解码失败")
        except:
            print(f"\n   Base64解码失败（token不是Base64格式）")
    
    def _analyze_patterns(self):
        """分析模式"""
        print("\n" + "=" * 80)
        print("3️⃣  模式分析")
        print("=" * 80)
        
        # 检查重复模式
        patterns = []
        for length in range(2, min(20, len(self.token) // 4)):
            for i in range(len(self.token) - length):
                pattern = self.token[i:i+length]
                count = self.token.count(pattern)
                if count > 1:
                    patterns.append((pattern, count, i))
        
        if patterns:
            print(f"\n   发现重复模式:")
            unique_patterns = {}
            for pattern, count, pos in patterns:
                if pattern not in unique_patterns or unique_patterns[pattern][1] < count:
                    unique_patterns[pattern] = (count, pos)
            
            for pattern, (count, pos) in sorted(unique_patterns.items(), key=lambda x: x[1][1])[:10]:
                print(f"     '{pattern}' 出现 {count} 次 (首次位置: {pos})")
        else:
            print(f"\n   未发现明显的重复模式")
        
        # 检查是否有固定前缀/后缀
        if len(self.token) > 10:
            prefix = self.token[:10]
            suffix = self.token[-10:]
            print(f"\n   前缀: {prefix}")
            print(f"   后缀: {suffix}")
            
            # 检查前缀是否常见
            common_prefixes = ['d3d3', 'd3d', 'token', 'auth']
            if any(prefix.lower().startswith(p) for p in common_prefixes):
                print(f"   ⚠️  前缀 '{prefix}' 可能是标识符")
        
        self.analysis_results['patterns'] = {
            'repeated_patterns': dict(unique_patterns) if patterns else {},
            'prefix': self.token[:10] if len(self.token) > 10 else '',
            'suffix': self.token[-10:] if len(self.token) > 10 else ''
        }
    
    def _analyze_url_structure(self):
        """分析URL结构"""
        print("\n" + "=" * 80)
        print("4️⃣  URL结构分析")
        print("=" * 80)
        
        parsed = urlparse(self.m3u8_url)
        print(f"\n   URL组成部分:")
        print(f"   协议: {parsed.scheme}")
        print(f"   域名: {parsed.netloc}")
        print(f"   路径: {parsed.path}")
        print(f"   查询参数: {parsed.query}")
        
        # 提取路径中的hash
        path_parts = parsed.path.split('/')
        for part in path_parts:
            if len(part) == 32 and all(c in '0123456789abcdef' for c in part.lower()):
                print(f"\n   ⚠️  路径中的hash (可能是MD5): {part}")
                self.analysis_results['url_hash'] = part
        
        # 解析查询参数
        params = parse_qs(parsed.query)
        print(f"\n   查询参数:")
        for key, values in params.items():
            print(f"     {key}: {values[0][:50]}...")
    
    def _suggest_generation_methods(self):
        """推测可能的生成方式"""
        print("\n" + "=" * 80)
        print("5️⃣  可能的生成方式推测")
        print("=" * 80)
        
        suggestions = []
        
        # 1. 十六进制编码的加密数据
        hex_chars = set('0123456789abcdefABCDEF')
        if set(self.token).issubset(hex_chars):
            suggestions.append({
                'method': '十六进制编码的加密数据',
                'description': 'token可能是某种加密算法（如AES、RC4）的结果，然后转换为十六进制字符串',
                'steps': [
                    '1. 使用某种密钥和算法加密数据（可能是URL、时间戳、ID等）',
                    '2. 将加密后的二进制数据转换为十六进制字符串',
                    '3. 作为token使用'
                ]
            })
        
        # 2. 哈希值
        if len(self.token) in [32, 40, 64]:
            hash_type = {
                32: 'MD5',
                40: 'SHA1',
                64: 'SHA256'
            }.get(len(self.token), '未知')
            suggestions.append({
                'method': f'{hash_type}哈希值',
                'description': f'token可能是{hash_type}哈希值（长度匹配）',
                'steps': [
                    f'1. 对某些数据进行{hash_type}哈希',
                    '2. 将哈希值转换为十六进制字符串',
                    '3. 作为token使用'
                ]
            })
        
        # 3. 组合哈希
        suggestions.append({
            'method': '组合数据的哈希',
            'description': 'token可能是多个数据组合后的哈希值',
            'steps': [
                '1. 组合多个数据（如：config.id + video_url + timestamp）',
                '2. 对组合后的数据进行哈希（MD5/SHA1/SHA256）',
                '3. 将哈希值转换为十六进制字符串',
                '4. 作为token使用'
            ]
        })
        
        # 4. 加密签名
        suggestions.append({
            'method': '加密签名',
            'description': 'token可能是使用密钥对数据进行签名后的结果',
            'steps': [
                '1. 使用密钥（可能是config.id或其他）对数据进行签名',
                '2. 签名算法可能是HMAC-SHA256、HMAC-MD5等',
                '3. 将签名结果转换为十六进制字符串',
                '4. 作为token使用'
            ]
        })
        
        print(f"\n   推测的生成方式:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n   [{i}] {suggestion['method']}")
            print(f"       描述: {suggestion['description']}")
            print(f"       步骤:")
            for step in suggestion['steps']:
                print(f"         {step}")
        
        self.analysis_results['suggestions'] = suggestions
    
    def save_analysis(self, filename: str = 'token_structure_analysis.json'):
        """保存分析结果"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'token': self.token,
                'm3u8_url': self.m3u8_url,
                'analysis': self.analysis_results
            }, f, ensure_ascii=False, indent=2)
        print(f"\n💾 分析结果已保存到: {filename}")


def main():
    """主函数"""
    # 从分析结果文件中读取token
    try:
        with open('jx2s0_token_analysis.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if data.get('m3u8_urls'):
            m3u8_item = data['m3u8_urls'][0]
            token = m3u8_item['token']
            m3u8_url = m3u8_item['url']
            
            print(f"[INFO] 从 jx2s0_token_analysis.json 加载token")
            print(f"   URL: {m3u8_url}")
            print(f"   Token: {token[:50]}...")
            
            analyzer = TokenStructureAnalyzer(token, m3u8_url)
            analyzer.analyze()
            analyzer.save_analysis()
        else:
            print("[ERROR] 未找到m3u8 URL数据")
    except FileNotFoundError:
        print("[ERROR] 未找到 jx2s0_token_analysis.json 文件")
        print("   请先运行 analyze_jx2s0_token.py 或 deep_analyze_jx2s0_token.py")
    except Exception as e:
        print(f"[ERROR] 读取文件失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

