# Tampermonkey用户脚本安装指南

## 为什么使用Tampermonkey？

1. **持久化**: 脚本会在每次页面加载时自动运行
2. **跨页面**: 可以在多个页面使用
3. **自动注入**: 在页面加载前就注入，不会因为刷新而丢失
4. **易于管理**: 可以随时启用/禁用

## 安装步骤

### 步骤1: 安装Tampermonkey扩展

1. 打开Chrome浏览器
2. 访问 [Tampermonkey官网](https://www.tampermonkey.net/)
3. 点击"Download"下载扩展
4. 安装到Chrome

### 步骤2: 创建新脚本

1. 点击浏览器右上角的Tampermonkey图标
2. 选择"Create a new script"
3. 会打开编辑器

### 步骤3: 粘贴代码

1. 删除编辑器中的所有默认内容
2. 复制 `analyze_api_params_persistent.js` 的完整内容
3. 粘贴到编辑器
4. 保存 (Ctrl+S)

### 步骤4: 启用脚本

1. 确保脚本已启用（开关是绿色的）
2. 访问目标页面
3. 打开Console查看输出

## 使用方法

### 查看所有API调用

在Console中运行：

```javascript
_analyzeApiParams.showCalls()
```

### 清除保存的数据

```javascript
_analyzeApiParams.clear()
```

## 脚本功能

1. **自动Hook**: 自动Hook fetch和XMLHttpRequest
2. **自动保存**: 自动保存API调用到localStorage
3. **跨页面**: 即使页面刷新，数据也会保存
4. **禁用Debugger**: 自动禁用debugger断点

## 匹配的URL

脚本会在以下URL自动运行：
- `https://videocdn.ihelpy.net/*`
- `https://m1-z2.cloud.nnpp.vip:2223/*`
- `https://m1-a1.cloud.nnpp.vip:2223/*`

## 注意事项

1. 确保Tampermonkey扩展已启用
2. 确保脚本已启用
3. 如果脚本没有运行，检查Tampermonkey的日志

## 替代方案

如果不想安装Tampermonkey，可以使用：

1. **Chrome Snippets** (推荐)
2. **手动在Console运行** (每次刷新需要重新运行)
3. **Chrome扩展开发** (高级)


