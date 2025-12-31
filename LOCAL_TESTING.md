# 本地测试指南

## 📋 前置准备

### 1. 安装依赖

```bash
# 安装所有依赖
pip install -r requirements.txt

# 如果需要测试 z_param_api_service.py（Flask版本），单独安装
pip install flask
```

### 2. 准备配置文件

```bash
# 创建data目录
mkdir -p data

# 复制配置文件
cp config.json.example data/config.json
```

## 🚀 运行主服务（推荐）

主服务使用 FastAPI，提供完整的视频解析和搜索功能：

```bash
# 方式1：直接运行
python api_server.py

# 方式2：使用uvicorn（推荐）
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后：
- API文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health
- 解析接口：http://localhost:8000/api/v1/parse?url=<视频URL>
- 搜索接口：http://localhost:8000/api/v1/search?ac=videolist&wd=<关键词>

## 🧪 测试脚本

### 测试解析接口

```bash
# Windows PowerShell
curl "http://localhost:8000/api/v1/parse?url=https://www.iqiyi.com/v_19rrf6eqrk.html"

# 或使用Python测试脚本
python test_parse.py
```

### 测试搜索接口

```bash
# Windows PowerShell
curl "http://localhost:8000/api/v1/search?ac=videolist&wd=新僵尸先生"

# 或使用Python测试脚本
python test_search.py
```

## 📝 快速测试脚本

已创建以下测试脚本：

### test_parse.py - 测试解析接口
```bash
# 使用默认URL测试
python test_parse.py

# 使用自定义URL测试
python test_parse.py "https://v.qq.com/x/cover/xxx.html"
```

### test_search.py - 测试搜索接口
```bash
# 使用默认关键词测试
python test_search.py

# 使用自定义关键词测试
python test_search.py "新僵尸先生"
```

### test_z_param.py - 测试z参数更新
```bash
# 测试z参数更新功能
python test_z_param.py

# 使用自定义视频URL测试
python test_z_param.py "https://www.iqiyi.com/v_xxx.html"
```

## 🔧 测试z_param_api_service.py（可选）

如果需要测试Flask版本的z参数服务：

```bash
# 安装Flask（如果还没安装）
pip install flask

# 运行服务
python z_param_api_service.py

# 测试API
curl "http://localhost:5000/api/get_z_param?video_url=https://www.iqiyi.com/v_19rrf6eqrk.html"
```

## 📌 注意事项

1. **首次运行**：
   - z参数文件不存在是正常的，系统会自动尝试获取
   - 如果自动获取失败，参考 `Z_PARAM_MANUAL_SETUP.md` 手动设置

2. **Playwright**：
   - 如果使用Playwright方式，需要先安装浏览器：
   ```bash
   playwright install chromium
   ```

3. **配置文件**：
   - 确保 `data/config.json` 存在
   - 可以修改其中的API站点配置

4. **日志**：
   - 日志文件保存在 `logs/` 目录
   - 控制台也会输出日志

5. **端口冲突**：
   - 默认端口8000，如果被占用可以修改 `api_server.py` 中的端口

