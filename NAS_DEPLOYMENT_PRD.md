# NAS视频解析服务 - 产品需求文档（PRD）

## 📋 文档信息
- **文档版本**：v1.0
- **创建时间**：2024-12-08
- **最后更新**：2024-12-08
- **文档作者**：AI Product Manager
- **审核状态**：待审核

---

## 1. 背景与目标

### 1.1 业务背景
当前视频解析服务部署在GitHub Actions上，虽然免费但存在以下问题：
- 需要GitHub账号和Token管理
- 每次调用需要触发workflow，响应时间较长（30-60秒）
- 无法直接通过API调用，需要GitHub API集成
- 迭代和调试不够灵活

用户希望将服务部署在NAS上，实现：
- 本地化部署，更好的控制权
- 快速API响应（秒级）
- 便于迭代和调试
- 降低外部依赖

### 1.2 用户痛点
- **响应速度慢**：GitHub Actions每次调用需要30-60秒
- **集成复杂**：需要通过GitHub API触发workflow
- **参数管理**：z参数过期时需要手动更新，不够自动化
- **备选方案缺失**：当z参数方式失败时，没有自动降级方案

### 1.3 业务目标
- **主要目标**：在NAS上部署视频解析API服务，提供快速、可靠的视频解析能力
- **成功指标**：
  - API响应时间 ≤ 5秒（z参数未过期时）
  - API响应时间 ≤ 30秒（z参数过期，需要模拟获取时）
  - 服务可用性 ≥ 95%
  - z参数自动更新成功率 ≥ 90%
  - 备选方案触发率 ≤ 10%（说明主要方案稳定）

### 1.4 项目范围
- **包含范围**：
  - NAS Docker容器化部署（群晖系统）
  - RESTful API接口设计（解析接口 + 资源检索接口）
  - z参数智能管理（过期检测、自动更新）
  - 备选方案集成（final_direct_parser_v2.py）
  - 资源检索和批量解析功能
  - 配置文件管理（config.json）
  - 定期任务（z参数更新）
  - 健康检查和监控
- **不包含范围**：
  - Web UI界面（后续迭代）
  - 用户认证和权限管理（后续迭代）
  - 多实例负载均衡（后续迭代）
  - 数据库存储（当前使用文件存储）

---

## 2. 用户与场景

### 2.1 目标用户
- **主要用户**：开发者、技术爱好者
- **用户特征**：
  - 拥有NAS设备（群晖、威联通等）
  - 熟悉Docker部署
  - 需要视频解析API服务
  - 希望本地化部署，降低外部依赖

### 2.2 使用场景

**场景1：快速解析视频（z参数有效）**
- **用户**：开发者
- **时间**：任意时间
- **地点**：本地网络
- **行为**：调用API接口解析视频URL
- **目标**：快速获取m3u8链接（≤5秒）

**场景2：z参数过期自动处理**
- **用户**：系统自动
- **时间**：z参数过期时
- **地点**：NAS服务器
- **行为**：检测到z参数过期，自动使用浏览器模拟获取新参数
- **目标**：自动恢复服务，无需人工干预

**场景3：主要方案失败降级**
- **用户**：系统自动
- **时间**：z参数方式解析失败时
- **地点**：NAS服务器
- **行为**：自动切换到final_direct_parser_v2.py解密方案
- **目标**：提高解析成功率，确保服务可用性

**场景4：定期更新z参数**
- **用户**：定时任务
- **时间**：每天凌晨2点（可配置）
- **地点**：NAS服务器
- **行为**：使用浏览器模拟获取最新z参数并保存
- **目标**：保持z参数有效性，减少过期情况

### 2.3 用户故事
- As a 开发者, I want 通过API调用解析视频, So that 我可以快速获取m3u8链接
- As a 系统管理员, I want z参数自动更新, So that 服务可以持续稳定运行
- As a 用户, I want 解析失败时自动降级, So that 提高解析成功率
- As a 开发者, I want 快速构建和部署, So that 我可以快速迭代和调试

---

## 3. 功能需求

### 3.1 功能概览
| 功能 | 优先级 | 说明 |
|------|--------|------|
| 视频解析API接口 | P0 | RESTful API，支持单个视频URL解析 |
| 资源检索API接口 | P0 | 支持关键词搜索，批量解析视频资源 |
| z参数管理 | P0 | 过期检测、自动更新、缓存 |
| 备选方案 | P0 | final_direct_parser_v2.py集成 |
| 配置文件管理 | P0 | config.json配置管理 |
| Docker部署 | P0 | 容器化部署，快速构建（群晖） |
| 定期任务 | P1 | z参数自动更新任务 |
| 健康检查 | P1 | 服务健康状态监控 |
| 日志记录 | P1 | 请求日志、错误日志 |

### 3.2 功能详细说明

#### 功能1：视频解析API接口
**优先级**：P0

**功能描述**：
提供RESTful API接口，接收视频URL，返回m3u8链接。

**API设计**：
```
POST /api/v1/parse
Content-Type: application/json

Request:
{
  "video_url": "https://www.iqiyi.com/v_1c168e2yzbk.html",
  "parser_url": "https://jx.789jiexi.com"  // 可选，默认值
}

Response (成功):
{
  "success": true,
  "data": {
    "m3u8_url": "https://example.com/video.m3u8",
    "method": "z_param",  // 或 "decrypt"
    "parse_time": 3.2  // 秒
  }
}

Response (失败):
{
  "success": false,
  "error": "解析失败：z参数已过期",
  "fallback_used": true  // 是否使用了备选方案
}
```

**交互流程**：
1. 客户端发送POST请求到 `/api/v1/parse`
2. 服务端验证请求参数
3. 检查z参数是否过期
4. 如果z参数有效，使用API方式解析（快速路径）
5. 如果z参数过期，先尝试模拟获取新参数，再解析
6. 如果z参数方式失败，自动切换到解密方案
7. 返回解析结果

**输入输出**：
- **输入**：视频URL（必填）、解析网站URL（可选）
- **输出**：m3u8链接、解析方法、耗时

**边界条件**：
- 视频URL格式错误：返回400错误
- z参数过期且模拟获取失败：切换到备选方案
- 所有方案都失败：返回500错误，包含详细错误信息
- 请求超时：返回504错误

**验收标准**：
- [ ] API接口可以正常接收请求
- [ ] z参数有效时，响应时间 ≤ 5秒
- [ ] z参数过期时，自动更新并解析成功
- [ ] 主要方案失败时，自动切换到备选方案
- [ ] 返回格式符合API规范

#### 功能1.5：资源检索解析API接口
**优先级**：P0

**功能描述**：
提供资源检索和批量解析功能，支持关键词搜索，自动解析多个视频平台的资源。

**API设计**：
```
POST /api/v1/search
Content-Type: application/json

Request:
{
  "keyword": "新僵尸先生",
  "page": 1  // 可选，默认1
}

Response (成功):
{
  "code": 1,
  "msg": "数据列表",
  "page": 1,
  "pagecount": 1,
  "limit": 20,
  "total": 2,
  "list": [
    {
      "vod_id": 24608,
      "vod_name": "新僵尸先生2",
      "vod_play_from": "qiyi",
      "vod_play_url": "正片${解析后的m3u8地址}",
      // ... 其他字段
    }
  ]
}

Response (全部解析失败):
{
  "code": 1,
  "msg": "数据列表",
  "page": 1,
  "pagecount": 0,
  "limit": 20,
  "total": 0,
  "list": []
}
```

**交互流程**：
1. 客户端发送POST请求到 `/api/v1/search`
2. 读取config.json配置文件，获取API站点列表
3. 并发调用所有配置的API站点：`{api_url}/?ac=videolist&wd={keyword}`
4. 合并所有API返回的数据：
   - 按`vod_name`去重（相同名称只保留一个）
   - 按`vod_play_url`中的平台去重（bilibili、qq、youku、iqiyi等）
   - 合并相同平台的资源
5. 解析合并后的视频地址：
   - 解析`vod_play_url`中的每个视频URL
   - 成功解析的替换为m3u8地址
   - 解析失败的删除该资源
6. 如果某个资源的`vod_play_url`全部解析失败，删除该资源
7. 返回最终结果

**数据去重逻辑**：
- **按名称去重**：`vod_name`相同的资源只保留一个
- **按平台去重**：`vod_play_url`格式为：`正片$url1$$$正片$url2$$$...`
  - 解析每个URL，识别平台（bilibili、qq、youku、iqiyi等）
  - 相同平台的URL只保留一个
  - 合并不同平台的URL

**解析逻辑**：
- 解析`vod_play_url`中的每个视频URL
- 使用功能1的解析接口解析每个URL
- 解析成功：替换为m3u8地址，格式：`正片${m3u8_url}`
- 解析失败：删除该URL
- 如果某个资源的所有URL都解析失败，删除该资源

**配置文件格式**（config.json）：
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

**输入输出**：
- **输入**：搜索关键词（必填）、页码（可选）
- **输出**：合并后的资源列表，包含解析后的m3u8地址

**边界条件**：
- 关键词为空：返回400错误
- 所有API站点都失败：返回空列表
- 所有资源都解析失败：返回空列表
- 配置文件不存在：返回500错误
- 请求超时：返回504错误（设置超时时间，如30秒）

**验收标准**：
- [ ] API接口可以正常接收请求
- [ ] 可以正确读取config.json配置文件
- [ ] 可以并发调用多个API站点
- [ ] 数据去重逻辑正确（按名称和平台）
- [ ] 可以正确解析视频URL并替换
- [ ] 解析失败的资源正确删除
- [ ] 返回格式符合API规范

#### 功能2：z参数智能管理
**优先级**：P0

**功能描述**：
智能管理z参数的生命周期，包括过期检测、自动更新、缓存管理。

**核心逻辑**：
1. **过期检测**：
   - 检查z参数文件是否存在
   - 检查z参数文件的时间戳（如果超过24小时，认为可能过期）
   - 尝试使用z参数解析测试视频，如果失败则认为过期

2. **自动更新**：
   - z参数过期时，使用Playwright模拟浏览器获取新参数
   - 保存新参数到文件（`z_params.json`）
   - 记录更新时间戳

3. **缓存管理**：
   - z参数存储在内存中（应用启动时加载）
   - 文件存储作为持久化备份
   - 支持手动刷新缓存

**交互流程**：
1. 应用启动时，加载z参数文件
2. 每次解析请求时，检查z参数是否过期
3. 如果过期，触发自动更新流程
4. 更新成功后，继续解析请求
5. 更新失败时，记录错误并尝试备选方案

**输入输出**：
- **输入**：无（自动检测）
- **输出**：z参数值、更新时间戳、有效期

**边界条件**：
- z参数文件不存在：触发首次获取
- 模拟浏览器失败：记录错误，使用备选方案
- 网络超时：重试3次，失败后使用备选方案

**验收标准**：
- [ ] z参数过期时自动检测
- [ ] 自动更新成功率 ≥ 90%
- [ ] z参数更新后可以正常使用
- [ ] 更新失败时有错误日志

#### 功能3：备选方案集成
**优先级**：P0

**功能描述**：
当z参数方式失败时，自动切换到final_direct_parser_v2.py解密方案。

**触发条件**：
1. z参数过期且无法更新
2. z参数方式解析失败（返回错误或超时）
3. API返回非预期结果

**集成方式**：
- 将final_direct_parser_v2.py作为独立模块导入
- 在主解析流程中，捕获异常并切换到备选方案
- 记录使用的解析方法（用于统计和调试）

**交互流程**：
1. 主要方案（z参数方式）失败
2. 捕获异常，记录错误日志
3. 切换到final_direct_parser_v2.py
4. 使用解密方案解析
5. 返回结果，标注使用的方案

**输入输出**：
- **输入**：视频URL、解析网站URL
- **输出**：m3u8链接（如果成功）

**边界条件**：
- 备选方案也失败：返回错误，包含两个方案的错误信息
- 备选方案超时：返回超时错误

**验收标准**：
- [ ] 主要方案失败时自动切换
- [ ] 备选方案可以正常解析
- [ ] 返回结果中包含使用的方案信息
- [ ] 切换时有日志记录

#### 功能4：Docker容器化部署
**优先级**：P0

**功能描述**：
使用Docker容器化部署，支持快速构建和迭代。

**镜像选择**：
- **基础镜像**：`python:3.11-slim`（轻量级，构建快）
- **备选镜像**：`python:3.11-alpine`（更小，但可能兼容性问题）
- **不推荐**：`python:3.11`（体积大，构建慢）

**Dockerfile设计**：
```dockerfile
FROM python:3.11-slim

# 安装系统依赖（Playwright需要）
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# 安装Playwright（用于z参数获取）
RUN pip install playwright && \
    playwright install chromium && \
    playwright install-deps chromium

# 复制代码
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# 创建data目录
RUN mkdir -p /app/data

# 暴露端口（内部端口8000，外部映射到1233）
EXPOSE 8000

# 启动命令
CMD ["python", "api_server.py"]
```

**Docker Compose配置**（推荐群晖使用）：
```yaml
version: '3.8'

services:
  video-parser:
    build: .
    container_name: video-parser
    ports:
      - "1233:8000"
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    environment:
      - TZ=Asia/Shanghai
```

**构建优化**：
- 使用多阶段构建（如果依赖复杂）
- 利用Docker缓存层
- 最小化镜像体积

**交互流程**：
1. 编写Dockerfile
2. 构建镜像：`docker build -t video-parser:latest .`
3. 运行容器：`docker run -d -p 8000:8000 video-parser:latest`
4. 验证服务：`curl http://localhost:8000/health`

**输入输出**：
- **输入**：源代码、requirements.txt
- **输出**：Docker镜像

**边界条件**：
- 构建失败：检查依赖和Dockerfile语法
- 容器启动失败：检查端口冲突和资源限制
- Playwright安装失败：检查系统依赖

**验收标准**：
- [ ] Docker镜像可以成功构建（≤5分钟）
- [ ] 容器可以正常启动
- [ ] API接口可以正常访问
- [ ] Playwright可以正常运行

#### 功能5：定期更新z参数
**优先级**：P1

**功能描述**：
使用定时任务定期更新z参数，保持参数有效性。

**实现方式**：
- 使用APScheduler或schedule库
- 每天凌晨2点执行（可配置）
- 使用Playwright模拟浏览器获取新参数

**定时任务设计**：
```python
from apscheduler.schedulers.background import BackgroundScheduler

def update_z_param():
    """更新z参数"""
    try:
        # 使用Playwright获取新参数
        new_z_param = get_z_param_with_playwright()
        # 保存到文件
        save_z_param(new_z_param)
        logger.info("z参数更新成功")
    except Exception as e:
        logger.error(f"z参数更新失败: {e}")

# 每天凌晨2点执行
scheduler = BackgroundScheduler()
scheduler.add_job(update_z_param, 'cron', hour=2, minute=0)
scheduler.start()
```

**交互流程**：
1. 应用启动时，初始化定时任务
2. 每天凌晨2点，触发更新任务
3. 使用Playwright获取新z参数
4. 保存新参数，更新缓存
5. 记录更新结果（成功/失败）

**输入输出**：
- **输入**：无（定时触发）
- **输出**：更新结果日志

**边界条件**：
- 更新失败：记录错误，不影响服务运行
- 更新超时：设置超时时间（5分钟），超时后放弃

**验收标准**：
- [ ] 定时任务可以正常执行
- [ ] z参数可以成功更新
- [ ] 更新失败时有错误日志
- [ ] 更新后参数可以正常使用

#### 功能6：健康检查和监控
**优先级**：P1

**功能描述**：
提供健康检查接口和基础监控功能。

**健康检查接口**：
```
GET /health

Response:
{
  "status": "healthy",
  "z_param_status": "valid",  // valid/expired/unknown
  "z_param_age": 3600,  // 秒
  "uptime": 86400  // 秒
}
```

**监控指标**：
- 服务运行时间
- z参数状态和年龄
- 最近解析成功率
- 平均响应时间

**交互流程**：
1. 客户端请求 `/health`
2. 检查服务状态
3. 检查z参数状态
4. 返回健康状态

**输入输出**：
- **输入**：无
- **输出**：健康状态JSON

**边界条件**：
- 服务异常：返回unhealthy状态
- z参数过期：返回warning状态

**验收标准**：
- [ ] 健康检查接口可以正常访问
- [ ] 返回的状态信息准确
- [ ] 可以用于容器健康检查

---

## 4. 非功能需求

### 4.1 性能要求
- **API响应时间**：
  - z参数有效时：≤ 5秒
  - z参数过期时：≤ 30秒（包含更新时间）
  - 备选方案：≤ 15秒
- **并发处理**：支持至少10个并发请求
- **资源占用**：
  - 内存：≤ 512MB（不含Playwright）
  - CPU：正常情况 ≤ 20%
- **构建时间**：Docker镜像构建 ≤ 5分钟

### 4.2 安全要求
- API接口不需要认证（内网使用）
- 输入验证：验证URL格式，防止注入攻击
- 错误信息：不暴露敏感信息（如内部错误详情）
- 日志安全：不记录敏感信息（如完整URL）

### 4.3 兼容性要求
- **NAS系统**：支持群晖、威联通等主流NAS系统
- **Docker版本**：Docker 20.10+
- **Python版本**：Python 3.11+
- **浏览器**：Playwright Chromium（headless模式）

### 4.4 可维护性要求
- **代码规范**：遵循PEP 8
- **日志格式**：结构化日志（JSON格式）
- **错误处理**：完善的异常处理和错误提示
- **文档**：API文档、部署文档、故障排除文档

---

## 5. 技术方案

### 5.1 技术选型

**后端框架**：
- **FastAPI**（推荐）：高性能、自动API文档、类型提示
- **Flask**（备选）：轻量级、简单易用

**浏览器自动化**：
- **Playwright**（推荐）：比Selenium更快、更稳定
- **Selenium**（备选）：兼容性好但较慢

**定时任务**：
- **APScheduler**（推荐）：功能强大、易于配置
- **schedule**（备选）：简单但功能有限

**容器化**：
- **Docker**：标准容器化方案

### 5.2 架构设计

```
┌─────────────────┐
│   API Client    │
└────────┬────────┘
         │ HTTP POST /api/v1/parse
         ▼
┌─────────────────────────────────┐
│      FastAPI Server              │
│  ┌───────────────────────────┐  │
│  │   Parse Endpoint          │  │
│  └───────────┬───────────────┘  │
│              │                   │
│  ┌───────────▼───────────────┐  │
│  │   Z Param Manager         │  │
│  │   - Check expiration      │  │
│  │   - Auto update           │  │
│  │   - Cache management      │  │
│  └───────────┬───────────────┘  │
│              │                   │
│  ┌───────────▼───────────────┐  │
│  │   Parser Strategy         │  │
│  │   ├─ Z Param Parser       │  │
│  │   └─ Decrypt Parser       │  │
│  │      (fallback)            │  │
│  └───────────────────────────┘  │
│                                  │
│  ┌───────────────────────────┐  │
│  │   Scheduler                │  │
│  │   - Daily z param update   │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  File Storage   │
│  - z_params.json │
│  - logs/         │
└─────────────────┘
```

### 5.3 数据模型

**z_params.json**（存储在/data目录）：
```json
{
  "z_param": "b413af76b43b1a0abc231718862417e2",
  "s1ig_param": "11397",
  "g_param": "",
  "updated_at": "2024-12-08T10:00:00Z",
  "expires_in": 86400,
  "source": "playwright"
}
```

**config.json**（存储在/data目录）：
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

### 5.4 API接口设计

**解析接口**：
```
POST /api/v1/parse
Content-Type: application/json

Request Body:
{
  "video_url": "string (required)",
  "parser_url": "string (optional, default: https://jx.789jiexi.com)"
}

Response:
{
  "success": boolean,
  "data": {
    "m3u8_url": "string",
    "method": "z_param" | "decrypt",
    "parse_time": number
  },
  "error": "string (if success is false)"
}
```

**资源检索接口**：
```
POST /api/v1/search
Content-Type: application/json

Request Body:
{
  "keyword": "string (required)",
  "page": number (optional, default: 1)
}

Response:
{
  "code": 1,
  "msg": "数据列表",
  "page": number,
  "pagecount": number,
  "limit": 20,
  "total": number,
  "list": [
    {
      "vod_id": number,
      "vod_name": "string",
      "vod_play_from": "string",
      "vod_play_url": "正片${m3u8_url}",
      // ... 其他字段
    }
  ]
}
```

**健康检查接口**：
```
GET /health

Response:
{
  "status": "healthy" | "unhealthy" | "degraded",
  "z_param_status": "valid" | "expired" | "unknown",
  "z_param_age": number,
  "uptime": number
}
```

---

## 6. 风险评估

### 6.1 技术风险

**风险1：Playwright在NAS上运行不稳定**
- **影响**：高（z参数更新失败）
- **应对**：
  - 使用headless模式
  - 设置合理的超时时间
  - 提供备选方案（HTTP提取）
  - 增加重试机制

**风险2：z参数更新失败**
- **影响**：中（服务降级到备选方案）
- **应对**：
  - 定期更新任务
  - 失败时使用备选方案
  - 记录详细错误日志
  - 支持手动触发更新

**风险3：Docker镜像构建慢**
- **影响**：低（影响开发体验）
- **应对**：
  - 使用slim镜像
  - 优化Dockerfile
  - 利用Docker缓存
  - 考虑多阶段构建

### 6.2 业务风险

**风险1：解析成功率下降**
- **影响**：高（影响用户体验）
- **应对**：
  - 实现备选方案
  - 监控解析成功率
  - 及时更新z参数
  - 记录失败原因

**风险2：NAS资源占用过高**
- **影响**：中（影响NAS性能）
- **应对**：
  - 限制并发数
  - 优化资源使用
  - 监控资源占用
  - 支持资源限制配置

---

## 7. 迭代计划

### 7.1 MVP范围（V1.0）

**核心功能**：
- ✅ API接口（POST /api/v1/parse）
- ✅ z参数管理（过期检测、自动更新）
- ✅ 备选方案集成（final_direct_parser_v2.py）
- ✅ Docker部署
- ✅ 健康检查接口

**不包含**：
- 定期更新任务（手动触发）
- 详细监控（基础健康检查）
- Web UI（后续迭代）

### 7.2 后续迭代

**V1.1 - 自动化增强**：
- 定期更新z参数任务
- 失败重试机制
- 更详细的日志

**V1.2 - 监控和运维**：
- Prometheus指标导出
- Grafana仪表板
- 告警通知

**V1.3 - 功能增强**：
- 批量解析接口
- 解析历史记录
- 缓存机制

---

## 8. 实施计划

### 8.1 开发阶段

**阶段1：核心API开发（3天）**
- 搭建FastAPI项目结构
- 实现解析接口
- 集成z参数管理
- 集成备选方案

**阶段2：Docker化（1天）**
- 编写Dockerfile
- 优化镜像构建
- 测试容器部署

**阶段3：定时任务（1天）**
- 集成APScheduler
- 实现z参数更新任务
- 测试定时执行

**阶段4：测试和优化（2天）**
- 功能测试
- 性能测试
- 错误处理测试
- 文档编写

### 8.2 部署阶段

**步骤1：准备NAS环境（群晖）**
- 确保Docker已安装（群晖套件中心）
- 创建存储目录：`/volume1/docker/video-parser/data`
- 准备配置文件：将`config.json.example`复制为`config.json`并配置

**步骤2：构建和部署**
- 构建Docker镜像：`docker build -t video-parser:latest .`
- 运行容器：
```bash
docker run -d \
  --name video-parser \
  -p 1233:8000 \
  -v /volume1/docker/video-parser/data:/app/data \
  video-parser:latest
```
- 验证服务：`curl http://localhost:1233/health`

**步骤3：监控和维护**
- 配置健康检查
- 设置日志收集
- 定期检查服务状态

---

## 9. 验收标准

### 9.1 功能验收

- [ ] API接口可以正常接收和响应请求
- [ ] z参数过期时可以自动检测和更新
- [ ] 主要方案失败时可以自动切换到备选方案
- [ ] Docker容器可以正常构建和运行
- [ ] 定时任务可以正常执行
- [ ] 健康检查接口返回准确状态

### 9.2 性能验收

- [ ] z参数有效时，API响应时间 ≤ 5秒
- [ ] z参数过期时，API响应时间 ≤ 30秒
- [ ] 支持至少10个并发请求
- [ ] Docker镜像构建时间 ≤ 5分钟

### 9.3 可靠性验收

- [ ] 服务可用性 ≥ 95%
- [ ] z参数自动更新成功率 ≥ 90%
- [ ] 备选方案触发率 ≤ 10%
- [ ] 错误处理完善，不会导致服务崩溃

---

## 10. 附录

### 10.1 参考资料

- [FastAPI文档](https://fastapi.tiangolo.com/)
- [Playwright文档](https://playwright.dev/python/)
- [Docker最佳实践](https://docs.docker.com/develop/dev-best-practices/)
- [APScheduler文档](https://apscheduler.readthedocs.io/)

### 10.2 相关文件

- `final_direct_parser_v2.py` - 备选解析方案
- `z_param_api_service.py` - z参数获取服务
- `capture_api_params.py` - z参数捕获脚本
- `direct_videocdn_parser_simple.py` - z参数解析方案

### 10.3 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0 | 2024-12-08 | 初始版本 | AI Product Manager |

---

## 📌 关键决策点

1. **镜像选择**：使用`python:3.11-slim`而非`python:3.11`，平衡构建速度和兼容性
2. **框架选择**：使用FastAPI而非Flask，获得更好的性能和自动文档
3. **浏览器自动化**：使用Playwright而非Selenium，获得更好的性能和稳定性
4. **备选方案**：集成final_direct_parser_v2.py作为降级方案，提高成功率
5. **参数更新策略**：过期时立即更新，而非定期更新，减少失败率

---

**文档状态**：✅ 已完成  
**下一步行动**：开始开发实施


