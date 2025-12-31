# 故障排查指南

## 🔍 z参数获取失败

### 问题现象
- HTTP方式：未能从HTTP响应中提取z参数
- Playwright方式：页面加载超时或未能捕获到z参数

### 排查步骤

#### 1. 检查网络连接
```bash
# 测试能否访问解析网站
curl "https://videocdn.ihelpy.net/jiexi/m1907.html?m1907jx=https://www.iqiyi.com/v_19rrf6eqrk.html"
```

#### 2. 查看调试文件
如果HTTP方式失败，系统会自动保存HTML到：
```
data/z_param_debug.html
```

打开这个文件，搜索以下内容：
- `z=`
- `api/v`
- 32位十六进制字符串

#### 3. 手动提取z参数
参考 `Z_PARAM_MANUAL_SETUP.md` 手动设置z参数

#### 4. 检查Playwright
```bash
# 确认Playwright已安装浏览器
playwright install chromium

# 测试Playwright是否正常工作
python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); print('OK')"
```

### 临时解决方案

如果z参数获取持续失败，可以：

1. **使用解密方案**：系统会自动回退到解密方案，虽然可能较慢，但通常能工作

2. **手动设置z参数**：
   ```bash
   # 创建z参数文件
   echo '{
     "z_param": "你的32位z参数",
     "s1ig_param": "11397",
     "g_param": "",
     "updated_at": "2024-12-30T09:00:00"
   }' > data/z_params.json
   ```

3. **增加超时时间**：修改 `utils/z_param_manager.py` 中的超时设置

## 🔧 常见问题

### Q: HTTP方式总是失败
**A**: 可能是网站结构变化，建议：
- 查看 `data/z_param_debug.html` 文件
- 检查正则表达式是否需要更新
- 考虑使用Playwright方式

### Q: Playwright方式超时
**A**: 可能是网络问题或网站响应慢，建议：
- 检查网络连接
- 增加超时时间
- 使用HTTP方式（如果可用）

### Q: 两种方式都失败
**A**: 系统会自动使用解密方案，虽然可能较慢，但通常能工作。也可以手动设置z参数。

## 📝 调试技巧

### 启用详细日志
修改 `utils/logger.py` 中的日志级别：
```python
logger.setLevel(logging.DEBUG)
```

### 保存调试信息
系统会自动保存：
- `data/z_param_debug.html` - HTTP响应的HTML
- `logs/` - 日志文件

### 测试z参数提取
```bash
python test_z_param.py
```

