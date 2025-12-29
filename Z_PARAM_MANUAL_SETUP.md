# z参数手动设置指南

## 📋 问题说明

如果自动获取z参数失败，可以手动设置z参数。

## 🔧 手动设置方法

### 方法1：通过浏览器获取z参数

1. **打开浏览器**，访问解析网站：
   ```
   https://videocdn.ihelpy.net/jiexi/m1907.html?m1907jx=https://www.iqiyi.com/v_19rrf6eqrk.html
   ```

2. **打开浏览器开发者工具**（F12）

3. **切换到Network（网络）标签**

4. **刷新页面**，查找包含 `api/v` 的请求

5. **点击该请求**，在URL中找到 `z=` 参数，复制32位十六进制字符串

6. **创建或编辑文件** `/app/data/z_params.json`：
   ```json
   {
     "z_param": "你的32位z参数值",
     "s1ig_param": "11397",
     "g_param": "",
     "updated_at": "2024-12-29T12:00:00"
   }
   ```

### 方法2：通过Docker容器设置

```bash
# 进入容器
docker exec -it video-parser bash

# 编辑z参数文件
nano /app/data/z_params.json

# 或使用echo创建
echo '{
  "z_param": "你的32位z参数值",
  "s1ig_param": "11397",
  "g_param": "",
  "updated_at": "2024-12-29T12:00:00"
}' > /app/data/z_params.json
```

### 方法3：通过挂载目录设置

如果data目录已挂载到本地：

```bash
# 编辑本地文件
nano ./data/z_params.json

# 内容同上
```

## 📝 文件格式

```json
{
  "z_param": "32位十六进制字符串（必填）",
  "s1ig_param": "11397（可选，默认值）",
  "g_param": "（可选，通常为空）",
  "updated_at": "ISO格式时间戳（可选）"
}
```

## ✅ 验证

设置完成后，重启容器：

```bash
docker-compose restart video-parser
```

查看日志确认z参数已加载：

```bash
docker-compose logs video-parser | grep "z参数"
```

应该看到：
```
z参数加载成功
```

## 🔍 故障排查

### 问题1：z参数格式错误
- **症状**：日志显示"z参数格式错误"
- **解决**：确保z参数是32位十六进制字符串（只包含0-9和a-f）

### 问题2：文件权限问题
- **症状**：无法写入z_params.json
- **解决**：检查data目录权限，确保容器有写入权限

### 问题3：z参数过期
- **症状**：日志显示"z参数已过期"
- **解决**：更新z参数，或修改过期时间设置

## 📌 注意事项

1. **z参数有效期**：z参数通常24小时有效，需要定期更新
2. **备份**：建议备份有效的z参数，以便快速恢复
3. **自动更新**：设置z参数后，系统仍会尝试自动更新（如果HTTP或Playwright方式可用）

