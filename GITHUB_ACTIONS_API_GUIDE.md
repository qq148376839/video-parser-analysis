# GitHub Actions API 视频解析服务

## 📋 概述

使用GitHub Actions作为视频解析API服务，绕过Cloudflare Workers的限制。

## ✨ 优势

- ✅ **无需服务器**: 使用GitHub Actions的免费额度
- ✅ **Python环境**: 可以直接运行Python脚本
- ✅ **已验证可用**: 本地Python脚本已验证可用
- ✅ **免费额度**: 每月2000分钟（私有仓库），公开仓库无限

## 🚀 快速开始

### 步骤1: 创建GitHub Personal Access Token

1. 访问: https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 选择权限:
   - `repo` (完整仓库权限)
   - `workflow` (工作流权限)
4. 复制token

### 步骤2: 配置Secrets

在GitHub仓库中设置Secrets:
- `GITHUB_TOKEN`: 你的Personal Access Token

### 步骤3: 使用方式

#### 方式1: 通过GitHub Actions UI触发

1. 访问: `https://github.com/{owner}/{repo}/actions/workflows/video_parser_api.yml`
2. 点击 "Run workflow"
3. 输入视频URL
4. 点击 "Run workflow" 按钮
5. 等待运行完成，查看结果

#### 方式2: 通过API触发（推荐）

使用Python脚本触发：

```python
from github_actions_api_server import GitHubActionsParser

parser = GitHubActionsParser(
    token='your-github-token',
    owner='your-username',
    repo='video-parser-analysis'
)

result = parser.trigger_parse_workflow('https://www.iqiyi.com/v_1c168e2yzbk.html')
print(result)
```

#### 方式3: 通过Webhook触发

```bash
curl -X POST \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/{owner}/{repo}/dispatches \
  -d '{
    "event_type": "parse-video",
    "client_payload": {
      "video_url": "https://www.iqiyi.com/v_1c168e2yzbk.html"
    }
  }'
```

## 📝 Workflow配置

### 主Workflow: `.github/workflows/video_parser_api.yml`

这个workflow支持：
- `workflow_dispatch`: 手动触发（通过UI或API）
- `repository_dispatch`: Webhook触发

### Webhook Workflow: `.github/workflows/video_parser_webhook.yml`

专门用于webhook触发，可以添加更多自定义逻辑。

## 🔧 使用示例

### Python客户端

```python
import requests
import json
import time

def parse_video_via_github_actions(video_url: str, token: str, owner: str, repo: str):
    """通过GitHub Actions解析视频"""
    
    # 1. 触发workflow
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/video_parser_api.yml/dispatches"
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
    }
    payload = {
        'ref': 'main',
        'inputs': {
            'video_url': video_url
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code != 204:
        return {'success': False, 'error': f'触发失败: {response.status_code}'}
    
    # 2. 等待workflow完成（可选）
    # 这里可以轮询workflow状态，获取结果
    
    return {'success': True, 'message': 'Workflow已触发，请查看GitHub Actions获取结果'}


# 使用
result = parse_video_via_github_actions(
    'https://www.iqiyi.com/v_1c168e2yzbk.html',
    'your-token',
    'your-username',
    'video-parser-analysis'
)
print(result)
```

### 获取Workflow运行结果

```python
def get_workflow_result(token: str, owner: str, repo: str, run_id: int):
    """获取workflow运行结果"""
    
    # 获取artifacts
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts"
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        artifacts = response.json().get('artifacts', [])
        for artifact in artifacts:
            if artifact['name'] == 'parse-result':
                # 下载artifact（需要处理zip文件）
                download_url = artifact['archive_download_url']
                return {'artifact_id': artifact['id'], 'download_url': download_url}
    
    return None
```

## 🔄 实时获取结果（高级）

如果需要实时获取结果，可以：

1. **使用GitHub API轮询**: 定期检查workflow状态
2. **使用Webhook**: 配置GitHub Webhook，workflow完成后通知
3. **使用GitHub Pages**: 将结果保存到GitHub Pages，通过HTTP访问

### 示例：轮询获取结果

```python
import time

def wait_for_result(token: str, owner: str, repo: str, run_id: int, timeout: int = 300):
    """等待workflow完成并获取结果"""
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        # 检查workflow状态
        url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}"
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            run = response.json()
            status = run['status']
            conclusion = run.get('conclusion')
            
            if status == 'completed':
                if conclusion == 'success':
                    # 获取artifacts
                    return get_workflow_result(token, owner, repo, run_id)
                else:
                    return {'success': False, 'error': f'Workflow失败: {conclusion}'}
        
        time.sleep(5)  # 等待5秒后重试
    
    return {'success': False, 'error': '超时'}
```

## 📊 使用限制

### GitHub Actions免费额度

- **私有仓库**: 每月2000分钟
- **公开仓库**: 无限（推荐使用公开仓库）
- **并发**: 最多20个workflow同时运行

### 成本考虑

- 每次解析大约需要30-60秒
- 私有仓库：约33-66次/月（免费）
- 公开仓库：无限制

## 🔐 安全建议

1. **使用公开仓库**: 避免消耗免费额度
2. **Token权限**: 只授予必要的权限
3. **Secrets管理**: 不要在代码中硬编码token
4. **速率限制**: GitHub API有速率限制，注意控制请求频率

## 🚀 部署为API服务

### 方案1: 使用Flask创建API服务

```python
# api_server.py
from flask import Flask, request, jsonify
from github_actions_api_server import GitHubActionsParser
import os

app = Flask(__name__)

parser = GitHubActionsParser(
    token=os.getenv('GITHUB_TOKEN'),
    owner=os.getenv('GITHUB_OWNER'),
    repo=os.getenv('GITHUB_REPO')
)

@app.route('/api/parse', methods=['GET'])
def parse_video():
    video_url = request.args.get('video_url')
    
    if not video_url:
        return jsonify({'error': '缺少video_url参数'}), 400
    
    result = parser.trigger_parse_workflow(video_url)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### 方案2: 使用Vercel/Netlify Functions

创建 `api/parse.py`:

```python
from github_actions_api_server import GitHubActionsParser
import os

def handler(request):
    video_url = request.args.get('video_url')
    
    parser = GitHubActionsParser(
        token=os.getenv('GITHUB_TOKEN'),
        owner=os.getenv('GITHUB_OWNER'),
        repo=os.getenv('GITHUB_REPO')
    )
    
    result = parser.trigger_parse_workflow(video_url)
    return result
```

## 📚 相关文件

- `.github/workflows/video_parser_api.yml` - 主workflow
- `.github/workflows/video_parser_webhook.yml` - Webhook workflow
- `github_actions_api_server.py` - Python客户端库

## ✅ 优势总结

相比Cloudflare Workers：
- ✅ 可以运行Python脚本
- ✅ 无需处理SSL/代理问题
- ✅ 已验证可用（使用本地Python脚本）
- ✅ 免费额度充足（公开仓库）

相比本地服务器：
- ✅ 无需维护服务器
- ✅ 自动扩展
- ✅ 免费（公开仓库）

## 🎯 推荐使用场景

1. **公开仓库**: 无限免费额度
2. **API服务**: 通过API触发，适合集成到其他系统
3. **定时任务**: 可以设置定时解析
4. **批量处理**: 可以处理多个视频

