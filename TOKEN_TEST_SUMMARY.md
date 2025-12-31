# Token 测试总结 - 使用 final_direct_parser_v2.py 的解密逻辑

## 📋 测试目标

使用 `final_direct_parser_v2.py` 中的解密逻辑来测试 jx.2s0.cn 的 token 生成方式。

## 🔑 解密逻辑（来自 final_direct_parser_v2.py）

### 密钥生成
```python
key_str = '2890' + uid + 'tB959C'
key_bytes = key_str.encode('utf-8')

# 方式1: MD5哈希（16字节）
key = hashlib.md5(key_bytes).digest()

# 方式2: SHA256哈希（前16/24/32字节）
key = hashlib.sha256(key_bytes).digest()[:16]
```

### IV生成
```python
iv_str = '2F131BE91247866E'

# 方式1: UTF-8编码（16字节）
iv = iv_str.encode('utf-8')

# 方式2: 十六进制解析+填充
iv = bytes.fromhex(iv_str).ljust(16, b'\0')

# 方式3: 重复填充
iv = (bytes.fromhex(iv_str) * 2)[:16]
```

### 解密流程
```python
# AES-CBC解密
cipher = AES.new(key, AES.MODE_CBC, iv)
decrypted = cipher.decrypt(encrypted_data)

# 移除PKCS7填充
decrypted_unpadded = unpad(decrypted, AES.block_size)
result = decrypted_unpadded.decode('utf-8')
```

## 🎯 Token 信息

**Token值**:
```
d3d376466714168607a696b254956444b496d653377613c6751386134663357714a42525358415f695947764648393b6b4a6545694545433f4d65376c646152513a7a6257303757627f69745a75535352445645305a5b6e4
```

**特征**:
- 长度: 176 字符（88 字节）
- 格式: 十六进制字符串
- 位置: m3u8 URL 的查询参数

## 🔍 测试方案

### 方案1: 解密 Token（反向操作）

假设 token 是加密后的数据，尝试使用相同的密钥和IV解密：

```python
token_bytes = bytes.fromhex(token)

# 尝试不同的 uid 值
uid_candidates = [None, 'test', '12345', ...]

for uid in uid_candidates:
    key_str = '2890' + (uid or '') + 'tB959C'
    key = hashlib.md5(key_str.encode()).digest()
    
    iv = '2F131BE91247866E'.encode('utf-8')
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(token_bytes)
    
    # 检查解密结果
    if decrypted.startswith(b'http') or b'm3u8' in decrypted:
        print("解密成功！")
```

### 方案2: 加密生成 Token（正向操作）

假设 token 是通过加密某些数据生成的，尝试加密可能的输入数据：

```python
# 可能的输入数据
input_data_candidates = [
    config.url,      # 从 /admin/api.php 响应中获取
    config.id,       # 从 /admin/api.php 响应中获取
    video_url,       # 原始视频URL
    config.url + config.id,  # 组合数据
]

for data in input_data_candidates:
    data_bytes = pad(data.encode('utf-8'), AES.block_size)
    
    key = hashlib.md5(('2890' + uid + 'tB959C').encode()).digest()
    iv = '2F131BE91247866E'.encode('utf-8')
    
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(data_bytes)
    
    encrypted_hex = encrypted.hex()
    
    if encrypted_hex == token:
        print("生成成功！")
```

## 📝 关键问题

1. **UID 来源**: 
   - 需要从 `/admin/api.php` 响应中获取
   - 可能是 `config.id` 或 `config.uid`

2. **输入数据**:
   - Token 可能是加密后的 `config.url`
   - Token 可能是加密后的 `config.id`
   - Token 可能是加密后的组合数据

3. **加密方向**:
   - Token 可能是**加密后的数据**（需要解密）
   - Token 可能是**签名数据**（不需要解密，用于验证）

## 🚀 下一步行动

### 1. 获取 API 响应

运行 `capture_admin_api_response.py` 获取 `/admin/api.php` 的完整响应：

```bash
python capture_admin_api_response.py
```

### 2. 提取关键数据

从 API 响应中提取：
- `config.url`（加密的URL）
- `config.id` 或 `config.uid`
- 其他可能的字段

### 3. 测试解密逻辑

使用提取的数据测试 token 的生成/解密：

```python
# 测试脚本: test_jx2s0_token_with_decrypt_logic.py
python test_jx2s0_token_with_decrypt_logic.py
```

### 4. 验证结果

如果解密成功，验证解密后的数据是否：
- 是有效的 URL
- 包含 m3u8 相关信息
- 可以用于生成最终的 m3u8 链接

## 💡 推测

基于 `final_direct_parser_v2.py` 的逻辑，最可能的情况是：

1. **Token 是加密后的数据**:
   - 输入: `config.url` 或 `config.id` 或组合数据
   - 密钥: `MD5('2890' + uid + 'tB959C')`
   - IV: `'2F131BE91247866E'` (UTF-8编码)
   - 算法: AES-CBC
   - 输出: Token（十六进制字符串）

2. **Token 用于验证**:
   - Token 可能是签名，用于验证请求的合法性
   - 服务器端使用相同的逻辑生成 token，然后验证

3. **Token 包含信息**:
   - Token 可能包含加密后的 m3u8 URL
   - 解密后可以直接使用或进一步处理

## 📊 测试脚本

已创建以下测试脚本：

1. **`test_jx2s0_token_with_decrypt_logic.py`**: 完整测试脚本
   - 获取 API 响应
   - 测试 token 解密
   - 测试 token 生成

2. **`simple_token_test.py`**: 简化测试脚本
   - 直接测试 token 解密
   - 不依赖 API 响应

3. **`capture_admin_api_response.py`**: API 响应捕获脚本
   - 专门捕获 `/admin/api.php` 的响应
   - 保存响应内容到 JSON 文件

## ✅ 建议

1. **优先执行**: 运行 `capture_admin_api_response.py` 获取 API 响应
2. **分析响应**: 查看响应中是否包含 `uid`、`id`、`url` 等字段
3. **测试解密**: 使用提取的数据测试 token 解密逻辑
4. **验证结果**: 确认解密后的数据是否有效

---

**最后更新**: 2024-12-19
**相关文件**: 
- `final_direct_parser_v2.py` - 解密逻辑参考
- `test_jx2s0_token_with_decrypt_logic.py` - 完整测试脚本
- `simple_token_test.py` - 简化测试脚本


