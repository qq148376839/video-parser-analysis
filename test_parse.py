#!/usr/bin/env python3
"""
测试解析接口
"""
import requests
import sys

def test_parse(video_url: str):
    """测试解析接口"""
    url = "http://localhost:8000/api/v1/parse"
    params = {
        "url": video_url,
        "parser_url": "https://jx.789jiexi.com"  # 可选
    }
    
    print(f"测试解析接口...")
    print(f"视频URL: {video_url}")
    print(f"请求URL: {url}")
    print("-" * 60)
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get("success"):
            print("✅ 解析成功！")
            print(f"m3u8链接: {result['data']['m3u8_url']}")
            print(f"解析方法: {result['data']['method']}")
            print(f"耗时: {result['data']['parse_time']}秒")
        else:
            print("❌ 解析失败")
            print(f"错误: {result.get('error', '未知错误')}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # 默认测试URL
    test_url = "https://www.iqiyi.com/v_19rrf6eqrk.html"
    
    # 如果提供了命令行参数，使用提供的URL
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    
    test_parse(test_url)

