"""
直接调用 jx.m3u8.tv API解析视频
基于捕获的参数，直接调用API获取m3u8链接
添加JavaScript捕获功能，分析token生成逻辑
"""

import requests
import json
import re
import asyncio
import subprocess
import tempfile
import socket
import time
import os
import shutil
from typing import Optional, Dict, List
from urllib.parse import urlparse, parse_qs, urlencode, quote
from playwright.async_api import async_playwright, Browser, BrowserContext, Page


class DirectJxM3u8TvParser:
    """直接调用 jx.m3u8.tv API解析器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def get_iframe_url(self, parser_url: str, video_url: str) -> Optional[str]:
        """从主页面提取iframe URL"""
        try:
            full_url = f"{parser_url}/jiexi/?url={quote(video_url)}"
            print(f"[步骤1] 访问主页面: {full_url}")
            
            response = self.session.get(full_url, timeout=30)
            response.raise_for_status()
            html = response.text
            
            # 提取iframe src
            iframe_patterns = [
                r'<iframe[^>]+src=["\']([^"\']+)["\']',
                r'iframe\.src\s*=\s*["\']([^"\']+)["\']',
                r'iframe\.setAttribute\(["\']src["\'],\s*["\']([^"\']+)["\']',
            ]
            
            for pattern in iframe_patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    iframe_url = match.group(1)
                    # 处理相对URL
                    if not iframe_url.startswith('http'):
                        iframe_url = f"{parser_url}{iframe_url}" if iframe_url.startswith('/') else f"{parser_url}/{iframe_url}"
                    print(f"   ✅ 找到iframe URL: {iframe_url}")
                    return iframe_url
            
            print(f"   ⚠️ 未找到iframe URL")
            return None
            
        except Exception as e:
            print(f"   ❌ 获取iframe URL失败: {e}")
            return None
    
    def extract_config_from_iframe(self, iframe_url: str) -> Optional[Dict]:
        """从iframe页面提取ConFig对象"""
        try:
            print(f"[步骤2] 访问iframe页面: {iframe_url}")
            
            response = self.session.get(iframe_url, timeout=30)
            response.raise_for_status()
            html = response.text
            
            # 方法1: 从JavaScript代码中提取ConFig对象
            config_patterns = [
                r'window\.ConFig\s*=\s*({.+?});',
                r'var\s+ConFig\s*=\s*({.+?});',
                r'ConFig\s*[:=]\s*({.+?});',
            ]
            
            for pattern in config_patterns:
                match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
                if match:
                    config_str = match.group(1)
                    try:
                        # 尝试解析JSON
                        config = json.loads(config_str)
                        print(f"   ✅ 提取到ConFig对象")
                        return config
                    except json.JSONDecodeError:
                        # 如果不是标准JSON，尝试eval（注意安全性）
                        try:
                            config = eval(config_str)
                            print(f"   ✅ 提取到ConFig对象（通过eval）")
                            return config
                        except:
                            continue
            
            print(f"   ⚠️ 未找到ConFig对象")
            return None
            
        except Exception as e:
            print(f"   ❌ 提取ConFig失败: {e}")
            return None
    
    def find_api_url_in_html(self, html: str) -> Optional[str]:
        """从HTML中查找API URL"""
        api_patterns = [
            r'["\'](https?://[^"\']+api[^"\']+)["\']',
            r'apiUrl\s*[:=]\s*["\']([^"\']+)["\']',
            r'api_url\s*[:=]\s*["\']([^"\']+)["\']',
            r'fetch\(["\']([^"\']+api[^"\']+)["\']',
            r'\.get\(["\']([^"\']+api[^"\']+)["\']',
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                if 'api' in match.lower():
                    return match
        
        return None
    
    def construct_api_url(self, video_url: str, captured_params: Dict = None) -> Optional[str]:
        """构造API URL"""
        # 如果提供了捕获的参数，使用它们
        if captured_params and captured_params.get('url'):
            api_url = captured_params['url']
            print(f"[步骤3] 使用捕获的API URL: {api_url[:100]}...")
            return api_url
        
        # 否则尝试构造
        # 常见的API端点模式
        api_endpoints = [
            'https://jx.m3u8.tv/api/parse',
            'https://jx.m3u8.tv/api/jiexi',
            'https://jx.m3u8.tv/api/video',
            'https://api.m3u8.tv/parse',
        ]
        
        # 尝试访问主页面获取API URL
        try:
            parser_url = "https://jx.m3u8.tv"
            full_url = f"{parser_url}/jiexi/?url={quote(video_url)}"
            response = self.session.get(full_url, timeout=30)
            html = response.text
            
            api_url = self.find_api_url_in_html(html)
            if api_url:
                print(f"[步骤3] 从HTML中提取API URL: {api_url}")
                return api_url
        except:
            pass
        
        # 如果找不到，尝试常见的端点
        for endpoint in api_endpoints:
            print(f"[步骤3] 尝试API端点: {endpoint}")
            return endpoint
        
        return None
    
    def call_api(self, api_url: str, video_url: str, params: Dict = None) -> Optional[Dict]:
        """调用API"""
        try:
            print(f"[步骤4] 调用API: {api_url[:100]}...")
            
            # 准备参数
            request_params = params.copy() if params else {}
            if 'url' not in request_params:
                request_params['url'] = video_url
            
            # 发送请求
            response = self.session.get(api_url, params=request_params, timeout=30)
            response.raise_for_status()
            
            content = response.text
            print(f"   响应状态码: {response.status_code}")
            print(f"   响应长度: {len(content)} 字符")
            
            # 尝试解析JSON
            try:
                json_data = json.loads(content)
                print(f"   ✅ JSON解析成功")
                return json_data
            except json.JSONDecodeError:
                # 尝试从响应中提取m3u8链接
                m3u8_urls = self.extract_m3u8_from_text(content)
                if m3u8_urls:
                    print(f"   ✅ 从响应中提取到 {len(m3u8_urls)} 个m3u8链接")
                    return {'m3u8_urls': m3u8_urls}
                
                print(f"   ⚠️ 无法解析响应")
                print(f"   响应预览: {content[:500]}")
                return None
                
        except Exception as e:
            print(f"   ❌ API调用失败: {e}")
            return None
    
    def extract_m3u8_from_text(self, text: str) -> List[str]:
        """从文本中提取m3u8链接"""
        m3u8_patterns = [
            r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
            r'["\']([^"\']+\.m3u8[^"\']*)["\']',
            r'url["\']?\s*[:=]\s*["\']([^"\']+\.m3u8[^"\']*)["\']',
        ]
        
        m3u8_urls = []
        for pattern in m3u8_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                url = match if isinstance(match, str) else match[0] if match else None
                if url and url.startswith('http') and url not in m3u8_urls:
                    m3u8_urls.append(url)
        
        return m3u8_urls
    
    def extract_m3u8_from_json(self, json_data: Dict) -> List[str]:
        """从JSON中提取m3u8链接"""
        m3u8_urls = []
        
        def find_m3u8(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k in ['url', 'm3u8', 'play_url', 'video_url', 'src'] and isinstance(v, str) and '.m3u8' in v:
                        m3u8_urls.append(v)
                    find_m3u8(v)
            elif isinstance(obj, list):
                for item in obj:
                    find_m3u8(item)
            elif isinstance(obj, str):
                if '.m3u8' in obj and obj.startswith('http'):
                    m3u8_urls.append(obj)
        
        find_m3u8(json_data)
        return list(set(m3u8_urls))  # 去重
    
    def follow_redirects(self, url: str, max_redirects: int = 10) -> Optional[str]:
        """跟踪重定向"""
        current_url = url
        redirect_count = 0
        
        while redirect_count < max_redirects:
            try:
                response = self.session.get(current_url, allow_redirects=False, timeout=30)
                
                # 检查是否是m3u8文件
                if '.m3u8' in current_url or response.headers.get('Content-Type', '').startswith('application/vnd.apple.mpegurl'):
                    return current_url
                
                # 检查重定向
                if response.status_code in [301, 302, 303, 307, 308]:
                    location = response.headers.get('Location')
                    if location:
                        if not location.startswith('http'):
                            from urllib.parse import urljoin
                            location = urljoin(current_url, location)
                        current_url = location
                        redirect_count += 1
                        print(f"   重定向 {redirect_count}: {current_url[:100]}...")
                        continue
                
                # 没有重定向
                break
                
            except Exception as e:
                print(f"   跟踪重定向失败: {e}")
                break
        
        return current_url if '.m3u8' in current_url else None
    
    # ==================== JavaScript 捕获功能 ====================
    
    def get_free_port(self):
        """获取一个未被占用的端口"""
        s = socket.socket()
        s.bind(('', 0))
        port = s.getsockname()[1]
        s.close()
        return port
    
    def launch_chrome(self, url="about:blank", chrome_path=None):
        """启动独立的Chrome浏览器实例"""
        if not chrome_path:
            possible_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    chrome_path = path
                    break
            
            if not chrome_path:
                print("[ERROR] 未找到Chrome浏览器")
                return None, None, None
        
        debug_port = self.get_free_port()
        temp_user_data_dir = tempfile.mkdtemp(prefix="chrome_automation_")
        
        args = [
            chrome_path,
            f'--remote-debugging-port={debug_port}',
            f'--user-data-dir={temp_user_data_dir}',
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-extensions',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-web-security',
            '--disable-site-isolation-trials',
            '--disable-features=BlockInsecurePrivateNetworkRequests',
            '--disable-blink-features=AutomationControlled',
            url
        ]
        
        try:
            chrome_process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8',
                errors='ignore'
            )
            
            for i in range(30):
                try:
                    s = socket.create_connection(('127.0.0.1', debug_port), timeout=1.0)
                    s.close()
                    return chrome_process, debug_port, temp_user_data_dir
                except Exception:
                    if chrome_process.poll() is not None:
                        return None, None, None
                    time.sleep(1)
            
            chrome_process.terminate()
            return None, None, None
            
        except Exception as e:
            return None, None, None
    
    def cleanup_user_data(self, user_data_dir):
        """删除临时用户数据目录"""
        if user_data_dir and os.path.exists(user_data_dir):
            shutil.rmtree(user_data_dir, ignore_errors=True)
    
    async def add_stealth_script(self, context: BrowserContext):
        """添加反爬虫脚本"""
        stealth_script = """
        (function() {
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            delete navigator.__proto__.webdriver;
            Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
            Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en'] });
            window.chrome = { runtime: {}, loadTimes: function() {}, csi: function() {}, app: {} };
            window.debugger = function() {};
            console.debug = () => {};
        })();
        """
        await context.add_init_script(script=stealth_script)
    
    async def capture_javascript_code(self, page: Page) -> Dict:
        """捕获JavaScript代码"""
        print("\n[JS捕获] 开始捕获JavaScript代码...")
        
        js_files = []
        inline_scripts = []
        
        try:
            # 获取所有script标签的信息
            scripts_info = await page.evaluate("""
                () => {
                    const scripts = [];
                    
                    // 外部脚本
                    document.querySelectorAll('script[src]').forEach(script => {
                        scripts.push({
                            type: 'external',
                            src: script.src,
                            content: null
                        });
                    });
                    
                    // 内联脚本
                    document.querySelectorAll('script:not([src])').forEach(script => {
                        scripts.push({
                            type: 'inline',
                            src: null,
                            content: script.textContent
                        });
                    });
                    
                    return scripts;
                }
            """)
            
            print(f"   [OK] 找到 {len(scripts_info)} 个script标签")
            
            # 下载外部脚本
            for script_info in scripts_info:
                if script_info['type'] == 'external' and script_info['src']:
                    try:
                        response = await page.request.get(script_info['src'])
                        if response.ok():
                            content = await response.text()
                            js_files.append({
                                'type': 'external',
                                'url': script_info['src'],
                                'content': content,
                                'size': len(content)
                            })
                            print(f"   [OK] 下载外部脚本: {script_info['src'][:80]}... ({len(content)} 字符)")
                    except Exception as e:
                        print(f"   [WARN] 下载失败 {script_info['src']}: {e}")
                
                elif script_info['type'] == 'inline' and script_info['content']:
                    inline_scripts.append({
                        'type': 'inline',
                        'content': script_info['content'],
                        'size': len(script_info['content'])
                    })
                    print(f"   [OK] 捕获内联脚本 ({len(script_info['content'])} 字符)")
            
            return {
                'external_scripts': js_files,
                'inline_scripts': inline_scripts
            }
        
        except Exception as e:
            print(f"   [ERROR] 捕获JavaScript代码失败: {e}")
            return {
                'external_scripts': [],
                'inline_scripts': []
            }
    
    def analyze_token_generation_in_js(self, js_code: str) -> Dict:
        """分析JavaScript代码中的token生成逻辑"""
        findings = {
            'token_patterns': [],
            'cachem3u8_patterns': [],
            'encryption_functions': [],
            'md5_usage': [],
            'aes_usage': [],
            'config_usage': [],
            'api_calls': []
        }
        
        # 查找token相关模式
        token_patterns = [
            r'token\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{50,})["\']?',  # token赋值
            r'["\']token["\']\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{50,})["\']?',  # token属性
            r'\?token=([a-zA-Z0-9_\-]{50,})',  # URL中的token
            r'cachem3u8[^"\']*token=([a-zA-Z0-9_\-]{50,})',  # cachem3u8 URL中的token
        ]
        
        for pattern in token_patterns:
            matches = re.findall(pattern, js_code, re.IGNORECASE)
            if matches:
                findings['token_patterns'].extend(matches[:5])  # 只保存前5个
        
        # 查找cachem3u8相关模式
        cachem3u8_patterns = [
            r'cachem3u8[^"\']+',
            r'Cache/[^"\']+\.m3u8',
            r'Cache/LZ/[^"\']+',
        ]
        
        for pattern in cachem3u8_patterns:
            matches = re.findall(pattern, js_code, re.IGNORECASE)
            if matches:
                findings['cachem3u8_patterns'].extend(matches[:5])
        
        # 查找加密函数
        encryption_patterns = [
            r'(encrypt|decrypt|AES|CryptoJS|rc4|md5|sha256|sha1)\s*\(',
            r'CryptoJS\.(encrypt|decrypt|AES|MD5|SHA256)',
            r'\.encrypt\s*\(',
            r'\.decrypt\s*\(',
        ]
        
        for pattern in encryption_patterns:
            matches = re.findall(pattern, js_code, re.IGNORECASE)
            if matches:
                findings['encryption_functions'].extend(matches[:10])
        
        # 查找MD5使用
        md5_patterns = [
            r'md5\s*\([^)]+\)',
            r'MD5\s*\([^)]+\)',
            r'CryptoJS\.MD5\s*\(',
        ]
        
        for pattern in md5_patterns:
            matches = re.findall(pattern, js_code, re.IGNORECASE)
            if matches:
                findings['md5_usage'].extend(matches[:10])
        
        # 查找AES使用
        aes_patterns = [
            r'AES\.(encrypt|decrypt)',
            r'CryptoJS\.AES\.(encrypt|decrypt)',
            r'AES\.new\s*\(',
        ]
        
        for pattern in aes_patterns:
            matches = re.findall(pattern, js_code, re.IGNORECASE)
            if matches:
                findings['aes_usage'].extend(matches[:10])
        
        # 查找ConFig使用
        config_patterns = [
            r'ConFig\.(url|id|uid|config)',
            r'config\.(url|id|uid)',
            r'window\.ConFig',
        ]
        
        for pattern in config_patterns:
            matches = re.findall(pattern, js_code, re.IGNORECASE)
            if matches:
                findings['config_usage'].extend(matches[:10])
        
        # 查找API调用
        api_patterns = [
            r'["\'](/admin/api\.php[^"\']*)["\']',
            r'fetch\s*\(\s*["\']([^"\']+api[^"\']+)["\']',
            r'\.get\s*\(\s*["\']([^"\']+api[^"\']+)["\']',
            r'\.post\s*\(\s*["\']([^"\']+api[^"\']+)["\']',
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, js_code, re.IGNORECASE)
            if matches:
                findings['api_calls'].extend(matches[:10])
        
        return findings
    
    async def analyze_all_javascript(self, js_data: Dict) -> Dict:
        """分析所有JavaScript代码"""
        print("\n[JS分析] 开始分析JavaScript代码...")
        
        all_findings = {
            'external_scripts': {},
            'inline_scripts': []
        }
        
        # 分析外部脚本
        for script in js_data.get('external_scripts', []):
            url = script.get('url', 'unknown')
            content = script.get('content', '')
            
            print(f"\n   分析外部脚本: {url[:80]}...")
            findings = self.analyze_token_generation_in_js(content)
            all_findings['external_scripts'][url] = findings
            
            # 打印关键发现
            if findings['token_patterns']:
                print(f"      [OK] 找到 {len(findings['token_patterns'])} 个token模式")
            if findings['cachem3u8_patterns']:
                print(f"      [OK] 找到 {len(findings['cachem3u8_patterns'])} 个cachem3u8模式")
            if findings['encryption_functions']:
                print(f"      [OK] 找到 {len(findings['encryption_functions'])} 个加密函数")
            if findings['md5_usage']:
                print(f"      [OK] 找到 {len(findings['md5_usage'])} 个MD5使用")
            if findings['aes_usage']:
                print(f"      [OK] 找到 {len(findings['aes_usage'])} 个AES使用")
        
        # 分析内联脚本
        for i, script in enumerate(js_data.get('inline_scripts', [])):
            content = script.get('content', '')
            if content:
                print(f"\n   分析内联脚本 #{i+1} ({len(content)} 字符)")
                findings = self.analyze_token_generation_in_js(content)
                all_findings['inline_scripts'].append(findings)
                
                if findings['token_patterns'] or findings['cachem3u8_patterns']:
                    print(f"      [OK] 找到关键模式")
        
        return all_findings
    
    async def capture_and_analyze_js(self, video_url: str, parser_url: str = "https://jx.2s0.cn") -> Optional[Dict]:
        """捕获并分析JavaScript代码"""
        print("=" * 60)
        print("JavaScript代码捕获和分析")
        print("=" * 60)
        print(f"目标视频: {video_url}")
        print(f"解析网站: {parser_url}")
        
        chrome_process = None
        user_data_dir = None
        
        try:
            # 启动独立浏览器
            print(f"\n[步骤0] 启动独立Chrome浏览器...")
            chrome_process, debug_port, user_data_dir = self.launch_chrome()
            if not chrome_process or not debug_port:
                print("[ERROR] 启动独立Chrome浏览器失败")
                return None
            print(f"   [OK] Chrome浏览器已启动，调试端口: {debug_port}")
            
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{debug_port}")
                print(f"   [OK] 成功连接到Chrome浏览器")
                
                # 创建上下文
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    locale='zh-CN',
                )
                
                # 添加反爬虫脚本
                await self.add_stealth_script(context)
                
                page = await context.new_page()
                
                # 访问解析网站
                full_url = f"{parser_url}/player/?url={quote(video_url)}"
                print(f"\n[步骤1] 访问解析网站: {full_url}")
                
                await page.goto(full_url, wait_until='domcontentloaded', timeout=60000)
                print(f"   [OK] 页面加载完成")
                
                # 等待JavaScript执行
                print(f"\n[步骤2] 等待JavaScript执行...")
                await asyncio.sleep(10)
                
                # 捕获JavaScript代码
                js_data = await self.capture_javascript_code(page)
                
                # 分析JavaScript代码
                analysis_result = await self.analyze_all_javascript(js_data)
                
                # 保存结果
                result = {
                    'video_url': video_url,
                    'parser_url': parser_url,
                    'js_files': js_data,
                    'analysis': analysis_result
                }
                
                output_file = 'js_capture_analysis.json'
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False, default=str)
                print(f"\n[OK] 结果已保存到: {output_file}")
                
                # 保存JavaScript文件
                js_dir = 'captured_js_files'
                os.makedirs(js_dir, exist_ok=True)
                
                for script in js_data.get('external_scripts', []):
                    url = script.get('url', 'unknown')
                    content = script.get('content', '')
                    if content:
                        # 从URL提取文件名
                        filename = url.split('/')[-1].split('?')[0] or 'script.js'
                        filepath = os.path.join(js_dir, filename)
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"   [OK] 保存JavaScript文件: {filepath}")
                
                # 打印总结
                print("\n" + "=" * 60)
                print("[总结]")
                print("=" * 60)
                
                total_token_patterns = sum(len(v.get('token_patterns', [])) for v in analysis_result.get('external_scripts', {}).values())
                total_token_patterns += sum(len(v.get('token_patterns', [])) for v in analysis_result.get('inline_scripts', []))
                
                if total_token_patterns > 0:
                    print(f"\n[OK] 找到 {total_token_patterns} 个token相关模式")
                
                total_cachem3u8 = sum(len(v.get('cachem3u8_patterns', [])) for v in analysis_result.get('external_scripts', {}).values())
                total_cachem3u8 += sum(len(v.get('cachem3u8_patterns', [])) for v in analysis_result.get('inline_scripts', []))
                
                if total_cachem3u8 > 0:
                    print(f"[OK] 找到 {total_cachem3u8} 个cachem3u8相关模式")
                
                total_encryption = sum(len(v.get('encryption_functions', [])) for v in analysis_result.get('external_scripts', {}).values())
                total_encryption += sum(len(v.get('encryption_functions', [])) for v in analysis_result.get('inline_scripts', []))
                
                if total_encryption > 0:
                    print(f"[OK] 找到 {total_encryption} 个加密函数")
                
                await context.close()
                await browser.close()
                
                return result
        
        finally:
            # 清理资源
            if chrome_process:
                try:
                    chrome_process.terminate()
                    chrome_process.wait(timeout=5)
                except:
                    try:
                        chrome_process.kill()
                    except:
                        pass
            
            if user_data_dir:
                self.cleanup_user_data(user_data_dir)
    
    def parse_video(self, video_url: str, captured_params_file: str = None) -> Optional[str]:
        """解析视频，获取m3u8链接"""
        print("=" * 60)
        print("直接调用 jx.m3u8.tv API解析视频")
        print("=" * 60)
        print(f"目标视频: {video_url}")
        
        # 如果提供了捕获的参数文件，加载它
        captured_params = None
        if captured_params_file:
            try:
                with open(captured_params_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 获取最新的参数
                    if data.get('captured_params'):
                        captured_params = data['captured_params'][-1]
                        print(f"\n📋 使用捕获的参数:")
                        for k, v in captured_params.items():
                            if k not in ['url', 'timestamp']:
                                print(f"   {k}: {v}")
            except Exception as e:
                print(f"   ⚠️ 加载捕获参数失败: {e}")
        
        parser_url = "https://jx.m3u8.tv"
        
        # 方法1: 尝试通过iframe和ConFig解析
        iframe_url = self.get_iframe_url(parser_url, video_url)
        if iframe_url:
            config = self.extract_config_from_iframe(iframe_url)
            if config and config.get('url'):
                # 如果有加密URL，需要解密（这里假设直接使用）
                config_url = config['url']
                print(f"\n[步骤5] 跟踪ConFig URL重定向...")
                m3u8_url = self.follow_redirects(config_url)
                if m3u8_url:
                    print(f"\n✅ 成功获取m3u8链接: {m3u8_url}")
                    return m3u8_url
        
        # 方法2: 直接调用API
        api_url = self.construct_api_url(video_url, captured_params)
        if api_url:
            # 准备参数
            params = {}
            if captured_params:
                for k, v in captured_params.items():
                    if k not in ['url', 'timestamp']:
                        params[k] = v
            
            api_response = self.call_api(api_url, video_url, params)
            if api_response:
                # 提取m3u8链接
                m3u8_urls = self.extract_m3u8_from_json(api_response)
                if m3u8_urls:
                    print(f"\n✅ 成功提取到 {len(m3u8_urls)} 个m3u8链接:")
                    for i, url in enumerate(m3u8_urls[:3], 1):
                        print(f"   [{i}] {url[:100]}...")
                    return m3u8_urls[0]
        
        print(f"\n❌ 解析失败")
        print(f"\n💡 建议:")
        print(f"   1. 运行 capture_jx_m3u8_tv_params.py 捕获最新参数")
        print(f"   2. 检查网络连接")
        print(f"   3. 查看 captured_jx_m3u8_tv_params.json 文件")
        
        return None


async def main_async():
    """异步主函数 - 用于JavaScript捕获"""
    video_url = "https://v.youku.com/v_show/id_XMTA0MTc5NzI4.html"
    parser_url = "https://jx.2s0.cn"
    
    parser = DirectJxM3u8TvParser()
    
    # 捕获并分析JavaScript代码
    result = await parser.capture_and_analyze_js(video_url, parser_url)
    
    if result:
        print(f"\n[成功] JavaScript代码捕获和分析完成！")
        print(f"   结果已保存到: js_capture_analysis.json")
        print(f"   JavaScript文件已保存到: captured_js_files/")
    else:
        print(f"\n[失败] JavaScript代码捕获失败")


def main():
    """主函数"""
    import sys
    
    # 检查是否有 --capture-js 参数
    if '--capture-js' in sys.argv or '-js' in sys.argv:
        # 运行JavaScript捕获
        asyncio.run(main_async())
        return
    
    video_url = "https://v.youku.com/v_show/id_XMTA0MTc5NzI4.html"
    
    parser = DirectJxM3u8TvParser()
    
    # 尝试使用捕获的参数文件
    m3u8_url = parser.parse_video(
        video_url, 
        captured_params_file='captured_jx_m3u8_tv_params.json'
    )
    
    if m3u8_url:
        print(f"\n✅ 解析成功！")
        print(f"m3u8链接: {m3u8_url}")
    else:
        print(f"\n⚠️ 解析失败")
        print(f"请先运行 capture_jx_m3u8_tv_params.py 捕获参数")
        print(f"\n💡 或者运行JavaScript捕获:")
        print(f"   python direct_jx_m3u8_tv_parser.py --capture-js")


if __name__ == '__main__':
    main()

