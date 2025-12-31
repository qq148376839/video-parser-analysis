"""
深度分析 jx.2s0.cn token 生成方式
通过注入JavaScript代码监控token的生成过程
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


async def inject_token_monitor(page: Page):
    """注入token监控代码"""
    monitor_script = """
    (function() {
        // 监控对象
        window.__tokenMonitor = {
            m3u8Urls: [],
            tokenGenerations: [],
            urlConstructions: [],
            apiCalls: [],
            configData: null
        };
        
        // 拦截XMLHttpRequest
        const originalOpen = XMLHttpRequest.prototype.open;
        const originalSend = XMLHttpRequest.prototype.send;
        
        XMLHttpRequest.prototype.open = function(method, url, ...args) {
            this._url = url;
            this._method = method;
            
            // 记录API调用
            if (url.includes('api.php') || url.includes('admin')) {
                window.__tokenMonitor.apiCalls.push({
                    method: method,
                    url: url,
                    timestamp: Date.now()
                });
            }
            
            return originalOpen.apply(this, [method, url, ...args]);
        };
        
        XMLHttpRequest.prototype.send = function(...args) {
            const xhr = this;
            
            xhr.addEventListener('load', function() {
                if (xhr._url && (xhr._url.includes('api.php') || xhr._url.includes('admin'))) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        if (response.data) {
                            window.__tokenMonitor.configData = response.data;
                            console.log('[TokenMonitor] API响应:', response.data);
                        }
                    } catch(e) {}
                }
            });
            
            return originalSend.apply(this, args);
        };
        
        // 拦截fetch
        const originalFetch = window.fetch;
        window.fetch = function(...args) {
            const url = args[0];
            
            if (url && (typeof url === 'string' && (url.includes('api.php') || url.includes('admin')))) {
                window.__tokenMonitor.apiCalls.push({
                    method: 'fetch',
                    url: url,
                    timestamp: Date.now()
                });
            }
            
            return originalFetch.apply(...args).then(response => {
                if (response.url && (response.url.includes('api.php') || response.url.includes('admin'))) {
                    response.clone().json().then(data => {
                        if (data.data) {
                            window.__tokenMonitor.configData = data.data;
                            console.log('[TokenMonitor] Fetch响应:', data.data);
                        }
                    }).catch(() => {});
                }
                return response;
            });
        };
        
        // 监控URL构造
        const originalConcat = String.prototype.concat;
        String.prototype.concat = function(...args) {
            const result = originalConcat.apply(this, args);
            if (result.includes('cachem3u8') || result.includes('m3u8') || result.includes('token=')) {
                window.__tokenMonitor.urlConstructions.push({
                    url: result,
                    stack: new Error().stack,
                    timestamp: Date.now()
                });
            }
            return result;
        };
        
        // 监控字符串拼接
        const originalToString = Object.prototype.toString;
        Object.prototype.toString = function() {
            const str = originalToString.call(this);
            if (str.includes('cachem3u8') || (str.includes('m3u8') && str.includes('token='))) {
                window.__tokenMonitor.urlConstructions.push({
                    url: str,
                    timestamp: Date.now()
                });
            }
            return str;
        };
        
        // 监控window对象的变化
        const originalDefineProperty = Object.defineProperty;
        Object.defineProperty = function(obj, prop, descriptor) {
            if (obj === window && (prop.includes('token') || prop.includes('m3u8') || prop.includes('YKQ'))) {
                console.log('[TokenMonitor] 定义属性:', prop, descriptor);
            }
            return originalDefineProperty.apply(this, arguments);
        };
        
        // 监控所有包含token的URL
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // Element node
                        // 检查src属性
                        if (node.src && (node.src.includes('m3u8') || node.src.includes('token='))) {
                            window.__tokenMonitor.m3u8Urls.push({
                                url: node.src,
                                element: node.tagName,
                                timestamp: Date.now()
                            });
                        }
                        // 检查所有属性
                        if (node.attributes) {
                            for (let attr of node.attributes) {
                                if (attr.value && (attr.value.includes('m3u8') || attr.value.includes('token='))) {
                                    window.__tokenMonitor.m3u8Urls.push({
                                        url: attr.value,
                                        attribute: attr.name,
                                        element: node.tagName,
                                        timestamp: Date.now()
                                    });
                                }
                            }
                        }
                    }
                });
            });
        });
        
        observer.observe(document.body || document.documentElement, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['src', 'href', 'data-src']
        });
        
        console.log('[TokenMonitor] Token监控已启动');
    })();
    """
    await page.add_init_script(script=monitor_script)


class DeepJx2s0TokenAnalyzer:
    """深度分析 jx.2s0.cn token 生成器"""
    
    def __init__(self):
        self.target_url = "https://jx.2s0.cn/player/?url=https://v.youku.com/v_show/id_XMTA0MTc5NzI4.html"
        self.m3u8_urls = []
        self.network_requests = []
        self.js_sources = []
        self.monitor_data = {}
        self.token_generation_logic = {}
        
    async def analyze(self):
        """执行完整分析流程"""
        chrome_process = None
        user_data_dir = None
        
        try:
            print("=" * 80)
            print("🔍 深度分析 jx.2s0.cn token 生成方式")
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
                
                # 注入token监控代码
                print("\n[步骤2] 注入token监控代码...")
                await inject_token_monitor(page)
                
                # 监听网络请求
                print("\n[步骤3] 设置网络请求监听...")
                await self._setup_network_listeners(page)
                
                # 监听控制台消息
                page.on('console', lambda msg: print(f"[Console] {msg.text}"))
                
                # 访问目标页面
                print(f"\n[步骤4] 访问目标页面: {self.target_url}")
                await page.goto(self.target_url, wait_until='domcontentloaded', timeout=60000)
                
                # 等待页面加载
                print("\n[步骤5] 等待页面加载和视频初始化...")
                await asyncio.sleep(5)
                
                # 尝试等待视频播放器加载
                try:
                    await page.wait_for_selector('video, iframe, [class*="player"], [id*="player"]', timeout=10000)
                except:
                    print("⚠️  未找到视频播放器元素，继续分析...")
                
                # 等待更多网络请求
                print("\n[步骤6] 等待m3u8请求和token生成...")
                await asyncio.sleep(15)
                
                # 获取监控数据
                print("\n[步骤7] 获取监控数据...")
                await self._get_monitor_data(page)
                
                # 分析JavaScript代码
                print("\n[步骤8] 分析JavaScript代码...")
                await self._analyze_javascript_deep(page)
                
                # 尝试提取token生成函数
                print("\n[步骤9] 尝试提取token生成函数...")
                await self._extract_token_functions(page)
                
                # 分析token结构
                print("\n[步骤10] 分析token结构...")
                self._analyze_token_structure()
                
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
                'headers': dict(request.headers),
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
            
            # 如果是JavaScript文件，保存内容
            if url.endswith('.js') or 'javascript' in response.headers.get('content-type', ''):
                try:
                    content = await response.text()
                    if 'token' in content.lower() or 'm3u8' in content.lower() or 'cachem3u8' in content.lower():
                        self.js_sources.append({
                            'url': url,
                            'content': content[:50000],  # 限制大小
                            'size': len(content)
                        })
                        print(f"\n📜 发现相关JS文件: {url} ({len(content)} 字符)")
                except:
                    pass
        
        page.on('request', handle_request)
        page.on('response', handle_response)
    
    async def _get_monitor_data(self, page: Page):
        """获取监控数据"""
        try:
            monitor_data = await page.evaluate("""
                () => {
                    if (window.__tokenMonitor) {
                        return {
                            m3u8Urls: window.__tokenMonitor.m3u8Urls,
                            tokenGenerations: window.__tokenMonitor.tokenGenerations,
                            urlConstructions: window.__tokenMonitor.urlConstructions,
                            apiCalls: window.__tokenMonitor.apiCalls,
                            configData: window.__tokenMonitor.configData
                        };
                    }
                    return null;
                }
            """)
            
            if monitor_data:
                self.monitor_data = monitor_data
                print(f"✅ 获取到监控数据:")
                print(f"   m3u8 URLs: {len(monitor_data.get('m3u8Urls', []))}")
                print(f"   URL构造: {len(monitor_data.get('urlConstructions', []))}")
                print(f"   API调用: {len(monitor_data.get('apiCalls', []))}")
                if monitor_data.get('configData'):
                    print(f"   Config数据: {monitor_data.get('configData')}")
        except Exception as e:
            print(f"⚠️  获取监控数据失败: {e}")
    
    async def _analyze_javascript_deep(self, page: Page):
        """深度分析JavaScript代码"""
        try:
            # 获取所有脚本
            scripts = await page.evaluate("""
                () => {
                    const scripts = [];
                    document.querySelectorAll('script').forEach(script => {
                        if (script.src) {
                            scripts.push({ type: 'external', src: script.src });
                        } else if (script.textContent) {
                            scripts.push({ 
                                type: 'inline', 
                                content: script.textContent.substring(0, 5000) 
                            });
                        }
                    });
                    return scripts;
                }
            """)
            
            print(f"\n📜 发现 {len(scripts)} 个脚本标签")
            
            # 查找包含token/m3u8的脚本
            for script in scripts:
                if script['type'] == 'inline':
                    content = script.get('content', '')
                    if any(keyword in content.lower() for keyword in ['token', 'm3u8', 'cachem3u8', '2s0.cn']):
                        print(f"   ✅ 内联脚本包含相关代码")
                        # 提取关键代码片段
                        lines = content.split('\n')
                        for i, line in enumerate(lines):
                            if any(keyword in line.lower() for keyword in ['token', 'm3u8', 'cachem3u8']):
                                print(f"      行 {i+1}: {line.strip()[:150]}")
        
        except Exception as e:
            print(f"⚠️  JavaScript深度分析失败: {e}")
    
    async def _extract_token_functions(self, page: Page):
        """提取token生成函数"""
        try:
            # 尝试查找所有可能的token生成函数
            func_names = [
                'getToken', 'generateToken', 'createToken', 'makeToken',
                'getM3u8Token', 'buildToken', 'token', 'YKQ',
                'video', 'play', 'load', 'init'
            ]
            
            print("\n🔍 查找token相关函数...")
            for func_name in func_names:
                try:
                    exists = await page.evaluate(f"""
                        () => {{
                            if (typeof window.{func_name} === 'function') {{
                                return window.{func_name}.toString().substring(0, 500);
                            }}
                            return null;
                        }}
                    """)
                    if exists:
                        print(f"   ✅ 发现函数: {func_name}")
                        print(f"   代码片段: {exists[:200]}...")
                        self.token_generation_logic[func_name] = exists
                except:
                    pass
            
            # 查找YKQ对象
            try:
                ykq = await page.evaluate("""
                    () => {
                        if (window.YKQ) {
                            return {
                                methods: Object.keys(window.YKQ).filter(k => typeof window.YKQ[k] === 'function'),
                                properties: Object.keys(window.YKQ).filter(k => typeof window.YKQ[k] !== 'function')
                            };
                        }
                        return null;
                    }
                """)
                if ykq:
                    print(f"\n🌐 YKQ对象:")
                    print(f"   方法: {ykq.get('methods', [])}")
                    print(f"   属性: {ykq.get('properties', [])}")
                    self.token_generation_logic['YKQ'] = ykq
            except:
                pass
        
        except Exception as e:
            print(f"⚠️  提取token函数失败: {e}")
    
    def _analyze_token_structure(self):
        """分析token结构"""
        if not self.m3u8_urls:
            return
        
        token = self.m3u8_urls[0]['token']
        print(f"\n🔬 Token结构分析:")
        print(f"   长度: {len(token)} 字符")
        print(f"   完整内容: {token}")
        
        # 分析字符集
        hex_chars = set('0123456789abcdefABCDEF')
        token_chars = set(token)
        is_hex = token_chars.issubset(hex_chars)
        
        print(f"\n   字符集分析:")
        print(f"   是否为十六进制: {is_hex}")
        print(f"   唯一字符数: {len(token_chars)}")
        print(f"   字符集: {sorted(list(token_chars))[:30]}")
        
        # 尝试解码
        if is_hex:
            try:
                decoded = bytes.fromhex(token).decode('utf-8', errors='ignore')
                print(f"\n   十六进制解码结果: {decoded[:200]}")
            except:
                print(f"\n   十六进制解码失败")
        
        # 分析URL结构
        if self.m3u8_urls:
            url = self.m3u8_urls[0]['url']
            parsed = urlparse(url)
            print(f"\n   URL结构:")
            print(f"   域名: {parsed.netloc}")
            print(f"   路径: {parsed.path}")
            print(f"   查询参数: {parsed.query[:100]}...")
    
    def _print_results(self):
        """打印分析结果"""
        print("\n1️⃣  m3u8 URL和Token:")
        if self.m3u8_urls:
            for i, item in enumerate(self.m3u8_urls, 1):
                print(f"\n   [{i}] URL: {item['url']}")
                print(f"       Token: {item['token']}")
        else:
            print("   ❌ 未找到m3u8 URL")
        
        print(f"\n2️⃣  监控数据:")
        if self.monitor_data:
            print(f"   m3u8 URLs: {len(self.monitor_data.get('m3u8Urls', []))}")
            print(f"   URL构造记录: {len(self.monitor_data.get('urlConstructions', []))}")
            print(f"   API调用: {len(self.monitor_data.get('apiCalls', []))}")
            if self.monitor_data.get('configData'):
                print(f"   Config数据: {self.monitor_data.get('configData')}")
        
        print(f"\n3️⃣  JavaScript源文件:")
        if self.js_sources:
            for js in self.js_sources[:5]:
                print(f"   {js['url']} ({js['size']} 字符)")
        else:
            print("   ❌ 未找到相关JS文件")
        
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
            'monitor_data': self.monitor_data,
            'network_requests_count': len(self.network_requests),
            'm3u8_requests': [r for r in self.network_requests if '.m3u8' in r['url']],
            'token_requests': [r for r in self.network_requests if 'token=' in r['url']],
            'js_sources_count': len(self.js_sources),
            'js_sources': [{'url': js['url'], 'size': js['size']} for js in self.js_sources],
            'token_generation_logic': self.token_generation_logic,
            'timestamp': time.time()
        }
        
        output_file = 'jx2s0_token_deep_analysis.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 分析结果已保存到: {output_file}")


async def main():
    """主函数"""
    analyzer = DeepJx2s0TokenAnalyzer()
    await analyzer.analyze()


if __name__ == '__main__':
    asyncio.run(main())

