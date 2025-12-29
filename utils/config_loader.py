"""
配置加载器模块
读取和管理config.json配置文件
"""
import json
from pathlib import Path
from typing import Dict, Optional, List
from .logger import logger

# 数据目录
DATA_DIR = Path("/app/data")
if not DATA_DIR.exists():
    DATA_DIR = Path("./data")
DATA_DIR.mkdir(exist_ok=True)

CONFIG_FILE = DATA_DIR / "config.json"
CONFIG_EXAMPLE_FILE = Path("./config.json.example")


class ConfigLoader:
    """配置加载器"""
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        初始化配置加载器
        
        Args:
            config_file: 配置文件路径，默认使用DATA_DIR/config.json
        """
        self.config_file = config_file or CONFIG_FILE
        self.config: Dict = {}
        self.load_config()
    
    def load_config(self) -> Dict:
        """
        加载配置文件
        
        Returns:
            配置字典
        """
        try:
            if not self.config_file.exists():
                logger.warning(f"配置文件不存在: {self.config_file}")
                logger.info(f"请从 {CONFIG_EXAMPLE_FILE} 复制并配置")
                # 尝试从示例文件加载
                if CONFIG_EXAMPLE_FILE.exists():
                    logger.info(f"使用示例配置文件: {CONFIG_EXAMPLE_FILE}")
                    self.config_file = CONFIG_EXAMPLE_FILE
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            logger.info(f"配置文件加载成功: {self.config_file}")
            return self.config
            
        except json.JSONDecodeError as e:
            logger.error(f"配置文件JSON格式错误: {e}")
            self.config = {}
            return self.config
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            self.config = {}
            return self.config
    
    def get_cache_time(self) -> int:
        """获取缓存时间（秒）"""
        return self.config.get("cache_time", 7200)
    
    def get_api_sites(self) -> Dict:
        """获取API站点配置"""
        return self.config.get("api_site", {})
    
    def get_api_site_list(self) -> List[Dict]:
        """
        获取API站点列表
        
        Returns:
            API站点列表，每个元素包含：key, api, name, official_parser
        """
        sites = []
        api_sites = self.get_api_sites()
        
        for key, site_config in api_sites.items():
            sites.append({
                "key": key,
                "api": site_config.get("api", ""),
                "name": site_config.get("name", key),
                "official_parser": site_config.get("official_parser", True)
            })
        
        return sites
    
    def reload(self) -> Dict:
        """重新加载配置"""
        return self.load_config()


# 全局配置加载器实例
config_loader = ConfigLoader()

