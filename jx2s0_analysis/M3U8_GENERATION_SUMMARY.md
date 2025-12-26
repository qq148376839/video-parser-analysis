# m3u8 链接生成方式分析总结

## 📋 问题

分析链接 `https://cachem3u8.2s0.cn:8899/Cache/Ff/2089c333a6d6a31e306bd190557aea36.m3u8?token=d3d315341476033443543795551335e6c4a6f6c68653438423247664a40533770383968597961423071364c45567457717479585f294d45633251343f207643663273386e60563970776243676545373b2a425f643d426a4` 是如何生成的，是否可以使用直接调用的方式获取到这个链接。

---

## 🔍 分析结果

### 1. m3u8 链接的生成方式

**结论**：m3u8 链接是**通过 JavaScript 代码动态生成的**，不是通过简单的 API 调用获取的。

**证据**：

1. **网络请求顺序**：
   ```
   1. 访问 https://jx.2s0.cn/player/?url=xxx
   2. 加载 iframe: https://jx.2s0.cn/player/analysis.php?v=xxx
   3. 加载 JavaScript 文件：
      - 7zl.js
      - 7zlplayer.js
      - hls.min.js
   4. 调用 /admin/api.php 获取配置（config.url, config.id）
   5. JavaScript 执行，生成 m3u8 链接
   6. 请求 m3u8 文件
   ```

2. **代码分析**：
   - 在反混淆后的 JavaScript 代码中**没有找到** `cachem3u8`、`Cache/Ff` 等关键字
   - m3u8 链接不在 `/admin/api.php` 的响应中
   - m3u8 链接是在 JavaScript 执行后自动出现的

3. **m3u8 链接格式**：
   ```
   https://cachem3u8.2s0.cn:8899/Cache/Ff/{hash}.m3u8?token={token}
   ```
   - **hash**: `2089c333a6d6a31e306bd190557aea36` (32字符，可能是MD5)
   - **token**: `d3d315341476033443543795551335e6c4a6f6c68653438423247664a40533770383968597961423071364c45567457717479585f294d45633251343f207643663273386e60563970776243676545373b2a425f643d426a4` (长字符串，可能是加密或签名)

---

## 🎯 生成逻辑推测

### 可能的生成流程

```
1. 调用 /admin/api.php 获取配置
   ↓
   返回: {
     "data": {
       "url": "O/zpjS4gC4ztyL9ve/+wx/3Lmpl7X/QAEOuqmTie93atrwDjwxRosEpoaXZw0TRD/...",  // Base64编码的加密URL
       "id": "b664f44e3be2ad57fdb6"  // ID
     }
   }

2. JavaScript 处理配置
   ↓
   - 生成 YKQ.id = config.id + " P" = "b664f44e3be2ad57fdb6 P"
   - 解密 config.url（使用RC4算法，但解密后是二进制数据，不是m3u8链接）

3. 生成 hash 和 token
   ↓
   - hash: 可能是基于 config.id 或 video_url 生成的MD5/SHA1
   - token: 可能是基于 config.url、config.id 或其他数据生成的签名

4. 构造 m3u8 链接
   ↓
   https://cachem3u8.2s0.cn:8899/Cache/Ff/{hash}.m3u8?token={token}

5. 播放器加载 m3u8 文件
```

---

## ❓ 关键问题

### 1. hash 的生成方式

**可能的生成方式**：
- 基于 `config.id` 的MD5：`md5("b664f44e3be2ad57fdb6")`
- 基于 `video_url` 的MD5：`md5("https://www.iqiyi.com/v_1c168e2yzbk.html")`
- 基于 `config.id + video_url` 的MD5
- 其他算法（SHA1、SHA256等）

**需要验证**：
```python
import hashlib

config_id = "b664f44e3be2ad57fdb6"
video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"

# 测试不同的hash生成方式
hash1 = hashlib.md5(config_id.encode()).hexdigest()
hash2 = hashlib.md5(video_url.encode()).hexdigest()
hash3 = hashlib.md5((config_id + video_url).encode()).hexdigest()

print(f"hash1 (config.id): {hash1}")
print(f"hash2 (video_url): {hash2}")
print(f"hash3 (config.id + video_url): {hash3}")
print(f"实际hash: 2089c333a6d6a31e306bd190557aea36")
```

### 2. token 的生成方式

**可能的生成方式**：
- 基于 `config.url`（解密后的二进制数据）生成
- 基于 `config.id` 和 `video_url` 生成
- 使用某种加密算法（RC4、AES等）生成
- 通过API调用获取（但网络请求中没有看到）

**token 特征**：
- 长度：约200+字符
- 格式：主要是十六进制字符，但可能包含其他字符
- 可能包含时间戳、签名等信息

---

## 🔧 是否可以直接调用获取？

### ❌ 直接调用 API 获取（不可行）

**尝试的方法**：
1. 直接调用 `/admin/api.php` → 返回配置，但不包含 m3u8 链接
2. 尝试调用 `/api.php?url=xxx`、`/jiexi.php?url=xxx` 等 → 不存在或返回错误
3. 尝试调用 `cachem3u8.2s0.cn:8899/api.php` → 不存在或返回错误

**结论**：**没有直接的 API 可以获取 m3u8 链接**。

### ✅ 使用浏览器自动化（可行）

**方法**：
1. 使用 Playwright 或 Selenium 访问页面
2. 等待 JavaScript 执行
3. 监听网络请求，捕获 m3u8 链接

**已实现的脚本**：
- `analyze_jx2s0_parser.py` - 可以捕获 m3u8 链接
- `analyze_m3u8_generation.py` - 专门分析 m3u8 生成逻辑

**使用示例**：
```bash
python analyze_jx2s0_parser.py
# 输出中包含 m3u8 链接
```

### ⚠️ 完全自动化（需要进一步分析）

**如果希望完全自动化（不需要浏览器）**，需要：

1. **分析 hash 生成算法**：
   - 在浏览器中执行 JavaScript，监控 hash 的生成过程
   - 尝试不同的 hash 生成方式，找到正确的算法

2. **分析 token 生成算法**：
   - 在浏览器中执行 JavaScript，监控 token 的生成过程
   - 分析 token 的生成逻辑（可能是加密、签名等）

3. **实现 Python 版本**：
   - 根据分析结果，实现 Python 版本的 hash 和 token 生成算法
   - 直接构造 m3u8 链接

---

## 📝 推荐方案

### 方案1：使用浏览器自动化（推荐）

**优点**：
- ✅ 简单、可靠
- ✅ 不需要理解复杂的生成逻辑
- ✅ 可以获取到实际的 m3u8 链接

**缺点**：
- ⚠️ 需要浏览器环境
- ⚠️ 执行速度较慢

**实现**：
```python
# 使用 analyze_jx2s0_parser.py
python analyze_jx2s0_parser.py
```

### 方案2：分析生成算法（完全自动化）

**优点**：
- ✅ 不需要浏览器环境
- ✅ 执行速度快

**缺点**：
- ⚠️ 需要深入分析 JavaScript 代码
- ⚠️ 如果算法复杂，可能难以实现
- ⚠️ 如果算法变更，需要重新分析

**实现步骤**：
1. 使用 `analyze_m3u8_generation.py` 分析生成过程
2. 在浏览器中执行 JavaScript，监控 hash 和 token 的生成
3. 根据分析结果，实现 Python 版本的生成算法
4. 测试验证

---

## 🔬 下一步分析方向

### 1. 分析 hash 生成算法

**方法**：
```javascript
// 在浏览器控制台中执行
// 监控 hash 的生成过程
const originalMD5 = window.crypto?.subtle?.digest;
// 或者监控字符串拼接操作
```

**工具**：
- 使用 `analyze_m3u8_generation.py` 脚本
- 在浏览器中设置断点，监控关键变量

### 2. 分析 token 生成算法

**方法**：
```javascript
// 在浏览器控制台中执行
// 监控 token 的生成过程
// 检查是否有加密函数调用
```

**工具**：
- 使用浏览器开发者工具的网络面板
- 使用 `analyze_m3u8_generation.py` 脚本

### 3. 尝试逆向工程

**方法**：
1. 反混淆 JavaScript 代码
2. 查找 `cachem3u8`、`Cache/Ff` 等关键字的生成位置
3. 分析字符串拼接和URL构造逻辑

**工具**：
- `deobfuscate_js.py` - 反混淆工具
- `search_deobfuscated.py` - 搜索关键字

---

## 📊 测试结果

### 从网络请求中捕获的 m3u8 链接

```
https://cachem3u8.2s0.cn:8899/Cache/Ff/2089c333a6d6a31e306bd190557aea36.m3u8?token=d3d315341476033443543795551335e6c4a6f6c68653438423247664a40533770383968597961423071364c45567457717479585f294d45633251343f207643663273386e60563970776243676545373b2a425f643d426a4
```

### 解析结果

- **域名**: `cachem3u8.2s0.cn:8899`
- **路径**: `/Cache/Ff/2089c333a6d6a31e306bd190557aea36.m3u8`
- **hash**: `2089c333a6d6a31e306bd190557aea36` (32字符)
- **token**: `d3d315341476033443543795551335e6c4a6f6c68653438423247664a40533770383968597961423071364c45567457717479585f294d45633251343f207643663273386e60563970776243676545373b2a425f643d426a4` (约200字符)

---

## 📌 总结

### ✅ 已确认

1. **m3u8 链接格式**：`https://cachem3u8.2s0.cn:8899/Cache/Ff/{hash}.m3u8?token={token}`
2. **生成方式**：通过 JavaScript 代码动态生成
3. **无法直接调用 API 获取**：没有直接的 API 端点可以获取 m3u8 链接
4. **可以使用浏览器自动化获取**：通过监听网络请求可以捕获 m3u8 链接

### ❓ 待解决

1. **hash 生成算法**：需要分析 hash 是如何生成的
2. **token 生成算法**：需要分析 token 是如何生成的
3. **完全自动化**：如果希望完全自动化，需要实现 hash 和 token 的生成算法

### 💡 推荐

**优先使用浏览器自动化方案**：
- 使用 `analyze_jx2s0_parser.py` 脚本
- 简单、可靠、无需理解复杂逻辑

**如果需要完全自动化**：
- 使用 `analyze_m3u8_generation.py` 深入分析生成逻辑
- 根据分析结果实现 Python 版本的生成算法

---

**最后更新**：2024-12-08  
**状态**：m3u8 链接生成方式已分析，确认需要通过 JavaScript 执行生成

