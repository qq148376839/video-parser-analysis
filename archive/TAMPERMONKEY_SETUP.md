# Tampermonkey 配置指南 - API参数分析工具

## 📋 问题说明

当使用 Tampermonkey 注入脚本时，页面代码中的 `debugger` 语句仍然会触发，导致无法正常使用 F12 调试。

## ✅ 解决方案

已创建增强版脚本 `analyze_api_params_v2_tampermonkey.js`，该版本：

1. **彻底禁用 debugger**：
   - Hook `Function` 构造函数，移除动态创建函数中的 `debugger`
   - Hook `eval`，移除 eval 代码中的 `debugger`
   - Hook `setTimeout`/`setInterval`，移除回调中的 `debugger`
   - Hook `requestAnimationFrame`
   - Hook `document.createElement`，拦截 script 标签创建
   - Hook `innerHTML`/`textContent` 设置器

2. **使用 `@run-at document-start`**：
   - 确保脚本在页面代码执行前运行
   - 在所有其他脚本加载前禁用 debugger

## 🚀 安装步骤

### 步骤 1: 安装 Tampermonkey

1. 访问 [Tampermonkey 官网](https://www.tampermonkey.net/)
2. 根据浏览器安装对应版本：
   - Chrome: [Chrome Web Store](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo)
   - Firefox: [Firefox Add-ons](https://addons.mozilla.org/en-US/firefox/addon/tampermonkey/)
   - Edge: [Edge Add-ons](https://microsoftedge.microsoft.com/addons/detail/tampermonkey/iikmkjmpaadaobahmlepeloendndfphd)

### 步骤 2: 创建新脚本

1. 点击浏览器工具栏中的 Tampermonkey 图标
2. 选择 **"创建新脚本"** 或 **"Dashboard"** → **"+"** 按钮

### 步骤 3: 配置脚本头部

将以下内容复制到脚本编辑器中：

```javascript
// ==UserScript==
// @name         API参数分析工具 - 增强反调试版
// @namespace    http://tampermonkey.net/
// @version      2.1
// @description  分析API参数生成逻辑，彻底禁用debugger干扰
// @author       You
// @match        *://*/*
// @run-at       document-start
// @grant        none
// ==/UserScript==
```

**重要配置说明**：

- `@match *://*/*`: 匹配所有网站（可根据需要修改为特定域名）
- `@run-at document-start`: **必须设置**，确保在页面代码执行前运行
- `@grant none`: 不需要特殊权限

### 步骤 4: 复制脚本代码

1. 打开 `analyze_api_params_v2_tampermonkey.js` 文件
2. 复制**整个文件内容**（包括脚本头部）
3. 粘贴到 Tampermonkey 脚本编辑器中
4. 点击 **"文件"** → **"保存"** 或按 `Ctrl+S`

### 步骤 5: 测试脚本

1. 访问目标网站
2. 打开浏览器控制台（F12）
3. 应该看到以下日志：
   ```
   🚀 开始分析API参数生成逻辑（Tampermonkey增强版）...
   ✅ Debugger已彻底禁用（Hook Function/eval/setTimeout等）
   ✅ Fetch已Hook
   ✅ XMLHttpRequest已Hook
   ...
   ```

4. **验证 debugger 是否被禁用**：
   - 在控制台输入：`debugger`
   - 应该不会触发断点
   - 或者尝试：`Function('debugger')()`
   - 也应该不会触发断点

## 🔧 高级配置

### 仅针对特定网站

如果只想在特定网站运行，修改 `@match` 行：

```javascript
// 示例：仅匹配 example.com
// @match        https://example.com/*
// @match        https://*.example.com/*

// 示例：匹配多个网站
// @match        https://site1.com/*
// @match        https://site2.com/*
```

### 调试模式

如果需要查看更详细的日志，可以在脚本中添加：

```javascript
// 在脚本开头添加
const DEBUG = true;

// 然后修改 console.log 为条件输出
if (DEBUG) {
    console.log('调试信息');
}
```

## 🐛 故障排除

### 问题 1: 脚本未运行

**症状**：控制台没有看到脚本日志

**解决方案**：
1. 检查 Tampermonkey 是否启用（图标应该是彩色的）
2. 检查脚本是否启用（Dashboard 中脚本状态应该是绿色）
3. 检查 `@match` 是否匹配当前网站
4. 刷新页面（Ctrl+F5 强制刷新）

### 问题 2: Debugger 仍然触发

**症状**：F12 打开后仍然遇到 debugger 断点

**解决方案**：
1. 确认脚本头部包含 `@run-at document-start`
2. 检查脚本是否在页面加载前执行（查看控制台日志时间）
3. 尝试手动调用：`_analyzeApiParams.disableDebugger()`
4. 如果问题持续，可能是页面使用了更高级的反调试技术

### 问题 3: API 调用未被捕获

**症状**：`_analyzeApiParams.showCalls()` 返回空数组

**解决方案**：
1. 确认目标 API URL 包含 `api/v` 或 `m1-a1.cloud`
2. 如果 API URL 不同，修改脚本中的匹配条件：
   ```javascript
   // 在 hookFetch 和 hookXHR 函数中修改
   if (typeof url === 'string' && (url.includes('你的API关键词'))) {
   ```
3. 触发一次 API 调用，然后检查控制台日志

### 问题 4: 脚本冲突

**症状**：页面功能异常或报错

**解决方案**：
1. 检查是否有其他 Tampermonkey 脚本冲突
2. 尝试禁用其他脚本，只保留当前脚本
3. 检查浏览器控制台的错误信息

## 📖 使用方法

脚本加载后，可以使用以下命令：

```javascript
// 查看所有捕获的API调用
_analyzeApiParams.showCalls()

// 提取URL参数
_analyzeApiParams.extractParams('https://example.com/api/v1?param=value')

// 搜索代码中的关键词
_analyzeApiParams.searchCode('z=')

// 分析z参数
_analyzeApiParams.analyzeZ()

// 分析s1ig参数
_analyzeApiParams.analyzeS1ig()

// 保存数据到localStorage
_analyzeApiParams.save()

// 从localStorage加载数据
_analyzeApiParams.load()

// 重新禁用debugger（如果遇到问题）
_analyzeApiParams.disableDebugger()
```

## 🔍 工作原理

### Debugger 禁用机制

1. **Function 构造函数 Hook**：
   - 拦截所有通过 `new Function()` 或 `Function()` 创建的函数
   - 在函数体字符串中移除 `debugger` 语句

2. **Eval Hook**：
   - 拦截所有 `eval()` 调用
   - 移除代码字符串中的 `debugger` 语句

3. **定时器 Hook**：
   - 拦截 `setTimeout` 和 `setInterval`
   - 移除字符串回调中的 `debugger`
   - 包装函数回调，捕获可能的 debugger 异常

4. **DOM Hook**：
   - 拦截 `document.createElement('script')`
   - 拦截 script 标签的 `innerHTML`/`textContent` 设置
   - 移除其中的 `debugger` 语句

### 执行时机

- `@run-at document-start` 确保脚本在 DOM 构建前执行
- 所有 Hook 在页面代码加载前完成设置
- 延迟执行的函数会等待相应 API 可用后再执行

## 📝 注意事项

1. **性能影响**：Hook 多个函数可能略微影响性能，但通常可以忽略
2. **兼容性**：脚本兼容现代浏览器（Chrome、Firefox、Edge）
3. **更新**：如果页面更新了反调试技术，可能需要更新脚本
4. **安全性**：脚本仅在本地运行，不会发送数据到外部服务器

## 🆘 获取帮助

如果遇到问题：

1. 检查浏览器控制台的错误信息
2. 确认脚本版本是最新的（v2.1）
3. 尝试在控制台手动调用 `_analyzeApiParams.disableDebugger()`
4. 检查 Tampermonkey Dashboard 中的脚本状态

---

**版本**: 2.1  
**最后更新**: 2024-12-08  
**兼容性**: Chrome 90+, Firefox 88+, Edge 90+

