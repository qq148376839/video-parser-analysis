# iframe 网络请求拦截指南

## 📋 问题

在 F12 的 Network 面板中看不到 token 获取接口，可能是因为：
1. **请求在 iframe 中发起**：主窗口的 Network 面板默认不显示 iframe 的请求
2. **请求被混淆隐藏**：接口名称可能被混淆，不容易识别
3. **请求在页面加载后动态发起**：需要等待足够长时间才能捕获

---

## 🔧 方法1：使用 Playwright 自动监听（推荐）

### 脚本说明

已创建 `intercept_iframe_requests.py` 脚本，可以：
- ✅ 监听**所有 frame**（包括主页面和所有 iframe）的网络请求
- ✅ 自动识别 token 相关的请求
- ✅ 自动识别 m3u8 相关的请求
- ✅ 自动识别 API 请求
- ✅ 保存详细的请求和响应信息

### 使用方法

```bash
cd archive/jx2s0_analysis
python intercept_iframe_requests.py
```

### 脚本功能

1. **监听所有请求**：
   - 主页面请求
   - iframe 中的请求
   - 嵌套 iframe 的请求

2. **自动分类**：
   - 🔑 Token 相关请求（URL、请求头、POST 数据中包含 token）
   - 🎬 M3U8 相关请求（包含 .m3u8 或 cachem3u8）
   - 📡 API 请求（包含 api、jiexi、parse 等关键字）

3. **详细信息**：
   - 请求方法、URL、请求头、POST 数据
   - 响应状态、响应头、响应内容（如果包含 token/m3u8）
   - Frame 信息（哪个 iframe 发起的请求）

4. **结果保存**：
   - 控制台输出详细日志
   - 保存到 `iframe_requests_intercept.json` 文件

### 输出示例

```
🔑 [TOKEN相关请求] GET https://jx.2s0.cn/admin/api.php?id=xxx
   Frame: https://jx.2s0.cn/player/analysis.php?v=xxx
   POST数据: ...

🎬 [M3U8相关请求] GET https://cachem3u8.2s0.cn:8899/Cache/Ff/xxx.m3u8?token=xxx
   Frame: https://jx.2s0.cn/player/analysis.php?v=xxx
   Token参数: d3d315341476033443543795551335e6c...
```

---

## 🔧 方法2：浏览器开发者工具手动监听

### 步骤1：打开开发者工具

1. 访问解析页面：`https://jx.2s0.cn/player/?url=xxx`
2. 按 `F12` 打开开发者工具
3. 切换到 **Network** 面板

### 步骤2：启用 iframe 请求显示

**Chrome/Edge**：
1. 在 Network 面板中，点击右上角的 **⚙️ 设置图标**
2. 勾选 **"Show all frames"** 或 **"显示所有框架"**
3. 这样就能看到所有 iframe 的请求了

**Firefox**：
1. 在 Network 面板中，点击右上角的 **⚙️ 设置图标**
2. 勾选 **"Show third-party resources"** 和 **"Show all frames"**

### 步骤3：过滤和搜索

1. **过滤 API 请求**：
   - 在 Filter 框中输入：`api` 或 `jiexi` 或 `parse`
   - 或者使用 XHR 过滤器（只显示 AJAX 请求）

2. **搜索 token**：
   - 在 Network 面板中按 `Ctrl+F`（Windows）或 `Cmd+F`（Mac）
   - 搜索关键词：`token`、`m3u8`、`cachem3u8`

3. **查看请求详情**：
   - 点击请求，查看：
     - **Headers**：请求头、响应头
     - **Payload**：POST 数据
     - **Preview/Response**：响应内容

### 步骤4：监听动态请求

1. **清空网络日志**：
   - 点击 Network 面板左上角的 **🚫 清空按钮**

2. **等待页面加载**：
   - 页面加载后，等待 10-30 秒
   - token 请求可能在页面加载后动态发起

3. **检查所有请求**：
   - 滚动查看所有请求
   - 特别关注：
     - XHR/Fetch 请求（蓝色图标）
     - 包含 `api`、`jiexi`、`parse` 的请求
     - 响应中包含 `token` 或 `m3u8` 的请求

---

## 🔧 方法3：使用浏览器控制台拦截

### 在控制台中执行以下代码

```javascript
// 拦截所有 XMLHttpRequest
(function() {
    const originalOpen = XMLHttpRequest.prototype.open;
    const originalSend = XMLHttpRequest.prototype.send;
    
    XMLHttpRequest.prototype.open = function(method, url, ...args) {
        this._url = url;
        console.log('🔍 XHR请求:', method, url);
        
        // 检查是否是 token 相关请求
        if (url.includes('token') || url.includes('api') || url.includes('jiexi') || url.includes('parse')) {
            console.log('🔑 [TOKEN相关]', method, url);
        }
        
        // 检查是否是 m3u8 相关请求
        if (url.includes('m3u8') || url.includes('cachem3u8')) {
            console.log('🎬 [M3U8相关]', method, url);
        }
        
        return originalOpen.apply(this, [method, url, ...args]);
    };
    
    XMLHttpRequest.prototype.send = function(...args) {
        this.addEventListener('load', function() {
            if (this.responseURL.includes('token') || this.responseURL.includes('m3u8')) {
                console.log('📥 [响应]', this.status, this.responseURL);
                try {
                    const response = JSON.parse(this.responseText);
                    console.log('   响应内容:', response);
                } catch (e) {
                    console.log('   响应内容:', this.responseText.substring(0, 500));
                }
            }
        });
        return originalSend.apply(this, args);
    };
    
    console.log('✅ XHR拦截器已安装');
})();

// 拦截所有 Fetch 请求
(function() {
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        const url = args[0];
        console.log('🔍 Fetch请求:', url);
        
        if (typeof url === 'string') {
            if (url.includes('token') || url.includes('api') || url.includes('jiexi')) {
                console.log('🔑 [TOKEN相关]', url);
            }
            if (url.includes('m3u8') || url.includes('cachem3u8')) {
                console.log('🎬 [M3U8相关]', url);
            }
        }
        
        return originalFetch.apply(this, args).then(response => {
            if (response.url.includes('token') || response.url.includes('m3u8')) {
                response.clone().text().then(text => {
                    console.log('📥 [Fetch响应]', response.status, response.url);
                    console.log('   响应内容:', text.substring(0, 500));
                });
            }
            return response;
        });
    };
    
    console.log('✅ Fetch拦截器已安装');
})();
```

### 使用方法

1. 打开解析页面
2. 按 `F12` 打开开发者工具
3. 切换到 **Console** 面板
4. 粘贴上面的代码并回车执行
5. 刷新页面或等待页面加载
6. 观察控制台输出，查找 token 相关的请求

---

## 🔧 方法4：使用 Playwright 监听特定 iframe

如果需要监听特定 iframe 的请求，可以使用以下代码：

```python
async def intercept_specific_iframe(page: Page, iframe_url_pattern: str):
    """监听特定 iframe 的请求"""
    
    async def handle_request(request):
        frame = request.frame
        if frame and iframe_url_pattern in frame.url:
            print(f"🔍 iframe请求: {request.method} {request.url}")
            print(f"   Frame URL: {frame.url}")
            if request.post_data:
                print(f"   POST数据: {request.post_data}")
    
    # 监听所有 frame 的请求
    page.on('request', handle_request)
    
    # 监听新附加的 frame
    async def handle_frame_attached(frame: Frame):
        if iframe_url_pattern in frame.url:
            print(f"📦 发现目标iframe: {frame.url}")
            frame.on('request', handle_request)
    
    page.on('frameattached', handle_frame_attached)
    
    # 对已存在的 frames 也设置监听
    for frame in page.frames:
        if iframe_url_pattern in frame.url:
            frame.on('request', handle_request)
```

---

## 📊 分析结果

### 常见的 token 获取接口模式

根据经验，token 获取接口可能是：

1. **API 接口**：
   - `https://jx.2s0.cn/admin/api.php?id=xxx`
   - `https://jx.2s0.cn/api/getm3u8.php?url=xxx`
   - `https://jx.2s0.cn/api.php?action=gettoken&id=xxx`

2. **请求方式**：
   - GET 请求：`?id=xxx&url=xxx`
   - POST 请求：`{"id": "xxx", "url": "xxx"}`

3. **响应格式**：
   - JSON：`{"token": "xxx", "m3u8": "xxx"}`
   - 文本：直接返回 m3u8 URL（包含 token）

### 如何识别 token 接口

1. **时间顺序**：
   - token 接口通常在页面加载后 1-5 秒内调用
   - 在 m3u8 请求之前

2. **请求特征**：
   - 通常是 XHR/Fetch 请求
   - URL 中包含 `api`、`jiexi`、`parse`、`getm3u8` 等关键字
   - 请求参数中包含视频 URL 或 ID

3. **响应特征**：
   - 响应中包含 `token` 或 `m3u8` 字符串
   - 响应可能是 JSON 格式，包含 token 字段

---

## 🎯 推荐流程

1. **首先使用脚本自动监听**（方法1）：
   ```bash
   python intercept_iframe_requests.py
   ```
   - 自动捕获所有请求
   - 自动分类和过滤
   - 保存详细结果

2. **如果脚本没有捕获到，使用浏览器手动监听**（方法2）：
   - 启用 "Show all frames"
   - 过滤和搜索 token 相关请求

3. **使用控制台拦截器**（方法3）：
   - 在控制台执行拦截代码
   - 实时查看所有请求

4. **分析结果**：
   - 查看 `iframe_requests_intercept.json` 文件
   - 重点关注 token 相关请求
   - 分析请求参数和响应内容

---

## 📝 注意事项

1. **等待时间**：
   - token 请求可能在页面加载后几秒才发起
   - 建议等待至少 30 秒

2. **iframe 加载**：
   - iframe 可能延迟加载
   - 需要等待 iframe 完全加载

3. **请求顺序**：
   - 先调用配置接口（如 `/admin/api.php`）
   - 然后调用 token 接口
   - 最后请求 m3u8 文件

4. **跨域问题**：
   - 如果 iframe 是跨域的，可能无法直接访问其内容
   - 但网络请求仍然可以在 Network 面板中看到

---

## 🔍 调试技巧

1. **使用断点**：
   - 在 Network 面板中，右键点击请求 → "Copy" → "Copy as cURL"
   - 可以复制完整的请求命令

2. **查看调用栈**：
   - 在 Network 面板中，点击请求 → "Initiator" 标签
   - 可以看到是哪个 JavaScript 文件发起的请求

3. **保存 HAR 文件**：
   - 在 Network 面板中，右键 → "Save all as HAR"
   - 可以保存所有网络请求的详细信息

4. **使用代理工具**：
   - 使用 Fiddler、Charles 等代理工具
   - 可以捕获所有网络流量（包括 iframe）

---

## 📚 相关文件

- `intercept_iframe_requests.py` - 自动监听脚本
- `analyze_jx2s0_parser.py` - 完整的分析脚本
- `iframe_requests_intercept.json` - 监听结果（运行脚本后生成）

