"""
最终版本 v2 - 改进的解密逻辑
尝试更多密钥和IV组合，匹配CryptoJS/NotGm的实际行为
"""

import requests
import re
import json
import base64
from urllib.parse import urlparse, urljoin
from typing import Optional
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib


class FinalDirectParserV2:
    """最终版本直接解析器 v2 - 改进解密逻辑"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://jx.789jiexi.com/',
        })
    
    def get_iframe_url(self, parser_url: str, video_url: str) -> Optional[str]:
        """获取iframe URL"""
        print(f"\n[步骤1] 获取iframe URL...")
        full_url = f"{parser_url}/?url={video_url}"
        
        try:
            response = self.session.get(full_url, timeout=30)
            response.raise_for_status()
            
            html = response.text
            iframe_pattern = r'<iframe[^>]+src=["\']([^"\']+)["\']'
            iframe_matches = re.findall(iframe_pattern, html, re.IGNORECASE)
            
            if iframe_matches:
                iframe_url = iframe_matches[0]
                if not iframe_url.startswith('http'):
                    iframe_url = urljoin(full_url, iframe_url)
                print(f"   ✅ 找到iframe URL: {iframe_url}")
                return iframe_url
            
            return None
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            return None
    
    def extract_config_from_html(self, html: str) -> Optional[dict]:
        """从HTML中提取ConFig的url和uid"""
        print(f"\n[步骤2] 提取ConFig对象...")
        
        # 直接从HTML中搜索url和uid字段
        url_match = re.search(r'"url"\s*:\s*"([^"]+)"', html)
        uid_match = re.search(r'"uid"\s*:\s*"([^"]+)"', html)
        
        if url_match and uid_match:
            url_value = url_match.group(1).replace('\\/', '/')  # 处理转义的斜杠
            uid_value = uid_match.group(1)
            
            print(f"   ✅ 提取成功")
            print(f"   ✅ ConFig.url: {url_value[:100]}...")
            print(f"   ✅ ConFig.config.uid: {uid_value}")
            
            return {
                'url': url_value,
                'config': {
                    'uid': uid_value
                }
            }
        
        print(f"   ❌ 未能提取ConFig对象")
        return None
    
    def decrypt_url(self, encrypted_url: str, uid: str) -> Optional[str]:
        """
        解密ConFig.url - 改进版本
        尝试多种密钥和IV组合，匹配CryptoJS/NotGm的实际行为
        """
        print(f"\n[步骤3] 解密ConFig.url...")
        print(f"   encrypted_url长度: {len(encrypted_url)}")
        print(f"   uid: {uid}")
        
        # 清理转义字符（HTML中的 \/ 需要转换为 /）
        cleaned_url = encrypted_url.replace('\\/', '/')
        
        # Key生成方式
        key_str = '2890' + uid + 'tB959C'
        key_bytes = key_str.encode('utf-8')
        key_len = len(key_bytes)
        
        print(f"\n   Key字符串: {key_str}")
        print(f"   Key长度: {key_len} 字节")
        
        # 尝试不同的密钥生成方式
        key_methods = []
        
        # 方式1: 直接使用UTF-8字节（如果长度正好是16/24/32）
        if key_len in [16, 24, 32]:
            key_methods.append(("直接UTF-8", key_bytes))
        
        # 方式2: MD5哈希（16字节）
        key_methods.append(("MD5哈希", hashlib.md5(key_bytes).digest()))
        
        # 方式3: SHA256哈希（前16字节）
        key_methods.append(("SHA256前16字节", hashlib.sha256(key_bytes).digest()[:16]))
        
        # 方式4: SHA256哈希（前24字节）
        if key_len != 24:
            key_methods.append(("SHA256前24字节", hashlib.sha256(key_bytes).digest()[:24]))
        
        # 方式5: SHA256哈希（前32字节）
        if key_len != 32:
            key_methods.append(("SHA256前32字节", hashlib.sha256(key_bytes).digest()[:32]))
        
        # IV生成方式
        iv_str = '2F131BE91247866E'
        iv_methods = [
            ("UTF-8编码(16字节)", iv_str.encode('utf-8')),
            ("十六进制解析(8字节)", bytes.fromhex(iv_str)),
            ("十六进制解析+填充", bytes.fromhex(iv_str).ljust(16, b'\0')),
            ("重复填充", (bytes.fromhex(iv_str) * 2)[:16]),
        ]
        
        # Base64解码
        try:
            encrypted_data = base64.b64decode(cleaned_url)
            print(f"   ✅ Base64解码成功，数据长度: {len(encrypted_data)} 字节")
            
            if len(encrypted_data) % 16 != 0:
                print(f"   ⚠️ 警告: 加密数据长度不是16的倍数")
                return None
        except Exception as e:
            print(f"   ❌ Base64解码失败: {e}")
            return None
        
        # 尝试所有组合
        print(f"\n   尝试 {len(key_methods)} x {len(iv_methods)} = {len(key_methods) * len(iv_methods)} 种组合...")
        
        for key_name, key in key_methods:
            # 确保key长度正确
            if len(key) not in [16, 24, 32]:
                # 如果不是标准长度，尝试填充或截断
                if len(key) < 16:
                    key_padded = key.ljust(16, b'\0')
                    key_methods.append((f"{key_name}(填充到16)", key_padded))
                elif len(key) > 16 and len(key) < 24:
                    key_methods.append((f"{key_name}(截断到16)", key[:16]))
                    key_methods.append((f"{key_name}(填充到24)", key.ljust(24, b'\0')))
                continue
            
            for iv_name, iv in iv_methods:
                # 确保IV长度为16字节
                if len(iv) != 16:
                    if len(iv) < 16:
                        iv = iv.ljust(16, b'\0')
                    else:
                        iv = iv[:16]
                
                try:
                    # AES-CBC解密
                    cipher = AES.new(key, AES.MODE_CBC, iv)
                    decrypted = cipher.decrypt(encrypted_data)
                    
                    # 尝试移除PKCS7填充
                    try:
                        decrypted_unpadded = unpad(decrypted, AES.block_size)
                        result = decrypted_unpadded.decode('utf-8')
                        
                        if result.startswith('http'):
                            print(f"\n   ✅ 解密成功！")
                            print(f"   ✅ 密钥方式: {key_name}")
                            print(f"   ✅ IV方式: {iv_name}")
                            print(f"   ✅ 解密后的URL: {result}")
                            return result
                        else:
                            # 检查是否包含URL片段
                            if 'http' in result or '.m3u8' in result or 'm3u8' in result.lower():
                                print(f"\n   ⚠️ 解密成功但结果不是标准URL:")
                                print(f"   ⚠️ 密钥方式: {key_name}, IV方式: {iv_name}")
                                print(f"   ⚠️ 结果: {result[:200]}")
                    
                    except ValueError as e:
                        # 填充移除失败，尝试手动移除
                        try:
                            padding_len = decrypted[-1]
                            if 1 <= padding_len <= 16:
                                decrypted_manual = decrypted[:-padding_len]
                                result_manual = decrypted_manual.decode('utf-8')
                                
                                if result_manual.startswith('http'):
                                    print(f"\n   ✅ 手动移除填充后解密成功！")
                                    print(f"   ✅ 密钥方式: {key_name}")
                                    print(f"   ✅ IV方式: {iv_name}")
                                    print(f"   ✅ 解密后的URL: {result_manual}")
                                    return result_manual
                        except:
                            pass
                
                except Exception as e:
                    # 静默失败，继续尝试下一个组合
                    continue
        
        print(f"\n   ❌ 所有组合都失败了")
        print(f"\n   建议:")
        print(f"   1. 在浏览器中打开iframe页面")
        print(f"   2. 在Console中执行: PlayEr.ad.uic(ConFig.url)")
        print(f"   3. 查看实际的解密结果")
        
        return None
    
    def follow_redirect_to_final_m3u8(self, initial_url: str) -> Optional[str]:
        """跟踪重定向获取最终m3u8"""
        print(f"\n[步骤4] 跟踪重定向...")
        print(f"   初始URL: {initial_url}")
        
        try:
            response = self.session.get(initial_url, timeout=30, allow_redirects=False)
            
            if response.status_code in [301, 302, 303, 307, 308]:
                redirect_url = response.headers.get('Location')
                if redirect_url:
                    if not redirect_url.startswith('http'):
                        redirect_url = urljoin(initial_url, redirect_url)
                    
                    print(f"   🔄 重定向 ({response.status_code}) → {redirect_url}")
                    
                    # 如果重定向到最终m3u8 API
                    if 'api/m3u8' in redirect_url or 'm3u8.shipinbofang.net' in redirect_url:
                        return self.get_final_m3u8(redirect_url)
                    else:
                        return self.follow_redirect_to_final_m3u8(redirect_url)
            
            elif response.status_code == 200:
                content = response.text
                if content.strip().startswith('#EXTM3U'):
                    print(f"   ✅ 这是最终的m3u8播放列表")
                    print(f"   📊 包含 {content.count('#EXTINF')} 个视频片段")
                    return initial_url
            
            return None
            
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            return None
    
    def get_final_m3u8(self, api_url: str) -> Optional[str]:
        """获取最终m3u8播放列表"""
        print(f"\n[步骤5] 获取最终m3u8播放列表...")
        print(f"   API URL: {api_url}")
        
        try:
            response = self.session.get(api_url, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            # 检查响应头
            content_type = response.headers.get('Content-Type', '').lower()
            print(f"   Content-Type: {content_type}")
            
            content = response.text
            print(f"   响应长度: {len(content)} 字节")
            print(f"   响应预览: {content[:200]}")
            
            # 方法1: 检查是否是m3u8格式
            if content.strip().startswith('#EXTM3U'):
                print(f"   ✅ 成功获取最终m3u8播放列表")
                print(f"   📊 包含 {content.count('#EXTINF')} 个视频片段")
                
                # 保存m3u8内容
                with open('final_m3u8_v2.m3u8', 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"   💾 已保存到: final_m3u8_v2.m3u8")
                
                return response.url  # 返回最终URL（可能经过重定向）
            
            # 方法2: 检查响应中是否包含m3u8链接
            m3u8_patterns = [
                r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
                r'["\']([^"\']+\.m3u8[^"\']*)["\']',
            ]
            
            for pattern in m3u8_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    url = match if isinstance(match, str) else match[0] if match else None
                    if url and url.startswith('http') and '.m3u8' in url:
                        print(f"   ✅ 从响应中提取到m3u8链接: {url}")
                        # 递归调用获取实际的m3u8内容
                        return self.get_final_m3u8(url)
            
            # 方法3: 尝试解析JSON响应
            try:
                json_data = json.loads(content)
                print(f"   ⚠️ API返回JSON格式")
                
                # 递归查找m3u8链接
                def find_m3u8_in_json(obj, path=""):
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            result = find_m3u8_in_json(value, f"{path}.{key}")
                            if result:
                                return result
                    elif isinstance(obj, list):
                        for i, item in enumerate(obj):
                            result = find_m3u8_in_json(item, f"{path}[{i}]")
                            if result:
                                return result
                    elif isinstance(obj, str) and '.m3u8' in obj and obj.startswith('http'):
                        print(f"   ✅ 在JSON中找到m3u8链接: {obj}")
                        return obj
                    return None
                
                m3u8_url = find_m3u8_in_json(json_data)
                if m3u8_url:
                    return self.get_final_m3u8(m3u8_url)
                    
            except json.JSONDecodeError:
                pass
            
            # 方法4: 检查是否有Location头（重定向）
            if 'Location' in response.headers:
                redirect_url = response.headers['Location']
                if redirect_url and redirect_url != api_url:
                    print(f"   🔄 发现重定向: {redirect_url}")
                    return self.get_final_m3u8(redirect_url)
            
            # 方法5: 检查最终URL是否不同（可能发生了重定向）
            final_url = response.url
            if final_url != api_url:
                print(f"   ⚠️ URL已重定向到: {final_url}")
                # 如果最终URL包含m3u8，直接返回
                if '.m3u8' in final_url:
                    print(f"   ✅ 最终URL包含m3u8，返回此URL")
                    return final_url
            
            print(f"   ⚠️ API响应不是m3u8格式，也未找到m3u8链接")
            print(f"   💡 建议：直接使用API URL作为m3u8链接")
            print(f"   API URL: {final_url}")
            
            # 即使不是标准m3u8格式，如果URL包含m3u8，也返回它
            if '.m3u8' in final_url or 'm3u8' in final_url.lower():
                print(f"   ✅ URL包含m3u8关键字，返回此URL")
                return final_url
            
            return None
            
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def parse_video(self, parser_url: str, video_url: str) -> Optional[str]:
        """解析视频，获取最终m3u8"""
        print("=" * 60)
        print("最终版本 v2 - 改进解密逻辑")
        print("=" * 60)
        print(f"解析网站: {parser_url}")
        print(f"目标视频: {video_url}")
        
        # 步骤1: 获取iframe URL
        iframe_url = self.get_iframe_url(parser_url, video_url)
        if not iframe_url:
            print("\n❌ 未能获取iframe URL")
            return None
        
        # 步骤2: 访问iframe页面并提取ConFig
        try:
            response = self.session.get(iframe_url, timeout=30)
            response.raise_for_status()
            html = response.text
            
            # 保存HTML
            with open('iframe_page_v2.html', 'w', encoding='utf-8') as f:
                f.write(html)
            
            config = self.extract_config_from_html(html)
            if not config:
                print("\n❌ 未能提取ConFig对象")
                return None
            
            # 步骤3: 解密URL
            encrypted_url = config['url']
            uid = config['config']['uid']
            
            decrypted_url = self.decrypt_url(encrypted_url, uid)
            if not decrypted_url:
                print("\n❌ 解密失败")
                print("\n💡 建议使用浏览器自动化方案:")
                print("   python browser_decrypt_parser.py")
                return None
            
            # 步骤4: 跟踪重定向
            final_m3u8 = self.follow_redirect_to_final_m3u8(decrypted_url)
            
            if final_m3u8:
                print("\n" + "=" * 60)
                print("✅ 解析成功！")
                print("=" * 60)
                print(f"\n🎬 最终的m3u8链接:")
                print(f"   {final_m3u8}")
                print(f"\n📥 使用ffmpeg下载:")
                print(f'   ffmpeg -i "{final_m3u8}" -c copy output.mp4')
                
                # 保存完整结果
                result = {
                    'encrypted_url': encrypted_url,
                    'uid': uid,
                    'decrypted_url': decrypted_url,
                    'final_m3u8': final_m3u8,
                }
                with open('final_parse_result_v2.json', 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"\n✅ 完整结果已保存到: final_parse_result_v2.json")
                
                return final_m3u8
            else:
                print("\n❌ 未能获取最终的m3u8链接")
                return None
                
        except Exception as e:
            print(f"\n❌ 解析失败: {e}")
            import traceback
            traceback.print_exc()
            return None


def main():
    """主函数"""
    parser_url = "https://jx.789jiexi.com"
    video_url = "https://v.qq.com/x/cover/mzc0020079qbkmf/i4101t8jpi9.html"
    
    parser = FinalDirectParserV2()
    final_m3u8 = parser.parse_video(parser_url, video_url)
    
    if not final_m3u8:
        print("\n❌ 解析失败")


if __name__ == '__main__':
    main()

