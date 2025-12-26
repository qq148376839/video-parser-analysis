# jx.2s0.cn 解密逻辑分析

## 📋 关键代码片段

### 1. RC4解密函数（7zl.js:2807-2926）

这是核心的解密函数，使用RC4算法：

```javascript
function rc4(_0x2262fd, _0x112647, _0x1bd18b) {
    // _0x2262fd: 加密的URL（Base64编码）
    // _0x112647: 密钥
    // _0x1bd18b: 标志（1表示解密，0表示加密）
    
    // 如果 _0x1bd18b == 1:
    //   1. 使用 atob() 解码Base64
    //   2. 使用RC4算法解密
    //   3. 使用 decodeURIComponent() 解码URL编码
    //   返回解密后的URL
    
    // 如果 _0x1bd18b != 1:
    //   1. 使用 encodeURIComponent() 编码
    //   2. 使用RC4算法加密
    //   3. 使用 btoa() 编码为Base64
    //   返回加密后的字符串
}
```

**关键逻辑**：
- 第2872行：`var _0x2262fd = _0x272f19[_0x35a7ff(0x5b4, 'ZFAJ')](atob, _0x2262fd);` - Base64解码
- 第2880-2889行：RC4密钥调度算法（KSA）
- 第2890-2919行：RC4伪随机生成算法（PRGA）
- 第2922行：`return _0x272f19['bUtHS'](decodeURIComponent, _0x409395);` - URL解码

---

### 2. 调用rc4解密的地方（7zl.js:256）

```javascript
YKQ[_0x319ba2(0x205, '3Txb')](_0x5e7426[_0x319ba2(0x4a1, 'W19[')](rc4, config[_0x319ba2(0x1ea, 'Iar!')], _0x5e7426[_0x319ba2(0x6f3, 'Y!Al')], 0x1));
```

**参数说明**：
- `config['url']`: 加密的URL（Base64字符串）
- `_0x5e7426[_0x319ba2(0x6f3, 'Y!Al')]`: **密钥**（需要找到这个值）
- `0x1`: 解密标志

**需要分析**：
- `_0x5e7426` 对象的定义位置
- `_0x319ba2(0x6f3, 'Y!Al')` 对应的实际键名
- 密钥的生成方式

---

### 3. YKQ.id的生成（7zl.js:411-417）

```javascript
if (_0x35b4de[_0x5eb9ee(0x2bf, '6xPH')](up['diyid'][0x0], 0x0) && _0x35b4de[_0x5eb9ee(0x45c, '@)D$')](config['id'], ''))
    a = config['id'],
    b = config[_0x5eb9ee(0x4a2, 'zoK3')];
else
    (_0x35b4de[_0x5eb9ee(0x250, 'hg%J')](up[_0x5eb9ee(0x627, ']DI(')][0x0], 0x1) || !config['id']) && (a = up[_0x5eb9ee(0x25e, '@)D$')][0x1],
    b = up[_0x5eb9ee(0x3ab, 'i&0C')][0x2]);
YKQ['id'] = _0x35b4de['vboWg'](_0x35b4de[_0x5eb9ee(0x6cb, '2H%]')](a, '\x20P'), b);
```

**说明**：
- `YKQ.id` 可能是密钥的一部分
- 由 `config['id']` 或 `up` 数组的值生成
- 格式：`a + ' P' + b`

---

### 4. config对象的来源（7zl.js:219-242）

```javascript
$[_0x232352(0x288, 'U!$n')]({
    'url': _0x5e7426[_0x232352(0x4df, '2H%]')],
    'dataType': _0x5e7426[_0x232352(0x721, 'i&0C')],
    'success': function(_0x4f0b5a) {
        // ...
        config['url'] = _0x4f0b5a['data']['url'],  // 加密的URL
        config['id'] = _0x4f0b5a['data']['id'],    // ID
        // ...
    }
});
```

**说明**：
- `config['url']` 从API响应 `_0x4f0b5a['data']['url']` 获取
- `config['id']` 从API响应 `_0x4f0b5a['data']['id']` 获取
- API端点：`_0x5e7426[_0x232352(0x4df, '2H%]')]`（需要找到实际URL）

---

## 🔍 需要分析的代码片段

### 片段1：密钥的定义（7zl.js:190-218）

**位置**：`_0x5e7426` 对象的定义

**需要找到**：
- `_0x319ba2(0x6f3, 'Y!Al')` 对应的实际键名
- 密钥的值或生成方式

**可能的位置**：
- 第190-218行：`_0x5e7426` 对象的定义
- 密钥可能是：
  - `YKQ.id`
  - `config.id`
  - 固定的字符串
  - 从API响应中获取

---

### 片段2：YKQ对象的初始化（7zl.js:121-259）

**位置**：YKQ对象的定义和初始化

**需要找到**：
- `YKQ[_0x319ba2(0x205, '3Txb')]` 是什么方法（可能是 `video` 或 `player`）
- `_0x5e7426[_0x319ba2(0x4a1, 'W19[')]` 是什么方法（可能是 `call` 或 `apply`）

---

### 片段3：API端点的定义（7zl.js:190-220）

**位置**：`_0x5e7426` 对象中 `url` 字段的定义

**需要找到**：
- API的实际URL（可能是 `/admin/api.php` 或类似）

---

### 片段4：RC4密钥调度（7zl.js:2863-2889）

**位置**：RC4算法的密钥调度部分

**关键代码**：
```javascript
var _0x29a4a9 = _0x272f19[_0x35a7ff(0x687, 'vicG')](_0x112647, _0x272f19['MCwlj'])
var _0x1bbf36 = _0x29a4a9[_0x35a7ff(0x218, 'XIKw')];

// 初始化S-box
for (i = 0x0; _0x272f19['jeGXy'](i, 0x100); i++) {
    _0x112647[i] = _0x29a4a9[_0x272f19['HMOFz'](i, _0x1bbf36)][_0x35a7ff(0x2fa, '%9H0')](),
    _0x3e4509[i] = i;
}

// KSA (Key Scheduling Algorithm)
for (j = i = 0x0; _0x272f19['jeGXy'](i, 0x100); i++) {
    j = _0x272f19['mEkeZ'](_0x272f19['IJVze'](_0x272f19[_0x35a7ff(0x22f, 'a*Iz')](j, _0x3e4509[i]), _0x112647[i]), 0x100),
    tmp = _0x3e4509[i],
    _0x3e4509[i] = _0x3e4509[j],
    _0x3e4509[j] = tmp;
}
```

**说明**：
- `_0x29a4a9` 是密钥字符串
- `_0x1bbf36` 是密钥长度
- `_0x112647` 是密钥字节数组
- `_0x3e4509` 是S-box（状态数组）

---

### 片段5：RC4伪随机生成（7zl.js:2890-2919）

**位置**：RC4算法的PRGA部分

**关键代码**：
```javascript
for (a = j = i = 0x0; _0x272f19[_0x35a7ff(0x4b4, 'OuvR')](i, _0x143495); i++) {
    // 生成伪随机字节流
    // 与密文异或得到明文
    _0x409395 += String[_0x35a7ff(0x4fe, '%9H0')](_0x272f19[_0x35a7ff(0x4bb, '08@C')](_0x2262fd[i][_0x35a7ff(0x564, 'IFAK')](), k));
}
```

**说明**：
- `_0x143495` 是密文长度
- `k` 是伪随机字节
- `_0x409395` 是解密后的字符串

---

## 🎯 分析步骤

### 步骤1：找到密钥

1. **查找 `_0x5e7426` 对象的定义**
   - 位置：7zl.js:190-218
   - 找到 `_0x319ba2(0x6f3, 'Y!Al')` 对应的键名

2. **可能的密钥来源**：
   - `YKQ.id`（从config.id生成）
   - `config.id`（从API响应获取）
   - 固定的字符串
   - 从URL参数中提取

### 步骤2：理解RC4算法

1. **Base64解码**：`atob(encrypted_url)`
2. **RC4解密**：使用密钥解密
3. **URL解码**：`decodeURIComponent(decrypted_string)`

### 步骤3：实现Python版本

1. **Base64解码**：`base64.b64decode()`
2. **RC4解密**：实现RC4算法
3. **URL解码**：`urllib.parse.unquote()`

---

## 📝 建议的分析方法

### 方法1：动态调试

在浏览器中运行以下代码，获取实际值：

```javascript
// 在analysis.php页面中执行
console.log('config.url:', config.url);
console.log('config.id:', config.id);
console.log('YKQ.id:', YKQ.id);

// 找到密钥
// 假设密钥是 YKQ.id
var key = YKQ.id;
console.log('Key:', key);

// 测试解密
var encrypted = config.url;
var decrypted = rc4(encrypted, key, 1);
console.log('Decrypted URL:', decrypted);
```

### 方法2：静态分析

1. **反混淆代码**：使用工具或手动分析
2. **追踪变量**：找到密钥的实际值
3. **提取算法**：提取RC4算法的纯逻辑

### 方法3：使用分析脚本

使用 `analyze_jx2s0_parser.py` 脚本：
1. 运行脚本获取 `config` 对象
2. 提取 `config.url` 和 `config.id`
3. 在浏览器控制台中测试解密

---

## 🔧 Python实现思路

```python
import base64
from urllib.parse import unquote

def rc4_decrypt(encrypted_data, key, decode_flag=1):
    """
    RC4解密函数
    
    Args:
        encrypted_data: Base64编码的加密字符串
        key: 密钥字符串
        decode_flag: 1表示解密，0表示加密
    
    Returns:
        解密后的URL字符串
    """
    if decode_flag == 1:
        # Base64解码
        encrypted_bytes = base64.b64decode(encrypted_data)
        
        # RC4解密
        decrypted_bytes = rc4_crypt(encrypted_bytes, key)
        
        # URL解码
        decrypted_str = decrypted_bytes.decode('utf-8', errors='ignore')
        return unquote(decrypted_str)
    else:
        # 加密逻辑（如果需要）
        pass

def rc4_crypt(data, key):
    """
    RC4加密/解密核心算法
    """
    # KSA (Key Scheduling Algorithm)
    S = list(range(256))
    j = 0
    key_bytes = key.encode('utf-8')
    
    for i in range(256):
        j = (j + S[i] + key_bytes[i % len(key_bytes)]) % 256
        S[i], S[j] = S[j], S[i]
    
    # PRGA (Pseudo-Random Generation Algorithm)
    i = j = 0
    result = bytearray()
    
    for byte in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        k = S[(S[i] + S[j]) % 256]
        result.append(byte ^ k)
    
    return bytes(result)
```

---

## ⚠️ 注意事项

1. **密钥可能动态变化**：密钥可能基于视频ID或其他参数生成
2. **字符编码**：注意UTF-8和URL编码的处理
3. **Base64填充**：确保Base64字符串格式正确
4. **错误处理**：解密失败时的处理逻辑

---

## 📌 下一步行动

1. ✅ 运行 `analyze_jx2s0_parser.py` 获取 `config` 对象
2. 🔍 在浏览器控制台中测试解密逻辑
3. 🔑 找到密钥的实际值或生成方式
4. 💻 实现Python版本的解密函数
5. ✅ 测试解密功能

---

## 📊 实际测试结果

### 从分析脚本获取的数据

**加密URL**：
```
O/zpjS4gC4ztyL9ve/+wx/3Lmpl7X/QAEOuqmTie93atrwDjwxRosEpoaXZw0TRD/AGtcvvIxMxgcxsQWcHumCqsvuIlf3lGXkqJgVWIsvPYgh8+Nsu4r36vZQ6fs/7edsA0WFSEDE16nQGeuSgCzC9HRMXafpabTanng2B2TaMPVJwkEAP24qZ8LdQvO/xA28+7iJ4Llj55cOlCqDSNg7g0Qvlc35/ngUrCRpXCxyQLod1GyL81cUTuDcOJTHe+cay4ZVB89fiZ48vYKwhA14o/IBdKo38EPHHj0XVLvf9VzCjgzdu8sBzAskD2i+923XStnQr8znCRh9bk+LR0sTvL69vQo8bTPLxHe2bqqyun0Qd0Qw==
```

**config.id**：
```
b664f44e3be2ad57fdb6
```

**YKQ.id**：
```
b664f44e3be2ad57fdb6 P
```

**可能的密钥**：
- `config.id` = `"b664f44e3be2ad57fdb6"`
- `YKQ.id` = `"b664f44e3be2ad57fdb6 P"` (根据7zl.js:417的代码，格式为 `a + ' P' + b`)

### ⚠️ 重要发现

**解密测试结果**：
- ✅ 使用密钥 `"b664f44e3be2ad57fdb6 P"` 可以成功调用rc4函数
- ⚠️ 但解密后的内容是乱码，不是有效的URL
- 💡 **实际m3u8链接是通过网络请求直接获取的**，不是通过解密config.url得到的

**实际m3u8链接格式**：
```
https://cachem3u8.2s0.cn:8899/Cache/Ff/{hash}.m3u8?token={token}
```

**获取方式**：
- m3u8链接是在JavaScript执行后，通过API请求自动生成的
- 可以直接从网络请求中提取，无需解密config.url

### 测试脚本

运行以下脚本测试解密：

```bash
python test_jx2s0_decrypt.py
```

该脚本会：
1. 加载7zl.js到浏览器
2. 访问analysis.php页面
3. 提取config和YKQ对象
4. 测试多种可能的密钥
5. 返回解密结果

### 预期结果

如果解密成功，应该得到类似这样的URL：
- m3u8链接：`https://cachem3u8.2s0.cn:8899/Cache/...`
- 或直接视频链接

---

## 🔧 快速测试方法

### 方法1：使用测试脚本（推荐）

```bash
python test_jx2s0_decrypt.py
```

### 方法2：在浏览器控制台中手动测试

1. 访问 `https://jx.2s0.cn/player/analysis.php?v=https://www.iqiyi.com/v_1c168e2yzbk.html`
2. 打开浏览器控制台（F12）
3. 执行以下代码：

```javascript
// 检查对象
console.log('config:', config);
console.log('config.url:', config.url);
console.log('config.id:', config.id);
console.log('YKQ.id:', YKQ.id);

// 测试解密
var encrypted = config.url;
var key = YKQ.id;  // 或 config.id
var decrypted = rc4(encrypted, key, 1);
console.log('解密结果:', decrypted);
```

### 方法3：使用Python实现（需要先找到密钥）

一旦确定了密钥，可以使用 `direct_jx2s0_parser_simple.py` 中的RC4实现。

