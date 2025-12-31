"""
简化版 token 测试 - 直接使用解密逻辑测试
"""

import json
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad


def test_token_decrypt():
    """测试 token 解密"""
    # 从捕获数据中读取 token
    with open('captured_jx_m3u8_tv_params.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 提取 token
    token = None
    for params in data.get('captured_params', []):
        if 'token' in params:
            token = params['token']
            break
    
    if not token:
        print("未找到 token")
        return
    
    print(f"Token: {token[:50]}...")
    print(f"Token长度: {len(token)} 字符 ({len(token)//2} 字节)")
    
    # 转换为字节
    token_bytes = bytes.fromhex(token)
    print(f"Token字节长度: {len(token_bytes)} 字节")
    
    # 尝试不同的 uid 值
    uid_candidates = [
        None,  # 无 uid
        'test',  # 测试值
        '12345',  # 数字
    ]
    
    # Key生成方式
    iv_str = '2F131BE91247866E'
    iv_methods = [
        ("UTF-8编码", iv_str.encode('utf-8')),
        ("十六进制+填充", bytes.fromhex(iv_str).ljust(16, b'\0')),
        ("重复填充", (bytes.fromhex(iv_str) * 2)[:16]),
    ]
    
    print("\n尝试解密 token...")
    
    for uid in uid_candidates:
        if uid:
            key_str = '2890' + uid + 'tB959C'
        else:
            key_str = '2890' + 'tB959C'
        
        key_bytes = key_str.encode('utf-8')
        
        # 生成密钥
        key_methods = [
            ("MD5", hashlib.md5(key_bytes).digest()),
            ("SHA256前16", hashlib.sha256(key_bytes).digest()[:16]),
            ("SHA256前24", hashlib.sha256(key_bytes).digest()[:24]),
            ("SHA256前32", hashlib.sha256(key_bytes).digest()[:32]),
        ]
        
        for key_name, key in key_methods:
            if len(key) not in [16, 24, 32]:
                continue
            
            for iv_name, iv in iv_methods:
                if len(iv) != 16:
                    if len(iv) < 16:
                        iv = iv.ljust(16, b'\0')
                    else:
                        iv = iv[:16]
                
                try:
                    cipher = AES.new(key, AES.MODE_CBC, iv)
                    decrypted = cipher.decrypt(token_bytes)
                    
                    try:
                        decrypted_unpadded = unpad(decrypted, AES.block_size)
                        result = decrypted_unpadded.decode('utf-8')
                        
                        print(f"\n[成功] 解密成功！")
                        print(f"  UID: {uid}")
                        print(f"  Key方式: {key_name}")
                        print(f"  IV方式: {iv_name}")
                        print(f"  解密结果: {result[:200]}")
                        return result
                    except ValueError:
                        # 手动移除填充
                        try:
                            padding_len = decrypted[-1]
                            if 1 <= padding_len <= 16:
                                decrypted_manual = decrypted[:-padding_len]
                                result_manual = decrypted_manual.decode('utf-8')
                                
                                print(f"\n[成功] 手动移除填充后解密成功！")
                                print(f"  UID: {uid}")
                                print(f"  Key方式: {key_name}")
                                print(f"  IV方式: {iv_name}")
                                print(f"  解密结果: {result_manual[:200]}")
                                return result_manual
                        except:
                            pass
                except Exception:
                    continue
    
    print("\n[失败] 无法解密 token")
    return None


if __name__ == '__main__':
    test_token_decrypt()


