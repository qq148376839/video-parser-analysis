#!/bin/bash
# 创建Docker部署项目脚本

SOURCE_DIR="$(dirname "$0")"
TARGET_DIR="video-parser-service"

echo "============================================================"
echo "创建Docker部署项目"
echo "============================================================"
echo "源目录: $SOURCE_DIR"
echo "目标目录: $TARGET_DIR"
echo ""

# 检查源目录
if [ ! -f "$SOURCE_DIR/api_server.py" ]; then
    echo "❌ 错误: 源目录不正确，找不到 api_server.py"
    exit 1
fi

# 创建目标目录
echo "📁 创建目录结构..."
mkdir -p "$TARGET_DIR"
mkdir -p "$TARGET_DIR/parsers"
mkdir -p "$TARGET_DIR/utils"
mkdir -p "$TARGET_DIR/data"

# 复制核心文件
echo "📋 复制核心文件..."
cp "$SOURCE_DIR/api_server.py" "$TARGET_DIR/" && echo "  ✅ api_server.py"
cp "$SOURCE_DIR/healthcheck.py" "$TARGET_DIR/" && echo "  ✅ healthcheck.py"
cp "$SOURCE_DIR/final_direct_parser_v2.py" "$TARGET_DIR/" && echo "  ✅ final_direct_parser_v2.py"
cp "$SOURCE_DIR/direct_videocdn_parser_simple.py" "$TARGET_DIR/" && echo "  ✅ direct_videocdn_parser_simple.py"

# 复制配置文件
echo "📋 复制配置文件..."
cp "$SOURCE_DIR/requirements.txt" "$TARGET_DIR/" && echo "  ✅ requirements.txt"
cp "$SOURCE_DIR/Dockerfile" "$TARGET_DIR/" && echo "  ✅ Dockerfile"
cp "$SOURCE_DIR/docker-compose.yml" "$TARGET_DIR/" && echo "  ✅ docker-compose.yml"
cp "$SOURCE_DIR/config.json.example" "$TARGET_DIR/" && echo "  ✅ config.json.example"

# 复制可选文件
if [ -f "$SOURCE_DIR/.dockerignore" ]; then
    cp "$SOURCE_DIR/.dockerignore" "$TARGET_DIR/" && echo "  ✅ .dockerignore"
fi
if [ -f "$SOURCE_DIR/start.sh" ]; then
    cp "$SOURCE_DIR/start.sh" "$TARGET_DIR/" && echo "  ✅ start.sh"
fi

# 复制parsers目录
echo "📋 复制parsers模块..."
cp "$SOURCE_DIR/parsers/__init__.py" "$TARGET_DIR/parsers/" && echo "  ✅ parsers/__init__.py"
cp "$SOURCE_DIR/parsers/z_param_parser.py" "$TARGET_DIR/parsers/" && echo "  ✅ parsers/z_param_parser.py"
cp "$SOURCE_DIR/parsers/decrypt_parser.py" "$TARGET_DIR/parsers/" && echo "  ✅ parsers/decrypt_parser.py"
cp "$SOURCE_DIR/parsers/search_parser.py" "$TARGET_DIR/parsers/" && echo "  ✅ parsers/search_parser.py"

# 复制utils目录
echo "📋 复制utils模块..."
cp "$SOURCE_DIR/utils/__init__.py" "$TARGET_DIR/utils/" && echo "  ✅ utils/__init__.py"
cp "$SOURCE_DIR/utils/logger.py" "$TARGET_DIR/utils/" && echo "  ✅ utils/logger.py"
cp "$SOURCE_DIR/utils/config_loader.py" "$TARGET_DIR/utils/" && echo "  ✅ utils/config_loader.py"
cp "$SOURCE_DIR/utils/z_param_manager.py" "$TARGET_DIR/utils/" && echo "  ✅ utils/z_param_manager.py"

# 创建配置文件
echo "📋 准备配置文件..."
if [ ! -f "$TARGET_DIR/data/config.json" ]; then
    cp "$SOURCE_DIR/config.json.example" "$TARGET_DIR/data/config.json"
    echo "  ✅ 已创建 data/config.json（请编辑配置）"
else
    echo "  ℹ️  data/config.json 已存在，跳过"
fi

# 创建README
cat > "$TARGET_DIR/README.md" << 'EOF'
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
EOF

echo ""
echo "============================================================"
echo "✅ 部署项目创建完成！"
echo "============================================================"
echo ""
echo "📁 项目目录: $TARGET_DIR"
echo ""
echo "📋 文件清单:"
find "$TARGET_DIR" -type f -not -path "*/data/*" | sort | sed 's|^|  |'
echo ""
echo "📝 下一步:"
echo "  1. cd $TARGET_DIR"
echo "  2. 编辑 data/config.json 配置API站点"
echo "  3. docker-compose build"
echo "  4. docker-compose up -d"
echo ""

