# 视频解析API服务

基于NAS部署的视频解析服务，支持视频URL解析和资源检索功能。

## ✨ 功能特性

- ✅ **视频解析**：支持多种视频平台（爱奇艺、腾讯视频、优酷、B站等）
- ✅ **资源检索**：关键词搜索，自动解析多个视频平台的资源
- ✅ **智能降级**：z参数方案失败时自动切换到解密方案
- ✅ **自动更新**：z参数过期时自动更新
- ✅ **Docker部署**：一键部署，支持群晖NAS

## 🚀 快速开始

### 1. 准备配置文件

```bash
cp config.json.example data/config.json
# 编辑 data/config.json，配置API站点
```

### 2. 启动服务

使用Docker Compose（推荐）：
```bash
docker-compose up -d
```

或使用快速启动脚本：
```bash
chmod +x start.sh
./start.sh
```

### 3. 验证服务

```bash
curl http://localhost:1233/health
```

## 📖 API文档

启动服务后，访问以下地址查看API文档：
- Swagger UI: http://localhost:1233/docs
- ReDoc: http://localhost:1233/redoc

### API接口

#### 1. 视频解析接口

```bash
GET /api/v1/parse?url={video_url}&parser_url={parser_url}

参数：
- url: 要解析的视频URL（必填）
- parser_url: 解析网站URL（可选，默认https://jx.789jiexi.com）

示例：
GET /api/v1/parse?url=https://www.iqiyi.com/v_xxx.html&parser_url=https://jx.789jiexi.com
```

响应：
```json
{
  "success": true,
  "data": {
    "m3u8_url": "https://example.com/video.m3u8",
    "method": "z_param",
    "parse_time": 3.2
  },
  "fallback_used": false
}
```

#### 2. 资源检索接口

```bash
GET /api/v1/search?ac=videolist&wd={keyword}&page={page}

参数：
- ac: 固定值 "videolist"（必填）
- wd: 搜索关键词（必填）
- page: 页码（可选，默认1）

示例：
GET /api/v1/search?ac=videolist&wd=新僵尸先生&page=1
```

响应：
```json
{
  "code": 1,
  "msg": "数据列表",
  "page": 1,
  "pagecount": 1,
  "limit": 20,
  "total": 2,
  "list": [
    {
      "vod_name": "新僵尸先生",
      "vod_play_url": "正片${m3u8_url}",
      ...
    }
  ]
}
```

#### 3. 健康检查接口

```bash
GET /health
```

响应：
```json
{
  "status": "healthy",
  "z_param_status": "valid",
  "z_param_age": 3600,
  "uptime": 86400
}
```

## 📁 项目结构

```
video-parser-analysis/
├── api_server.py          # FastAPI主服务
├── Dockerfile             # Docker镜像构建文件
├── docker-compose.yml     # Docker Compose配置
├── requirements.txt       # Python依赖
├── config.json.example    # 配置文件示例
├── start.sh              # 快速启动脚本
├── parsers/              # 解析器模块
│   ├── z_param_parser.py  # z参数解析器
│   ├── decrypt_parser.py  # 解密解析器（备选）
│   └── search_parser.py  # 资源检索解析器
├── utils/                 # 工具模块
│   ├── logger.py         # 日志工具
│   ├── config_loader.py  # 配置加载器
│   └── z_param_manager.py # z参数管理器
└── data/                  # 数据目录（挂载）
    ├── config.json       # 配置文件
    ├── z_params.json     # z参数文件
    └── logs/             # 日志目录
```

## 🔧 配置说明

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

- **cache_time**: 缓存时间（秒）
- **api_site**: API站点配置列表

## 📝 部署文档

详细部署说明请参考：[DEPLOYMENT.md](DEPLOYMENT.md)

## 🐛 故障排除

### 1. 服务无法启动
- 检查Docker是否运行
- 查看日志：`docker-compose logs`
- 检查端口1233是否被占用

### 2. z参数过期
- z参数会自动更新
- 如果更新失败，检查网络连接
- 查看日志文件：`data/logs/api_server.log`

### 3. 解析失败
- 检查视频URL是否正确
- 查看日志了解详细错误
- 尝试使用不同的解析网站URL

## 📄 许可证

本项目仅供学习交流使用。

## 🙏 致谢

- FastAPI - 现代、快速的Web框架
- Playwright - 浏览器自动化工具
- 所有贡献者
