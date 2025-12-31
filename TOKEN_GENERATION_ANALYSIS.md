# jx.2s0.cn Token 生成方式分析报告

## 📋 问题概述

**目标**: 分析 `captured_jx_m3u8_tv_params.json` 中的关键 token 是如何生成的

**Token值**:
```
d3d376466714168607a696b254956444b496d653377613c6751386134663357714a42525358415f695947764648393b6b4a6545694545433f4d65376c646152513a7a6257303757627f69745a75535352445645305a5b6e4
```

**m3u8 URL**:
```
https://cachem3u8.2s0.cn:8899/Cache/LZ/4e7a11f1eb74b1fbe7b5c6359d501c3d.m3u8?token={token}
```

---

## 🔍 Token 结构分析

### 1. 基本信息
- **长度**: 176 字符
- **字符集**: 十六进制字符 (0-9, a-f)
- **格式**: 纯十六进制字符串

### 2. 字符分布
- 最常见的字符: `6` (17.0%), `5` (15.9%), `4` (14.8%), `3` (11.9%)
- 字符分布相对均匀，无明显模式

### 3. 模式分析
- 发现重复模式: `'d3'` 出现 2 次
- 整体无明显重复模式，可能是加密或哈希后的数据

### 4. 编码分析
- Token 是十六进制字符串
- 转换为字节后长度: 88 字节
- Base64 编码后: `09N2RmcUFoYHppayVJVkRLSW1lM3dhPGdROGE0ZjNXcUpCUlNYQV9pWUd2Rkg5O2tKZUVpRUVDP01lN2xkYVJROnpiVzA3V2J/aX...`

---

## 🔗 m3u8 URL 结构分析

### URL 组成部分
```
https://cachem3u8.2s0.cn:8899/Cache/LZ/4e7a11f1eb74b1fbe7b5c6359d501c3d.m3u8?token={token}
```

- **域名**: `cachem3u8.2s0.cn:8899`
- **路径**: `/Cache/LZ/4e7a11f1eb74b1fbe7b5c6359d501c3d.m3u8`
- **路径中的 hash**: `4e7a11f1eb74b1fbe7b5c6359d501c3d` (32字符，可能是MD5)
- **查询参数**: `token={token}`

### Hash 分析
- Hash 长度: 32 字符
- 格式: 十六进制
- 可能的生成方式:
  - MD5(video_url)
  - MD5(config.id)
  - MD5(config.id + video_url)
  - 其他算法

---

## 📡 API 调用分析

### 关键 API 调用

1. **主页面**: `https://jx.2s0.cn/player/?url={video_url}`
   - 时间戳: 338429.859
   - 返回: HTML页面（包含iframe）

2. **iframe页面**: `https://jx.2s0.cn/player/analysis.php?v={video_url}`
   - 时间戳: 338430.031
   - 返回: HTML页面（包含JavaScript代码）

3. **关键API**: `https://jx.2s0.cn/admin/api.php`
   - 时间戳: 338431.14
   - 方法: GET
   - 参数: 无
   - **⚠️ 响应内容未在捕获数据中**

4. **m3u8 URL**: `https://cachem3u8.2s0.cn:8899/Cache/LZ/{hash}.m3u8?token={token}`
   - 时间戳: 338431.14（与 `/admin/api.php` 几乎同时）

### 调用顺序
```
1. 访问主页面 → 加载iframe
2. iframe加载 → 执行JavaScript
3. JavaScript调用 /admin/api.php → 获取配置
4. JavaScript处理配置 → 生成m3u8 URL和token
5. 请求m3u8文件
```

---

## 💡 Token 生成假设

### 假设1: Token 基于 video_url 生成
**测试结果**: ❌ 不匹配
- MD5(video_url): `b486c3442506ab06add8fff3e685161f`
- SHA1(video_url): `e86515ab05650b99c31262e8537d35d168e2f86c`
- SHA256(video_url): `61871837b5c789fc445f740e030cb18acdd89ee8a95b7745de8a7163dfc72d50`
- **结论**: Token 不是直接基于 video_url 的哈希

### 假设2: Token 基于 API 响应字段生成
**状态**: ⚠️ 需要验证
- `/admin/api.php` 的响应内容未捕获
- 响应可能包含:
  - `config.url` (加密的URL)
  - `config.id` (视频ID)
  - 其他配置数据
- **下一步**: 捕获完整的API响应内容

### 假设3: Token 是加密数据
**特征**:
- Token 长度: 176 字符 (88 字节)
- 转换为字节后可能包含:
  - 加密后的URL
  - 签名数据
  - 时间戳 + 其他数据
- **可能的加密方式**:
  - RC4加密（之前分析中发现网站使用RC4）
  - AES加密
  - 其他对称加密算法

### 假设4: Token 包含时间戳
**测试结果**: ⚠️ 部分匹配
- 在token中找到多个10位数字，可能是Unix时间戳:
  - `3764667141` → 2089-04-18（未来时间，不合理）
  - `6751386134` → 2183-12-11（未来时间，不合理）
- **结论**: 这些数字可能不是时间戳，而是加密数据的一部分

---

## 🎯 关键发现

### 1. Token 生成时机
- Token 出现在 `/admin/api.php` 调用之后
- 时间戳几乎相同（338431.14），说明token是在API响应后立即生成的

### 2. Token 生成位置
- **最可能**: JavaScript代码中生成（7zl.js 或 7zlplayer.js）
- **生成方式**: 
  - 基于 `/admin/api.php` 的响应数据
  - 使用某种加密或签名算法

### 3. 需要的信息
- ✅ `/admin/api.php` 的完整响应内容
- ✅ JavaScript代码中的token生成逻辑
- ✅ 可能的加密密钥或算法

---

## 📝 下一步行动

### 1. 捕获 API 响应内容
**工具**: `capture_admin_api_response.py`
```bash
python capture_admin_api_response.py
```

**目标**:
- 捕获 `/admin/api.php` 的完整响应
- 分析响应中的数据结构
- 查找与token相关的字段

### 2. 分析 JavaScript 代码
**文件**: 
- `7zl.js`
- `7zlplayer.js`

**查找关键字**:
- `token`
- `cachem3u8`
- `Cache/LZ`
- `m3u8`
- 加密函数（`rc4`, `encrypt`, `md5`, `sha`等）

### 3. 浏览器控制台调试
**方法**:
1. 打开浏览器开发者工具
2. 访问解析网站
3. 在控制台中执行:
   ```javascript
   // 查看全局变量
   console.log(window.ConFig);
   console.log(window.config);
   
   // 监听网络请求
   // 查看 /admin/api.php 的响应
   
   // 尝试调用生成token的函数
   ```

### 4. 逆向 JavaScript 代码
**步骤**:
1. 下载 `7zl.js` 和 `7zlplayer.js`
2. 反混淆代码（如果需要）
3. 查找token生成相关的函数
4. 还原生成逻辑

---

## 🔧 改进的捕获脚本

已创建 `capture_admin_api_response.py`，专门用于:
- ✅ 捕获 `/admin/api.php` 的完整响应
- ✅ 保存响应内容到JSON文件
- ✅ 提取页面中的全局变量（ConFig等）
- ✅ 捕获m3u8 URL

**使用方法**:
```bash
python capture_admin_api_response.py
```

---

## 📊 总结

### Token 特征
- ✅ 176字符的十六进制字符串
- ✅ 88字节的二进制数据（转换为字节后）
- ✅ 可能是加密或签名后的数据
- ✅ 基于 `/admin/api.php` 响应生成

### 生成流程推测
```
1. 调用 /admin/api.php
   ↓
2. 获取响应数据（config.url, config.id等）
   ↓
3. JavaScript处理响应数据
   ↓
4. 使用某种算法生成token
   ↓
5. 构造m3u8 URL: https://cachem3u8.2s0.cn:8899/Cache/LZ/{hash}.m3u8?token={token}
```

### 关键问题
1. ❓ `/admin/api.php` 返回什么数据？
2. ❓ Token 的生成算法是什么？
3. ❓ Hash (`4e7a11f1eb74b1fbe7b5c6359d501c3d`) 是如何生成的？
4. ❓ Token 和 Hash 的关系是什么？

---

## 🚀 建议

1. **立即执行**: 运行 `capture_admin_api_response.py` 捕获API响应
2. **深入分析**: 分析JavaScript代码，查找token生成逻辑
3. **浏览器调试**: 在浏览器控制台中调试，直接调用相关函数
4. **逆向工程**: 如果代码被混淆，需要反混淆后再分析

---

**最后更新**: 2024-12-19
**分析工具**: `analyze_token_generation.py`
**捕获工具**: `capture_admin_api_response.py`


