# 视频解析网站技术分析文档

## 📋 项目概述

本项目用于分析视频解析网站（如 `jx.789jiexi.com`、`videocdn.ihelpy.net`）如何从原始视频URL（如爱奇艺、腾讯视频等）解析出 `.m3u8` 播放文件的原理和技术实现。

## 🎯 已实现的解析器

### ✅ videocdn.ihelpy.net 解析器

**状态**: ✅ 已完成并测试通过

**文档**: [VIDEOCDN_IHELPY_PARSER.md](VIDEOCDN_IHELPY_PARSER.md)

**快速开始**:
```bash
python direct_videocdn_parser_simple.py
```

**特性**:
- 无需浏览器自动化
- 直接HTTP请求
- 自动解压响应
- 提取多个m3u8链接

### 🔄 jx.789jiexi.com 解析器

**状态**: 🔄 开发中

**文档**: [DECRYPT_SOLUTION.md](DECRYPT_SOLUTION.md)

---

## 🎯 分析目标

**核心问题**：视频解析网站是如何获取 `.m3u8` 文件的？

**分析维度**：
1. 网络请求流程
2. API调用链
3. 数据提取方法
4. 技术实现原理

---

## 🔍 分析方法

### 方法1：浏览器开发者工具分析（推荐）

**步骤**：

1. **打开浏览器开发者工具**
   - 按 `F12` 或右键 -> 检查
   - 切换到 `Network`（网络）标签

2. **访问解析网站**
   ```
   https://jx.789jiexi.com/?url=https://www.iqiyi.com/v_237eaj98iv0.html
   ```

3. **观察网络请求**
   - 清空现有请求（点击 🚫 图标）
   - 刷新页面（F5）
   - 观察所有网络请求

4. **重点关注**：
   - **XHR/Fetch 请求**：通常是API调用，用于获取视频信息
   - **Media 请求**：`.m3u8` 文件请求
   - **Document 请求**：页面HTML
   - **Script 请求**：JavaScript文件

5. **分析关键请求**：
   - 点击某个请求，查看：
     - **Headers**：请求头、请求参数
     - **Preview/Response**：响应内容
     - **Timing**：请求时间线

6. **查找m3u8链接**：
   - 在Network标签中搜索 `.m3u8`
   - 查看响应内容，找到m3u8 URL
   - 记录完整的请求流程

### 方法2：使用Python脚本自动化分析

#### 2.1 基础分析脚本

```bash
# 安装依赖
pip install requests

# 运行分析
python analyze_video_parser.py
```

**功能**：
- 获取解析页面HTML
- 从HTML中提取可能的m3u8链接
- 提取API调用
- 保存分析结果

#### 2.2 浏览器自动化分析（推荐）

```bash
# 安装Playwright（推荐）
pip install playwright
playwright install

# 或安装Selenium
pip install selenium

# 运行自动化分析
python browser_automation.py
```

**功能**：
- 自动打开浏览器
- 监听所有网络请求
- 自动提取m3u8链接
- 保存网络请求日志

---

## 🔬 技术原理分析

### 视频解析网站的工作原理

#### 1. 基本流程

```
用户输入原始视频URL
    ↓
解析网站接收URL参数
    ↓
后端API调用（可能有多个步骤）
    ↓
获取视频真实播放地址（m3u8/mp4等）
    ↓
返回给前端播放器
    ↓
前端播放器加载m3u8文件
```

#### 2. 常见实现方式

**方式A：直接API调用**
```
前端 -> 解析网站API -> 视频平台API -> 返回m3u8
```

**方式B：服务器代理**
```
前端 -> 解析网站后端 -> 代理请求视频平台 -> 解析响应 -> 返回m3u8
```

**方式C：JavaScript解析**
```
前端加载页面 -> 执行JS代码 -> 调用解析API -> 获取m3u8 -> 注入播放器
```

#### 3. 关键技术点

**3.1 URL参数传递**
- 大多数解析网站使用 `?url=` 参数传递原始视频URL
- 示例：`https://jx.789jiexi.com/?url=https://www.iqiyi.com/v_xxx.html`

**3.2 API调用**
- 解析网站通常有自己的后端API
- API可能调用第三方解析服务
- 常见端点：`/api/parse`, `/api/get`, `/parse.php` 等

**3.3 数据提取**
- 从视频平台页面提取播放信息
- 可能需要解析HTML、执行JavaScript
- 可能需要处理加密/混淆的代码

**3.4 m3u8文件获取**
- m3u8文件可能直接返回
- 也可能需要二次请求（先获取播放列表URL，再请求m3u8）

---

## 📊 分析结果示例

### 典型的请求流程

```
1. GET /?url=https://www.iqiyi.com/v_xxx.html
   ↓
2. 页面加载，执行JavaScript
   ↓
3. POST/GET /api/parse
   Request: { url: "https://www.iqiyi.com/v_xxx.html" }
   ↓
4. Response: { 
     success: true,
     url: "https://cdn.example.com/video.m3u8",
     ...
   }
   ↓
5. GET https://cdn.example.com/video.m3u8
   ↓
6. 播放器加载m3u8文件，开始播放
```

### m3u8文件格式

```m3u8
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXTINF:9.009,
segment1.ts
#EXTINF:9.009,
segment2.ts
...
```

---

## 🛠️ 实现自己的解析服务

### 方案1：调用现有解析API

```python
import requests

def parse_video(video_url: str):
    """调用解析API"""
    api_url = "https://jx.789jiexi.com/api/parse"
    response = requests.post(api_url, data={'url': video_url})
    result = response.json()
    return result.get('url')  # m3u8链接
```

### 方案2：模拟浏览器请求

```python
from selenium import webdriver

def parse_video_with_browser(video_url: str):
    """使用浏览器模拟"""
    driver = webdriver.Chrome()
    driver.get(f"https://jx.789jiexi.com/?url={video_url}")
    
    # 等待页面加载
    import time
    time.sleep(5)
    
    # 从页面中提取m3u8链接
    # 方法：执行JavaScript或解析DOM
    m3u8_url = driver.execute_script("return window.videoUrl;")
    
    driver.quit()
    return m3u8_url
```

### 方案3：直接解析视频平台（高级）

需要：
- 分析视频平台的API
- 处理加密/签名
- 模拟登录（如需要）
- 处理反爬虫机制

---

## ⚠️ 注意事项

### 法律和道德

1. **版权问题**：视频解析可能涉及版权问题，请确保合法使用
2. **服务条款**：不要违反视频平台的服务条款
3. **个人使用**：仅用于学习和个人使用，不要商业化

### 技术限制

1. **反爬虫**：视频平台可能有反爬虫机制
2. **API变化**：解析API可能随时变化
3. **稳定性**：解析服务可能不稳定

### 最佳实践

1. **缓存结果**：避免频繁请求
2. **错误处理**：处理网络错误、超时等
3. **用户代理**：使用合理的User-Agent
4. **请求频率**：控制请求频率，避免被封IP

---

## 📚 相关资源

### 技术文档

- [HLS协议文档](https://developer.apple.com/streaming/)
- [m3u8格式说明](https://en.wikipedia.org/wiki/M3U)
- [视频流媒体技术](https://developer.mozilla.org/zh-CN/docs/Web/Media)

### 工具和库

- **前端播放器**：
  - [DPlayer](https://github.com/DIYgod/DPlayer)
  - [Video.js](https://videojs.com/)
  - [ArtPlayer](https://artplayer.org/)

- **HLS播放库**：
  - [hls.js](https://github.com/video-dev/hls.js/)
  - [videojs-contrib-hls](https://github.com/videojs/videojs-contrib-hls)

- **Python库**：
  - [requests](https://requests.readthedocs.io/)
  - [selenium](https://www.selenium.dev/)
  - [playwright](https://playwright.dev/python/)

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests selenium playwright
playwright install  # 如果使用Playwright
```

### 2. 运行分析脚本

```bash
# 基础分析
python analyze_video_parser.py

# 浏览器自动化分析（推荐）
python browser_automation.py
```

### 3. 查看结果

- `parser_page.html` - 解析页面HTML
- `network_requests.json` - 网络请求日志
- `analysis_result.json` - 分析结果

### 4. 手动分析

1. 打开 `parser_page.html`
2. 使用浏览器开发者工具（F12）
3. 查看Network标签，分析请求流程

---

## 📝 分析报告模板

### 分析结果记录

```markdown
## 解析网站分析报告

**网站**: https://jx.789jiexi.com
**目标视频**: https://www.iqiyi.com/v_xxx.html

### 请求流程

1. **初始请求**
   - URL: `/?url=...`
   - 方法: GET
   - 响应: HTML页面

2. **API调用**
   - URL: `/api/parse`
   - 方法: POST
   - 请求参数: `{url: "..."}`
   - 响应: `{url: "m3u8链接", ...}`

3. **m3u8请求**
   - URL: `https://cdn.example.com/video.m3u8`
   - 方法: GET
   - 响应: m3u8播放列表

### 关键技术点

- API端点: `/api/parse`
- 参数格式: JSON/FormData
- 响应格式: JSON
- 认证方式: 无/Token/Cookie

### m3u8获取方式

[描述如何从API响应中提取m3u8链接]
```

---

## ❓ 常见问题

### Q1: 为什么分析不到m3u8链接？

**A**: 可能原因：
- 页面使用了JavaScript动态加载
- m3u8链接被加密或混淆
- 需要等待页面完全加载
- 需要执行特定的JavaScript代码

**解决方案**：
- 使用浏览器自动化工具（Selenium/Playwright）
- 等待页面完全加载
- 执行页面中的JavaScript
- 监听网络请求，而不是解析HTML

### Q2: 如何找到API端点？

**A**: 方法：
1. 打开浏览器开发者工具 -> Network标签
2. 刷新页面
3. 查看XHR/Fetch请求
4. 找到包含视频信息的请求
5. 查看请求URL和参数

### Q3: API需要认证怎么办？

**A**: 可能需要：
- Cookie/Session
- Token/API Key
- 请求签名
- User-Agent验证

**解决方案**：
- 复制浏览器中的请求头
- 使用Session保持Cookie
- 分析JavaScript代码，找到认证逻辑

---

## 📞 技术支持

如有问题，请：
1. 查看浏览器开发者工具的Network标签
2. 分析网络请求流程
3. 查看本文档的常见问题部分

---

**版本**: v1.0  
**更新日期**: 2024-12-08  
**作者**: AI Assistant


