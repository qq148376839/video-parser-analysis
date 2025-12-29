# 文件归档说明

## 📋 归档目的

为了保持项目目录整洁，将与NAS部署无关的文件归档到`archive`目录。

## 📁 需要归档的文件

### GitHub Actions相关
- `GITHUB_ACTIONS_SETUP.md`
- `GITHUB_ACTIONS_QUICK_START.md`
- `GITHUB_UPLOAD_GUIDE.md`
- `GITHUB_ACTIONS_API_GUIDE.md`
- `github_actions_api_server.py`
- `test_github_actions_api.py`

### Cloudflare Workers相关
- `cloudflare_deployment_guide.md`
- `CLOUDFLARE_DEPLOYMENT_SUMMARY.md`
- `FINAL_CLOUDFLARE_SOLUTION.md`
- `cloudflare_worker_parser.js`
- `wrangler.toml`
- `wrangler.toml.example`
- `WORKER_ERROR_4000_SOLUTION.md`
- `WORKER_FINAL_SOLUTION.md`
- `WORKER_PROXY_SOLUTION.md`
- `TROUBLESHOOTING_525.md`

### 分析和捕获脚本
- `analyze_*.py`、`analyze_*.js`
- `capture_*.py`
- `extract_js_code.py`
- `update_parser_with_z_api.py`
- `organize_jx2s0_files.py`
- `browser_decrypt_parser.py`
- `final_direct_parser.py`（保留v2版本）

### 输出文件
- `*.json`（除了config.json）
- `*.html`
- `*.m3u8`
- `*.mp4`
- `extracted_iframe_js/`目录

### 其他文档
- 各种分析文档和指南（保留`NAS_DEPLOYMENT_PRD.md`和`README.md`）

## ✅ 需要保留的文件

### 核心文件
- `NAS_DEPLOYMENT_PRD.md` - NAS部署需求文档
- `README.md` - 项目说明
- `PROJECT_STRUCTURE.md` - 项目结构说明
- `config.json.example` - 配置文件示例
- `requirements.txt` - Python依赖

### 解析器文件
- `final_direct_parser_v2.py` - 解密解析器（备选方案）
- `direct_videocdn_parser_simple.py` - z参数解析器
- `z_param_api_service.py` - z参数API服务

### 目录
- `jx2s0_analysis/` - jx2s0解析器分析（保留）

## 🔧 手动归档步骤

1. 创建archive目录：
   ```bash
   mkdir archive
   ```

2. 移动文件（Windows PowerShell）：
   ```powershell
   # GitHub Actions相关
   Move-Item GITHUB_ACTIONS*.md archive\
   Move-Item github_actions*.py archive\
   Move-Item test_github_actions*.py archive\
   
   # Cloudflare相关
   Move-Item cloudflare*.md archive\
   Move-Item CLOUDFLARE*.md archive\
   Move-Item FINAL_CLOUDFLARE*.md archive\
   Move-Item WORKER*.md archive\
   Move-Item TROUBLESHOOTING*.md archive\
   Move-Item cloudflare*.js archive\
   Move-Item wrangler.toml* archive\
   
   # 分析和捕获脚本
   Move-Item analyze_*.py archive\
   Move-Item analyze_*.js archive\
   Move-Item capture_*.py archive\
   Move-Item extract_js_code.py archive\
   Move-Item update_parser_with_z_api.py archive\
   Move-Item organize_jx2s0_files.py archive\
   Move-Item browser_decrypt_parser.py archive\
   Move-Item final_direct_parser.py archive\
   
   # 输出文件
   Move-Item *.json archive\ -Exclude config.json.example
   Move-Item *.html archive\
   Move-Item *.m3u8 archive\
   Move-Item *.mp4 archive\
   Move-Item extracted_iframe_js archive\
   ```

3. 验证：
   ```powershell
   # 检查archive目录
   Get-ChildItem archive\ | Select-Object Name
   ```

## 📌 注意事项

- 归档操作不会删除文件，只是移动到archive目录
- 如果需要使用归档的文件，可以从archive目录中找回
- 建议在归档前先备份重要文件

