# 付费Key分析总结

## 📊 当前状态

### ✅ 已确认

1. **付费版本直接返回m3u8 URL**
   - 不需要JavaScript生成
   - 服务器端直接生成并返回

2. **Hash和Token信息**
   - **Hash**: `2089c333a6d6a31e306bd190557aea36` (32字符，MD5格式)
   - **Token**: `d3d37757e6345566e4e43623b4c614571477a447f43424e6265423b4365435376667f2259455247746c6a415744324c613f6547443a43443a626e6d40786a77334e4f487c64775b2474793b44567741794951513f62477e4` (176字符，十六进制格式)

3. **测试结果**
   - ❌ Hash未找到匹配的生成算法
   - ❌ Token未找到匹配的生成算法

### ❓ 可能的原因

#### Hash未找到匹配的原因

1. **服务器端生成（最可能）**
   - Hash可能是基于数据库中的记录ID生成的
   - 服务器可能先查询数据库，找到对应的记录，然后生成hash
   - Hash可能包含时间戳或其他服务器端信息

2. **使用其他参数**
   - 可能使用了IP地址、User-Agent等请求信息
   - 可能使用了时间戳或随机数
   - 可能使用了其他隐藏参数

3. **不同的编码方式**
   - 可能使用了URL编码、Base64编码等
   - 可能使用了特殊的字符串处理方式

#### Token未找到匹配的原因

1. **复杂的加密算法**
   - 可能使用了多层加密
   - 可能使用了自定义的加密算法
   - 可能使用了服务器端的密钥

2. **包含额外信息**
   - Token可能包含时间戳、签名等信息
   - Token可能包含服务器端的验证信息

## 🎯 下一步分析方向

### 方向1：测试不同的视频URL（推荐）⭐

**目标**：确定hash和token是否基于video_url生成

**方法**：
1. 使用相同的 `uid` 和 `key`，但不同的 `video_url`
2. 观察hash和token是否变化
3. 如果变化，说明hash和token是基于video_url生成的
4. 如果不变，说明hash和token可能是固定的或基于其他参数

**测试脚本**：
```python
import requests
import re

uid = "4059917"
key = "cgklotuyDGHILOTW38"

test_urls = [
    "https://www.iqiyi.com/v_1c168e2yzbk.html",
    "https://www.iqiyi.com/v_19rr7qhfg0.html",
    "https://v.youku.com/v_show/id_XMTA0MTc5NzI4.html",
]

for video_url in test_urls:
    url = f"https://json.2s0.cn:5678/player/analysis.php/?uid={uid}&key={key}&url={video_url}"
    response = requests.get(url)
    html = response.text
    
    # 提取m3u8 URL
    m3u8_match = re.search(r'var url = "([^"]+)"', html)
    if m3u8_match:
        m3u8_url = m3u8_match.group(1)
        # 提取hash和token
        hash_match = re.search(r'/Cache/Ff/([a-f0-9]+)\.m3u8', m3u8_url)
        token_match = re.search(r'token=([^"]+)', m3u8_url)
        
        if hash_match and token_match:
            hash_value = hash_match.group(1)
            token_value = token_match.group(1)
            print(f"Video URL: {video_url}")
            print(f"  Hash: {hash_value}")
            print(f"  Token: {token_value[:50]}...")
            print()
```

### 方向2：分析服务器端代码

**目标**：找到PHP代码中的生成逻辑

**方法**：
1. 如果可能，分析 `analysis.php` 的源代码
2. 查找hash和token的生成函数
3. 理解生成逻辑

**可能的PHP代码结构**：
```php
<?php
$uid = $_GET['uid'];
$key = $_GET['key'];
$url = $_GET['url'];

// 验证uid和key
if (!verify_key($uid, $key)) {
    die('Invalid key');
}

// 查询数据库，获取视频信息
$video_info = get_video_info($url);

// 生成hash（可能是基于数据库ID）
$hash = generate_hash($video_info['id'], $uid, $key);

// 生成token（可能是加密的签名）
$token = generate_token($video_info, $uid, $key);

// 构造m3u8 URL
$m3u8_url = "https://cachem3u8.2s0.cn:8899/Cache/Ff/{$hash}.m3u8?token={$token}";

// 返回HTML
echo generate_html($m3u8_url);
?>
```

### 方向3：分析Token格式

**目标**：理解token的结构和内容

**方法**：
1. 分析token的十六进制格式
2. 尝试解码token
3. 查找token中的模式

**Token分析**：
- Token长度：176字符（88字节）
- 格式：十六进制字符串
- 可能包含：uid、key、video_url、时间戳、签名等

## 📝 建议

### 短期建议

1. **运行扩展测试脚本**
   ```bash
   python test_paid_key_extended.py
   ```
   测试更多的字符串组合和编码方式

2. **测试不同的视频URL**
   使用相同的uid和key，但不同的video_url，观察hash和token的变化

3. **分析Token格式**
   尝试解码token，看是否包含可识别的信息

### 长期建议

1. **如果hash和token无法逆向**
   - 可以考虑直接调用API获取m3u8 URL
   - 不需要逆向算法，直接使用API

2. **如果找到生成算法**
   - 可以实现Python版本的生成函数
   - 可以直接生成m3u8 URL，不需要API调用

## 🔍 关键发现

### 免费版本 vs 付费版本

| 特性 | 免费版本 | 付费版本 |
|------|---------|---------|
| **m3u8 URL来源** | JavaScript动态生成 | 服务器端直接返回 |
| **需要config对象** | ✅ 是 | ❌ 否 |
| **需要JavaScript执行** | ✅ 是 | ❌ 否 |
| **Hash生成** | 客户端生成 | 服务器端生成 |
| **Token生成** | 客户端生成 | 服务器端生成 |

### 重要结论

1. **付费版本更简单**
   - 直接返回m3u8 URL
   - 不需要复杂的JavaScript执行
   - 可以直接通过API调用获取

2. **Hash和Token可能是服务器端生成的**
   - 基于数据库记录
   - 基于服务器端密钥
   - 可能包含时间戳等动态信息

3. **如果无法逆向算法**
   - 可以直接调用API获取m3u8 URL
   - 这是最简单可靠的方法

## 🎯 推荐行动

### 方案1：直接使用API（最简单）⭐

**优点**：
- ✅ 不需要逆向算法
- ✅ 简单可靠
- ✅ 不需要理解复杂的生成逻辑

**实现**：
```python
import requests
import re

def get_m3u8_url(uid, key, video_url):
    """获取m3u8 URL"""
    url = f"https://json.2s0.cn:5678/player/analysis.php/?uid={uid}&key={key}&url={video_url}"
    response = requests.get(url)
    html = response.text
    
    # 提取m3u8 URL
    m3u8_match = re.search(r'var url = "([^"]+)"', html)
    if m3u8_match:
        return m3u8_match.group(1)
    return None
```

### 方案2：继续分析算法（如果希望完全自动化）

**优点**：
- ✅ 不需要API调用
- ✅ 可以离线生成

**缺点**：
- ❌ 需要找到生成算法
- ❌ 如果算法更新，需要重新分析

## 📚 相关文件

- `PAID_KEY_FINDINGS.md` - 详细发现
- `test_paid_key_hash_token.py` - Hash和Token测试脚本
- `test_paid_key_extended.py` - 扩展测试脚本
- `paid_key_analysis.html` - 付费版本的HTML文件

