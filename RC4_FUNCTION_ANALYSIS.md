# rc4 函数分析 - 判断是否用于 token 生成

## 📋 分析结果总结

### 文件信息
- **分析文件**: `downloaded_js/7zl.js`
- **文件大小**: 130,758 字符
- **混淆工具**: jsjiami.com.v7

### 发现的关键信息

#### 1. rc4 函数定义
- **位置**: 第 2814 行（位置 126911）
- **函数签名**: `function rc4(_0x2262fd, _0x112647, _0x1bd18b)`
- **参数数量**: 3 个参数
- **函数类型**: 解密函数（RC4算法）

#### 2. ConFig 对象使用
找到 4 处 ConFig 对象的使用：

**config['id'] 使用（3处）**:
- 位置 40146, 40165, 40293（第418-419行）
- **关键代码**:
  ```javascript
  if(config['id'], '') a=config['id'], b=config[...];
  YKQ['id'] = _0x35b4de['vboWg'](_0x35b4de[...](a, ' P'), b);
  ```
- **用途**: 生成 `YKQ['id']`，格式为 `a + ' P' + b`，其中 `a` 是 `config['id']`

**config['url'] 使用（1处）**:
- 位置 74858（第1357行）
- **关键代码**:
  ```javascript
  YKQ['setCookie'](_0x4e4a10[...](_0x4e4a10['cbLbF'], config['url']), '', -0x1)
  ```
- **用途**: 设置 Cookie，使用 `config['url']`

## 🔍 关键分析

### rc4 函数是否用于 token 生成？

**结论**: **很可能不是用于 token 生成，而是用于解密 config.url**

**证据**:

1. **rc4 是解密函数**
   - RC4 是对称加密算法，可以用于加密和解密
   - 函数名是 `rc4`，通常用于解密操作

2. **参数分析**
   - `rc4(_0x2262fd, _0x112647, _0x1bd18b)` - 3个参数
   - 典型的 RC4 解密调用格式：`rc4(encrypted_data, key, mode)`
   - 第一个参数可能是加密的数据（如 `config.url`）
   - 第二个参数可能是密钥（如 `YKQ.id`）
   - 第三个参数可能是模式标志

3. **与已知逻辑的对比**
   - 根据 `final_direct_parser_v2.py`，解密逻辑是：
     ```python
     key = MD5('2890' + uid + 'tB959C')
     iv = '2F131BE91247866E'
     decrypted = AES.decrypt(config.url, key, iv)
     ```
   - 但这里使用的是 **RC4**，不是 AES
   - 说明 `7zl.js` 和 `final_direct_parser_v2.py` 可能使用不同的解密算法

4. **config['url'] 的使用**
   - `config['url']` 被用于设置 Cookie
   - 这可能是解密后的 URL
   - 如果 rc4 用于解密，那么调用可能是：`rc4(config.url, YKQ.id, 1)`

5. **YKQ['id'] 的生成**
   - `YKQ['id'] = config['id'] + ' P'`
   - 这个 `YKQ.id` 很可能就是 RC4 解密的密钥
   - 与 `final_direct_parser_v2.py` 中的 `'2890' + uid + 'tB959C'` 类似

## 💡 推测的调用流程

基于分析，推测的调用流程：

```
1. 获取 ConFig 对象
   ↓
   config.url = "加密的URL"（Base64编码）
   config.id = "用户ID"
   
2. 生成密钥
   ↓
   YKQ.id = config.id + " P"
   （或可能是其他方式生成密钥）
   
3. RC4 解密 config.url
   ↓
   decrypted_url = rc4(config.url, YKQ.id, 1)
   
4. 使用解密后的 URL
   ↓
   - 设置 Cookie
   - 加载视频
   - 生成 m3u8 URL
```

## 🎯 Token 生成的可能位置

如果 rc4 **不是**用于 token 生成，那么 token 生成可能在：

1. **7zlplayer.js 中**
   - 7zlplayer.js 是播放器主文件
   - 可能包含 token 生成逻辑
   - 但目前未找到加密函数

2. **服务器端生成**
   - Token 可能由服务器端生成
   - 客户端只是使用 token
   - 通过 API 调用获取 token

3. **其他 JavaScript 文件**
   - 可能在其他 JS 文件中
   - 需要分析所有下载的 JS 文件

## 📝 下一步行动

### 1. 提取 rc4 函数的完整代码

需要查看 rc4 函数的完整实现，确认：
- 函数的具体逻辑
- 参数的含义
- 返回值是什么

### 2. 查找 rc4 函数的调用位置

需要找到所有调用 `rc4()` 的地方，查看：
- 传入的参数是什么
- 返回值如何使用
- 是否与 token 相关

### 3. 分析 7zlplayer.js

虽然未找到加密函数，但需要：
- 查找 token 相关的字符串
- 查找 m3u8 URL 的构造
- 查找 cachem3u8 相关的代码

### 4. 对比分析

对比 `7zl.js` 和 `final_direct_parser_v2.py`：
- 确认是否使用相同的解密算法
- 如果不同，理解为什么不同
- 找到 token 生成的真正位置

## 🔧 建议的分析方法

### 方法1: 提取 rc4 函数完整代码

```python
# 读取文件
with open('downloaded_js/7zl.js', 'r') as f:
    code = f.read()

# 查找 rc4 函数（从位置 126911 开始）
# 提取函数体（需要匹配大括号）
```

### 方法2: 在浏览器中调试

1. 打开解析网站
2. 在浏览器控制台中执行：
   ```javascript
   // 查看 rc4 函数
   console.log(rc4.toString());
   
   // 查看 ConFig 对象
   console.log(window.ConFig);
   
   // 查看 YKQ 对象
   console.log(window.YKQ);
   
   // 尝试调用 rc4
   // rc4(config.url, YKQ.id, 1)
   ```

### 方法3: 搜索关键字符串

搜索以下字符串（包括混淆后的形式）：
- `cachem3u8`
- `Cache/LZ`
- `token`
- `m3u8`

## 📊 总结

### rc4 函数的用途

**最可能**: 用于**解密 config.url**，而不是生成 token

**理由**:
1. rc4 是解密函数
2. 参数格式符合解密调用
3. config['url'] 被使用，可能是解密后的结果
4. YKQ['id'] 可能是密钥

### Token 生成的位置

**可能位置**:
1. 服务器端生成（通过 API）
2. 7zlplayer.js 中（但未找到加密函数）
3. 其他 JavaScript 文件中

### 建议

1. **优先分析 rc4 函数的完整代码**
2. **查找 rc4 函数的所有调用位置**
3. **分析调用上下文，确认是否与 token 相关**
4. **如果 rc4 不是用于 token，继续查找 token 生成的位置**

---

**相关文件**:
- `7zlplayer_analysis.json` - 分析结果
- `downloaded_js/7zl.js` - 源文件
- `final_direct_parser_v2.py` - 参考解密逻辑

**最后更新**: 2024-12-19


