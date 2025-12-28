# Cloudflare Workers 最终解决方案

## 📋 分析结果

经过JavaScript代码提取和分析，发现：

1. **解析网站使用React应用**: iframe中加载的是React单页应用
2. **主要代码在**: `/static/js/main.1336e445.js` (压缩/混淆)
3. **z参数已捕获**: `b413af76b43b1a0abc231718862417e2`
4. **代码已混淆**: 主要JavaScript代码经过压缩和混淆，难以直接提取生成逻辑

## ✅ 推荐方案：使用定期更新的缓存参数

由于z参数生成逻辑在混淆的JavaScript中，**最实用的方案是使用定期更新的缓存参数**。

## 🚀 部署步骤

### 步骤1: 准备Worker代码

使用已提供的 `cloudflare_worker_parser.js`，它已经实现了：
- ✅ 从环境变量读取z参数
- ✅ 调用解析API
- ✅ 提取m3u8链接
- ✅ CORS支持

### 步骤2: 配置wrangler.toml

```toml
name = "video-parser-worker"
main = "cloudflare_worker_parser.js"
compatibility_date = "2024-01-01"

[vars]
DEFAULT_Z_PARAM = "b413af76b43b1a0abc231718862417e2"  # 从captured_iframe_js.json获取
DEFAULT_S1IG_PARAM = "11397"
DEFAULT_G_PARAM = ""
```

### 步骤3: 部署

```bash
# 安装Wrangler
npm install -g wrangler

# 登录
wrangler login

# 部署
wrangler deploy
```

### 步骤4: 测试

```bash
curl "https://your-worker.workers.dev/api/parse?video_url=https://www.iqiyi.com/v_1c168e2yzbk.html"
```

## 🔄 定期更新z参数

### 方案A: 使用GitHub Actions（推荐）

创建 `.github/workflows/update_cloudflare_params.yml`:

```yaml
name: Update Cloudflare Worker Params

on:
  schedule:
    - cron: '0 2 * * *'  # 每天UTC 2点（北京时间10点）
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
          Z_PARAM=$(python3 -c "
          import json
          data = json.load(open('captured_iframe_js.json'))
          for call in data['api_calls']:
              if 'z' in call.get('params', {}):
                  print(call['params']['z'])
                  break
          ")
          echo "z_param=$Z_PARAM" >> $GITHUB_OUTPUT
      
      - name: Update Cloudflare Worker
        run: |
          npm install -g wrangler
          wrangler secret put DEFAULT_Z_PARAM <<< "${{ steps.extract_z.outputs.z_param }}"
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
```

### 方案B: 手动更新

```bash
# 1. 捕获参数
python3 capture_iframe_js.py

# 2. 提取z参数
Z_PARAM=$(python3 -c "
import json
data = json.load(open('captured_iframe_js.json'))
for call in data['api_calls']:
    if 'z' in call.get('params', {}):
        print(call['params']['z'])
        break
")

# 3. 更新Worker
wrangler secret put DEFAULT_Z_PARAM
# 输入: $Z_PARAM
```

### 方案C: 使用KV存储

```bash
# 创建KV命名空间
wrangler kv:namespace create "Z_PARAMS_KV"

# 更新wrangler.toml
# [[kv_namespaces]]
# binding = "Z_PARAMS_KV"
# id = "your-kv-namespace-id"

# 更新z参数
wrangler kv:key put "latest_z_param" "$Z_PARAM" --binding Z_PARAMS_KV
```

## 📝 Worker代码说明

`cloudflare_worker_parser.js` 已经实现了：

1. **参数获取优先级**:
   - 首先尝试从KV存储读取
   - 然后从环境变量读取
   - 最后使用默认值

2. **API调用**:
   - 构造API URL
   - 发送请求
   - 处理响应（包括压缩）

3. **m3u8提取**:
   - 递归查找m3u8链接
   - 返回最佳链接

## 🎯 使用示例

### JavaScript

```javascript
const response = await fetch(
  'https://your-worker.workers.dev/api/parse?video_url=' + 
  encodeURIComponent('https://www.iqiyi.com/v_1c168e2yzbk.html')
);
const result = await response.json();
console.log(result.best_m3u8);
```

### Python

```python
import requests

response = requests.get(
  'https://your-worker.workers.dev/api/parse',
  params={'video_url': 'https://www.iqiyi.com/v_1c168e2yzbk.html'}
)
result = response.json()
print(result['best_m3u8'])
```

## ⚠️ 重要提示

1. **z参数会定期过期**: 建议每天或每周更新一次
2. **监控参数有效性**: 如果API返回错误，立即更新参数
3. **使用缓存**: Worker已配置缓存，减少API调用
4. **成本控制**: 免费计划每天10万次请求

## 📚 相关文件

- `cloudflare_worker_parser.js` - Worker主文件
- `wrangler.toml.example` - 配置文件示例
- `capture_iframe_js.py` - 参数捕获工具
- `cloudflare_deployment_guide.md` - 详细部署指南

## ✅ 总结

虽然无法直接提取z参数的生成逻辑（代码已混淆），但通过**定期更新缓存参数**的方案，可以成功部署到Cloudflare Workers。这个方案：

- ✅ 简单可靠
- ✅ 无需反混淆JavaScript
- ✅ 可以自动化更新
- ✅ 适合生产环境

