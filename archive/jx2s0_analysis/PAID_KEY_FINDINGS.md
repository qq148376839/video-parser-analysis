# 付费Key分析结果

## 🎯 重大发现！

### ✅ 付费版本直接返回m3u8 URL！

**HTML中的关键代码**（第19行）：
```javascript
var url = "https://cachem3u8.2s0.cn:8899/Cache/Ff/2089c333a6d6a31e306bd190557aea36.m3u8?token=d3d37757e6345566e4e43623b4c614571477a447f43424e6265423b4365435376667f2259455247746c6a415744324c613f6547443a43443a626e6d40786a77334e4f487c64775b2474793b44567741794951513f62477e4";
```

**关键信息**：
- **Hash**: `2089c333a6d6a31e306bd190557aea36` (32字符，MD5格式)
- **Token**: `d3d37757e6345566e4e43623b4c614571477a447f43424e6265423b4365435376667f2259455247746c6a415744324c613f6547443a43443a626e6d40786a77334e4f487c64775b2474793b44567741794951513f62477e4` (约200+字符，十六进制格式)

## 📊 对比分析

### 免费版本 vs 付费版本

| 项目 | 免费版本 | 付费版本 |
|------|---------|---------|
| **m3u8 URL来源** | JavaScript动态生成 | 服务器端直接返回 |
| **config对象** | 需要JavaScript执行 | 不需要config对象 |
| **Hash** | 动态生成 | 直接返回 |
| **Token** | 动态生成 | 直接返回 |

### 关键差异

1. **免费版本**：
   - 返回HTML包含 `config` 对象
   - 需要JavaScript执行 `YKQ.start()` 和 `YKQ.video()`
   - m3u8 URL是客户端生成的

2. **付费版本**：
   - 返回HTML直接包含m3u8 URL
   - 不需要JavaScript生成
   - m3u8 URL是服务器端生成的

## 🔍 加密算法分析

### Hash分析

**Hash值**: `2089c333a6d6a31e306bd190557aea36`

**可能的生成方式**：
```python
import hashlib

uid = "4059917"
key = "cgklotuyDGHILOTW38"
video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"

# 测试不同的组合
test_strings = [
    f"{uid}{key}{video_url}",
    f"{uid}{key}",
    f"{key}{video_url}",
    f"{uid}{video_url}",
    video_url,
]

for test_str in test_strings:
    md5_hash = hashlib.md5(test_str.encode()).hexdigest()
    print(f"MD5({test_str[:50]}...): {md5_hash}")
    if md5_hash == "2089c333a6d6a31e306bd190557aea36":
        print("  🎯 找到匹配！")
```

### Token分析

**Token值**: `d3d37757e6345566e4e43623b4c614571477a447f43424e6265423b4365435376667f2259455247746c6a415744324c613f6547443a43443a626e6d40786a77334e4f487c64775b2474793b44567741794951513f62477e4`

**特征**：
- 长度：约200+字符
- 格式：十六进制字符串
- 可能包含：uid、key、video_url、时间戳等信息

**可能的生成方式**：
1. 使用 `uid`、`key`、`video_url` 生成签名
2. 使用加密算法（RC4、AES等）加密数据
3. 使用Base64编码后再转换为十六进制

## 🎯 下一步分析方向

### 方向1：分析Hash生成算法

**目标**：找到hash的生成方式

**方法**：
1. 测试不同的字符串组合
2. 测试不同的hash算法（MD5、SHA1、SHA256等）
3. 测试不同的编码方式

**测试代码**：
```python
import hashlib

uid = "4059917"
key = "cgklotuyDGHILOTW38"
video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
target_hash = "2089c333a6d6a31e306bd190557aea36"

# 测试不同的组合和算法
test_cases = [
    (f"{uid}{key}{video_url}", "MD5"),
    (f"{uid}{key}", "MD5"),
    (f"{key}{video_url}", "MD5"),
    (video_url, "MD5"),
    # 添加更多测试用例
]

for test_str, algorithm in test_cases:
    if algorithm == "MD5":
        hash_value = hashlib.md5(test_str.encode()).hexdigest()
    elif algorithm == "SHA1":
        hash_value = hashlib.sha1(test_str.encode()).hexdigest()
    elif algorithm == "SHA256":
        hash_value = hashlib.sha256(test_str.encode()).hexdigest()
    
    if hash_value == target_hash:
        print(f"🎯 找到匹配！")
        print(f"   字符串: {test_str}")
        print(f"   算法: {algorithm}")
        print(f"   Hash: {hash_value}")
        break
```

### 方向2：分析Token生成算法

**目标**：找到token的生成方式

**方法**：
1. 分析token的格式和结构
2. 测试不同的加密算法
3. 尝试解密token

**测试代码**：
```python
import hashlib
import base64
from Crypto.Cipher import ARC4

uid = "4059917"
key = "cgklotuyDGHILOTW38"
video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
target_token = "d3d37757e6345566e4e43623b4c614571477a447f43424e6265423b4365435376667f2259455247746c6a415744324c613f6547443a43443a626e6d40786a77334e4f487c64775b2474793b44567741794951513f62477e4"

# 测试不同的组合
test_strings = [
    f"{uid}{key}{video_url}",
    f"{uid}{key}",
    f"{key}{video_url}",
]

for test_str in test_strings:
    # MD5
    md5_hash = hashlib.md5(test_str.encode()).hexdigest()
    
    # SHA1
    sha1_hash = hashlib.sha1(test_str.encode()).hexdigest()
    
    # Base64
    b64_encoded = base64.b64encode(test_str.encode()).decode()
    
    # RC4加密
    possible_keys = [uid, key, f"{uid}{key}", f"{key}{uid}"]
    for rc4_key in possible_keys:
        try:
            cipher = ARC4.new(rc4_key.encode())
            encrypted = cipher.encrypt(test_str.encode())
            hex_encrypted = encrypted.hex()
            if hex_encrypted.startswith(target_token[:20]):
                print(f"🎯 可能匹配！")
                print(f"   字符串: {test_str}")
                print(f"   RC4密钥: {rc4_key}")
                print(f"   加密结果: {hex_encrypted[:100]}...")
        except:
            pass
```

### 方向3：分析服务器端代码

**目标**：找到PHP代码中的生成逻辑

**方法**：
1. 分析 `analysis.php` 的URL参数处理
2. 查找hash和token的生成代码
3. 尝试逆向PHP代码

**可能的PHP代码结构**：
```php
<?php
$uid = $_GET['uid'];
$key = $_GET['key'];
$url = $_GET['url'];

// 生成hash
$hash = md5($uid . $key . $url); // 或其他组合

// 生成token
$token = generate_token($uid, $key, $url); // 需要找到这个函数

// 构造m3u8 URL
$m3u8_url = "https://cachem3u8.2s0.cn:8899/Cache/Ff/{$hash}.m3u8?token={$token}";

// 返回HTML
echo generate_html($m3u8_url);
?>
```

## 📝 总结

### ✅ 已确认

1. **付费版本直接返回m3u8 URL**
2. **Hash**: `2089c333a6d6a31e306bd190557aea36`
3. **Token**: `d3d37757e6345566e4e43623b4c614571477a447f43424e6265423b4365435376667f2259455247746c6a415744324c613f6547443a43443a626e6d40786a77334e4f487c64775b2474793b44567741794951513f62477e4`

### ❓ 待确认

1. **Hash的生成算法**（可能是MD5，但需要确认输入字符串）
2. **Token的生成算法**（可能是加密或签名）
3. **服务器端代码**（PHP中的生成逻辑）

### 🎯 推荐行动

1. **运行hash测试脚本**，找到hash的生成方式
2. **运行token测试脚本**，找到token的生成方式
3. **分析服务器端代码**，如果可能的话

