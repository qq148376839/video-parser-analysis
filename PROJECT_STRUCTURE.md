# 项目结构说明

## 📁 目录结构

```
video-parser-analysis/
├── direct_videocdn_parser_simple.py    # ✅ videocdn.ihelpy.net 解析器（主要脚本）
├── analyze_videocdn_ihelpy.py          # 🔍 videocdn.ihelpy.net 浏览器分析脚本
├── analyze_api_params_persistent.js    # 🔍 Tampermonkey参数分析脚本
├── analyze_api_params_v2.js            # 🔍 Console参数分析脚本
├── analyze_params_generation.js        # 🔍 参数生成逻辑分析脚本
│
├── VIDEOCDN_IHELPY_PARSER.md          # 📖 videocdn.ihelpy.net 完整文档
├── BYPASS_DEBUGGER_GUIDE.md           # 📖 绕过Debugger指南
├── TAMPERMONKEY_SETUP.md              # 📖 Tampermonkey安装指南
├── USAGE_GUIDE.md                     # 📖 使用指南
├── PROJECT_STRUCTURE.md                # 📖 本文件
├── README.md                           # 📖 项目总览
│
├── requirements.txt                    # 📦 Python依赖
├── .gitignore                          # 🚫 Git忽略文件
│
└── [其他项目的文件]                    # 其他解析器的相关文件
```

## 📝 文件说明

### 核心脚本

#### `direct_videocdn_parser_simple.py`
**用途**: videocdn.ihelpy.net 的直接解析器  
**状态**: ✅ 已完成  
**使用方法**: `python direct_videocdn_parser_simple.py`

#### `analyze_videocdn_ihelpy.py`
**用途**: 使用浏览器自动化分析videocdn.ihelpy.net  
**状态**: ✅ 已完成  
**使用方法**: `python analyze_videocdn_ihelpy.py`

### 分析工具

#### `analyze_api_params_persistent.js`
**用途**: Tampermonkey用户脚本，持久化分析API参数  
**状态**: ✅ 已完成  
**使用方法**: 安装Tampermonkey后创建新脚本

#### `analyze_api_params_v2.js`
**用途**: Console脚本，分析API参数（页面刷新后需重新运行）  
**状态**: ✅ 已完成  
**使用方法**: 在浏览器Console中运行

#### `analyze_params_generation.js`
**用途**: 分析z和g参数的生成逻辑  
**状态**: ✅ 已完成  
**使用方法**: 在浏览器Console中运行

### 文档

#### `VIDEOCDN_IHELPY_PARSER.md`
**内容**: videocdn.ihelpy.net 解析器的完整文档  
**包含**: API说明、使用方法、故障排除等

#### `BYPASS_DEBUGGER_GUIDE.md`
**内容**: 绕过无限debugger断点的指南  
**包含**: 6种绕过方法

#### `TAMPERMONKEY_SETUP.md`
**内容**: Tampermonkey用户脚本安装指南

#### `USAGE_GUIDE.md`
**内容**: 参数分析脚本的使用指南

## 🗑️ 已删除的文件

以下文件已被删除（多余或过时）：
- `analyze_api_params.js` - 旧版本，已被v2替代
- `direct_videocdn_parser.py` - 完整版但不需要，simple版本已足够
- `videocdn_ihelpy_page.html` - 临时文件
- `media_staticfile_page.html` - 临时文件

## 📦 依赖文件

### requirements.txt
包含所有Python依赖：
- `requests` - HTTP请求
- `brotli` - Brotli解压支持
- `playwright` - 浏览器自动化（用于分析脚本）

## 🎯 使用流程

### 1. 直接解析（推荐）

```bash
# 安装依赖
pip install -r requirements.txt

# 运行解析器
python direct_videocdn_parser_simple.py
```

### 2. 浏览器分析

```bash
# 运行浏览器分析脚本
python analyze_videocdn_ihelpy.py
```

### 3. 参数分析

1. 安装Tampermonkey
2. 创建新脚本，粘贴 `analyze_api_params_persistent.js`
3. 访问目标页面
4. 在Console中运行分析函数

## 📊 输出文件

解析器会生成以下文件：
- `videocdn_parse_result.json` - 解析结果
- `videocdn_ihelpy_analysis.json` - 浏览器分析结果（如果运行了分析脚本）

这些文件在 `.gitignore` 中，不会被提交到Git。

## 🔄 其他项目文件

项目中还包含其他解析器的相关文件：
- `final_direct_parser_v2.py` - jx.789jiexi.com解析器
- `browser_decrypt_parser.py` - 浏览器解密解析器
- `analyze_playerjy_parser.py` - playerjy解析器
- `analyze_media_staticfile.py` - media.staticfile解析器

这些文件保留用于参考，但不属于videocdn.ihelpy.net项目。

