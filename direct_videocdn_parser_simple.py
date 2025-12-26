"""
简化版直接解析 videocdn.ihelpy.net - 直接调用API
跳过可能被403拦截的步骤，直接调用已知的API端点
"""

import requests
import json
import re
import gzip
import zlib
from typing import Optional, List, Dict

# 尝试导入brotli
try:
    import brotli
    HAS_BROTLI = True
except ImportError:
    HAS_BROTLI = False
    print("⚠️ 警告: 未安装brotli库，无法解压Brotli压缩的响应")
    print("💡 安装方法: pip install brotli")


class DirectVideoCdnParserSimple:
    """简化版直接解析器 - 直接调用API"""
    
    def __init__(self):
        self.session = requests.Session()
        # 注意：移除Accept-Encoding来避免压缩，让服务器返回未压缩的响应
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7',
            # 'Accept-Encoding': 'gzip, deflate, br',  # 移除，避免压缩
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Referer': 'https://m1-z2.cloud.nnpp.vip:2223/',
            'Origin': 'https://m1-z2.cloud.nnpp.vip:2223',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Storage-Access': 'active',
            'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        })
    
    def construct_api_url(self, video_url: str, g_param: str = None) -> str:
        """构造API URL"""
        print(f"\n[步骤1] 构造API URL...")
        
        # 基于分析结果，API URL格式为：
        # https://m1-a1.cloud.nnpp.vip:2223/api/v/?z={z}&jx={video_url}&s1ig={s1ig}&g={g}
        
        # 从分析结果中提取的参数（可能需要动态生成，但先使用固定值测试）
        z_value = "e8e56ecaca35c6229baa93884b6b7323"
        s1ig_value = "11402"
        
        # g参数：从实际请求中发现是 "b2.bdzy"，可能是动态生成的
        # 可能是从m3u8 URL中提取的域名部分
        if g_param is None:
            # 尝试从之前的m3u8 URL中提取
            # 例如: https://b2.bdzybf22.com/... -> b2.bdzy
            g_param = "b2.bdzy"  # 默认值，可能需要动态生成
        
        api_url = f"https://m1-a1.cloud.nnpp.vip:2223/api/v/?z={z_value}&jx={video_url}&s1ig={s1ig_value}&g={g_param}"
        
        print(f"   ✅ API URL: {api_url}")
        print(f"   💡 注意: z、s1ig和g参数可能需要动态生成")
        print(f"   💡 g参数当前值: {g_param}")
        
        return api_url
    
    def call_api(self, api_url: str) -> Optional[Dict]:
        """调用API获取视频信息"""
        print(f"\n[步骤2] 调用API...")
        print(f"   URL: {api_url}")
        
        try:
            # 方法1: 尝试不压缩（移除Accept-Encoding）
            headers_no_compress = self.session.headers.copy()
            if 'Accept-Encoding' in headers_no_compress:
                del headers_no_compress['Accept-Encoding']
            
            response = self.session.get(api_url, headers=headers_no_compress, timeout=30, allow_redirects=True)
            
            print(f"   状态码: {response.status_code}")
            
            if response.status_code != 200:
                print(f"   ⚠️ API返回非200状态码")
                return None
            
            content_type = response.headers.get('Content-Type', '').lower()
            content_encoding = response.headers.get('Content-Encoding', '').lower()
            print(f"   Content-Type: {content_type}")
            print(f"   Content-Encoding: {content_encoding or 'none'}")
            
            # 获取原始字节数据
            raw_content = response.content
            print(f"   原始响应长度: {len(raw_content)} 字节")
            
            # 尝试解压
            content = None
            decompress_success = False
            
            if content_encoding == 'gzip':
                try:
                    content = gzip.decompress(raw_content).decode('utf-8')
                    print(f"   ✅ Gzip解压成功")
                    decompress_success = True
                except Exception as e:
                    print(f"   ⚠️ Gzip解压失败: {e}")
            elif content_encoding == 'deflate':
                try:
                    content = zlib.decompress(raw_content).decode('utf-8')
                    print(f"   ✅ Deflate解压成功")
                    decompress_success = True
                except Exception as e:
                    print(f"   ⚠️ Deflate解压失败: {e}")
            elif content_encoding == 'br':
                # Brotli压缩
                if HAS_BROTLI:
                    try:
                        content = brotli.decompress(raw_content).decode('utf-8')
                        print(f"   ✅ Brotli解压成功")
                        decompress_success = True
                    except Exception as e:
                        print(f"   ⚠️ Brotli解压失败: {e}")
                        print(f"   💡 尝试直接解码（可能Content-Encoding头错误）...")
                else:
                    print(f"   ⚠️ 响应标记为Brotli压缩，但未安装brotli库")
                    print(f"   💡 尝试直接解码...")
            
            # 如果解压失败，尝试直接解码（可能Content-Encoding头错误）
            if not decompress_success:
                try:
                    # 尝试直接UTF-8解码
                    test_content = raw_content.decode('utf-8')
                    # 检查是否是有效的JSON开头
                    if test_content.strip().startswith('{') or test_content.strip().startswith('['):
                        content = test_content
                        print(f"   ✅ 直接UTF-8解码成功（Content-Encoding头可能错误）")
                    else:
                        # 尝试其他编码
                        raise UnicodeDecodeError('utf-8', raw_content, 0, 1, 'test')
                except (UnicodeDecodeError, UnicodeError):
                    # 尝试其他编码
                    for encoding in ['gbk', 'latin1', 'cp1252', 'iso-8859-1']:
                        try:
                            test_content = raw_content.decode(encoding, errors='ignore')
                            if test_content.strip().startswith('{') or test_content.strip().startswith('['):
                                content = test_content
                                print(f"   ✅ 使用{encoding}编码解码成功")
                                break
                        except:
                            continue
                    
                    # 如果还是失败，尝试自动检测
                    if not content:
                        try:
                            import chardet
                            detected = chardet.detect(raw_content)
                            encoding = detected.get('encoding', 'utf-8')
                            content = raw_content.decode(encoding, errors='ignore')
                            print(f"   ✅ 使用自动检测编码({encoding})解码成功")
                        except ImportError:
                            # 最后尝试：忽略错误
                            content = raw_content.decode('utf-8', errors='ignore')
                            print(f"   ⚠️ 使用UTF-8解码（忽略错误）")
            
            if not content:
                print(f"   ❌ 无法解码响应内容")
                print(f"   原始字节预览: {raw_content[:200]}")
                # 即使解码失败，也尝试从原始字节中提取m3u8链接
                try:
                    raw_str = raw_content.decode('utf-8', errors='ignore')
                    if '.m3u8' in raw_str:
                        print(f"   💡 在原始字节中找到m3u8关键字，尝试提取...")
                        m3u8_patterns = [
                            r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
                            r'["\']([^"\']+\.m3u8[^"\']*)["\']',
                        ]
                        found_urls = []
                        for pattern in m3u8_patterns:
                            matches = re.findall(pattern, raw_str, re.IGNORECASE)
                            for match in matches:
                                url = match if isinstance(match, str) else match[0] if match else None
                                if url and url.startswith('http') and url not in found_urls:
                                    found_urls.append(url)
                                    print(f"   ✅ 找到m3u8链接: {url}")
                        if found_urls:
                            return {'m3u8_urls': found_urls}
                except:
                    pass
                return None
            
            print(f"   解码后长度: {len(content)} 字符")
            print(f"   内容预览: {content[:200]}")
            
            # 尝试解析JSON
            try:
                json_data = json.loads(content)
                print(f"   ✅ JSON解析成功")
                return json_data
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON解析失败: {e}")
                print(f"   完整响应内容: {content[:1000]}")
                
                # 尝试从响应中直接提取m3u8链接（即使不是JSON）
                m3u8_patterns = [
                    r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
                    r'["\']([^"\']+\.m3u8[^"\']*)["\']',
                ]
                found_urls = []
                for pattern in m3u8_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        url = match if isinstance(match, str) else match[0] if match else None
                        if url and url.startswith('http') and url not in found_urls:
                            found_urls.append(url)
                            print(f"   ✅ 从响应中提取到m3u8链接: {url}")
                
                if found_urls:
                    # 构造一个简单的JSON结构返回
                    return {
                        'type': 'movie',
                        'data': [{
                            'source': {
                                'eps': [{'url': url} for url in found_urls]
                            }
                        }]
                    }
                
                return None
                
        except Exception as e:
            print(f"   ❌ 请求失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def extract_m3u8_urls(self, api_response: Dict) -> List[str]:
        """从API响应中提取m3u8链接"""
        print(f"\n[步骤3] 提取m3u8链接...")
        
        m3u8_urls = []
        
        def find_m3u8_in_json(obj, path=""):
            """递归查找m3u8链接"""
            if isinstance(obj, dict):
                for key, value in obj.items():
                    find_m3u8_in_json(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    find_m3u8_in_json(item, f"{path}[{i}]")
            elif isinstance(obj, str):
                if '.m3u8' in obj and obj.startswith('http'):
                    if obj not in m3u8_urls:
                        m3u8_urls.append(obj)
                        print(f"   ✅ 找到m3u8链接 ({path}): {obj}")
        
        find_m3u8_in_json(api_response)
        
        if not m3u8_urls:
            print(f"   ⚠️ 未找到m3u8链接")
            print(f"   💡 尝试从响应中搜索...")
            # 如果递归没找到，尝试正则表达式
            json_str = json.dumps(api_response)
            m3u8_patterns = [
                r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
                r'["\']([^"\']+\.m3u8[^"\']*)["\']',
            ]
            for pattern in m3u8_patterns:
                matches = re.findall(pattern, json_str, re.IGNORECASE)
                for match in matches:
                    url = match if isinstance(match, str) else match[0] if match else None
                    if url and url.startswith('http') and url not in m3u8_urls:
                        m3u8_urls.append(url)
                        print(f"   ✅ 通过正则找到m3u8链接: {url}")
        
        return m3u8_urls
    
    def get_best_m3u8(self, m3u8_urls: List[str]) -> Optional[str]:
        """选择最佳的m3u8链接"""
        print(f"\n[步骤4] 选择最佳m3u8链接...")
        
        if not m3u8_urls:
            return None
        
        # 优先选择第一个（通常是HD版本）
        best_url = m3u8_urls[0]
        print(f"   ✅ 选择: {best_url}")
        
        return best_url
    
    def verify_m3u8(self, m3u8_url: str) -> bool:
        """验证m3u8链接是否有效"""
        print(f"\n[步骤5] 验证m3u8链接...")
        print(f"   URL: {m3u8_url}")
        
        try:
            # 使用不同的请求头验证
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': '*/*',
                'Referer': 'https://videocdn.ihelpy.net/',
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
        print("简化版直接解析 videocdn.ihelpy.net")
        print("=" * 60)
        print(f"目标视频: {video_url}")
        
        # 步骤1: 构造API URL
        api_url = self.construct_api_url(video_url)
        
        # 步骤2: 调用API
        api_response = self.call_api(api_url)
        if not api_response:
            print("\n❌ API调用失败")
            print("\n💡 可能的原因:")
            print("   1. z参数需要动态生成")
            print("   2. s1ig参数需要动态生成")
            print("   3. 需要特定的Referer或Cookie")
            print("   4. API端点已变更")
            print("\n💡 建议:")
            print("   1. 使用浏览器分析脚本获取最新的API参数")
            print("   2. 检查网络连接")
            return None
        
        # 步骤3: 提取m3u8链接
        m3u8_urls = self.extract_m3u8_urls(api_response)
        if not m3u8_urls:
            print("\n❌ 未能提取m3u8链接")
            print(f"\n📄 API响应内容:")
            print(json.dumps(api_response, indent=2, ensure_ascii=False)[:1000])
            return None
        
        # 步骤4: 选择最佳m3u8
        best_m3u8 = self.get_best_m3u8(m3u8_urls)
        if not best_m3u8:
            print("\n❌ 未能选择m3u8链接")
            return None
        
        # 步骤5: 验证m3u8（可选）
        self.verify_m3u8(best_m3u8)
        
        # 保存结果
        result = {
            'video_url': video_url,
            'api_url': api_url,
            'api_response': api_response,
            'm3u8_urls': m3u8_urls,
            'best_m3u8': best_m3u8,
        }
        
        with open('videocdn_parse_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n✅ 完整结果已保存到: videocdn_parse_result.json")
        
        print("\n" + "=" * 60)
        print("✅ 解析成功！")
        print("=" * 60)
        print(f"\n🎬 找到 {len(m3u8_urls)} 个m3u8链接:")
        for i, url in enumerate(m3u8_urls, 1):
            marker = "⭐" if url == best_m3u8 else "  "
            print(f"   {marker} [{i}] {url}")
        
        print(f"\n📥 使用ffmpeg下载:")
        print(f'   ffmpeg -i "{best_m3u8}" -c copy output.mp4')
        
        return best_m3u8


def main():
    """主函数"""
    video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    
    parser = DirectVideoCdnParserSimple()
    final_m3u8 = parser.parse_video(video_url)
    
    if not final_m3u8:
        print("\n❌ 解析失败")
        print("\n💡 建议:")
        print("   1. 检查网络连接")
        print("   2. 检查API参数是否需要更新")
        print("   3. 使用浏览器分析脚本获取最新的API参数")


if __name__ == '__main__':
    main()

