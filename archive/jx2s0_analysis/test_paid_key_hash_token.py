#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试付费key的hash和token生成算法
"""

import hashlib
import base64
from Crypto.Cipher import ARC4
import hmac

def test_hash_generation():
    """测试hash生成算法"""
    print("="*80)
    print("测试Hash生成算法")
    print("="*80)
    
    uid = "4059917"
    key = "cgklotuyDGHILOTW38"
    video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    target_hash = "2089c333a6d6a31e306bd190557aea36"
    
    print(f"目标Hash: {target_hash}")
    print(f"uid: {uid}")
    print(f"key: {key}")
    print(f"video_url: {video_url}")
    print()
    
    # 测试不同的字符串组合
    test_cases = [
        # 格式: (字符串, 描述)
        (f"{uid}{key}{video_url}", "uid+key+video_url"),
        (f"{uid}{key}", "uid+key"),
        (f"{key}{video_url}", "key+video_url"),
        (f"{uid}{video_url}", "uid+video_url"),
        (video_url, "video_url"),
        (f"{key}", "key"),
        (f"{uid}", "uid"),
        # 添加URL编码版本
        (f"{uid}{key}{video_url.replace('https://', '')}", "uid+key+video_url(无协议)"),
        (f"{uid}{key}{video_url.split('/')[-1]}", "uid+key+视频ID"),
    ]
    
    print("测试MD5:")
    print("-"*80)
    for test_str, description in test_cases:
        md5_hash = hashlib.md5(test_str.encode()).hexdigest()
        match = "🎯 匹配！" if md5_hash == target_hash else ""
        print(f"{description:30} MD5: {md5_hash} {match}")
        if md5_hash == target_hash:
            print(f"  ✅ 找到匹配！")
            print(f"     输入字符串: {test_str}")
            return test_str, "MD5"
    
    print()
    print("测试SHA1:")
    print("-"*80)
    for test_str, description in test_cases:
        sha1_hash = hashlib.sha1(test_str.encode()).hexdigest()
        print(f"{description:30} SHA1: {sha1_hash[:32]}...")
    
    print()
    print("测试SHA256:")
    print("-"*80)
    for test_str, description in test_cases:
        sha256_hash = hashlib.sha256(test_str.encode()).hexdigest()
        print(f"{description:30} SHA256: {sha256_hash[:32]}...")
    
    return None, None

def test_token_generation():
    """测试token生成算法"""
    print()
    print("="*80)
    print("测试Token生成算法")
    print("="*80)
    
    uid = "4059917"
    key = "cgklotuyDGHILOTW38"
    video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    target_token = "d3d37757e6345566e4e43623b4c614571477a447f43424e6265423b4365435376667f2259455247746c6a415744324c613f6547443a43443a626e6d40786a77334e4f487c64775b2474793b44567741794951513f62477e4"
    
    print(f"目标Token: {target_token[:100]}...")
    print(f"Token长度: {len(target_token)}")
    print()
    
    # 测试不同的字符串组合
    test_strings = [
        f"{uid}{key}{video_url}",
        f"{uid}{key}",
        f"{key}{video_url}",
        f"{uid}{video_url}",
        video_url,
    ]
    
    print("测试Base64编码:")
    print("-"*80)
    for test_str in test_strings:
        b64_encoded = base64.b64encode(test_str.encode()).decode()
        hex_encoded = b64_encoded.encode().hex()
        print(f"{test_str[:50]:50} Base64->Hex: {hex_encoded[:100]}...")
        if hex_encoded.startswith(target_token[:20]):
            print(f"  🎯 可能匹配！")
    
    print()
    print("测试RC4加密:")
    print("-"*80)
    possible_keys = [uid, key, f"{uid}{key}", f"{key}{uid}", f"{key} P"]
    for test_str in test_strings[:3]:  # 只测试前3个
        for rc4_key in possible_keys:
            try:
                cipher = ARC4.new(rc4_key.encode())
                encrypted = cipher.encrypt(test_str.encode())
                hex_encrypted = encrypted.hex()
                match = "🎯 可能匹配！" if hex_encrypted.startswith(target_token[:20]) else ""
                print(f"{test_str[:30]:30} RC4({rc4_key[:20]:20}) {hex_encrypted[:50]}... {match}")
            except Exception as e:
                pass
    
    print()
    print("测试HMAC:")
    print("-"*80)
    for test_str in test_strings:
        for hmac_key in [uid, key, f"{uid}{key}"]:
            hmac_md5 = hmac.new(hmac_key.encode(), test_str.encode(), hashlib.md5).hexdigest()
            hmac_sha1 = hmac.new(hmac_key.encode(), test_str.encode(), hashlib.sha1).hexdigest()
            print(f"{test_str[:30]:30} HMAC-MD5({hmac_key[:15]:15}): {hmac_md5[:50]}...")
            print(f"{'':30} HMAC-SHA1({hmac_key[:15]:15}): {hmac_sha1[:50]}...")

def main():
    """主函数"""
    # 测试hash
    hash_input, hash_algorithm = test_hash_generation()
    
    # 测试token
    test_token_generation()
    
    print()
    print("="*80)
    print("测试完成！")
    print("="*80)
    
    if hash_input:
        print(f"\n✅ Hash生成算法:")
        print(f"   算法: {hash_algorithm}")
        print(f"   输入: {hash_input}")
    else:
        print("\n⚠️ 未找到Hash生成算法，可能需要:")
        print("   1. 测试更多的字符串组合")
        print("   2. 测试不同的编码方式")
        print("   3. 分析服务器端代码")

if __name__ == "__main__":
    main()

