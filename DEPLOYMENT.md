# NAS部署指南

## 📋 前置准备

### 1. 群晖NAS环境要求
- Docker已安装（套件中心安装）
- 至少512MB可用内存
- 至少1GB可用磁盘空间

### 2. 准备配置文件

复制配置文件模板：
```bash
cp config.json.example data/config.json
```

编辑 `data/config.json`，配置API站点：
```json
{
  "cache_time": 7200,
  "api_site": {
    "789caiji": {
      "api": "https://www.caiji.cyou/api.php/provide/vod",
      "name": "789采集",
      "official_parser": true
    },
    "金蝉": {
      "api": "https://zy.jinchancaiji.com/api.php/provide/vod",
      "name": "金蝉采集",
      "official_parser": true
    },
    "山海": {
      "api": "https://zy.sh0o.cn/api.php/provide/vod",
      "name": "山海采集",
      "official_parser": true
    }
  }
}
```

## 🚀 部署步骤

### 方式1：使用Docker Compose（推荐）

1. **上传项目文件到NAS**
   - 将整个项目目录上传到NAS（例如：`/volume1/docker/video-parser`）

2. **准备配置文件**
   ```bash
   cd /volume1/docker/video-parser
   cp config.json.example data/config.json
   # 编辑 data/config.json
   ```

3. **构建和启动**
   ```bash
   docker-compose up -d
   ```

4. **查看日志**
   ```bash
   docker-compose logs -f
   ```

5. **停止服务**
   ```bash
   docker-compose down
   ```

### 方式2：使用Docker命令

1. **构建镜像**
   ```bash
   docker build -t video-parser:latest .
   ```

2. **运行容器**
   ```bash
   docker run -d \
     --name video-parser \
     -p 1233:8000 \
     -v /volume1/docker/video-parser/data:/app/data \
     --restart unless-stopped \
     video-parser:latest
   ```

3. **查看日志**
   ```bash
   docker logs -f video-parser
   ```

4. **停止服务**
   ```bash
   docker stop video-parser
   docker rm video-parser
   ```

## ✅ 验证部署

### 1. 健康检查
```bash
curl http://localhost:1233/health
```

预期响应：
```json
{
  "status": "healthy",
  "z_param_status": "valid",
  "z_param_age": 3600,
  "uptime": 86400
}
```

### 2. 测试解析接口
```bash
curl -X POST http://localhost:1233/api/v1/parse \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.iqiyi.com/v_xxx.html"
  }'
```

### 3. 测试搜索接口
```bash
curl -X POST http://localhost:1233/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "新僵尸先生"
  }'
```

## 📁 目录结构

部署后的目录结构：
```
/volume1/docker/video-parser/
├── api_server.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── config.json.example
├── data/
│   ├── config.json          # 配置文件（需要手动创建）
│   ├── z_params.json        # z参数文件（自动生成）
│   └── logs/
│       └── api_server.log   # 日志文件
├── parsers/
├── utils/
└── ...
```

## 🔧 配置说明

### config.json配置

- **cache_time**: 缓存时间（秒），默认7200（2小时）
- **api_site**: API站点配置
  - **api**: API基础地址
  - **name**: 站点显示名称
  - **official_parser**: 是否使用官方解析器

### 环境变量

可以通过环境变量配置：
- `TZ`: 时区（默认：Asia/Shanghai）

## 📊 监控和维护

### 查看日志
```bash
# Docker Compose方式
docker-compose logs -f

# Docker命令方式
docker logs -f video-parser

# 查看日志文件
tail -f data/logs/api_server.log
```

### 重启服务
```bash
# Docker Compose方式
docker-compose restart

# Docker命令方式
docker restart video-parser
```

### 更新服务
```bash
# 1. 停止服务
docker-compose down

# 2. 重新构建镜像
docker-compose build

# 3. 启动服务
docker-compose up -d
```

## ⚠️ 常见问题

### 1. 端口被占用
如果1233端口被占用，修改 `docker-compose.yml` 中的端口映射：
```yaml
ports:
  - "其他端口:8000"
```

### 2. z参数过期
z参数会自动更新，如果更新失败：
- 检查网络连接
- 查看日志文件
- 手动触发更新（需要实现管理接口）

### 3. 配置文件不存在
确保 `data/config.json` 存在，可以从 `config.json.example` 复制。

### 4. Playwright安装失败
如果Playwright安装失败，检查：
- 系统依赖是否完整
- 网络连接是否正常
- Docker镜像是否正确构建

## 📝 API文档

启动服务后，访问以下地址查看自动生成的API文档：
- Swagger UI: http://localhost:1233/docs
- ReDoc: http://localhost:1233/redoc

## 🔄 更新说明

### 更新代码
1. 停止服务
2. 更新代码文件
3. 重新构建镜像
4. 启动服务

### 更新配置
1. 修改 `data/config.json`
2. 重启服务：`docker-compose restart`

### 更新z参数
z参数会自动更新，也可以手动删除 `data/z_params.json` 文件，服务启动时会自动获取。

