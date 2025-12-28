# 解决Worker返回type:4000错误

## 🔍 问题分析

Worker返回 `{"type":4000}` 错误，但本地Python脚本可以正常工作。这说明：

1. **z参数仍然有效**（本地测试成功）
2. **API检测到了Cloudflare Workers的请求并拒绝**
3. **代理服务可能没有正确传递请求头**

## 💡 解决方案

### 方案1: 使用不同的代理服务（推荐）

尝试使用其他CORS代理服务：

```javascript
// 使用corsproxy.io
const proxyUrl = `https://corsproxy.io/?${encodeURIComponent(apiUrl)}`;

// 或使用cors-anywhere
const proxyUrl = `https://cors-anywhere.herokuapp.com/${apiUrl}`;
```

### 方案2: 自建代理Worker

创建一个专门的代理Worker，更好地控制请求头：

```javascript
// proxy-worker.js
export default {
  async fetch(request) {
    const url = new URL(request.url);
    const targetUrl = url.searchParams.get('url');
    
    if (!targetUrl) {
      return new Response('缺少url参数', { status: 400 });
    }
    
    const response = await fetch(targetUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': '*/*',
        'Referer': 'https://m1-z2.cloud.nnpp.vip:2223/',
        'Origin': 'https://m1-z2.cloud.nnpp.vip:2223',
      }
    });
    
    return response;
  }
}
```

### 方案3: 使用本地服务器作为中间层

在本地运行一个简单的代理服务器，然后Worker调用本地服务器：

```python
# local_proxy.py
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    response = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0...',
        'Referer': 'https://m1-z2.cloud.nnpp.vip:2223/',
    })
    return response.text, response.status_code
```

### 方案4: 直接从客户端调用（绕过Worker）

如果Worker无法工作，可以考虑从客户端直接调用解析API：

```javascript
// 客户端代码
async function parseVideo(videoUrl) {
  // 直接调用解析API（需要处理CORS）
  const apiUrl = `https://m1-a1.cloud.nnpp.vip:2223/api/v/?z=${zParam}&jx=${videoUrl}&s1ig=11397&g=`;
  
  // 使用代理服务
  const proxyUrl = `https://api.allorigins.win/get?url=${encodeURIComponent(apiUrl)}`;
  const response = await fetch(proxyUrl);
  const data = await response.json();
  return JSON.parse(data.contents);
}
```

## 🔧 当前问题

从测试结果看：
- **本地Python脚本**: ✅ 可以正常工作
- **通过代理访问**: ❌ 返回 `{"type":4000}`
- **直接访问**: 需要测试

这说明API可能：
1. 检测到了代理请求并拒绝
2. 需要特定的请求头（代理可能没有传递）
3. 有反爬虫机制

## 📝 建议

1. **优先使用本地Python脚本**（已验证可用）
2. **如果需要Worker，考虑自建代理服务**
3. **或者使用其他解析服务**

## 🚀 快速修复

如果急需使用Worker，可以：

1. **使用本地服务器作为中间层**（最简单）
2. **使用其他CORS代理服务**
3. **自建代理Worker**

