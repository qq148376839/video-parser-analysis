"""
解密解析器模块
基于final_direct_parser_v2.py的解密方案（备选方案）
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from final_direct_parser_v2 import FinalDirectParserV2
from typing import Optional
from utils.logger import logger


class DecryptParser:
    """解密解析器（备选方案）"""
    
    def __init__(self):
        """初始化解密解析器"""
        self.parser = FinalDirectParserV2()
        logger.info("解密解析器初始化完成")
    
    def parse(self, parser_url: str, video_url: str) -> Optional[str]:
        """
        解析视频URL，返回m3u8或mp4链接
        
        Args:
            parser_url: 解析网站URL
            video_url: 视频URL
        
        Returns:
            m3u8或mp4链接，如果失败返回None
        """
        try:
            logger.info(f"使用解密方案解析: {video_url}")
            result_url = self.parser.parse_video(parser_url, video_url)
            
            if result_url:
                # 检查返回的URL类型
                if '.m3u8' in result_url.lower():
                    logger.info(f"解密方案解析成功（m3u8）: {result_url[:100]}...")
                elif '.mp4' in result_url.lower():
                    logger.info(f"解密方案解析成功（mp4）: {result_url[:100]}...")
                    # mp4链接也可以直接使用，返回它
                else:
                    logger.info(f"解密方案解析成功（其他格式）: {result_url[:100]}...")
                
                return result_url
            else:
                logger.warning("解密方案解析失败")
                return None
                
        except Exception as e:
            logger.error(f"解密方案解析异常: {e}")
            return None

