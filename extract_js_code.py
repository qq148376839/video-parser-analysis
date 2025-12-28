"""
提取解析网站的JavaScript代码
用于分析z参数生成逻辑，并准备部署到Cloudflare Workers
"""

import requests
import re
import json
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs


class JavaScriptExtractor:
    """JavaScript代码提取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
    
    def extract_all_scripts(self, url: str) -> Dict:
        """提取页面中的所有JavaScript代码"""
        print(f"🔍 访问页面: {url}")
        
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code != 200:
                print(f"❌ 访问失败: {response.status_code}")
                return {}
            
            html = response.text
            print(f"✅ 页面加载成功，长度: {len(html)} 字符")
            
            # 提取所有script标签
            scripts = self._extract_script_tags(html)
            
            # 提取外部JS文件URL
            external_scripts = self._extract_external_scripts(html)
            
            # 下载外部JS文件
            external_js_content = {}
            for script_url in external_scripts:
                print(f"\n📥 下载外部脚本: {script_url}")
                content = self._download_script(script_url)
                if content:
                    external_js_content[script_url] = content
            
            return {
                'url': url,
                'inline_scripts': scripts,
                'external_scripts': external_scripts,
                'external_js_content': external_js_content,
                'html_length': len(html)
            }
        
        except Exception as e:
            print(f"❌ 提取失败: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _extract_script_tags(self, html: str) -> List[Dict]:
        """提取内联script标签"""
        scripts = []
        
        # 匹配script标签（包括内联和外部）
        pattern = r'<script[^>]*>(.*?)</script>'
        matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
        
        for i, content in enumerate(matches):
            if content.strip():  # 只保存有内容的script
                scripts.append({
                    'index': i,
                    'type': 'inline',
                    'content': content.strip(),
                    'length': len(content)
                })
        
        print(f"📋 找到 {len(scripts)} 个内联script标签")
        return scripts
    
    def _extract_external_scripts(self, html: str) -> List[str]:
        """提取外部script标签的URL"""
        external_scripts = []
        
        # 匹配外部script标签
        pattern = r'<script[^>]+src=["\']([^"\']+)["\']'
        matches = re.findall(pattern, html, re.IGNORECASE)
        
        for script_url in matches:
            # 处理相对URL
            if script_url.startswith('//'):
                script_url = 'https:' + script_url
            elif script_url.startswith('/'):
                script_url = 'https://videocdn.ihelpy.net' + script_url
            
            if script_url not in external_scripts:
                external_scripts.append(script_url)
        
        print(f"📋 找到 {len(external_scripts)} 个外部script标签")
        return external_scripts
    
    def _download_script(self, url: str) -> Optional[str]:
        """下载外部JavaScript文件"""
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                content = response.text
                print(f"   ✅ 下载成功，长度: {len(content)} 字符")
                return content
            else:
                print(f"   ⚠️ 下载失败: {response.status_code}")
        except Exception as e:
            print(f"   ⚠️ 下载失败: {e}")
        return None
    
    def find_z_param_generation(self, scripts_data: Dict) -> List[Dict]:
        """查找z参数生成相关的代码"""
        findings = []
        
        # 搜索关键词
        keywords = [
            'z=', 'z:', 'z =', 'z:', 
            'api/v', 'm1-a1.cloud',
            'b413af76b43b1a0abc231718862417e2',  # 已知的z参数值
            'md5', 'hash', 'crypto', 'encrypt',
            'fetch', 'XMLHttpRequest', 'ajax'
        ]
        
        # 搜索内联脚本
        for script in scripts_data.get('inline_scripts', []):
            content = script.get('content', '')
            for keyword in keywords:
                if keyword.lower() in content.lower():
                    # 提取相关代码行
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if keyword.lower() in line.lower():
                            findings.append({
                                'type': 'inline',
                                'script_index': script.get('index'),
                                'line_number': i + 1,
                                'keyword': keyword,
                                'code': line.strip()[:200],
                                'context': self._get_context(lines, i, 3)
                            })
        
        # 搜索外部脚本
        for url, content in scripts_data.get('external_js_content', {}).items():
            for keyword in keywords:
                if keyword.lower() in content.lower():
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if keyword.lower() in line.lower():
                            findings.append({
                                'type': 'external',
                                'url': url,
                                'line_number': i + 1,
                                'keyword': keyword,
                                'code': line.strip()[:200],
                                'context': self._get_context(lines, i, 3)
                            })
        
        return findings
    
    def _get_context(self, lines: List[str], line_index: int, context_lines: int = 3) -> str:
        """获取代码上下文"""
        start = max(0, line_index - context_lines)
        end = min(len(lines), line_index + context_lines + 1)
        context = '\n'.join(lines[start:end])
        return context
    
    def save_extracted_code(self, scripts_data: Dict, output_file: str = 'extracted_js_code.json'):
        """保存提取的代码"""
        # 只保存关键信息，避免文件过大
        output = {
            'url': scripts_data.get('url'),
            'inline_scripts_count': len(scripts_data.get('inline_scripts', [])),
            'external_scripts': scripts_data.get('external_scripts', []),
            'inline_scripts': [
                {
                    'index': s.get('index'),
                    'length': s.get('length'),
                    'content_preview': s.get('content', '')[:500]  # 只保存前500字符
                }
                for s in scripts_data.get('inline_scripts', [])
            ]
        }
        
        # 保存完整的外部JS内容到单独文件
        for url, content in scripts_data.get('external_js_content', {}).items():
            # 清理文件名
            filename = re.sub(r'[^\w\-_\.]', '_', urlparse(url).path.split('/')[-1])
            if not filename.endswith('.js'):
                filename += '.js'
            
            with open(f'extracted_js/{filename}', 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"💾 保存外部脚本: extracted_js/{filename}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"💾 保存提取结果: {output_file}")


def main():
    """主函数"""
    print("=" * 60)
    print("提取解析网站的JavaScript代码")
    print("=" * 60)
    
    video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    parser_url = f"https://videocdn.ihelpy.net/jiexi/m1907.html?m1907jx={video_url}"
    
    extractor = JavaScriptExtractor()
    
    # 提取所有脚本
    scripts_data = extractor.extract_all_scripts(parser_url)
    
    if scripts_data:
        # 查找z参数生成相关代码
        print("\n" + "=" * 60)
        print("查找z参数生成相关代码")
        print("=" * 60)
        
        findings = extractor.find_z_param_generation(scripts_data)
        
        if findings:
            print(f"\n✅ 找到 {len(findings)} 处相关代码:")
            for i, finding in enumerate(findings[:20], 1):  # 只显示前20个
                print(f"\n[{i}] {finding.get('type', 'unknown')}")
                if finding.get('url'):
                    print(f"   URL: {finding['url']}")
                print(f"   关键词: {finding.get('keyword')}")
                print(f"   行号: {finding.get('line_number')}")
                print(f"   代码: {finding.get('code')}")
        else:
            print("\n⚠️ 未找到z参数生成相关代码")
            print("   💡 可能需要执行JavaScript才能看到生成逻辑")
        
        # 保存提取的代码
        import os
        os.makedirs('extracted_js', exist_ok=True)
        extractor.save_extracted_code(scripts_data)
        
        print("\n" + "=" * 60)
        print("✅ 提取完成")
        print("=" * 60)
        print("\n📁 输出文件:")
        print("   - extracted_js_code.json (提取结果摘要)")
        print("   - extracted_js/ (外部JavaScript文件)")
    else:
        print("\n❌ 提取失败")


if __name__ == '__main__':
    main()

