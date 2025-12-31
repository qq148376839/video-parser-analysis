"""
测试直接通过接口请求获取播放地址
目标：不通过浏览器模拟，直接调用 API 获取 m3u8 URL
"""

import requests
import re
import json
import sys
import io
from urllib.parse import urlparse, parse_qs, urlencode
from typing import Optional, Dict

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class DirectAPITester:
    """直接 API 请求测试器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://jx.2s0.cn/',
        })
    
    def test_main_page(self, video_url: str) -> Optional[Dict]:
        """测试主页面请求"""
        print(f"\n{'='*80}")
        print(f"测试1: 请求主页面")
        print(f"{'='*80}")
        
        main_url = f"https://jx.2s0.cn/player/?url={video_url}"
        print(f"URL: {main_url}")
        
        try:
            response = self.session.get(main_url, timeout=30)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                html = response.text
                
                # 查找 iframe
                iframe_pattern = r'<iframe[^>]+src=["\']([^"\']+)["\']'
                iframe_matches = re.findall(iframe_pattern, html)
                
                if iframe_matches:
                    print(f"✅ 找到 {len(iframe_matches)} 个 iframe:")
                    for i, iframe_url in enumerate(iframe_matches, 1):
                        print(f"   [{i}] {iframe_url}")
                    return {'iframes': iframe_matches, 'html': html}
                else:
                    print("❌ 未找到 iframe")
                    return None
            else:
                print(f"❌ 请求失败: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def test_iframe_page(self, iframe_url: str) -> Optional[Dict]:
        """测试 iframe 页面请求"""
        print(f"\n{'='*80}")
        print(f"测试2: 请求 iframe 页面")
        print(f"{'='*80}")
        
        print(f"URL: {iframe_url}")
        
        try:
            response = self.session.get(iframe_url, timeout=30)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                html = response.text
                
                # 查找 config 对象
                config_pattern = r'var\s+config\s*=\s*({[^}]+})'
                config_match = re.search(config_pattern, html, re.DOTALL)
                
                if config_match:
                    print(f"✅ 找到 config 对象")
                    config_str = config_match.group(1)
                    print(f"   Config: {config_str[:200]}...")
                    
                    # 尝试提取 config.url 和 config.id
                    url_match = re.search(r'"url"\s*:\s*"([^"]+)"', config_str)
                    id_match = re.search(r'"id"\s*:\s*"([^"]+)"', config_str)
                    
                    if url_match and id_match:
                        config_url = url_match.group(1)
                        config_id = id_match.group(1)
                        print(f"   config.url: {config_url[:50]}...")
                        print(f"   config.id: {config_id}")
                        return {
                            'config': {
                                'url': config_url,
                                'id': config_id
                            },
                            'html': html
                        }
                
                return {'html': html}
            else:
                print(f"❌ 请求失败: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def test_admin_api(self, config_data: Optional[Dict] = None) -> Optional[Dict]:
        """测试 /admin/api.php 接口"""
        print(f"\n{'='*80}")
        print(f"测试3: 请求 /admin/api.php")
        print(f"{'='*80}")
        
        api_url = "https://jx.2s0.cn/admin/api.php"
        
        # 尝试不同的参数组合
        params_list = [
            {},  # 无参数
            {"id": config_data.get('id') if config_data else None},
            {"url": config_data.get('url') if config_data else None},
            {"id": config_data.get('id') if config_data else None, "url": config_data.get('url') if config_data else None},
        ]
        
        for params in params_list:
            # 过滤 None 值
            params = {k: v for k, v in params.items() if v is not None}
            
            if not params:
                print(f"测试: GET {api_url} (无参数)")
            else:
                print(f"测试: GET {api_url}?{urlencode(params)}")
            
            try:
                response = self.session.get(api_url, params=params, timeout=30)
                print(f"   状态码: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"   ✅ JSON 响应:")
                        print(f"   {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
                        
                        # 检查是否包含 m3u8 或 token
                        response_text = json.dumps(data)
                        if "m3u8" in response_text.lower() or "token" in response_text.lower():
                            print(f"   🎯 找到 m3u8/token 相关信息！")
                            return data
                    except:
                        text = response.text[:500]
                        print(f"   📄 文本响应: {text}")
                        if "m3u8" in text.lower() or "token" in text.lower():
                            print(f"   🎯 找到 m3u8/token 相关信息！")
                            return {'text': text}
            except Exception as e:
                print(f"   ❌ 错误: {e}")
        
        return None
    
    def test_possible_m3u8_apis(self, config_data: Optional[Dict] = None, video_url: str = None) -> Optional[str]:
        """测试可能的 m3u8 API"""
        print(f"\n{'='*80}")
        print(f"测试4: 测试可能的 m3u8 API")
        print(f"{'='*80}")
        
        # 可能的 API 端点
        endpoints = [
            "https://jx.2s0.cn/api.php",
            "https://jx.2s0.cn/api/getm3u8.php",
            "https://jx.2s0.cn/api/gettoken.php",
            "https://jx.2s0.cn/jiexi.php",
            "https://jx.2s0.cn/parse.php",
            "https://jx.2s0.cn/getm3u8.php",
            "https://jx.2s0.cn/gettoken.php",
        ]
        
        # 可能的参数组合
        params_list = []
        if config_data:
            params_list.extend([
                {"url": config_data.get('url'), "id": config_data.get('id')},
                {"encrypted_url": config_data.get('url'), "uid": config_data.get('id')},
                {"data": config_data.get('url'), "key": config_data.get('id')},
            ])
        if video_url:
            params_list.extend([
                {"url": video_url},
                {"video_url": video_url},
                {"source_url": video_url},
            ])
            if config_data:
                params_list.extend([
                    {"url": video_url, "id": config_data.get('id')},
                    {"url": video_url, "config_url": config_data.get('url'), "id": config_data.get('id')},
                ])
        
        for endpoint in endpoints:
            for params in params_list:
                # 过滤 None 值
                params = {k: v for k, v in params.items() if v is not None}
                
                if not params:
                    continue
                
                print(f"\n测试: GET {endpoint}?{urlencode(params)}")
                
                try:
                    response = self.session.get(endpoint, params=params, timeout=10)
                    print(f"   状态码: {response.status_code}")
                    
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            response_text = json.dumps(data)
                        except:
                            response_text = response.text
                        
                        if "m3u8" in response_text.lower() or "token" in response_text.lower() or "cachem3u8" in response_text.lower():
                            print(f"   🎯 找到 m3u8/token 相关信息！")
                            print(f"   响应: {response_text[:500]}")
                            return response_text
                except Exception as e:
                    pass
        
        return None
    
    def test_full_flow(self, video_url: str) -> Optional[str]:
        """测试完整流程"""
        print(f"\n{'='*80}")
        print(f"完整流程测试")
        print(f"{'='*80}")
        print(f"视频URL: {video_url}")
        
        # 步骤1: 请求主页面
        main_result = self.test_main_page(video_url)
        if not main_result or not main_result.get('iframes'):
            print("\n❌ 无法获取 iframe URL")
            return None
        
        # 步骤2: 请求 iframe 页面
        iframe_url = main_result['iframes'][0]
        iframe_result = self.test_iframe_page(iframe_url)
        
        config_data = iframe_result.get('config') if iframe_result else None
        
        # 步骤3: 测试 /admin/api.php
        api_result = self.test_admin_api(config_data)
        
        # 步骤4: 测试可能的 m3u8 API
        m3u8_result = self.test_possible_m3u8_apis(config_data, video_url)
        
        if m3u8_result:
            return m3u8_result
        
        print("\n" + "="*80)
        print("❌ 未找到直接获取 m3u8 的 API")
        print("="*80)
        print("\n结论：")
        print("1. 可能需要 JavaScript 执行才能生成 token")
        print("2. token 可能是在客户端动态生成的")
        print("3. 建议使用浏览器自动化方式获取")
        
        return None

def main():
    """主函数"""
    tester = DirectAPITester()
    
    # 测试视频 URL
    video_url = "https://v.youku.com/v_show/id_XMTA0MTc5NzI4.html"
    
    result = tester.test_full_flow(video_url)
    
    if result:
        print(f"\n✅ 成功获取结果:")
        print(result)
    else:
        print(f"\n❌ 无法直接通过 API 获取播放地址")
        print(f"   建议使用浏览器自动化方式")

if __name__ == "__main__":
    main()

