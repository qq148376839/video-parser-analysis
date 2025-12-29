"""
FastAPI主服务
提供视频解析和资源检索API接口
"""
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional
from contextlib import asynccontextmanager

from utils.logger import logger, setup_logger
from utils.config_loader import config_loader
from utils.z_param_manager import z_param_manager
from parsers.z_param_parser import ZParamParser
from parsers.decrypt_parser import DecryptParser
from parsers.search_parser import SearchParser

# 设置日志
setup_logger("video_parser", log_file="api_server.log")

# 全局变量
app_start_time = time.time()
z_param_parser = None
decrypt_parser = None
search_parser = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global z_param_parser, decrypt_parser, search_parser
    
    # 启动时初始化
    logger.info("=" * 60)
    logger.info("视频解析API服务启动")
    logger.info("=" * 60)
    
    # 初始化解析器
    z_param_parser = ZParamParser()
    decrypt_parser = DecryptParser()
    search_parser = SearchParser()
    
    logger.info("所有解析器初始化完成")
    logger.info("=" * 60)
    
    yield
    
    # 关闭时清理
    logger.info("服务关闭")


# 创建FastAPI应用
app = FastAPI(
    title="视频解析API服务",
    description="提供视频解析和资源检索功能",
    version="1.0.0",
    lifespan=lifespan
)


# 请求模型
class ParseRequest(BaseModel):
    video_url: HttpUrl
    parser_url: Optional[str] = "https://jx.789jiexi.com"


class SearchRequest(BaseModel):
    keyword: str
    page: Optional[int] = 1


# 响应模型
class ParseResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    fallback_used: Optional[bool] = False


@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "视频解析API服务",
        "version": "1.0.0",
        "endpoints": {
            "parse": "/api/v1/parse",
            "search": "/api/v1/search",
            "health": "/health"
        }
    }


@app.post("/api/v1/parse", response_model=ParseResponse)
async def parse_video(request: ParseRequest):
    """
    解析视频URL，返回m3u8链接
    
    Args:
        request: 解析请求，包含video_url和可选的parser_url
    
    Returns:
        解析结果，包含m3u8_url和解析方法
    """
    start_time = time.time()
    video_url = str(request.video_url)
    parser_url = request.parser_url
    
    logger.info(f"收到解析请求: {video_url}")
    
    try:
        # 先尝试z参数方案
        m3u8_url = z_param_parser.parse(video_url)
        method = "z_param"
        fallback_used = False
        
        # 如果失败，使用解密方案
        if not m3u8_url:
            logger.info("z参数方案失败，切换到解密方案")
            m3u8_url = decrypt_parser.parse(parser_url, video_url)
            method = "decrypt"
            fallback_used = True
        
        parse_time = time.time() - start_time
        
        if m3u8_url:
            logger.info(f"解析成功 ({method}): {m3u8_url[:100]}... (耗时: {parse_time:.2f}秒)")
            return ParseResponse(
                success=True,
                data={
                    "m3u8_url": m3u8_url,
                    "method": method,
                    "parse_time": round(parse_time, 2)
                },
                fallback_used=fallback_used
            )
        else:
            logger.warning(f"解析失败 (耗时: {parse_time:.2f}秒)")
            return ParseResponse(
                success=False,
                error="所有解析方案都失败",
                fallback_used=fallback_used
            )
            
    except Exception as e:
        logger.error(f"解析异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")


@app.post("/api/v1/search")
async def search_videos(request: SearchRequest):
    """
    搜索资源并解析视频地址
    
    Args:
        request: 搜索请求，包含keyword和可选的page
    
    Returns:
        搜索结果，包含解析后的m3u8地址
    """
    start_time = time.time()
    keyword = request.keyword
    page = request.page
    
    logger.info(f"收到搜索请求: {keyword} (页码: {page})")
    
    if not keyword or not keyword.strip():
        raise HTTPException(status_code=400, detail="关键词不能为空")
    
    try:
        result = search_parser.search_and_parse(keyword.strip())
        
        search_time = time.time() - start_time
        logger.info(f"搜索完成 (耗时: {search_time:.2f}秒, 结果数: {result.get('total', 0)})")
        
        return result
        
    except Exception as e:
        logger.error(f"搜索异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@app.get("/health")
async def health_check():
    """
    健康检查接口
    
    Returns:
        服务健康状态
    """
    uptime = int(time.time() - app_start_time)
    z_param_status = "valid" if not z_param_manager.is_expired() else "expired"
    z_param_age = z_param_manager.get_age_seconds()
    
    status = "healthy"
    if z_param_status == "expired":
        status = "degraded"
    
    return {
        "status": status,
        "z_param_status": z_param_status,
        "z_param_age": z_param_age,
        "uptime": uptime
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False
    )

