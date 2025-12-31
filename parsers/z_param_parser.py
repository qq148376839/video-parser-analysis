"""
z参数解析器模块
使用z参数方式解析视频（主要方案）
"""
import requests
import json
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict
from utils.logger import logger
from utils.z_param_manager import z_param_manager

# 创建线程池用于运行Playwright（避免asyncio冲突）
_playwright_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="playwright")


class ZParamParser:
    """z参数解析器（主要方案）"""
    
    def __init__(self):
        """初始化z参数解析器"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Referer': 'https://m1-z2.cloud.nnpp.vip:2223/',
            'Origin': 'https://m1-z2.cloud.nnpp.vip:2223',
        })
        logger.info("z参数解析器初始化完成")
    
    def construct_api_url(self, video_url: str) -> Optional[str]:
        """
        构造API URL
        
        Args:
            video_url: 视频URL
        
        Returns:
            API URL，如果失败返回None
        """
        z_param = z_param_manager.get_z_param()
        s1ig_param = z_param_manager.get_s1ig_param()
        g_param = z_param_manager.get_g_param()
        
        if not z_param:
            logger.warning("z参数不存在，无法构造API URL")
            return None
        
        api_url = f"https://m1-a1.cloud.nnpp.vip:2223/api/v/?z={z_param}&jx={video_url}&s1ig={s1ig_param}&g={g_param}"
        logger.debug(f"构造API URL: {api_url[:100]}...")
        return api_url
    
    def call_api(self, api_url: str) -> Optional[Dict]:
        """
        调用API获取视频信息
        
        Args:
            api_url: API URL
        
        Returns:
            API响应数据，如果失败返回None
        """
        try:
            # 移除Accept-Encoding避免压缩问题
            headers = self.session.headers.copy()
            if 'Accept-Encoding' in headers:
                del headers['Accept-Encoding']
            
            response = self.session.get(api_url, headers=headers, timeout=30, allow_redirects=True)
            
            if response.status_code != 200:
                logger.warning(f"API返回非200状态码: {response.status_code}")
                return None
            
            # 处理响应内容
            content = response.text
            
            # 检查是否是错误信息
            if '联系QQ' in content or '获取json版api地址' in content:
                logger.warning("API返回错误信息，z参数可能已过期")
                return None
            
            # 尝试解析JSON
            try:
                json_data = json.loads(content)
                return json_data
            except json.JSONDecodeError:
                # 尝试从响应中提取m3u8链接
                m3u8_patterns = [
                    r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
                    r'["\']([^"\']+\.m3u8[^"\']*)["\']',
                ]
                
                for pattern in m3u8_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        url = match if isinstance(match, str) else match[0] if match else None
                        if url and url.startswith('http'):
                            logger.info(f"从响应中提取到m3u8链接: {url[:100]}...")
                            return {'m3u8_url': url}
                
                logger.warning("无法解析API响应")
                return None
                
        except Exception as e:
            logger.error(f"调用API失败: {e}")
            return None
    
    def extract_m3u8(self, api_response: Dict) -> Optional[str]:
        """
        从API响应中提取m3u8链接
        
        Args:
            api_response: API响应数据
        
        Returns:
            m3u8链接，如果失败返回None
        """
        # 如果响应中直接包含m3u8_url
        if 'm3u8_url' in api_response:
            return api_response['m3u8_url']
        
        # 递归查找m3u8链接
        def find_m3u8(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    result = find_m3u8(value, f"{path}.{key}")
                    if result:
                        return result
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    result = find_m3u8(item, f"{path}[{i}]")
                    if result:
                        return result
            elif isinstance(obj, str) and '.m3u8' in obj and obj.startswith('http'):
                return obj
            return None
        
        m3u8_url = find_m3u8(api_response)
        return m3u8_url
    
    def parse(self, video_url: str) -> Optional[str]:
        """
        解析视频URL，返回m3u8链接
        
        Args:
            video_url: 视频URL
        
        Returns:
            m3u8链接，如果失败返回None
        """
        try:
            # 验证URL格式
            if not video_url or not video_url.startswith(('http://', 'https://')):
                logger.error(f"无效的视频URL格式: {video_url}")
                return None
            
            logger.info(f"使用z参数方案解析: {video_url}")
            
            # 检查z参数是否过期或不存在
            if z_param_manager.is_expired() or not z_param_manager.get_z_param():
                logger.info("z参数已过期或不存在，尝试更新...")
                # 先尝试HTTP方式（快速）
                new_z = z_param_manager.update_with_http(video_url)
                # 如果HTTP方式失败，尝试Playwright方式（需要浏览器）
                if not new_z:
                    logger.info("HTTP方式失败，尝试Playwright方式...")
                    # 始终在线程池中运行Playwright，避免asyncio冲突
                    # 因为即使parse()在单独线程中，Playwright仍可能检测到asyncio事件循环
                    try:
                        future = _playwright_executor.submit(z_param_manager.update_with_playwright, video_url)
                        new_z = future.result(timeout=60)  # 最多等待60秒
                    except Exception as e:
                        logger.error(f"Playwright线程执行失败: {e}", exc_info=True)
                        new_z = None
                
                if not new_z:
                    logger.warning("z参数更新失败，将尝试使用当前参数（如果存在）")
            
            # 构造API URL
            api_url = self.construct_api_url(video_url)
            if not api_url:
                logger.error("无法构造API URL（z参数不存在）")
                return None
            
            # 调用API
            api_response = self.call_api(api_url)
            if not api_response:
                logger.warning("API调用失败")
                return None
            
            # 提取m3u8链接
            m3u8_url = self.extract_m3u8(api_response)
            
            if m3u8_url:
                logger.info(f"z参数方案解析成功: {m3u8_url[:100]}...")
                return m3u8_url
            else:
                logger.warning("未能从API响应中提取m3u8链接")
                return None
                
        except Exception as e:
            logger.error(f"z参数方案解析异常: {e}")
            return None

