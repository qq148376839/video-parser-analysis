# jx.2s0.cn Token 分析脚本使用说明

## 📋 功能说明

本脚本用于分析 `jx.2s0.cn` 视频解析网站中 m3u8 请求的 token 生成方式。

**目标URL**: `https://jx.2s0.cn/player/?url=https://v.youku.com/v_show/id_XMTA0MTc5NzI4.html`

**分析目标**: 找到请求 m3u8 链接时 token 的生成逻辑

## 🔧 使用方法

### 1. 安装依赖

确保已安装所需依赖：

```bash
pip install playwright pycryptodome requests
playwright install chromium
```

### 2. 运行分析脚本

```bash
python analyze_jx2s0_token.py
```

或使用快捷运行脚本：

```bash
python run_analyze_jx2s0_token.py
```

## 📊 脚本功能

### 核心功能

1. **独立浏览器启动**
   - 使用独立Chrome实例，避免被检测
   - 通过CDP协议连接，更接近真实浏览器

2. **网络请求监听**
   - 监听所有网络请求
   - 自动识别m3u8请求和token参数
   - 记录请求头和响应信息

3. **JavaScript代码分析**
   - 分析页面中的JavaScript代码
   - 提取token相关的函数定义
   - 查找window对象中的token相关变量

4. **Token生成逻辑提取**
   - 尝试执行常见的token生成函数
   - 提取函数代码
   - 分析token的生成流程

### 输出结果

脚本会生成 `jx2s0_token_analysis.json` 文件，包含：

- **m3u8_urls**: 发现的m3u8 URL和对应的token
- **network_requests**: 所有网络请求记录
- **js_functions**: 发现的JavaScript函数
- **token_generation_logic**: token生成逻辑

## 🔍 分析流程

```
1. 启动独立Chrome浏览器实例
   ↓
2. 设置网络请求监听器
   ↓
3. 访问目标页面
   ↓
4. 等待页面加载和视频初始化
   ↓
5. 等待m3u8请求
   ↓
6. 分析页面JavaScript代码
   ↓
7. 提取token生成逻辑
   ↓
8. 输出分析结果
```

## 📝 注意事项

1. **浏览器路径**: 脚本会自动查找Chrome浏览器路径，如果找不到会报错
2. **等待时间**: 脚本会等待足够的时间让页面加载和m3u8请求发生
3. **资源清理**: 脚本会自动清理临时文件和浏览器进程
4. **错误处理**: 包含完善的错误处理机制

## 🎯 预期结果

脚本运行后，你应该能看到：

1. ✅ 发现的m3u8 URL和token
2. ✅ token相关的网络请求
3. ✅ JavaScript中的token生成函数
4. ✅ token生成逻辑的代码片段

## 🔧 自定义配置

如果需要分析其他URL，可以修改 `analyze_jx2s0_token.py` 中的 `target_url`：

```python
self.target_url = "https://jx.2s0.cn/player/?url=YOUR_VIDEO_URL"
```

## 📚 相关文件

- `analyze_jx2s0_token.py` - 主分析脚本
- `run_analyze_jx2s0_token.py` - 快捷运行脚本
- `jx2s0_token_analysis.json` - 分析结果（运行后生成）
- `TOKEN_GENERATION_ANALYSIS.md` - 之前的token分析报告

## 🐛 故障排除

### 问题1: Chrome浏览器未找到

**解决方案**: 手动指定Chrome路径

```python
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
chrome_process, debug_port, user_data_dir = launch_chrome(chrome_path=chrome_path)
```

### 问题2: 未找到m3u8请求

**可能原因**:
- 页面加载时间过长
- 视频需要用户交互才能加载
- 网站有反爬虫机制

**解决方案**: 增加等待时间或手动交互

### 问题3: 无法提取token生成逻辑

**可能原因**:
- token生成逻辑在服务器端
- JavaScript代码被混淆
- token通过其他方式生成（如WebSocket）

**解决方案**: 查看网络请求的请求头，可能token在请求头中

## 📖 开发规则遵循

本脚本严格遵循项目开发规则：

- ✅ 使用独立浏览器实例 (`/use-standalone-browser`)
- ✅ 添加反爬虫脚本 (`/add-stealth-script`)
- ✅ 完善的错误处理 (`/error-handling-pattern`)
- ✅ 资源清理机制

## 🔗 相关资源

- [Playwright文档](https://playwright.dev/python/)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [视频解析网站逆向分析指南](.cursorrules)

