@echo off
REM Windows批处理脚本 - 启动本地测试服务

echo ============================================================
echo 视频解析服务 - 本地测试
echo ============================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查依赖是否安装
echo [1/4] 检查依赖...
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [警告] 依赖未安装，正在安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

REM 创建data目录和配置文件
echo [2/4] 准备配置文件...
if not exist "data" mkdir data
if not exist "data\config.json" (
    echo [信息] 复制配置文件...
    copy config.json.example data\config.json >nul
)

REM 创建logs目录
if not exist "logs" mkdir logs

REM 启动服务
echo [3/4] 启动服务...
echo.
echo ============================================================
echo 服务启动中...
echo API文档: http://localhost:8000/docs
echo 健康检查: http://localhost:8000/health
echo 解析接口: GET http://localhost:8000/api/v1/parse?url=<视频URL>
echo 搜索接口: GET http://localhost:8000/api/v1/search?ac=videolist&wd=<关键词>
echo ============================================================
echo.
echo 按 Ctrl+C 停止服务
echo.

python api_server.py

pause

