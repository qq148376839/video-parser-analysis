"""
测试GitHub Actions API
"""

import os
import requests
import json
import time

def trigger_github_actions_parse(video_url: str, token: str, owner: str, repo: str):
    """触发GitHub Actions解析视频"""
    
    # 触发workflow
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/video_parser_api.yml/dispatches"
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
    }
    payload = {
        'ref': 'main',  # 根据你的默认分支修改
        'inputs': {
            'video_url': video_url
        }
    }
    
    print(f"触发GitHub Actions workflow...")
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 204:
        print(f"✅ Workflow已触发")
        print(f"   视频URL: {video_url}")
        print(f"\n💡 查看运行状态:")
        print(f"   https://github.com/{owner}/{repo}/actions")
        return True
    else:
        print(f"❌ 触发失败: {response.status_code}")
        print(f"   响应: {response.text}")
        return False


def main():
    """主函数"""
    # 从环境变量读取配置
    token = os.getenv('GITHUB_TOKEN')
    owner = os.getenv('GITHUB_OWNER', 'your-username')
    repo = os.getenv('GITHUB_REPO', 'video-parser-analysis')
    
    if not token:
        print("❌ 请设置GITHUB_TOKEN环境变量")
        print("   export GITHUB_TOKEN=your_token")
        return
    
    video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    
    print("=" * 60)
    print("GitHub Actions 视频解析测试")
    print("=" * 60)
    print(f"仓库: {owner}/{repo}")
    print(f"视频URL: {video_url}")
    print()
    
    success = trigger_github_actions_parse(video_url, token, owner, repo)
    
    if success:
        print("\n✅ 测试完成！")
        print("\n📝 下一步:")
        print("   1. 访问GitHub Actions页面查看运行状态")
        print("   2. 等待workflow完成")
        print("   3. 下载artifact查看解析结果")


if __name__ == '__main__':
    main()

