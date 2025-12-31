"""
捕获 jx.m3u8.tv API参数
使用Playwright监听网络请求，捕获API调用和关键参数
"""

import asyncio
import json
import re
import subprocess
import tempfile
import socket
import time
import os
import shutil
from typing import Optional, Dict, List
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from urllib.parse import urlparse, parse_qs


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
            print("❌ 未找到Chrome浏览器")
            return None, None, None
    
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


def cleanup_user_data(user_data_dir):
    """删除临时用户数据目录"""
    if user_data_dir and os.path.exists(user_data_dir):
        shutil.rmtree(user_data_dir, ignore_errors=True)


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


class JxM3u8TvParamsCapturer:
    """jx.m3u8.tv API参数捕获器"""
    
    def __init__(self):
        self.api_calls = []
        self.captured_params = []
        self.m3u8_urls = []
        self.config_objects = []
    
    async def setup_page(self, page: Page):
        """设置页面，监听网络请求"""
        print("🔧 设置网络请求监听...")
        
        async def handle_request(request):
            """处理请求"""
            url = request.url
            
            # 检查是否是API请求或相关请求
            if any(keyword in url for keyword in [
                'api', 'jiexi', 'parse', 'play', 'video', 
                'm3u8', 'cloud', 'cdn', 'json'
            ]):
                try:
                    url_obj = request.url
                    # 提取URL参数
                    params = {}
                    if '?' in url_obj:
                        parsed_url = urlparse(url_obj)
                        query_string = parsed_url.query
                        params = dict(parse_qs(query_string))
                        # 将列表值转换为单个值
                        params = {k: v[0] if len(v) == 1 else v for k, v in params.items()}
                    
                    call_info = {
                        'url': url_obj,
                        'method': request.method,
                        'headers': dict(request.headers),
                        'params': params,
                        'timestamp': asyncio.get_event_loop().time()
                    }
                    
                    self.api_calls.append(call_info)
                    
                    print(f"\n🔍 [请求] 捕获API调用:")
                    print(f"   URL: {url_obj[:150]}...")
                    print(f"   方法: {request.method}")
                    if params:
                        print(f"   参数: {json.dumps(params, indent=6, ensure_ascii=False)[:300]}")
                    
                    # 提取关键参数
                    key_params = {}
                    for key in ['z', 's1ig', 'g', 'jx', 'url', 'code', 'sign', 'token', 'key', 't', 'time', 'timestamp']:
                        if key in params:
                            key_params[key] = params[key]
                    
                    if key_params:
                        self.captured_params.append({
                            **key_params,
                            'url': url_obj,
                            'timestamp': call_info['timestamp']
                        })
                        print(f"   ✅ 捕获到关键参数:")
                        for k, v in key_params.items():
                            print(f"      {k}: {v}")
                
                except Exception as e:
                    print(f"   ⚠️ 处理请求失败: {e}")
        
        async def handle_response(response):
            """处理响应"""
            url = response.url
            
            # 检查是否是API响应或m3u8文件
            if any(keyword in url for keyword in [
                'api', 'jiexi', 'parse', 'play', 'video',
                'm3u8', 'cloud', 'cdn', 'json'
            ]):
                try:
                    status = response.status
                    content_type = response.headers.get('content-type', '')
                    
                    print(f"\n📡 [响应] API响应:")
                    print(f"   URL: {url[:150]}...")
                    print(f"   状态码: {status}")
                    print(f"   Content-Type: {content_type}")
                    
                    # 检查是否是m3u8文件
                    if '.m3u8' in url or 'm3u8' in content_type.lower():
                        self.m3u8_urls.append(url)
                        print(f"   ✅ 发现m3u8文件: {url}")
                    
                    # 尝试读取响应内容
                    try:
                        content = await response.text()
                        print(f"   响应长度: {len(content)} 字符")
                        
                        # 检查是否是JSON格式
                        if content.strip().startswith('{') or content.strip().startswith('['):
                            print(f"   ✅ 响应是JSON格式")
                            try:
                                json_data = json.loads(content)
                                print(f"   ✅ JSON解析成功")
                                
                                # 检查是否包含m3u8链接
                                m3u8_urls = self.find_m3u8_in_json(json_data)
                                if m3u8_urls:
                                    print(f"   ✅ 找到 {len(m3u8_urls)} 个m3u8链接:")
                                    for m3u8_url in m3u8_urls:
                                        print(f"      - {m3u8_url[:100]}...")
                                        self.m3u8_urls.append(m3u8_url)
                                
                                # 检查是否包含ConFig对象
                                config = self.find_config_in_json(json_data)
                                if config:
                                    print(f"   ✅ 找到ConFig对象")
                                    self.config_objects.append(config)
                                    
                            except json.JSONDecodeError:
                                pass
                        
                        # 检查是否是m3u8内容
                        elif '#EXTM3U' in content:
                            print(f"   ✅ 响应是m3u8文件内容")
                            self.m3u8_urls.append(url)
                        
                        # 显示内容预览
                        preview = content[:300].replace('\n', '\\n')
                        print(f"   内容预览: {preview}...")
                        
                    except Exception as e:
                        print(f"   ⚠️ 读取响应失败: {e}")
                
                except Exception as e:
                    print(f"   ⚠️ 处理响应失败: {e}")
        
        page.on('request', handle_request)
        page.on('response', handle_response)
    
    def find_m3u8_in_json(self, obj, path=''):
        """递归查找JSON中的m3u8链接"""
        m3u8_urls = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                m3u8_urls.extend(self.find_m3u8_in_json(v, f"{path}.{k}"))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                m3u8_urls.extend(self.find_m3u8_in_json(item, f"{path}[{i}]"))
        elif isinstance(obj, str):
            if '.m3u8' in obj and obj.startswith('http'):
                m3u8_urls.append(obj)
        return m3u8_urls
    
    def find_config_in_json(self, obj):
        """查找JSON中的ConFig对象"""
        if isinstance(obj, dict):
            # 检查是否是ConFig对象
            if 'url' in obj and 'config' in obj:
                return obj
            # 递归查找
            for v in obj.values():
                config = self.find_config_in_json(v)
                if config:
                    return config
        elif isinstance(obj, list):
            for item in obj:
                config = self.find_config_in_json(item)
                if config:
                    return config
        return None
    
    async def inject_analysis_script(self, page: Page):
        """注入参数分析脚本"""
        print("🔧 注入参数分析脚本...")
        
        analysis_script = """
        (function() {
            'use strict';
            
            console.log('🔍 参数分析脚本已注入');
            
            // Hook fetch
            const originalFetch = window.fetch;
            window.fetch = function(...args) {
                const url = args[0];
                if (typeof url === 'string') {
                    console.log('\\n🔍 [Fetch Hook] 捕获请求:', url);
                    
                    // 提取参数
                    try {
                        const urlObj = new URL(url);
                        const params = Object.fromEntries(urlObj.searchParams);
                        console.log('   参数:', params);
                        
                        // 保存到window对象供Python读取
                        if (!window._capturedApiParams) {
                            window._capturedApiParams = [];
                        }
                        window._capturedApiParams.push({
                            url: url,
                            params: params,
                            method: 'fetch',
                            timestamp: new Date().toISOString()
                        });
                    } catch (e) {
                        console.error('   解析URL失败:', e);
                    }
                }
                return originalFetch.apply(this, args);
            };
            
            // Hook XMLHttpRequest
            const originalXHROpen = XMLHttpRequest.prototype.open;
            XMLHttpRequest.prototype.open = function(method, url, ...args) {
                if (typeof url === 'string') {
                    console.log('\\n🔍 [XHR Hook] 捕获请求:', url);
                    
                    try {
                        const urlObj = new URL(url);
                        const params = Object.fromEntries(urlObj.searchParams);
                        console.log('   参数:', params);
                        
                        if (!window._capturedApiParams) {
                            window._capturedApiParams = [];
                        }
                        window._capturedApiParams.push({
                            url: url,
                            params: params,
                            method: method,
                            timestamp: new Date().toISOString()
                        });
                    } catch (e) {
                        console.error('   解析URL失败:', e);
                    }
                }
                return originalXHROpen.apply(this, [method, url, ...args]);
            };
            
            // Hook XMLHttpRequest send 以捕获POST数据
            const originalXHRSend = XMLHttpRequest.prototype.send;
            XMLHttpRequest.prototype.send = function(data) {
                if (data && typeof data === 'string') {
                    try {
                        const jsonData = JSON.parse(data);
                        console.log('\\n🔍 [XHR POST] 捕获POST数据:', jsonData);
                        
                        if (!window._capturedPostData) {
                            window._capturedPostData = [];
                        }
                        window._capturedPostData.push({
                            data: jsonData,
                            timestamp: new Date().toISOString()
                        });
                    } catch (e) {
                        // 不是JSON，忽略
                    }
                }
                return originalXHRSend.apply(this, arguments);
            };
            
            // 监听window对象的变化（如ConFig）
            let configCheckInterval = setInterval(() => {
                if (window.ConFig) {
                    console.log('\\n🔍 [ConFig] 发现ConFig对象:', window.ConFig);
                    if (!window._capturedConfigs) {
                        window._capturedConfigs = [];
                    }
                    window._capturedConfigs.push({
                        config: window.ConFig,
                        timestamp: new Date().toISOString()
                    });
                }
            }, 1000);
            
            // 10秒后停止检查
            setTimeout(() => {
                clearInterval(configCheckInterval);
            }, 30000);
            
            console.log('✅ 参数分析脚本已就绪');
        })();
        """
        
        await page.add_init_script(analysis_script)
    
    async def analyze_js_code(self, page: Page) -> Dict:
        """分析JavaScript代码，查找参数生成逻辑"""
        print("\n🔍 分析JavaScript代码...")
        
        try:
            # 获取所有script标签的内容
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
            
            print(f"   📋 找到 {len(scripts_info)} 个script标签")
            
            # 分析内联脚本
            param_patterns = {
                'z': r'[zZ]\s*[:=]\s*["\']?([a-f0-9]{32,})["\']?',
                's1ig': r's1ig\s*[:=]\s*["\']?(\d+)["\']?',
                'g': r'[gG]\s*[:=]\s*["\']?([a-z0-9]+\.[a-z0-9]+)["\']?',
                'sign': r'sign\s*[:=]\s*["\']?([a-f0-9]+)["\']?',
                'token': r'token\s*[:=]\s*["\']?([a-zA-Z0-9_-]+)["\']?',
                'md5': r'md5\s*\([^)]+\)',
                'hash': r'hash\s*\([^)]+\)',
                'encrypt': r'encrypt\s*\([^)]+\)',
                'config': r'ConFig\s*[:=]\s*({[^}]+})',
                'api_url': r'["\'](https?://[^"\']+api[^"\']+)["\']',
            }
            
            found_patterns = {}
            
            for script in scripts_info:
                if script['type'] == 'inline' and script['content']:
                    content = script['content']
                    
                    for pattern_name, pattern in param_patterns.items():
                        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
                        if matches:
                            if pattern_name not in found_patterns:
                                found_patterns[pattern_name] = []
                            found_patterns[pattern_name].extend(matches[:5])  # 只保存前5个
                            
                            # 显示上下文
                            for match in matches[:2]:  # 只显示前2个
                                match_str = match if isinstance(match, str) else str(match)[:100]
                                match_pos = content.find(match_str)
                                if match_pos >= 0:
                                    context_start = max(0, match_pos - 100)
                                    context_end = min(len(content), match_pos + len(match_str) + 100)
                                    context = content[context_start:context_end]
                                    print(f"   ✅ 找到{pattern_name}模式: {match_str[:100]}...")
                                    print(f"      上下文: {context[:200]}...")
            
            return found_patterns
        
        except Exception as e:
            print(f"   ⚠️ 分析JavaScript代码失败: {e}")
            return {}
    
    async def extract_page_info(self, page: Page) -> Dict:
        """提取页面信息"""
        print("\n🔍 提取页面信息...")
        
        try:
            # 提取iframe信息
            iframes = await page.evaluate("""
                () => {
                    const iframes = [];
                    document.querySelectorAll('iframe').forEach(iframe => {
                        iframes.push({
                            src: iframe.src,
                            id: iframe.id,
                            name: iframe.name
                        });
                    });
                    return iframes;
                }
            """)
            
            # 提取ConFig对象
            config = None
            try:
                config = await page.evaluate("() => window.ConFig || null")
            except:
                pass
            
            # 提取其他全局变量
            global_vars = {}
            try:
                # 尝试提取一些常见的全局变量
                for var_name in ['ConFig', 'config', 'apiUrl', 'api_url', 'baseUrl', 'base_url']:
                    try:
                        value = await page.evaluate(f"() => window.{var_name} || null")
                        if value:
                            global_vars[var_name] = value
                    except:
                        pass
            except:
                pass
            
            # 从JavaScript中获取捕获的参数
            captured_from_js = []
            try:
                captured_from_js = await page.evaluate("() => window._capturedApiParams || []")
            except:
                pass
            
            # 获取捕获的POST数据
            captured_post_data = []
            try:
                captured_post_data = await page.evaluate("() => window._capturedPostData || []")
            except:
                pass
            
            # 获取捕获的ConFig
            captured_configs = []
            try:
                captured_configs = await page.evaluate("() => window._capturedConfigs || []")
            except:
                pass
            
            return {
                'iframes': iframes,
                'config': config,
                'global_vars': global_vars,
                'captured_from_js': captured_from_js,
                'captured_post_data': captured_post_data,
                'captured_configs': captured_configs
            }
        
        except Exception as e:
            print(f"   ⚠️ 提取页面信息失败: {e}")
            return {}
    
    async def capture_params(self, video_url: str, use_standalone_browser: bool = True) -> Optional[Dict]:
        """捕获API参数
        
        Args:
            video_url: 要解析的视频URL
            use_standalone_browser: 是否使用独立浏览器（推荐，可绕过反爬虫）
        """
        print("=" * 60)
        print("捕获 jx.m3u8.tv API参数")
        print("=" * 60)
        print(f"目标视频: {video_url}")
        print(f"使用独立浏览器: {use_standalone_browser}")
        
        chrome_process = None
        user_data_dir = None
        
        try:
            if use_standalone_browser:
                # 使用独立浏览器启动
                print(f"\n[步骤0] 启动独立Chrome浏览器...")
                chrome_process, debug_port, user_data_dir = launch_chrome()
                if not chrome_process or not debug_port:
                    print("❌ 启动独立Chrome浏览器失败，回退到Playwright启动方式")
                    use_standalone_browser = False
                else:
                    print(f"   ✅ Chrome浏览器已启动，调试端口: {debug_port}")
            
            async with async_playwright() as p:
                if use_standalone_browser:
                    # 连接到已启动的Chrome浏览器
                    browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{debug_port}")
                    print(f"   ✅ 成功连接到Chrome浏览器")
                else:
                    # 使用Playwright启动浏览器
                    browser = await p.chromium.launch(
                        headless=False,
                        args=[
                            '--disable-blink-features=AutomationControlled',
                            '--disable-dev-shm-usage',
                            '--no-sandbox',
                        ]
                    )
                
                # 创建上下文
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    locale='zh-CN',
                )
                
                # 添加反爬虫脚本
                await add_stealth_script(context)
                
                page = await context.new_page()
                
                # 注入分析脚本
                await self.inject_analysis_script(page)
                
                # 设置网络监听
                await self.setup_page(page)
                
                try:
                    # 访问解析网站
                    parser_url = f"https://jx.2s0.cn/player/?url={video_url}"
                    print(f"\n[步骤1] 访问解析网站...")
                    print(f"   URL: {parser_url}")
                    
                    await page.goto(parser_url, wait_until='domcontentloaded', timeout=60000)
                    print(f"   ✅ 页面加载完成")
                    
                    # 等待页面执行
                    print(f"\n[步骤2] 等待JavaScript执行...")
                    await asyncio.sleep(10)
                    
                    # 尝试触发视频加载（如果有播放按钮）
                    try:
                        # 查找播放按钮或视频元素
                        play_selectors = [
                            'button', '.play-btn', '[class*="play"]', 
                            'video', '.video-player', '#player'
                        ]
                        for selector in play_selectors:
                            try:
                                element = await page.query_selector(selector)
                                if element:
                                    print(f"   💡 找到元素 ({selector})，尝试点击...")
                                    await element.click()
                                    await asyncio.sleep(3)
                                    break
                            except:
                                continue
                    except:
                        pass
                    
                    # 等待网络请求
                    print(f"\n[步骤3] 等待API调用...")
                    await asyncio.sleep(15)
                    
                    # 提取页面信息
                    page_info = await self.extract_page_info(page)
                    
                    # 从JavaScript中获取捕获的参数
                    if page_info.get('captured_from_js'):
                        print(f"   ✅ 从JavaScript中获取到 {len(page_info['captured_from_js'])} 个API调用")
                        for call in page_info['captured_from_js']:
                            params = call.get('params', {})
                            key_params = {}
                            for key in ['z', 's1ig', 'g', 'jx', 'url', 'code', 'sign', 'token', 'key', 't', 'time']:
                                if key in params:
                                    key_params[key] = params[key]
                            
                            if key_params:
                                self.captured_params.append({
                                    **key_params,
                                    'url': call.get('url'),
                                    'timestamp': call.get('timestamp')
                                })
                    
                    # 分析JavaScript代码
                    js_analysis = await self.analyze_js_code(page)
                    
                    # 汇总结果
                    result = {
                        'video_url': video_url,
                        'parser_url': parser_url,
                        'api_calls': self.api_calls,
                        'captured_params': self.captured_params,
                        'm3u8_urls': list(set(self.m3u8_urls)),  # 去重
                        'config_objects': self.config_objects,
                        'page_info': page_info,
                        'js_analysis': js_analysis
                    }
                    
                    # 保存结果
                    output_file = 'captured_jx_m3u8_tv_params.json'
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
                    print(f"\n✅ 捕获结果已保存到: {output_file}")
                    
                    # 打印总结
                    print("\n" + "=" * 60)
                    print("📊 捕获总结")
                    print("=" * 60)
                    
                    if self.captured_params:
                        print(f"\n✅ 成功捕获 {len(self.captured_params)} 组参数:")
                        for i, params in enumerate(self.captured_params, 1):
                            print(f"\n[组 {i}]")
                            for k, v in params.items():
                                if k not in ['url', 'timestamp']:
                                    print(f"   {k}: {v}")
                            if params.get('url'):
                                print(f"   URL: {params['url'][:100]}...")
                        
                        # 提取最新的参数
                        latest_params = self.captured_params[-1] if self.captured_params else {}
                        print(f"\n💡 最新参数（可用于更新脚本）:")
                        for k, v in latest_params.items():
                            if k not in ['url', 'timestamp']:
                                print(f"   {k} = \"{v}\"")
                    else:
                        print(f"\n⚠️ 未捕获到参数")
                        print(f"   💡 可能的原因:")
                        print(f"      1. 页面未触发API调用")
                        print(f"      2. API调用被拦截")
                        print(f"      3. 需要手动操作页面")
                        print(f"      4. 参数在JavaScript中动态生成")
                    
                    if self.m3u8_urls:
                        print(f"\n✅ 找到 {len(self.m3u8_urls)} 个m3u8链接:")
                        for i, m3u8_url in enumerate(self.m3u8_urls[:5], 1):  # 只显示前5个
                            print(f"   [{i}] {m3u8_url[:100]}...")
                    
                    if self.config_objects:
                        print(f"\n✅ 找到 {len(self.config_objects)} 个ConFig对象")
                        for i, config in enumerate(self.config_objects[:2], 1):  # 只显示前2个
                            print(f"   [ConFig {i}]: {json.dumps(config, indent=4, ensure_ascii=False)[:300]}...")
                    
                    if page_info.get('iframes'):
                        print(f"\n📋 找到 {len(page_info['iframes'])} 个iframe:")
                        for i, iframe in enumerate(page_info['iframes'], 1):
                            print(f"   [iframe {i}]: {iframe.get('src', 'N/A')}")
                    
                    if js_analysis:
                        print(f"\n🔍 JavaScript代码分析结果:")
                        for pattern_name, matches in js_analysis.items():
                            if matches:
                                print(f"   {pattern_name}: 找到 {len(matches)} 个匹配")
                    
                    # 保持浏览器打开一段时间
                    print(f"\n⏸️ 浏览器将保持打开30秒，您可以手动检查...")
                    await asyncio.sleep(30)
                    
                    await context.close()
                    await browser.close()
                    
                    return result
                
                except Exception as e:
                    print(f"\n❌ 捕获过程中发生错误: {e}")
                    import traceback
                    traceback.print_exc()
                    await context.close()
                    await browser.close()
                    return None
        
        finally:
            # 清理独立浏览器进程
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
                cleanup_user_data(user_data_dir)


async def main():
    """主函数"""
    video_url = "https://v.youku.com/v_show/id_XMTA0MTc5NzI4.html"
    
    capturer = JxM3u8TvParamsCapturer()
    # 使用独立浏览器启动（推荐，可绕过反爬虫）
    result = await capturer.capture_params(video_url, use_standalone_browser=True)
    
    if result:
        print("\n✅ 参数捕获完成！")
        print("\n💡 下一步:")
        print("   1. 查看 captured_jx_m3u8_tv_params.json 文件")
        print("   2. 分析捕获的参数，理解API调用方式")
        print("   3. 编写直接调用API的脚本")
    else:
        print("\n⚠️ 参数捕获失败，请检查:")
        print("   1. 网络连接是否正常")
        print("   2. 解析网站是否可以访问")
        print("   3. 是否需要手动操作页面触发API调用")


if __name__ == '__main__':
    asyncio.run(main())

