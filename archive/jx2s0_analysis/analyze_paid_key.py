"""
分析付费key的加密算法
URL: https://json.2s0.cn:5678/player/analysis.php/?uid=4059917&key=cgklotuyDGHILOTW38&url=https://www.iqiyi.com/v_1c168e2yzbk.html
"""

import requests
import re
import json
import base64
from urllib.parse import urlparse, parse_qs, quote
from typing import Optional, Dict
import sys
import io

# 修复Windows控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class PaidKeyAnalyzer:
    """付费key分析器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://json.2s0.cn/',
        })
    
    def fetch_analysis_page(self, uid: str, key: str, video_url: str) -> Optional[Dict]:
        """获取analysis.php页面"""
        print(f"\n{'='*80}")
        print(f"步骤1: 访问analysis.php页面")
        print(f"{'='*80}")
        
        url = f"https://json.2s0.cn:5678/player/analysis.php/?uid={uid}&key={key}&url={quote(video_url)}"
        print(f"URL: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                html = response.text
                
                # 保存HTML到文件
                import os
                output_dir = os.path.dirname(os.path.abspath(__file__))
                html_file = os.path.join(output_dir, 'paid_key_analysis.html')
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"✅ HTML已保存到: {html_file}")
                
                return {'html': html, 'status': response.status_code}
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"响应内容: {response.text[:500]}")
                return None
                
        except Exception as e:
            print(f"❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def extract_config(self, html: str) -> Optional[Dict]:
        """提取config对象"""
        print(f"\n{'='*80}")
        print(f"步骤2: 提取config对象")
        print(f"{'='*80}")
        
        # 查找config对象
        config_patterns = [
            r'var\s+config\s*=\s*({[^}]+})',
            r'config\s*=\s*({[^}]+})',
            r'var\s+config\s*=\s*({.*?});',
        ]
        
        config_data = {}
        
        for pattern in config_patterns:
            matches = re.findall(pattern, html, re.DOTALL)
            if matches:
                print(f"✅ 找到config对象（模式: {pattern[:30]}...）")
                for i, match in enumerate(matches, 1):
                    print(f"\n   Config {i}:")
                    print(f"   {match[:200]}...")
                    
                    # 尝试提取关键字段
                    url_match = re.search(r'"url"\s*:\s*"([^"]+)"', match)
                    id_match = re.search(r'"id"\s*:\s*"([^"]+)"', match)
                    
                    if url_match:
                        config_url = url_match.group(1)
                        print(f"   config.url: {config_url[:100]}...")
                        config_data['url'] = config_url
                    
                    if id_match:
                        config_id = id_match.group(1)
                        print(f"   config.id: {config_id}")
                        config_data['id'] = config_id
                
                break
        
        if not config_data:
            print("❌ 未找到config对象")
            # 尝试查找其他可能的配置
            print("\n🔍 尝试查找其他配置...")
            
            # 查找所有var声明
            var_pattern = r'var\s+(\w+)\s*=\s*([^;]+);'
            vars_found = re.findall(var_pattern, html)
            if vars_found:
                print(f"   找到 {len(vars_found)} 个变量声明")
                for var_name, var_value in vars_found[:10]:
                    if 'url' in var_name.lower() or 'id' in var_name.lower():
                        print(f"   {var_name} = {var_value[:100]}")
        
        return config_data if config_data else None
    
    def extract_all_javascript(self, html: str) -> Dict:
        """提取所有JavaScript代码"""
        print(f"\n{'='*80}")
        print(f"步骤3: 提取JavaScript代码")
        print(f"{'='*80}")
        
        js_data = {}
        
        # 查找script标签
        script_pattern = r'<script[^>]*>(.*?)</script>'
        scripts = re.findall(script_pattern, html, re.DOTALL)
        
        print(f"✅ 找到 {len(scripts)} 个script标签")
        
        for i, script in enumerate(scripts, 1):
            # 跳过空脚本和外部脚本
            if not script.strip() or script.strip().startswith('http'):
                continue
            
            # 保存每个脚本
            import os
            output_dir = os.path.dirname(os.path.abspath(__file__))
            filename = os.path.join(output_dir, f'paid_key_script_{i}.js')
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(script)
            
            print(f"\n   Script {i}:")
            print(f"   长度: {len(script)} 字符")
            print(f"   已保存到: {filename}")
            
            # 查找关键函数
            if 'YKQ' in script:
                print(f"   ✅ 包含 YKQ")
            if 'config' in script:
                print(f"   ✅ 包含 config")
            if 'rc4' in script:
                print(f"   ✅ 包含 rc4")
            if 'video' in script:
                print(f"   ✅ 包含 video")
            
            js_data[f'script_{i}'] = script
        
        return js_data
    
    def compare_with_free_version(self, paid_config: Dict, uid: str, key: str) -> None:
        """对比付费版本和免费版本"""
        print(f"\n{'='*80}")
        print(f"步骤4: 对比付费版本和免费版本")
        print(f"{'='*80}")
        
        print(f"\n📊 付费版本信息:")
        print(f"   uid: {uid}")
        print(f"   key: {key}")
        print(f"   config.url: {paid_config.get('url', 'N/A')[:100]}...")
        print(f"   config.id: {paid_config.get('id', 'N/A')}")
        
        print(f"\n📊 免费版本信息（从之前的分析）:")
        print(f"   config.url: O/zpjS4gC4ztyL9ve/+wx/3Lmpl7X/QAEOuqmTie93atrwDjwxRosEpoaXZw0TRD/...")
        print(f"   config.id: b664f44e3be2ad57fdb6")
        
        print(f"\n🔍 差异分析:")
        if paid_config.get('url') and paid_config.get('url') != 'O/zpjS4gC4ztyL9ve/+wx/3Lmpl7X/QAEOuqmTie93atrwDjwxRosEpoaXZw0TRD/...':
            print(f"   ✅ config.url 不同（可能基于uid/key生成）")
        if paid_config.get('id') and paid_config.get('id') != 'b664f44e3be2ad57fdb6':
            print(f"   ✅ config.id 不同（可能基于uid/key生成）")
    
    def analyze_encryption_algorithm(self, paid_config: Dict, uid: str, key: str, video_url: str) -> None:
        """分析加密算法"""
        print(f"\n{'='*80}")
        print(f"步骤5: 分析加密算法")
        print(f"{'='*80}")
        
        config_url = paid_config.get('url')
        config_id = paid_config.get('id')
        
        if not config_url:
            print("❌ 无法分析：缺少config.url")
            return
        
        print(f"\n🔐 加密算法分析:")
        print(f"   输入参数:")
        print(f"     uid: {uid}")
        print(f"     key: {key}")
        print(f"     video_url: {video_url}")
        print(f"   输出:")
        print(f"     config.url: {config_url[:100]}...")
        print(f"     config.id: {config_id}")
        
        # 分析config.url的格式
        print(f"\n📋 config.url格式分析:")
        print(f"   长度: {len(config_url)} 字符")
        print(f"   是否Base64: {self.is_base64(config_url)}")
        
        # 尝试Base64解码
        try:
            decoded = base64.b64decode(config_url)
            print(f"   Base64解码后长度: {len(decoded)} 字节")
            print(f"   前20字节（十六进制）: {decoded[:20].hex()}")
        except:
            print(f"   ❌ Base64解码失败")
        
        # 分析可能的加密方式
        print(f"\n🔍 可能的加密方式:")
        print(f"   1. 使用uid和key生成config.url")
        print(f"   2. 使用video_url生成config.url")
        print(f"   3. 使用uid+key+video_url生成config.url")
        print(f"   4. 服务器端生成（需要API调用）")
        
        # 尝试不同的组合
        print(f"\n🧪 测试不同的组合:")
        test_strings = [
            f"{uid}{key}{video_url}",
            f"{uid}{key}",
            f"{key}{video_url}",
            f"{uid}{video_url}",
        ]
        
        for test_str in test_strings:
            import hashlib
            md5_hash = hashlib.md5(test_str.encode()).hexdigest()
            sha1_hash = hashlib.sha1(test_str.encode()).hexdigest()
            print(f"   MD5({test_str[:50]}...): {md5_hash}")
            print(f"   SHA1({test_str[:50]}...): {sha1_hash[:40]}")
    
    def is_base64(self, s: str) -> bool:
        """检查字符串是否是Base64编码"""
        try:
            if isinstance(s, str):
                s = s.encode('ascii')
            return base64.b64decode(s, validate=True) is not None
        except:
            return False
    
    def analyze_full_flow(self, uid: str, key: str, video_url: str) -> None:
        """完整分析流程"""
        print(f"\n{'='*80}")
        print(f"付费Key加密算法分析")
        print(f"{'='*80}")
        print(f"uid: {uid}")
        print(f"key: {key}")
        print(f"video_url: {video_url}")
        
        # 步骤1: 获取页面
        page_result = self.fetch_analysis_page(uid, key, video_url)
        if not page_result:
            print("\n❌ 无法获取页面")
            return
        
        html = page_result['html']
        
        # 步骤2: 提取config
        config_data = self.extract_config(html)
        
        # 步骤3: 提取JavaScript
        js_data = self.extract_all_javascript(html)
        
        # 步骤4: 对比版本
        if config_data:
            self.compare_with_free_version(config_data, uid, key)
        
        # 步骤5: 分析加密算法
        if config_data:
            self.analyze_encryption_algorithm(config_data, uid, key, video_url)
        
        print(f"\n{'='*80}")
        print(f"分析完成！")
        print(f"{'='*80}")
        print(f"\n📁 生成的文件:")
        print(f"   - paid_key_analysis.html")
        for i in range(1, len(js_data) + 1):
            print(f"   - paid_key_script_{i}.js")

def main():
    """主函数"""
    analyzer = PaidKeyAnalyzer()
    
    # 付费key信息
    uid = "4059917"
    key = "cgklotuyDGHILOTW38"
    video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    
    analyzer.analyze_full_flow(uid, key, video_url)

if __name__ == "__main__":
    main()

