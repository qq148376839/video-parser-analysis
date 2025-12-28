# API参数捕获指南

## 📋 问题说明

当 `direct_videocdn_parser_simple.py` 返回错误信息"联系QQ 3366 129 856 获取json版api地址"时，说明API参数（z、s1ig、g）已过期，需要重新捕获。

## 🔧 解决方案

### 方法1: 使用Python脚本自动捕获（推荐）

使用 `capture_api_params.py` 脚本自动捕获最新的API参数：

```bash
python3 capture_api_params.py
```

**脚本功能：**
- ✅ 自动打开浏览器访问解析网站
- ✅ 监听所有网络请求
- ✅ 捕获API调用中的z、s1ig、g参数
- ✅ 分析JavaScript代码查找参数生成逻辑
- ✅ 保存结果到 `captured_api_params.json`

**输出示例：**
```
✅ 成功捕获 1 组参数:

[组 1]
   z: e8e56ecaca35c6229baa93884b6b7323
   s1ig: 11402
   g: b2.bdzy
   jx: https://www.iqiyi.com/v_1c168e2yzbk.html

💡 最新参数（可用于更新脚本）:
   z = "e8e56ecaca35c6229baa93884b6b7323"
   s1ig = "11402"
   g = "b2.bdzy"
```

### 方法2: 使用Tampermonkey脚本捕获

1. **安装Tampermonkey扩展**
   - Chrome: [Tampermonkey](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo)
   - Firefox: [Tampermonkey](https://addons.mozilla.org/en-US/firefox/addon/tampermonkey/)

2. **创建新脚本**
   - 点击Tampermonkey图标 → 创建新脚本
   - 粘贴 `analyze_api_params_persistent.js` 的内容
   - 保存并启用

3. **访问解析网站**
   - 访问: `https://videocdn.ihelpy.net/jiexi/m1907.html?m1907jx={视频URL}`
   - 打开浏览器Console（F12）
   - 运行: `_analyzeApiParams.showCalls()`

4. **查看捕获的参数**
   ```javascript
   // 在Console中运行
   _analyzeApiParams.showCalls()
   ```

### 方法3: 使用浏览器Console脚本

1. **访问解析网站**
   - 打开: `https://videocdn.ihelpy.net/jiexi/m1907.html?m1907jx={视频URL}`
   - 打开浏览器Console（F12）

2. **运行分析脚本**
   - 复制 `analyze_params_generation.js` 的内容
   - 粘贴到Console并执行

3. **触发API调用**
   - 刷新页面或操作页面触发视频加载

4. **查看分析结果**
   ```javascript
   // 查看所有API调用
   _analyzeParams.showCalls()
   
   // 分析z参数
   _analyzeParams.analyzeZ()
   
   // 分析g参数
   _analyzeParams.analyzeG()
   
   // 比较多个调用
   _analyzeParams.compareCalls()
   ```

## 📝 更新解析器脚本

捕获到新参数后，更新 `direct_videocdn_parser_simple.py`:

```python
# 在 construct_api_url 方法中更新参数
z_value = "新的z参数值"  # 从捕获结果中获取
s1ig_value = "新的s1ig参数值"  # 从捕获结果中获取
g_param = "新的g参数值"  # 从捕获结果中获取
```

## 🔍 参数说明

### z参数
- **格式**: 32位十六进制字符串（可能是MD5哈希）
- **示例**: `e8e56ecaca35c6229baa93884b6b7323`
- **特点**: 可能是固定值，也可能需要动态生成

### s1ig参数
- **格式**: 数字字符串
- **示例**: `11402`
- **特点**: 可能是固定值

### g参数
- **格式**: 域名格式字符串（子域名.域名部分）
- **示例**: `b2.bdzy`
- **特点**: 可能是从m3u8 URL中提取的

## 🚨 常见问题

### 问题1: 脚本未捕获到参数

**可能原因：**
- 页面未触发API调用
- API调用被拦截
- 需要手动操作页面

**解决方案：**
1. 在浏览器中手动访问页面
2. 等待页面完全加载
3. 尝试点击播放按钮
4. 检查浏览器Console中的网络请求

### 问题2: 参数仍然无效

**可能原因：**
- 参数有时效性（需要实时生成）
- 需要特定的Cookie或Session
- API端点已变更

**解决方案：**
1. 检查参数是否有时效性（多次调用是否不同）
2. 使用浏览器自动化保持Session
3. 检查API端点是否变更

### 问题3: 参数生成逻辑复杂

**可能原因：**
- 参数需要JavaScript计算生成
- 涉及加密算法

**解决方案：**
1. 使用浏览器自动化执行JavaScript
2. 分析JavaScript代码找到生成逻辑
3. 使用PyExecJS或Node.js执行JavaScript代码

## 📚 相关文件

- `capture_api_params.py` - 自动参数捕获脚本
- `analyze_api_params_persistent.js` - Tampermonkey脚本
- `analyze_params_generation.js` - Console分析脚本
- `direct_videocdn_parser_simple.py` - 解析器脚本（需要更新参数）

## 💡 最佳实践

1. **定期更新参数**: 参数可能定期过期，建议定期运行捕获脚本
2. **保存历史参数**: 保存不同时间的参数，便于对比分析
3. **自动化流程**: 如果参数频繁变化，考虑自动化参数更新流程
4. **错误处理**: 在解析器中添加参数失效检测和自动更新机制

## 🔄 自动化更新流程（未来改进）

可以考虑实现自动参数更新：

```python
class AutoUpdatingParser:
    def __init__(self):
        self.params = self.load_params()
        self.last_update = self.get_last_update_time()
    
    def check_and_update_params(self):
        """检查参数是否过期，如果过期则自动更新"""
        if self.is_params_expired():
            print("⚠️ 参数已过期，正在更新...")
            new_params = self.capture_latest_params()
            self.update_params(new_params)
            print("✅ 参数已更新")
    
    def parse_video(self, video_url):
        """解析视频，自动检查参数"""
        self.check_and_update_params()
        # ... 解析逻辑
```

