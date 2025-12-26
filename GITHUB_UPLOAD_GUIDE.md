# GitHub 上传指南

## 📋 前置准备

1. **确保已安装 Git**
   ```bash
   git --version
   ```
   如果未安装，请访问：https://git-scm.com/downloads

2. **配置 Git 用户信息**（如果还没配置）
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

3. **确保有 GitHub 账号**
   - 如果没有，请访问 https://github.com 注册账号

---

## 🚀 操作步骤

### 步骤 1: 初始化 Git 仓库

在项目目录下打开终端（PowerShell 或 CMD），执行：

```bash
cd "D:\Python脚本\video-parser-analysis"
git init
```

### 步骤 2: 检查 .gitignore 文件

项目已包含 `.gitignore` 文件，会自动忽略以下文件：
- Python 缓存文件（`__pycache__/`）
- 输出文件（`*.mp4`, `*.m3u8`, `*.json`, `*.html`）
- 虚拟环境（`venv/`, `env/`）
- IDE 配置文件

### 步骤 3: 添加文件到 Git

```bash
# 查看将要添加的文件（预览）
git status

# 添加所有文件
git add .

# 再次查看状态，确认文件已添加
git status
```

### 步骤 4: 提交代码

```bash
git commit -m "Initial commit: Video parser analysis project"
```

### 步骤 5: 在 GitHub 创建仓库

1. **登录 GitHub**：访问 https://github.com
2. **创建新仓库**：
   - 点击右上角的 `+` 号，选择 `New repository`
   - Repository name: `video-parser-analysis`（或你喜欢的名字）
   - Description: `视频解析网站技术分析项目`
   - 选择 `Public`（公开）或 `Private`（私有）
   - **不要**勾选 "Initialize this repository with a README"（因为本地已有代码）
   - 点击 `Create repository`

### 步骤 6: 连接本地仓库到 GitHub

GitHub 创建仓库后，会显示一个页面，复制其中的命令。通常如下：

```bash
# 添加远程仓库（将 YOUR_USERNAME 替换为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/video-parser-analysis.git

# 或者使用 SSH（如果你配置了 SSH 密钥）
git remote add origin git@github.com:YOUR_USERNAME/video-parser-analysis.git
```

### 步骤 7: 推送代码到 GitHub

```bash
# 推送代码（首次推送）
git branch -M main
git push -u origin main
```

如果使用 `master` 分支：
```bash
git branch -M master
git push -u origin master
```

---

## 🔐 身份验证

### 方式 1: Personal Access Token（推荐）

如果推送时提示需要身份验证：

1. **生成 Token**：
   - 访问：https://github.com/settings/tokens
   - 点击 `Generate new token` -> `Generate new token (classic)`
   - 设置名称和过期时间
   - 勾选 `repo` 权限
   - 点击 `Generate token`
   - **复制生成的 token**（只显示一次）

2. **使用 Token**：
   - 推送时，用户名输入你的 GitHub 用户名
   - 密码输入刚才生成的 token

### 方式 2: GitHub CLI

```bash
# 安装 GitHub CLI
# Windows: winget install GitHub.cli

# 登录
gh auth login

# 然后正常推送
git push -u origin main
```

### 方式 3: SSH 密钥（推荐用于长期使用）

1. **生成 SSH 密钥**：
   ```bash
   ssh-keygen -t ed25519 -C "your.email@example.com"
   ```

2. **复制公钥**：
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```

3. **添加到 GitHub**：
   - 访问：https://github.com/settings/keys
   - 点击 `New SSH key`
   - 粘贴公钥内容
   - 点击 `Add SSH key`

4. **使用 SSH URL**：
   ```bash
   git remote set-url origin git@github.com:YOUR_USERNAME/video-parser-analysis.git
   ```

---

## ✅ 验证上传成功

1. **刷新 GitHub 仓库页面**，应该能看到所有文件
2. **检查文件**：确认重要文件都已上传
3. **查看提交历史**：应该能看到 "Initial commit"

---

## 🔄 后续更新代码

以后修改代码后，使用以下命令更新 GitHub：

```bash
# 1. 查看修改的文件
git status

# 2. 添加修改的文件
git add .

# 3. 提交修改
git commit -m "描述你的修改内容"

# 4. 推送到 GitHub
git push
```

---

## 📝 常见问题

### Q1: 推送时提示 "remote: Support for password authentication was removed"

**A**: GitHub 已不再支持密码认证，需要使用 Personal Access Token 或 SSH 密钥。

### Q2: 如何忽略大文件（如 output.mp4）？

**A**: 项目中的 `.gitignore` 已包含 `*.mp4`，但如果你之前已经提交了大文件，需要：

```bash
# 从 Git 历史中删除大文件（但保留本地文件）
git rm --cached output.mp4
git commit -m "Remove large file from git"
git push
```

### Q3: 如何修改远程仓库地址？

```bash
# 查看当前远程地址
git remote -v

# 修改远程地址
git remote set-url origin https://github.com/YOUR_USERNAME/NEW_REPO_NAME.git
```

### Q4: 如何只推送部分文件？

```bash
# 只添加特定文件
git add file1.py file2.py

# 提交并推送
git commit -m "Update specific files"
git push
```

---

## 🎯 快速命令总结

```bash
# 完整流程（首次上传）
cd "D:\Python脚本\video-parser-analysis"
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/video-parser-analysis.git
git branch -M main
git push -u origin main

# 后续更新
git add .
git commit -m "Update description"
git push
```

---

**提示**：如果遇到任何问题，可以查看 Git 错误信息，或访问 GitHub 帮助文档。

