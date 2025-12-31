# jx.2s0.cn Token 分析总结

## 📋 分析目标

分析 `jx.2s0.cn` 视频解析网站中 m3u8 请求的 token 生成方式。

**目标URL**: `https://jx.2s0.cn/player/?url=https://v.youku.com/v_show/id_XMTA0MTc5NzI4.html`

**m3u8 URL示例**:
```
https://cachem3u8.2s0.cn:8899/Cache/LZ/4e7a11f1eb74b1fbe7b5c6359d501c3d.m3u8?token=d3d376b2430527a424a613e4e6960775f4b286978765a59603a62315e416c4b48727f69473e6a7966793667783033744a66624f4b2c615a55776e666656695a7f41305a5e4c474a457e687942753033564776684234656e6
```

---

## 🔧 已创建的脚本

### 1. `analyze_jx2s0_token.py` - 基础分析脚本
- 使用独立Chrome浏览器实例
- 监听网络请求，自动识别m3u8请求和token
- 分析JavaScript代码，提取token相关函数
- 输出分析结果到JSON文件

**使用方法**:
```bash
python analyze_jx2s0_token.py
```

### 2. `deep_analyze_jx2s0_token.py` - 深度分析脚本
- 注入JavaScript监控代码
- 拦截XMLHttpRequest和fetch请求
- 监控URL构造过程
- 捕获API响应数据
- 更深入的token生成逻辑分析

**使用方法**:
```bash
python deep_analyze_jx2s0_token.py
```

### 3. `analyze_token_structure.py` - Token结构分析脚本
- 分析token的字符集、编码方式
- 分析token的模式和结构
- 推测token的生成方式
- 保存详细的分析结果

**使用方法**:
```bash
python analyze_token_structure.py
```

### 4. `analyze_token_direct.py` - 直接分析脚本（简化版）
- 直接分析已知的token
- 不依赖文件读取
- 快速分析token结构

**使用方法**:
```bash
python analyze_token_direct.py
```

---

## 📊 Token分析结果

### Token基本信息

- **长度**: 176 字符
- **格式**: 十六进制字符串（0-9, a-f）
- **字节长度**: 88 字节（十六进制解码后）

### Token结构特征

```
Token: d3d376b2430527a424a613e4e6960775f4b286978765a59603a62315e416c4b48727f69473e6a7966793667783033744a66624f4b2c615a55776e666656695a7f41305a5e4c474a457e687942753033564776684234656e6
```

**字符频率分析**:
- `6`: 18.8% (33次)
- `7`: 13.1% (23次)
- `4`: 12.5% (22次)
- `3`: 9.1% (16次)
- `5`: 9.1% (16次)

**前缀/后缀**:
- 前缀: `d3d376b243` (可能是标识符)
- 后缀: `84234656e6`

### 编码分析

1. **十六进制解码**: 成功，得到88字节的二进制数据
2. **UTF-8解码**: 失败（不是文本数据）
3. **Base64编码**: 可以编码，但原始格式是十六进制

### URL结构分析

```
https://cachem3u8.2s0.cn:8899/Cache/LZ/4e7a11f1eb74b1fbe7b5c6359d501c3d.m3u8?token={token}
```

- **域名**: `cachem3u8.2s0.cn:8899`
- **路径**: `/Cache/LZ/{hash}.m3u8`
- **Hash**: `4e7a11f1eb74b1fbe7b5c6359d501c3d` (32字符，可能是MD5)
- **Token**: 作为查询参数传递

---

## 🔍 Token生成方式推测

基于分析结果，token可能是以下几种方式之一：

### 方式1: 十六进制编码的加密数据 ⭐ (最可能)

**描述**: Token可能是某种加密算法（如AES、RC4）的结果，然后转换为十六进制字符串。

**步骤**:
1. 使用某种密钥和算法加密数据（可能是URL、时间戳、ID等）
2. 将加密后的二进制数据转换为十六进制字符串
3. 作为token使用

**证据**:
- Token是88字节的二进制数据（不是文本）
- 字符分布相对均匀，符合加密数据的特征
- 前缀`d3d3`可能是加密算法的标识或IV的一部分

### 方式2: 组合数据的哈希

**描述**: Token可能是多个数据组合后的哈希值。

**步骤**:
1. 组合多个数据（如：config.id + video_url + timestamp + 其他参数）
2. 对组合后的数据进行哈希（MD5/SHA1/SHA256）
3. 将哈希值转换为十六进制字符串
4. 作为token使用

**问题**: 88字节对于常见哈希算法来说太长（MD5=16字节，SHA1=20字节，SHA256=32字节）

### 方式3: 加密签名

**描述**: Token可能是使用密钥对数据进行签名后的结果。

**步骤**:
1. 使用密钥（可能是config.id或其他）对数据进行签名
2. 签名算法可能是HMAC-SHA256、HMAC-MD5等
3. 将签名结果转换为十六进制字符串
4. 作为token使用

**问题**: 88字节对于常见签名算法来说也偏长

### 方式4: 多层加密/编码

**描述**: Token可能是经过多层加密或编码的结果。

**步骤**:
1. 原始数据 → 第一层加密（如RC4）
2. 加密结果 → Base64编码或其他编码
3. 编码结果 → 第二层加密（如AES）
4. 最终结果 → 十六进制字符串

---

## 🎯 下一步分析建议

### 1. 深入JavaScript代码分析 ⭐ (优先)

**目标**: 找到token生成的实际代码

**方法**:
1. 使用 `deep_analyze_jx2s0_token.py` 脚本
2. 注入监控代码，捕获所有URL构造过程
3. 查找包含 `cachem3u8`、`token`、`m3u8` 的JavaScript代码
4. 分析API响应数据（`/admin/api.php`）与token的关系

**关键点**:
- 查找 `YKQ` 对象的方法
- 查找 `video()` 或 `play()` 方法的实现
- 查找URL构造的代码（字符串拼接、`concat`等）

### 2. 分析API响应数据

**目标**: 理解API响应与token生成的关系

**方法**:
1. 捕获 `/admin/api.php` 的响应
2. 分析 `config.url` 和 `config.id` 的作用
3. 尝试将 `config.url` 解密后的数据与token关联
4. 检查是否有其他API调用返回token

**关键字段**:
- `config.url`: Base64编码的加密URL
- `config.id`: 视频ID（如 `b664f44e3be2ad57fdb6`）

### 3. 尝试逆向token生成算法

**目标**: 通过多次请求分析token的变化规律

**方法**:
1. 多次访问同一视频URL，收集多个token
2. 分析token的变化规律（是否包含时间戳）
3. 尝试使用已知数据（config.id、video_url等）生成token
4. 测试不同的加密算法和密钥组合

### 4. 使用浏览器开发者工具手动分析

**目标**: 在浏览器中直接观察token生成过程

**方法**:
1. 打开浏览器开发者工具
2. 访问目标URL
3. 在Network标签中查找m3u8请求
4. 在Sources标签中搜索token相关代码
5. 在Console中执行JavaScript，尝试生成token

---

## 📝 已收集的数据

### 网络请求

- **总请求数**: 24个
- **m3u8相关请求**: 1个
- **token相关请求**: 1个

### JavaScript文件

- 发现 `tokenize` 函数（来自jQuery，不是我们要找的）
- 需要进一步分析播放器相关的JavaScript文件

### 监控数据

- 监控代码已注入，但需要更长时间运行才能捕获完整的生成过程

---

## 🔗 相关文件

### 分析脚本
- `analyze_jx2s0_token.py` - 基础分析脚本
- `deep_analyze_jx2s0_token.py` - 深度分析脚本
- `analyze_token_structure.py` - Token结构分析
- `analyze_token_direct.py` - 直接分析脚本

### 分析结果
- `jx2s0_token_analysis.json` - 基础分析结果
- `jx2s0_token_deep_analysis.json` - 深度分析结果（运行deep脚本后生成）
- `token_structure_analysis.json` - Token结构分析结果

### 文档
- `JX2S0_TOKEN_ANALYSIS_README.md` - 使用说明
- `JX2S0_TOKEN_ANALYSIS_SUMMARY.md` - 本文档

### Archive中的相关分析
- `archive/jx2s0_analysis/` - 之前的分析文件
  - `M3U8_GENERATION_SUMMARY.md` - m3u8生成总结
  - `JX2S0_M3U8_GENERATION_ANALYSIS.md` - m3u8生成分析
  - `analyze_jx2s0_parser.py` - 之前的分析脚本

---

## 💡 关键发现

1. ✅ **Token格式确认**: 176字符的十六进制字符串，解码后是88字节的二进制数据
2. ✅ **URL结构确认**: `https://cachem3u8.2s0.cn:8899/Cache/LZ/{hash}.m3u8?token={token}`
3. ⚠️ **生成逻辑未找到**: 在JavaScript代码中未找到明确的token生成函数
4. ⚠️ **API响应关系**: 需要进一步分析API响应数据与token的关系

---

## 🚀 推荐行动

1. **运行深度分析脚本**: 使用 `deep_analyze_jx2s0_token.py` 进行更长时间的分析
2. **手动浏览器分析**: 在浏览器中手动分析，观察token生成过程
3. **多次请求分析**: 收集多个token样本，分析变化规律
4. **逆向JavaScript**: 如果可能，反混淆JavaScript代码，找到token生成函数

---

**最后更新**: 2024-12-XX  
**状态**: Token结构已分析，生成逻辑待进一步分析

