#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整的付费Key分析脚本
分析付费key的加密算法，对比免费版本和付费版本的差异
"""

import requests
import re
import base64
import hashlib
import json
from urllib.parse import quote
import os

class PaidKeyAnalyzer:
    """付费Key分析器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        })
    
    def fetch_and_analyze(self, uid, key, video_url):
        """获取并分析付费key"""
        print("="*80)
        print("付费Key加密算法分析")
        print("="*80)
        print(f"uid: {uid}")
        print(f"key: {key}")
        print(f"video_url: {video_url}")
        print()
        
        # 构建URL
        url = f"https://json.2s0.cn:5678/player/analysis.php/?uid={uid}&key={key}&url={quote(video_url)}"
        print(f"访问URL: {url}")
        print()
        
        try:
            response = self.session.get(url, timeout=30)
            print(f"状态码: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ 请求失败: {response.status_code}")
                return None
            
            html = response.text
            
            # 保存HTML
            output_dir = os.path.dirname(os.path.abspath(__file__))
            html_file = os.path.join(output_dir, 'paid_key_analysis.html')
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"✅ HTML已保存到: {html_file}")
            print()
            
            # 提取config
            config_data = self.extract_config(html)
            
            if config_data:
                # 对比免费版本
                self.compare_with_free(config_data)
                
                # 分析加密算法
                self.analyze_encryption(uid, key, video_url, config_data)
            
            return config_data
            
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def extract_config(self, html):
        """提取config对象"""
        print("步骤1: 提取config对象")
        print("-"*80)
        
        # 查找config对象
        patterns = [
            r'var\s+config\s*=\s*({[^}]+})',
            r'config\s*=\s*({[^}]+})',
            r'var\s+config\s*=\s*({.*?});',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                config_str = match.group(1)
                print(f"✅ 找到config对象")
                print(f"   内容预览: {config_str[:200]}...")
                
                # 提取关键字段
                url_match = re.search(r'"url"\s*:\s*"([^"]+)"', config_str)
                id_match = re.search(r'"id"\s*:\s*"([^"]+)"', config_str)
                
                config_data = {}
                if url_match:
                    config_data['url'] = url_match.group(1)
                    print(f"   config.url: {config_data['url'][:100]}...")
                    print(f"   config.url长度: {len(config_data['url'])}")
                
                if id_match:
                    config_data['id'] = id_match.group(1)
                    print(f"   config.id: {config_data['id']}")
                
                print()
                return config_data
        
        print("❌ 未找到config对象")
        print("   显示HTML前500字符:")
        print(html[:500])
        print()
        return None
    
    def compare_with_free(self, paid_config):
        """对比免费版本"""
        print("步骤2: 对比免费版本和付费版本")
        print("-"*80)
        
        # 免费版本（从之前的分析）
        free_config = {
            'url': 'O/zpjS4gC4ztyL9ve/+wx/3Lmpl7X/QAEOuqmTie93atrwDjwxRosEpoaXZw0TRD/AGtcvvIxMxgcxsQWcHumCqsvuIlf3lGXkqJgVWIsvPYgh8+Nsu4r36vZQ6fs/7edsA0WFSEDE16mwOTvC8ByCxFQJXZcJaeTf7igGItTKkNAp5yEF325qV9KNQuP/wR3si83JgFlTJ5d+hDqD6PjLpnQa9dj5jhhU3CRZaUxnIK9d1Gy+UxI0HhDsyLRnS+c6C7NFAu8aOZ48zeKlJH14o6IB9Io39UOiPh13dLuq9QmSqwzty7th+dt0Pz3O5w3nOvyQn+yieU0tPg+eNwujrN79nX+8bTPr5FdGfgqCyn0wMhRA==',
            'id': 'b664f44e3be2ad57fdb6'
        }
        
        print("付费版本:")
        print(f"  config.url: {paid_config.get('url', 'N/A')[:100]}...")
        print(f"  config.id: {paid_config.get('id', 'N/A')}")
        print()
        
        print("免费版本:")
        print(f"  config.url: {free_config['url'][:100]}...")
        print(f"  config.id: {free_config['id']}")
        print()
        
        print("对比结果:")
        if paid_config.get('url') and paid_config['url'] != free_config['url']:
            print("  ✅ config.url 不同（可能基于uid/key生成）")
        else:
            print("  ⚠️ config.url 相同（可能不基于uid/key生成）")
        
        if paid_config.get('id') and paid_config['id'] != free_config['id']:
            print("  ✅ config.id 不同（可能基于uid/key生成）")
        else:
            print("  ⚠️ config.id 相同（可能不基于uid/key生成）")
        print()
    
    def analyze_encryption(self, uid, key, video_url, config_data):
        """分析加密算法"""
        print("步骤3: 分析加密算法")
        print("-"*80)
        
        config_url = config_data.get('url')
        config_id = config_data.get('id')
        
        if not config_url:
            print("❌ 无法分析：缺少config.url")
            return
        
        print(f"输入参数:")
        print(f"  uid: {uid}")
        print(f"  key: {key}")
        print(f"  video_url: {video_url}")
        print()
        
        print(f"输出:")
        print(f"  config.url: {config_url[:100]}...")
        print(f"  config.id: {config_id}")
        print()
        
        # 分析config.url格式
        print("config.url格式分析:")
        print(f"  长度: {len(config_url)} 字符")
        
        # 检查是否是Base64
        try:
            decoded = base64.b64decode(config_url)
            print(f"  ✅ 是Base64编码")
            print(f"  解码后长度: {len(decoded)} 字节")
            print(f"  前20字节（十六进制）: {decoded[:20].hex()}")
        except:
            print(f"  ❌ 不是Base64编码")
        
        print()
        
        # 测试不同的加密算法
        print("测试不同的加密算法:")
        print("-"*80)
        
        test_strings = [
            f"{uid}{key}{video_url}",
            f"{uid}{key}",
            f"{key}{video_url}",
            f"{uid}{video_url}",
            f"{key}",
            f"{uid}",
        ]
        
        for test_str in test_strings:
            print(f"\n测试字符串: {test_str[:50]}...")
            
            # MD5
            md5_hash = hashlib.md5(test_str.encode()).hexdigest()
            print(f"  MD5: {md5_hash}")
            
            # SHA1
            sha1_hash = hashlib.sha1(test_str.encode()).hexdigest()
            print(f"  SHA1: {sha1_hash[:40]}...")
            
            # Base64
            b64_encoded = base64.b64encode(test_str.encode()).decode()
            print(f"  Base64: {b64_encoded[:50]}...")
            
            # 检查是否匹配config.url的开头
            if config_url.startswith(b64_encoded[:20]):
                print(f"  🎯 可能匹配！Base64编码的开头与config.url匹配")
        
        print()
        print("="*80)
        print("分析完成！")
        print("="*80)
        print()
        print("📝 下一步:")
        print("1. 查看保存的HTML文件: paid_key_analysis.html")
        print("2. 分析config.url的生成方式")
        print("3. 查找PHP或JavaScript中的加密代码")
        print("4. 尝试逆向加密算法")

def main():
    """主函数"""
    analyzer = PaidKeyAnalyzer()
    
    # 付费key信息
    uid = "4059917"
    key = "cgklotuyDGHILOTW38"
    video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    
    analyzer.fetch_and_analyze(uid, key, video_url)

if __name__ == "__main__":
    main()

