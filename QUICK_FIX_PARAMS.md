# 快速修复参数过期问题

## 🚨 问题症状

运行 `python3 direct_videocdn_parser_simple.py` 时，出现以下错误：

```
❌ JSON解析失败: Expecting value: line 1 column 1 (char 0)
完整响应内容: 联系QQ 3366 129 856 获取json版api地址
```

## ✅ 快速解决方案

### 步骤1: 运行参数捕获脚本

```bash
python3 capture_api_params.py
```

脚本会：
- 自动打开浏览器
- 访问解析网站
- 捕获最新的API参数
- 保存到 `captured_api_params.json`

### 步骤2: 等待捕获完成

脚本会自动捕获参数，输出类似：

```
✅ 成功捕获 1 组参数:

[组 1]
   z: e8e56ecaca35c6229baa93884b6b7323
   s1ig: 11402
   g: b2.bdzy

💡 最新参数（可用于更新脚本）:
   z = "e8e56ecaca35c6229baa93884b6b7323"
   s1ig = "11402"
   g = "b2.bdzy"
```

### 步骤3: 重新运行解析器

解析器会自动从 `captured_api_params.json` 读取最新参数：

```bash
python3 direct_videocdn_parser_simple.py
```

## 🔧 手动更新参数（可选）

如果自动读取失败，可以手动更新 `direct_videocdn_parser_simple.py`：

1. 打开 `captured_api_params.json`，找到最新的参数
2. 编辑 `direct_videocdn_parser_simple.py`，更新以下行：

```python
# 在 construct_api_url 方法中
z_value = "新的z值"  # 从 captured_api_params.json 获取
s1ig_value = "新的s1ig值"  # 从 captured_api_params.json 获取
g_param = "新的g值"  # 从 captured_api_params.json 获取
```

## 📝 注意事项

1. **参数可能定期过期**：如果再次出现相同错误，重复上述步骤
2. **保持浏览器打开**：`capture_api_params.py` 默认会打开浏览器，方便查看
3. **网络问题**：确保网络连接正常，可以访问解析网站

## 🆘 如果仍然失败

1. **检查网络连接**：确保可以访问 `videocdn.ihelpy.net`
2. **手动访问网站**：在浏览器中手动访问解析网站，检查是否正常
3. **查看详细文档**：参考 [PARAM_CAPTURE_GUIDE.md](PARAM_CAPTURE_GUIDE.md) 获取更多帮助

## 💡 自动化建议

如果参数频繁过期，可以考虑：

1. **定期运行捕获脚本**：设置定时任务定期更新参数
2. **参数验证**：在解析器中添加参数有效性检测
3. **自动更新**：实现参数过期自动更新机制

