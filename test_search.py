#!/usr/bin/env python3
"""
测试搜索接口
"""
import requests
import sys
from urllib.parse import quote

def test_search(keyword: str):
    """测试搜索接口"""
    url = "http://localhost:8000/api/v1/search"
    params = {
        "ac": "videolist",
        "wd": keyword,
        "page": 1
    }
    
    print(f"测试搜索接口...")
    print(f"关键词: {keyword}")
    print(f"请求URL: {url}")
    print("-" * 60)
    
    try:
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get("code") == 1:
            total = result.get("total", 0)
            print(f"✅ 搜索成功！")
            print(f"结果总数: {total}")
            print(f"当前页: {result.get('page', 1)}")
            print(f"总页数: {result.get('pagecount', 0)}")
            print("-" * 60)
            
            if total > 0:
                print(f"前3条结果:")
                for i, item in enumerate(result.get("list", [])[:3], 1):
                    print(f"\n{i}. {item.get('vod_name', '未知')}")
                    print(f"   播放地址: {item.get('vod_play_url', '无')[:100]}...")
            else:
                print("⚠️ 未找到结果")
        else:
            print("❌ 搜索失败")
            print(f"错误: {result.get('msg', '未知错误')}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # 默认测试关键词
    test_keyword = "新僵尸先生"
    
    # 如果提供了命令行参数，使用提供的关键词
    if len(sys.argv) > 1:
        test_keyword = sys.argv[1]
    
    test_search(test_keyword)

