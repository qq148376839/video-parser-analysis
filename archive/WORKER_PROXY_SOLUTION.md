# Cloudflare Workers 520/525错误解决方案

## 🔍 问题分析

520/525错误表示Cloudflare Workers无法连接到目标服务器。这通常是因为：

1. **目标服务器阻止了Cloudflare的请求**
2. **SSL/TLS配置不兼容**
3. **目标服务器检测到自动化请求并拒绝**
4. **网络连接问题**

## 💡 解决方案：使用代理服务

由于直接连接可能被阻止，可以使用代理服务来绕过这个问题。

### 方案1: 使用CORS代理服务

修改Worker代码，使用CORS代理：

```javascript
// 使用CORS代理服务
async function callParserApiWithProxy(apiUrl) {
  // 使用allorigins.win作为代理
  const proxyUrl = `https://api.allorigins.win/get?url=${encodeURIComponent(apiUrl)}`;
  
  const response = await fetch(proxyUrl);
  const data = await response.json();
  
  // 解析代理返回的内容
  const content = data.contents;
  return JSON.parse(content);
}
```

### 方案2: 使用自己的代理服务器

如果可能，创建一个简单的代理服务器：

```python
# proxy_server.py
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': '缺少url参数'}), 400
    
    try:
        response = requests.get(url, timeout=30)
        return response.text, response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### 方案3: 使用Cloudflare Workers作为代理

创建一个专门的代理Worker：

```javascript
// proxy-worker.js
export default {
  async fetch(request) {
    const url = new URL(request.url);
    const targetUrl = url.searchParams.get('url');
    
    if (!targetUrl) {
      return new Response('缺少url参数', { status: 400 });
    }
    
    try {
      const response = await fetch(targetUrl, {
        headers: {
          'User-Agent': 'Mozilla/5.0...',
        }
      });
      
      return response;
    } catch (error) {
      return new Response(`代理错误: ${error.message}`, { status: 500 });
    }
  }
}
```

## 🔧 修改现有Worker

### 选项1: 集成CORS代理

修改 `callParserApi` 函数：

```javascript
async function callParserApi(apiUrl, useProxy = false) {
  let finalUrl = apiUrl;
  
  if (useProxy) {
    // 使用CORS代理
    finalUrl = `https://api.allorigins.win/get?url=${encodeURIComponent(apiUrl)}`;
  }
  
  const response = await fetch(finalUrl, {
    method: 'GET',
    headers: {
      'User-Agent': 'Mozilla/5.0...',
    }
  });
  
  if (useProxy) {
    const data = await response.json();
    return JSON.parse(data.contents);
  }
  
  return response.json();
}
```

### 选项2: 添加代理重试逻辑

```javascript
// 主处理函数中
let apiResponse;
try {
  // 先尝试直接连接
  apiResponse = await callParserApi(apiUrl, false);
} catch (error) {
  if (error.message.includes('520') || error.message.includes('525')) {
    // 如果直接连接失败，使用代理
    console.log('直接连接失败，使用代理...');
    apiResponse = await callParserApi(apiUrl, true);
  } else {
    throw error;
  }
}
```

## 📝 推荐的CORS代理服务

1. **allorigins.win**: `https://api.allorigins.win/get?url=`
2. **corsproxy.io**: `https://corsproxy.io/?`
3. **cors-anywhere**: `https://cors-anywhere.herokuapp.com/`

## ⚠️ 注意事项

1. **代理服务的限制**: 免费代理服务可能有速率限制
2. **安全性**: 确保代理服务是可信的
3. **性能**: 使用代理会增加延迟
4. **可靠性**: 代理服务可能不稳定

## 🚀 实施步骤

1. **测试代理服务**: 先测试代理服务是否可用
2. **修改Worker代码**: 添加代理支持
3. **部署测试**: 部署并测试
4. **监控**: 监控代理服务的可用性

## 🔄 备用方案

如果代理也不工作，可以考虑：

1. **使用本地服务器**: 在本地运行解析服务
2. **使用其他解析服务**: 寻找支持HTTPS的替代服务
3. **直接调用**: 从客户端直接调用解析API（绕过Worker）

