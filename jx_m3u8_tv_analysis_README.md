# jx.m3u8.tv 视频解析网站逆向分析

## 概述

本项目用于分析 `jx.m3u8.tv` 视频解析网站的工作原理，提取API调用参数，并实现直接调用API获取m3u8播放地址的功能。

## 文件说明

### 1. `capture_jx_m3u8_tv_params.py`
**功能**: 使用Playwright自动化浏览器，监听网络请求，捕获API调用和关键参数

**使用方法**:
```bash
python capture_jx_m3u8_tv_params.py
```

**功能特点**:
- **独立浏览器启动**：使用独立Chrome浏览器实例，绕过反爬虫检测（推荐）
- 自动访问解析网站
- 监听所有网络请求（fetch/XHR）
- 捕获API调用参数（z、s1ig、g、sign、token等）
- 提取ConFig对象
- 查找m3u8链接
- 分析JavaScript代码，查找参数生成逻辑
- 保存结果到 `captured_jx_m3u8_tv_params.json`

**反爬虫绕过**:
- 使用独立Chrome浏览器实例（`--remote-debugging-port`）
- 添加反爬虫脚本（隐藏webdriver特征）
- 禁用自动化控制特征（`--disable-blink-features=AutomationControlled`）

**输出文件**: `captured_jx_m3u8_tv_params.json`

### 2. `direct_jx_m3u8_tv_parser.py`
**功能**: 基于捕获的参数，直接调用API获取m3u8链接

**使用方法**:
```bash
python direct_jx_m3u8_tv_parser.py
```

**功能特点**:
- 支持两种解析方式：
  1. **iframe + ConFig方式**: 提取iframe URL → 获取ConFig对象 → 跟踪重定向
  2. **直接API调用方式**: 使用捕获的参数直接调用API
- 自动提取m3u8链接
- 跟踪重定向链
- 支持从JSON响应中提取m3u8

## 使用流程

### 步骤1: 捕获API参数

```bash
python capture_jx_m3u8_tv_params.py
```

脚本会：
1. **启动独立Chrome浏览器**（默认启用，可绕过反爬虫检测）
2. 连接到Chrome浏览器的调试端口（CDP协议）
3. 添加反爬虫脚本（隐藏webdriver特征）
4. 访问 `https://jx.m3u8.tv/jiexi/?url={video_url}`
5. 监听网络请求，捕获所有API调用
6. 提取关键参数（z、s1ig、g、sign等）
7. 分析JavaScript代码
8. 保存结果到 `captured_jx_m3u8_tv_params.json`

**注意**: 
- **默认使用独立浏览器启动**（`use_standalone_browser=True`），可有效绕过反爬虫检测
- 如果独立浏览器启动失败，会自动回退到Playwright启动方式
- 如果页面需要手动操作（如点击播放按钮），脚本会尝试自动点击
- 捕获过程可能需要30-60秒
- 独立浏览器会在完成后自动清理

### 步骤2: 分析捕获的参数

查看 `captured_jx_m3u8_tv_params.json` 文件，了解：
- API端点URL
- 请求参数（z、s1ig、g等）
- ConFig对象结构
- m3u8链接

### 步骤3: 直接调用API

```bash
python direct_jx_m3u8_tv_parser.py
```

脚本会：
1. 加载捕获的参数（如果存在）
2. 尝试通过iframe和ConFig解析
3. 如果失败，使用捕获的参数直接调用API
4. 提取m3u8链接

## 参数说明

### 捕获的关键参数

根据不同的视频解析网站，可能包含以下参数：

- **z**: 通常是32位MD5哈希值，用于签名验证
- **s1ig**: 时间戳或签名参数
- **g**: 域名或服务器标识
- **sign**: 签名参数
- **token**: 访问令牌
- **t/timestamp**: 时间戳
- **code**: 编码参数
- **url**: 原始视频URL

### ConFig对象结构

```javascript
window.ConFig = {
    url: "加密的URL（通常是Base64编码）",
    config: {
        uid: "用户ID",
        // 其他配置项
    }
}
```

## 解析流程

### 方式1: iframe + ConFig方式

```
主页面: GET /jiexi/?url={video_url}
    ↓
提取iframe URL
    ↓
iframe页面: GET {iframe_url}
    ↓
提取ConFig对象: window.ConFig = { url: "加密URL", config: {...} }
    ↓
解密/跟踪ConFig.url重定向
    ↓
获取m3u8链接
```

### 方式2: 直接API调用方式

```
使用捕获的参数构造API请求
    ↓
API调用: GET {api_url}?z=xxx&s1ig=xxx&url={video_url}
    ↓
解析JSON响应
    ↓
提取m3u8链接
```

## 注意事项

1. **参数时效性**: 某些参数（如sign、token）可能有时效性，需要定期更新
2. **反爬虫机制**: 网站可能有反爬虫机制，建议：
   - 使用真实的User-Agent
   - 设置合理的请求间隔
   - 使用浏览器自动化方案
3. **网络环境**: 确保网络连接正常，可以访问目标网站
4. **法律合规**: 仅用于学习研究，遵守相关法律法规

## 常见问题

### Q1: 触发反爬虫检测怎么办？

**解决方案**:
- ✅ **使用独立浏览器启动**（默认启用）：脚本会自动启动独立的Chrome浏览器实例，绕过反爬虫检测
- 如果独立浏览器启动失败，脚本会自动回退到Playwright启动方式
- 确保Chrome浏览器已正确安装

### Q2: 捕获不到参数怎么办？

**可能原因**:
1. 页面需要手动操作才能触发API调用
2. API调用被拦截或加密
3. 参数在JavaScript中动态生成
4. 反爬虫检测导致请求被拦截

**解决方案**:
1. **使用独立浏览器启动**（默认已启用）
2. 手动操作页面（浏览器会保持打开30秒）
3. 检查浏览器Console中的网络请求
4. 分析JavaScript代码，查找参数生成逻辑
5. 查看捕获的JSON文件，了解API调用情况

### Q2: API调用返回错误？

**可能原因**:
1. 参数已过期
2. 缺少必要的请求头（Referer、Cookie等）
3. API端点已变更

**解决方案**:
1. 重新运行捕获脚本获取最新参数
2. 检查请求头设置
3. 查看API响应内容，了解错误原因

### Q3: 如何找到参数生成逻辑？

**方法**:
1. 查看 `js_analysis` 字段中的模式匹配结果
2. 在浏览器中设置断点，调试JavaScript代码
3. 查找MD5、hash、encrypt等加密函数调用

## 扩展开发

### 添加新的参数模式

在 `capture_jx_m3u8_tv_params.py` 的 `param_patterns` 中添加新的正则表达式模式：

```python
param_patterns = {
    'new_param': r'new_param\s*[:=]\s*["\']?([^"\']+)["\']?',
    # ...
}
```

### 添加新的API端点

在 `direct_jx_m3u8_tv_parser.py` 的 `api_endpoints` 列表中添加：

```python
api_endpoints = [
    'https://jx.m3u8.tv/api/parse',
    'https://new-api-endpoint.com/parse',  # 新增
]
```

## 依赖安装

```bash
pip install playwright requests
playwright install chromium
```

## 许可证

本项目仅用于学习和研究目的，请遵守相关法律法规和网站服务条款。

