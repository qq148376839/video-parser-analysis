# jx.2s0.cn m3u8链接生成分析

## 📋 关键发现

### 1. `/admin/api.php` 响应分析

**API响应**：
```json
{
  "code": 1,
  "data": {
    "bgsp": "https://videobd-platform.cdn.huya.com/1048585/1259553301717/40497871/b33c01064a59e267de2a1b237c2d4881.mp4",
    "url": "O/zpjS4gC4ztyL9ve/+wx/3Lmpl7X/QAEOuqmTie93atrwDjwxRosEpoaXZw0TRD/...",
    "id": "b664f44e3be2ad57fdb6",
    ...
  }
}
```

**关键字段**：
- `bgsp`: 背景视频链接（mp4格式）
- `url`: **加密的URL**（Base64编码的RC4加密字符串）
- `id`: 视频ID

**问题**：
- API响应中**没有直接返回m3u8链接**
- m3u8链接格式：`https://cachem3u8.2s0.cn:8899/Cache/Ff/{hash}.m3u8?token={token}`
- 这个链接**不在代码中**（搜索 `cachem3u8`、`Cache`、`m3u8` 都没找到）

---

### 2. m3u8链接生成推测

**可能性1：通过解密 `config.url` 得到**

**流程**：
```
config.url (加密) 
  → rc4解密 (密钥: YKQ.id = "b664f44e3be2ad57fdb6 P")
  → 得到m3u8链接
```

**问题**：
- 之前测试解密结果是乱码
- 可能原因：
  1. 密钥不对（但YKQ.id应该是正确的）
  2. 解密后的数据需要进一步处理
  3. 解密后的数据是另一个加密的URL，需要再次解密

**验证方法**：
- 在浏览器控制台中测试解密
- 检查解密后的数据是否是有效的URL

---

**可能性2：通过另一个API调用得到**

**流程**：
```
1. 调用 /admin/api.php 获取 config.url 和 config.id
2. 使用 config.url 或 config.id 调用另一个API
3. API返回m3u8链接
```

**可能的API端点**：
- `/api.php?id={config.id}`
- `/jiexi.php?url={config.url}`
- `/parse.php?id={config.id}`
- 其他隐藏的API端点

**验证方法**：
- 在网络请求中查找所有API调用
- 检查是否有返回m3u8链接的API

---

**可能性3：通过JavaScript动态构造**

**流程**：
```
1. 获取 config.url 和 config.id
2. 使用某种算法生成hash和token
3. 构造m3u8链接：https://cachem3u8.2s0.cn:8899/Cache/Ff/{hash}.m3u8?token={token}
```

**问题**：
- 代码中没有找到 `cachem3u8`、`Cache`、`m3u8` 等关键字
- 说明链接可能是通过字符串拼接或变量构造的

**验证方法**：
- 搜索 `cachem3u8`、`2s0.cn`、`8899` 等关键字
- 查找字符串拼接或URL构造的代码

---

## 🔍 代码分析

### 关键代码位置

**7zl.js:256**：
```javascript
YKQ[_0x319ba2(0x205, '3Txb')](_0x5e7426[_0x319ba2(0x4a1, 'W19[')](rc4, config[_0x319ba2(0x1ea, 'Iar!')], _0x5e7426[_0x319ba2(0x6f3, 'Y!Al')], 0x1));
```

**分析**：
- `_0x319ba2(0x205, '3Txb')` 应该是 `'video'` 或类似的方法名
- `_0x5e7426[_0x319ba2(0x4a1, 'W19[')]` 应该是 `call` 或 `apply`
- 实际调用：`YKQ.video(rc4(config.url, YKQ.id, 1))`

**问题**：
- 需要找到 `YKQ.video` 方法如何处理解密后的URL
- 解密后的URL是否直接是m3u8链接，还是需要进一步处理

---

### 7zlplayer.js中的XMLHttpRequest

**位置**：`7zlplayer.js:4318`

**代码**：
```javascript
var _0xda7da8 = new XMLHttpRequest();
```

**分析**：
- 这可能用于加载m3u8文件或其他资源
- 需要查看这个XMLHttpRequest的完整代码，看它请求什么URL

---

## 🎯 验证方案

### 方案1：在浏览器中测试解密（推荐）

**步骤**：
1. 访问 `https://jx.2s0.cn/player/analysis.php?v=https://www.iqiyi.com/v_1c168e2yzbk.html`
2. 打开浏览器控制台
3. 执行以下代码：

```javascript
// 检查config对象
console.log('config:', config);
console.log('config.url:', config.url);
console.log('config.id:', config.id);

// 检查YKQ对象
console.log('YKQ.id:', YKQ.id);

// 测试解密
var encrypted = config.url;
var key = YKQ.id;  // "b664f44e3be2ad57fdb6 P"
var decrypted = rc4(encrypted, key, 1);
console.log('解密结果:', decrypted);
console.log('是否是URL:', decrypted.startsWith('http'));
console.log('包含m3u8:', decrypted.includes('.m3u8'));
console.log('包含cachem3u8:', decrypted.includes('cachem3u8'));

// 检查解密后的数据
console.log('解密后长度:', decrypted.length);
console.log('前100字符:', decrypted.substring(0, 100));
```

**预期结果**：
- 如果解密成功，应该得到m3u8链接
- 如果还是乱码，说明密钥不对或需要其他处理

---

### 方案2：监听网络请求

**步骤**：
1. 使用浏览器开发者工具的网络面板
2. 访问analysis.php页面
3. 查找所有包含 `cachem3u8` 或 `.m3u8` 的请求
4. 检查请求的Referer、Headers等信息
5. 查看请求是如何触发的（可能是JavaScript调用）

**关键信息**：
- 请求的URL
- 请求的方法（GET/POST）
- 请求的参数
- 请求的触发时机

---

### 方案3：搜索相关关键字

**搜索关键字**：
- `cachem3u8`
- `2s0.cn:8899`
- `Cache/Ff`
- `token=`
- 字符串拼接：`+`、`concat`、`join`
- URL构造：`new URL()`、`window.location`

**搜索位置**：
- `7zl.js`
- `7zlplayer.js`
- 其他JavaScript文件

---

## 📝 工作流程推测（更新）

### 流程A：通过解密config.url（最可能）

```
1. YKQ.start()
   ↓
2. 调用 /admin/api.php 获取配置
   ↓
3. 设置 config.url（加密）和 config.id
   ↓
4. 生成 YKQ.id = config.id + " P"
   ↓
5. 调用 rc4(config.url, YKQ.id, 1) 解密
   ↓
6. 解密结果应该是m3u8链接（但之前测试是乱码）
   ↓
7. YKQ.video(decrypted_url) 设置视频源
   ↓
8. 播放器加载m3u8文件
```

**问题**：
- 解密结果是乱码，可能密钥不对或需要其他处理

---

### 流程B：通过另一个API调用

```
1. YKQ.start()
   ↓
2. 调用 /admin/api.php 获取配置
   ↓
3. 设置 config.url 和 config.id
   ↓
4. 使用 config.url 或 config.id 调用另一个API
   ↓
5. API返回m3u8链接
   ↓
6. YKQ.video(m3u8_url) 设置视频源
   ↓
7. 播放器加载m3u8文件
```

**问题**：
- 代码中没有找到这个API调用
- 可能是在7zlplayer.js中

---

### 流程C：动态构造m3u8链接

```
1. YKQ.start()
   ↓
2. 调用 /admin/api.php 获取配置
   ↓
3. 设置 config.url 和 config.id
   ↓
4. 使用某种算法生成hash和token
   ↓
5. 构造m3u8链接：https://cachem3u8.2s0.cn:8899/Cache/Ff/{hash}.m3u8?token={token}
   ↓
6. YKQ.video(m3u8_url) 设置视频源
   ↓
7. 播放器加载m3u8文件
```

**问题**：
- 代码中没有找到构造逻辑
- hash和token的生成算法未知

---

## 🔧 下一步行动

### 1. 在浏览器中测试解密（优先）

**目的**：验证 `config.url` 解密后是否是m3u8链接

**方法**：
- 使用浏览器控制台执行解密代码
- 检查解密结果

### 2. 监听网络请求

**目的**：找到m3u8链接的请求来源

**方法**：
- 使用浏览器开发者工具
- 查找所有包含 `cachem3u8` 的请求
- 分析请求的触发时机和参数

### 3. 搜索相关关键字

**目的**：找到m3u8链接的生成代码

**方法**：
- 搜索 `cachem3u8`、`2s0.cn:8899`、`Cache/Ff` 等
- 搜索字符串拼接和URL构造的代码

---

## 📌 总结

### 已确认的信息

1. ✅ `/admin/api.php` 返回 `config.url`（加密）和 `config.id`
2. ✅ API响应中**没有直接返回m3u8链接**
3. ✅ m3u8链接格式：`https://cachem3u8.2s0.cn:8899/Cache/Ff/{hash}.m3u8?token={token}`
4. ✅ 代码中**没有找到** `cachem3u8`、`Cache`、`m3u8` 等关键字

### 待解决的问题

1. ❓ **m3u8链接的来源**：是通过解密 `config.url` 得到的，还是通过其他方式？
2. ❓ **解密结果**：之前测试解密是乱码，需要重新验证
3. ❓ **生成逻辑**：如果m3u8链接是动态构造的，hash和token是如何生成的？

### 推荐方案

**优先在浏览器中测试解密**：
- 使用浏览器控制台执行解密代码
- 验证解密结果是否是m3u8链接
- 如果还是乱码，检查是否有其他处理

**备选方案**：
- 使用浏览器自动化监听网络请求
- 直接提取m3u8链接
- 简单、可靠、无需理解复杂逻辑

