# 服务器部署指南 - z参数获取

## 📋 概述

在服务器上部署视频解析器时，由于无法使用Playwright等浏览器自动化工具，需要采用其他方式获取z参数。

## ✅ 推荐方案：定期更新参数文件

### 方案说明

在本地（有浏览器的环境）定期捕获参数，然后上传到服务器。这是最简单可靠的方案。

### 实施步骤

#### 1. 本地环境设置

```bash
# 安装依赖
pip install playwright requests brotli
python3 -m playwright install chromium

# 运行参数捕获
python3 capture_api_params.py
```

#### 2. 上传参数文件到服务器

```bash
# 方式1: 使用scp
scp captured_api_params.json user@server:/path/to/project/

# 方式2: 使用rsync
rsync -avz captured_api_params.json user@server:/path/to/project/

# 方式3: 使用Git（如果使用版本控制）
git add captured_api_params.json
git commit -m "Update API params"
git push
# 在服务器上: git pull
```

#### 3. 服务器端使用

解析器会自动从 `captured_api_params.json` 读取参数：

```python
from direct_videocdn_parser_simple import DirectVideoCdnParserSimple

parser = DirectVideoCdnParserSimple()
m3u8_url = parser.parse_video("https://www.iqiyi.com/v_1c168e2yzbk.html")
```

### 自动化更新流程

#### 方案A: 使用Cron定时任务（Linux/Mac）

```bash
# 编辑crontab
crontab -e

# 添加定时任务（每天凌晨2点更新）
0 2 * * * cd /path/to/local/project && python3 capture_api_params.py && scp captured_api_params.json user@server:/path/to/server/project/
```

#### 方案B: 使用GitHub Actions（推荐）

创建 `.github/workflows/update_params.yml`:

```yaml
name: Update API Params

on:
  schedule:
    - cron: '0 2 * * *'  # 每天UTC 2点（北京时间10点）
  workflow_dispatch:  # 允许手动触发

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
      
      - name: Commit and push
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add captured_api_params.json
          git commit -m "Auto-update API params" || exit 0
          git push
```

#### 方案C: 使用脚本 + 定时任务

创建 `update_and_upload.sh`:

```bash
#!/bin/bash
# update_and_upload.sh

LOCAL_PROJECT="/path/to/local/project"
SERVER_USER="user"
SERVER_HOST="server.example.com"
SERVER_PATH="/path/to/server/project"

cd "$LOCAL_PROJECT"

# 捕获参数
echo "捕获API参数..."
python3 capture_api_params.py

# 检查是否成功
if [ -f "captured_api_params.json" ]; then
    echo "上传参数文件到服务器..."
    scp captured_api_params.json "$SERVER_USER@$SERVER_HOST:$SERVER_PATH/"
    
    # 可选：在服务器上测试
    echo "在服务器上测试..."
    ssh "$SERVER_USER@$SERVER_HOST" "cd $SERVER_PATH && python3 direct_videocdn_parser_simple.py"
    
    echo "✅ 参数更新完成"
else
    echo "❌ 参数捕获失败"
    exit 1
fi
```

## 🔄 参数失效处理

### 检测参数是否失效

在解析器中添加参数有效性检测：

```python
def check_params_validity(self):
    """检查参数是否有效"""
    test_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    result = self.parse_video(test_url)
    
    if not result:
        # 参数可能已失效
        return False
    return True
```

### 自动告警

```python
import smtplib
from email.mime.text import MIMEText

def send_alert(message):
    """发送告警邮件"""
    msg = MIMEText(message)
    msg['Subject'] = 'API参数失效告警'
    msg['From'] = 'alert@example.com'
    msg['To'] = 'admin@example.com'
    
    # 发送邮件（需要配置SMTP）
    # smtp.sendmail(...)
```

## 📊 监控和日志

### 记录参数使用情况

```python
import logging
from datetime import datetime

logging.basicConfig(
    filename='parser.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_param_usage(z_param, success):
    """记录参数使用情况"""
    logging.info(f"使用z参数: {z_param[:16]}..., 成功: {success}")
```

### 参数使用统计

```python
import json
from datetime import datetime

def track_param_usage(z_param, success):
    """跟踪参数使用情况"""
    stats_file = 'param_usage_stats.json'
    
    try:
        with open(stats_file, 'r') as f:
            stats = json.load(f)
    except:
        stats = {}
    
    date = datetime.now().strftime('%Y-%m-%d')
    if date not in stats:
        stats[date] = {'total': 0, 'success': 0, 'failed': 0}
    
    stats[date]['total'] += 1
    if success:
        stats[date]['success'] += 1
    else:
        stats[date]['failed'] += 1
    
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
```

## 🚨 故障排除

### 问题1: 参数文件不存在

**解决方案**:
```python
# 在解析器中添加默认值
if not z_value:
    z_value = "b413af76b43b1a0abc231718862417e2"  # 最新已知的有效值
```

### 问题2: 参数已过期

**症状**: API返回"联系QQ"错误信息

**解决方案**:
1. 立即运行 `capture_api_params.py` 更新参数
2. 上传新的参数文件到服务器
3. 重新运行解析器

### 问题3: 无法访问解析网站

**解决方案**:
1. 检查网络连接
2. 检查解析网站是否可访问
3. 使用代理（如果需要）

## 📝 最佳实践

1. **定期更新**: 建议每天或每周更新一次参数
2. **版本控制**: 将参数文件纳入版本控制，便于回滚
3. **监控告警**: 设置监控，参数失效时及时告警
4. **备用方案**: 准备多个备用参数值
5. **日志记录**: 记录参数使用情况，便于分析

## 🔗 相关文档

- [Z_PARAM_SOLUTIONS.md](Z_PARAM_SOLUTIONS.md) - z参数获取方案详解
- [PARAM_CAPTURE_GUIDE.md](PARAM_CAPTURE_GUIDE.md) - 参数捕获指南
- [QUICK_FIX_PARAMS.md](QUICK_FIX_PARAMS.md) - 快速修复参数过期问题

