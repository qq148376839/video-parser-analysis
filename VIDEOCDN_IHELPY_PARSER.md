# videocdn.ihelpy.net 视频解析器

## 📋 项目概述

本项目实现了对 `videocdn.ihelpy.net` 视频解析接口的直接调用，无需浏览器自动化，直接通过HTTP请求获取m3u8播放链接。

## ✨ 特性

- ✅ **无需浏览器**: 纯HTTP请求，速度快
- ✅ **自动解压**: 支持gzip、deflate、brotli压缩格式
- ✅ **智能解码**: 自动处理各种编码格式
- ✅ **多链接提取**: 自动提取所有可用的m3u8链接
- ✅ **结果保存**: 自动保存解析结果到JSON文件

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 使用方法

```python
from direct_videocdn_parser_simple import DirectVideoCdnParserSimple

# 创建解析器实例
parser = DirectVideoCdnParserSimple()

# 解析视频
video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
m3u8_url = parser.parse_video(video_url)

if m3u8_url:
    print(f"✅ 解析成功！m3u8链接: {m3u8_url}")
else:
    print("❌ 解析失败")
```

### 命令行使用

```bash
python direct_videocdn_parser_simple.py
```

## 📖 API说明

### DirectVideoCdnParserSimple类

#### 方法

##### `parse_video(video_url: str) -> Optional[str]`

解析视频URL，返回最佳的m3u8链接。

**参数:**
- `video_url` (str): 目标视频URL，例如 `https://www.iqiyi.com/v_1c168e2yzbk.html`

**返回:**
- `Optional[str]`: 最佳的m3u8链接，如果解析失败返回None

**示例:**
```python
parser = DirectVideoCdnParserSimple()
m3u8_url = parser.parse_video("https://www.iqiyi.com/v_1c168e2yzbk.html")
```

##### `construct_api_url(video_url: str, g_param: str = None) -> str`

构造API调用URL。

**参数:**
- `video_url` (str): 目标视频URL
- `g_param` (str, optional): g参数值，默认为"b2.bdzy"

**返回:**
- `str`: 完整的API URL

##### `call_api(api_url: str) -> Optional[Dict]`

调用API获取视频信息。

**参数:**
- `api_url` (str): API URL

**返回:**
- `Optional[Dict]`: API响应的JSON数据

##### `extract_m3u8_urls(api_response: Dict) -> List[str]`

从API响应中提取所有m3u8链接。

**参数:**
- `api_response` (Dict): API响应的JSON数据

**返回:**
- `List[str]`: m3u8链接列表

##### `get_best_m3u8(m3u8_urls: List[str]) -> Optional[str]`

选择最佳的m3u8链接（默认选择第一个）。

**参数:**
- `m3u8_urls` (List[str]): m3u8链接列表

**返回:**
- `Optional[str]`: 最佳的m3u8链接

##### `verify_m3u8(m3u8_url: str) -> bool`

验证m3u8链接是否有效。

**参数:**
- `m3u8_url` (str): m3u8链接

**返回:**
- `bool`: 是否有效

## 🔧 解析流程

1. **构造API URL**: 根据视频URL构造API调用地址
2. **调用API**: 发送HTTP请求获取视频信息
3. **解压响应**: 自动解压gzip/deflate/brotli压缩
4. **解析JSON**: 提取m3u8链接
5. **选择最佳**: 选择第一个m3u8链接作为最佳选择
6. **验证链接**: 验证m3u8链接是否有效
7. **保存结果**: 保存完整结果到JSON文件

## 📝 API参数说明

### 必需参数

- `z`: 32位十六进制字符串，可能是MD5哈希值
  - 当前值: `e8e56ecaca35c6229baa93884b6b7323`
  - 可能是固定值或需要动态生成

- `jx`: 目标视频URL
  - 示例: `https://www.iqiyi.com/v_1c168e2yzbk.html`

- `s1ig`: 数字字符串
  - 当前值: `11402`
  - 可能是固定值

- `g`: 域名格式字符串
  - 当前值: `b2.bdzy`
  - 可能是从m3u8 URL的域名中提取的

### API端点

```
https://m1-a1.cloud.nnpp.vip:2223/api/v/?z={z}&jx={video_url}&s1ig={s1ig}&g={g}
```

### 请求头

重要的请求头包括：
- `Referer`: `https://m1-z2.cloud.nnpp.vip:2223/`
- `Origin`: `https://m1-z2.cloud.nnpp.vip:2223`
- `Sec-Fetch-Site`: `same-site`

## 📊 响应格式

API返回JSON格式数据：

```json
{
  "type": "movie",
  "data": [
    {
      "name": "视频名称",
      "year": "年份",
      "source": {
        "eps": [
          {
            "name": "HD",
            "url": "https://example.com/play/index.m3u8"
          }
        ]
      }
    }
  ],
  "ep": "1",
  "y": [],
  "sp": 0,
  "p": ""
}
```

## 🛠️ 故障排除

### 问题1: Brotli解压失败

**症状**: 出现 `brotli: decoder failed` 错误

**解决方案**:
1. 安装brotli库: `pip install brotli`
2. 脚本会自动尝试直接解码（Content-Encoding头可能错误）

### 问题2: 403 Forbidden错误

**症状**: API返回403错误

**可能原因**:
1. 请求头不正确
2. 需要特定的Referer或Cookie
3. IP被限制

**解决方案**:
1. 检查请求头是否正确
2. 确保Referer和Origin正确设置
3. 尝试使用代理

### 问题3: 参数需要动态生成

**症状**: API返回错误或空响应

**可能原因**:
- z、s1ig或g参数需要动态生成

**解决方案**:
1. 使用浏览器分析脚本分析参数生成逻辑
2. 参考 `analyze_params_generation.js` 脚本

## 📁 输出文件

### videocdn_parse_result.json

包含完整的解析结果：

```json
{
  "video_url": "目标视频URL",
  "api_url": "API调用URL",
  "api_response": {
    "完整的API响应"
  },
  "m3u8_urls": [
    "所有m3u8链接"
  ],
  "best_m3u8": "最佳的m3u8链接"
}
```

## 🔍 参数分析工具

### 浏览器脚本

使用 `analyze_params_generation.js` 分析参数生成逻辑：

1. 在浏览器Console中运行脚本
2. 刷新页面触发API调用
3. 使用分析函数：
   ```javascript
   _analyzeParams.showCalls()      // 查看所有调用
   _analyzeParams.analyzeZ()       // 分析z参数
   _analyzeParams.analyzeG()       // 分析g参数
   _analyzeParams.compareCalls()   // 比较多个调用
   ```

### Tampermonkey脚本

使用 `analyze_api_params_persistent.js` 创建持久化的分析脚本：

1. 安装Tampermonkey扩展
2. 创建新脚本，粘贴 `analyze_api_params_persistent.js` 的内容
3. 保存并启用
4. 脚本会自动捕获所有API调用

## 📚 相关文档

- [绕过Debugger指南](BYPASS_DEBUGGER_GUIDE.md)
- [Tampermonkey安装指南](TAMPERMONKEY_SETUP.md)
- [使用指南](USAGE_GUIDE.md)

## 🎯 示例

### 基本使用

```python
from direct_videocdn_parser_simple import DirectVideoCdnParserSimple

parser = DirectVideoCdnParserSimple()
m3u8_url = parser.parse_video("https://www.iqiyi.com/v_1c168e2yzbk.html")

if m3u8_url:
    print(f"✅ 解析成功: {m3u8_url}")
    # 使用ffmpeg下载
    # ffmpeg -i "{m3u8_url}" -c copy output.mp4
```

### 批量解析

```python
video_urls = [
    "https://www.iqiyi.com/v_1c168e2yzbk.html",
    "https://www.iqiyi.com/v_xxxxx.html",
]

parser = DirectVideoCdnParserSimple()
results = []

for url in video_urls:
    m3u8 = parser.parse_video(url)
    if m3u8:
        results.append({"video_url": url, "m3u8_url": m3u8})

print(f"✅ 成功解析 {len(results)} 个视频")
```

## 📄 许可证

本项目仅供学习和研究使用。

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 联系方式

如有问题，请提交Issue。

