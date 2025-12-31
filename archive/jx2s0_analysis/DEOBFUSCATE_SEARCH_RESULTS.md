# 反混淆搜索结果分析

## 📋 搜索结果汇总

### 7zl.js 搜索结果

| 关键字 | 找到数量 | 位置 | 说明 |
|--------|---------|------|------|
| `Cache` | 1处 | 第2086行 | `'cache': ![]` - 缓存配置 |
| `rc4` | 2处 | 第256行, 第2807行 | RC4解密函数调用和定义 |
| `atob` | 1处 | 第2872行 | Base64解码（在rc4函数中） |
| `btoa` | 1处 | 第2926行 | Base64编码（在rc4函数中） |

**未找到的关键字**：
- `m3u8`、`cachem3u8`、`token`、`cachem3u8.2s0.cn`、`8899`、`Cache/Ff`
- `XMLHttpRequest`、`fetch`、`$.ajax`
- `config.url`、`YKQ.video`、`YKQ.player`、`/admin/api.php`

**分析**：
- `7zl.js` 主要负责配置获取和RC4解密
- 不包含m3u8链接的生成逻辑
- m3u8链接可能在其他地方生成或通过API获取

---

### 7zlplayer.js 搜索结果

| 关键字 | 找到数量 | 位置 | 说明 |
|--------|---------|------|------|
| `m3u8` | 1处 | 第2434行 | m3u8格式检查 |
| `token` | 5处 | 第2271, 2416, 3091, 6099, 8025行 | token使用（主要用于弹幕API） |
| `8899` | 3处 | 第6633, 6645, 6646行 | 函数名的一部分，不是端口号 |
| `XMLHttpRequest` | 1处 | 第4346行 | XMLHttpRequest创建（用于弹幕） |
| `rc4` | 2处 | 第11108, 11109行 | 字符串数组中的rc4（可能是版本信息） |

**未找到的关键字**：
- `cachem3u8`、`Cache`、`Cache/Ff`、`cachem3u8.2s0.cn`
- `fetch`、`$.ajax`
- `config.url`、`YKQ.video`、`YKQ.player`、`/admin/api.php`

**分析**：
- `7zlplayer.js` 是播放器核心代码
- 第2434行检查URL格式，如果是m3u8则使用Hls.js加载
- token主要用于弹幕功能，不是m3u8链接生成

---

### hls.min.js 搜索结果

| 关键字 | 找到数量 | 位置 | 说明 |
|--------|---------|------|------|
| `token` | ❌ 0处 | - | **未找到 token 相关代码** |
| `sign` / `signature` | 4处 | 第1608, 3032, 3098, 8743行 | WebVTT签名验证（字幕相关） |
| `encrypt` / `decrypt` | 114处 | 多处 | AES解密（视频片段解密） |
| `timestamp` | 30处 | 多处 | 时间戳处理（视频同步） |
| `loadLevel` / `loadPlaylist` | 18处 | 多处 | 播放列表加载 |
| `XMLHttpRequest` | 8处 | 第9175, 9219, 9234等 | XHR请求处理 |
| `xhrSetup` | 6处 | 第8118, 9178, 9213等 | XHR设置钩子 |

**关键发现**：
- ✅ **hls.min.js 中没有 token 计算逻辑**
- ✅ **hls.min.js 中没有 URL 修改或参数添加逻辑**
- ✅ **Hls.js 只是标准的 HLS 播放器库**，负责加载和播放 m3u8 文件
- 📍 **xhrSetup 钩子**：允许外部代码在请求前修改 XHR（需要外部配置）

**分析**：
- `hls.min.js` 是标准的 HLS.js 库，不包含业务逻辑
- token 的计算**不在 hls.js 中**，应该在调用 `hls.loadSource()` 之前就已经添加到 URL
- 可能的 token 添加位置：
  1. 在 `7zl.js` 或 `7zlplayer.js` 中，调用 `video()` 方法之前
  2. 通过 `xhrSetup` 钩子动态添加（但需要外部配置）

---

## 🔍 关键代码位置分析

### 1. m3u8格式检查（7zlplayer.js:2434）

**代码位置**：第2434行

**代码片段**：
```javascript
switch (_0x344e20[_0x22489a(0x295, 'K*Uh')](_0x344e20['nQwww'], this['type']) && 
    (/m3u8(#|\?|$)/i['exec'](_0x2de0a3['src']) ? 
        this[_0x22489a(0x143, 'nA5Z')] = _0x344e20[_0x22489a(0x97a, 'nA5Z')] : 
        /.flv(#|\?|$)/i['exec'](_0x2de0a3[_0x22489a(0x901, '960y')]) ? 
            this[_0x22489a(0x14ba, 's71*')] = _0x344e20[_0x22489a(0xb29, 'T#Xc')] : 
        /.mpd(#|\?|$)/i[_0x22489a(0xacd, 'eIRR')](_0x2de0a3[_0x22489a(0x1322, 'eIRR')]) ? 
            this[_0x22489a(0xb0c, 'tIKR')] = _0x344e20[_0x22489a(0xfe6, 'nA5Z')] : 
            this[_0x22489a(0x9e4, 'qk^d')] = _0x344e20[_0x22489a(0x8ba, 'OEl8')]),
    this[_0x22489a(0xa14, 'hcBW')]) {
    case _0x344e20[_0x22489a(0x1401, 'SrCy')]:
        if (Hls) {
            if (Hls[_0x22489a(0xed9, '%!Pk')]()) {
                var _0x43bddc = new Hls();
                _0x43bddc['loadSource'](_0x2de0a3[_0x22489a(0x14f4, ')3ld')]),
                _0x43bddc[_0x22489a(0xf08, 'f0bY')](_0x2de0a3);
```

**分析**：
- 检查 `_0x2de0a3['src']` 是否是m3u8格式
- 如果是m3u8，使用Hls.js加载：`_0x43bddc['loadSource'](_0x2de0a3['src'])`
- **关键**：m3u8链接是通过 `_0x2de0a3['src']` 传入的

---

### 2. video方法定义（7zlplayer.js:2402-2420）

**代码位置**：第2402-2420行

**代码片段**：
```javascript
'key': _0x19c90a[_0xa00505(0x1244, 'wrK*')],  // 应该是 'video'
'value': function(_0x55660d, _0x41555b) {
    var _0x1a10c7 = _0xa00505;
    this[_0x1a10c7(0x5d8, 'sNI]')](),
    this[_0x1a10c7(0x1182, ']Q6v')][_0x1a10c7(0xcc9, '(PWa')] = _0x55660d[_0x1a10c7(0xd3b, 'p$C]')] ? _0x55660d[_0x1a10c7(0xdcb, '74ri')] : '',
    this[_0x1a10c7(0x607, 'Y3Yq')][_0x1a10c7(0x14f4, ')3ld')] = _0x55660d['url'],  // 设置视频源URL
    this[_0x1a10c7(0x5bb, '%oG4')](this[_0x1a10c7(0x91c, 'nA5Z')], _0x55660d['type'] || _0x344e20[_0x1a10c7(0x1100, 'dP!U')]),
    // ... 弹幕配置 ...
}
```

**分析**：
- `video` 方法接受参数 `_0x55660d`，其中包含 `url` 属性
- 第2406行：`this['options']['video']['src'] = _0x55660d['url']` - 设置视频源
- 然后调用 `this['type']` 方法，最终在第2434行检查URL格式

**关键问题**：
- **谁调用了 `video` 方法？**
- **`_0x55660d['url']` 是从哪里来的？**

---

### 3. token使用位置

**位置1**：第2271行 - API配置
```javascript
'token': this['options'][_0x43496a(0xf7f, 'Hx)%')][_0x43496a(0x13a1, '1[kd')],
```
- 用于API配置，可能是弹幕API的token

**位置2**：第2416行 - 弹幕配置
```javascript
'token': _0x41555b[_0x1a10c7(0x285, 'bNX[')],
```
- 在 `video` 方法中设置弹幕token

**位置3**：第3091行 - 弹幕发送
```javascript
'token': this['options'][_0x2955f9(0xe14, 'SrCy')]['token'],
```
- 发送弹幕时使用

**位置4-5**：第6099, 8025行 - 其他弹幕相关

**结论**：token主要用于弹幕功能，**不是用于m3u8链接生成**

---

## 🎯 关键发现

### ✅ 已确认

1. **m3u8链接是通过 `video` 方法的 `url` 参数传入的**
   - 位置：`7zlplayer.js:2406` - `this['options']['video']['src'] = _0x55660d['url']`
   - 然后通过 `_0x2de0a3['src']` 传递给Hls.js
   - **重要**：Hls.js 只是加载器，不会修改URL或添加token参数

2. **hls.min.js 分析结果**
   - ✅ **已确认**：hls.min.js 中没有 token 相关的代码
   - ✅ **已确认**：hls.min.js 中没有 URL 修改或参数添加的逻辑
   - ✅ **已确认**：Hls.js 使用 `xhrSetup` 钩子允许外部代码修改请求（但需要外部配置）
   - 📍 **关键代码位置**：
     - `hls.min.js:9217` - `xhrSetup` 回调调用：`i(e, t.url)`
     - `hls.min.js:9222` - 直接使用传入的URL：`e.open("GET", t.url, !0)`
   - **结论**：**token 的计算不在 hls.js 中**，应该在调用 `hls.loadSource()` 之前就已经添加到 URL 中

2. **播放器会根据URL后缀判断格式**
   - m3u8 → 使用Hls.js
   - flv → 使用flv.js
   - mpd → 使用dash.js

3. **token主要用于弹幕功能**
   - 不是m3u8链接生成的关键

### ❓ 待解决的问题

1. **谁调用了 `video` 方法？**
   - 需要查找 `player.video()` 或 `YKQ.video()` 的调用位置
   - 可能在 `7zl.js` 中

2. **m3u8链接是从哪里来的？**
   - 不在 `7zl.js` 和 `7zlplayer.js` 中直接生成
   - 可能是：
     - 通过API获取（但未找到相关代码）
     - 在iframe中生成
     - 通过其他JavaScript文件生成

3. **为什么搜索不到 `cachem3u8`？**
   - 可能：
     - 字符串被进一步混淆（不是简单的十六进制编码）
     - 通过字符串拼接生成
     - 在运行时动态生成

---

## 🔧 下一步分析方向

### 方向1：查找video方法的调用位置（推荐）

**方法**：
1. 在 `7zl.js` 中搜索 `video` 方法的调用
2. 查找 `YKQ.video()` 或 `player.video()` 的调用
3. 分析传入的URL参数来源

**搜索关键字**：
- `.video(`、`['video'](`、`["video"](`
- `YKQ.video`、`player.video`

### 方向2：分析iframe中的代码

**方法**：
1. 使用浏览器开发者工具查看iframe内容
2. 分析iframe中的JavaScript代码
3. 查找m3u8链接的生成逻辑

**工具**：
- `analyze_jx2s0_parser.py` - 已实现iframe分析

### 方向3：监听网络请求（最实用）

**方法**：
1. 使用浏览器开发者工具的网络面板
2. 访问页面，监听所有网络请求
3. 查找包含 `cachem3u8` 或 `.m3u8` 的请求
4. 分析请求的触发位置和参数

**工具**：
- `analyze_jx2s0_parser.py` - 已实现网络监听
- `direct_jx2s0_parser.py` - 直接提取m3u8链接

### 方向4：监听 iframe 中的网络请求（**强烈推荐**）

**问题**：在 F12 的 Network 面板中看不到 token 获取接口，可能是因为请求在 iframe 中发起。

**解决方案**：

#### 方法A：使用自动监听脚本（推荐）

已创建 `intercept_iframe_requests.py` 脚本，可以：
- ✅ 监听**所有 frame**（包括主页面和所有 iframe）的网络请求
- ✅ 自动识别 token 相关的请求
- ✅ 自动识别 m3u8 相关的请求
- ✅ 保存详细的请求和响应信息

**使用方法**：
```bash
cd archive/jx2s0_analysis
python intercept_iframe_requests.py
```

**输出**：
- 控制台实时显示所有 token 相关请求
- 保存到 `iframe_requests_intercept.json` 文件

#### 方法B：浏览器开发者工具手动监听

1. **启用 iframe 请求显示**：
   - Chrome/Edge: Network 面板 → ⚙️ 设置 → 勾选 "Show all frames"
   - Firefox: Network 面板 → ⚙️ 设置 → 勾选 "Show all frames"

2. **过滤和搜索**：
   - 在 Filter 框中输入：`api` 或 `jiexi` 或 `parse`
   - 按 `Ctrl+F` 搜索：`token`、`m3u8`、`cachem3u8`

3. **等待动态请求**：
   - 页面加载后等待 10-30 秒
   - token 请求可能在页面加载后动态发起

#### 方法C：使用控制台拦截器

在浏览器控制台中执行以下代码：

```javascript
// 拦截所有 XMLHttpRequest
const originalOpen = XMLHttpRequest.prototype.open;
XMLHttpRequest.prototype.open = function(method, url, ...args) {
    if (url.includes('token') || url.includes('api') || url.includes('jiexi')) {
        console.log('🔑 [TOKEN相关]', method, url);
    }
    return originalOpen.apply(this, [method, url, ...args]);
};

// 拦截所有 Fetch 请求
const originalFetch = window.fetch;
window.fetch = function(...args) {
    const url = args[0];
    if (typeof url === 'string' && (url.includes('token') || url.includes('api'))) {
        console.log('🔑 [TOKEN相关]', url);
    }
    return originalFetch.apply(this, args);
};
```

**详细指南**：参见 `IFRAME_REQUEST_INTERCEPT_GUIDE.md`

### 方向5：分析 hls.js 的 xhrSetup 配置（如果存在）

**方法**：
1. 在浏览器控制台中检查 Hls 实例的配置
2. 查看是否有 `xhrSetup` 回调函数
3. 如果有，分析该回调函数是否添加了 token 参数

**代码示例**：
```javascript
// 在浏览器控制台中执行
var hls = new Hls();
console.log(hls.config.xhrSetup);  // 查看是否有 xhrSetup 配置

// 如果有 xhrSetup，可以查看其实现
if (hls.config.xhrSetup) {
    console.log(hls.config.xhrSetup.toString());
}
```

**可能性**：
- 如果存在 `xhrSetup`，token 可能在这里动态添加
- 但根据代码分析，更可能是在调用 `hls.loadSource()` 之前就已经添加到 URL

---

## 📝 总结

### 反混淆工具的效果

✅ **成功解码**：
- 十六进制字符串已解码（如 `'\x6f\x70\x65\x6e'` → `'open'`）
- 可以搜索到 `m3u8`、`token`、`XMLHttpRequest` 等关键字
- 代码可读性大幅提升

⚠️ **限制**：
- 变量名仍然是混淆的（如 `_0x2de0a3`、`_0x55660d`）
- 字符串拼接的URL可能无法直接搜索到
- 动态生成的字符串无法搜索

### 关键代码位置

| 文件 | 行号 | 内容 | 重要性 |
|------|------|------|--------|
| 7zlplayer.js | 2402-2420 | `video` 方法定义 | ⭐⭐⭐ |
| 7zlplayer.js | 2434 | m3u8格式检查 | ⭐⭐⭐ |
| 7zlplayer.js | 2440 | Hls.js加载m3u8 | ⭐⭐⭐ |
| 7zl.js | 256 | rc4解密调用 | ⭐⭐ |
| 7zl.js | 2807 | rc4函数定义 | ⭐⭐ |
| hls.min.js | 9217 | xhrSetup 回调调用 | ⭐ |
| hls.min.js | 9222 | XHR open 调用 | ⭐ |

### hls.min.js 分析结论

**✅ 已确认**：
- hls.min.js 是标准的 HLS.js 播放器库，不包含业务逻辑
- **hls.min.js 中没有 token 计算或添加逻辑**
- Hls.js 只是接收 m3u8 URL 并加载播放列表和片段

**📌 重要结论**：
- **token 的计算不在 hls.js 中**
- token 应该在调用 `hls.loadSource(url)` 之前就已经添加到 URL
- 可能的 token 添加位置：
  1. 在 `7zl.js` 中，调用 `YKQ.video()` 之前
  2. 在 `7zlplayer.js` 中，调用 `hls.loadSource()` 之前
  3. 通过 `xhrSetup` 钩子动态添加（需要外部配置，但可能性较小）

**🔍 下一步**：
- 重点分析 `7zl.js` 中调用 `video()` 方法的代码
- 查找 m3u8 URL 的生成和 token 添加逻辑

### 推荐方案

**优先使用网络监听方案**：
- 直接、可靠、无需理解复杂逻辑
- 已实现：`direct_jx2s0_parser.py`

**备选方案**：
- 继续分析代码，查找 `video` 方法的调用位置
- 分析iframe中的代码

