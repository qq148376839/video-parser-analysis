# 付费Key加密算法分析

## 📋 付费Key信息

**URL**: `https://json.2s0.cn:5678/player/analysis.php/?uid=4059917&key=cgklotuyDGHILOTW38&url=https://www.iqiyi.com/v_1c168e2yzbk.html`

**参数**:
- `uid`: `4059917`
- `key`: `cgklotuyDGHILOTW38`
- `url`: `https://www.iqiyi.com/v_1c168e2yzbk.html`

## 🎯 分析目标

1. **对比付费版本和免费版本的差异**
   - 免费版本：`config.url` 和 `config.id` 是固定的
   - 付费版本：`config.url` 和 `config.id` 可能基于 `uid` 和 `key` 生成

2. **分析加密算法**
   - `config.url` 的生成方式
   - `config.id` 的生成方式
   - 是否可以通过 `uid` 和 `key` 直接生成

3. **找到加密算法的实现**
   - 服务器端生成（PHP）
   - 客户端生成（JavaScript）
   - 混合方式

## 🔍 分析步骤

### 步骤1：访问付费URL并提取config

**方法1：使用Python脚本**

```python
import requests
import re

url = "https://json.2s0.cn:5678/player/analysis.php/?uid=4059917&key=cgklotuyDGHILOTW38&url=https://www.iqiyi.com/v_1c168e2yzbk.html"

response = requests.get(url)
html = response.text

# 提取config
config_pattern = r'var\s+config\s*=\s*({[^}]+})'
match = re.search(config_pattern, html, re.DOTALL)

if match:
    config_str = match.group(1)
    print("Config对象:", config_str)
    
    # 提取url和id
    url_match = re.search(r'"url"\s*:\s*"([^"]+)"', config_str)
    id_match = re.search(r'"id"\s*:\s*"([^"]+)"', config_str)
    
    if url_match:
        print("config.url:", url_match.group(1))
    if id_match:
        print("config.id:", id_match.group(1))
```

**方法2：在浏览器中查看**

1. 打开浏览器，访问付费URL
2. 按F12打开开发者工具
3. 切换到Console面板
4. 执行：
```javascript
console.log('config.url:', config.url);
console.log('config.id:', config.id);
```

### 步骤2：对比免费版本和付费版本

**免费版本**（从之前的分析）:
- `config.url`: `O/zpjS4gC4ztyL9ve/+wx/3Lmpl7X/QAEOuqmTie93atrwDjwxRosEpoaXZw0TRD/...`
- `config.id`: `b664f44e3be2ad57fdb6`

**付费版本**（需要提取）:
- `config.url`: `???`（待提取）
- `config.id`: `???`（待提取）

**对比分析**:
- 如果 `config.url` 不同 → 可能基于 `uid` 和 `key` 生成
- 如果 `config.id` 不同 → 可能基于 `uid` 和 `key` 生成
- 如果相同 → 可能是固定的，与 `uid` 和 `key` 无关

### 步骤3：分析加密算法

**可能的加密方式**:

1. **基于uid和key生成config.url**
   ```python
   # 可能的算法
   import hashlib
   import base64
   
   uid = "4059917"
   key = "cgklotuyDGHILOTW38"
   video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
   
   # 方式1: MD5/SHA1
   data = f"{uid}{key}{video_url}"
   hash_value = hashlib.md5(data.encode()).hexdigest()
   
   # 方式2: Base64编码
   encoded = base64.b64encode(data.encode()).decode()
   
   # 方式3: RC4加密
   # 需要找到RC4的密钥
   ```

2. **服务器端生成**
   - PHP代码在服务器端生成 `config.url`
   - 客户端JavaScript只是使用，不生成

3. **客户端生成**
   - JavaScript代码使用 `uid` 和 `key` 生成 `config.url`
   - 需要找到生成代码

### 步骤4：查找生成代码

**搜索位置**:

1. **analysis.php页面**
   - 查看PHP代码
   - 查找 `config.url` 的生成逻辑

2. **JavaScript文件**
   - `7zl.js`
   - `7zlplayer.js`
   - 其他相关JS文件

3. **网络请求**
   - 查看是否有API调用生成 `config.url`
   - 查看请求参数和响应

## 🔧 测试脚本

### 脚本1：提取config并对比

```python
import requests
import re
import base64
import hashlib

def analyze_paid_key(uid, key, video_url):
    """分析付费key"""
    url = f"https://json.2s0.cn:5678/player/analysis.php/?uid={uid}&key={key}&url={video_url}"
    
    response = requests.get(url)
    html = response.text
    
    # 提取config
    config_pattern = r'var\s+config\s*=\s*({[^}]+})'
    match = re.search(config_pattern, html, re.DOTALL)
    
    if match:
        config_str = match.group(1)
        url_match = re.search(r'"url"\s*:\s*"([^"]+)"', config_str)
        id_match = re.search(r'"id"\s*:\s*"([^"]+)"', config_str)
        
        config_url = url_match.group(1) if url_match else None
        config_id = id_match.group(1) if id_match else None
        
        print(f"付费版本:")
        print(f"  config.url: {config_url[:100] if config_url else 'N/A'}...")
        print(f"  config.id: {config_id}")
        
        # 对比免费版本
        free_url = "O/zpjS4gC4ztyL9ve/+wx/3Lmpl7X/QAEOuqmTie93atrwDjwxRosEpoaXZw0TRD/..."
        free_id = "b664f44e3be2ad57fdb6"
        
        print(f"\n免费版本:")
        print(f"  config.url: {free_url[:100]}...")
        print(f"  config.id: {free_id}")
        
        print(f"\n对比结果:")
        if config_url and config_url != free_url:
            print(f"  ✅ config.url 不同（可能基于uid/key生成）")
        if config_id and config_id != free_id:
            print(f"  ✅ config.id 不同（可能基于uid/key生成）")
        
        return config_url, config_id
    
    return None, None

# 测试
uid = "4059917"
key = "cgklotuyDGHILOTW38"
video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"

config_url, config_id = analyze_paid_key(uid, key, video_url)
```

### 脚本2：测试不同的加密算法

```python
import hashlib
import base64
from Crypto.Cipher import ARC4

def test_encryption_algorithms(uid, key, video_url, target_config_url):
    """测试不同的加密算法"""
    
    # 测试数据
    test_strings = [
        f"{uid}{key}{video_url}",
        f"{uid}{key}",
        f"{key}{video_url}",
        f"{uid}{video_url}",
        f"{key}",
        f"{uid}",
    ]
    
    print("测试不同的加密算法:")
    print(f"目标config.url: {target_config_url[:100]}...")
    print()
    
    for test_str in test_strings:
        print(f"测试字符串: {test_str[:50]}...")
        
        # MD5
        md5_hash = hashlib.md5(test_str.encode()).hexdigest()
        print(f"  MD5: {md5_hash}")
        
        # SHA1
        sha1_hash = hashlib.sha1(test_str.encode()).hexdigest()
        print(f"  SHA1: {sha1_hash[:40]}...")
        
        # Base64
        b64_encoded = base64.b64encode(test_str.encode()).decode()
        print(f"  Base64: {b64_encoded[:50]}...")
        
        # RC4（需要密钥）
        # 可能的密钥：uid, key, uid+key, 等
        possible_keys = [uid, key, f"{uid}{key}", f"{key}{uid}"]
        for rc4_key in possible_keys:
            try:
                cipher = ARC4.new(rc4_key.encode())
                encrypted = cipher.encrypt(test_str.encode())
                b64_encrypted = base64.b64encode(encrypted).decode()
                print(f"  RC4({rc4_key}): {b64_encrypted[:50]}...")
            except:
                pass
        
        print()
```

## 📊 预期结果

### 如果config.url基于uid和key生成

**可能的情况**:
1. **服务器端生成**（最可能）
   - PHP代码在服务器端使用 `uid` 和 `key` 生成 `config.url`
   - 客户端JavaScript只是使用，不生成
   - 需要分析PHP代码或API调用

2. **客户端生成**
   - JavaScript代码使用 `uid` 和 `key` 生成 `config.url`
   - 需要找到生成代码

### 如果config.url是固定的

**可能的情况**:
- `uid` 和 `key` 只是用于验证，不用于生成 `config.url`
- `config.url` 可能是通用的或基于其他参数生成

## 🎯 下一步行动

1. **运行测试脚本**，提取付费版本的 `config.url` 和 `config.id`
2. **对比免费版本**，看是否有差异
3. **分析差异**，确定是否基于 `uid` 和 `key` 生成
4. **查找生成代码**，在PHP或JavaScript中找到加密算法
5. **实现Python版本**，如果可以找到算法

## 📝 注意事项

1. **保护付费key**：不要泄露 `uid` 和 `key`
2. **合法使用**：仅用于学习和研究
3. **遵守服务条款**：不要违反网站的服务条款

