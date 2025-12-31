#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
扩展的付费key hash和token测试
测试更多的组合和编码方式
"""

import hashlib
import base64
from urllib.parse import quote, unquote, urlparse, parse_qs
from Crypto.Cipher import ARC4
import hmac
import time

def test_hash_extended():
    """扩展的hash测试"""
    print("="*80)
    print("扩展Hash测试")
    print("="*80)
    
    uid = "4059917"
    key = "cgklotuyDGHILOTW38"
    video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    target_hash = "2089c333a6d6a31e306bd190557aea36"
    
    print(f"目标Hash: {target_hash}")
    print()
    
    # 提取视频ID
    video_id = video_url.split('/')[-1].replace('.html', '')
    print(f"视频ID: {video_id}")
    print()
    
    # 更多测试用例
    test_cases = []
    
    # 基础组合
    test_cases.extend([
        (f"{uid}{key}{video_url}", "uid+key+video_url"),
        (f"{key}{uid}{video_url}", "key+uid+video_url"),
        (f"{video_url}{uid}{key}", "video_url+uid+key"),
        (f"{uid}{key}", "uid+key"),
        (f"{key}{uid}", "key+uid"),
    ])
    
    # URL编码版本
    test_cases.extend([
        (quote(f"{uid}{key}{video_url}"), "quote(uid+key+video_url)"),
        (quote(video_url), "quote(video_url)"),
    ])
    
    # 视频ID相关
    test_cases.extend([
        (f"{uid}{key}{video_id}", "uid+key+video_id"),
        (f"{key}{video_id}", "key+video_id"),
        (f"{uid}{video_id}", "uid+video_id"),
        (video_id, "video_id"),
    ])
    
    # 去除协议
    video_url_no_protocol = video_url.replace('https://', '').replace('http://', '')
    test_cases.extend([
        (f"{uid}{key}{video_url_no_protocol}", "uid+key+video_url(无协议)"),
        (video_url_no_protocol, "video_url(无协议)"),
    ])
    
    # 时间戳相关（可能包含时间）
    timestamp = int(time.time())
    test_cases.extend([
        (f"{uid}{key}{video_url}{timestamp}", f"uid+key+video_url+timestamp({timestamp})"),
        (f"{uid}{key}{timestamp}", f"uid+key+timestamp({timestamp})"),
    ])
    
    # 特殊格式
    test_cases.extend([
        (f"{uid}|{key}|{video_url}", "uid|key|video_url"),
        (f"{uid}_{key}_{video_url}", "uid_key_video_url"),
        (f"{uid}-{key}-{video_url}", "uid-key-video_url"),
    ])
    
    print("测试MD5:")
    print("-"*80)
    matches = []
    for test_str, description in test_cases:
        md5_hash = hashlib.md5(test_str.encode()).hexdigest()
        if md5_hash == target_hash:
            matches.append((description, test_str))
            print(f"🎯 {description:40} MD5: {md5_hash} ✅ 匹配！")
        else:
            print(f"   {description:40} MD5: {md5_hash}")
    
    if matches:
        print()
        print("✅ 找到匹配的Hash生成方式:")
        for desc, test_str in matches:
            print(f"   {desc}: {test_str}")
    else:
        print()
        print("⚠️ 未找到匹配的MD5")
        print("   可能的原因:")
        print("   1. Hash是基于服务器端数据生成的（如数据库ID）")
        print("   2. Hash使用了其他参数（如时间戳、随机数等）")
        print("   3. Hash使用了不同的编码方式")
        print("   4. Hash是基于视频URL的某种处理结果")
    
    return matches

def test_token_extended():
    """扩展的token测试"""
    print()
    print("="*80)
    print("扩展Token测试")
    print("="*80)
    
    uid = "4059917"
    key = "cgklotuyDGHILOTW38"
    video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    target_token = "d3d37757e6345566e4e43623b4c614571477a447f43424e6265423b4365435376667f2259455247746c6a415744324c613f6547443a43443a626e6d40786a77334e4f487c64775b2474793b44567741794951513f62477e4"
    
    print(f"目标Token: {target_token[:50]}...")
    print(f"Token长度: {len(target_token)} 字符")
    print(f"Token（十六进制）长度: {len(target_token) // 2} 字节")
    print()
    
    # 分析token格式
    print("Token格式分析:")
    print("-"*80)
    
    # 尝试将token转换为字节
    try:
        token_bytes = bytes.fromhex(target_token)
        print(f"✅ Token可以转换为字节")
        print(f"   字节长度: {len(token_bytes)}")
        print(f"   前20字节（十六进制）: {token_bytes[:20].hex()}")
        print(f"   前20字节（尝试UTF-8解码）: {token_bytes[:20].decode('utf-8', errors='ignore')}")
        
        # 尝试Base64解码
        try:
            b64_decoded = base64.b64decode(token_bytes)
            print(f"   尝试Base64解码: {b64_decoded[:20].hex()}")
        except:
            print(f"   Base64解码失败")
    except:
        print(f"❌ Token无法转换为字节")
    
    print()
    
    # 测试不同的生成方式
    test_strings = [
        f"{uid}{key}{video_url}",
        f"{uid}{key}",
        f"{key}{video_url}",
    ]
    
    print("测试RC4加密（更多密钥）:")
    print("-"*80)
    possible_keys = [
        uid,
        key,
        f"{uid}{key}",
        f"{key}{uid}",
        f"{key} P",
        f"{uid} P",
        f"{uid}{key} P",
    ]
    
    for test_str in test_strings[:2]:  # 只测试前2个
        for rc4_key in possible_keys:
            try:
                cipher = ARC4.new(rc4_key.encode())
                encrypted = cipher.encrypt(test_str.encode())
                hex_encrypted = encrypted.hex()
                
                # 检查前20个字符是否匹配
                if hex_encrypted.startswith(target_token[:20]):
                    print(f"🎯 可能匹配！")
                    print(f"   字符串: {test_str[:50]}...")
                    print(f"   RC4密钥: {rc4_key}")
                    print(f"   加密结果前50字符: {hex_encrypted[:50]}")
                    print(f"   目标Token前50字符: {target_token[:50]}")
            except Exception as e:
                pass
    
    print()
    print("测试HMAC（更多密钥）:")
    print("-"*80)
    for test_str in test_strings[:2]:
        for hmac_key in possible_keys:
            hmac_md5 = hmac.new(hmac_key.encode(), test_str.encode(), hashlib.md5).hexdigest()
            hmac_sha1 = hmac.new(hmac_key.encode(), test_str.encode(), hashlib.sha1).hexdigest()
            
            if hmac_md5.startswith(target_token[:20]):
                print(f"🎯 HMAC-MD5可能匹配！")
                print(f"   字符串: {test_str[:50]}...")
                print(f"   HMAC密钥: {hmac_key}")
                print(f"   HMAC-MD5: {hmac_md5[:50]}...")
            
            if hmac_sha1.startswith(target_token[:20]):
                print(f"🎯 HMAC-SHA1可能匹配！")
                print(f"   字符串: {test_str[:50]}...")
                print(f"   HMAC密钥: {hmac_key}")
                print(f"   HMAC-SHA1: {hmac_sha1[:50]}...")

def test_different_video_urls():
    """测试不同的视频URL，观察hash变化"""
    print()
    print("="*80)
    print("测试不同视频URL的Hash变化")
    print("="*80)
    print("建议：使用相同的uid和key，但不同的video_url")
    print("观察hash是否变化，以确定hash是否基于video_url生成")
    print()
    print("测试用例:")
    print("-"*80)
    
    uid = "4059917"
    key = "cgklotuyDGHILOTW38"
    
    test_urls = [
        "https://www.iqiyi.com/v_1c168e2yzbk.html",
        "https://www.iqiyi.com/v_19rr7qhfg0.html",
        "https://v.youku.com/v_show/id_XMTA0MTc5NzI4.html",
    ]
    
    for video_url in test_urls:
        test_str = f"{uid}{key}{video_url}"
        md5_hash = hashlib.md5(test_str.encode()).hexdigest()
        print(f"{video_url[:50]:50} MD5: {md5_hash}")

def main():
    """主函数"""
    # 扩展hash测试
    matches = test_hash_extended()
    
    # 扩展token测试
    test_token_extended()
    
    # 测试不同视频URL
    test_different_video_urls()
    
    print()
    print("="*80)
    print("测试完成！")
    print("="*80)
    print()
    print("📝 建议:")
    print("1. 如果hash未找到匹配，可能是服务器端生成的（基于数据库）")
    print("2. 尝试使用不同的video_url测试，看hash是否变化")
    print("3. 分析token的格式，看是否包含可识别的模式")
    print("4. 如果可能，分析服务器端PHP代码")

if __name__ == "__main__":
    main()

