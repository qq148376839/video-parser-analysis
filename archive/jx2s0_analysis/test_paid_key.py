#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import re
import base64
import os

url = "https://json.2s0.cn:5678/player/analysis.php/?uid=4059917&key=cgklotuyDGHILOTW38&url=https://www.iqiyi.com/v_1c168e2yzbk.html"

print("正在访问URL...")
response = requests.get(url, timeout=30)
print(f"状态码: {response.status_code}")

if response.status_code == 200:
    html = response.text
    
    # 保存HTML
    with open('paid_key_analysis.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("HTML已保存到: paid_key_analysis.html")
    
    # 提取config
    config_pattern = r'var\s+config\s*=\s*({[^}]+})'
    match = re.search(config_pattern, html, re.DOTALL)
    if match:
        config_str = match.group(1)
        print("\n找到config对象:")
        print(config_str[:500])
        
        # 提取url和id
        url_match = re.search(r'"url"\s*:\s*"([^"]+)"', config_str)
        id_match = re.search(r'"id"\s*:\s*"([^"]+)"', config_str)
        
        if url_match:
            config_url = url_match.group(1)
            print(f"\nconfig.url: {config_url[:100]}...")
            print(f"config.url长度: {len(config_url)}")
            
        if id_match:
            config_id = id_match.group(1)
            print(f"config.id: {config_id}")
    else:
        print("\n未找到config对象，显示HTML前1000字符:")
        print(html[:1000])

