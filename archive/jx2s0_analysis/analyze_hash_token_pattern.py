#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
分析hash和token的生成规律
基于测试结果：不同video_url的hash和token都不同
"""

import hashlib
import base64
from urllib.parse import quote, unquote
from Crypto.Cipher import ARC4
import hmac

def analyze_hash_pattern():
    """分析hash的生成规律"""
    print("="*80)
    print("Hash生成规律分析")
    print("="*80)
    
    uid = "4059917"
    key = "cgklotuyDGHILOTW38"
    
    # 测试数据
    test_cases = [
        {
            'video_url': "https://www.iqiyi.com/v_1c168e2yzbk.html",
            'hash': "2089c333a6d6a31e306bd190557aea36"
        },
        {
            'video_url': "https://www.iqiyi.com/v_19rr7qhfg0.html",
            'hash': "aeaf87d55e9fd0251470c951429cde13"
        }
    ]
    
    print("测试数据:")
    for i, case in enumerate(test_cases, 1):
        print(f"  {i}. {case['video_url']}")
        print(f"     Hash: {case['hash']}")
    print()
    
    # 测试不同的组合
    print("测试不同的字符串组合:")
    print("-"*80)
    
    for case in test_cases:
        video_url = case['video_url']
        target_hash = case['hash']
        
        print(f"\n分析: {video_url}")
        print(f"目标Hash: {target_hash}")
        print()
        
        # 提取视频ID
        video_id = video_url.split('/')[-1].replace('.html', '')
        
        # 测试用例
        test_strings = [
            # 基础组合
            (f"{uid}{key}{video_url}", "uid+key+video_url"),
            (f"{key}{uid}{video_url}", "key+uid+video_url"),
            (f"{video_url}{uid}{key}", "video_url+uid+key"),
            (f"{uid}{key}{video_id}", "uid+key+video_id"),
            (f"{key}{video_id}", "key+video_id"),
            (f"{uid}{video_id}", "uid+video_id"),
            (video_id, "video_id"),
            (video_url, "video_url"),
            
            # URL编码版本
            (quote(video_url), "quote(video_url)"),
            (quote(video_id), "quote(video_id)"),
            
            # 去除协议
            (video_url.replace('https://', ''), "video_url(无协议)"),
            (video_url.replace('https://', '').replace('http://', ''), "video_url(无协议)"),
            
            # 特殊格式
            (f"{uid}|{key}|{video_url}", "uid|key|video_url"),
            (f"{uid}_{key}_{video_url}", "uid_key_video_url"),
        ]
        
        matches = []
        for test_str, description in test_strings:
            md5_hash = hashlib.md5(test_str.encode()).hexdigest()
            if md5_hash == target_hash:
                matches.append((description, test_str))
                print(f"  🎯 {description:30} MD5: {md5_hash} ✅ 匹配！")
            else:
                print(f"     {description:30} MD5: {md5_hash}")
        
        if matches:
            print(f"\n  ✅ 找到匹配！")
            for desc, test_str in matches:
                print(f"     方式: {desc}")
                print(f"     输入: {test_str}")
        else:
            print(f"\n  ❌ 未找到匹配")
    
    print()
    print("="*80)
    print("Hash分析总结")
    print("="*80)
    print("如果未找到匹配，可能的原因:")
    print("1. Hash可能基于服务器端数据（如数据库记录ID）")
    print("2. Hash可能使用了其他参数（如时间戳、IP等）")
    print("3. Hash可能使用了特殊的编码或处理方式")

def analyze_token_pattern():
    """分析token的生成规律"""
    print()
    print("="*80)
    print("Token生成规律分析")
    print("="*80)
    
    uid = "4059917"
    key = "cgklotuyDGHILOTW38"
    
    # 测试数据
    test_cases = [
        {
            'video_url': "https://www.iqiyi.com/v_1c168e2yzbk.html",
            'token': "d3d376e44505b4448705e6f20564368367264405b4474377b4c614571477a447f43424e6265423b4365435376667f2259455247746c6a415744324c613f6547443a43443a626e6d40786a77334e4f487c64775b2474793b44567741794951513f62477e4"
        },
        {
            'video_url': "https://www.iqiyi.com/v_19rr7qhfg0.html",
            'token': "d3d37727b4a6a62473873466576713b603b253559397359723b4c614571477a447f43424e6265423b4365435376667f2259455247746c6a415744324c613f6547443a43443a626e6d40786a77334e4f487c64775b2474793b44567741794951513f62477e4"
        }
    ]
    
    print("测试数据:")
    for i, case in enumerate(test_cases, 1):
        print(f"  {i}. {case['video_url']}")
        print(f"     Token: {case['token'][:50]}...")
        print(f"     Token长度: {len(case['token'])} 字符")
    print()
    
    # 分析token格式
    print("Token格式分析:")
    print("-"*80)
    
    for case in test_cases:
        token = case['token']
        print(f"\nToken: {token[:50]}...")
        
        # 检查是否是十六进制
        try:
            token_bytes = bytes.fromhex(token)
            print(f"  ✅ 是十六进制格式")
            print(f"     字节长度: {len(token_bytes)}")
            print(f"     前20字节（十六进制）: {token_bytes[:20].hex()}")
            
            # 尝试UTF-8解码
            try:
                utf8_decoded = token_bytes.decode('utf-8', errors='ignore')
                print(f"     前20字节（UTF-8）: {utf8_decoded[:20]}")
            except:
                pass
            
            # 尝试Base64解码
            try:
                b64_decoded = base64.b64decode(token_bytes)
                print(f"     Base64解码后长度: {len(b64_decoded)} 字节")
                print(f"     Base64解码后（十六进制）: {b64_decoded[:20].hex()}")
            except:
                pass
        except:
            print(f"  ❌ 不是有效的十六进制")
    
    # 对比两个token
    print()
    print("Token对比分析:")
    print("-"*80)
    token1 = test_cases[0]['token']
    token2 = test_cases[1]['token']
    
    # 找出相同的前缀
    common_prefix = ""
    for i in range(min(len(token1), len(token2))):
        if token1[i] == token2[i]:
            common_prefix += token1[i]
        else:
            break
    
    print(f"相同前缀长度: {len(common_prefix)} 字符")
    print(f"相同前缀: {common_prefix[:50]}...")
    
    if len(common_prefix) > 20:
        print(f"  ✅ Token有较长的相同前缀")
        print(f"     说明：Token可能包含固定的部分（如uid/key）和变化的部分（如video_url）")
    
    # 找出不同的部分
    diff_start = len(common_prefix)
    print(f"\n不同部分开始位置: {diff_start}")
    print(f"Token1的不同部分: {token1[diff_start:diff_start+50]}...")
    print(f"Token2的不同部分: {token2[diff_start:diff_start+50]}...")
    
    # 测试token生成
    print()
    print("测试Token生成:")
    print("-"*80)
    
    for case in test_cases:
        video_url = case['video_url']
        target_token = case['token']
        
        print(f"\n分析: {video_url}")
        print(f"目标Token: {target_token[:50]}...")
        
        # 提取视频ID
        video_id = video_url.split('/')[-1].replace('.html', '')
        
        # 测试用例
        test_strings = [
            f"{uid}{key}{video_url}",
            f"{uid}{key}{video_id}",
            f"{key}{video_url}",
            video_url,
        ]
        
        # 测试RC4加密
        possible_keys = [uid, key, f"{uid}{key}", f"{key}{uid}", f"{key} P"]
        
        for test_str in test_strings:
            for rc4_key in possible_keys:
                try:
                    cipher = ARC4.new(rc4_key.encode())
                    encrypted = cipher.encrypt(test_str.encode())
                    hex_encrypted = encrypted.hex()
                    
                    # 检查前20个字符是否匹配
                    if hex_encrypted.startswith(target_token[:20]):
                        print(f"  🎯 可能匹配！")
                        print(f"     字符串: {test_str[:50]}...")
                        print(f"     RC4密钥: {rc4_key}")
                        print(f"     加密结果前50字符: {hex_encrypted[:50]}")
                        print(f"     目标Token前50字符: {target_token[:50]}")
                except:
                    pass
        
        # 测试HMAC
        for test_str in test_strings:
            for hmac_key in [uid, key, f"{uid}{key}"]:
                hmac_md5 = hmac.new(hmac_key.encode(), test_str.encode(), hashlib.md5).hexdigest()
                hmac_sha1 = hmac.new(hmac_key.encode(), test_str.encode(), hashlib.sha1).hexdigest()
                
                if hmac_md5.startswith(target_token[:20]):
                    print(f"  🎯 HMAC-MD5可能匹配！")
                    print(f"     字符串: {test_str[:50]}...")
                    print(f"     HMAC密钥: {hmac_key}")
                    print(f"     HMAC-MD5: {hmac_md5[:50]}...")
                
                if hmac_sha1.startswith(target_token[:20]):
                    print(f"  🎯 HMAC-SHA1可能匹配！")
                    print(f"     字符串: {test_str[:50]}...")
                    print(f"     HMAC密钥: {hmac_key}")
                    print(f"     HMAC-SHA1: {hmac_sha1[:50]}...")

def main():
    """主函数"""
    # 分析hash
    analyze_hash_pattern()
    
    # 分析token
    analyze_token_pattern()
    
    print()
    print("="*80)
    print("分析完成！")
    print("="*80)
    print()
    print("📝 关键发现:")
    print("1. Hash和Token都基于video_url生成")
    print("2. 需要找到具体的生成算法")
    print("3. 如果无法找到算法，可以直接使用API调用方式")

if __name__ == "__main__":
    main()

