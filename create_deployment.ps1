# PowerShell脚本 - 创建Docker部署项目

$SOURCE_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$TARGET_DIR = "video-parser-service"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "创建Docker部署项目" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "源目录: $SOURCE_DIR"
Write-Host "目标目录: $TARGET_DIR"
Write-Host ""

# 检查源目录
if (-not (Test-Path "$SOURCE_DIR\api_server.py")) {
    Write-Host "❌ 错误: 源目录不正确，找不到 api_server.py" -ForegroundColor Red
    exit 1
}

# 创建目标目录
Write-Host "📁 创建目录结构..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "$TARGET_DIR" | Out-Null
New-Item -ItemType Directory -Force -Path "$TARGET_DIR\parsers" | Out-Null
New-Item -ItemType Directory -Force -Path "$TARGET_DIR\utils" | Out-Null
New-Item -ItemType Directory -Force -Path "$TARGET_DIR\data" | Out-Null

# 复制核心文件
Write-Host "📋 复制核心文件..." -ForegroundColor Yellow
Copy-Item "$SOURCE_DIR\api_server.py" "$TARGET_DIR\" -Force | Out-Null; Write-Host "  ✅ api_server.py" -ForegroundColor Green
Copy-Item "$SOURCE_DIR\healthcheck.py" "$TARGET_DIR\" -Force | Out-Null; Write-Host "  ✅ healthcheck.py" -ForegroundColor Green
Copy-Item "$SOURCE_DIR\final_direct_parser_v2.py" "$TARGET_DIR\" -Force | Out-Null; Write-Host "  ✅ final_direct_parser_v2.py" -ForegroundColor Green
Copy-Item "$SOURCE_DIR\direct_videocdn_parser_simple.py" "$TARGET_DIR\" -Force | Out-Null; Write-Host "  ✅ direct_videocdn_parser_simple.py" -ForegroundColor Green

# 复制配置文件
Write-Host "📋 复制配置文件..." -ForegroundColor Yellow
Copy-Item "$SOURCE_DIR\requirements.txt" "$TARGET_DIR\" -Force | Out-Null; Write-Host "  ✅ requirements.txt" -ForegroundColor Green
Copy-Item "$SOURCE_DIR\Dockerfile" "$TARGET_DIR\" -Force | Out-Null; Write-Host "  ✅ Dockerfile" -ForegroundColor Green
Copy-Item "$SOURCE_DIR\docker-compose.yml" "$TARGET_DIR\" -Force | Out-Null; Write-Host "  ✅ docker-compose.yml" -ForegroundColor Green
Copy-Item "$SOURCE_DIR\config.json.example" "$TARGET_DIR\" -Force | Out-Null; Write-Host "  ✅ config.json.example" -ForegroundColor Green

# 复制可选文件
if (Test-Path "$SOURCE_DIR\.dockerignore") {
    Copy-Item "$SOURCE_DIR\.dockerignore" "$TARGET_DIR\" -Force | Out-Null; Write-Host "  ✅ .dockerignore" -ForegroundColor Green
}
if (Test-Path "$SOURCE_DIR\start.sh") {
    Copy-Item "$SOURCE_DIR\start.sh" "$TARGET_DIR\" -Force | Out-Null; Write-Host "  ✅ start.sh" -ForegroundColor Green
}

# 复制parsers目录
Write-Host "📋 复制parsers模块..." -ForegroundColor Yellow
Copy-Item "$SOURCE_DIR\parsers\__init__.py" "$TARGET_DIR\parsers\" -Force | Out-Null; Write-Host "  ✅ parsers\__init__.py" -ForegroundColor Green
Copy-Item "$SOURCE_DIR\parsers\z_param_parser.py" "$TARGET_DIR\parsers\" -Force | Out-Null; Write-Host "  ✅ parsers\z_param_parser.py" -ForegroundColor Green
Copy-Item "$SOURCE_DIR\parsers\decrypt_parser.py" "$TARGET_DIR\parsers\" -Force | Out-Null; Write-Host "  ✅ parsers\decrypt_parser.py" -ForegroundColor Green
Copy-Item "$SOURCE_DIR\parsers\search_parser.py" "$TARGET_DIR\parsers\" -Force | Out-Null; Write-Host "  ✅ parsers\search_parser.py" -ForegroundColor Green

# 复制utils目录
Write-Host "📋 复制utils模块..." -ForegroundColor Yellow
Copy-Item "$SOURCE_DIR\utils\__init__.py" "$TARGET_DIR\utils\" -Force | Out-Null; Write-Host "  ✅ utils\__init__.py" -ForegroundColor Green
Copy-Item "$SOURCE_DIR\utils\logger.py" "$TARGET_DIR\utils\" -Force | Out-Null; Write-Host "  ✅ utils\logger.py" -ForegroundColor Green
Copy-Item "$SOURCE_DIR\utils\config_loader.py" "$TARGET_DIR\utils\" -Force | Out-Null; Write-Host "  ✅ utils\config_loader.py" -ForegroundColor Green
Copy-Item "$SOURCE_DIR\utils\z_param_manager.py" "$TARGET_DIR\utils\" -Force | Out-Null; Write-Host "  ✅ utils\z_param_manager.py" -ForegroundColor Green

# 创建配置文件
Write-Host "📋 准备配置文件..." -ForegroundColor Yellow
$configPath = Join-Path $TARGET_DIR "data\config.json"
if (-not (Test-Path $configPath)) {
    Copy-Item "$SOURCE_DIR\config.json.example" $configPath -Force
    Write-Host "  ✅ 已创建 data\config.json（请编辑配置）" -ForegroundColor Green
} else {
    Write-Host "  ℹ️  data\config.json 已存在，跳过" -ForegroundColor Yellow
}

# 创建README
$README_CONTENT = @'
# 视频解析服务 - Docker部署版

## 快速开始

### 1. 配置
编辑 `data/config.json`，配置API站点。

### 2. 构建和启动
```bash
docker-compose build
docker-compose up -d
```

### 3. 验证
```bash
# 查看日志
docker-compose logs -f

# 健康检查
curl http://localhost:1233/health

# API文档
浏览器访问: http://localhost:1233/docs
```

## API接口

### 解析接口
```
GET /api/v1/parse?url=<视频URL>&parser_url=<解析网站URL>
```

### 搜索接口
```
GET /api/v1/search?ac=videolist&wd=<关键词>&page=<页码>
```

## 配置说明

配置文件：`data/config.json`

- `cache_time`: 缓存时间（秒）
- `api_site`: API站点配置列表

## 数据目录

- `data/config.json`: 配置文件
- `data/z_params.json`: z参数缓存（自动生成）
- `data/logs/`: 日志文件

## 故障排查

1. 查看日志：`docker-compose logs -f`
2. 检查健康状态：`curl http://localhost:1233/health`
3. 查看z参数状态：检查日志中的z参数相关信息
'@

Set-Content -Path "$TARGET_DIR\README.md" -Value $README_CONTENT -Encoding UTF8

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "✅ 部署项目创建完成！" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📁 项目目录: $TARGET_DIR" -ForegroundColor Yellow
Write-Host ""
Write-Host "📋 文件清单:" -ForegroundColor Yellow
$rootPath = (Resolve-Path $PWD.Path).Path
Get-ChildItem -Path "$TARGET_DIR" -Recurse -File | Where-Object { 
    $_.FullName -notlike "*\data\*" 
} | ForEach-Object { 
    $relativePath = $_.FullName.Replace($rootPath + '\', '')
    Write-Host "  $relativePath" 
}
Write-Host ""
Write-Host "📝 下一步:" -ForegroundColor Yellow
Write-Host "  1. cd $TARGET_DIR" -ForegroundColor White
Write-Host "  2. 编辑 data\config.json 配置API站点" -ForegroundColor White
Write-Host "  3. docker-compose build" -ForegroundColor White
Write-Host "  4. docker-compose up -d" -ForegroundColor White
Write-Host ""

