# 快速开始指南

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install playwright requests
playwright install chromium
```

### 2. 测试单个注册

```bash
cd batch_register
python test_single_register.py
```

### 3. 批量注册

```bash
# 注册5个账号（默认）
python batch_register_jx2s0.py

# 注册10个账号
python batch_register_jx2s0.py -n 10

# 不使用代理
python batch_register_jx2s0.py -n 5 --no-proxy
```

## 📁 文件说明

- `batch_register_jx2s0.py` - 批量注册主脚本
- `test_single_register.py` - 单个注册测试脚本
- `registration_results.json` - 注册结果文件（自动生成）
- `README.md` - 完整使用说明文档

## ⚙️ 配置说明

### 代理IP配置

默认使用代理IP，代理API地址：
```
https://white.1024proxy.com/white/api?region=jp&num=1&time=10&format=0&type=json
```

如需修改代理API，编辑 `batch_register_jx2s0.py` 中的 `get_proxy_ip()` 函数。

### 邮箱生成策略

脚本使用英文名+数字的方式生成邮箱，包括：
- 英文名 + 生日（如：alex1990）
- 英文名 + 随机数字（如：alex123）
- 两个英文名组合（如：alexjames）
- 英文名 + 首字母 + 数字（如：alexj123）

## 📊 查看结果

注册结果保存在 `registration_results.json` 文件中，格式：

```json
[
  {
    "email": "alex1990@gmail.com",
    "password": "qwer1234!",
    "uid": "4059917",
    "key": "cgklotuyDGHILOTW38",
    "register_time": "2024-01-15 10:30:45"
  }
]
```

## ⚠️ 注意事项

1. **首次使用建议先运行测试脚本**，确保环境配置正确
2. **默认使用代理IP**，如果代理失败会自动尝试直连
3. **每次注册成功立即保存**，避免数据丢失
4. **自动检测反爬虫**，触发后会自动更换浏览器和IP

## 🔧 故障排除

### 问题1: 浏览器启动失败
- 确保已安装Chrome浏览器
- 检查Chrome路径是否正确

### 问题2: 滑块验证失败
- 检查网络连接
- 检查XPath是否正确
- 查看是否触发反爬虫检测

### 问题3: 代理IP获取失败
- 检查网络连接
- 使用 `--no-proxy` 参数禁用代理
- 检查代理API是否可访问

更多详细信息请查看 [README.md](README.md)
