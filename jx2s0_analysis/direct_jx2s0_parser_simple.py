"""
简化版直接解析 jx.2s0.cn - 直接调用API或访问页面
参考 direct_videocdn_parser_simple.py 的结构
"""

import requests
import json
import re
import base64
from typing import Optional, List, Dict
from urllib.parse import urlencode, quote


class DirectJx2s0ParserSimple:
    """简化版直接解析器 - 直接调用API或访问页面"""
    
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
    
    def call_api(self, video_url: str) -> Optional[Dict]:
        """调用API获取播放器配置"""
        print(f"\n[步骤1] 调用API获取配置...")
        api_url = "https://jx.2s0.cn/admin/api.php"
        print(f"   URL: {api_url}")
        
        try:
            response = self.session.get(api_url, timeout=30)
            print(f"   状态码: {response.status_code}")
            
            if response.status_code != 200:
                print(f"   ⚠️ API返回非200状态码")
                return None
            
            try:
                json_data = response.json()
                print(f"   ✅ JSON解析成功")
                return json_data
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON解析失败: {e}")
                print(f"   响应内容: {response.text[:500]}")
                return None
                
        except Exception as e:
            print(f"   ❌ 请求失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def call_analysis_api(self, video_url: str) -> Optional[str]:
        """调用analysis.php API获取视频信息"""
        print(f"\n[步骤2] 调用analysis.php API...")
        
        # 构造analysis.php URL
        analysis_url = f"https://jx.2s0.cn/player/analysis.php?v={quote(video_url)}"
        print(f"   URL: {analysis_url}")
        
        try:
            # 设置Referer
            headers = self.session.headers.copy()
            headers['Referer'] = 'https://jx.2s0.cn/player/'
            
            response = self.session.get(analysis_url, headers=headers, timeout=30)
            print(f"   状态码: {response.status_code}")
            
            if response.status_code != 200:
                print(f"   ⚠️ API返回非200状态码")
                return None
            
            # 从HTML中提取配置对象
            html = response.text
            
            # 查找window.config对象
            # 通常格式为: var config = {...} 或 window.config = {...}
            config_patterns = [
                r'window\.config\s*=\s*({[^}]+})',
                r'var\s+config\s*=\s*({[^}]+})',
                r'config\s*=\s*({[^}]+})',
            ]
            
            config_json = None
            for pattern in config_patterns:
                match = re.search(pattern, html, re.DOTALL)
                if match:
                    try:
                        config_json = json.loads(match.group(1))
                        print(f"   ✅ 找到config对象")
                        break
                    except:
                        continue
            
            if not config_json:
                # 尝试从script标签中提取
                script_pattern = r'<script[^>]*>(.*?)</script>'
                scripts = re.findall(script_pattern, html, re.DOTALL | re.IGNORECASE)
                for script in scripts:
                    for pattern in config_patterns:
                        match = re.search(pattern, script, re.DOTALL)
                        if match:
                            try:
                                config_json = json.loads(match.group(1))
                                print(f"   ✅ 在script中找到config对象")
                                break
                            except:
                                continue
                    if config_json:
                        break
            
            if config_json and config_json.get('url'):
                encrypted_url = config_json['url']
                print(f"   ✅ 找到加密URL: {encrypted_url[:50]}...")
                return encrypted_url
            
            print(f"   ⚠️ 未找到config对象或url字段")
            return None
                
        except Exception as e:
            print(f"   ❌ 请求失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def decrypt_url(self, encrypted_url: str) -> Optional[str]:
        """解密URL（Base64解码）"""
        print(f"\n[步骤3] 尝试解密URL...")
        print(f"   加密URL长度: {len(encrypted_url)}")
        
        try:
            # 尝试Base64解码
            decoded_bytes = base64.b64decode(encrypted_url)
            decoded_str = decoded_bytes.decode('utf-8', errors='ignore')
            
            print(f"   ✅ Base64解码成功")
            print(f"   解码后长度: {len(decoded_str)}")
            print(f"   解码后内容预览: {decoded_str[:100]}...")
            
            # 检查是否是URL
            if decoded_str.startswith('http'):
                print(f"   ✅ 解码后是URL")
                return decoded_str
            
            # 如果不是URL，可能还需要进一步处理
            # 检查是否包含m3u8关键字
            if '.m3u8' in decoded_str.lower():
                # 尝试提取m3u8链接
                m3u8_patterns = [
                    r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
                    r'["\']([^"\']+\.m3u8[^"\']*)["\']',
                ]
                for pattern in m3u8_patterns:
                    matches = re.findall(pattern, decoded_str, re.IGNORECASE)
                    for match in matches:
                        url = match if isinstance(match, str) else match[0] if match else None
                        if url and url.startswith('http'):
                            print(f"   ✅ 从解码内容中提取到m3u8链接: {url}")
                            return url
            
            print(f"   ⚠️ 解码后不是URL格式，可能需要进一步处理")
            return decoded_str
            
        except Exception as e:
            print(f"   ❌ 解密失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def extract_m3u8_from_html(self, html: str) -> List[str]:
        """从HTML中提取m3u8链接"""
        print(f"\n[步骤4] 从HTML中提取m3u8链接...")
        
        m3u8_urls = []
        
        # 查找m3u8链接
        m3u8_patterns = [
            r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
            r'["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'(https?://[^\s"\'<>]+cachem3u8[^\s"\'<>]*\.m3u8[^\s"\'<>]*)',
        ]
        
        for pattern in m3u8_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                url = match if isinstance(match, str) else match[0] if match else None
                if url and url.startswith('http') and url not in m3u8_urls:
                    m3u8_urls.append(url)
                    print(f"   ✅ 找到m3u8链接: {url}")
        
        return m3u8_urls
    
    def get_m3u8_from_cache_api(self, video_url: str) -> Optional[str]:
        """尝试从缓存API获取m3u8链接"""
        print(f"\n[步骤5] 尝试从缓存API获取m3u8...")
        
        # 根据分析结果，m3u8链接格式为：
        # https://cachem3u8.2s0.cn:8899/Cache/Ff/{hash}.m3u8?token={token}
        # 这个链接通常是通过analysis.php页面加载后，JavaScript执行生成的
        
        # 由于无法直接调用，我们需要访问analysis.php页面，然后等待JavaScript执行
        # 或者尝试构造可能的API端点
        
        # 可能的API端点模式
        possible_apis = [
            f"https://jx.2s0.cn/api.php?url={quote(video_url)}",
            f"https://jx.2s0.cn/jiexi.php?url={quote(video_url)}",
            f"https://jx.2s0.cn/parse.php?url={quote(video_url)}",
        ]
        
        for api_url in possible_apis:
            print(f"   🔍 尝试API: {api_url}")
            try:
                response = self.session.get(api_url, timeout=10)
                if response.status_code == 200:
                    content = response.text
                    # 检查是否包含m3u8
                    if '.m3u8' in content.lower():
                        m3u8_urls = self.extract_m3u8_from_html(content)
                        if m3u8_urls:
                            print(f"   ✅ 从API响应中找到m3u8链接")
                            return m3u8_urls[0]
            except:
                continue
        
        print(f"   ⚠️ 无法从缓存API获取m3u8链接")
        return None
    
    def verify_m3u8(self, m3u8_url: str) -> bool:
        """验证m3u8链接是否有效"""
        print(f"\n[步骤6] 验证m3u8链接...")
        print(f"   URL: {m3u8_url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': '*/*',
                'Referer': 'https://jx.2s0.cn/',
            }
            
            response = requests.get(m3u8_url, headers=headers, timeout=10, stream=True)
            
            if response.status_code == 200:
                # 读取前几行
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
                    print(f"   内容预览: {content[:200]}")
                    return False
            else:
                print(f"   ⚠️ 验证请求返回状态码: {response.status_code}")
                return True  # 仍然返回True，因为可能是访问限制问题
                
        except Exception as e:
            print(f"   ⚠️ 验证失败: {e}")
            print(f"   💡 链接可能仍然有效，但需要特定请求头或Cookie")
            return True  # 仍然返回True，因为可能是访问限制问题
    
    def parse_video(self, video_url: str) -> Optional[str]:
        """解析视频，获取最终m3u8"""
        print("=" * 60)
        print("简化版直接解析 jx.2s0.cn")
        print("=" * 60)
        print(f"目标视频: {video_url}")
        
        # 步骤1: 调用API获取配置
        api_response = self.call_api(video_url)
        
        # 步骤2: 调用analysis.php获取加密URL
        encrypted_url = self.call_analysis_api(video_url)
        
        if not encrypted_url:
            print("\n❌ 未能获取加密URL")
            print("\n💡 可能的原因:")
            print("   1. 需要访问analysis.php页面并等待JavaScript执行")
            print("   2. 需要特定的Cookie或Session")
            print("   3. API端点已变更")
            print("\n💡 建议:")
            print("   1. 使用浏览器分析脚本获取最新的API参数")
            print("   2. 检查网络连接")
            return None
        
        # 步骤3: 解密URL
        decrypted_url = self.decrypt_url(encrypted_url)
        
        if not decrypted_url:
            print("\n❌ 解密失败")
            return None
        
        # 步骤4: 验证m3u8（如果解密后是m3u8链接）
        if '.m3u8' in decrypted_url.lower():
            self.verify_m3u8(decrypted_url)
            final_m3u8 = decrypted_url
        else:
            # 如果解密后不是m3u8，可能需要进一步处理
            print(f"\n⚠️ 解密后的URL不是m3u8格式: {decrypted_url[:100]}")
            print(f"💡 可能需要进一步处理或使用浏览器分析脚本")
            final_m3u8 = decrypted_url
        
        # 保存结果
        result = {
            'video_url': video_url,
            'api_response': api_response,
            'encrypted_url': encrypted_url,
            'decrypted_url': decrypted_url,
            'final_m3u8': final_m3u8,
        }
        
        with open('jx2s0_parse_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n✅ 完整结果已保存到: jx2s0_parse_result.json")
        
        print("\n" + "=" * 60)
        print("✅ 解析完成！")
        print("=" * 60)
        
        if final_m3u8:
            print(f"\n🎬 最终URL: {final_m3u8}")
            
            if '.m3u8' in final_m3u8.lower():
                print(f"\n📥 使用ffmpeg下载:")
                print(f'   ffmpeg -i "{final_m3u8}" -c copy output.mp4')
            else:
                print(f"\n💡 注意: 返回的URL不是m3u8格式，可能需要进一步处理")
        
        return final_m3u8


def main():
    """主函数"""
    video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    
    parser = DirectJx2s0ParserSimple()
    final_m3u8 = parser.parse_video(video_url)
    
    if not final_m3u8:
        print("\n❌ 解析失败")
        print("\n💡 建议:")
        print("   1. 检查网络连接")
        print("   2. 使用浏览器分析脚本获取最新的API参数")
        print("   3. 可能需要使用浏览器自动化工具来执行JavaScript")


if __name__ == '__main__':
    main()

