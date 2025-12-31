#!/usr/bin/env python3
"""
测试z参数获取功能
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.z_param_manager import z_param_manager

def test_z_param_update(video_url: str = None):
    """测试z参数更新"""
    if not video_url:
        video_url = "https://www.iqiyi.com/v_19rrf6eqrk.html"
    
    print("=" * 60)
    print("测试z参数更新")
    print("=" * 60)
    print(f"视频URL: {video_url}")
    print("-" * 60)
    
    # 检查当前z参数状态
    current_z = z_param_manager.get_z_param()
    is_expired = z_param_manager.is_expired()
    
    print(f"当前z参数状态:")
    print(f"  是否存在: {'是' if current_z else '否'}")
    print(f"  是否过期: {'是' if is_expired else '否'}")
    if current_z:
        print(f"  z参数值: {current_z.get('z_param', 'N/A')[:16]}...")
        print(f"  更新时间: {current_z.get('updated_at', 'N/A')}")
    print("-" * 60)
    
    # 尝试更新z参数
    print("\n尝试使用HTTP方式更新z参数...")
    new_z = z_param_manager.update_with_http(video_url)
    
    if new_z:
        print(f"✅ HTTP方式更新成功: {new_z[:16]}...")
    else:
        print("❌ HTTP方式更新失败")
        print("\n尝试使用Playwright方式更新z参数...")
        new_z = z_param_manager.update_with_playwright(video_url)
        
        if new_z:
            print(f"✅ Playwright方式更新成功: {new_z[:16]}...")
        else:
            print("❌ Playwright方式也失败")
            print("\n💡 建议：")
            print("1. 检查网络连接")
            print("2. 检查解析网站是否可访问")
            print("3. 查看详细日志了解失败原因")
            print("4. 参考 Z_PARAM_MANUAL_SETUP.md 手动设置z参数")
    
    # 再次检查z参数状态
    print("\n" + "-" * 60)
    print("更新后的z参数状态:")
    current_z = z_param_manager.get_z_param()
    if current_z:
        print(f"  z参数值: {current_z.get('z_param', 'N/A')[:16]}...")
        print(f"  更新时间: {current_z.get('updated_at', 'N/A')}")
    else:
        print("  z参数不存在")


if __name__ == "__main__":
    test_url = None
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
    
    test_z_param_update(test_url)

