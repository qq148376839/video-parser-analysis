@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

set "SOURCE_DIR=%~dp0"
set "TARGET_DIR=video-parser-service"

echo ============================================================
echo 创建Docker部署项目
echo ============================================================
echo 源目录: %SOURCE_DIR%
echo 目标目录: %TARGET_DIR%
echo.

REM 检查源目录
if not exist "%SOURCE_DIR%api_server.py" (
    echo [错误] 源目录不正确，找不到 api_server.py
    exit /b 1
)

REM 创建目标目录
echo [信息] 创建目录结构...
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"
if not exist "%TARGET_DIR%\parsers" mkdir "%TARGET_DIR%\parsers"
if not exist "%TARGET_DIR%\utils" mkdir "%TARGET_DIR%\utils"
if not exist "%TARGET_DIR%\data" mkdir "%TARGET_DIR%\data"

REM 复制核心文件
echo [信息] 复制核心文件...
copy /Y "%SOURCE_DIR%api_server.py" "%TARGET_DIR%\" >nul && echo   [OK] api_server.py
copy /Y "%SOURCE_DIR%healthcheck.py" "%TARGET_DIR%\" >nul && echo   [OK] healthcheck.py
copy /Y "%SOURCE_DIR%final_direct_parser_v2.py" "%TARGET_DIR%\" >nul && echo   [OK] final_direct_parser_v2.py
copy /Y "%SOURCE_DIR%direct_videocdn_parser_simple.py" "%TARGET_DIR%\" >nul && echo   [OK] direct_videocdn_parser_simple.py

REM 复制配置文件
echo [信息] 复制配置文件...
copy /Y "%SOURCE_DIR%requirements.txt" "%TARGET_DIR%\" >nul && echo   [OK] requirements.txt
copy /Y "%SOURCE_DIR%Dockerfile" "%TARGET_DIR%\" >nul && echo   [OK] Dockerfile
copy /Y "%SOURCE_DIR%docker-compose.yml" "%TARGET_DIR%\" >nul && echo   [OK] docker-compose.yml
copy /Y "%SOURCE_DIR%config.json.example" "%TARGET_DIR%\" >nul && echo   [OK] config.json.example

REM 复制可选文件
if exist "%SOURCE_DIR%.dockerignore" (
    copy /Y "%SOURCE_DIR%.dockerignore" "%TARGET_DIR%\" >nul && echo   [OK] .dockerignore
)
if exist "%SOURCE_DIR%start.sh" (
    copy /Y "%SOURCE_DIR%start.sh" "%TARGET_DIR%\" >nul && echo   [OK] start.sh
)

REM 复制parsers目录
echo [信息] 复制parsers模块...
copy /Y "%SOURCE_DIR%parsers\__init__.py" "%TARGET_DIR%\parsers\" >nul && echo   [OK] parsers\__init__.py
copy /Y "%SOURCE_DIR%parsers\z_param_parser.py" "%TARGET_DIR%\parsers\" >nul && echo   [OK] parsers\z_param_parser.py
copy /Y "%SOURCE_DIR%parsers\decrypt_parser.py" "%TARGET_DIR%\parsers\" >nul && echo   [OK] parsers\decrypt_parser.py
copy /Y "%SOURCE_DIR%parsers\search_parser.py" "%TARGET_DIR%\parsers\" >nul && echo   [OK] parsers\search_parser.py

REM 复制utils目录
echo [信息] 复制utils模块...
copy /Y "%SOURCE_DIR%utils\__init__.py" "%TARGET_DIR%\utils\" >nul && echo   [OK] utils\__init__.py
copy /Y "%SOURCE_DIR%utils\logger.py" "%TARGET_DIR%\utils\" >nul && echo   [OK] utils\logger.py
copy /Y "%SOURCE_DIR%utils\config_loader.py" "%TARGET_DIR%\utils\" >nul && echo   [OK] utils\config_loader.py
copy /Y "%SOURCE_DIR%utils\z_param_manager.py" "%TARGET_DIR%\utils\" >nul && echo   [OK] utils\z_param_manager.py

REM 创建配置文件
echo [信息] 准备配置文件...
if not exist "%TARGET_DIR%\data\config.json" (
    copy /Y "%SOURCE_DIR%config.json.example" "%TARGET_DIR%\data\config.json" >nul
    echo   [OK] 已创建 data\config.json（请编辑配置）
) else (
    echo   [信息] data\config.json 已存在，跳过
)

REM 创建README.md
echo [信息] 创建README.md...
(
echo # 视频解析服务 - Docker部署版
echo.
echo ## 快速开始
echo.
echo ### 1. 配置
echo 编辑 `data/config.json`，配置API站点。
echo.
echo ### 2. 构建和启动
echo ```bash
echo docker-compose build
echo docker-compose up -d
echo ```
echo.
echo ### 3. 验证
echo ```bash
echo # 查看日志
echo docker-compose logs -f
echo.
echo # 健康检查
echo curl http://localhost:1233/health
echo.
echo # API文档
echo 浏览器访问: http://localhost:1233/docs
echo ```
echo.
echo ## API接口
echo.
echo ### 解析接口
echo ```
echo GET /api/v1/parse?url=^<视频URL^>^&parser_url=^<解析网站URL^>
echo ```
echo.
echo ### 搜索接口
echo ```
echo GET /api/v1/search?ac=videolist^&wd=^<关键词^>^&page=^<页码^>
echo ```
echo.
echo ## 配置说明
echo.
echo 配置文件：`data/config.json`
echo.
echo - `cache_time`: 缓存时间（秒）
echo - `api_site`: API站点配置列表
echo.
echo ## 数据目录
echo.
echo - `data/config.json`: 配置文件
echo - `data/z_params.json`: z参数缓存（自动生成）
echo - `data/logs/`: 日志文件
echo.
echo ## 故障排查
echo.
echo 1. 查看日志：`docker-compose logs -f`
echo 2. 检查健康状态：`curl http://localhost:1233/health`
echo 3. 查看z参数状态：检查日志中的z参数相关信息
) > "%TARGET_DIR%\README.md"

echo   [OK] README.md
echo.
echo ============================================================
echo [完成] 部署项目创建完成！
echo ============================================================
echo.
echo [目录] 项目目录: %TARGET_DIR%
echo.
echo [文件] 文件清单:
for /r "%TARGET_DIR%" %%f in (*) do (
    set "filepath=%%f"
    set "filepath=!filepath:%CD%\=!"
    set "filepath=!filepath:%CD%=!"
    echo   !filepath!
)
echo.
echo [下一步]
echo   1. cd %TARGET_DIR%
echo   2. 编辑 data\config.json 配置API站点
echo   3. docker-compose build
echo   4. docker-compose up -d
echo.

endlocal

