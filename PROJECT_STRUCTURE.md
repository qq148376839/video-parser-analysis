# 项目结构说明

## 📁 目录结构

```
video-parser-analysis/
├── api_server.py              # FastAPI主服务文件（待创建）
├── config.json.example        # 配置文件示例
├── config.json                # 实际配置文件（需要手动创建）
├── requirements.txt           # Python依赖
├── Dockerfile                 # Docker镜像构建文件（待创建）
├── docker-compose.yml         # Docker Compose配置（待创建）
├── NAS_DEPLOYMENT_PRD.md     # NAS部署产品需求文档
├── README.md                  # 项目说明文档
│
├── data/                      # 数据目录（挂载到容器）
│   ├── config.json           # 配置文件（从项目根目录复制）
│   ├── z_params.json         # z参数存储文件
│   └── logs/                 # 日志目录
│
├── parsers/                   # 解析器模块
│   ├── __init__.py
│   ├── z_param_parser.py     # z参数解析器（待创建）
│   ├── decrypt_parser.py     # 解密解析器（final_direct_parser_v2.py）
│   └── search_parser.py      # 资源检索解析器（待创建）
│
├── utils/                     # 工具模块
│   ├── __init__.py
│   ├── z_param_manager.py    # z参数管理器（待创建）
│   ├── config_loader.py      # 配置加载器（待创建）
│   └── logger.py             # 日志工具（待创建）
│
├── jx2s0_analysis/            # jx2s0解析器分析（保留）
│   └── ...
│
└── archive/                   # 归档目录（与NAS部署无关的文件）
    ├── GitHub Actions相关文件
    ├── Cloudflare Workers相关文件
    ├── 分析和捕获脚本
    └── 输出文件（JSON、HTML、M3U8等）
```

## 📝 文件说明

### 核心文件

- **api_server.py**: FastAPI主服务，提供API接口
- **config.json.example**: 配置文件模板，包含API站点配置
- **config.json**: 实际配置文件（需要从example复制并修改）
- **Dockerfile**: Docker镜像构建文件
- **docker-compose.yml**: Docker Compose配置（群晖推荐使用）

### 数据目录（/data）

- **config.json**: 配置文件，包含API站点列表
- **z_params.json**: z参数存储文件，自动生成
- **logs/**: 日志目录，自动生成

### 解析器模块

- **z_param_parser.py**: z参数方式解析器
- **decrypt_parser.py**: 解密方式解析器（备选方案）
- **search_parser.py**: 资源检索和批量解析器

### 工具模块

- **z_param_manager.py**: z参数管理器，负责过期检测和自动更新
- **config_loader.py**: 配置加载器，读取config.json
- **logger.py**: 日志工具，统一日志格式

## 🔧 配置文件说明

### config.json

```json
{
  "cache_time": 7200,
  "api_site": {
    "站点名称": {
      "api": "API地址",
      "name": "显示名称",
      "official_parser": true
    }
  }
}
```

- **cache_time**: 缓存时间（秒），默认7200秒（2小时）
- **api_site**: API站点配置
  - **api**: API基础地址
  - **name**: 站点显示名称
  - **official_parser**: 是否使用官方解析器

## 🚀 部署说明

### 群晖NAS部署

1. **准备目录**：
   ```bash
   mkdir -p /volume1/docker/video-parser/data
   ```

2. **复制配置文件**：
   ```bash
   cp config.json.example /volume1/docker/video-parser/data/config.json
   # 编辑config.json，配置API站点
   ```

3. **构建镜像**：
   ```bash
   docker build -t video-parser:latest .
   ```

4. **运行容器**：
   ```bash
   docker run -d \
     --name video-parser \
     -p 1233:8000 \
     -v /volume1/docker/video-parser/data:/app/data \
     video-parser:latest
   ```

   或使用Docker Compose：
   ```bash
   docker-compose up -d
   ```

5. **验证服务**：
   ```bash
   curl http://localhost:1233/health
   ```

## 📊 API接口

### 1. 视频解析接口

```
POST /api/v1/parse
Content-Type: application/json

{
  "video_url": "https://www.iqiyi.com/v_xxx.html",
  "parser_url": "https://jx.789jiexi.com"  // 可选
}
```

### 2. 资源检索接口

```
POST /api/v1/search
Content-Type: application/json

{
  "keyword": "新僵尸先生",
  "page": 1  // 可选
}
```

### 3. 健康检查接口

```
GET /health
```

## 📌 注意事项

1. **配置文件位置**：config.json需要放在/data目录，容器启动时会自动加载
2. **数据持久化**：/data目录需要挂载到宿主机，确保数据不丢失
3. **端口映射**：内部端口8000，外部端口1233
4. **日志位置**：日志文件存储在/data/logs目录
5. **z参数更新**：z参数自动更新，存储在/data/z_params.json

## 🔄 更新说明

- 修改config.json后，需要重启容器才能生效
- z参数会自动更新，无需手动干预
- 日志文件会自动轮转，避免占用过多空间
