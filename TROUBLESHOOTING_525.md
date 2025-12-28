# 解决525错误（SSL Handshake Failed）

## 🔍 问题分析

525错误表示"SSL Handshake Failed"，通常发生在Cloudflare Workers尝试连接到外部API时。

### 可能的原因

1. **目标服务器SSL证书问题**: `m1-a1.cloud.nnpp.vip:2223` 的SSL证书可能有问题
2. **Cloudflare无法验证证书**: Workers可能无法验证某些自签名或过期的证书
3. **端口问题**: 使用非标准端口(2223)可能导致SSL握手问题
4. **防火墙/安全策略**: 目标服务器可能阻止了来自Cloudflare的请求

## 💡 解决方案

### 方案1: 使用HTTP而不是HTTPS（如果支持）

如果目标服务器支持HTTP，可以尝试使用HTTP：

```javascript
// 将 https:// 改为 http://
const apiUrl = apiUrl.replace('https://', 'http://');
```

**注意**: 这可能会降低安全性，但可以绕过SSL问题。

### 方案2: 使用代理服务

创建一个中间代理服务来处理SSL问题：

```javascript
// 使用第三方代理服务
const proxyUrl = `https://api.allorigins.win/get?url=${encodeURIComponent(apiUrl)}`;
const response = await fetch(proxyUrl);
```

### 方案3: 使用Cloudflare Tunnel或Pages Functions

如果可能，将解析逻辑移到支持更灵活SSL配置的环境。

### 方案4: 检查目标服务器SSL配置

```bash
# 检查SSL证书
openssl s_client -connect m1-a1.cloud.nnpp.vip:2223 -showcerts

# 检查TLS版本支持
nmap --script ssl-enum-ciphers -p 2223 m1-a1.cloud.nnpp.vip
```

### 方案5: 使用不同的API端点

如果可能，尝试使用不同的API端点或服务器。

## 🔧 临时解决方案

### 修改Worker代码使用HTTP

如果目标服务器支持HTTP访问，可以修改代码：

```javascript
// 在 constructApiUrl 函数中
function constructApiUrl(videoUrl, zParam, s1igParam, gParam) {
  // 尝试使用HTTP
  const baseUrl = "http://m1-a1.cloud.nnpp.vip:2223/api/v/";
  // 或使用不同的服务器
  // const baseUrl = "https://m1-z2.cloud.nnpp.vip:2223/api/v/";
  
  const params = new URLSearchParams({
    z: zParam,
    jx: videoUrl,
    s1ig: s1igParam,
    g: gParam
  });
  return `${baseUrl}?${params.toString()}`;
}
```

## 📝 调试步骤

1. **检查API URL是否正确**:
   ```javascript
   console.log('API URL:', apiUrl);
   ```

2. **测试直接访问**:
   ```bash
   curl "https://m1-a1.cloud.nnpp.vip:2223/api/v/?z=b413af76b43b1a0abc231718862417e2&jx=https://www.iqiyi.com/v_1c168e2yzbk.html&s1ig=11397&g="
   ```

3. **检查SSL证书**:
   ```bash
   openssl s_client -connect m1-a1.cloud.nnpp.vip:2223
   ```

4. **查看Worker日志**:
   ```bash
   wrangler tail
   ```

## ⚠️ 重要提示

525错误通常是**目标服务器的问题**，而不是Worker代码的问题。可能的解决方案：

1. **联系目标服务器管理员**: 检查SSL配置
2. **使用替代API端点**: 如果有其他可用的服务器
3. **使用代理服务**: 通过第三方代理访问
4. **降级到HTTP**: 如果安全要求允许

## 🔄 替代方案

如果无法解决525错误，可以考虑：

1. **使用本地服务器**: 在本地运行解析服务，然后通过Worker调用
2. **使用其他解析服务**: 寻找支持HTTPS的替代服务
3. **使用Cloudflare Pages Functions**: 可能有不同的SSL处理方式

## 📚 相关资源

- [Cloudflare 525错误文档](https://support.cloudflare.com/hc/en-us/articles/115003011431-Troubleshooting-Cloudflare-5XX-errors#525error)
- [Cloudflare Workers SSL/TLS](https://developers.cloudflare.com/workers/runtime-apis/fetch/)

