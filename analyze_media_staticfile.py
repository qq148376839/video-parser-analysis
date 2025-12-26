"""
直接分析 media.staticfile.link 解析接口
跳过 getdata.staticfile.link 的中间层，直接访问最终播放页面
"""

import asyncio
import json
import subprocess
import tempfile
import socket
import time
import os
import re
from typing import Optional
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
            print("❌ 未找到Chrome浏览器，请手动指定chrome_path")
            return None, None, None
    
    debug_port = get_free_port()
    temp_user_data_dir = tempfile.mkdtemp(prefix="chrome_automation_")
    
    print(f"🚀 启动独立Chrome浏览器...")
    print(f"   调试端口: {debug_port}")
    
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
        
        print(f"⏳ 等待Chrome调试端口 {debug_port} 开放...")
        for i in range(30):
            try:
                s = socket.create_connection(('127.0.0.1', debug_port), timeout=1.0)
                s.close()
                print(f"✅ 端口 {debug_port} 已开放")
                return chrome_process, debug_port, temp_user_data_dir
            except Exception:
                if chrome_process.poll() is not None:
                    print("❌ Chrome进程已退出")
                    return None, None, None
                time.sleep(1)
        
        print(f"❌ 端口 {debug_port} 在30秒内未开放")
        chrome_process.terminate()
        return None, None, None
        
    except Exception as e:
        print(f"❌ 启动Chrome失败: {e}")
        return None, None, None


def cleanup_user_data(user_data_dir):
    """删除临时用户数据目录"""
    if user_data_dir and os.path.exists(user_data_dir):
        import shutil
        shutil.rmtree(user_data_dir, ignore_errors=True)


async def add_stealth_script(context: BrowserContext):
    """添加反爬虫脚本（增强版）"""
    stealth_script = """
    (function() {
        // 隐藏webdriver属性
        Object.defineProperty(navigator, 'webdriver', { 
            get: () => undefined,
            configurable: true
        });
        
        // 删除webdriver相关属性
        delete navigator.__proto__.webdriver;
        
        // 设置平台信息
        Object.defineProperty(navigator, 'platform', { 
            get: () => 'Win32',
            configurable: true
        });
        
        // 设置语言
        Object.defineProperty(navigator, 'languages', { 
            get: () => ['zh-CN', 'zh', 'en'],
            configurable: true
        });
        
        // 隐藏自动化特征
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Object;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy;
        
        // 覆盖Chrome对象
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {}
        };
        
        // 禁用debugger
        const originalDebugger = window.debugger;
        window.debugger = function() {};
        
        // 覆盖console方法
        const noop = () => {};
        console.debug = noop;
        
        // 禁用DevTools检测
        let devtools = {open: false, orientation: null};
        const threshold = 160;
        
        // 覆盖DevTools检测
        Object.defineProperty(window, 'devtools', {
            get: () => ({open: false}),
            set: () => {},
            configurable: true
        });
        
        // 禁用toString检测
        const originalToString = Function.prototype.toString;
        Function.prototype.toString = function() {
            if (this === originalDebugger || this === window.debugger) {
                return 'function debugger() { [native code] }';
            }
            return originalToString.apply(this, arguments);
        };
        
        // 覆盖权限查询
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // 覆盖插件检测
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
            configurable: true
        });
        
        // 覆盖硬件并发
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 8,
            configurable: true
        });
        
        // 覆盖设备内存
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => 8,
            configurable: true
        });
        
        // 禁用无限debugger循环
        const dbg = window.debugger;
        window.debugger = noop;
        
        // 覆盖window.outerHeight/outerWidth检测
        const originalOuterHeight = Object.getOwnPropertyDescriptor(window, 'outerHeight');
        const originalOuterWidth = Object.getOwnPropertyDescriptor(window, 'outerWidth');
        
        // 监听并阻止DevTools检测
        setInterval(() => {
            if (window.outerHeight - window.innerHeight > threshold || 
                window.outerWidth - window.innerWidth > threshold) {
                // 阻止检测
            }
        }, 500);
        
        console.log('🔐 增强反检测脚本已加载');
    })();
    """
    await context.add_init_script(script=stealth_script)


class MediaStaticFileAnalyzer:
    """分析 media.staticfile.link 解析接口"""
    
    def __init__(self):
        self.m3u8_urls = []
        self.api_responses = []
    
    async def analyze_page(self, page: Page, url: str) -> Optional[dict]:
        """分析页面"""
        print(f"\n[步骤1] 访问页面...")
        print(f"   URL: {url}")
        
        # 监听网络请求和响应
        network_data = []
        m3u8_found = []
        
        async def handle_response(response):
            resp_url = response.url
            content_type = response.headers.get('content-type', '').lower()
            
            # 检查API响应
            if ('api' in resp_url.lower() or 'php' in resp_url.lower() or 
                'json' in content_type or 'dmku.byteamone.cn' in resp_url.lower()):
                try:
                    content = await response.text()
                    network_data.append({
                        'url': resp_url,
                        'status': response.status,
                        'content_type': content_type,
                        'content': content[:10000]  # 保存前10000字符
                    })
                    
                    # 检查m3u8链接
                    if 'm3u8' in content.lower():
                        m3u8_patterns = [
                            r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
                            r'["\']([^"\']+\.m3u8[^"\']*)["\']',
                        ]
                        for pattern in m3u8_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            for match in matches:
                                url_match = match if isinstance(match, str) else match[0] if match else None
                                if url_match and url_match.startswith('http') and url_match not in m3u8_found:
                                    m3u8_found.append(url_match)
                                    print(f"   ✅ 在响应中找到m3u8链接: {url_match}")
                    
                    # 尝试解析JSON
                    if 'json' in content_type:
                        try:
                            json_data = json.loads(content)
                            print(f"   ✅ JSON响应: {resp_url}")
                            # 递归查找m3u8或url
                            def find_urls(obj, path=""):
                                urls = []
                                if isinstance(obj, dict):
                                    for key, value in obj.items():
                                        urls.extend(find_urls(value, f"{path}.{key}"))
                                elif isinstance(obj, list):
                                    for i, item in enumerate(obj):
                                        urls.extend(find_urls(item, f"{path}[{i}]"))
                                elif isinstance(obj, str):
                                    if '.m3u8' in obj and obj.startswith('http'):
                                        urls.append({'path': path, 'url': obj, 'type': 'm3u8'})
                                    elif ('url' in path.lower() or 'link' in path.lower()) and obj.startswith('http'):
                                        urls.append({'path': path, 'url': obj, 'type': 'url'})
                                return urls
                            
                            found_urls = find_urls(json_data)
                            if found_urls:
                                for item in found_urls:
                                    print(f"      📍 {item['type']}: {item['url']}")
                                    if item['type'] == 'm3u8' and item['url'] not in m3u8_found:
                                        m3u8_found.append(item['url'])
                        except:
                            pass
                except:
                    pass
        
        page.on('response', handle_response)
        
        try:
            # 设置额外的请求头
            await page.set_extra_http_headers({
                'Referer': 'https://jx.playerjy.com/',
                'Origin': 'https://jx.playerjy.com'
            })
            
            # 访问页面
            await page.goto(url, wait_until='domcontentloaded', timeout=90000)
            print(f"   ✅ 页面加载完成")
            
            # 检查页面是否显示错误
            page_text = await page.evaluate("() => document.body.innerText || ''")
            if '请求异常' in page_text or '请稍后重试' in page_text:
                print(f"   ⚠️ 页面显示错误信息: {page_text[:100]}")
                print(f"   💡 可能检测到自动化工具，尝试绕过...")
                
                # 尝试多种绕过方法
                # 方法1: 等待并重新加载
                await asyncio.sleep(5)
                try:
                    await page.reload(wait_until='networkidle', timeout=60000)
                    await asyncio.sleep(10)
                except:
                    pass
                
                # 方法2: 模拟用户交互
                try:
                    # 移动鼠标
                    await page.mouse.move(100, 100)
                    await asyncio.sleep(0.5)
                    await page.mouse.move(200, 200)
                    await asyncio.sleep(0.5)
                    
                    # 点击页面
                    await page.click('body')
                    await asyncio.sleep(2)
                    
                    # 滚动页面
                    await page.evaluate("window.scrollTo(0, 100)")
                    await asyncio.sleep(1)
                    await page.evaluate("window.scrollTo(0, 0)")
                    await asyncio.sleep(2)
                except:
                    pass
                
                # 再次检查
                page_text = await page.evaluate("() => document.body.innerText || ''")
                if '请求异常' in page_text or '请稍后重试' in page_text:
                    print(f"   ❌ 页面仍然显示错误")
                    print(f"   💡 建议：")
                    print(f"      1. 检查是否需要Cookie或登录状态")
                    print(f"      2. 检查是否需要特定的Referer")
                    print(f"      3. 可能需要手动访问一次以建立会话")
                else:
                    print(f"   ✅ 页面恢复正常")
            
            # 等待所有资源加载
            print(f"   ⏳ 等待所有资源加载...")
            try:
                await page.wait_for_load_state('networkidle', timeout=60000)
                print(f"   ✅ 资源加载完成")
            except:
                print(f"   ⚠️ 等待资源加载超时")
            
            await asyncio.sleep(20)  # 等待JavaScript执行
            
            # 检查页面中的对象
            print(f"\n[步骤2] 检查页面对象...")
            page_objects = await page.evaluate("""
                () => {
                    const objects = {};
                    const keywords = ['player', 'config', 'play', 'video', 'llq'];
                    
                    for (const key in window) {
                        try {
                            if (typeof window[key] === 'object' && window[key] !== null) {
                                const keyLower = key.toLowerCase();
                                if (keywords.some(kw => keyLower.includes(kw))) {
                                    const obj = window[key];
                                    objects[key] = {
                                        type: typeof obj,
                                        keys: Object.keys(obj).slice(0, 20),
                                        hasUrl: !!(obj.url || obj.Url || obj.URL),
                                        hasData: !!(obj.data || obj.Data),
                                        hasSrc: !!(obj.src || obj.Src)
                                    };
                                }
                            }
                        } catch (e) {
                            // 忽略错误
                        }
                    }
                    return objects;
                }
            """)
            
            if page_objects:
                print(f"   📋 找到相关对象:")
                for obj_name, obj_info in page_objects.items():
                    print(f"      - {obj_name}: {obj_info.get('type', 'unknown')}")
                    if obj_info.get('keys'):
                        print(f"        属性: {', '.join(obj_info['keys'][:10])}")
                    if obj_info.get('hasUrl'):
                        print(f"        ✅ 包含url属性")
            
            # 检查是否有视频元素
            print(f"\n[步骤3] 检查视频元素...")
            video_info = await page.evaluate("""
                () => {
                    const videos = document.querySelectorAll('video');
                    const result = [];
                    videos.forEach((video, index) => {
                        result.push({
                            index: index,
                            src: video.src,
                            currentSrc: video.currentSrc,
                            poster: video.poster,
                            autoplay: video.autoplay,
                            controls: video.controls
                        });
                    });
                    return result;
                }
            """)
            
            if video_info:
                print(f"   📋 找到 {len(video_info)} 个video元素:")
                for video in video_info:
                    print(f"      [{video['index']}]")
                    if video.get('src'):
                        print(f"         src: {video['src']}")
                    if video.get('currentSrc'):
                        print(f"         currentSrc: {video['currentSrc']}")
            
            # 检查所有script标签中的内容
            print(f"\n[步骤4] 检查script标签...")
            script_urls = await page.evaluate("""
                () => {
                    const scripts = [];
                    document.querySelectorAll('script[src]').forEach(script => {
                        scripts.push(script.src);
                    });
                    return scripts;
                }
            """)
            
            print(f"   📋 找到 {len(script_urls)} 个外部script:")
            for script_url in script_urls[:10]:
                print(f"      - {script_url}")
            
            # 保存页面HTML
            html = await page.content()
            with open('media_staticfile_page.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"\n   💾 页面HTML已保存到: media_staticfile_page.html")
            
            return {
                'url': url,
                'page_objects': page_objects,
                'video_info': video_info,
                'script_urls': script_urls,
                'm3u8_urls': m3u8_found,
                'network_data': network_data,
                'html': html
            }
            
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def analyze_url_params(self, url: str) -> dict:
        """分析URL参数"""
        print(f"\n[步骤0] 分析URL参数...")
        from urllib.parse import urlparse, parse_qs
        
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        result = {
            'base_url': f"{parsed.scheme}://{parsed.netloc}{parsed.path}",
            'params': {}
        }
        
        for key, value in params.items():
            result['params'][key] = value[0] if value else ''
            print(f"   📋 {key}: {value[0] if value else ''}")
            
            # 尝试解码iv参数（可能是十六进制编码）
            if key == 'iv':
                try:
                    iv_hex = value[0]
                    iv_decoded = bytes.fromhex(iv_hex).decode('utf-8', errors='ignore')
                    print(f"      iv解码: {iv_decoded}")
                    result['params'][f'{key}_decoded'] = iv_decoded
                except:
                    pass
        
        return result
    
    async def check_api_endpoints(self, page: Page, base_url: str, params: dict) -> Optional[dict]:
        """检查可能的API端点"""
        print(f"\n[步骤5] 检查API端点...")
        
        # 检查UPDATEDMKU.php API
        if 'url' in params:
            import base64
            try:
                # URL参数可能是base64编码的
                encoded_url = params['url']
                # 添加padding如果必要
                padding = 4 - len(encoded_url) % 4
                if padding != 4:
                    encoded_url += '=' * padding
                decoded_url = base64.b64decode(encoded_url).decode('utf-8')
                print(f"   📋 url参数解码: {decoded_url}")
                
                # 尝试访问UPDATEDMKU.php API
                api_url = f"https://dmku.byteamone.cn/UPDATEDMKU.php?url={params['url']}"
                print(f"   🔍 检查API: {api_url}")
                
                try:
                    response = await page.goto(api_url, wait_until='networkidle', timeout=30000)
                    if response:
                        content = await response.text()
                        print(f"   ✅ API响应状态: {response.status}")
                        print(f"   📄 响应内容: {content[:500]}")
                        
                        # 检查是否包含m3u8
                        if 'm3u8' in content.lower():
                            m3u8_patterns = [
                                r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
                            ]
                            for pattern in m3u8_patterns:
                                matches = re.findall(pattern, content, re.IGNORECASE)
                                for match in matches:
                                    if match.startswith('http'):
                                        print(f"   ✅ 在API响应中找到m3u8: {match}")
                                        return {'m3u8_url': match, 'source': 'UPDATEDMKU.php'}
                        
                        # 尝试解析JSON
                        try:
                            json_data = json.loads(content)
                            print(f"   ✅ JSON解析成功")
                            return {'json_data': json_data, 'source': 'UPDATEDMKU.php'}
                        except:
                            pass
                except Exception as e:
                    print(f"   ⚠️ API访问失败: {e}")
            except Exception as e:
                print(f"   ⚠️ URL解码失败: {e}")
        
        return None
    
    async def analyze(self, url: str, chrome_path: str = None) -> Optional[dict]:
        """完整分析"""
        print("=" * 60)
        print("分析 media.staticfile.link 解析接口")
        print("=" * 60)
        print(f"目标URL: {url}")
        
        # 分析URL参数
        url_params = await self.analyze_url_params(url)
        
        # 启动Chrome
        chrome_process, debug_port, user_data_dir = launch_chrome(chrome_path=chrome_path)
        if not chrome_process or not debug_port:
            print("\n❌ 启动Chrome浏览器失败")
            return None
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{debug_port}")
                print(f"✅ 成功连接到Chrome浏览器")
                
                # 创建更真实的浏览器上下文
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    locale='zh-CN',
                    timezone_id='Asia/Shanghai',
                    permissions=['geolocation', 'notifications'],
                    color_scheme='light',
                    reduced_motion='no-preference',
                    forced_colors='none',
                    extra_http_headers={
                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                        'Cache-Control': 'max-age=0',
                    },
                    # 设置真实的屏幕信息
                    screen={'width': 1920, 'height': 1080},
                    device_scale_factor=1,
                )
                
                await add_stealth_script(context)
                
                page = await context.new_page()
                
                # 使用CDP禁用调试器
                try:
                    cdp_session = await context.new_cdp_session(page)
                    await cdp_session.send('Runtime.disable')
                    await cdp_session.send('Debugger.disable')
                    print("✅ CDP调试器已禁用")
                except:
                    pass
                
                try:
                    # 先访问主页面建立会话（如果需要）
                    print(f"\n[步骤0.5] 访问主页面建立会话...")
                    try:
                        main_page_url = "https://jx.playerjy.com/"
                        await page.goto(main_page_url, wait_until='domcontentloaded', timeout=30000)
                        await asyncio.sleep(3)
                        print(f"   ✅ 主页面访问完成")
                        
                        # 获取Cookie
                        cookies = await context.cookies()
                        if cookies:
                            print(f"   ✅ 获取到 {len(cookies)} 个Cookie")
                    except Exception as e:
                        print(f"   ⚠️ 访问主页面失败: {e}")
                    
                    # 分析页面
                    page_info = await self.analyze_page(page, url)
                    
                    # 检查API端点
                    api_info = await self.check_api_endpoints(page, url_params['base_url'], url_params['params'])
                    
                    # 汇总结果
                    result = {
                        'url': url,
                        'url_params': url_params,
                        'page_info': page_info,
                        'api_info': api_info
                    }
                    
                    # 保存结果
                    with open('media_staticfile_analysis.json', 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
                    print(f"\n✅ 分析结果已保存到: media_staticfile_analysis.json")
                    
                    # 打印总结
                    print("\n" + "=" * 60)
                    print("📊 分析总结")
                    print("=" * 60)
                    
                    if page_info and page_info.get('m3u8_urls'):
                        print(f"\n✅ 找到 {len(page_info['m3u8_urls'])} 个m3u8链接:")
                        for m3u8_url in page_info['m3u8_urls']:
                            print(f"   - {m3u8_url}")
                    
                    if api_info and api_info.get('m3u8_url'):
                        print(f"\n✅ API返回的m3u8链接:")
                        print(f"   - {api_info['m3u8_url']}")
                    
                    if page_info and page_info.get('video_info'):
                        print(f"\n✅ 找到 {len(page_info['video_info'])} 个video元素")
                        for video in page_info['video_info']:
                            if video.get('currentSrc'):
                                print(f"   - {video['currentSrc']}")
                    
                    print(f"\n⏸️ 浏览器将保持打开15秒，您可以手动检查...")
                    await asyncio.sleep(15)
                    
                    await context.close()
                    await browser.close()
                    
                    return result
                    
                except Exception as e:
                    print(f"\n❌ 分析过程中发生错误: {e}")
                    import traceback
                    traceback.print_exc()
                    try:
                        await context.close()
                        await browser.close()
                    except:
                        pass
                    return None
                    
        finally:
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
    # 直接使用media.staticfile.link URL
    url = "https://media.staticfile.link/?iv=3130312e33322e3232312e3739&key=d652ece029bb2681283dab579aa72f89&url=https://www.iqiyi.com/v_1c168e2yzbk.html"
    
    analyzer = MediaStaticFileAnalyzer()
    result = await analyzer.analyze(url)
    
    if not result:
        print("\n❌ 分析失败")


if __name__ == '__main__':
    asyncio.run(main())

