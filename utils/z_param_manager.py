"""
z参数管理器模块
负责z参数的过期检测、自动更新和缓存管理
"""
import json
import time
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime, timedelta
from .logger import logger

# 数据目录
DATA_DIR = Path("/app/data")
if not DATA_DIR.exists():
    DATA_DIR = Path("./data")
DATA_DIR.mkdir(exist_ok=True)

Z_PARAMS_FILE = DATA_DIR / "z_params.json"


class ZParamManager:
    """z参数管理器"""
    
    def __init__(self):
        """初始化z参数管理器"""
        self.z_params: Dict = {}
        self.load_params()
    
    def load_params(self) -> Dict:
        """
        从文件加载z参数
        
        Returns:
            z参数字典
        """
        try:
            if Z_PARAMS_FILE.exists():
                with open(Z_PARAMS_FILE, 'r', encoding='utf-8') as f:
                    self.z_params = json.load(f)
                logger.info("z参数加载成功")
            else:
                logger.warning("z参数文件不存在，将使用默认值或自动获取")
                self.z_params = {}
            return self.z_params
        except Exception as e:
            logger.error(f"加载z参数失败: {e}")
            self.z_params = {}
            return self.z_params
    
    def save_params(self, z_param: str, s1ig_param: str = "11397", g_param: str = "") -> bool:
        """
        保存z参数到文件
        
        Args:
            z_param: z参数值
            s1ig_param: s1ig参数值
            g_param: g参数值
        
        Returns:
            是否保存成功
        """
        try:
            self.z_params = {
                "z_param": z_param,
                "s1ig_param": s1ig_param,
                "g_param": g_param,
                "updated_at": datetime.now().isoformat(),
                "expires_in": 86400,  # 24小时
                "source": "playwright"
            }
            
            with open(Z_PARAMS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.z_params, f, indent=2, ensure_ascii=False)
            
            logger.info("z参数保存成功")
            return True
        except Exception as e:
            logger.error(f"保存z参数失败: {e}")
            return False
    
    def get_z_param(self) -> Optional[str]:
        """获取z参数"""
        return self.z_params.get("z_param")
    
    def get_s1ig_param(self) -> str:
        """获取s1ig参数"""
        return self.z_params.get("s1ig_param", "11397")
    
    def get_g_param(self) -> str:
        """获取g参数"""
        return self.z_params.get("g_param", "")
    
    def is_expired(self, max_age_hours: int = 24) -> bool:
        """
        检查z参数是否过期
        
        Args:
            max_age_hours: 最大有效期（小时）
        
        Returns:
            是否过期
        """
        if not self.z_params or not self.z_params.get("z_param"):
            logger.info("z参数不存在，视为过期")
            return True
        
        updated_at_str = self.z_params.get("updated_at")
        if not updated_at_str:
            logger.info("z参数更新时间不存在，视为过期")
            return True
        
        try:
            updated_at = datetime.fromisoformat(updated_at_str)
            age = datetime.now() - updated_at
            max_age = timedelta(hours=max_age_hours)
            
            is_expired = age > max_age
            if is_expired:
                logger.info(f"z参数已过期（年龄: {age}, 最大: {max_age}）")
            else:
                logger.debug(f"z参数有效（年龄: {age}）")
            
            return is_expired
        except Exception as e:
            logger.error(f"检查z参数过期状态失败: {e}")
            return True
    
    def get_age_seconds(self) -> int:
        """获取z参数年龄（秒）"""
        updated_at_str = self.z_params.get("updated_at")
        if not updated_at_str:
            return 0
        
        try:
            updated_at = datetime.fromisoformat(updated_at_str)
            age = datetime.now() - updated_at
            return int(age.total_seconds())
        except Exception:
            return 0
    
    def update_with_playwright(self, video_url: str) -> Optional[str]:
        """
        使用Playwright更新z参数
        
        Args:
            video_url: 视频URL（用于测试）
        
        Returns:
            新的z参数值，如果失败返回None
        """
        try:
            from playwright.sync_api import sync_playwright
            
            logger.info("开始使用Playwright获取z参数...")
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()
                
                # 访问解析网站
                parser_url = f"https://videocdn.ihelpy.net/jiexi/m1907.html?m1907jx={video_url}"
                page.goto(parser_url, wait_until='networkidle', timeout=30000)
                
                # 等待页面加载
                page.wait_for_timeout(3000)
                
                # 监听网络请求，捕获API调用
                z_param = None
                s1ig_param = "11397"
                g_param = ""
                
                def handle_request(request):
                    nonlocal z_param, s1ig_param, g_param
                    url = request.url
                    if 'api/v' in url:
                        # 提取参数
                        if 'z=' in url:
                            import re
                            z_match = re.search(r'z=([a-f0-9]{32})', url, re.IGNORECASE)
                            if z_match:
                                z_param = z_match.group(1)
                                logger.info(f"捕获到z参数: {z_param}")
                        
                        if 's1ig=' in url:
                            import re
                            s1ig_match = re.search(r's1ig=([^&]+)', url)
                            if s1ig_match:
                                s1ig_param = s1ig_match.group(1)
                        
                        if 'g=' in url:
                            import re
                            g_match = re.search(r'g=([^&]+)', url)
                            if g_match:
                                g_param = g_match.group(1)
                
                page.on("request", handle_request)
                
                # 等待API调用
                page.wait_for_timeout(5000)
                
                browser.close()
                
                if z_param:
                    self.save_params(z_param, s1ig_param, g_param)
                    logger.info("z参数更新成功")
                    return z_param
                else:
                    logger.warning("未能捕获到z参数")
                    return None
                    
        except ImportError:
            logger.error("Playwright未安装，无法更新z参数")
            return None
        except Exception as e:
            logger.error(f"使用Playwright更新z参数失败: {e}")
            return None
    
    def update_with_http(self, video_url: str) -> Optional[str]:
        """
        使用HTTP请求更新z参数（备用方案）
        
        Args:
            video_url: 视频URL
        
        Returns:
            新的z参数值，如果失败返回None
        """
        try:
            import requests
            import re
            
            logger.info("开始使用HTTP请求获取z参数...")
            
            parser_url = f"https://videocdn.ihelpy.net/jiexi/m1907.html?m1907jx={video_url}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            
            response = requests.get(parser_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                html = response.text
                
                # 从API调用URL中提取z参数
                api_url_pattern = r'https://[^/]+/api/v/\?[^"\'<>]*z=([a-f0-9]{32})'
                matches = re.findall(api_url_pattern, html, re.IGNORECASE)
                
                if matches:
                    z_param = matches[0]
                    self.save_params(z_param)
                    logger.info("z参数更新成功（HTTP方式）")
                    return z_param
            
            logger.warning("未能从HTTP响应中提取z参数")
            return None
            
        except Exception as e:
            logger.error(f"使用HTTP请求更新z参数失败: {e}")
            return None


# 全局z参数管理器实例
z_param_manager = ZParamManager()

