"""
分析 jx.2s0.cn token 生成方式
使用浏览器自动化访问页面，监听网络请求，分析token生成逻辑
"""

import asyncio
import subprocess
import tempfile
import socket
import time
import os
import shutil
import json
import re
from typing import Optional, Dict, List
from urllib.parse import urlparse, parse_qs
from playwright.async_api import async_playwright, Browser, BrowserContext, Page


def get_free_port():
    """获取一个未被占用的端口"""
    s = socket.socket()
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port


def launch_chrome(url="about:blank", chrome_path=None):
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
        raise FileNotFoundError("未找到Chrome浏览器路径")
    
    debug_port = get_free_port()
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
    
    chrome_process = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding='utf-8',
        errors='ignore'
    )
    
    # 等待浏览器启动
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


async def add_stealth_script(context: BrowserContext):
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


class Jx2s0TokenAnalyzer:
    """jx.2s0.cn token 分析器"""
    
    def __init__(self):
        self.target_url = "https://jx.2s0.cn/player/?url=https://v.youku.com/v_show/id_XMTA0MTc5NzI4.html"
        self.m3u8_urls = []
        self.network_requests = []
        self.js_functions = []
        self.token_generation_logic = {}
        
    async def analyze(self):
        """执行完整分析流程"""
        chrome_process = None
        user_data_dir = None
        
        try:
            print("=" * 80)
            print("🔍 开始分析 jx.2s0.cn token 生成方式")
            print("=" * 80)
            
            # 启动独立浏览器
            print("\n[步骤1] 启动独立Chrome浏览器实例...")
            chrome_process, debug_port, user_data_dir = launch_chrome()
            if not chrome_process:
                print("❌ 启动浏览器失败")
                return
            
            print(f"✅ 浏览器已启动，调试端口: {debug_port}")
            
            async with async_playwright() as p:
                # 连接到浏览器
                browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{debug_port}")
                
                # 创建上下文并添加反爬虫脚本
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    locale='zh-CN',
                )
                await add_stealth_script(context)
                
                page = await context.new_page()
                
                # 监听网络请求
                print("\n[步骤2] 设置网络请求监听...")
                await self._setup_network_listeners(page)
                
                # 监听控制台消息（可能包含token生成信息）
                page.on('console', lambda msg: print(f"[Console] {msg.text}"))
                
                # 访问目标页面
                print(f"\n[步骤3] 访问目标页面: {self.target_url}")
                await page.goto(self.target_url, wait_until='domcontentloaded', timeout=60000)
                
                # 等待页面加载
                print("\n[步骤4] 等待页面加载和视频初始化...")
                await asyncio.sleep(5)
                
                # 尝试等待视频播放器加载
                try:
                    await page.wait_for_selector('video, iframe, [class*="player"], [id*="player"]', timeout=10000)
                except:
                    print("⚠️  未找到视频播放器元素，继续分析...")
                
                # 等待更多网络请求（m3u8请求可能需要时间）
                print("\n[步骤5] 等待m3u8请求...")
                await asyncio.sleep(10)
                
                # 分析页面JavaScript代码
                print("\n[步骤6] 分析页面JavaScript代码...")
                await self._analyze_javascript(page)
                
                # 提取token生成逻辑
                print("\n[步骤7] 提取token生成逻辑...")
                await self._extract_token_logic(page)
                
                # 输出分析结果
                print("\n" + "=" * 80)
                print("📊 分析结果")
                print("=" * 80)
                self._print_results()
                
                # 保存分析结果
                self._save_results()
                
                await context.close()
                await browser.close()
        
        except Exception as e:
            print(f"\n❌ 分析过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
        
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
                try:
                    shutil.rmtree(user_data_dir, ignore_errors=True)
                except:
                    pass
    
    async def _setup_network_listeners(self, page: Page):
        """设置网络请求监听器"""
        async def handle_request(request):
            url = request.url
            method = request.method
            
            # 记录所有请求
            self.network_requests.append({
                'url': url,
                'method': method,
                'headers': request.headers,
                'timestamp': time.time()
            })
            
            # 检查是否是m3u8请求
            if '.m3u8' in url or 'token=' in url:
                print(f"\n🎯 发现关键请求:")
                print(f"   URL: {url}")
                print(f"   方法: {method}")
                
                # 提取token
                if 'token=' in url:
                    parsed = urlparse(url)
                    params = parse_qs(parsed.query)
                    if 'token' in params:
                        token = params['token'][0]
                        print(f"   Token: {token[:50]}...")
                        self.m3u8_urls.append({
                            'url': url,
                            'token': token,
                            'timestamp': time.time()
                        })
        
        async def handle_response(response):
            url = response.url
            
            # 检查响应头中是否有token相关信息
            headers = response.headers
            if 'token' in str(headers).lower():
                print(f"\n📦 响应中包含token信息:")
                print(f"   URL: {url}")
                for key, value in headers.items():
                    if 'token' in key.lower():
                        print(f"   {key}: {value}")
            
            # 如果是JavaScript文件，尝试分析
            if url.endswith('.js') or 'javascript' in headers.get('content-type', ''):
                try:
                    content = await response.text()
                    # 查找token相关的函数
                    if 'token' in content.lower() or 'm3u8' in content.lower():
                        print(f"\n📜 发现相关JS文件: {url}")
                        # 提取可能的token生成函数
                        await self._extract_token_functions_from_js(content, url)
                except:
                    pass
        
        page.on('request', handle_request)
        page.on('response', handle_response)
    
    async def _extract_token_functions_from_js(self, js_content: str, js_url: str):
        """从JavaScript代码中提取token生成函数"""
        # 查找token相关的函数定义
        patterns = [
            r'function\s+(\w*[tT]oken\w*)\s*\([^)]*\)\s*\{[^}]*\}',
            r'(\w*[tT]oken\w*)\s*[:=]\s*function\s*\([^)]*\)\s*\{[^}]*\}',
            r'(\w*[tT]oken\w*)\s*[:=]\s*\([^)]*\)\s*=>\s*\{[^}]*\}',
            r'\.(\w*[tT]oken\w*)\s*[:=]\s*function',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, js_content, re.MULTILINE | re.DOTALL)
            for match in matches:
                func_name = match.group(1) if match.groups() else 'unknown'
                func_code = match.group(0)
                self.js_functions.append({
                    'name': func_name,
                    'code': func_code[:500],  # 只保存前500字符
                    'url': js_url
                })
                print(f"   ✅ 发现函数: {func_name}")
    
    async def _analyze_javascript(self, page: Page):
        """分析页面中的JavaScript代码"""
        try:
            # 获取所有脚本标签的内容
            scripts = await page.evaluate("""
                () => {
                    const scripts = [];
                    document.querySelectorAll('script').forEach(script => {
                        if (script.src) {
                            scripts.push({ type: 'external', src: script.src });
                        } else if (script.textContent) {
                            scripts.push({ type: 'inline', content: script.textContent.substring(0, 1000) });
                        }
                    });
                    return scripts;
                }
            """)
            
            print(f"\n📜 发现 {len(scripts)} 个脚本标签")
            
            # 查找包含token的脚本
            for script in scripts:
                if script['type'] == 'inline':
                    content = script.get('content', '')
                    if 'token' in content.lower() or 'm3u8' in content.lower():
                        print(f"   ✅ 内联脚本包含token相关代码")
                        # 提取token相关代码片段
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if 'token' in line.lower():
                                print(f"      行 {i+1}: {line.strip()[:100]}")
            
            # 尝试从window对象中提取token相关函数
            try:
                window_vars = await page.evaluate("""
                    () => {
                        const vars = {};
                        for (let key in window) {
                            if (key.toLowerCase().includes('token') || 
                                key.toLowerCase().includes('m3u8') ||
                                key.toLowerCase().includes('player')) {
                                try {
                                    const value = window[key];
                                    vars[key] = typeof value === 'function' ? 'function' : 
                                               typeof value === 'object' ? 'object' : String(value).substring(0, 100);
                                } catch(e) {}
                            }
                        }
                        return vars;
                    }
                """)
                
                if window_vars:
                    print(f"\n🌐 Window对象中的相关变量:")
                    for key, value in window_vars.items():
                        print(f"   {key}: {value}")
                        self.token_generation_logic[key] = value
            except Exception as e:
                print(f"   ⚠️  提取window变量失败: {e}")
        
        except Exception as e:
            print(f"⚠️  JavaScript分析失败: {e}")
    
    async def _extract_token_logic(self, page: Page):
        """提取token生成逻辑"""
        try:
            # 尝试执行一些常见的token生成函数名
            common_token_funcs = [
                'getToken',
                'generateToken',
                'createToken',
                'makeToken',
                'token',
                'getM3u8Token',
            ]
            
            print("\n🔍 尝试查找token生成函数...")
            for func_name in common_token_funcs:
                try:
                    result = await page.evaluate(f"""
                        () => {{
                            if (typeof window.{func_name} === 'function') {{
                                return 'function exists';
                            }}
                            return null;
                        }}
                    """)
                    if result:
                        print(f"   ✅ 发现函数: {func_name}")
                        # 尝试获取函数代码
                        try:
                            func_code = await page.evaluate(f"window.{func_name}.toString()")
                            print(f"   函数代码: {func_code[:200]}...")
                            self.token_generation_logic[func_name] = func_code
                        except:
                            pass
                except:
                    pass
            
            # 查找所有包含token的全局变量
            try:
                all_vars = await page.evaluate("""
                    () => {
                        const result = {};
                        for (let key in window) {
                            if (key.toLowerCase().includes('token') || 
                                key.toLowerCase().includes('m3u8')) {
                                try {
                                    const value = window[key];
                                    if (typeof value === 'string' && value.length > 0) {
                                        result[key] = value.substring(0, 200);
                                    } else if (typeof value === 'function') {
                                        result[key] = 'function: ' + value.toString().substring(0, 200);
                                    }
                                } catch(e) {}
                            }
                        }
                        return result;
                    }
                """)
                
                if all_vars:
                    print(f"\n📋 找到的token相关变量:")
                    for key, value in all_vars.items():
                        print(f"   {key}: {value}")
                        self.token_generation_logic[key] = value
            except Exception as e:
                print(f"   ⚠️  查找变量失败: {e}")
        
        except Exception as e:
            print(f"⚠️  提取token逻辑失败: {e}")
    
    def _print_results(self):
        """打印分析结果"""
        print("\n1️⃣  m3u8 URL和Token:")
        if self.m3u8_urls:
            for i, item in enumerate(self.m3u8_urls, 1):
                print(f"\n   [{i}] URL: {item['url']}")
                print(f"       Token: {item['token']}")
        else:
            print("   ❌ 未找到m3u8 URL")
        
        print(f"\n2️⃣  网络请求统计:")
        print(f"   总请求数: {len(self.network_requests)}")
        m3u8_requests = [r for r in self.network_requests if '.m3u8' in r['url']]
        print(f"   m3u8相关请求: {len(m3u8_requests)}")
        token_requests = [r for r in self.network_requests if 'token=' in r['url']]
        print(f"   token相关请求: {len(token_requests)}")
        
        print(f"\n3️⃣  JavaScript函数:")
        if self.js_functions:
            for func in self.js_functions:
                print(f"   函数名: {func['name']}")
                print(f"   来源: {func['url']}")
        else:
            print("   ❌ 未找到相关函数")
        
        print(f"\n4️⃣  Token生成逻辑:")
        if self.token_generation_logic:
            for key, value in self.token_generation_logic.items():
                print(f"   {key}: {str(value)[:200]}...")
        else:
            print("   ❌ 未找到token生成逻辑")
    
    def _save_results(self):
        """保存分析结果到文件"""
        results = {
            'target_url': self.target_url,
            'm3u8_urls': self.m3u8_urls,
            'network_requests_count': len(self.network_requests),
            'm3u8_requests': [r for r in self.network_requests if '.m3u8' in r['url']],
            'token_requests': [r for r in self.network_requests if 'token=' in r['url']],
            'js_functions': self.js_functions,
            'token_generation_logic': self.token_generation_logic,
            'timestamp': time.time()
        }
        
        output_file = 'jx2s0_token_analysis.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 分析结果已保存到: {output_file}")


async def main():
    """主函数"""
    analyzer = Jx2s0TokenAnalyzer()
    await analyzer.analyze()


if __name__ == '__main__':
    asyncio.run(main())

