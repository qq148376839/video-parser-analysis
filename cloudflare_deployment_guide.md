# Cloudflare Workers 部署指南

## 📋 概述

将视频解析器部署到Cloudflare Workers，实现无服务器、全球加速的解析服务。

## 🎯 优势

- ✅ **无服务器**: 无需管理服务器
- ✅ **全球加速**: Cloudflare的全球CDN网络
- ✅ **自动扩展**: 自动处理高并发
- ✅ **免费额度**: 每天10万次请求（免费计划）
- ✅ **低延迟**: 边缘计算，就近响应

## 📝 前置准备

### 1. 提取JavaScript代码

解析网站使用iframe加载实际解析逻辑，需要捕获iframe中的JavaScript：

```bash
# 方法1: 捕获iframe中的JavaScript（推荐）
python3 capture_iframe_js.py

# 方法2: 捕获运行时JavaScript
python3 capture_runtime_js.py

# 方法3: 提取静态JavaScript
python3 extract_js_code.py

# 查看提取结果
cat captured_iframe_js.json
ls extracted_iframe_js/
```

### 2. 分析z参数生成逻辑

查看提取的JavaScript代码，找到z参数的生成方式：

```bash
# 搜索z参数相关代码
grep -r "z=" extracted_iframe_js/
grep -r "api/v" extracted_iframe_js/

# 查看捕获的API调用
cat captured_iframe_js.json | jq '.api_calls'
```

**注意**: 如果无法找到z参数的生成逻辑（可能是动态生成或混淆），可以使用以下方案：
- 使用定期更新的缓存参数（推荐）
- 使用外部API服务获取z参数

## 🚀 部署步骤

### 步骤1: 安装Wrangler CLI

```bash
npm install -g wrangler
# 或
npm install wrangler --save-dev
```

### 步骤2: 登录Cloudflare

```bash
wrangler login
```

### 步骤3: 创建Worker项目

```bash
# 创建新项目
wrangler init video-parser-worker

# 或使用现有文件
mkdir cloudflare-worker
cd cloudflare-worker
```

### 步骤4: 配置wrangler.toml

创建 `wrangler.toml`:

```toml
name = "video-parser-worker"
main = "cloudflare_worker_parser.js"
compatibility_date = "2024-01-01"

# 如果需要使用KV存储（存储z参数）
# [[kv_namespaces]]
# binding = "Z_PARAMS_KV"
# id = "your-kv-namespace-id"

# 环境变量（存储z参数等）
[vars]
DEFAULT_Z_PARAM = "b413af76b43b1a0abc231718862417e2"
DEFAULT_S1IG_PARAM = "11397"
```

### 步骤5: 部署Worker

```bash
# 部署到生产环境
wrangler deploy

# 或部署到预览环境
wrangler deploy --env preview
```

## 🔧 配置z参数

### 方案1: 使用环境变量（推荐）

在 `wrangler.toml` 中配置：

```toml
[vars]
DEFAULT_Z_PARAM = "b413af76b43b1a0abc231718862417e2"
DEFAULT_S1IG_PARAM = "11397"
```

在代码中读取：

```javascript
const zParam = env.DEFAULT_Z_PARAM || await generateZParam(videoUrl);
```

### 方案2: 使用KV存储

创建KV命名空间：

```bash
# 创建KV命名空间
wrangler kv:namespace create "Z_PARAMS_KV"
wrangler kv:namespace create "Z_PARAMS_KV" --preview
```

更新 `wrangler.toml`:

```toml
[[kv_namespaces]]
binding = "Z_PARAMS_KV"
id = "your-kv-namespace-id"
preview_id = "your-preview-kv-namespace-id"
```

在代码中使用：

```javascript
async function getCachedZParam(env) {
  return await env.Z_PARAMS_KV.get('latest_z_param');
}

async function updateZParam(env, zParam) {
  await env.Z_PARAMS_KV.put('latest_z_param', zParam);
}
```

### 方案3: 使用外部API

如果z参数需要动态生成，可以调用外部API：

```javascript
async function generateZParam(videoUrl) {
  // 调用外部API获取z参数
  const response = await fetch('https://your-api.com/get_z_param?video_url=' + encodeURIComponent(videoUrl));
  const data = await response.json();
  return data.z_param;
}
```

## 📊 更新z参数

### 方法1: 使用Wrangler CLI更新KV

```bash
# 更新z参数
wrangler kv:key put "latest_z_param" "新的z参数值" --binding Z_PARAMS_KV
```

### 方法2: 使用API更新

创建更新API端点：

```javascript
// 在worker中添加更新端点
if (url.pathname === '/api/update_z_param') {
  const authToken = request.headers.get('Authorization');
  if (authToken !== 'Bearer YOUR_SECRET_TOKEN') {
    return new Response('Unauthorized', { status: 401 });
  }
  
  const { z_param } = await request.json();
  await env.Z_PARAMS_KV.put('latest_z_param', z_param);
  
  return new Response(JSON.stringify({ success: true }));
}
```

### 方法3: 使用GitHub Actions自动更新

创建 `.github/workflows/update_cloudflare_params.yml`:

```yaml
name: Update Cloudflare Worker Params

on:
  schedule:
    - cron: '0 2 * * *'  # 每天UTC 2点
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install playwright requests brotli
          python3 -m playwright install chromium
      
      - name: Capture API params
        run: python3 capture_api_params.py
      
      - name: Extract z param
        id: extract_z
        run: |
          Z_PARAM=$(python3 -c "import json; print(json.load(open('captured_api_params.json'))['captured_params'][-1]['z'])")
          echo "z_param=$Z_PARAM" >> $GITHUB_OUTPUT
      
      - name: Update Cloudflare KV
        run: |
          npm install -g wrangler
          wrangler kv:key put "latest_z_param" "${{ steps.extract_z.outputs.z_param }}" --binding Z_PARAMS_KV
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
```

## 🧪 测试

### 本地测试

```bash
# 使用Wrangler本地开发服务器
wrangler dev

# 测试API
curl "http://localhost:8787/api/parse?video_url=https://www.iqiyi.com/v_1c168e2yzbk.html"
```

### 生产环境测试

```bash
# 部署后测试
curl "https://your-worker.your-subdomain.workers.dev/api/parse?video_url=https://www.iqiyi.com/v_1c168e2yzbk.html"
```

## 📝 完整示例

### 1. 项目结构

```
cloudflare-worker/
├── cloudflare_worker_parser.js  # Worker主文件
├── wrangler.toml                # 配置文件
└── package.json                 # 依赖（可选）
```

### 2. 使用示例

```javascript
// 前端调用
async function parseVideo(videoUrl) {
  const response = await fetch(
    'https://your-worker.workers.dev/api/parse?video_url=' + 
    encodeURIComponent(videoUrl)
  );
  const result = await response.json();
  return result;
}

// 使用
const result = await parseVideo('https://www.iqiyi.com/v_1c168e2yzbk.html');
if (result.success) {
  console.log('m3u8链接:', result.best_m3u8);
}
```

## ⚠️ 注意事项

### 1. z参数生成

- **关键问题**: z参数是JavaScript动态生成的
- **解决方案**: 
  - 如果找到了生成逻辑，在Worker中实现
  - 否则使用定期更新的缓存参数

### 2. 请求限制

- **免费计划**: 每天10万次请求
- **付费计划**: 更高限制
- **建议**: 添加缓存减少API调用

### 3. 超时限制

- **免费计划**: 10秒CPU时间，30秒总时间
- **付费计划**: 更高限制
- **建议**: 优化代码，避免长时间运行

### 4. CORS配置

Worker已配置CORS，支持跨域请求。

## 🔄 自动化流程

### 定期更新z参数

1. **本地捕获参数** (使用Playwright)
2. **上传到Cloudflare KV** (使用Wrangler或API)
3. **Worker自动使用新参数**

### 监控和告警

```javascript
// 在Worker中添加监控
if (!result.success && result.error.includes('参数已过期')) {
  // 发送告警（使用外部服务）
  await fetch('https://your-monitoring-service.com/alert', {
    method: 'POST',
    body: JSON.stringify({ error: 'z参数已过期' })
  });
}
```

## 📚 相关资源

- [Cloudflare Workers文档](https://developers.cloudflare.com/workers/)
- [Wrangler CLI文档](https://developers.cloudflare.com/workers/wrangler/)
- [KV存储文档](https://developers.cloudflare.com/workers/runtime-apis/kv/)

## 🆘 故障排除

### 问题1: z参数过期

**解决方案**: 运行参数捕获脚本，更新KV存储

```bash
python3 capture_api_params.py
wrangler kv:key put "latest_z_param" "新的z参数值" --binding Z_PARAMS_KV
```

### 问题2: 请求超时

**解决方案**: 优化代码，减少处理时间

### 问题3: CORS错误

**解决方案**: 检查Worker的CORS配置

