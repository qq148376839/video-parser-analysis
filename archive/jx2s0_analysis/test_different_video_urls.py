#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试不同的视频URL，观察hash和token的变化
这是确定hash和token生成算法的关键测试
"""

import requests
import re
from urllib.parse import quote
import time

def test_different_video_urls():
    """测试不同的视频URL"""
    print("="*80)
    print("测试不同的视频URL")
    print("="*80)
    print("目标：观察hash和token是否变化，以确定生成算法")
    print()
    
    uid = "4059917"
    key = "cgklotuyDGHILOTW38"
    
    # 测试不同的视频URL
    test_urls = [
        "https://www.iqiyi.com/v_1c168e2yzbk.html",
        "https://www.iqiyi.com/v_19rr7qhfg0.html",
        "https://v.youku.com/v_show/id_XMTA0MTc5NzI4.html",
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    })
    
    results = []
    
    for video_url in test_urls:
        print(f"测试视频URL: {video_url}")
        print("-"*80)
        
        url = f"https://json.2s0.cn:5678/player/analysis.php/?uid={uid}&key={key}&url={quote(video_url)}"
        
        try:
            response = session.get(url, timeout=30)
            if response.status_code == 200:
                html = response.text
                
                # 提取m3u8 URL
                m3u8_match = re.search(r'var url = "([^"]+)"', html)
                if m3u8_match:
                    m3u8_url = m3u8_match.group(1)
                    
                    # 提取hash和token
                    hash_match = re.search(r'/Cache/Ff/([a-f0-9]+)\.m3u8', m3u8_url)
                    token_match = re.search(r'token=([^"]+)', m3u8_url)
                    
                    if hash_match and token_match:
                        hash_value = hash_match.group(1)
                        token_value = token_match.group(1)
                        
                        result = {
                            'video_url': video_url,
                            'hash': hash_value,
                            'token': token_value,
                            'm3u8_url': m3u8_url
                        }
                        results.append(result)
                        
                        print(f"  ✅ Hash: {hash_value}")
                        print(f"  ✅ Token: {token_value[:50]}...")
                        print(f"  ✅ m3u8 URL: {m3u8_url[:80]}...")
                    else:
                        print(f"  ❌ 未找到hash或token")
                else:
                    print(f"  ❌ 未找到m3u8 URL")
            else:
                print(f"  ❌ 请求失败: {response.status_code}")
        except Exception as e:
            print(f"  ❌ 错误: {e}")
        
        print()
        time.sleep(1)  # 避免请求过快
    
    # 分析结果
    print("="*80)
    print("分析结果")
    print("="*80)
    
    if len(results) > 1:
        # 检查hash是否相同
        hashes = [r['hash'] for r in results]
        if len(set(hashes)) == 1:
            print("⚠️ 所有视频URL的Hash相同")
            print("   说明：Hash可能不基于video_url生成，可能是固定的或基于其他参数")
        else:
            print("✅ 不同视频URL的Hash不同")
            print("   说明：Hash可能基于video_url生成")
            print("   Hash列表:")
            for i, hash_val in enumerate(hashes, 1):
                print(f"     {i}. {hash_val}")
        
        print()
        
        # 检查token是否相同
        tokens = [r['token'] for r in results]
        if len(set(tokens)) == 1:
            print("⚠️ 所有视频URL的Token相同")
            print("   说明：Token可能不基于video_url生成，可能是固定的或基于其他参数")
        else:
            print("✅ 不同视频URL的Token不同")
            print("   说明：Token可能基于video_url生成")
            print("   Token列表（前50字符）:")
            for i, token_val in enumerate(tokens, 1):
                print(f"     {i}. {token_val[:50]}...")
        
        print()
        print("详细结果:")
        for i, result in enumerate(results, 1):
            print(f"\n结果 {i}:")
            print(f"  Video URL: {result['video_url']}")
            print(f"  Hash: {result['hash']}")
            print(f"  Token: {result['token'][:50]}...")
    else:
        print("⚠️ 无法分析：需要至少2个成功的测试结果")
    
    return results

def main():
    """主函数"""
    results = test_different_video_urls()
    
    print()
    print("="*80)
    print("测试完成！")
    print("="*80)
    print()
    print("📝 建议:")
    if results:
        if len(results) > 1:
            hashes = [r['hash'] for r in results]
            if len(set(hashes)) > 1:
                print("1. Hash基于video_url生成，继续分析hash生成算法")
            else:
                print("1. Hash不基于video_url生成，可能是固定的或基于uid/key")
            
            tokens = [r['token'] for r in results]
            if len(set(tokens)) > 1:
                print("2. Token基于video_url生成，继续分析token生成算法")
            else:
                print("2. Token不基于video_url生成，可能是固定的或基于uid/key")
        else:
            print("1. 需要测试更多的视频URL")
    else:
        print("1. 检查网络连接和API访问")
        print("2. 确认uid和key是否有效")

if __name__ == "__main__":
    main()

