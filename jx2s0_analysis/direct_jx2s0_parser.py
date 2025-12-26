"""
直接解析 jx.2s0.cn - 从网络请求中提取m3u8链接
参考 direct_videocdn_parser_simple.py 的结构
"""

import requests
import json
import re
import base64
from typing import Optional, List, Dict
from urllib.parse import urlencode, quote
import time


class DirectJx2s0Parser:
    """直接解析器 - 从网络请求中提取m3u8链接"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Referer': 'https://jx.2s0.cn/',
            'Origin': 'https://jx.2s0.cn',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        })
    
    def get_config_from_api(self) -> Optional[Dict]:
        """从API获取配置"""
        print(f"\n[步骤1] 获取播放器配置...")
        api_url = "https://jx.2s0.cn/admin/api.php"
        print(f"   URL: {api_url}")
        
        try:
            response = self.session.get(api_url, timeout=30)
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    print(f"   ✅ 配置获取成功")
                    return json_data
                except:
                    print(f"   ⚠️ 响应不是JSON格式")
                    return None
            else:
                print(f"   ⚠️ API返回状态码: {response.status_code}")
                return None
        except Exception as e:
            print(f"   ❌ 请求失败: {e}")
            return None
    
    def get_video_id_from_dmku(self, video_url: str) -> Optional[str]:
        """从dmku API获取视频ID"""
        print(f"\n[步骤2] 获取视频ID...")
        
        # 访问analysis.php页面，可能会重定向或返回包含ID的信息
        analysis_url = f"https://jx.2s0.cn/player/analysis.php?v={quote(video_url)}"
        print(f"   URL: {analysis_url}")
        
        try:
            response = self.session.get(analysis_url, timeout=30)
            if response.status_code == 200:
                html = response.text
                
                # 从HTML中提取config对象
                # 查找 var config = {...}
                config_patterns = [
                    r'var\s+config\s*=\s*({[^}]+})',
                    r'config\s*=\s*({[^}]+})',
                ]
                
                for pattern in config_patterns:
                    match = re.search(pattern, html, re.DOTALL)
                    if match:
                        try:
                            config_str = match.group(1)
                            # 尝试提取id字段
                            id_match = re.search(r'"id"\s*:\s*"([^"]+)"', config_str)
                            if id_match:
                                video_id = id_match.group(1)
                                print(f"   ✅ 找到视频ID: {video_id}")
                                return video_id
                        except:
                            continue
                
                print(f"   ⚠️ 未找到视频ID")
                return None
            else:
                print(f"   ⚠️ 请求返回状态码: {response.status_code}")
                return None
        except Exception as e:
            print(f"   ❌ 请求失败: {e}")
            return None
    
    def get_m3u8_from_cache_api(self, video_id: str) -> Optional[str]:
        """从缓存API获取m3u8链接"""
        print(f"\n[步骤3] 尝试从缓存API获取m3u8...")
        
        # 根据分析结果，m3u8链接格式为：
        # https://cachem3u8.2s0.cn:8899/Cache/Ff/{hash}.m3u8?token={token}
        
        # 可能的API端点
        possible_apis = [
            f"https://jx.2s0.cn/api.php?id={quote(video_id)}",
            f"https://jx.2s0.cn/jiexi.php?id={quote(video_id)}",
            f"https://jx.2s0.cn/parse.php?id={quote(video_id)}",
            f"https://jx.2s0.cn/dmku/?ac=dm&id={quote(video_id)}%20P",
        ]
        
        for api_url in possible_apis:
            print(f"   🔍 尝试API: {api_url}")
            try:
                response = self.session.get(api_url, timeout=10)
                if response.status_code == 200:
                    content = response.text
                    
                    # 检查是否包含m3u8
                    if '.m3u8' in content.lower():
                        m3u8_patterns = [
                            r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
                            r'["\']([^"\']+\.m3u8[^"\']*)["\']',
                        ]
                        for pattern in m3u8_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            for match in matches:
                                url = match if isinstance(match, str) else match[0] if match else None
                                if url and url.startswith('http') and 'cachem3u8' in url:
                                    print(f"   ✅ 找到m3u8链接: {url}")
                                    return url
            except:
                continue
        
        print(f"   ⚠️ 无法从API获取m3u8链接")
        return None
    
    def verify_m3u8(self, m3u8_url: str) -> bool:
        """验证m3u8链接"""
        print(f"\n[步骤4] 验证m3u8链接...")
        print(f"   URL: {m3u8_url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': '*/*',
                'Referer': 'https://jx.2s0.cn/',
            }
            
            response = requests.get(m3u8_url, headers=headers, timeout=10, stream=True)
            
            if response.status_code == 200:
                content = ''
                for i, line in enumerate(response.iter_lines(decode_unicode=True)):
                    if i >= 5:
                        break
                    content += line + '\n'
                
                if content.strip().startswith('#EXTM3U'):
                    print(f"   ✅ m3u8链接有效")
                    print(f"   预览: {content[:200]}")
                    return True
                else:
                    print(f"   ⚠️ m3u8链接格式可能不正确")
                    return False
            else:
                print(f"   ⚠️ 验证请求返回状态码: {response.status_code}")
                return True
                
        except Exception as e:
            print(f"   ⚠️ 验证失败: {e}")
            return True
    
    def parse_video(self, video_url: str) -> Optional[str]:
        """解析视频，获取m3u8链接"""
        print("=" * 60)
        print("直接解析 jx.2s0.cn")
        print("=" * 60)
        print(f"目标视频: {video_url}")
        
        # 方法1: 尝试从analysis.php页面提取m3u8链接
        print(f"\n[方法1] 从analysis.php页面提取...")
        analysis_url = f"https://jx.2s0.cn/player/analysis.php?v={quote(video_url)}"
        
        try:
            response = self.session.get(analysis_url, timeout=30)
            if response.status_code == 200:
                html = response.text
                
                # 查找m3u8链接
                m3u8_patterns = [
                    r'https?://[^\s"\'<>]+cachem3u8[^\s"\'<>]*\.m3u8[^\s"\'<>]*',
                    r'["\']([^"\']+cachem3u8[^"\']*\.m3u8[^"\']*)["\']',
                ]
                
                for pattern in m3u8_patterns:
                    matches = re.findall(pattern, html, re.IGNORECASE)
                    for match in matches:
                        url = match if isinstance(match, str) else match[0] if match else None
                        if url and url.startswith('http'):
                            print(f"   ✅ 在HTML中找到m3u8链接: {url}")
                            self.verify_m3u8(url)
                            return url
        except Exception as e:
            print(f"   ⚠️ 方法1失败: {e}")
        
        # 方法2: 获取视频ID，然后尝试API
        print(f"\n[方法2] 通过API获取...")
        video_id = self.get_video_id_from_dmku(video_url)
        
        if video_id:
            m3u8_url = self.get_m3u8_from_cache_api(video_id)
            if m3u8_url:
                self.verify_m3u8(m3u8_url)
                return m3u8_url
        
        print(f"\n❌ 未能获取m3u8链接")
        print(f"\n💡 建议:")
        print(f"   1. 使用浏览器分析脚本获取m3u8链接")
        print(f"   2. m3u8链接可能需要JavaScript执行后才能生成")
        print(f"   3. 可能需要特定的Cookie或Session")
        
        return None


def main():
    """主函数"""
    video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    
    parser = DirectJx2s0Parser()
    m3u8_url = parser.parse_video(video_url)
    
    if m3u8_url:
        print("\n" + "=" * 60)
        print("✅ 解析成功！")
        print("=" * 60)
        print(f"\n🎬 m3u8链接: {m3u8_url}")
        print(f"\n📥 使用ffmpeg下载:")
        print(f'   ffmpeg -i "{m3u8_url}" -c copy output.mp4')
    else:
        print("\n❌ 解析失败")
        print("\n💡 建议使用 analyze_jx2s0_parser.py 脚本获取m3u8链接")


if __name__ == '__main__':
    main()

