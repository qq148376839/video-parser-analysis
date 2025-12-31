# JavaScript 捕获功能使用说明

## 📋 功能概述

`direct_jx_m3u8_tv_parser.py` 现在支持捕获和分析 JavaScript 代码，用于分析 token 生成逻辑。

## 🚀 使用方法

### 方法1: 命令行参数

```bash
python direct_jx_m3u8_tv_parser.py --capture-js
```

或使用简写：

```bash
python direct_jx_m3u8_tv_parser.py -js
```

### 方法2: 在代码中调用

```python
import asyncio
from direct_jx_m3u8_tv_parser import DirectJxM3u8TvParser

async def main():
    parser = DirectJxM3u8TvParser()
    video_url = "https://v.youku.com/v_show/id_XMTA0MTc5NzI4.html"
    parser_url = "https://jx.2s0.cn"
    
    result = await parser.capture_and_analyze_js(video_url, parser_url)
    
    if result:
        print("JavaScript代码捕获成功！")

asyncio.run(main())
```

## 📊 输出文件

### 1. `js_capture_analysis.json`

包含完整的捕获和分析结果：

```json
{
  "video_url": "...",
  "parser_url": "...",
  "js_files": {
    "external_scripts": [...],
    "inline_scripts": [...]
  },
  "analysis": {
    "external_scripts": {
      "https://jx.2s0.cn/playerapi/js/7zl.js": {
        "token_patterns": [...],
        "cachem3u8_patterns": [...],
        "encryption_functions": [...],
        "md5_usage": [...],
        "aes_usage": [...],
        "config_usage": [...],
        "api_calls": [...]
      }
    },
    "inline_scripts": [...]
  }
}
```

### 2. `captured_js_files/` 目录

保存所有捕获的 JavaScript 文件：
- `7zl.js`
- `7zlplayer.js`
- `jquery.min.js`
- `hls.min.js`
- 其他外部脚本...

## 🔍 分析内容

### Token 相关模式

查找以下模式：
- `token = "..."` - token 赋值
- `?token=...` - URL 中的 token
- `cachem3u8...token=...` - cachem3u8 URL 中的 token

### cachem3u8 相关模式

查找以下模式：
- `cachem3u8` - 域名
- `Cache/LZ/` - 路径
- `Cache/.../...m3u8` - m3u8 文件路径

### 加密函数

查找以下加密函数：
- `encrypt()` / `decrypt()`
- `AES.encrypt()` / `AES.decrypt()`
- `CryptoJS.AES`
- `md5()` / `MD5()`
- `sha256()` / `SHA256()`
- `rc4()`

### ConFig 使用

查找以下模式：
- `ConFig.url`
- `ConFig.id`
- `ConFig.uid`
- `window.ConFig`

### API 调用

查找以下 API 调用：
- `/admin/api.php`
- `fetch(...api...)`
- `.get(...api...)`
- `.post(...api...)`

## 💡 使用场景

### 场景1: 分析 Token 生成逻辑

```bash
python direct_jx_m3u8_tv_parser.py --capture-js
```

然后查看 `js_capture_analysis.json` 中的 `token_patterns` 和 `encryption_functions`。

### 场景2: 查找加密算法

查看 `js_capture_analysis.json` 中的：
- `encryption_functions` - 加密函数列表
- `md5_usage` - MD5 使用情况
- `aes_usage` - AES 使用情况

### 场景3: 分析 m3u8 URL 生成

查看 `js_capture_analysis.json` 中的：
- `cachem3u8_patterns` - cachem3u8 URL 模式
- `api_calls` - API 调用

## 🔧 技术细节

### 浏览器自动化

- 使用独立 Chrome 浏览器实例（`launch_chrome()`）
- 通过 CDP 连接（`connect_over_cdp()`）
- 添加反爬虫脚本（`add_stealth_script()`）

### JavaScript 捕获

1. **外部脚本**: 通过 `page.request.get()` 下载
2. **内联脚本**: 通过 `page.evaluate()` 提取
3. **分析**: 使用正则表达式匹配关键模式

### 分析算法

使用正则表达式匹配以下模式：
- Token 模式: `token\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{50,})["\']?`
- cachem3u8 模式: `cachem3u8[^"\']+`
- 加密函数: `(encrypt|decrypt|AES|CryptoJS|rc4|md5|sha256)`
- ConFig 使用: `ConFig\.(url|id|uid|config)`

## 📝 示例输出

```
============================================================
JavaScript代码捕获和分析
============================================================
目标视频: https://v.youku.com/v_show/id_XMTA0MTc5NzI4.html
解析网站: https://jx.2s0.cn

[步骤0] 启动独立Chrome浏览器...
   [OK] Chrome浏览器已启动，调试端口: 9222
   [OK] 成功连接到Chrome浏览器

[步骤1] 访问解析网站: https://jx.2s0.cn/player/?url=...
   [OK] 页面加载完成

[步骤2] 等待JavaScript执行...

[JS捕获] 开始捕获JavaScript代码...
   [OK] 找到 8 个script标签
   [OK] 下载外部脚本: https://jx.2s0.cn/playerapi/js/7zl.js... (12345 字符)
   [OK] 下载外部脚本: https://jx.2s0.cn/playerapi/js/7zlplayer.js... (23456 字符)
   [OK] 捕获内联脚本 (567 字符)

[JS分析] 开始分析JavaScript代码...

   分析外部脚本: https://jx.2s0.cn/playerapi/js/7zl.js...
      [OK] 找到 3 个token模式
      [OK] 找到 2 个cachem3u8模式
      [OK] 找到 5 个加密函数
      [OK] 找到 2 个MD5使用
      [OK] 找到 1 个AES使用

   分析内联脚本 #1 (567 字符)
      [OK] 找到关键模式

[OK] 结果已保存到: js_capture_analysis.json
   [OK] 保存JavaScript文件: captured_js_files/7zl.js
   [OK] 保存JavaScript文件: captured_js_files/7zlplayer.js

============================================================
[总结]
============================================================

[OK] 找到 3 个token相关模式
[OK] 找到 2 个cachem3u8相关模式
[OK] 找到 5 个加密函数
```

## 🎯 下一步

1. **查看分析结果**: 打开 `js_capture_analysis.json`
2. **检查关键文件**: 查看 `captured_js_files/` 目录中的文件
3. **分析 token 生成**: 查找 `token_patterns` 和 `encryption_functions`
4. **还原算法**: 根据找到的模式还原 token 生成逻辑

## ⚠️ 注意事项

1. **需要 Chrome 浏览器**: 确保已安装 Chrome 浏览器
2. **网络连接**: 需要能够访问解析网站
3. **执行时间**: JavaScript 捕获可能需要 10-30 秒
4. **文件大小**: 捕获的 JavaScript 文件可能较大

## 🔗 相关文件

- `direct_jx_m3u8_tv_parser.py` - 主脚本
- `js_capture_analysis.json` - 分析结果
- `captured_js_files/` - 捕获的 JavaScript 文件目录
- `TOKEN_GENERATION_ANALYSIS.md` - Token 生成分析报告

---

**最后更新**: 2024-12-19


