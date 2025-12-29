# API参数分析脚本使用指南

## 问题：页面刷新后变量丢失

当页面刷新或导航到新页面时，JavaScript上下文会被重置，导致全局变量丢失。

## 解决方案

### 方法1: 使用Chrome Snippets（最推荐）

1. **打开Chrome DevTools** (F12)
2. **进入Sources标签页**
3. **点击左侧的"Snippets"**
4. **右键点击 → New snippet**
5. **命名**: `analyze_api_params`
6. **粘贴** `analyze_api_params_v2.js` 的内容
7. **保存** (Ctrl+S)
8. **右键点击snippet → Run** (或按Ctrl+Enter)

**优点**:
- 脚本会持久保存
- 可以在任何页面运行
- 不会因为页面刷新而丢失

### 方法2: 使用Console（页面加载后）

1. **打开目标页面**
2. **按F12打开开发者工具**
3. **等待页面完全加载**
4. **在Console中粘贴脚本**
5. **按Enter执行**

**注意**: 如果页面刷新，需要重新运行脚本。

### 方法3: 使用Chrome Overrides（高级）

1. **打开Chrome DevTools** (F12)
2. **进入Sources标签页**
3. **点击"Overrides"标签**
4. **选择本地文件夹**（用于保存覆盖的文件）
5. **允许访问**
6. **在Network标签页找到目标JS文件**
7. **右键 → Override content**
8. **修改文件内容**（添加我们的Hook代码）

### 方法4: 使用Bookmarklet（最简单）

创建一个书签，URL填入：

```javascript
javascript:(function(){
    var script=document.createElement('script');
    script.src='data:text/javascript;base64,'+btoa(`
        // 这里粘贴 analyze_api_params_v2.js 的内容
    `);
    document.head.appendChild(script);
})();
```

**注意**: 由于代码较长，建议使用方法1或2。

## 使用步骤

### 步骤1: 运行脚本

使用上述任一方法运行脚本。

### 步骤2: 刷新页面

刷新页面，脚本会自动捕获API调用。

### 步骤3: 查看结果

在Console中运行：

```javascript
// 查看所有API调用
_analyzeApiParams.showCalls()

// 分析z参数
_analyzeApiParams.analyzeZ()

// 分析s1ig参数
_analyzeApiParams.analyzeS1ig()

// 搜索特定关键词
_analyzeApiParams.searchCode('z=')
```

### 步骤4: 保存结果（防止丢失）

```javascript
// 保存到localStorage
_analyzeApiParams.save()

// 如果页面刷新，可以恢复
_analyzeApiParams.load()
```

## 分析参数生成逻辑

### 1. 查看Network标签页

1. **打开Network标签页**
2. **刷新页面**
3. **找到API请求**: `https://m1-a1.cloud.nnpp.vip:2223/api/v/`
4. **点击请求**
5. **查看Headers标签页**
   - 查看Request URL中的参数
   - 查看Request Headers

### 2. 查看Sources标签页

1. **打开Sources标签页**
2. **在左侧文件树中找到JS文件**
3. **搜索关键词**:
   - `z=`
   - `s1ig`
   - `api/v`
   - `e8e56ecaca35c6229baa93884b6b7323`

### 3. 使用Console搜索

```javascript
// 搜索所有脚本中的z参数
_analyzeApiParams.searchCode('z=')

// 搜索s1ig参数
_analyzeApiParams.searchCode('s1ig')

// 搜索API URL
_analyzeApiParams.searchCode('m1-a1.cloud')
```

### 4. 设置断点分析

1. **在Sources中找到参数生成的代码**
2. **设置断点**
3. **刷新页面**
4. **查看变量值**
5. **单步调试**

## 常见问题

### Q: 脚本运行后没有捕获到API调用？

A: 
1. 确保页面已完全加载
2. 刷新页面
3. 检查Network标签页，确认API请求确实存在
4. 尝试手动触发API调用

### Q: 页面刷新后变量丢失？

A: 
1. 使用 `_analyzeApiParams.save()` 保存
2. 使用 `_analyzeApiParams.load()` 恢复
3. 或者使用Chrome Snippets（方法1）

### Q: 如何找到参数生成代码？

A:
1. 在Network标签页查看请求的调用栈（Call Stack）
2. 在Sources中搜索关键词
3. 使用 `_analyzeApiParams.searchCode()` 搜索
4. 查看捕获的API调用的stack属性

### Q: Debugger仍然触发？

A:
1. 在Sources标签页点击"Deactivate breakpoints"按钮
2. 或按 `Ctrl+F8`
3. 脚本已经禁用了debugger，但某些网站可能有其他检测

## 下一步

找到参数生成逻辑后：

1. **记录参数生成规则**
2. **在Python脚本中实现相同的逻辑**
3. **测试验证**

## 示例：分析z参数

```javascript
// 1. 运行脚本
// 2. 刷新页面
// 3. 查看API调用
_analyzeApiParams.showCalls()

// 4. 分析z参数
_analyzeApiParams.analyzeZ()

// 5. 搜索相关代码
_analyzeApiParams.searchCode('z=')
_analyzeApiParams.searchCode('e8e56ecaca35c6229baa93884b6b7323')

// 6. 查看调用栈
const calls = _analyzeApiParams.showCalls()
if (calls.length > 0) {
    console.log('调用栈:', calls[0].stack)
}
```


