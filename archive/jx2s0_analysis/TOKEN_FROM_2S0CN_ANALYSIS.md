# Token 从 www.2s0.cn 获取的可能性分析

## 📋 假设

**用户假设**：token 可能是根据 `analysis.php` 中的 `config` 对象（`config.url` 和 `config.id`），从 `https://www.2s0.cn` 获取的。

## 🔍 关键发现

### 1. `config` 对象的来源

**位置**：`analysis.php` 第71-82行

```javascript
var config = {
    "api": "/dmku/",
    "av": "",
    "url": "O/zpjS4gC4ztyL9ve/+wx/3Lmpl7X/QAEOuqmTie93atrwDjwxRosEpoaXZw0TRD/...",
    "id": "b664f44e3be2ad57fdb6",
    ...
}
```

**关键点**：
- `config.url` 是 Base64 编码的加密字符串
- `config.id` 是 `"b664f44e3be2ad57fdb6"`
- 这些值是在页面中**硬编码**的，不是从 `/admin/api.php` 获取的

### 2. `YKQ.start()` 的调用流程

**代码位置**：`7zl.js` 第179-259行

```javascript
YKQ.start = function() {
    $.ajax({
        url: '/admin/api.php',  // 调用 /admin/api.php
        dataType: 'json',
        success: function(response) {
            // 设置配置（但响应中没有 config.url 和 config.id）
            // ...
            
            // 第256行：解密并调用 video
            YKQ.video(rc4(config.url, YKQ.id, 1));
        }
    });
}
```

**关键发现**：
- `YKQ.start()` 调用 `/admin/api.php`，但响应中**不包含** `config.url` 和 `config.id`
- `config.url` 和 `config.id` 是在 `analysis.php` 页面中硬编码的
- 第256行调用 `YKQ.video(rc4(config.url, YKQ.id, 1))`

### 3. 网络请求分析

**从 `iframe_requests_intercept.json` 分析**：
- ❌ **没有**对 `www.2s0.cn` 的 API 调用
- ✅ 有对 `/admin/api.php` 的调用（但响应中没有 token）
- ✅ 有对 `cachem3u8.2s0.cn:8899` 的 m3u8 请求（包含 token）

## 🎯 可能性分析

### 可能性1：`config.url` 解密后是 API URL

**假设**：
- `config.url` 解密后可能是一个 API URL（如 `https://www.2s0.cn/api.php`）
- 使用这个 URL 和 `config.id` 调用 API 获取 token

**验证方法**：
1. 解密 `config.url`（RC4，密钥：`config.id + " P"`）
2. 检查解密后的内容是否是 URL
3. 如果是 URL，尝试调用该 API

**测试代码**：
```python
# 解密 config.url
decrypted = rc4_decrypt(config.url, config.id + " P")

# 检查是否是 URL
if decrypted.startswith("http"):
    # 调用 API
    response = requests.get(decrypted, params={"id": config.id})
```

### 可能性2：通过 `config.url` 和 `config.id` 调用 `www.2s0.cn` 的 API

**假设**：
- 使用 `config.url` 和 `config.id` 作为参数调用 `www.2s0.cn` 的某个 API
- API 返回 m3u8 URL 或 token

**可能的 API 端点**：
- `https://www.2s0.cn/api.php`
- `https://www.2s0.cn/api/getm3u8.php`
- `https://www.2s0.cn/api/gettoken.php`
- `https://www.2s0.cn/jiexi.php`

**可能的请求参数**：
- `{"url": config.url, "id": config.id}`
- `{"encrypted_url": config.url, "uid": config.id}`
- `{"data": config.url, "key": config.id}`

### 可能性3：token 在 JavaScript 中生成

**假设**：
- token 不是通过 API 获取的
- 是在 JavaScript 代码中使用 `config.url` 和 `config.id` 生成的
- 需要找到生成算法

## 🔧 测试方案

### 方案1：测试 `config.url` 解密后是否是 URL

```python
# 1. 解密 config.url
from Crypto.Cipher import ARC4
import base64

config_url = "O/zpjS4gC4ztyL9ve/+wx/3Lmpl7X/QAEOuqmTie93atrwDjwxRosEpoaXZw0TRD/..."
config_id = "b664f44e3be2ad57fdb6"

# Base64 解码
encrypted_data = base64.b64decode(config_url)

# RC4 解密
key = (config_id + " P").encode()
cipher = ARC4.new(key)
decrypted = cipher.decrypt(encrypted_data)

# 检查是否是 URL
print(f"解密后内容: {decrypted}")
if decrypted.startswith(b"http"):
    print(f"✅ 是 URL: {decrypted.decode()}")
```

### 方案2：测试 `www.2s0.cn` 的可能 API

```python
import requests

config_url = "O/zpjS4gC4ztyL9ve/+wx/..."
config_id = "b664f44e3be2ad57fdb6"

# 测试不同的 API 端点和参数
endpoints = [
    "https://www.2s0.cn/api.php",
    "https://www.2s0.cn/api/getm3u8.php",
]

params_combinations = [
    {"url": config_url, "id": config_id},
    {"encrypted_url": config_url, "uid": config_id},
    {"data": config_url, "key": config_id},
]

for endpoint in endpoints:
    for params in params_combinations:
        response = requests.get(endpoint, params=params)
        if "m3u8" in response.text or "token" in response.text:
            print(f"✅ 找到 API: {endpoint}")
            print(f"   参数: {params}")
```

### 方案3：在浏览器中拦截 `YKQ.video` 调用

```javascript
// 拦截 YKQ.video 调用
const originalVideo = YKQ.video;
YKQ.video = function(url) {
    console.log('🔍 YKQ.video 被调用');
    console.log('   URL:', url);
    console.log('   URL类型:', typeof url);
    console.log('   URL长度:', url.length);
    
    // 检查是否是 m3u8 URL
    if (url.includes('m3u8') || url.includes('cachem3u8')) {
        console.log('✅ 找到m3u8 URL:', url);
    }
    
    // 检查是否是 API URL
    if (url.startsWith('http')) {
        console.log('🔍 可能是 API URL:', url);
    }
    
    return originalVideo.apply(this, arguments);
};
```

## 📊 当前状态

### ✅ 已确认

1. `config` 对象在 `analysis.php` 中硬编码
2. `YKQ.start()` 调用 `/admin/api.php`，但响应中没有 `config.url` 和 `config.id`
3. 网络请求中没有看到对 `www.2s0.cn` 的 API 调用

### ❓ 待验证

1. `config.url` 解密后是否是 URL？
2. 是否有对 `www.2s0.cn` 的隐藏 API 调用？
3. token 是否在 JavaScript 中生成？

## 🎯 推荐行动

### 优先：测试 `config.url` 解密后是否是 URL

1. 运行 RC4 解密脚本
2. 检查解密后的内容
3. 如果是 URL，尝试调用该 API

### 备选：测试 `www.2s0.cn` 的可能 API

1. 使用 `test_token_from_2s0cn.py` 脚本
2. 测试所有可能的 API 端点和参数组合
3. 查看是否有返回 m3u8/token 的 API

### 最后：在浏览器中调试

1. 拦截 `YKQ.video` 调用
2. 查看传入的参数
3. 分析 token 的生成过程

