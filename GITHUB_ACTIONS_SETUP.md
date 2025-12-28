# GitHub Actions 视频解析服务 - 完整设置指南

## 📋 概述

使用GitHub Actions作为视频解析API服务，完全绕过Cloudflare Workers的限制。

## ✨ 优势

- ✅ **无需服务器**: 使用GitHub Actions的免费额度
- ✅ **Python环境**: 可以直接运行已验证的Python脚本
- ✅ **免费额度**: 公开仓库无限，私有仓库每月2000分钟
- ✅ **自动扩展**: GitHub自动处理并发
- ✅ **已验证可用**: 使用本地已验证的Python脚本

## 🚀 快速开始（3步）

### 步骤1: 创建GitHub Personal Access Token

1. 访问: https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 选择权限:
   - ✅ `repo` (完整仓库权限)
   - ✅ `workflow` (工作流权限)
4. 复制token（只显示一次，请保存）

### 步骤2: 上传代码到GitHub

```bash
# 如果还没有git仓库
git init
git add .
git commit -m "Add GitHub Actions video parser"

# 创建GitHub仓库（在GitHub网页上创建）
# 然后推送代码
git remote add origin https://github.com/your-username/video-parser-analysis.git
git branch -M main
git push -u origin main
```

### 步骤3: 测试Workflow

#### 方式A: 通过GitHub UI（最简单）

1. 访问: `https://github.com/your-username/video-parser-analysis/actions`
2. 点击左侧 "Video Parser Simple" workflow
3. 点击右侧 "Run workflow" 按钮
4. 输入视频URL: `https://www.iqiyi.com/v_1c168e2yzbk.html`
5. 点击绿色的 "Run workflow" 按钮
6. 等待运行完成（约30-60秒）
7. 点击运行记录，查看结果

#### 方式B: 通过API（适合集成）

```bash
# 设置环境变量
export GITHUB_TOKEN=your_token
export GITHUB_OWNER=your-username
export GITHUB_REPO=video-parser-analysis

# 运行测试
python3 test_github_actions_api.py
```

## 📝 使用方式详解

### 方式1: 手动触发（UI）

**适合**: 偶尔使用，测试

**步骤**:
1. 访问Actions页面
2. 选择workflow
3. 点击"Run workflow"
4. 输入视频URL
5. 查看结果

### 方式2: API触发（推荐）

**适合**: 集成到其他系统

**Python示例**:

```python
from github_actions_api_server import GitHubActionsParser

parser = GitHubActionsParser(
    token='your-token',
    owner='your-username',
    repo='video-parser-analysis'
)

# 触发解析
result = parser.trigger_parse_workflow('https://www.iqiyi.com/v_1c168e2yzbk.html')
print(result)
```

**cURL示例**:

```bash
curl -X POST \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/your-username/video-parser-analysis/actions/workflows/video_parser_simple.yml/dispatches \
  -d '{
    "ref": "main",
    "inputs": {
      "video_url": "https://www.iqiyi.com/v_1c168e2yzbk.html"
    }
  }'
```

### 方式3: Webhook触发

**适合**: 从外部系统触发

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

### 通过GitHub UI

1. 访问Actions页面
2. 点击对应的workflow运行
3. 查看 "Parse video" 步骤的输出
4. 下载 "parse-result" artifact（包含JSON结果）

### 通过API获取

```python
# 获取最近的workflow运行
runs = parser.get_workflow_runs(limit=1)
if runs:
    run_id = runs[0]['id']
    # 下载artifact获取结果
    result = parser.get_workflow_run_result(run_id)
```

## ⚙️ 配置说明

### Workflow文件

- `.github/workflows/video_parser_simple.yml` - 简化版（推荐使用）
- `.github/workflows/video_parser_api.yml` - 完整版（支持webhook）
- `.github/workflows/update_params.yml` - 自动更新参数

### 环境变量

在GitHub仓库的 Settings > Secrets 中设置（如果需要从外部API调用）:
- `GITHUB_TOKEN` - GitHub Personal Access Token

## 📊 使用限制

### GitHub Actions免费额度

- **公开仓库**: ✅ 无限（推荐）
- **私有仓库**: 每月2000分钟
- **并发**: 最多20个workflow同时运行

### 成本估算

- 每次解析: 约30-60秒
- 私有仓库: 约33-66次/月（免费）
- 公开仓库: 无限制

## 🔄 自动更新参数

`.github/workflows/update_params.yml` 会自动：
- 每天UTC 2点（北京时间10点）更新z参数
- 自动提交到仓库

**注意**: 需要安装playwright，可能需要更长时间。

## 🎯 最佳实践

1. **使用公开仓库**: 获得无限免费额度
2. **设置自动更新参数**: 确保z参数始终有效
3. **通过API调用**: 适合集成到其他系统
4. **监控workflow**: 定期检查是否正常运行

## 📚 相关文件

- `.github/workflows/video_parser_simple.yml` - 主workflow（推荐）
- `github_actions_api_server.py` - Python客户端库
- `test_github_actions_api.py` - 测试脚本
- `GITHUB_ACTIONS_API_GUIDE.md` - 详细API文档

## ✅ 优势总结

相比Cloudflare Workers：
- ✅ 可以运行Python脚本
- ✅ 无需处理SSL/代理问题
- ✅ 已验证可用
- ✅ 免费额度充足

相比本地服务器：
- ✅ 无需维护服务器
- ✅ 自动扩展
- ✅ 免费（公开仓库）

## 🆘 故障排除

### 问题1: Workflow运行失败

**检查**:
1. 查看workflow日志
2. 检查Python脚本是否有错误
3. 检查依赖是否正确安装

### 问题2: 无法触发workflow

**检查**:
1. Token权限是否正确
2. 仓库名称是否正确
3. workflow文件路径是否正确

### 问题3: 解析失败

**检查**:
1. z参数是否过期（运行update_params workflow）
2. 视频URL是否正确
3. 网络连接是否正常

