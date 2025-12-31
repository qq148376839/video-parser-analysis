# API 响应分析指南

## 📋 当前状态

### ✅ 已确认的信息

1. **请求流程**：
   ```
   主页面 → iframe → /admin/api.php → m3u8请求（包含token）
   ```

2. **关键接口**：
   - `/admin/api.php` - 配置接口（XHR 请求）
   - 请求头：`x-requested-with: XMLHttpRequest`
   - 接受类型：`application/json, text/javascript, */*; q=0.01`

3. **m3u8 URL 格式**：
   ```
   https://cachem3u8.2s0.cn:8899/Cache/Ff/{hash}.m3u8?token={token}
   ```

### ❓ 待解决的问题

1. **`/admin/api.php` 的响应内容是什么？**
   - 响应可能包含生成 token 所需的信息
   - 需要查看实际的响应内容

2. **token 是如何生成的？**
   - token 在 JavaScript 中生成
   - 需要找到生成算法和参数

---

## 🔧 改进后的脚本功能

### 新功能

1. **专门捕获重要 API 响应**：
   - 无论响应是否包含 token，都会捕获 `/admin/api.php` 的响应
   - 自动解析 JSON 响应
   - 显示完整的响应内容

2. **关联请求和响应**：
   - 在输出中显示 API 请求和对应的响应
   - 方便分析请求-响应关系

3. **保存所有响应**：
   - 所有响应都保存到 JSON 文件
   - 重要 API 响应单独提取

### 使用方法

```bash
cd archive/jx2s0_analysis
python intercept_iframe_requests.py
```

### 输出改进

现在脚本会：
1. ✅ 专门捕获 `/admin/api.php` 的响应
2. ✅ 自动解析 JSON 响应并格式化显示
3. ✅ 在 API 请求详情中显示对应的响应
4. ✅ 保存所有响应到 JSON 文件

---

## 📊 预期输出示例

运行改进后的脚本，您应该能看到类似以下输出：

```
📡 [API请求] GET https://jx.2s0.cn/admin/api.php
   Frame: https://jx.2s0.cn/player/analysis.php?v=xxx
   资源类型: xhr

📥 [重要API响应] 200 https://jx.2s0.cn/admin/api.php
   Frame: https://jx.2s0.cn/player/analysis.php?v=xxx
   Content-Type: application/json
   内容预览: {"url":"...","id":"...","config":{...}}
   ✅ JSON解析成功:
   {
     "url": "...",
     "id": "...",
     "config": {
       "uid": "...",
       ...
     }
   }

================================================================================
📡 API请求详情
================================================================================

[1] GET https://jx.2s0.cn/admin/api.php
    Frame: https://jx.2s0.cn/player/analysis.php?v=xxx
    Frame名称: myiframe
    ✅ 响应状态: 200
    📦 JSON响应:
    {
        "url": "...",
        "id": "...",
        ...
    }
```

---

## 🎯 下一步操作

### 步骤1：运行改进后的脚本

```bash
python intercept_iframe_requests.py
```

**目标**：查看 `/admin/api.php` 的实际响应内容

### 步骤2：分析响应内容

**如果响应是 JSON**：
- 查看响应中包含哪些字段
- 分析哪些字段可能用于生成 token
- 检查是否有时间戳、签名等字段

**如果响应是文本**：
- 查看响应格式
- 分析是否包含加密或编码的数据

### 步骤3：分析 token 生成逻辑

**在 JavaScript 代码中搜索**：
1. 搜索使用响应数据的代码
2. 搜索 URL 拼接相关的代码
3. 搜索加密/编码相关的代码

**搜索关键字**：
- `cachem3u8`、`2s0.cn:8899`、`Cache/Ff`
- `token`、`generateToken`、`createToken`
- URL 拼接：`+`、`concat`、`join`

---

## 📝 分析要点

### 1. 响应字段分析

如果 `/admin/api.php` 返回 JSON，重点关注：
- `url` - 可能是加密的 URL
- `id` - 可能是用户 ID 或配置 ID
- `config` - 配置对象
- `uid` - 用户 ID
- `timestamp` - 时间戳
- `sign` - 签名

### 2. token 生成可能需要的参数

根据经验，token 生成可能需要：
- 配置接口返回的数据（`id`、`uid` 等）
- 视频 URL
- 时间戳
- 密钥（可能在 JavaScript 代码中）

### 3. token 格式分析

当前 token 格式：
```
d3d376f6b4a7275354c495432623a4a42517d6731783c4b6149446f4643344a74415852734441695738467b6745314577526e625a61444c444653763c6d427946577837315453644153534944473941573a6a487b613a4c6
```

**特征**：
- 十六进制字符串
- 长度约 200+ 字符
- 可能包含：时间戳、签名、加密数据

---

## 🔍 调试技巧

### 1. 在浏览器中手动检查

1. 打开开发者工具 → Network 面板
2. 找到 `/admin/api.php` 请求
3. 点击请求 → Response 标签
4. 查看响应内容

### 2. 使用控制台拦截

在浏览器控制台中执行：

```javascript
// 拦截 XMLHttpRequest
const originalOpen = XMLHttpRequest.prototype.open;
const originalSend = XMLHttpRequest.prototype.send;

XMLHttpRequest.prototype.open = function(method, url, ...args) {
    if (url.includes('/admin/api.php')) {
        console.log('🔍 API请求:', method, url);
        this.addEventListener('load', function() {
            console.log('📥 API响应:', this.status, this.responseText);
            try {
                const json = JSON.parse(this.responseText);
                console.log('📦 JSON数据:', json);
            } catch (e) {
                console.log('📄 文本数据:', this.responseText);
            }
        });
    }
    return originalOpen.apply(this, [method, url, ...args]);
};
```

### 3. 查看 JSON 文件

运行脚本后，查看 `iframe_requests_intercept.json`：
- 查找 `important_api_responses` 字段
- 查看 `response_json` 或 `response_text` 字段

---

## 📚 相关文件

- `intercept_iframe_requests.py` - 改进后的监听脚本
- `iframe_requests_intercept.json` - 监听结果（运行脚本后生成）
- `TOKEN_GENERATION_ANALYSIS.md` - Token 生成分析文档

