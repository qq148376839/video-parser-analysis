"""
直接获取 m3u8 链接
尝试通过API调用直接获取 m3u8 链接，而不需要浏览器自动化
"""

import requests
import json
import re
from typing import Optional, Dict
from urllib.parse import urlencode, quote, urlparse, parse_qs


class DirectM3U8Getter:
    """直接获取 m3u8 链接"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://jx.2s0.cn/',
            'Origin': 'https://jx.2s0.cn',
        })
    
    def get_config_from_api(self) -> Optional[Dict]:
        """从 /admin/api.php 获取配置"""
        print("\n[步骤1] 调用 /admin/api.php 获取配置...")
        api_url = "https://jx.2s0.cn/admin/api.php"
        
        try:
            response = self.session.get(api_url, timeout=30)
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ 获取配置成功")
                    print(f"   配置数据: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
                    return data
                except:
                    print(f"   ⚠️ 响应不是JSON格式")
                    print(f"   响应内容: {response.text[:500]}")
            else:
                print(f"   ❌ API返回状态码: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 请求失败: {e}")
        
        return None
    
    def try_direct_api_calls(self, video_url: str, config_id: Optional[str] = None) -> Optional[str]:
        """尝试直接调用可能的API获取m3u8链接"""
        print("\n[步骤2] 尝试直接调用API获取m3u8...")
        
        # 可能的API端点模式
        possible_apis = [
            # 模式1: 使用video_url作为参数
            f"https://jx.2s0.cn/api.php?url={quote(video_url)}",
            f"https://jx.2s0.cn/jiexi.php?url={quote(video_url)}",
            f"https://jx.2s0.cn/parse.php?url={quote(video_url)}",
            f"https://jx.2s0.cn/player/api.php?url={quote(video_url)}",
            f"https://jx.2s0.cn/player/jiexi.php?url={quote(video_url)}",
            
            # 模式2: 使用config.id作为参数
            f"https://jx.2s0.cn/api.php?id={quote(config_id)}" if config_id else None,
            f"https://jx.2s0.cn/jiexi.php?id={quote(config_id)}" if config_id else None,
            f"https://jx.2s0.cn/parse.php?id={quote(config_id)}" if config_id else None,
            
            # 模式3: 使用cachem3u8域名
            f"https://cachem3u8.2s0.cn:8899/api.php?url={quote(video_url)}",
            f"https://cachem3u8.2s0.cn:8899/jiexi.php?url={quote(video_url)}",
            f"https://cachem3u8.2s0.cn:8899/parse.php?url={quote(video_url)}",
        ]
        
        for api_url in possible_apis:
            if not api_url:
                continue
            
            print(f"\n   🔍 尝试API: {api_url}")
            try:
                response = self.session.get(api_url, timeout=10)
                
                if response.status_code == 200:
                    content = response.text
                    
                    # 检查是否包含m3u8链接
                    m3u8_patterns = [
                        r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
                        r'["\']([^"\']+cachem3u8[^"\']*\.m3u8[^"\']*)["\']',
                        r'(https?://cachem3u8\.2s0\.cn:8899[^\s"\'<>]+\.m3u8[^\s"\'<>]*)',
                    ]
                    
                    for pattern in m3u8_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        for match in matches:
                            url = match if isinstance(match, str) else match[0] if match else None
                            if url and url.startswith('http') and '.m3u8' in url:
                                print(f"   ✅ 找到m3u8链接: {url}")
                                return url
                    
                    # 检查是否是JSON响应
                    try:
                        json_data = response.json()
                        json_str = json.dumps(json_data)
                        if '.m3u8' in json_str or 'cachem3u8' in json_str:
                            print(f"   ✅ JSON响应包含m3u8相关信息")
                            print(f"   响应: {json.dumps(json_data, indent=2, ensure_ascii=False)[:500]}")
                            
                            # 尝试提取m3u8链接
                            if isinstance(json_data, dict):
                                for key, value in json_data.items():
                                    if isinstance(value, str) and '.m3u8' in value:
                                        return value
                                    elif isinstance(value, dict):
                                        for k, v in value.items():
                                            if isinstance(v, str) and '.m3u8' in v:
                                                return v
                    except:
                        pass
                
            except Exception as e:
                print(f"   ⚠️ 请求失败: {e}")
                continue
        
        print(f"   ❌ 所有API尝试都未找到m3u8链接")
        return None
    
    def try_construct_m3u8_url(self, config_id: Optional[str] = None, config_url: Optional[str] = None) -> Optional[str]:
        """尝试构造m3u8链接（如果知道hash和token的生成规则）"""
        print("\n[步骤3] 尝试构造m3u8链接...")
        
        if not config_id:
            print(f"   ⚠️ 缺少config.id，无法构造")
            return None
        
        # 根据观察到的m3u8链接格式：
        # https://cachem3u8.2s0.cn:8899/Cache/Ff/{hash}.m3u8?token={token}
        # hash看起来像是MD5或SHA1
        # token看起来像是十六进制字符串
        
        # 尝试使用config.id生成hash
        import hashlib
        
        # 可能的hash生成方式
        hash_candidates = [
            hashlib.md5(config_id.encode()).hexdigest(),
            hashlib.sha1(config_id.encode()).hexdigest(),
            hashlib.md5((config_id + ' P').encode()).hexdigest(),
        ]
        
        # 可能的token生成方式（需要进一步分析）
        # token可能是基于config.url或其他数据生成的
        
        print(f"   💡 需要进一步分析hash和token的生成规则")
        print(f"   已知信息:")
        print(f"      - config.id: {config_id}")
        print(f"      - m3u8格式: https://cachem3u8.2s0.cn:8899/Cache/Ff/{{hash}}.m3u8?token={{token}}")
        print(f"      - hash示例: 2089c333a6d6a31e306bd190557aea36 (32字符，可能是MD5)")
        print(f"      - token示例: d3d315341476033443543795551335e6c4a6f6c68653438423247664a40533770383968597961423071364c45567457717479585f294d45633251343f207643663273386e60563970776243676545373b2a425f643d426a4")
        
        return None
    
    def get_m3u8_from_analysis_page(self, video_url: str) -> Optional[str]:
        """从analysis.php页面提取m3u8链接"""
        print("\n[步骤4] 从analysis.php页面提取m3u8链接...")
        
        analysis_url = f"https://jx.2s0.cn/player/analysis.php?v={quote(video_url)}"
        print(f"   URL: {analysis_url}")
        
        try:
            response = self.session.get(analysis_url, timeout=30)
            if response.status_code == 200:
                html = response.text
                
                # 查找m3u8链接
                m3u8_patterns = [
                    r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
                    r'["\']([^"\']+cachem3u8[^"\']*\.m3u8[^"\']*)["\']',
                    r'(https?://cachem3u8\.2s0\.cn:8899[^\s"\'<>]+\.m3u8[^\s"\'<>]*)',
                ]
                
                for pattern in m3u8_patterns:
                    matches = re.findall(pattern, html, re.IGNORECASE)
                    for match in matches:
                        url = match if isinstance(match, str) else match[0] if match else None
                        if url and url.startswith('http') and '.m3u8' in url:
                            print(f"   ✅ 在HTML中找到m3u8链接: {url}")
                            return url
                
                print(f"   ⚠️ HTML中未找到m3u8链接（可能需要JavaScript执行）")
            else:
                print(f"   ❌ 请求失败，状态码: {response.status_code}")
        except Exception as e:
            print(f"   ❌ 请求失败: {e}")
        
        return None
    
    def parse_video(self, video_url: str) -> Optional[str]:
        """解析视频，获取m3u8链接"""
        print("=" * 60)
        print("直接获取 m3u8 链接")
        print("=" * 60)
        print(f"目标视频: {video_url}")
        
        # 步骤1: 获取配置
        config = self.get_config_from_api()
        config_id = None
        config_url = None
        
        if config and isinstance(config, dict):
            if 'data' in config:
                config_id = config['data'].get('id')
                config_url = config['data'].get('url')
            elif 'id' in config:
                config_id = config.get('id')
                config_url = config.get('url')
        
        # 步骤2: 尝试直接调用API
        m3u8_url = self.try_direct_api_calls(video_url, config_id)
        
        if m3u8_url:
            print(f"\n✅ 成功获取m3u8链接: {m3u8_url}")
            return m3u8_url
        
        # 步骤3: 尝试从analysis.php页面提取
        m3u8_url = self.get_m3u8_from_analysis_page(video_url)
        
        if m3u8_url:
            print(f"\n✅ 成功从页面提取m3u8链接: {m3u8_url}")
            return m3u8_url
        
        # 步骤4: 尝试构造m3u8链接
        m3u8_url = self.try_construct_m3u8_url(config_id, config_url)
        
        print(f"\n❌ 无法直接获取m3u8链接")
        print(f"\n💡 建议:")
        print(f"   1. m3u8链接可能是通过JavaScript动态生成的")
        print(f"   2. 需要使用浏览器自动化工具来执行JavaScript")
        print(f"   3. 或者需要进一步分析hash和token的生成算法")
        
        return None


def main():
    """主函数"""
    video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    
    getter = DirectM3U8Getter()
    m3u8_url = getter.parse_video(video_url)
    
    if m3u8_url:
        print(f"\n🎬 最终m3u8链接: {m3u8_url}")
        print(f"\n📥 使用ffmpeg下载:")
        print(f'   ffmpeg -i "{m3u8_url}" -c copy output.mp4')


if __name__ == '__main__':
    main()


