"""
直接分析 jx.2s0.cn token 结构（不使用emoji）
"""

import json
import re
import hashlib
import base64
from urllib.parse import urlparse, parse_qs

# 从分析结果中提取的token
TOKEN = "d3d376b2430527a424a613e4e6960775f4b286978765a59603a62315e416c4b48727f69473e6a7966793667783033744a66624f4b2c615a55776e666656695a7f41305a5e4c474a457e687942753033564776684234656e6"
M3U8_URL = "https://cachem3u8.2s0.cn:8899/Cache/LZ/4e7a11f1eb74b1fbe7b5c6359d501c3d.m3u8?token=" + TOKEN

def analyze_token():
    """分析token结构"""
    print("=" * 80)
    print("Token Structure Analysis")
    print("=" * 80)
    
    print(f"\nToken Info:")
    print(f"  Length: {len(TOKEN)} characters")
    print(f"  Content: {TOKEN}")
    
    # 1. 字符集分析
    print("\n" + "=" * 80)
    print("1. Charset Analysis")
    print("=" * 80)
    
    token_chars = set(TOKEN)
    hex_chars = set('0123456789abcdefABCDEF')
    is_hex = token_chars.issubset(hex_chars)
    
    print(f"\n  Charset Features:")
    print(f"  Is Hex: {is_hex}")
    print(f"  Unique chars: {len(token_chars)}")
    print(f"  Charset: {''.join(sorted(list(token_chars))[:50])}")
    
    # 字符频率
    char_freq = {}
    for char in TOKEN:
        char_freq[char] = char_freq.get(char, 0) + 1
    
    sorted_chars = sorted(char_freq.items(), key=lambda x: x[1], reverse=True)
    print(f"\n  Top 10 Character Frequency:")
    for char, freq in sorted_chars[:10]:
        percentage = (freq / len(TOKEN)) * 100
        print(f"    '{char}': {freq} times ({percentage:.1f}%)")
    
    # 2. 编码分析
    print("\n" + "=" * 80)
    print("2. Encoding Analysis")
    print("=" * 80)
    
    if is_hex:
        try:
            decoded_bytes = bytes.fromhex(TOKEN)
            print(f"\n  Hex Decoding:")
            print(f"  Byte length: {len(decoded_bytes)}")
            print(f"  First 100 bytes (hex): {decoded_bytes[:100].hex()}")
            
            # UTF-8解码
            try:
                decoded_utf8 = decoded_bytes.decode('utf-8', errors='ignore')
                print(f"  UTF-8 decoded: {decoded_utf8[:200]}")
            except:
                print(f"  UTF-8 decode failed")
            
            # Base64编码
            try:
                base64_encoded = base64.b64encode(decoded_bytes).decode('utf-8')
                print(f"  Base64 encoded: {base64_encoded[:100]}...")
            except:
                pass
        except Exception as e:
            print(f"  Hex decode failed: {e}")
    
    # 3. 模式分析
    print("\n" + "=" * 80)
    print("3. Pattern Analysis")
    print("=" * 80)
    
    # 检查前缀
    if len(TOKEN) > 10:
        prefix = TOKEN[:10]
        suffix = TOKEN[-10:]
        print(f"\n  Prefix: {prefix}")
        print(f"  Suffix: {suffix}")
        
        if prefix.lower().startswith('d3d3') or prefix.lower().startswith('d3d'):
            print(f"  [NOTE] Prefix '{prefix}' might be an identifier")
    
    # 4. URL结构分析
    print("\n" + "=" * 80)
    print("4. URL Structure Analysis")
    print("=" * 80)
    
    parsed = urlparse(M3U8_URL)
    print(f"\n  URL Components:")
    print(f"  Scheme: {parsed.scheme}")
    print(f"  Domain: {parsed.netloc}")
    print(f"  Path: {parsed.path}")
    
    # 提取路径中的hash
    path_parts = parsed.path.split('/')
    for part in path_parts:
        if len(part) == 32 and all(c in '0123456789abcdef' for c in part.lower()):
            print(f"\n  [NOTE] Hash in path (possibly MD5): {part}")
    
    # 5. 生成方式推测
    print("\n" + "=" * 80)
    print("5. Possible Generation Methods")
    print("=" * 80)
    
    print("\n  Suggested Methods:")
    print("\n  [1] Hex-encoded Encrypted Data")
    print("      Description: Token might be encrypted data (AES, RC4, etc.) converted to hex")
    print("      Steps:")
    print("        1. Encrypt data (URL, timestamp, ID, etc.) with some key/algorithm")
    print("        2. Convert encrypted binary to hex string")
    print("        3. Use as token")
    
    print("\n  [2] Hash Value")
    print("      Description: Token might be a hash value (MD5/SHA1/SHA256)")
    print("      Steps:")
    print("        1. Hash some data (config.id, video_url, etc.)")
    print("        2. Convert hash to hex string")
    print("        3. Use as token")
    
    print("\n  [3] Combined Hash")
    print("      Description: Token might be hash of combined data")
    print("      Steps:")
    print("        1. Combine multiple data (config.id + video_url + timestamp)")
    print("        2. Hash the combined data")
    print("        3. Convert to hex string")
    print("        4. Use as token")
    
    print("\n  [4] Encrypted Signature")
    print("      Description: Token might be a signature using a key")
    print("      Steps:")
    print("        1. Sign data with a key (possibly config.id or other)")
    print("        2. Signature algorithm might be HMAC-SHA256, HMAC-MD5, etc.")
    print("        3. Convert signature to hex string")
    print("        4. Use as token")
    
    # 保存结果
    results = {
        'token': TOKEN,
        'm3u8_url': M3U8_URL,
        'length': len(TOKEN),
        'is_hex': is_hex,
        'charset': ''.join(sorted(list(token_chars))),
        'char_frequency': dict(sorted_chars[:20]),
        'prefix': TOKEN[:10] if len(TOKEN) > 10 else '',
        'suffix': TOKEN[-10:] if len(TOKEN) > 10 else ''
    }
    
    if is_hex:
        try:
            decoded_bytes = bytes.fromhex(TOKEN)
            results['hex_decoded'] = {
                'byte_length': len(decoded_bytes),
                'hex_preview': decoded_bytes[:100].hex()
            }
        except:
            pass
    
    output_file = 'token_structure_analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n[INFO] Analysis results saved to: {output_file}")

if __name__ == '__main__':
    analyze_token()

