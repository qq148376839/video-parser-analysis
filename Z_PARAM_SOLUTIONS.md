# z参数获取方案（服务器端无浏览器环境）

## 📋 问题说明

在服务器上运行时，无法使用Playwright等浏览器自动化工具，需要找到其他方式获取z参数。

## 🔍 z参数分析

### 参数特征
- **格式**: 32位十六进制字符串（MD5哈希格式）
- **示例**: `b413af76b43b1a0abc231718862417e2`
- **特点**: 可能是动态生成的，每次请求可能不同

### 可能的生成方式
1. **MD5哈希**: 对某些字符串进行MD5加密
2. **动态生成**: 包含时间戳或其他动态值
3. **JavaScript计算**: 需要执行JavaScript代码生成

## 💡 解决方案

### 方案1: HTTP请求提取（备用方案）

通过HTTP请求解析网站，从HTML/JavaScript中提取z参数。

**优点**:
- ✅ 无需浏览器
- ✅ 轻量级
- ✅ 适合服务器环境

**缺点**:
- ⚠️ 如果z参数是JavaScript动态生成的，**通常无法提取**（已验证）
- ⚠️ 需要解析网站返回包含z参数的HTML或JavaScript代码

**实现**:

```python
# 使用 z_param_api_service.py
python z_param_api_service.py

# 调用API
curl "http://localhost:5000/api/get_z_param?video_url=https://www.iqiyi.com/v_1c168e2yzbk.html"
```

**代码示例**:

```python
from z_param_api_service import get_z_param_from_website

video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
z_param = get_z_param_from_website(video_url)

if z_param:
    print(f"✅ 获取到z参数: {z_param}")
else:
    print("❌ 无法获取z参数")
```

### 方案2: 定期更新参数文件（推荐⭐）

在本地使用Playwright捕获参数，然后上传到服务器。

**优点**:
- ✅ 简单可靠
- ✅ 不需要在服务器上运行浏览器
- ✅ 已验证可行
- ✅ 解析器已支持自动读取

**缺点**:
- ⚠️ 需要定期手动更新（建议每天或每周）
- ⚠️ 参数可能有时效性

**实现步骤**:

```bash
# 1. 在本地（有浏览器的环境）运行参数捕获
python3 capture_api_params.py

# 2. 上传 captured_api_params.json 到服务器
scp captured_api_params.json user@server:/path/to/project/

# 3. 在服务器上运行解析器（会自动读取参数）
python3 direct_videocdn_parser_simple.py
```

**自动化脚本**:

```bash
#!/bin/bash
# update_params.sh - 定期更新参数并上传到服务器

# 在本地运行
cd /path/to/local/project
python3 capture_api_params.py

# 上传到服务器
scp captured_api_params.json user@server:/path/to/server/project/

# 可选：在服务器上测试
ssh user@server "cd /path/to/server/project && python3 direct_videocdn_parser_simple.py"
```

**实现**:

```bash
# 1. 在本地运行参数捕获
python3 capture_api_params.py

# 2. 上传 captured_api_params.json 到服务器

# 3. 解析器会自动读取参数
python3 direct_videocdn_parser_simple.py
```

### 方案3: 使用Node.js执行JavaScript

如果找到了z参数的生成逻辑，可以使用Node.js执行JavaScript代码。

**优点**:
- ✅ 可以执行复杂的JavaScript逻辑
- ✅ 无需浏览器

**缺点**:
- ⚠️ 需要找到生成逻辑
- ⚠️ 需要Node.js环境

**实现**:

```python
import subprocess
import json

def get_z_param_with_nodejs(video_url: str, js_code: str) -> str:
    """使用Node.js执行JavaScript代码获取z参数"""
    # 创建临时JS文件
    js_file = 'temp_z_param.js'
    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(js_code)
        f.write(f'\nconsole.log(JSON.stringify({{z: generateZParam("{video_url}")}}));')
    
    # 执行Node.js
    result = subprocess.run(['node', js_file], capture_output=True, text=True)
    
    # 解析结果
    data = json.loads(result.stdout)
    return data['z']
```

### 方案4: 使用Selenium Grid或远程浏览器

使用远程浏览器服务（如Selenium Grid、Browserless等）。

**优点**:
- ✅ 可以在服务器上运行
- ✅ 可以执行JavaScript

**缺点**:
- ⚠️ 需要额外的服务
- ⚠️ 资源消耗较大

**实现**:

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# 连接到远程浏览器
options = webdriver.ChromeOptions()
driver = webdriver.Remote(
    command_executor='http://selenium-grid:4444/wd/hub',
    options=options
)

# 访问页面并提取z参数
driver.get(parser_url)
z_param = driver.execute_script("return window._zParam;")
```

## 🚀 推荐方案

### 对于服务器环境

**首选**: 方案2（定期更新参数文件）+ 方案1（API服务）的组合

1. **主要使用方案2**: 定期在本地捕获参数，上传到服务器
   - 优点：简单可靠，不需要在服务器上运行浏览器
   - 缺点：需要定期手动更新
   
2. **备用方案1**: 如果参数文件过期，使用API服务获取
   - 需要先运行 `z_param_api_service.py`
   - 如果z参数是JavaScript动态生成的，可能无法提取

3. **监控和告警**: 如果两种方案都失败，发送告警通知

### 实现示例

```python
class ZParamProvider:
    """z参数提供者 - 多种方式获取z参数"""
    
    def __init__(self):
        self.cached_params = self.load_cached_params()
    
    def get_z_param(self, video_url: str) -> Optional[str]:
        """获取z参数 - 尝试多种方式"""
        # 方式1: 从缓存文件读取
        if self.cached_params:
            z_param = self.cached_params.get('z')
            if z_param:
                return z_param
        
        # 方式2: 通过HTTP请求提取
        z_param = get_z_param_from_website(video_url)
        if z_param:
            # 更新缓存
            self.save_cached_params({'z': z_param})
            return z_param
        
        # 方式3: 使用默认值（可能已过期）
        return self.get_default_z_param()
    
    def load_cached_params(self) -> Optional[Dict]:
        """从文件加载缓存的参数"""
        try:
            with open('captured_api_params.json', 'r') as f:
                data = json.load(f)
                if data.get('captured_params'):
                    return data['captured_params'][-1]
        except:
            pass
        return None
    
    def save_cached_params(self, params: Dict):
        """保存参数到缓存"""
        try:
            with open('cached_z_params.json', 'w') as f:
                json.dump(params, f)
        except:
            pass
    
    def get_default_z_param(self) -> str:
        """获取默认z参数（可能已过期）"""
        return "b413af76b43b1a0abc231718862417e2"
```

## 📝 使用指南

### 1. 安装依赖

```bash
# 方案1需要的依赖
pip install requests flask

# 方案3需要的依赖（如果使用Node.js）
# 需要安装Node.js: https://nodejs.org/
```

### 2. 启动API服务（方案1）

```bash
python z_param_api_service.py
```

### 3. 在解析器中使用

```python
from z_param_api_service import get_z_param_from_website

# 获取z参数
video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
z_param = get_z_param_from_website(video_url)

# 使用z参数调用API
parser = DirectVideoCdnParserSimple()
m3u8_url = parser.parse_video(video_url, z_value=z_param)
```

## 🔄 自动化流程

### 定期更新参数

```bash
# 创建定时任务（crontab）
# 每天凌晨2点更新参数
0 2 * * * cd /path/to/project && python3 capture_api_params.py
```

### 监控和告警

```python
def check_z_param_validity():
    """检查z参数是否有效"""
    test_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    z_param = get_z_param_from_website(test_url)
    
    if not z_param:
        # 发送告警
        send_alert("z参数获取失败，需要手动更新")
        return False
    
    # 测试z参数是否有效
    parser = DirectVideoCdnParserSimple()
    result = parser.parse_video(test_url, z_value=z_param)
    
    if not result:
        send_alert("z参数可能已过期")
        return False
    
    return True
```

## ⚠️ 注意事项

1. **参数时效性**: z参数可能定期过期，需要定期更新
2. **反爬虫机制**: 解析网站可能有反爬虫机制，需要适当的请求头
3. **JavaScript执行**: 如果z参数是JavaScript动态生成的，HTTP提取可能失败
4. **备用方案**: 建议同时使用多种方案，确保可靠性

## 📚 相关文件

- `z_param_api_service.py` - HTTP请求提取z参数的API服务
- `analyze_z_param_generation.py` - 分析z参数生成逻辑
- `capture_api_params.py` - 参数捕获工具（需要浏览器）
- `direct_videocdn_parser_simple.py` - 解析器（支持从文件读取参数）

