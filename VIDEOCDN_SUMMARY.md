# videocdn.ihelpy.net 解析器项目总结

## ✅ 项目完成状态

**状态**: ✅ 已完成并测试通过

**完成时间**: 2024-12-08

## 🎯 项目目标

实现对 `videocdn.ihelpy.net` 视频解析接口的直接调用，无需浏览器自动化，直接通过HTTP请求获取m3u8播放链接。

## ✨ 实现的功能

### 1. 核心解析功能 ✅

- ✅ 直接HTTP请求调用API
- ✅ 自动解压响应（gzip/deflate/brotli）
- ✅ 智能解码（UTF-8/GBK/自动检测）
- ✅ 提取多个m3u8链接
- ✅ 选择最佳m3u8链接
- ✅ 验证m3u8链接有效性
- ✅ 保存完整结果到JSON

### 2. 分析工具 ✅

- ✅ 浏览器自动化分析脚本
- ✅ Tampermonkey用户脚本（持久化）
- ✅ Console分析脚本
- ✅ 参数生成逻辑分析脚本

### 3. 文档 ✅

- ✅ 完整API文档
- ✅ 使用指南
- ✅ 故障排除指南
- ✅ 绕过Debugger指南
- ✅ Tampermonkey安装指南
- ✅ 项目结构说明

## 📊 测试结果

### 测试用例

**输入**: `https://www.iqiyi.com/v_1c168e2yzbk.html`

**输出**: 
- ✅ 成功解析
- ✅ 找到5个m3u8链接
- ✅ 最佳链接: `https://b2.bdzybf22.com/videos/202509/11/68c2c7bf8bcb3e0950f2a613/f0cbcf/index.m3u8`

### 解析结果

```json
{
  "video_url": "https://www.iqiyi.com/v_1c168e2yzbk.html",
  "api_url": "https://m1-a1.cloud.nnpp.vip:2223/api/v/?z=e8e56ecaca35c6229baa93884b6b7323&jx=https://www.iqiyi.com/v_1c168e2yzbk.html&s1ig=11402&g=b2.bdzy",
  "m3u8_urls": [
    "https://b2.bdzybf22.com/videos/202509/11/68c2c7bf8bcb3e0950f2a613/f0cbcf/index.m3u8",
    "https://hd.ijycnd.com/play/xe7pMwa7/index.m3u8",
    "https://b2.bdzybf22.com/videos/202507/10/686f12008bcb3e09506a9ae0/b50812/index.m3u8",
    "https://play.xluuss.com/play/RdGx73eD/index.m3u8",
    "https://hn.bfvvs.com/play/lejkn4aj/index.m3u8"
  ],
  "best_m3u8": "https://b2.bdzybf22.com/videos/202509/11/68c2c7bf8bcb3e0950f2a613/f0cbcf/index.m3u8"
}
```

## 🔧 技术实现

### API端点

```
https://m1-a1.cloud.nnpp.vip:2223/api/v/?z={z}&jx={video_url}&s1ig={s1ig}&g={g}
```

### 关键参数

| 参数 | 值 | 说明 |
|------|-----|------|
| z | e8e56ecaca35c6229baa93884b6b7323 | 32位十六进制，可能是MD5哈希 |
| jx | 目标视频URL | 需要解析的视频链接 |
| s1ig | 11402 | 数字字符串，可能是固定值 |
| g | b2.bdzy | 域名格式，可能是从m3u8 URL提取 |

### 请求头

关键请求头：
- `Referer`: `https://m1-z2.cloud.nnpp.vip:2223/`
- `Origin`: `https://m1-z2.cloud.nnpp.vip:2223`
- `Sec-Fetch-Site`: `same-site`

### 响应格式

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
            "url": "m3u8链接"
          }
        ]
      }
    }
  ]
}
```

## 📁 项目文件

### 核心文件

- `direct_videocdn_parser_simple.py` - 主解析脚本 ✅
- `VIDEOCDN_IHELPY_PARSER.md` - 完整文档 ✅
- `requirements.txt` - Python依赖 ✅

### 分析工具

- `analyze_videocdn_ihelpy.py` - 浏览器分析脚本 ✅
- `analyze_api_params_persistent.js` - Tampermonkey脚本 ✅
- `analyze_api_params_v2.js` - Console脚本 ✅
- `analyze_params_generation.js` - 参数分析脚本 ✅
- `capture_api_params.py` - 参数捕获工具（新增）✅

### 文档

- `VIDEOCDN_IHELPY_PARSER.md` - API文档 ✅
- `BYPASS_DEBUGGER_GUIDE.md` - Debugger绕过指南 ✅
- `TAMPERMONKEY_SETUP.md` - Tampermonkey指南 ✅
- `USAGE_GUIDE.md` - 使用指南 ✅
- `PROJECT_STRUCTURE.md` - 项目结构 ✅
- `PARAM_CAPTURE_GUIDE.md` - 参数捕获指南（新增）✅
- `VIDEOCDN_SUMMARY.md` - 本文件 ✅

## 🗑️ 已清理的文件

以下多余文件已被删除：
- `analyze_api_params.js` - 旧版本
- `direct_videocdn_parser.py` - 完整版（不需要）
- `videocdn_ihelpy_page.html` - 临时文件
- `media_staticfile_page.html` - 临时文件

## 🚀 使用方法

### 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行解析器
python direct_videocdn_parser_simple.py
```

### Python代码

```python
from direct_videocdn_parser_simple import DirectVideoCdnParserSimple

parser = DirectVideoCdnParserSimple()
m3u8_url = parser.parse_video("https://www.iqiyi.com/v_1c168e2yzbk.html")

if m3u8_url:
    print(f"✅ 解析成功: {m3u8_url}")
```

## 📝 注意事项

### 参数说明

1. **z参数**: 当前使用固定值，如果API失效可能需要动态生成
2. **s1ig参数**: 当前使用固定值，可能是固定值
3. **g参数**: 当前使用固定值"b2.bdzy"，可能需要从m3u8 URL中提取

### 参数过期问题

如果API返回错误信息"联系QQ 3366 129 856 获取json版api地址"，说明参数已过期。

**解决方案：**

1. **使用参数捕获工具**（推荐）:
   ```bash
   python3 capture_api_params.py
   ```
   脚本会自动捕获最新的API参数并保存到 `captured_api_params.json`。

2. **手动更新参数**:
   - 查看 `captured_api_params.json` 文件
   - 更新 `direct_videocdn_parser_simple.py` 中的参数值

3. **使用Tampermonkey脚本**:
   - 安装 `analyze_api_params_persistent.js` 脚本
   - 访问解析网站，在Console中运行 `_analyzeApiParams.showCalls()`

详细说明请参考 [参数捕获指南](PARAM_CAPTURE_GUIDE.md)

### 限制

- 如果API参数需要动态生成，可能需要使用浏览器分析脚本
- 某些情况下可能需要特定的Cookie或Session
- 参数可能定期过期，需要定期更新

## 🔮 未来改进

### 可能的改进方向

1. **动态参数生成**: 如果z、s1ig或g参数需要动态生成，实现生成逻辑
2. **自动参数更新**: 实现参数过期检测和自动更新机制
3. **多视频源支持**: 支持更多视频网站
4. **批量处理**: 支持批量解析多个视频
5. **错误重试**: 添加自动重试机制
6. **缓存机制**: 添加结果缓存

## 📚 相关资源

- [完整API文档](VIDEOCDN_IHELPY_PARSER.md)
- [参数捕获指南](PARAM_CAPTURE_GUIDE.md) - **参数过期时必读**
- [项目结构说明](PROJECT_STRUCTURE.md)
- [使用指南](USAGE_GUIDE.md)

## ✅ 完成清单

- [x] 核心解析功能实现
- [x] 响应解压支持（gzip/deflate/brotli）
- [x] 智能解码支持
- [x] 多m3u8链接提取
- [x] 结果保存功能
- [x] 浏览器分析脚本
- [x] 参数分析工具
- [x] 完整文档编写
- [x] 项目清理和整理
- [x] 测试验证

## 🎉 项目总结

本项目成功实现了对 `videocdn.ihelpy.net` 视频解析接口的直接调用，无需浏览器自动化即可获取m3u8播放链接。项目包含完整的解析器、分析工具和文档，可以直接使用。

**状态**: ✅ 项目完成，可以投入使用

