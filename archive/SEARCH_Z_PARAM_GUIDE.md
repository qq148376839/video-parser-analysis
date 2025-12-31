# z参数生成逻辑搜索指南

## 📋 问题说明

z参数是一个32位的MD5哈希值，用于API调用。需要找到它的生成逻辑。

**已知信息**:
- z参数格式: 32位十六进制字符串（MD5格式）
- 示例值: `4bbcd9c68c6625b5432721b6290ec694`
- API调用: `https://m1-a1.cloud.nnpp.vip:2223/api/v/?z=...`

## 🔍 搜索策略

### 方法1: 使用浏览器开发者工具全局搜索（推荐⭐）

这是最直接有效的方法：

1. **打开浏览器开发者工具**
   - 按 `F12` 或 `Ctrl+Shift+I`（Windows）
   - 或 `Cmd+Option+I`（Mac）

2. **打开Sources标签页**
   - 点击 "Sources" 标签

3. **打开全局搜索**
   - 按 `Ctrl+Shift+F`（Windows）
   - 或 `Cmd+Option+F`（Mac）

4. **搜索关键词**
   ```
   # 搜索z参数值（如果已知）
   4bbcd9c68c6625b5432721b6290ec694
   
   # 搜索z参数赋值
   z=
   z:
   
   # 搜索MD5相关
   md5
   MD5
   
   # 搜索API调用
   api/v
   m1-a1.cloud
   ```

5. **过滤Chrome扩展文件**
   - 在搜索结果中，忽略 `chrome-extension://` 开头的文件
   - 重点关注网站自己的JS文件，如：
     - `https://m1-z2.cloud.nnpp.vip:2223/static/js/main.1336e445.js`
     - `https://m1-cn-201.cloud.nnpp.vip:2223/z1/js/h-1-6.js`

6. **分析找到的代码**
   - 点击搜索结果，跳转到代码位置
   - 查看上下文，理解z参数的生成逻辑
   - 设置断点，观察z参数的生成过程

### 方法2: 使用Python脚本自动搜索

运行 `search_z_param_in_js.py` 脚本：

```bash
python archive/search_z_param_in_js.py
```

脚本会：
1. 从 `captured_api_params.json` 读取z参数值
2. 下载网站JS文件
3. 搜索z参数相关代码
4. 保存结果到 `z_param_search_results.json`

### 方法3: 使用增强版捕获脚本

运行 `capture_and_analyze_js.py` 脚本：

```bash
python archive/capture_and_analyze_js.py
```

脚本会：
1. 使用Playwright打开页面
2. 捕获所有执行的JavaScript代码
3. 分析z参数生成逻辑
4. 保存结果到 `z_param_analysis_results.json`

## 🎯 重点关注的代码模式

### 模式1: z参数直接赋值
```javascript
z = "4bbcd9c68c6625b5432721b6290ec694"
var z = "4bbcd9c68c6625b5432721b6290ec694"
const z = "4bbcd9c68c6625b5432721b6290ec694"
```

### 模式2: z参数通过MD5计算
```javascript
z = md5(something)
z = MD5(something)
z = something.md5()
```

### 模式3: z参数在URL中
```javascript
fetch("https://m1-a1.cloud.nnpp.vip:2223/api/v/?z=...")
"api/v/?z=" + z
```

### 模式4: z参数在函数中生成
```javascript
function generateZ() {
    // ... 生成逻辑
    return z;
}
```

## 📝 分析步骤

### 步骤1: 找到z参数出现的位置

使用全局搜索找到所有z参数出现的位置。

### 步骤2: 分析上下文

查看z参数出现位置的上下文代码：
- 前面几行：z参数是如何生成的？
- 后面几行：z参数是如何使用的？

### 步骤3: 设置断点

在z参数生成的位置设置断点：
1. 点击行号左侧，设置断点
2. 刷新页面
3. 当代码执行到断点时，观察变量值
4. 使用 `F10`（单步跳过）或 `F11`（单步进入）逐步执行

### 步骤4: 追踪调用栈

在断点处：
1. 查看右侧的 "Call Stack"（调用栈）
2. 点击调用栈中的函数，查看调用链
3. 找到z参数的生成源头

### 步骤5: 提取生成逻辑

找到z参数的生成逻辑后：
1. 记录生成z参数的代码
2. 记录输入参数（如video_url、timestamp等）
3. 在Python中实现相同的逻辑

## 🔧 实用技巧

### 技巧1: 过滤文件类型

在全局搜索中，可以添加文件过滤：
- 只搜索 `.js` 文件
- 排除 `chrome-extension://` 文件

### 技巧2: 使用正则表达式搜索

在全局搜索中启用正则表达式：
- 搜索 `z\s*[:=]\s*` 找到所有z参数赋值
- 搜索 `md5\s*\(` 找到所有MD5函数调用

### 技巧3: 查看网络请求

在Network标签页中：
1. 找到API调用请求
2. 右键点击请求
3. 选择 "Copy" -> "Copy as cURL" 或 "Copy as fetch"
4. 查看请求的完整信息

### 技巧4: 使用Console调试

在Console中执行代码：
```javascript
// 查看全局变量
console.log(window.z)

// 调用函数
console.log(generateZ())

// 查看对象
console.log(JSON.stringify(someObject))
```

## 📊 常见z参数生成方式

### 方式1: MD5(video_url)
```javascript
z = md5(video_url)
```

### 方式2: MD5(video_url + timestamp)
```javascript
z = md5(video_url + Date.now())
```

### 方式3: MD5(video_url + secret)
```javascript
z = md5(video_url + "secret_key")
```

### 方式4: MD5(domain + video_url)
```javascript
z = md5(window.location.hostname + video_url)
```

### 方式5: 从服务器获取
```javascript
// 先请求获取z参数
fetch("https://m1-z2.cloud.nnpp.vip:2223/?r=...")
  .then(response => response.json())
  .then(data => {
    z = data.z;
  });
```

## 💡 下一步

找到z参数生成逻辑后：

1. **在Python中实现**
   - 如果使用MD5，使用 `hashlib.md5()`
   - 如果包含时间戳，使用 `time.time()`
   - 如果从服务器获取，使用 `requests.get()`

2. **测试验证**
   - 使用捕获的z参数值验证
   - 确保生成的z参数与捕获的一致

3. **集成到解析器**
   - 将z参数生成逻辑集成到视频解析器中
   - 实现自动生成z参数

## 🚨 注意事项

1. **Chrome扩展文件**
   - 忽略 `chrome-extension://` 开头的文件
   - 这些是浏览器扩展的代码，不是网站代码

2. **混淆代码**
   - 网站可能使用代码混淆
   - 变量名可能是 `a`、`b`、`c` 等
   - 需要仔细分析逻辑

3. **动态生成**
   - z参数可能是动态生成的
   - 每次请求可能不同
   - 需要找到生成规则，而不是固定值

4. **时间敏感性**
   - z参数可能包含时间戳
   - 需要实时生成，不能使用固定值

## 📚 相关文件

- `search_z_param_in_js.py` - 自动搜索JS文件中的z参数
- `capture_and_analyze_js.py` - 捕获并分析运行时JS代码
- `analyze_z_param_generation.py` - 分析z参数生成模式
- `capture_runtime_js.py` - 捕获运行时JavaScript代码

