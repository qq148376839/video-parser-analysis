 # GitHub Actions 视频解析 - 快速开始

## 🚀 5分钟快速部署

### 步骤1: 准备GitHub Token

1. 访问: https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 选择权限: `repo` 和 `workflow`
4. 复制token

### 步骤2: 上传代码到GitHub

```bash
# 初始化git（如果还没有）
git init
git add .
git commit -m "Add GitHub Actions video parser"

# 创建GitHub仓库并推送
git remote add origin https://github.com/your-username/video-parser-analysis.git
git push -u origin main
```

### 步骤3: 测试Workflow

#### 方式1: 通过GitHub UI

1. 访问: `https://github.com/your-username/video-parser-analysis/actions`
2. 点击 "Video Parser API" workflow
3. 点击 "Run workflow"
4. 输入视频URL: `https://www.iqiyi.com/v_1c168e2yzbk.html`
5. 点击 "Run workflow"
6. 等待完成，查看结果

#### 方式2: 通过API

```bash
# 设置token
export GITHUB_TOKEN=your_token
export GITHUB_OWNER=your-username
export GITHUB_REPO=video-parser-analysis

# 运行测试脚本
python3 test_github_actions_api.py
```

## 📝 使用方式

### 方式1: 手动触发（UI）

适合偶尔使用，通过GitHub网页界面操作。

### 方式2: API触发（推荐）

适合集成到其他系统，通过API调用。

```python
from github_actions_api_server import GitHubActionsParser

parser = GitHubActionsParser(
    token='your-token',
    owner='your-username',
    repo='video-parser-analysis'
)

result = parser.trigger_parse_workflow('https://www.iqiyi.com/v_1c168e2yzbk.html')
```

### 方式3: Webhook触发

适合从外部系统触发，通过HTTP请求。

```bash
curl -X POST \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/your-username/video-parser-analysis/dispatches \
  -d '{
    "event_type": "parse-video",
    "client_payload": {
      "video_url": "https://www.iqiyi.com/v_1c168e2yzbk.html"
    }
  }'
```

## 🔍 查看结果

### 方式1: 通过GitHub UI

1. 访问Actions页面
2. 点击对应的workflow运行
3. 查看 "Parse video" 步骤的输出
4. 下载 "parse-result" artifact

### 方式2: 通过API获取

```python
# 获取最近的workflow运行
runs = parser.get_workflow_runs(limit=1)
if runs:
    run_id = runs[0]['id']
    result = parser.get_workflow_run_result(run_id)
    print(result)
```

## ⚙️ 配置说明

### Workflow文件

- `.github/workflows/video_parser_api.yml` - 主解析workflow
- `.github/workflows/update_params.yml` - 自动更新参数workflow

### 环境变量

如果需要，可以在GitHub仓库的Settings > Secrets中设置：
- `GITHUB_TOKEN` - 用于API调用（如果从外部调用）

## 📊 优势

相比Cloudflare Workers：
- ✅ 可以运行Python脚本
- ✅ 无需处理SSL/代理问题
- ✅ 已验证可用
- ✅ 免费额度充足（公开仓库无限）

## 🎯 推荐配置

1. **使用公开仓库**: 无限免费额度
2. **设置自动更新参数**: 每天自动更新z参数
3. **通过API调用**: 适合集成到其他系统

## 📚 详细文档

- `GITHUB_ACTIONS_API_GUIDE.md` - 完整使用指南
- `github_actions_api_server.py` - Python客户端库
- `test_github_actions_api.py` - 测试脚本

