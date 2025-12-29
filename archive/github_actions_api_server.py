"""
GitHub Actions API服务器
通过GitHub Actions API触发workflow，实现视频解析
"""

import requests
import json
import time
from typing import Optional, Dict
import os


class GitHubActionsParser:
    """使用GitHub Actions进行视频解析"""
    
    def __init__(self, token: str, owner: str, repo: str):
        """
        初始化
        
        Args:
            token: GitHub Personal Access Token (需要repo权限)
            owner: GitHub用户名或组织名
            repo: 仓库名
        """
        self.token = token
        self.owner = owner
        self.repo = repo
        self.api_base = f"https://api.github.com/repos/{owner}/{repo}"
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
        }
    
    def trigger_parse_workflow(self, video_url: str) -> Dict:
        """
        触发解析workflow
        
        Args:
            video_url: 视频URL
            
        Returns:
            workflow运行信息
        """
        url = f"{self.api_base}/actions/workflows/video_parser_api.yml/dispatches"
        
        payload = {
            'ref': 'main',  # 或 'master'，根据你的默认分支
            'inputs': {
                'video_url': video_url
            }
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        
        if response.status_code == 204:
            return {
                'success': True,
                'message': 'Workflow已触发',
                'video_url': video_url
            }
        else:
            return {
                'success': False,
                'error': f'触发失败: {response.status_code} - {response.text}'
            }
    
    def trigger_webhook_parse(self, video_url: str) -> Dict:
        """
        通过repository_dispatch触发解析（webhook方式）
        
        Args:
            video_url: 视频URL
            
        Returns:
            webhook触发信息
        """
        url = f"{self.api_base}/dispatches"
        
        payload = {
            'event_type': 'parse-video',
            'client_payload': {
                'video_url': video_url
            }
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        
        if response.status_code == 204:
            return {
                'success': True,
                'message': 'Webhook已触发',
                'video_url': video_url
            }
        else:
            return {
                'success': False,
                'error': f'触发失败: {response.status_code} - {response.text}'
            }
    
    def get_workflow_runs(self, limit: int = 5) -> list:
        """获取最近的workflow运行记录"""
        url = f"{self.api_base}/actions/workflows/video_parser_api.yml/runs"
        params = {'per_page': limit}
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json().get('workflow_runs', [])
        return []
    
    def get_workflow_run_result(self, run_id: int) -> Optional[Dict]:
        """获取workflow运行结果"""
        # 获取artifacts
        url = f"{self.api_base}/actions/runs/{run_id}/artifacts"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            artifacts = response.json().get('artifacts', [])
            for artifact in artifacts:
                if artifact['name'] == 'parse-result':
                    # 下载artifact
                    download_url = artifact['archive_download_url']
                    # 注意：需要处理zip文件
                    return {
                        'artifact_id': artifact['id'],
                        'download_url': download_url
                    }
        return None


def main():
    """示例使用"""
    # 从环境变量读取配置
    token = os.getenv('GITHUB_TOKEN')
    owner = os.getenv('GITHUB_OWNER', 'your-username')
    repo = os.getenv('GITHUB_REPO', 'video-parser-analysis')
    
    if not token:
        print("❌ 请设置GITHUB_TOKEN环境变量")
        return
    
    parser = GitHubActionsParser(token, owner, repo)
    
    video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    
    print("触发GitHub Actions解析...")
    result = parser.trigger_parse_workflow(video_url)
    
    if result['success']:
        print(f"✅ {result['message']}")
        print(f"   视频URL: {result['video_url']}")
        print("\n💡 查看结果:")
        print(f"   https://github.com/{owner}/{repo}/actions")
    else:
        print(f"❌ {result['error']}")


if __name__ == '__main__':
    main()

