#!/bin/bash
# 快速启动脚本

echo "=========================================="
echo "视频解析API服务 - 快速启动"
echo "=========================================="

# 检查配置文件
if [ ! -f "data/config.json" ]; then
    echo "⚠️  配置文件不存在，从示例文件复制..."
    mkdir -p data
    cp config.json.example data/config.json
    echo "✅ 配置文件已创建，请编辑 data/config.json"
fi

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker"
    exit 1
fi

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
if curl -f http://localhost:1233/health > /dev/null 2>&1; then
    echo "✅ 服务启动成功！"
    echo ""
    echo "📊 API端点："
    echo "   - 健康检查: http://localhost:1233/health"
    echo "   - API文档: http://localhost:1233/docs"
    echo "   - 解析接口: POST http://localhost:1233/api/v1/parse"
    echo "   - 搜索接口: POST http://localhost:1233/api/v1/search"
    echo ""
    echo "📝 查看日志: docker-compose logs -f"
else
    echo "⚠️  服务可能未完全启动，请检查日志: docker-compose logs"
fi

