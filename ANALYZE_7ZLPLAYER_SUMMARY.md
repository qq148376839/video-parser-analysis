# 7zlplayer.js 解密逻辑分析总结

## 📋 文件信息

- **文件路径**: `downloaded_js/7zlplayer.js`
- **文件类型**: 混淆压缩的 JavaScript（单行文件）
- **混淆工具**: jsjiami.com.v7
- **文件大小**: 非常大（单行压缩）

## 🔍 分析策略

由于文件被严重混淆，需要采用以下策略：

### 1. 十六进制字符串解码

混淆代码使用 `\xXX` 格式的十六进制字符串，需要解码：
- `\x79\x72\x51\x78\x66` → 解码为实际字符串
- `\x32\x38\x39\x30` → `2890`（密钥的一部分）
- `\x32\x46\x31\x33\x31\x42\x45\x39\x31\x32\x34\x37\x38\x36\x36\x45` → `2F131BE91247866E`（IV值）

### 2. 关键模式搜索

需要搜索以下模式（包括混淆后的形式）：

#### Token 相关
- `token`（可能被混淆为 `\x74\x6f\x6b\x65\x6e`）
- `cachem3u8`
- `Cache/LZ`
- `.m3u8`

#### 加密相关
- `decrypt` / `encrypt`
- `AES`
- `CryptoJS`
- `md5` / `MD5`
- `sha256` / `SHA256`
- `rc4` / `RC4`

#### 密钥和IV
- `2890` + `tB959C`（密钥生成模式）
- `2F131BE91247866E`（IV值）
- `key` / `iv`

#### ConFig 相关
- `ConFig`
- `config`
- `url` / `id` / `uid`

## 🛠️ 分析工具

已创建 `analyze_7zlplayer_decrypt.py` 脚本，包含以下功能：

1. **十六进制字符串解码**
   - 提取所有 `\xXX` 格式的字符串
   - 解码为可读字符串
   - 识别关键字符串（如 `2890`, `tB959C`, `2F131BE91247866E`）

2. **解密函数查找**
   - 查找 `decrypt` / `encrypt` 函数
   - 查找 `AES` / `CryptoJS` 调用
   - 查找 `rc4` 函数

3. **Token 生成查找**
   - 查找 `token` 赋值
   - 查找 `cachem3u8` URL 构造
   - 查找 m3u8 URL 生成

4. **密钥和IV查找**
   - 查找 `2890` + `tB959C` 模式
   - 查找 `2F131BE91247866E` IV值
   - 查找 MD5 哈希调用

5. **ConFig 使用查找**
   - 查找 `ConFig.url` / `ConFig.id` / `ConFig.uid`
   - 查找 `config` 对象访问

## 📊 预期发现

基于 `final_direct_parser_v2.py` 的解密逻辑，预期在 `7zlplayer.js` 中找到：

### 1. 密钥生成逻辑
```javascript
// 预期模式（可能被混淆）
key_str = '2890' + uid + 'tB959C'
key = MD5(key_str)
// 或
key = SHA256(key_str).slice(0, 16)
```

### 2. IV 生成逻辑
```javascript
// 预期模式（可能被混淆）
iv = '2F131BE91247866E'.encode('utf-8')
// 或
iv = bytes.fromhex('2F131BE91247866E').ljust(16, '\0')
```

### 3. AES 解密逻辑
```javascript
// 预期模式（可能被混淆）
decrypted = AES.decrypt(encrypted_url, key, iv)
// 或
decrypted = CryptoJS.AES.decrypt(encrypted_url, key, {iv: iv})
```

### 4. Token 生成逻辑
```javascript
// 预期模式（可能被混淆）
token = encrypt(config.url, key, iv)
// 或
token = generateToken(config.id, config.url)
```

## 🔧 使用方法

### 方法1: 直接运行分析脚本

```bash
python analyze_7zlplayer_decrypt.py
```

### 方法2: 手动搜索关键模式

使用 grep 搜索关键模式：

```bash
# 搜索十六进制字符串中的关键值
grep -o "\\x32\\x38\\x39\\x30" downloaded_js/7zlplayer.js  # 2890
grep -o "\\x32\\x46\\x31\\x33\\x31\\x42\\x45\\x39\\x31\\x32\\x34\\x37\\x38\\x36\\x36\\x45" downloaded_js/7zlplayer.js  # 2F131BE91247866E

# 搜索函数调用模式
grep -o "function.*decrypt" downloaded_js/7zlplayer.js
grep -o "\.decrypt\(" downloaded_js/7zlplayer.js
grep -o "AES\." downloaded_js/7zlplayer.js
```

## 📝 分析结果输出

分析脚本会生成以下文件：

1. **`7zlplayer_analysis.json`** - 完整的分析结果
   - 十六进制字符串解码结果
   - 解密函数列表
   - Token 生成模式
   - 加密函数调用
   - ConFig 使用情况
   - API 调用
   - 密钥/IV 模式

2. **`7zlplayer_key_snippets.json`** - 关键代码片段
   - 包含解密相关代码的上下文
   - 便于进一步分析

## 💡 分析建议

1. **优先查看解码后的字符串**
   - 查看 `hex_strings` 中解码后的字符串
   - 查找 `2890`, `tB959C`, `2F131BE91247866E` 等关键值

2. **关注解密函数**
   - 查看 `decrypt_functions` 中的函数定义
   - 分析函数参数和返回值

3. **分析 Token 生成**
   - 查看 `token_patterns` 中的模式
   - 理解 token 的构造方式

4. **检查密钥和IV**
   - 查看 `key_iv_patterns` 中的模式
   - 确认密钥和IV的生成方式

5. **对比 final_direct_parser_v2.py**
   - 将找到的模式与已知的解密逻辑对比
   - 确认是否使用相同的算法

## 🎯 下一步行动

1. **运行分析脚本**
   ```bash
   python analyze_7zlplayer_decrypt.py
   ```

2. **查看分析结果**
   - 打开 `7zlplayer_analysis.json`
   - 重点关注 `decrypt_functions` 和 `key_iv_patterns`

3. **提取关键代码**
   - 查看 `7zlplayer_key_snippets.json`
   - 分析关键代码片段的逻辑

4. **还原解密算法**
   - 根据找到的模式还原解密逻辑
   - 与 `final_direct_parser_v2.py` 的逻辑对比

5. **测试验证**
   - 使用还原的算法测试解密
   - 验证是否能正确生成 token

---

**相关文件**:
- `analyze_7zlplayer_decrypt.py` - 分析脚本
- `downloaded_js/7zlplayer.js` - 目标文件
- `final_direct_parser_v2.py` - 参考解密逻辑

**最后更新**: 2024-12-19


