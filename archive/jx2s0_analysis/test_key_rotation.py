#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试key轮询功能
"""

import sys
import os

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 直接导入当前目录下的模块
from get_m3u8_with_paid_key import PaidKeyM3U8Getter

def test_key_rotation():
    """测试key轮询"""
    print("="*80)
    print("测试Key轮询功能")
    print("="*80)
    print()
    
    # 创建获取器（使用项目根目录的JSON文件）
    # 获取项目根目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    json_file = os.path.join(project_root, "registration_results.json")
    
    print(f"JSON文件路径: {json_file}")
    getter = PaidKeyM3U8Getter(json_file)
    
    # 测试视频URL
    video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    
    # 测试3次，观察是否使用不同的key
    print("测试1: 连续调用3次，观察key轮询")
    print("-"*80)
    
    for i in range(3):
        print(f"\n第 {i+1} 次调用:")
        m3u8_url = getter.get_m3u8_url(video_url)
        if m3u8_url:
            print(f"  ✅ 成功获取m3u8 URL")
            print(f"  📝 使用的key: uid={getter.current_uid}")
        else:
            print(f"  ❌ 获取失败")
    
    print()
    print("="*80)
    print("测试完成！")
    print("="*80)
    print()
    print("📝 检查JSON文件，确认:")
    print("  1. current_index 已更新")
    print("  2. expire_date 字段已添加")
    print("  3. 格式已转换为带元数据的格式")

if __name__ == "__main__":
    test_key_rotation()

