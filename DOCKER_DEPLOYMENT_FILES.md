# Docker部署文件清单

## 📋 必需文件（核心功能）

### 1. 主应用文件
```
api_server.py                    # FastAPI主服务（必需）
healthcheck.py                  # Docker健康检查脚本（必需）
```

### 2. 解析器模块（parsers/）
```
parsers/
├── __init__.py                 # Python包标识（必需）
├── z_param_parser.py          # z参数解析器（必需）
├── decrypt_parser.py          # 解密解析器（必需）
└── search_parser.py           # 资源检索解析器（必需）
```

### 3. 工具模块（utils/）
```
utils/
├── __init__.py                 # Python包标识（必需）
├── logger.py                   # 日志工具（必需）
├── config_loader.py            # 配置加载器（必需）
└── z_param_manager.py          # z参数管理器（必需）
```

### 4. 核心解析逻辑
```
final_direct_parser_v2.py       # 解密解析核心逻辑（必需）
direct_videocdn_parser_simple.py # z参数解析核心逻辑（必需）
```

### 5. Docker配置文件
```
Dockerfile                      # Docker镜像构建文件（必需）
docker-compose.yml              # Docker Compose配置（必需）
.dockerignore                   # Docker构建忽略文件（推荐）
```

### 6. 依赖和配置
```
requirements.txt                # Python依赖列表（必需）
config.json.example             # 配置文件示例（必需）
```

### 7. 启动脚本（可选但推荐）
```
start.sh                        # Linux启动脚本（可选）
```

## 📁 目录结构

部署时的完整目录结构应该是：

```
video-parser-service/
├── api_server.py
├── healthcheck.py
├── final_direct_parser_v2.py
├── direct_videocdn_parser_simple.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── config.json.example
├── start.sh
├── parsers/
│   ├── __init__.py
│   ├── z_param_parser.py
│   ├── decrypt_parser.py
│   └── search_parser.py
└── utils/
    ├── __init__.py
    ├── logger.py
    ├── config_loader.py
    └── z_param_manager.py
```

## 🚫 不需要的文件

以下文件**不需要**包含在Docker部署中：

### 测试文件
- `test_*.py` - 所有测试脚本
- `extract_z_param.py` - 调试工具

### 文档文件
- `*.md` - 所有Markdown文档（除了README.md可选）
- `ARCHIVE_README.md`
- `LOCAL_TESTING.md`
- `TROUBLESHOOTING.md`
- 等等

### 归档文件
- `archive/` - 整个归档目录
- `z_param_api_service.py` - Flask版本（已废弃）

### 本地开发文件
- `start_local.bat` - Windows批处理脚本
- `captured_*.json` - 临时捕获文件
- `*.html` - 调试HTML文件
- `*.m3u8` - 临时文件
- `downloaded_js/` - 下载的JS文件

### 数据文件（运行时生成）
- `data/` - 数据目录（通过volume挂载，不需要复制）
- `logs/` - 日志目录（运行时生成）
- `__pycache__/` - Python缓存（不需要）

## 📝 最小化部署清单

如果只需要最小化部署，以下文件是**绝对必需**的：

```
必需文件（15个）：
1. api_server.py
2. healthcheck.py
3. final_direct_parser_v2.py
4. direct_videocdn_parser_simple.py
5. requirements.txt
6. Dockerfile
7. docker-compose.yml
8. config.json.example
9. parsers/__init__.py
10. parsers/z_param_parser.py
11. parsers/decrypt_parser.py
12. parsers/search_parser.py
13. utils/__init__.py
14. utils/logger.py
15. utils/config_loader.py
16. utils/z_param_manager.py
```

## 🔧 快速创建部署项目

### 方法1：手动复制文件

```bash
# 创建新项目目录
mkdir video-parser-service
cd video-parser-service

# 复制必需文件
cp ../video-parser-analysis/api_server.py .
cp ../video-parser-analysis/healthcheck.py .
cp ../video-parser-analysis/final_direct_parser_v2.py .
cp ../video-parser-analysis/direct_videocdn_parser_simple.py .
cp ../video-parser-analysis/requirements.txt .
cp ../video-parser-analysis/Dockerfile .
cp ../video-parser-analysis/docker-compose.yml .
cp ../video-parser-analysis/config.json.example .
cp ../video-parser-analysis/.dockerignore .

# 复制目录
cp -r ../video-parser-analysis/parsers .
cp -r ../video-parser-analysis/utils .
```

### 方法2：使用脚本（推荐）

创建一个部署脚本 `create_deployment.sh`：

```bash
#!/bin/bash
# 创建Docker部署项目

SOURCE_DIR="video-parser-analysis"
TARGET_DIR="video-parser-service"

# 创建目标目录
mkdir -p "$TARGET_DIR"
mkdir -p "$TARGET_DIR/parsers"
mkdir -p "$TARGET_DIR/utils"

# 复制核心文件
cp "$SOURCE_DIR/api_server.py" "$TARGET_DIR/"
cp "$SOURCE_DIR/healthcheck.py" "$TARGET_DIR/"
cp "$SOURCE_DIR/final_direct_parser_v2.py" "$TARGET_DIR/"
cp "$SOURCE_DIR/direct_videocdn_parser_simple.py" "$TARGET_DIR/"
cp "$SOURCE_DIR/requirements.txt" "$TARGET_DIR/"
cp "$SOURCE_DIR/Dockerfile" "$TARGET_DIR/"
cp "$SOURCE_DIR/docker-compose.yml" "$TARGET_DIR/"
cp "$SOURCE_DIR/config.json.example" "$TARGET_DIR/"
cp "$SOURCE_DIR/.dockerignore" "$TARGET_DIR/" 2>/dev/null || true
cp "$SOURCE_DIR/start.sh" "$TARGET_DIR/" 2>/dev/null || true

# 复制parsers目录
cp "$SOURCE_DIR/parsers/__init__.py" "$TARGET_DIR/parsers/"
cp "$SOURCE_DIR/parsers/z_param_parser.py" "$TARGET_DIR/parsers/"
cp "$SOURCE_DIR/parsers/decrypt_parser.py" "$TARGET_DIR/parsers/"
cp "$SOURCE_DIR/parsers/search_parser.py" "$TARGET_DIR/parsers/"

# 复制utils目录
cp "$SOURCE_DIR/utils/__init__.py" "$TARGET_DIR/utils/"
cp "$SOURCE_DIR/utils/logger.py" "$TARGET_DIR/utils/"
cp "$SOURCE_DIR/utils/config_loader.py" "$TARGET_DIR/utils/"
cp "$SOURCE_DIR/utils/z_param_manager.py" "$TARGET_DIR/utils/"

echo "✅ 部署项目已创建: $TARGET_DIR"
echo ""
echo "📋 文件清单:"
find "$TARGET_DIR" -type f | sort
```

## 📦 文件说明

### api_server.py
- **作用**：FastAPI主服务，提供API接口
- **必需**：是
- **说明**：所有API请求的入口

### healthcheck.py
- **作用**：Docker健康检查脚本
- **必需**：是
- **说明**：用于Docker健康检查

### final_direct_parser_v2.py
- **作用**：解密解析核心逻辑
- **必需**：是
- **说明**：备选解析方案的核心实现

### direct_videocdn_parser_simple.py
- **作用**：z参数解析核心逻辑
- **必需**：是
- **说明**：主要解析方案的核心实现

### parsers/z_param_parser.py
- **作用**：z参数解析器封装
- **必需**：是
- **说明**：调用核心逻辑，管理z参数

### parsers/decrypt_parser.py
- **作用**：解密解析器封装
- **必需**：是
- **说明**：备选解析方案

### parsers/search_parser.py
- **作用**：资源检索和解析
- **必需**：是
- **说明**：搜索接口的核心实现

### utils/z_param_manager.py
- **作用**：z参数管理器
- **必需**：是
- **说明**：z参数的获取、更新、缓存

### utils/config_loader.py
- **作用**：配置加载器
- **必需**：是
- **说明**：加载config.json配置

### utils/logger.py
- **作用**：日志工具
- **必需**：是
- **说明**：统一日志管理

## 🔍 验证清单

部署前请确认：

- [ ] 所有必需文件都已复制
- [ ] `requirements.txt` 包含所有依赖
- [ ] `config.json.example` 存在
- [ ] `Dockerfile` 配置正确
- [ ] `docker-compose.yml` 端口映射正确
- [ ] `.dockerignore` 已配置（排除不需要的文件）
- [ ] 所有Python文件语法正确
- [ ] 目录结构完整（parsers/, utils/）

## 🚀 部署步骤

1. **创建部署项目**（使用上面的脚本）
2. **准备配置文件**：
   ```bash
   cd video-parser-service
   mkdir -p data
   cp config.json.example data/config.json
   # 编辑 data/config.json，配置API站点
   ```
3. **构建和启动**：
   ```bash
   docker-compose build
   docker-compose up -d
   ```
4. **验证**：
   ```bash
   docker-compose logs -f
   curl http://localhost:1233/health
   ```

## 📌 注意事项

1. **数据持久化**：`data/` 目录通过volume挂载，确保数据不丢失
2. **配置文件**：首次部署需要手动创建 `data/config.json`
3. **z参数**：首次运行会自动尝试获取，如果失败可手动设置
4. **日志**：日志保存在 `data/logs/` 目录
5. **端口**：默认外部端口1233，可在docker-compose.yml中修改

