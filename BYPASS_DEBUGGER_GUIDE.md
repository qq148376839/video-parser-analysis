# 绕过无限Debugger断点指南

## 问题描述

在浏览器F12开发者工具中打开页面时，会触发无限debugger断点，导致无法正常调试。

## 解决方案

### 方法1: 禁用断点（推荐）

1. **打开Chrome DevTools**
2. **进入Sources标签页**
3. **点击"Deactivate breakpoints"按钮**（或按 `Ctrl+F8`）
   - 图标是一个圆圈中间有斜线
   - 这会禁用所有断点，包括debugger语句

### 方法2: 条件断点

1. **找到触发debugger的代码行**
2. **右键点击行号**
3. **选择"Add conditional breakpoint"**
4. **输入条件**: `false` （这样断点永远不会触发）

### 方法3: 使用Console覆盖debugger

在Console中执行以下代码：

```javascript
// 方法1: 覆盖debugger函数
window.debugger = function() {};

// 方法2: 使用Object.defineProperty
Object.defineProperty(window, 'debugger', {
    get: function() { return function() {}; },
    configurable: true
});

// 方法3: 删除debugger
delete window.debugger;
```

### 方法4: 使用Chrome扩展

安装Chrome扩展来禁用debugger：
- **Disable JavaScript** (临时禁用JS)
- **JavaScript Toggle On and Off**

### 方法5: 修改源代码（本地调试）

如果需要在本地调试，可以：

1. **使用浏览器扩展拦截并修改响应**
   - Requestly
   - ModHeader
   - 自定义Chrome扩展

2. **使用代理工具**
   - Fiddler
   - Charles Proxy
   - mitmproxy

### 方法6: 使用Playwright/Puppeteer（自动化）

使用自动化工具时，可以在页面加载前注入代码：

```python
# Playwright示例
await page.add_init_script("""
    window.debugger = function() {};
    Object.defineProperty(window, 'debugger', {
        get: () => function() {},
        configurable: true
    });
""")
```

## 分析参数生成逻辑

### 步骤1: 禁用断点后分析

1. **禁用所有断点**（方法1）
2. **打开Network标签页**
3. **找到API请求**: `https://m1-a1.cloud.nnpp.vip:2223/api/v/`
4. **查看请求参数**: `z`, `jx`, `s1ig`

### 步骤2: 查找参数生成代码

在Console中搜索：

```javascript
// 搜索z参数
console.log('搜索z参数生成...');
// 在Sources中搜索: 'z=', 'z:', 'api/v'

// 搜索s1ig参数
console.log('搜索s1ig参数生成...');
// 在Sources中搜索: 's1ig', 's1ig='
```

### 步骤3: 使用断点分析（已禁用debugger后）

1. **在参数生成代码处设置断点**
2. **查看变量值**
3. **跟踪函数调用栈**

### 步骤4: Hook函数调用

在Console中执行：

```javascript
// Hook fetch请求
const originalFetch = window.fetch;
window.fetch = function(...args) {
    console.log('Fetch调用:', args);
    return originalFetch.apply(this, args);
};

// Hook XMLHttpRequest
const originalOpen = XMLHttpRequest.prototype.open;
XMLHttpRequest.prototype.open = function(method, url, ...args) {
    console.log('XHR请求:', method, url);
    return originalOpen.apply(this, [method, url, ...args]);
};
```

## 快速分析脚本

创建一个书签工具（Bookmarklet）：

```javascript
javascript:(function(){
    // 禁用debugger
    window.debugger = function() {};
    
    // Hook API调用
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        if (args[0].includes('api/v')) {
            console.log('🔍 API调用:', args[0]);
            console.log('📋 参数:', new URL(args[0]).searchParams);
        }
        return originalFetch.apply(this, args);
    };
    
    console.log('✅ Debugger已禁用，API调用已Hook');
})();
```

使用方法：
1. 复制上面的代码
2. 创建新书签，URL填入上面的代码
3. 在目标页面点击书签

## 常见参数生成模式

基于分析，参数可能是：

1. **z参数**: MD5/SHA256哈希值
   - 可能是: `MD5(video_url + timestamp + secret)`
   - 或: `SHA256(some_string)`

2. **s1ig参数**: 固定值或基于某些规则生成
   - 当前值: `11402`
   - 可能是固定值，也可能需要动态生成

## 下一步

1. 禁用断点后，使用Network标签页查看API请求
2. 在Sources中搜索参数生成代码
3. 使用Console Hook函数调用
4. 分析参数生成逻辑并实现到Python脚本中


