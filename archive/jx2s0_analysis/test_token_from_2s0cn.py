"""
测试 token 是否从 www.2s0.cn 获取
假设：使用 config.url 和 config.id 调用 www.2s0.cn 的 API 获取 token
"""

import requests
import base64
import json
from urllib.parse import urlencode, urlparse, parse_qs

# 从 analysis.php 中提取的 config 对象
config = {
    "url": "O/zpjS4gC4ztyL9ve/+wx/3Lmpl7X/QAEOuqmTie93atrwDjwxRosEpoaXZw0TRD/AGtcvvIxMxgcxsQWcHumCqsvuIlf3lGXkqJgVWIsvPYgh8+Nsu4r36vZQ6fs/7edsA0WFSEDE16mwOTvC8ByCxFQJXZcJaeTf7igGItTKkNAp5yEF325qV9KNQuP/wR3si83JgFlTJ5d+hDqD6PjLpnQa9dj5jhhU3CRZaUxnIK9d1Gy+UxI0HhDsyLRnS+c6C7NFAu8aOZ48zeKlJH14o6IB9Io39UOiPh13dLuq9QmSqwzty7th+dt0Pz3O5w3nOvyQn+yieU0tPg+eNwujrN79nX+8bTPr5FdGfgqCyn0wMhRA==",
    "id": "b664f44e3be2ad57fdb6"
}

# 测试视频 URL
video_url = "https://www.iqiyi.com/v_19rr7qhfg0.html"

# 可能的 API 端点
possible_endpoints = [
    "https://www.2s0.cn/api.php",
    "https://www.2s0.cn/api/getm3u8.php",
    "https://www.2s0.cn/api/gettoken.php",
    "https://www.2s0.cn/jiexi.php",
    "https://www.2s0.cn/parse.php",
    "https://www.2s0.cn/getm3u8.php",
    "https://www.2s0.cn/gettoken.php",
    "https://www.2s0.cn/api",
    "https://www.2s0.cn/video.php",
]

# 可能的请求参数组合
possible_params = [
    {"url": config["url"], "id": config["id"]},
    {"url": video_url, "id": config["id"]},
    {"config_url": config["url"], "config_id": config["id"]},
    {"encrypted_url": config["url"], "uid": config["id"]},
    {"data": config["url"], "key": config["id"]},
    {"url": video_url, "config_url": config["url"], "id": config["id"]},
    {"video_url": video_url, "url": config["url"], "id": config["id"]},
]

def test_api_endpoint(endpoint, params, method="GET"):
    """测试 API 端点"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://jx.2s0.cn/",
            "Origin": "https://jx.2s0.cn",
        }
        
        if method == "GET":
            response = requests.get(endpoint, params=params, headers=headers, timeout=10)
        else:
            headers["Content-Type"] = "application/json"
            response = requests.post(endpoint, json=params, headers=headers, timeout=10)
        
        print(f"\n{'='*80}")
        print(f"测试: {method} {endpoint}")
        print(f"参数: {params}")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                # 尝试解析 JSON
                data = response.json()
                print(f"✅ JSON 响应:")
                print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
                
                # 检查是否包含 m3u8 或 token
                response_text = json.dumps(data)
                if "m3u8" in response_text.lower() or "token" in response_text.lower() or "cachem3u8" in response_text.lower():
                    print(f"\n🎯 找到 m3u8/token 相关信息！")
                    return True
            except:
                # 不是 JSON，检查文本
                text = response.text[:500]
                print(f"📄 文本响应: {text}")
                if "m3u8" in text.lower() or "token" in text.lower() or "cachem3u8" in text.lower():
                    print(f"\n🎯 找到 m3u8/token 相关信息！")
                    return True
        else:
            print(f"❌ 请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    return False

def main():
    """主函数"""
    print("="*80)
    print("测试 token 是否从 www.2s0.cn 获取")
    print("="*80)
    print(f"config.url: {config['url'][:50]}...")
    print(f"config.id: {config['id']}")
    print(f"video_url: {video_url}")
    print("="*80)
    
    found = False
    
    # 测试所有可能的端点
    for endpoint in possible_endpoints:
        for params in possible_params:
            if test_api_endpoint(endpoint, params, "GET"):
                found = True
                print(f"\n✅ 找到可能的 API: {endpoint}")
                print(f"   参数: {params}")
            
            # 也测试 POST
            if test_api_endpoint(endpoint, params, "POST"):
                found = True
                print(f"\n✅ 找到可能的 API: {endpoint} (POST)")
                print(f"   参数: {params}")
    
    if not found:
        print("\n" + "="*80)
        print("❌ 未找到返回 m3u8/token 的 API")
        print("="*80)
        print("\n可能的原因：")
        print("1. API 端点不在 www.2s0.cn")
        print("2. 需要特定的请求头或认证")
        print("3. token 是在 JavaScript 中生成的，不是通过 API 获取")
        print("4. API 端点在其他域名（如 jx.2s0.cn）")
    
    # 也测试 jx.2s0.cn 的可能端点
    print("\n" + "="*80)
    print("测试 jx.2s0.cn 的可能端点")
    print("="*80)
    
    jx_endpoints = [
        "https://jx.2s0.cn/api.php",
        "https://jx.2s0.cn/api/getm3u8.php",
        "https://jx.2s0.cn/api/gettoken.php",
        "https://jx.2s0.cn/jiexi.php",
        "https://jx.2s0.cn/parse.php",
    ]
    
    for endpoint in jx_endpoints:
        for params in possible_params:
            if test_api_endpoint(endpoint, params, "GET"):
                found = True
                print(f"\n✅ 找到可能的 API: {endpoint}")
                print(f"   参数: {params}")

if __name__ == "__main__":
    main()

