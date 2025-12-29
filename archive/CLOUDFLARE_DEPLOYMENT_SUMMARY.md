# Cloudflare Workers 部署完整指南

## 📋 概述

本指南将帮助您：
1. 提取解析网站的JavaScript代码
2. 分析z参数生成逻辑
3. 部署到Cloudflare Workers

## 🔍 步骤1: 提取JavaScript代码

### 方法1: 捕获iframe中的JavaScript（推荐）

解析网站使用iframe加载实际解析逻辑，需要捕获iframe中的代码：

```bash
python3 capture_iframe_js.py
```

**输出**:
- `captured_iframe_js.json` - 捕获的完整数据
- `extracted_iframe_js/` - iframe中的JavaScript文件

### 方法2: 捕获运行时JavaScript

捕获实际执行的JavaScript代码：

```bash
python3 capture_runtime_js.py
```

**输出**:
- `captured_runtime_js.json` - 运行时捕获的数据

### 方法3: 提取静态JavaScript

提取页面中的静态JavaScript代码：

```bash
python3 extract_js_code.py
```

**输出**:
- `extracted_js_code.json` - 提取结果摘要
- `extracted_js/` - 外部JavaScript文件

## 🔬 步骤2: 分析z参数生成逻辑

### 查看捕获的数据

```bash
# 查看API调用和z参数
cat captured_iframe_js.json | jq '.api_calls'

# 查看iframe中的脚本
ls extracted_iframe_js/
cat extracted_iframe_js/*.js | grep -i "z"
```

### 分析z参数

z参数的特征：
- 32位十六进制字符串（MD5格式）
- 可能是动态生成的
- 每次请求可能不同

**如果找到了生成逻辑**:
- 在 `cloudflare_worker_parser.js` 中实现生成函数
- 更新 `generateZParam()` 函数

**如果未找到生成逻辑**（推荐方案）:
- 使用定期更新的缓存参数
- 从KV存储或环境变量读取

## 🚀 步骤3: 部署到Cloudflare Workers

### 3.1 安装Wrangler

```bash
npm install -g wrangler
# 或
npm install wrangler --save-dev
```

### 3.2 登录Cloudflare

```bash
wrangler login
```

### 3.3 创建项目

```bash
mkdir cloudflare-worker
cd cloudflare-worker
cp ../cloudflare_worker_parser.js .
cp ../wrangler.toml.example wrangler.toml
```

### 3.4 配置wrangler.toml

编辑 `wrangler.toml`:

```toml
name = "video-parser-worker"
main = "cloudflare_worker_parser.js"
compatibility_date = "2024-01-01"

[vars]
DEFAULT_Z_PARAM = "b413af76b43b1a0abc231718862417e2"  # 从captured_iframe_js.json获取
DEFAULT_S1IG_PARAM = "11397"
DEFAULT_G_PARAM = ""
```

### 3.5 部署

```bash
wrangler deploy
```

### 3.6 测试

```bash
# 测试API
curl "https://your-worker.your-subdomain.workers.dev/api/parse?video_url=https://www.iqiyi.com/v_1c168e2yzbk.html"
```

## 🔄 步骤4: 定期更新z参数

### 方案A: 使用GitHub Actions（推荐）

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
        run: python3 capture_iframe_js.py
      
      - name: Extract z param
        id: extract_z
        run: |
          Z_PARAM=$(python3 -c "import json; print(json.load(open('captured_iframe_js.json'))['api_calls'][0]['params']['z'])")
          echo "z_param=$Z_PARAM" >> $GITHUB_OUTPUT
      
      - name: Update Cloudflare Worker
        run: |
          npm install -g wrangler
          wrangler secret put DEFAULT_Z_PARAM <<< "${{ steps.extract_z.outputs.z_param }}"
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
```

### 方案B: 使用Wrangler CLI手动更新

```bash
# 捕获参数
python3 capture_iframe_js.py

# 提取z参数
Z_PARAM=$(python3 -c "import json; print(json.load(open('captured_iframe_js.json'))['api_calls'][0]['params']['z'])")

# 更新环境变量
wrangler secret put DEFAULT_Z_PARAM
# 输入: $Z_PARAM
```

### 方案C: 使用KV存储

```bash
# 创建KV命名空间
wrangler kv:namespace create "Z_PARAMS_KV"

# 更新z参数
wrangler kv:key put "latest_z_param" "新的z参数值" --binding Z_PARAMS_KV
```

## 📊 使用示例

### JavaScript/TypeScript

```javascript
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

### Python

```python
import requests

def parse_video(video_url):
    response = requests.get(
        'https://your-worker.workers.dev/api/parse',
        params={'video_url': video_url}
    )
    return response.json()

# 使用
result = parse_video('https://www.iqiyi.com/v_1c168e2yzbk.html')
if result.get('success'):
    print('m3u8链接:', result['best_m3u8'])
```

## ⚠️ 重要提示

### 1. z参数生成

- **如果找到了生成逻辑**: 在Worker中实现
- **如果未找到**: 使用定期更新的缓存参数（推荐）

### 2. 参数更新频率

- 建议每天或每周更新一次
- 参数失效时会返回错误，需要及时更新

### 3. 成本考虑

- **免费计划**: 每天10万次请求
- **付费计划**: 更高限制
- 建议添加缓存减少API调用

## 📚 相关文件

- `cloudflare_worker_parser.js` - Worker主文件
- `wrangler.toml.example` - 配置文件示例
- `capture_iframe_js.py` - iframe JavaScript捕获工具
- `capture_runtime_js.py` - 运行时JavaScript捕获工具
- `extract_js_code.py` - 静态JavaScript提取工具
- `cloudflare_deployment_guide.md` - 详细部署指南

## 🆘 故障排除

### 问题1: z参数过期

**解决方案**: 运行参数捕获脚本，更新Worker配置

```bash
python3 capture_iframe_js.py
# 提取z参数并更新
wrangler secret put DEFAULT_Z_PARAM
```

### 问题2: 无法找到z参数生成逻辑

**解决方案**: 使用定期更新的缓存参数方案

### 问题3: CORS错误

**解决方案**: Worker已配置CORS，检查请求头

### 问题4: 请求超时

**解决方案**: 优化代码，减少处理时间

## ✅ 检查清单

- [ ] 提取了iframe中的JavaScript代码
- [ ] 分析了z参数生成逻辑（或使用缓存方案）
- [ ] 配置了wrangler.toml
- [ ] 部署了Worker
- [ ] 测试了API
- [ ] 设置了参数自动更新流程
- [ ] 配置了监控和告警

