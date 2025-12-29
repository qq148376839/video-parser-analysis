"""
资源检索解析器模块
支持关键词搜索，批量解析多个视频平台的资源
"""
import requests
import json
import re
from typing import List, Dict, Optional, Set
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.logger import logger
from utils.config_loader import config_loader
from .z_param_parser import ZParamParser
from .decrypt_parser import DecryptParser


class SearchParser:
    """资源检索解析器"""
    
    def __init__(self):
        """初始化资源检索解析器"""
        self.z_param_parser = ZParamParser()
        self.decrypt_parser = DecryptParser()
        logger.info("资源检索解析器初始化完成")
    
    def search_api_sites(self, keyword: str) -> List[Dict]:
        """
        并发调用所有API站点搜索资源
        
        Args:
            keyword: 搜索关键词
        
        Returns:
            所有API站点返回的资源列表
        """
        api_sites = config_loader.get_api_site_list()
        all_results = []
        
        def fetch_site(site: Dict) -> Optional[Dict]:
            """获取单个站点的搜索结果"""
            try:
                api_url = site['api'].strip()  # 去除可能的空格
                
                # 验证API URL格式
                if not api_url or not api_url.startswith(('http://', 'https://')):
                    logger.warning(f"站点 [{site['name']}] API URL格式无效: {api_url}")
                    return None
                
                # 确保URL格式正确（去除末尾的斜杠，如果有）
                if api_url.endswith('/'):
                    api_url = api_url[:-1]
                
                search_url = f"{api_url}/?ac=videolist&wd={quote(keyword)}"
                
                logger.info(f"搜索站点 [{site['name']}]: {search_url}")
                
                response = requests.get(search_url, timeout=10)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data.get('code') == 1 and data.get('list'):
                            logger.info(f"站点 [{site['name']}] 返回 {len(data['list'])} 条结果")
                            return {
                                'site': site['name'],
                                'data': data
                            }
                        else:
                            logger.debug(f"站点 [{site['name']}] 无结果 (code: {data.get('code')}, list长度: {len(data.get('list', []))})")
                    except json.JSONDecodeError as e:
                        logger.error(f"站点 [{site['name']}] 响应JSON解析失败: {e}")
                        logger.debug(f"响应内容: {response.text[:200]}")
                else:
                    logger.warning(f"站点 [{site['name']}] 请求失败: {response.status_code}")
                    logger.debug(f"响应内容: {response.text[:200]}")
            except Exception as e:
                logger.error(f"站点 [{site['name']}] 搜索异常: {e}")
            return None
        
        # 并发请求所有站点
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(fetch_site, site): site for site in api_sites}
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    all_results.append(result)
        
        return all_results
    
    def merge_results(self, all_results: List[Dict]) -> List[Dict]:
        """
        合并和去重搜索结果
        
        Args:
            all_results: 所有API站点返回的结果
        
        Returns:
            合并去重后的资源列表
        """
        # 按vod_name去重
        name_map: Dict[str, Dict] = {}
        
        for result in all_results:
            for item in result['data'].get('list', []):
                vod_name = item.get('vod_name', '')
                if not vod_name:
                    continue
                
                if vod_name not in name_map:
                    name_map[vod_name] = item.copy()
                else:
                    # 合并vod_play_url（按平台去重）
                    existing_item = name_map[vod_name]
                    existing_urls = self.parse_play_urls(existing_item.get('vod_play_url', ''))
                    new_urls = self.parse_play_urls(item.get('vod_play_url', ''))
                    
                    # 合并URL，按平台去重
                    merged_urls = self.merge_play_urls(existing_urls, new_urls)
                    existing_item['vod_play_url'] = self.format_play_urls(merged_urls)
                    
                    # 合并其他字段（保留更完整的信息）
                    if not existing_item.get('vod_pic') and item.get('vod_pic'):
                        existing_item['vod_pic'] = item['vod_pic']
                    if not existing_item.get('vod_content') and item.get('vod_content'):
                        existing_item['vod_content'] = item['vod_content']
        
        return list(name_map.values())
    
    def parse_play_urls(self, play_url_str: str) -> Dict[str, str]:
        """
        解析vod_play_url字符串，提取平台和URL
        
        Args:
            play_url_str: vod_play_url字符串，格式：正片$url1$$$正片$url2
        
        Returns:
            字典，key为平台标识，value为URL
        """
        urls = {}
        if not play_url_str or not play_url_str.strip():
            return urls
        
        # 分割：$$$
        parts = play_url_str.split('$$$')
        for part in parts:
            part = part.strip()
            if not part or '$' not in part:
                continue
            
            # 格式：正片$url 或 平台名$url
            parts_split = part.split('$', 1)
            if len(parts_split) == 2:
                label, url = parts_split
                url = url.strip()  # 去除可能的空格
                
                # 验证URL格式
                if not url or not url.startswith(('http://', 'https://')):
                    logger.debug(f"跳过无效URL: {url[:50]}...")
                    continue
                
                # 识别平台
                platform = self.identify_platform(url)
                if platform:
                    # 如果平台已存在，保留第一个（去重）
                    if platform not in urls:
                        urls[platform] = url
                    else:
                        logger.debug(f"平台 [{platform}] 已存在，跳过重复URL")
                else:
                    logger.debug(f"无法识别平台，跳过URL: {url[:50]}...")
        
        return urls
    
    def identify_platform(self, url: str) -> Optional[str]:
        """
        识别视频平台
        
        Args:
            url: 视频URL
        
        Returns:
            平台标识（bilibili、vqq、youku、iqiyi等）
        """
        url_lower = url.lower()
        if 'bilibili.com' in url_lower or 'b23.tv' in url_lower:
            return 'bilibili'
        elif 'v.qq.com' in url_lower:
            return 'vqq'  # 使用vqq而不是qq，与用户需求一致
        elif 'qq.com' in url_lower:
            return 'vqq'
        elif 'youku.com' in url_lower:
            return 'youku'
        elif 'iqiyi.com' in url_lower:
            return 'iqiyi'
        elif 'mgtv.com' in url_lower:
            return 'mgtv'
        elif 'le.com' in url_lower:
            return 'letv'
        else:
            return None  # 不识别平台时返回None，不添加到字典中
    
    def merge_play_urls(self, urls1: Dict[str, str], urls2: Dict[str, str]) -> Dict[str, str]:
        """
        合并两个URL字典，相同平台只保留一个
        
        Args:
            urls1: 第一个URL字典
            urls2: 第二个URL字典
        
        Returns:
            合并后的URL字典
        """
        merged = urls1.copy()
        for platform, url in urls2.items():
            if platform not in merged:
                merged[platform] = url
        return merged
    
    def format_play_urls(self, urls: Dict[str, str]) -> str:
        """
        格式化URL字典为vod_play_url字符串
        
        Args:
            urls: URL字典
        
        Returns:
            格式化后的字符串
        """
        parts = []
        for platform, url in urls.items():
            parts.append(f"正片${url}")
        return '$$$'.join(parts)
    
    def parse_video_urls(self, play_url_str: str, parser_url: str = "https://jx.789jiexi.com") -> str:
        """
        解析vod_play_url中的所有视频URL，替换为m3u8地址
        
        Args:
            play_url_str: vod_play_url字符串
            parser_url: 解析网站URL
        
        Returns:
            解析后的vod_play_url字符串（失败的部分会被删除）
        """
        urls = self.parse_play_urls(play_url_str)
        parsed_urls = {}
        
        for platform, url in urls.items():
            # 验证URL格式
            if not url or not url.startswith(('http://', 'https://')):
                logger.warning(f"[{platform}] URL格式无效，跳过: {url[:100]}...")
                continue
            
            logger.info(f"解析 [{platform}] URL: {url[:100]}...")
            
            # 先尝试z参数方案
            m3u8_url = self.z_param_parser.parse(url)
            
            # 如果失败，尝试解密方案
            if not m3u8_url:
                logger.info(f"[{platform}] z参数方案失败，尝试解密方案...")
                m3u8_url = self.decrypt_parser.parse(parser_url, url)
            
            if m3u8_url:
                parsed_urls[platform] = m3u8_url
                logger.info(f"[{platform}] 解析成功")
            else:
                logger.warning(f"[{platform}] 解析失败，将删除")
        
        return self.format_play_urls(parsed_urls)
    
    def search_and_parse(self, keyword: str, parser_url: str = "https://jx.789jiexi.com") -> Dict:
        """
        搜索资源并解析视频地址
        
        Args:
            keyword: 搜索关键词
            parser_url: 解析网站URL
        
        Returns:
            搜索结果，包含解析后的m3u8地址
        """
        logger.info(f"搜索资源: {keyword}")
        
        # 1. 搜索所有API站点
        all_results = self.search_api_sites(keyword)
        
        if not all_results:
            logger.warning("所有API站点都无结果")
            return {
                "code": 1,
                "msg": "数据列表",
                "page": 1,
                "pagecount": 0,
                "limit": 20,
                "total": 0,
                "list": []
            }
        
        # 2. 合并去重
        merged_list = self.merge_results(all_results)
        logger.info(f"合并后共 {len(merged_list)} 条资源")
        
        # 3. 解析视频地址
        parsed_list = []
        for item in merged_list:
            play_url = item.get('vod_play_url', '')
            if not play_url:
                logger.debug(f"资源 [{item.get('vod_name')}] 没有vod_play_url，跳过")
                continue
            
            # 解析所有视频URL
            parsed_play_url = self.parse_video_urls(play_url, parser_url)
            
            # 如果解析后还有URL，保留该资源
            if parsed_play_url and parsed_play_url.strip():
                item['vod_play_url'] = parsed_play_url
                parsed_list.append(item)
                logger.debug(f"资源 [{item.get('vod_name')}] 解析成功，保留 {len(self.parse_play_urls(parsed_play_url))} 个URL")
            else:
                logger.warning(f"资源 [{item.get('vod_name')}] 所有URL解析失败，已删除")
        
        logger.info(f"解析后剩余 {len(parsed_list)} 条资源")
        
        # 如果所有资源都解析失败，返回空列表
        if not parsed_list:
            logger.warning("所有资源解析失败，返回空列表")
            return {
                "code": 1,
                "msg": "数据列表",
                "page": 1,
                "pagecount": 0,
                "limit": 20,
                "total": 0,
                "list": []
            }
        
        return {
            "code": 1,
            "msg": "数据列表",
            "page": 1,
            "pagecount": 1 if parsed_list else 0,
            "limit": 20,
            "total": len(parsed_list),
            "list": parsed_list
        }

