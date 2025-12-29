"""
更新解析器以支持从API服务获取z参数
演示如何在服务器环境中使用
"""

import requests
from typing import Optional


def get_z_param_from_api_service(video_url: str, api_url: str = "http://localhost:5000/api/get_z_param") -> Optional[str]:
    """从API服务获取z参数"""
    try:
        response = requests.get(api_url, params={'video_url': video_url}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('z_param'):
                return data['z_param']
    except Exception as e:
        print(f"从API服务获取z参数失败: {e}")
    return None


def get_z_param_from_website_direct(video_url: str) -> Optional[str]:
    """直接从解析网站提取z参数（无需浏览器）"""
    import re
    
    try:
        parser_url = f"https://videocdn.ihelpy.net/jiexi/m1907.html?m1907jx={video_url}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        response = requests.get(parser_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            html = response.text
            
            # 从API调用URL中提取z参数
            api_url_pattern = r'https://[^/]+/api/v/\?[^"\'<>]*z=([a-f0-9]{32})'
            matches = re.findall(api_url_pattern, html, re.IGNORECASE)
            if matches:
                return matches[0]
    except Exception as e:
        print(f"从网站提取z参数失败: {e}")
    return None


# 使用示例
if __name__ == '__main__':
    video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    
    print("=" * 60)
    print("获取z参数 - 服务器端方案")
    print("=" * 60)
    
    # 方式1: 从API服务获取（如果API服务正在运行）
    print("\n[方式1] 从API服务获取...")
    z_param = get_z_param_from_api_service(video_url)
    if z_param:
        print(f"✅ 成功获取: {z_param}")
    else:
        print("❌ API服务未运行或获取失败")
    
    # 方式2: 直接从网站提取
    print("\n[方式2] 直接从网站提取...")
    z_param = get_z_param_from_website_direct(video_url)
    if z_param:
        print(f"✅ 成功提取: {z_param}")
    else:
        print("❌ 提取失败（可能需要JavaScript执行）")

