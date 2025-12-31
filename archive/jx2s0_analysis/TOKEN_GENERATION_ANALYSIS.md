# Token 生成方式分析

## 📋 关键发现

从网络请求拦截结果分析，发现了以下关键信息：

### ✅ 已确认的请求流程

1. **主页面加载**：
   ```
   GET https://jx.2s0.cn/player/?url=https://www.iqiyi.com/v_19rr7qhfg0.html
   ```

2. **iframe 加载**：
   ```
   GET https://jx.2s0.cn/player/analysis.php?v=https://www.iqiyi.com/v_19rr7qhfg0.html
   ```

3. **配置接口调用**：
   ```
   GET https://jx.2s0.cn/admin/api.php
   ```
   - 请求类型：XHR
   - 请求头：`x-requested-with: XMLHttpRequest`
   - 接受类型：`application/json, text/javascript, */*; q=0.01`
   - **关键**：没有查询参数，说明可能是通过 POST 或请求头传递参数

4. **m3u8 请求**：
   ```
   GET https://cachem3u8.2s0.cn:8899/Cache/Ff/aeaf87d55e9fd0251470c951429cde13.m3u8?token=d3d3150395741603c427771426749747b6478576a705f2c6070736b2633635338324751347f213f435139456071333b67554c6e6d6473594736785e43684c445a4372743a58587561773a6b4766375a4452333c67346e663
   ```
   - **关键**：token 已经包含在 URL 中
   - 说明 token 是在 JavaScript 代码中生成的，而不是通过 API 获取的

---

## 🎯 关键结论

### Token 不是在 API 响应中返回的

**证据**：
1. `/admin/api.php` 是配置接口，但 m3u8 URL 已经包含了 token
2. m3u8 URL 是直接请求的，没有看到获取 token 的中间步骤
3. token 的格式是十六进制字符串，可能是加密或编码后的结果

### Token 是在 JavaScript 中生成的

**推测流程**：
```
1. 调用 /admin/api.php 获取配置（config.url, config.id）
   ↓
2. JavaScript 代码执行，使用配置信息生成 token
   ↓
3. 构造 m3u8 URL：https://cachem3u8.2s0.cn:8899/Cache/Ff/{hash}.m3u8?token={token}
   ↓
4. 调用 hls.loadSource(m3u8_url)
```

---

## 🔍 下一步分析方向

### 方向1：分析 `/admin/api.php` 的响应内容（优先）

**方法**：
1. 使用改进后的脚本捕获响应内容
2. 或者使用浏览器开发者工具查看响应
3. 分析响应中是否包含生成 token 所需的信息

**改进脚本**：
- 已更新 `intercept_iframe_requests.py`，现在会捕获响应内容
- 特别关注 JSON 响应，会自动解析

### 方向2：在 JavaScript 代码中查找 token 生成逻辑

**搜索位置**：
1. `7zl.js` - 配置获取和 RC4 解密
2. `7zlplayer.js` - 播放器核心代码
3. iframe 页面中的其他 JavaScript 代码

**搜索关键字**：
- `cachem3u8`、`2s0.cn:8899`、`Cache/Ff`
- `token`、`generateToken`、`createToken`
- URL 拼接相关的代码

### 方向3：分析 token 的格式和生成算法

**token 格式分析**：
```
token=d3d3150395741603c427771426749747b6478576a705f2c6070736b2633635338324751347f213f435139456071333b67554c6e6d6473594736785e43684c445a4372743a58587561773a6b4766375a4452333c67346e663
```

**特征**：
- 长度：约 200+ 字符
- 格式：十六进制字符串（0-9, a-f）
- 可能包含：时间戳、签名、加密数据

**可能的生成方式**：
1. **MD5/SHA 哈希**：对某些数据进行哈希
2. **AES 加密**：使用密钥加密某些数据
3. **Base64 编码**：编码后的数据转换为十六进制
4. **字符串拼接**：多个参数拼接后编码

---

## 🔧 改进的脚本功能

### 已改进的功能

1. **更精确的过滤**：
   - 排除静态资源（图片、CSS、字体等）
   - 排除 `playerapi` 路径下的静态资源
   - 只识别真正的 API 请求

2. **响应内容捕获**：
   - 自动捕获 JSON 响应并解析
   - 捕获包含 token/m3u8 的文本响应
   - 保存响应内容到 JSON 文件

3. **更清晰的输出**：
   - 显示资源类型
   - 只显示关键请求头
   - JSON 响应自动格式化

### 使用方法

```bash
cd archive/jx2s0_analysis
python intercept_iframe_requests.py
```

**输出改进**：
- 更少的误判（不再把图片、CSS 当作 token 相关）
- 捕获响应内容（可以看到 `/admin/api.php` 的响应）
- 自动解析 JSON（如果响应是 JSON 格式）

---

## 📊 分析结果总结

### 已确认的信息

1. ✅ `/admin/api.php` 是配置接口（XHR 请求）
2. ✅ m3u8 URL 已经包含 token（说明 token 在 JS 中生成）
3. ✅ 请求流程：主页面 → iframe → 配置接口 → m3u8 请求

### 待解决的问题

1. ❓ `/admin/api.php` 的响应内容是什么？
2. ❓ token 是如何生成的？（算法、参数）
3. ❓ hash（`aeaf87d55e9fd0251470c951429cde13`）是如何生成的？

### 推荐行动

1. **运行改进后的脚本**：
   ```bash
   python intercept_iframe_requests.py
   ```
   - 查看 `/admin/api.php` 的响应内容
   - 分析响应中是否包含生成 token 所需的信息

2. **在浏览器中手动检查**：
   - 打开开发者工具 → Network 面板
   - 找到 `/admin/api.php` 请求
   - 查看 Response 标签，查看响应内容

3. **分析 JavaScript 代码**：
   - 在 `7zl.js` 和 `7zlplayer.js` 中搜索 token 生成相关代码
   - 搜索 URL 拼接相关的代码

---

## 📝 注意事项

1. **token 可能有时效性**：
   - token 可能包含时间戳
   - 需要实时生成，不能复用

2. **token 生成可能需要多个参数**：
   - 配置接口返回的数据
   - 视频 URL
   - 时间戳
   - 其他签名参数

3. **token 可能包含加密数据**：
   - 需要找到加密算法和密钥
   - 可能需要逆向 JavaScript 代码

