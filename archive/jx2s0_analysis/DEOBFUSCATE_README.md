# JavaScript反混淆工具使用说明

## 📋 工具说明

本工具用于反混淆JavaScript文件，将混淆的代码还原为可读形式，方便搜索和分析。

### 功能

1. **解码十六进制字符串**：`'\x6f\x70\x65\x6e'` → `'open'`
2. **解码Unicode字符串**：`'\u006f'` → `'o'`
3. **解码八进制字符串**：`'\141'` → `'a'`
4. **搜索关键字**：在反混淆后的文件中搜索特定关键字

---

## 🚀 使用方法

### 方法1：反混淆文件

```bash
python deobfuscate_js.py
```

**输出**：
- `7zl_deobfuscated.js` - 反混淆后的7zl.js
- `7zlplayer_deobfuscated.js` - 反混淆后的7zlplayer.js

**用途**：
- 在反混淆后的文件中搜索关键字
- 更容易阅读和理解代码逻辑

---

### 方法2：直接搜索关键字（推荐）

```bash
python search_deobfuscated.py
```

**功能**：
- 自动反混淆文件
- 搜索常见关键字（m3u8、cachem3u8、Cache、token等）
- 显示匹配的行号和上下文
- 保存详细结果到 `search_results.txt`

**搜索的关键字**：
- `m3u8`
- `cachem3u8`
- `Cache`
- `token`
- `cachem3u8.2s0.cn`
- `8899`
- `Cache/Ff`
- `XMLHttpRequest`
- `fetch`
- `$.ajax`
- `config.url`
- `YKQ.video`
- `YKQ.player`
- `/admin/api.php`
- `rc4`
- `atob`
- `btoa`

---

## 📝 示例

### 示例1：反混淆单个文件

```python
from deobfuscate_js import JavaScriptDeobfuscator

deobfuscator = JavaScriptDeobfuscator()
output_file = deobfuscator.deobfuscate_file('7zl.js')
print(f"反混淆后的文件: {output_file}")
```

### 示例2：搜索特定关键字

```python
from search_deobfuscated import search_in_file

result = search_in_file('7zlplayer.js', ['m3u8', 'cachem3u8'], deobfuscate=True)
for keyword, matches in result['found'].items():
    print(f"找到 '{keyword}': {len(matches)} 处")
    for match in matches:
        print(f"  第 {match['line']} 行: {match['content']}")
```

---

## ⚠️ 注意事项

### 限制

1. **变量名仍然是混淆的**
   - 变量名如 `_0x87bd`、`_0xda7da8` 等不会被还原
   - 只有字符串字面量会被解码

2. **代码逻辑可能被重排**
   - 混淆工具可能重排了代码顺序
   - 需要结合上下文理解

3. **完全反混淆很困难**
   - 高度混淆的代码很难完全还原
   - 主要用于搜索关键字和分析

### 建议

1. **优先使用搜索功能**
   - `search_deobfuscated.py` 会自动反混淆并搜索
   - 可以直接找到关键代码位置

2. **结合浏览器调试**
   - 在浏览器中设置断点
   - 查看实际执行的代码

3. **使用网络监听**
   - 监听网络请求找到API调用
   - 比分析代码更直接

---

## 🔍 搜索技巧

### 搜索m3u8链接

```bash
# 在反混淆后的文件中搜索
grep -n "m3u8\|cachem3u8\|Cache" 7zlplayer_deobfuscated.js
```

### 搜索API调用

```bash
# 搜索XMLHttpRequest
grep -n "XMLHttpRequest\|fetch\|\.ajax" 7zlplayer_deobfuscated.js

# 搜索API端点
grep -n "api\.php\|jiexi\|parse" 7zl_deobfuscated.js
```

### 搜索关键函数

```bash
# 搜索rc4函数调用
grep -n "rc4\|atob\|btoa" 7zl_deobfuscated.js

# 搜索YKQ对象方法
grep -n "YKQ\.video\|YKQ\.player\|YKQ\.start" 7zl_deobfuscated.js
```

---

## 📊 输出示例

### search_deobfuscated.py 输出

```
============================================================
在JavaScript文件中搜索关键字
============================================================

搜索文件: 7zl.js
  反混淆中...
  ✅ 找到 'rc4': 5 处
  ✅ 找到 'atob': 3 处
  ❌ 未找到 'm3u8'
  ❌ 未找到 'cachem3u8'

搜索文件: 7zlplayer.js
  反混淆中...
  ✅ 找到 'XMLHttpRequest': 1 处
  ❌ 未找到 'm3u8'
  ❌ 未找到 'cachem3u8'

============================================================
搜索结果汇总
============================================================

📄 7zl.js:

  🔍 'rc4' - 找到 5 处:
    [1] 第 256 行:
        YKQ['video'](rc4(config['url'], YKQ['id'], 1));
    [2] 第 2807 行:
        function rc4(_0x2262fd, _0x112647, _0x1bd18b) {
    ...
```

---

## 🎯 使用场景

### 场景1：查找m3u8生成逻辑

```bash
python search_deobfuscated.py
# 查看 search_results.txt 中的结果
# 查找包含 m3u8、cachem3u8、Cache 的代码
```

### 场景2：查找API调用

```bash
python search_deobfuscated.py
# 在结果中查找 XMLHttpRequest、fetch、$.ajax
# 分析API调用的参数和响应
```

### 场景3：分析解密逻辑

```bash
python search_deobfuscated.py
# 查找 rc4、atob、btoa 的使用位置
# 分析解密流程
```

---

## 📌 总结

1. **反混淆工具**：`deobfuscate_js.py` - 反混淆JavaScript文件
2. **搜索工具**：`search_deobfuscated.py` - 自动反混淆并搜索关键字
3. **输出文件**：
   - `*_deobfuscated.js` - 反混淆后的JavaScript文件
   - `search_results.txt` - 搜索结果详情

**推荐使用**：`search_deobfuscated.py` - 一步完成反混淆和搜索

