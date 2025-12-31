# 付费Key最终分析结果

## 🎯 关键发现

### ✅ 确认：Hash和Token都基于video_url生成

**测试结果**：
- 不同video_url的Hash不同 ✅
- 不同video_url的Token不同 ✅

**结论**：
- Hash和Token的生成算法都依赖于video_url
- 需要找到具体的生成方式

## 📊 Hash分析

### 测试数据

| Video URL | Hash |
|-----------|------|
| `https://www.iqiyi.com/v_1c168e2yzbk.html` | `2089c333a6d6a31e306bd190557aea36` |
| `https://www.iqiyi.com/v_19rr7qhfg0.html` | `aeaf87d55e9fd0251470c951429cde13` |

### Hash特征

- **长度**：32字符（MD5格式）
- **格式**：十六进制字符串
- **变化**：不同video_url的hash不同

### 可能的生成方式

1. **MD5(video_url)** - 但测试未匹配
2. **MD5(uid + key + video_url)** - 但测试未匹配
3. **MD5(服务器端数据 + video_url)** - 可能包含数据库记录ID
4. **其他算法** - SHA1、SHA256等，但长度不符合

## 📊 Token分析

### 测试数据

| Video URL | Token (前50字符) |
|-----------|------------------|
| `https://www.iqiyi.com/v_1c168e2yzbk.html` | `d3d376e44505b4448705e6f20564368367264405b4474377b4...` |
| `https://www.iqiyi.com/v_19rr7qhfg0.html` | `d3d37727b4a6a62473873466576713b603b253559397359723...` |

### Token特征

- **长度**：176字符（88字节）
- **格式**：十六进制字符串
- **变化**：不同video_url的token不同
- **前缀**：两个token都以 `d3d3` 开头

### Token格式分析

**相同前缀**：
- 两个token都以 `d3d3` 开头
- 说明token可能包含固定的部分（如uid/key）和变化的部分（如video_url）

**可能的生成方式**：
1. **加密算法**：RC4、AES等
2. **签名算法**：HMAC-MD5、HMAC-SHA1等
3. **组合方式**：固定部分 + 加密的变化部分

## 🔍 进一步分析建议

### 1. 分析Token的固定部分

**观察**：
- Token1: `d3d376e44505b4448705e6f20564368367264405b4474377b4...`
- Token2: `d3d37727b4a6a62473873466576713b603b253559397359723...`

**分析**：
- 都以 `d3d3` 开头
- 可能是固定的前缀或标识符
- 后续部分可能包含加密的数据

### 2. 测试更多视频URL

**建议**：
- 测试更多不同的视频URL
- 观察hash和token的变化规律
- 找出生成模式

### 3. 分析服务器端代码

**如果可能**：
- 分析PHP代码中的生成逻辑
- 查找hash和token的生成函数
- 理解完整的生成流程

## 💡 实用方案

### 方案1：直接使用API（推荐）⭐

**优点**：
- ✅ 不需要逆向算法
- ✅ 简单可靠
- ✅ 直接可用

**实现**：
```python
import requests
import re

def get_m3u8_url(uid, key, video_url):
    """
    获取m3u8 URL
    
    参数:
        uid: 用户ID
        key: API密钥
        video_url: 视频URL
    
    返回:
        m3u8 URL或None
    """
    url = f"https://json.2s0.cn:5678/player/analysis.php/?uid={uid}&key={key}&url={video_url}"
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            html = response.text
            
            # 提取m3u8 URL
            m3u8_match = re.search(r'var url = "([^"]+)"', html)
            if m3u8_match:
                return m3u8_match.group(1)
    except Exception as e:
        print(f"错误: {e}")
    
    return None

# 使用示例
uid = "4059917"
key = "cgklotuyDGHILOTW38"
video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"

m3u8_url = get_m3u8_url(uid, key, video_url)
if m3u8_url:
    print(f"m3u8 URL: {m3u8_url}")
```

### 方案2：继续分析算法（如果希望完全自动化）

**步骤**：
1. 测试更多视频URL，找出hash和token的生成规律
2. 分析token的固定部分和变化部分
3. 尝试不同的加密算法和组合方式
4. 如果找到算法，实现Python版本

## 📝 总结

### ✅ 已确认

1. **Hash和Token都基于video_url生成**
2. **Hash格式**：32字符，MD5格式
3. **Token格式**：176字符，十六进制格式
4. **Token前缀**：都以 `d3d3` 开头

### ❓ 待确认

1. **Hash的生成算法**（可能是MD5，但输入字符串未知）
2. **Token的生成算法**（可能是加密或签名）
3. **Token的固定部分和变化部分**

### 🎯 推荐

**当前阶段**：使用API调用方式（方案1）

**原因**：
- 简单可靠
- 不需要逆向算法
- 可以直接使用

**未来**：如果希望完全自动化，可以继续分析算法

## 📚 相关文件

- `test_different_video_urls.py` - 测试不同视频URL的脚本
- `analyze_hash_token_pattern.py` - 分析hash和token规律的脚本
- `PAID_KEY_ANALYSIS_SUMMARY.md` - 完整分析总结

