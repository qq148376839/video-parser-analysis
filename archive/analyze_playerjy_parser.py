"""
分析 jx.playerjy.com 解析接口的逻辑
参考 browser_decrypt_parser.py 的结构，分析新接口的工作流程
使用独立Chrome实例和反爬虫技术
"""

import asyncio
import json
import subprocess
import tempfile
import socket
import time
import os
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
    """
    启动独立的Chrome浏览器实例
    返回进程、端口和用户数据目录
    """
    # 尝试查找Chrome路径
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
    print(f"   临时目录: {temp_user_data_dir}")
    
    # Chrome启动参数（参考enhanced_browser_controller）
    # 添加参数来禁用安全检查和阻止页面屏蔽
    args = [
        chrome_path,
        f'--remote-debugging-port={debug_port}',
        f'--user-data-dir={temp_user_data_dir}',
        '--no-first-run',
        '--no-default-browser-check',
        '--disable-extensions',
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-renderer-backgrounding',
        '--disable-features=TranslateUI',
        '--disable-ipc-flooding-protection',
        '--disable-hang-monitor',
        '--disable-prompt-on-repost',
        '--disable-domain-reliability',
        '--disable-default-apps',
        '--disable-sync',
        '--disable-translate',
        '--disable-web-security',
        '--disable-site-isolation-trials',  # 禁用站点隔离
        '--disable-features=BlockInsecurePrivateNetworkRequests',  # 允许不安全的私有网络请求
        '--disable-features=VizDisplayCompositor',  # 禁用显示合成器
        '--force-color-profile=srgb',
        '--metrics-recording-only',
        '--disable-gpu',
        '--disable-blink-features=AutomationControlled',  # 禁用自动化控制检测
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
        
        # 等待端口开放
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
    """添加反爬虫脚本到浏览器上下文"""
    stealth_script = """
    // 隐藏webdriver属性
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    
    // 设置平台信息
    Object.defineProperty(navigator, 'platform', { get: () => 'Win32' });
    
    // 设置语言
    Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en'] });
    
    // 隐藏自动化特征
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
    
    // 覆盖Chrome对象
    window.chrome = {
        runtime: {}
    };
    
    // 覆盖权限查询
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
            Promise.resolve({ state: Notification.permission }) :
            originalQuery(parameters)
    );
    
    // ===== 绕过开发者工具检测 =====
    // 禁用debugger
    const originalDebugger = window.debugger;
    window.debugger = function() {};
    
    // 覆盖console.debug，防止检测
    const originalConsoleDebug = console.debug;
    console.debug = function() {};
    
    // 禁用DevTools检测
    let devtools = {open: false, orientation: null};
    const threshold = 160;
    setInterval(() => {
        if (window.outerHeight - window.innerHeight > threshold || 
            window.outerWidth - window.innerWidth > threshold) {
            if (!devtools.open) {
                devtools.open = true;
            }
        } else {
            if (devtools.open) {
                devtools.open = false;
            }
        }
    }, 500);
    
    // 覆盖toString方法，防止检测
    const originalToString = Function.prototype.toString;
    Function.prototype.toString = function() {
        if (this === originalDebugger || this === window.debugger) {
            return 'function debugger() { [native code] }';
        }
        return originalToString.apply(this, arguments);
    };
    
    // 禁用无限debugger循环
    const noop = () => {};
    const dbg = window.debugger;
    window.debugger = noop;
    
    // 监听DevTools打开事件并阻止
    Object.defineProperty(window, 'devtools', {
        get: () => ({open: false}),
        set: () => {}
    });
    
    console.log('🔐 反检测脚本已加载（包含开发者工具绕过）');
    """
    
    await context.add_init_script(script=stealth_script)
    print("✅ 反检测脚本已添加（包含开发者工具绕过）")


class PlayerJYParserAnalyzer:
    """分析 jx.playerjy.com 解析接口的逻辑"""
    
    def __init__(self):
        self.session = None
        self.decrypted_url = None
    
    async def analyze_main_page(self, page: Page, parser_url: str, video_url: str) -> Optional[dict]:
        """分析主页面结构"""
        print(f"\n[步骤1] 分析主页面结构...")
        full_url = f"{parser_url}/?ads=0&url={video_url}"
        print(f"   访问URL: {full_url}")
        
        try:
            # 使用更宽松的等待策略，避免超时
            await page.goto(full_url, wait_until='domcontentloaded', timeout=90000)
            await asyncio.sleep(5)  # 等待JavaScript执行
            
            # 获取页面基本信息
            page_info = await page.evaluate("""
                () => {
                    return {
                        title: document.title,
                        url: window.location.href,
                        has_iframe: !!document.querySelector('iframe'),
                        iframe_count: document.querySelectorAll('iframe').length,
                        scripts_count: document.querySelectorAll('script').length,
                        window_keys: Object.keys(window).filter(k => !k.startsWith('webkit') && !k.startsWith('chrome')).slice(0, 20)
                    };
                }
            """)
            
            print(f"   ✅ 页面标题: {page_info.get('title', 'N/A')}")
            print(f"   ✅ 当前URL: {page_info.get('url', 'N/A')}")
            print(f"   ✅ iframe数量: {page_info.get('iframe_count', 0)}")
            print(f"   ✅ script标签数量: {page_info.get('scripts_count', 0)}")
            
            # 查找所有iframe
            iframes = await page.evaluate("""
                () => {
                    const iframes = [];
                    document.querySelectorAll('iframe').forEach((iframe, index) => {
                        iframes.push({
                            index: index,
                            src: iframe.src,
                            id: iframe.id,
                            name: iframe.name,
                            width: iframe.width,
                            height: iframe.height
                        });
                    });
                    return iframes;
                }
            """)
            
            if iframes:
                print(f"\n   📋 找到 {len(iframes)} 个iframe:")
                for iframe in iframes:
                    print(f"      [{iframe['index']}] src: {iframe['src']}")
                    print(f"          id: {iframe.get('id', 'N/A')}, name: {iframe.get('name', 'N/A')}")
            
            # 保存页面HTML（等待页面稳定）
            html = None
            try:
                await page.wait_for_load_state('networkidle', timeout=10000)
            except:
                pass  # 忽略超时
            
            try:
                html = await page.content()
                with open('playerjy_main_page.html', 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"\n   💾 主页面HTML已保存到: playerjy_main_page.html")
            except Exception as e:
                print(f"   ⚠️ 保存HTML失败（页面可能正在导航）: {e}")
                # 如果保存失败，尝试再次获取
                try:
                    await asyncio.sleep(2)
                    html = await page.content()
                    with open('playerjy_main_page.html', 'w', encoding='utf-8') as f:
                        f.write(html)
                    print(f"   ✅ 重试保存HTML成功")
                except:
                    html = ""  # 设置为空字符串避免错误
            
            return {
                'page_info': page_info,
                'iframes': iframes,
                'html': html or ""
            }
                
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def analyze_iframe_page(self, page: Page, iframe_url: str) -> Optional[dict]:
        """分析iframe页面结构"""
        print(f"\n[步骤2] 分析iframe页面结构...")
        print(f"   初始iframe URL: {iframe_url}")
        
        try:
            # 设置Referer，模拟从主页面跳转
            await page.set_extra_http_headers({
                'Referer': 'https://jx.playerjy.com/',
                'Origin': 'https://jx.playerjy.com'
            })
            
            # 监听响应，跟踪重定向
            final_url = None
            def handle_response(response):
                nonlocal final_url
                final_url = response.url
                print(f"   📍 响应URL: {response.url}")
            
            page.on('response', handle_response)
            
            # 访问iframe URL，等待重定向
            response = await page.goto(iframe_url, wait_until='domcontentloaded', timeout=90000)
            
            if response:
                final_url = response.url
                print(f"   ✅ 最终URL: {final_url}")
                
                # 如果发生了重定向，打印重定向信息
                if final_url != iframe_url:
                    print(f"   🔄 检测到重定向:")
                    print(f"      从: {iframe_url}")
                    print(f"      到: {final_url}")
            
            await asyncio.sleep(5)  # 等待JavaScript执行
            
            # 检查是否有播放按钮需要点击
            print(f"   🔍 检查是否有播放按钮...")
            play_button_found = False
            
            # 等待页面稳定
            await asyncio.sleep(3)
            
            # 尝试多种可能的播放按钮选择器
            play_button_selectors = [
                'button:has-text("播放")',
                'button:has-text("点击播放")',
                'div:has-text("播放")',
                'div:has-text("点击播放")',
                '[class*="play"]',
                '[id*="play"]',
                'button[class*="btn"]',
                'div[class*="play-btn"]',
                'a[class*="play"]',
                'button',
                'div[onclick]',
                'a[href*="player"]',
            ]
            
            # 先尝试通过文本查找
            try:
                play_button = page.get_by_text('播放', exact=False).first
                if await play_button.is_visible():
                    print(f"   ✅ 找到播放按钮（通过文本）")
                    print(f"   🖱️ 点击播放按钮...")
                    await play_button.click()
                    await asyncio.sleep(5)  # 等待跳转
                    play_button_found = True
                    
                    # 检查是否发生了跳转
                    new_url = page.url
                    if new_url != final_url:
                        print(f"   🔄 点击后跳转到: {new_url}")
                        final_url = new_url
            except Exception as e:
                print(f"   ℹ️ 通过文本查找播放按钮失败: {e}")
            
            # 如果文本查找失败，尝试通过选择器查找
            if not play_button_found:
                for selector in play_button_selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        if elements:
                            print(f"   📋 找到可能的播放按钮: {selector} ({len(elements)}个)")
                            for idx, element in enumerate(elements):
                                try:
                                    text = await element.text_content()
                                    is_visible = await element.is_visible()
                                    bbox = await element.bounding_box()
                                    
                                    print(f"      按钮[{idx}]: 文本='{text}', 可见={is_visible}, 位置={bbox}")
                                    
                                    # 检查是否是播放相关的按钮
                                    if is_visible and bbox:
                                        text_lower = (text or '').lower()
                                        if ('播放' in text or 'play' in text_lower or 
                                            '点击' in text or 'click' in text_lower or
                                            selector in ['button', 'div[onclick]', 'a[href*="player"]']):
                                            print(f"   🖱️ 点击按钮[{idx}]...")
                                            # 尝试滚动到元素可见
                                            await element.scroll_into_view_if_needed()
                                            await asyncio.sleep(1)
                                            
                                            # 点击元素
                                            await element.click(timeout=5000)
                                            await asyncio.sleep(5)  # 等待跳转
                                            play_button_found = True
                                            
                                            # 检查是否发生了跳转
                                            new_url = page.url
                                            if new_url != final_url:
                                                print(f"   🔄 点击后跳转到: {new_url}")
                                                final_url = new_url
                                            break
                                except Exception as e:
                                    print(f"      ⚠️ 检查按钮[{idx}]时出错: {e}")
                                    continue
                            
                            if play_button_found:
                                break
                    except Exception as e:
                        continue
            
            if not play_button_found:
                print(f"   ℹ️ 未找到明显的播放按钮，继续分析...")
                # 尝试点击页面中心（有些播放按钮可能是全屏的）
                try:
                    viewport = page.viewport_size
                    if viewport:
                        center_x = viewport['width'] // 2
                        center_y = viewport['height'] // 2
                        print(f"   🖱️ 尝试点击页面中心 ({center_x}, {center_y})...")
                        await page.mouse.click(center_x, center_y)
                        await asyncio.sleep(3)
                        new_url = page.url
                        if new_url != final_url:
                            print(f"   🔄 点击后跳转到: {new_url}")
                            final_url = new_url
                            play_button_found = True
                except Exception as e:
                    print(f"   ⚠️ 点击页面中心失败: {e}")
            
            await asyncio.sleep(5)  # 额外等待时间
            
            # 检查关键对象
            print(f"   检查关键对象...")
            
            # 等待一段时间，检查各种可能的对象（添加导航检测）
            objects_found = {}
            for wait_time in [3, 5, 10]:
                try:
                    await asyncio.sleep(wait_time)
                    check_result = await page.evaluate("""
                        () => {
                            const result = {};
                            
                            // 检查常见的配置对象
                            const objects_to_check = [
                                'ConFig', 'Config', 'config', 'CONFIG',
                                'PlayEr', 'Player', 'player', 'PLAYER',
                                'playerConfig', 'player_config', 'videoConfig',
                                'window.player', 'window.playerConfig',
                                'window.video', 'window.videoConfig'
                            ];
                            
                            objects_to_check.forEach(key => {
                                try {
                                    const keys = key.split('.');
                                    let obj = window;
                                    for (const k of keys) {
                                        if (obj && typeof obj === 'object' && k in obj) {
                                            obj = obj[k];
                                        } else {
                                            obj = null;
                                            break;
                                        }
                                    }
                                    if (obj && typeof obj === 'object') {
                                        result[key] = {
                                            exists: true,
                                            type: typeof obj,
                                            keys: Object.keys(obj).slice(0, 10)
                                        };
                                    }
                                } catch (e) {
                                    // 忽略错误
                                }
                            });
                            
                            return result;
                        }
                    """)
                    
                    if check_result:
                        objects_found.update(check_result)
                except Exception as e:
                    error_msg = str(e).lower()
                    if "destroyed" in error_msg or "navigation" in error_msg:
                        print(f"   ⚠️ 页面正在导航，跳过对象检查...")
                        break
                    # 其他错误继续
            
            if objects_found:
                print(f"   ✅ 找到以下对象:")
                for obj_name, obj_info in objects_found.items():
                    print(f"      - {obj_name}: {obj_info.get('type', 'unknown')}")
                    if obj_info.get('keys'):
                        print(f"        属性: {', '.join(obj_info['keys'][:10])}")
            
            # 提取ConFig对象（如果存在）
            config_data = await page.evaluate("""
                () => {
                    const result = {};
                    
                    // 尝试多种可能的ConFig路径
                    const config_paths = [
                        'window.ConFig',
                        'window.Config',
                        'window.config',
                        'window.playerConfig',
                        'window.videoConfig'
                    ];
                    
                    for (const path of config_paths) {
                        try {
                            const keys = path.split('.');
                            let obj = window;
                            for (const k of keys.slice(1)) {
                                if (obj && typeof obj === 'object' && k in obj) {
                                    obj = obj[k];
                                } else {
                                    obj = null;
                                    break;
                                }
                            }
                            
                            if (obj && typeof obj === 'object') {
                                result[path] = {
                                    url: obj.url || obj.Url || obj.URL || null,
                                    uid: (obj.config && obj.config.uid) || obj.uid || null,
                                    full: JSON.stringify(obj).substring(0, 500)
                                };
                            }
                        } catch (e) {
                            // 忽略错误
                        }
                    }
                    
                    return result;
                }
            """)
            
            if config_data:
                print(f"\n   ✅ 找到配置对象:")
                for path, data in config_data.items():
                    print(f"      {path}:")
                    if data.get('url'):
                        print(f"         url: {data['url'][:100]}...")
                    if data.get('uid'):
                        print(f"         uid: {data['uid']}")
            
            # 提取PlayEr对象（如果存在）
            player_data = await page.evaluate("""
                () => {
                    const result = {};
                    
                    // 尝试多种可能的PlayEr路径
                    const player_paths = [
                        'window.PlayEr',
                        'window.Player',
                        'window.player',
                        'window.PLAYER'
                    ];
                    
                    for (const path of player_paths) {
                        try {
                            const keys = path.split('.');
                            let obj = window;
                            for (const k of keys.slice(1)) {
                                if (obj && typeof obj === 'object' && k in obj) {
                                    obj = obj[k];
                                } else {
                                    obj = null;
                                    break;
                                }
                            }
                            
                            if (obj && typeof obj === 'object') {
                                // 查找解密函数
                                const decrypt_functions = [];
                                
                                function findFunctions(obj, prefix = '') {
                                    if (typeof obj === 'function') {
                                        decrypt_functions.push(prefix);
                                    } else if (typeof obj === 'object' && obj !== null) {
                                        for (const key in obj) {
                                            try {
                                                findFunctions(obj[key], prefix ? `${prefix}.${key}` : key);
                                            } catch (e) {
                                                // 忽略错误
                                            }
                                        }
                                    }
                                }
                                
                                findFunctions(obj);
                                
                                result[path] = {
                                    exists: true,
                                    functions: decrypt_functions.slice(0, 20)
                                };
                            }
                        } catch (e) {
                            // 忽略错误
                        }
                    }
                    
                    return result;
                }
            """)
            
            if player_data:
                print(f"\n   ✅ 找到播放器对象:")
                for path, data in player_data.items():
                    print(f"      {path}:")
                    if data.get('functions'):
                        print(f"         函数: {', '.join(data['functions'][:10])}")
            
            # 检查是否有嵌套iframe
            nested_iframe_src = await page.evaluate("""
                () => {
                    const iframe = document.querySelector('iframe');
                    return iframe ? iframe.src : null;
                }
            """)
            
            if nested_iframe_src:
                print(f"\n   📋 发现嵌套iframe: {nested_iframe_src}")
            
            # 保存iframe页面HTML
            html = await page.content()
            with open('playerjy_iframe_page.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"\n   💾 iframe页面HTML已保存到: playerjy_iframe_page.html")
            
            return {
                'final_url': page.url,
                'nested_iframe': nested_iframe_src,
                'objects_found': objects_found,
                'config_data': config_data,
                'player_data': player_data,
                'html': html
            }
                
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def extract_config_from_iframe(self, page: Page, iframe_url: str) -> Optional[dict]:
        """从iframe页面提取配置对象（参考原代码逻辑）"""
        print(f"\n[步骤3] 提取配置对象...")
        print(f"   初始iframe URL: {iframe_url}")
        
        try:
            # 设置Referer
            await page.set_extra_http_headers({
                'Referer': 'https://jx.playerjy.com/',
                'Origin': 'https://jx.playerjy.com'
            })
            
            # 访问iframe URL，跟踪重定向
            response = await page.goto(iframe_url, wait_until='domcontentloaded', timeout=90000)
            
            final_url = response.url if response else iframe_url
            if final_url != iframe_url:
                print(f"   🔄 重定向到: {final_url}")
            
            # 等待所有资源加载完成
            print(f"   ⏳ 等待所有资源加载完成...")
            try:
                # 等待networkidle，确保所有请求完成
                await page.wait_for_load_state('networkidle', timeout=60000)
                print(f"   ✅ 资源加载完成")
            except Exception as e:
                print(f"   ⚠️ 等待资源加载超时: {e}")
            
            # 额外等待，确保JavaScript执行完成
            await asyncio.sleep(15)  # 增加等待时间，确保JavaScript执行完成
            
            # 等待页面稳定（处理可能的导航）
            try:
                await page.wait_for_load_state('networkidle', timeout=30000)
            except:
                pass  # 忽略超时
            
            # 检查页面是否加载了iframe（说明又嵌套了一层）
            try:
                nested_iframe = await page.evaluate("""
                () => {
                    const iframe = document.querySelector('iframe');
                    if (iframe && iframe.src) {
                        return iframe.src;
                    }
                    return null;
                }
                """)
            except Exception as e:
                error_msg = str(e).lower()
                if "destroyed" in error_msg or "navigation" in error_msg:
                    print(f"   ⚠️ 页面正在导航，等待稳定...")
                    await asyncio.sleep(5)
                    try:
                        await page.wait_for_load_state('networkidle', timeout=15000)
                        nested_iframe = await page.evaluate("""
                            () => {
                                const iframe = document.querySelector('iframe');
                                return iframe && iframe.src ? iframe.src : null;
                            }
                        """)
                    except:
                        nested_iframe = None
                else:
                    nested_iframe = None
            
            if nested_iframe:
                print(f"   📋 发现嵌套iframe: {nested_iframe}")
                print(f"   🔄 访问嵌套iframe...")
                
                # 设置Referer为父页面
                await page.set_extra_http_headers({
                    'Referer': final_url if final_url else iframe_url,
                    'Origin': 'https://getdata.staticfile.link'
                })
                
                # 访问嵌套iframe
                await page.goto(nested_iframe, wait_until='domcontentloaded', timeout=90000)
                await asyncio.sleep(10)
                
                final_url = page.url
                print(f"   ✅ 嵌套iframe最终URL: {final_url}")
            
            # 先检查页面中的所有全局对象
            print(f"   🔍 检查页面中的全局对象...")
            all_objects = await page.evaluate("""
                () => {
                    const objects = {};
                    for (const key in window) {
                        try {
                            if (typeof window[key] === 'object' && window[key] !== null) {
                                const obj = window[key];
                                if (key.includes('Config') || key.includes('config') || 
                                    key.includes('Player') || key.includes('player') ||
                                    key.includes('Play') || key.includes('play')) {
                                    objects[key] = {
                                        type: typeof obj,
                                        keys: Object.keys(obj).slice(0, 20),
                                        hasUrl: !!(obj.url || obj.Url || obj.URL),
                                        hasUid: !!(obj.uid || (obj.config && obj.config.uid))
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
            
            if all_objects:
                print(f"   📋 找到相关对象:")
                for obj_name, obj_info in all_objects.items():
                    print(f"      - {obj_name}: {obj_info.get('type', 'unknown')}")
                    if obj_info.get('keys'):
                        print(f"        属性: {', '.join(obj_info['keys'][:10])}")
                    if obj_info.get('hasUrl'):
                        print(f"        ✅ 包含url属性")
                    if obj_info.get('hasUid'):
                        print(f"        ✅ 包含uid属性")
            
            # 等待配置对象出现（尝试多种可能的对象名）
            print(f"\n   等待配置对象出现...")
            config_found = None
            
            for i in range(60):  # 增加等待时间到60秒
                # 检查多种可能的配置对象（排除游戏配置）
                try:
                    has_config = await page.evaluate("""
                        () => {
                            // 检查 ConFig（视频配置）
                            if (window.ConFig && window.ConFig.url && window.ConFig.config && window.ConFig.config.uid) {
                                return 'ConFig';
                            }
                            
                            // 检查 llqplayer 相关对象
                            if (window.llqplayer && window.llqplayer.url) {
                                return 'llqplayer';
                            }
                            if (window.llqPlayer && window.llqPlayer.url) {
                                return 'llqPlayer';
                            }
                            
                            // 检查 PlayEr
                            if (window.PlayEr && window.PlayEr.url) {
                                return 'PlayEr';
                            }
                            
                            // 检查 playerConfig
                            if (window.playerConfig && window.playerConfig.url && window.playerConfig.uid) {
                                return 'playerConfig';
                            }
                            
                            // 检查 config（排除游戏配置）
                            if (window.config && window.config.url && window.config.uid) {
                                // 排除游戏配置（有HEIGHT、MOON_SPEED等属性的）
                                if (!window.config.HEIGHT && !window.config.MOON_SPEED) {
                                    return 'config';
                                }
                            }
                            
                            // 检查是否有任何包含url的对象（排除游戏配置）
                            for (const key in window) {
                                try {
                                    const obj = window[key];
                                    if (obj && typeof obj === 'object' && obj.url) {
                                        // 排除游戏配置对象
                                        if (obj.HEIGHT || obj.MOON_SPEED || obj.MAX_CLOUD_GAP) {
                                            continue;
                                        }
                                        
                                        const uid = (obj.config && obj.config.uid) || obj.uid || null;
                                        const keyLower = key.toLowerCase();
                                        
                                        // 优先检查包含player、video、play等关键词的对象
                                        if (keyLower.includes('player') || keyLower.includes('video') || 
                                            keyLower.includes('play') || uid) {
                                            return key;
                                        }
                                    }
                                } catch (e) {
                                    // 忽略错误
                                }
                            }
                            
                            // 检查 llqplayer 实例
                            if (window.player && typeof window.player === 'object') {
                                if (window.player.url || (window.player.config && window.player.config.url)) {
                                    return 'player';
                                }
                            }
                            
                            return null;
                        }
                    """)
                except Exception as e:
                    error_msg = str(e).lower()
                    if "destroyed" in error_msg or "navigation" in error_msg:
                        print(f"   ⚠️ 页面正在导航，等待稳定...")
                        await asyncio.sleep(3)
                        # 等待导航完成
                        try:
                            await page.wait_for_load_state('networkidle', timeout=10000)
                        except:
                            pass
                        continue
                    raise
                
                if has_config:
                    print(f"   ✅ 找到配置对象: {has_config}")
                    config_found = has_config
                    break
                
                # 每5秒打印一次进度
                if i > 0 and i % 5 == 0:
                    print(f"   ⏳ 等待中... ({i}/60)")
                
                await asyncio.sleep(1)
            else:
                print(f"   ⚠️ 配置对象未出现")
            
            # 提取配置数据（更全面的搜索，排除游戏配置）
            try:
                config_data = await page.evaluate("""
                    () => {
                        // 尝试多种可能的配置对象
                        const configs = [
                            {obj: window.ConFig, name: 'ConFig'},
                            {obj: window.llqplayer, name: 'llqplayer'},
                            {obj: window.llqPlayer, name: 'llqPlayer'},
                            {obj: window.PlayEr, name: 'PlayEr'},
                            {obj: window.playerConfig, name: 'playerConfig'},
                            {obj: window.Player, name: 'Player'},
                            {obj: window.player, name: 'player'}
                        ];
                        
                        for (const {obj: config, name} of configs) {
                            if (config && config.url) {
                                return {
                                    url: config.url,
                                    uid: (config.config && config.config.uid) || config.uid || null,
                                    source: name,
                                    full: JSON.stringify(config).substring(0, 1000)
                                };
                            }
                        }
                        
                        // 如果没找到，尝试搜索所有全局对象（排除游戏配置）
                        for (const key in window) {
                            try {
                                const obj = window[key];
                                if (obj && typeof obj === 'object' && obj !== null && obj.url) {
                                    // 排除游戏配置对象
                                    if (obj.HEIGHT || obj.MOON_SPEED || obj.MAX_CLOUD_GAP) {
                                        continue;
                                    }
                                    
                                    const uid = (obj.config && obj.config.uid) || obj.uid || null;
                                    const keyLower = key.toLowerCase();
                                    
                                    // 优先检查包含player、video、play等关键词的对象
                                    if (keyLower.includes('player') || keyLower.includes('video') || 
                                        keyLower.includes('play') || uid) {
                                        return {
                                            url: obj.url,
                                            uid: uid,
                                            source: key,
                                            full: JSON.stringify(obj).substring(0, 1000)
                                        };
                                    }
                                }
                            } catch (e) {
                                // 忽略错误
                            }
                        }
                        
                        // 最后尝试：检查是否有data属性包含url
                        for (const key in window) {
                            try {
                                const obj = window[key];
                                if (obj && typeof obj === 'object' && obj !== null) {
                                    if (obj.data && obj.data.url) {
                                        return {
                                            url: obj.data.url,
                                            uid: obj.data.uid || obj.uid || null,
                                            source: key + '.data',
                                            full: JSON.stringify(obj).substring(0, 1000)
                                        };
                                    }
                                }
                            } catch (e) {
                                // 忽略错误
                            }
                        }
                        
                        return null;
                    }
                """)
            except Exception as e:
                error_msg = str(e).lower()
                if "destroyed" in error_msg or "navigation" in error_msg:
                    print(f"   ⚠️ 页面正在导航，等待稳定后重试...")
                    await asyncio.sleep(5)
                    try:
                        await page.wait_for_load_state('networkidle', timeout=15000)
                        # 重试提取
                        config_data = await page.evaluate("""
                            () => {
                                // 简化搜索，只查找关键对象
                                if (window.ConFig && window.ConFig.url) {
                                    return {
                                        url: window.ConFig.url,
                                        uid: (window.ConFig.config && window.ConFig.config.uid) || null,
                                        source: 'ConFig',
                                        full: JSON.stringify(window.ConFig).substring(0, 1000)
                                    };
                                }
                                if (window.llqplayer && window.llqplayer.url) {
                                    return {
                                        url: window.llqplayer.url,
                                        uid: null,
                                        source: 'llqplayer',
                                        full: JSON.stringify(window.llqplayer).substring(0, 1000)
                                    };
                                }
                                return null;
                            }
                        """)
                    except:
                        config_data = None
                else:
                    raise
            
            if config_data and config_data.get('url'):
                print(f"   ✅ 提取成功")
                print(f"   ✅ 配置来源: {config_data.get('source', 'unknown')}")
                print(f"   ✅ url: {config_data['url'][:100]}...")
                if config_data.get('uid'):
                    print(f"   ✅ uid: {config_data['uid']}")
                return config_data
            else:
                print(f"   ❌ 未能提取配置对象")
                return None
                
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def extract_config_from_frame(self, frame) -> Optional[dict]:
        """从iframe frame中提取配置对象"""
        print(f"\n[步骤3-iframe] 从iframe frame提取配置对象...")
        
        try:
            # 检查frame是否有效
            try:
                await frame.evaluate("() => true")
            except Exception as e:
                if "detached" in str(e).lower():
                    print(f"   ❌ Frame已分离，无法访问")
                    return None
                raise
            
            # 先列出所有全局对象，帮助调试
            print(f"   🔍 检查所有全局对象...")
            all_objects = {}
            try:
                all_objects = await frame.evaluate("""
                    () => {
                        const objects = {};
                        const keywords = ['config', 'player', 'play', 'video', 'url', 'data', 'info'];
                        
                        for (const key in window) {
                            try {
                                if (typeof window[key] === 'object' && window[key] !== null) {
                                    const keyLower = key.toLowerCase();
                                    if (keywords.some(kw => keyLower.includes(kw))) {
                                        const obj = window[key];
                                        objects[key] = {
                                            type: typeof obj,
                                            keys: Object.keys(obj).slice(0, 15),
                                            hasUrl: !!(obj.url || obj.Url || obj.URL),
                                            hasUid: !!(obj.uid || (obj.config && obj.config.uid)),
                                            hasData: !!(obj.data || obj.Data)
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
            except Exception as e:
                error_msg = str(e).lower()
                if "detached" in error_msg:
                    print(f"   ❌ Frame在执行过程中被分离")
                    return None
                print(f"   ⚠️ 检查全局对象时出错: {e}")
                # 继续执行，即使检查失败
            
            if all_objects:
                print(f"   📋 找到相关对象:")
                for obj_name, obj_info in all_objects.items():
                    print(f"      - {obj_name}: {obj_info.get('type', 'unknown')}")
                    if obj_info.get('keys'):
                        print(f"        属性: {', '.join(obj_info['keys'][:10])}")
                    if obj_info.get('hasUrl'):
                        print(f"        ✅ 包含url属性")
                    if obj_info.get('hasUid'):
                        print(f"        ✅ 包含uid属性")
            
            # 等待配置对象出现
            print(f"\n   等待配置对象出现...")
            config_found = None
            
            for i in range(60):  # 增加到60秒
                # 检查多种可能的配置对象（排除游戏配置）
                try:
                    has_config = await frame.evaluate("""
                        () => {
                            // 检查 ConFig（视频配置）
                            if (window.ConFig && window.ConFig.url && window.ConFig.config && window.ConFig.config.uid) {
                                return 'ConFig';
                            }
                            
                            // 检查 llqplayer 相关对象
                            if (window.llqplayer && window.llqplayer.url) {
                                return 'llqplayer';
                            }
                            if (window.llqPlayer && window.llqPlayer.url) {
                                return 'llqPlayer';
                            }
                            
                            // 检查 PlayEr
                            if (window.PlayEr && window.PlayEr.url) {
                                return 'PlayEr';
                            }
                            
                            // 检查 playerConfig
                            if (window.playerConfig && window.playerConfig.url && window.playerConfig.uid) {
                                return 'playerConfig';
                            }
                            
                            // 检查 config（排除游戏配置）
                            if (window.config && window.config.url && window.config.uid) {
                                // 排除游戏配置（有HEIGHT、MOON_SPEED等属性的）
                                if (!window.config.HEIGHT && !window.config.MOON_SPEED) {
                                    return 'config';
                                }
                            }
                            
                            // 检查是否有任何包含url的对象（排除游戏配置）
                            for (const key in window) {
                                try {
                                    const obj = window[key];
                                    if (obj && typeof obj === 'object' && obj.url) {
                                        // 排除游戏配置对象
                                        if (obj.HEIGHT || obj.MOON_SPEED || obj.MAX_CLOUD_GAP) {
                                            continue;
                                        }
                                        
                                        const uid = (obj.config && obj.config.uid) || obj.uid || null;
                                        const keyLower = key.toLowerCase();
                                        
                                        // 优先检查包含player、video、play等关键词的对象
                                        if (keyLower.includes('player') || keyLower.includes('video') || 
                                            keyLower.includes('play') || uid) {
                                            return key;
                                        }
                                    }
                                } catch (e) {
                                    // 忽略错误
                                }
                            }
                            
                            // 检查 llqplayer 实例
                            if (window.player && typeof window.player === 'object') {
                                if (window.player.url || (window.player.config && window.player.config.url)) {
                                    return 'player';
                                }
                            }
                            
                            return null;
                        }
                    """)
                except Exception as e:
                    error_msg = str(e).lower()
                    if "detached" in error_msg or "destroyed" in error_msg:
                        print(f"   ⚠️ Frame在执行过程中被分离或销毁，等待重试...")
                        await asyncio.sleep(2)
                        # 尝试重新获取frame
                        try:
                            iframe_element = await page.query_selector('iframe')
                            if iframe_element:
                                frame = await iframe_element.content_frame()
                                if frame:
                                    await asyncio.sleep(3)
                                    continue
                        except:
                            pass
                        break
                    raise
                
                if has_config:
                    print(f"   ✅ 找到配置对象: {has_config}")
                    config_found = has_config
                    break
                
                if i > 0 and i % 5 == 0:
                    print(f"   ⏳ 等待中... ({i}/60)")
                
                await asyncio.sleep(1)
            
            # 提取配置数据
            config_data = await frame.evaluate("""
                () => {
                    // 尝试多种可能的配置对象
                    const configs = [
                        {obj: window.ConFig, name: 'ConFig'},
                        {obj: window.Config, name: 'Config'},
                        {obj: window.config, name: 'config'},
                        {obj: window.playerConfig, name: 'playerConfig'},
                        {obj: window.PlayEr, name: 'PlayEr'},
                        {obj: window.Player, name: 'Player'},
                        {obj: window.player, name: 'player'},
                        {obj: window.llqplayer, name: 'llqplayer'},
                        {obj: window.llqPlayer, name: 'llqPlayer'}
                    ];
                    
                    for (const {obj: config, name} of configs) {
                        if (config && config.url) {
                            return {
                                url: config.url,
                                uid: (config.config && config.config.uid) || config.uid || null,
                                source: name,
                                full: JSON.stringify(config).substring(0, 1000)
                            };
                        }
                    }
                    
                    // 如果没找到，尝试搜索所有全局对象（排除游戏配置）
                    for (const key in window) {
                        try {
                            const obj = window[key];
                            if (obj && typeof obj === 'object' && obj !== null && obj.url) {
                                // 排除游戏配置对象
                                if (obj.HEIGHT || obj.MOON_SPEED || obj.MAX_CLOUD_GAP) {
                                    continue;
                                }
                                
                                const uid = (obj.config && obj.config.uid) || obj.uid || null;
                                const keyLower = key.toLowerCase();
                                if (uid || keyLower.includes('config') || keyLower.includes('player') || 
                                    keyLower.includes('play') || keyLower.includes('video')) {
                                    return {
                                        url: obj.url,
                                        uid: uid,
                                        source: key,
                                        full: JSON.stringify(obj).substring(0, 1000)
                                    };
                                }
                            }
                        } catch (e) {
                            // 忽略错误
                        }
                    }
                    
                    // 最后尝试：检查是否有data属性包含url
                    for (const key in window) {
                        try {
                            const obj = window[key];
                            if (obj && typeof obj === 'object' && obj !== null) {
                                if (obj.data && obj.data.url) {
                                    return {
                                        url: obj.data.url,
                                        uid: obj.data.uid || obj.uid || null,
                                        source: key + '.data',
                                        full: JSON.stringify(obj).substring(0, 1000)
                                    };
                                }
                            }
                        } catch (e) {
                            // 忽略错误
                        }
                    }
                    
                    return null;
                }
            """)
            
            if config_data and config_data.get('url'):
                print(f"   ✅ 提取成功")
                print(f"   ✅ 配置来源: {config_data.get('source', 'unknown')}")
                print(f"   ✅ url: {config_data['url'][:100]}...")
                if config_data.get('uid'):
                    print(f"   ✅ uid: {config_data['uid']}")
                return config_data
            else:
                print(f"   ❌ 未能提取配置对象")
                return None
                
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def find_decrypt_function(self, page: Page) -> Optional[str]:
        """查找解密函数"""
        print(f"\n[步骤4] 查找解密函数...")
        
        try:
            # 查找可能的解密函数
            decrypt_info = await page.evaluate("""
                () => {
                    const functions = [];
                    
                    // 检查 PlayEr.ad.uic
                    if (window.PlayEr && window.PlayEr.ad && typeof window.PlayEr.ad.uic === 'function') {
                        functions.push('PlayEr.ad.uic');
                    }
                    
                    // 检查 Player.ad.uic
                    if (window.Player && window.Player.ad && typeof window.Player.ad.uic === 'function') {
                        functions.push('Player.ad.uic');
                    }
                    
                    // 检查 player.decrypt
                    if (window.player && typeof window.player.decrypt === 'function') {
                        functions.push('player.decrypt');
                    }
                    
                    // 检查全局解密函数
                    const globalFunctions = ['decrypt', 'decryptUrl', 'decodeUrl', 'uic'];
                    for (const funcName of globalFunctions) {
                        if (typeof window[funcName] === 'function') {
                            functions.push(funcName);
                        }
                    }
                    
                    return functions;
                }
            """)
            
            if decrypt_info:
                print(f"   ✅ 找到解密函数: {', '.join(decrypt_info)}")
                return decrypt_info[0] if decrypt_info else None
            else:
                print(f"   ⚠️ 未找到明显的解密函数")
                return None
                
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            return None
    
    async def find_decrypt_function_in_frame(self, frame) -> Optional[str]:
        """在iframe frame中查找解密函数"""
        print(f"\n[步骤4-iframe] 在iframe frame中查找解密函数...")
        
        try:
            decrypt_info = await frame.evaluate("""
                () => {
                    const functions = [];
                    
                    // 检查 PlayEr.ad.uic
                    if (window.PlayEr && window.PlayEr.ad && typeof window.PlayEr.ad.uic === 'function') {
                        functions.push('PlayEr.ad.uic');
                    }
                    
                    // 检查 Player.ad.uic
                    if (window.Player && window.Player.ad && typeof window.Player.ad.uic === 'function') {
                        functions.push('Player.ad.uic');
                    }
                    
                    // 检查 player.decrypt
                    if (window.player && typeof window.player.decrypt === 'function') {
                        functions.push('player.decrypt');
                    }
                    
                    // 检查全局解密函数
                    const globalFunctions = ['decrypt', 'decryptUrl', 'decodeUrl', 'uic'];
                    for (const funcName of globalFunctions) {
                        if (typeof window[funcName] === 'function') {
                            functions.push(funcName);
                        }
                    }
                    
                    return functions;
                }
            """)
            
            if decrypt_info:
                print(f"   ✅ 找到解密函数: {', '.join(decrypt_info)}")
                return decrypt_info[0] if decrypt_info else None
            else:
                print(f"   ⚠️ 未找到明显的解密函数")
                return None
                
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            return None
    
    async def test_decrypt_in_frame(self, frame, encrypted_url: str, decrypt_function: str) -> Optional[str]:
        """在iframe frame中测试解密函数"""
        print(f"\n[步骤5-iframe] 在iframe frame中测试解密函数...")
        print(f"   加密URL长度: {len(encrypted_url)}")
        print(f"   解密函数: {decrypt_function}")
        
        try:
            decrypted = await frame.evaluate(f"""
                (encrypted_url) => {{
                    try {{
                        const func = {decrypt_function};
                        if (typeof func === 'function') {{
                            const result = func(encrypted_url);
                            return {{
                                success: true,
                                url: result
                            }};
                        }} else {{
                            return {{
                                success: false,
                                error: '函数不存在或不是函数类型'
                            }};
                        }}
                    }} catch (e) {{
                        return {{
                            success: false,
                            error: e.toString()
                        }};
                    }}
                }}
            """, encrypted_url)
            
            if decrypted.get('success'):
                decrypted_url = decrypted['url']
                print(f"   ✅ 解密成功！")
                print(f"   ✅ 解密后的URL: {decrypted_url}")
                return decrypted_url
            else:
                print(f"   ❌ 解密失败: {decrypted.get('error', '未知错误')}")
                return None
                
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def test_decrypt(self, page: Page, encrypted_url: str, decrypt_function: str) -> Optional[str]:
        """测试解密函数"""
        print(f"\n[步骤5] 测试解密函数...")
        print(f"   加密URL长度: {len(encrypted_url)}")
        print(f"   解密函数: {decrypt_function}")
        
        try:
            # 执行解密
            decrypted = await page.evaluate(f"""
                (encrypted_url) => {{
                    try {{
                        const func = {decrypt_function};
                        if (typeof func === 'function') {{
                            const result = func(encrypted_url);
                            return {{
                                success: true,
                                url: result
                            }};
                        }} else {{
                            return {{
                                success: false,
                                error: '函数不存在或不是函数类型'
                            }};
                        }}
                    }} catch (e) {{
                        return {{
                            success: false,
                            error: e.toString()
                        }};
                    }}
                }}
            """, encrypted_url)
            
            if decrypted.get('success'):
                decrypted_url = decrypted['url']
                print(f"   ✅ 解密成功！")
                print(f"   ✅ 解密后的URL: {decrypted_url}")
                return decrypted_url
            else:
                print(f"   ❌ 解密失败: {decrypted.get('error', '未知错误')}")
                return None
                
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def analyze_parser(self, parser_url: str, video_url: str, chrome_path: str = None) -> Optional[dict]:
        """完整分析解析接口逻辑"""
        print("=" * 60)
        print("分析 jx.playerjy.com 解析接口逻辑")
        print("=" * 60)
        print(f"解析网站: {parser_url}")
        print(f"目标视频: {video_url}")
        
        # 启动独立Chrome浏览器
        chrome_process, debug_port, user_data_dir = launch_chrome(chrome_path=chrome_path)
        if not chrome_process or not debug_port:
            print("\n❌ 启动Chrome浏览器失败")
            return None
        
        try:
            async with async_playwright() as p:
                # 连接到已启动的浏览器
                browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{debug_port}")
                print(f"✅ 成功连接到Chrome浏览器，端口: {debug_port}")
                
                # 创建新的context
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                )
                
                # 添加反爬虫脚本
                await add_stealth_script(context)
                
                page = await context.new_page()
                
                # 使用CDP禁用调试器（绕过开发者工具检测）
                try:
                    cdp_session = await context.new_cdp_session(page)
                    await cdp_session.send('Runtime.disable')
                    await cdp_session.send('Debugger.disable')
                    print("✅ CDP调试器已禁用（绕过开发者工具检测）")
                except Exception as e:
                    print(f"⚠️ 禁用CDP调试器失败: {e}")
                
                # 监听网络请求和响应
                network_requests = []
                network_responses = []
                
                def handle_request(request):
                    network_requests.append({
                        'url': request.url,
                        'method': request.method,
                        'resource_type': request.resource_type
                    })
                
                async def handle_response(response):
                    resp_info = {
                        'url': response.url,
                        'status': response.status,
                        'content_type': response.headers.get('content-type', '')
                    }
                    network_responses.append(resp_info)
                    
                    # 检查是否是API响应，可能包含配置数据
                    url_lower = response.url.lower()
                    content_type = response.headers.get('content-type', '').lower()
                    
                    # 检查各种可能的API端点
                    is_api_response = (
                        'api' in url_lower or 
                        'json' in content_type or 
                        'php' in url_lower or 
                        'm3u8' in url_lower or
                        'dmku.byteamone.cn' in url_lower or
                        'UPDATEDMKU' in response.url or
                        'byteamone.cn' in url_lower or
                        response.status == 200 and ('text' in content_type or 'json' in content_type)
                    )
                    
                    if is_api_response:
                        try:
                            content = await response.text()
                            resp_info['content'] = content[:5000]  # 保存前5000字符
                            
                            # 检查是否包含m3u8链接
                            if 'm3u8' in content.lower():
                                print(f"   ✅ 发现m3u8链接在响应中: {response.url}")
                                # 提取m3u8链接
                                import re
                                m3u8_patterns = [
                                    r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
                                    r'["\']([^"\']+\.m3u8[^"\']*)["\']',
                                ]
                                for pattern in m3u8_patterns:
                                    matches = re.findall(pattern, content, re.IGNORECASE)
                                    for match in matches:
                                        url = match if isinstance(match, str) else match[0] if match else None
                                        if url and url.startswith('http'):
                                            print(f"      🎬 m3u8链接: {url}")
                            
                            # 检查是否包含配置数据（url和uid）
                            if ('url' in content.lower() and 
                                ('uid' in content.lower() or 'm3u8' in content.lower() or 
                                 'http' in content.lower())):
                                print(f"   🔍 发现可能的配置API响应: {response.url}")
                                print(f"      状态码: {response.status}")
                                print(f"      内容类型: {content_type}")
                                print(f"      内容预览: {content[:500]}")
                                
                                # 尝试解析JSON
                                try:
                                    import json
                                    json_data = json.loads(content)
                                    print(f"      ✅ JSON解析成功")
                                    # 递归查找url和uid
                                    def find_url_uid(obj, path=""):
                                        if isinstance(obj, dict):
                                            for key, value in obj.items():
                                                result = find_url_uid(value, f"{path}.{key}")
                                                if result:
                                                    return result
                                        elif isinstance(obj, list):
                                            for i, item in enumerate(obj):
                                                result = find_url_uid(item, f"{path}[{i}]")
                                                if result:
                                                    return result
                                        elif isinstance(obj, str):
                                            if '.m3u8' in obj and obj.startswith('http'):
                                                return {'path': path, 'value': obj, 'type': 'm3u8'}
                                            elif ('url' in path.lower() or 'link' in path.lower()) and obj.startswith('http'):
                                                return {'path': path, 'value': obj, 'type': 'url'}
                                        return None
                                    
                                    result = find_url_uid(json_data)
                                    if result:
                                        print(f"      ✅ 找到{result['type']}: {result['value']}")
                                        resp_info['found_data'] = result
                                except:
                                    pass
                        except Exception as e:
                            # 忽略错误，继续监听其他响应
                            pass
                
                page.on('request', handle_request)
                page.on('response', handle_response)
                
                # 监听页面导航事件
                navigation_count = 0
                def handle_navigation(frame):
                    nonlocal navigation_count
                    navigation_count += 1
                    if navigation_count > 1:
                        print(f"   🔄 检测到页面导航 (#{navigation_count})")
                
                page.on('framenavigated', handle_navigation)
                
                try:
                    # 步骤1: 分析主页面
                    main_page_info = await self.analyze_main_page(page, parser_url, video_url)
                    if not main_page_info or not main_page_info.get('iframes'):
                        print("\n❌ 未能获取iframe信息")
                        return None
                    
                    # 获取第一个iframe URL
                    iframe_url = main_page_info['iframes'][0]['src']
                    if not iframe_url:
                        print("\n❌ iframe URL为空")
                        return None
                    
                    # 步骤2: 分析iframe页面
                    iframe_info = await self.analyze_iframe_page(page, iframe_url)
                    
                    # 等待页面稳定（防止不断导航）
                    print(f"\n   ⏳ 等待页面稳定（防止导航）...")
                    try:
                        # 等待一段时间，确保没有新的导航
                        for i in range(10):
                            await asyncio.sleep(2)
                            current_url = page.url
                            # 如果URL稳定了，跳出循环
                            if i > 0:
                                await asyncio.sleep(1)
                                new_url = page.url
                                if current_url == new_url:
                                    print(f"   ✅ 页面已稳定: {current_url}")
                                    break
                    except:
                        pass
                    
                    # 获取当前URL（可能已经因为点击按钮而跳转）
                    current_url = page.url
                    print(f"\n   📍 当前页面URL: {current_url}")
                    
                    # 如果URL发生了变化，可能需要重新分析
                    if current_url != iframe_url and 'getdata.staticfile.link' not in current_url:
                        print(f"   🔄 页面已跳转，使用新URL继续分析...")
                        # 可能需要重新访问iframe
                        iframe_info = await self.analyze_iframe_page(page, current_url)
                    
                    # 检查是否有嵌套iframe需要访问
                    nested_iframe = iframe_info.get('nested_iframe') if iframe_info else None
                    iframe_frame = None
                    config = None
                    
                    if nested_iframe:
                        print(f"\n   🔄 发现嵌套iframe: {nested_iframe}")
                        print(f"   💡 使用iframe frame API访问嵌套内容...")
                        
                        # 等待iframe加载完成
                        try:
                            # 等待iframe元素出现
                            print(f"   ⏳ 等待iframe元素加载...")
                            await page.wait_for_selector('iframe', timeout=30000)
                            await asyncio.sleep(3)  # 等待iframe开始加载
                            
                            # 获取所有iframe元素
                            iframe_elements = await page.query_selector_all('iframe')
                            print(f"   📋 找到 {len(iframe_elements)} 个iframe元素")
                            
                            # 尝试获取每个iframe的frame对象
                            for idx, iframe_element in enumerate(iframe_elements):
                                try:
                                    iframe_src = await iframe_element.get_attribute('src')
                                    print(f"   📍 iframe[{idx}] src: {iframe_src}")
                                    
                                    # 等待iframe frame可用（增加重试机制）
                                    iframe_frame = None
                                    for retry in range(5):
                                        try:
                                            await asyncio.sleep(2)
                                            iframe_frame = await iframe_element.content_frame()
                                            if iframe_frame:
                                                break
                                        except Exception as e:
                                            if retry < 4:
                                                print(f"   ⏳ 重试获取iframe frame ({retry+1}/5)...")
                                                await asyncio.sleep(2)
                                            else:
                                                print(f"   ⚠️ 无法获取iframe frame: {e}")
                                    
                                    if iframe_frame:
                                        print(f"   ✅ 成功获取iframe[{idx}] frame对象")
                                        
                                        # 等待iframe内容加载
                                        try:
                                            await iframe_frame.wait_for_load_state('domcontentloaded', timeout=30000)
                                            await asyncio.sleep(15)  # 增加等待时间，确保JavaScript执行
                                        except Exception as e:
                                            print(f"   ⚠️ 等待iframe加载超时，继续尝试: {e}")
                                            await asyncio.sleep(15)
                                        
                                        # 检查frame是否仍然有效
                                        try:
                                            # 尝试执行一个简单的evaluate来检查frame是否有效
                                            await iframe_frame.evaluate("() => true")
                                        except Exception as e:
                                            print(f"   ⚠️ iframe frame已失效，重新获取: {e}")
                                            # 重新获取frame
                                            try:
                                                iframe_frame = await iframe_element.content_frame()
                                                await asyncio.sleep(5)
                                            except:
                                                iframe_frame = None
                                        
                                        if iframe_frame:
                                            # 在iframe frame中查找配置对象
                                            print(f"\n   🔍 在iframe frame中查找配置对象...")
                                            try:
                                                config = await self.extract_config_from_frame(iframe_frame)
                                                
                                                if config:
                                                    print(f"   ✅ 在iframe中找到配置对象")
                                                    break  # 找到配置后退出循环
                                                else:
                                                    print(f"   ⚠️ iframe[{idx}]中未找到配置对象")
                                            except Exception as e:
                                                if "detached" in str(e).lower() or "detached" in str(type(e)):
                                                    print(f"   ⚠️ iframe frame已分离，尝试重新获取: {e}")
                                                    # 重新获取frame
                                                    try:
                                                        await asyncio.sleep(3)
                                                        iframe_frame = await iframe_element.content_frame()
                                                        if iframe_frame:
                                                            config = await self.extract_config_from_frame(iframe_frame)
                                                            if config:
                                                                break
                                                    except:
                                                        pass
                                                else:
                                                    print(f"   ⚠️ 提取配置时出错: {e}")
                                    else:
                                        print(f"   ⚠️ 无法获取iframe[{idx}] frame对象")
                                except Exception as e:
                                    print(f"   ⚠️ 处理iframe[{idx}]时出错: {e}")
                                    continue
                            
                            # 如果所有iframe frame都失败，尝试直接访问URL
                            if not config:
                                print(f"   💡 所有iframe frame访问失败，尝试直接访问嵌套iframe URL...")
                                config = await self.extract_config_from_iframe(page, nested_iframe)
                                
                        except Exception as e:
                            print(f"   ⚠️ 访问iframe frame失败: {e}")
                            import traceback
                            traceback.print_exc()
                            print(f"   💡 尝试直接访问嵌套iframe URL...")
                            config = await self.extract_config_from_iframe(page, nested_iframe)
                    else:
                        # 没有嵌套iframe，直接提取配置
                        final_iframe_url = page.url
                        if final_iframe_url != iframe_url:
                            print(f"\n   🔄 iframe已重定向到: {final_iframe_url}")
                            iframe_url = final_iframe_url
                        
                        # 步骤3: 提取配置对象（使用最终URL）
                    # 如果页面不断导航，直接访问media.staticfile.link
                    if nested_iframe and 'media.staticfile.link' in nested_iframe:
                        print(f"\n   💡 检测到页面不断导航，直接访问media.staticfile.link...")
                        # 直接访问media.staticfile.link，跳过getdata.staticfile.link
                        config = await self.extract_config_from_iframe(page, nested_iframe)
                    else:
                        config = await self.extract_config_from_iframe(page, iframe_url)
                    if not config:
                        print("\n❌ 未能提取配置对象")
                        print("\n💡 建议：")
                        print("   1. 检查浏览器控制台是否有错误")
                        print("   2. 手动检查iframe页面中的JavaScript对象")
                        print("   3. 查看保存的HTML文件")
                        return None
                    
                    # 步骤4: 查找解密函数（在iframe frame或主页面中）
                    decrypt_function = None
                    if iframe_frame:
                        decrypt_function = await self.find_decrypt_function_in_frame(iframe_frame)
                    else:
                        decrypt_function = await self.find_decrypt_function(page)
                    
                    # 步骤5: 测试解密
                    encrypted_url = config['url']
                    decrypted_url = None
                    if decrypt_function:
                        if iframe_frame:
                            decrypted_url = await self.test_decrypt_in_frame(iframe_frame, encrypted_url, decrypt_function)
                        else:
                            decrypted_url = await self.test_decrypt(page, encrypted_url, decrypt_function)
                    
                    # 汇总分析结果
                    analysis_result = {
                        'parser_url': parser_url,
                        'video_url': video_url,
                        'iframe_url': iframe_url,
                        'config': config,
                        'decrypt_function': decrypt_function,
                        'decrypted_url': decrypted_url,
                        'network_requests': network_requests[:100],  # 保存前100个请求
                        'network_responses': network_responses[:100],  # 保存前100个响应
                        'main_page_info': main_page_info,
                        'iframe_info': iframe_info
                    }
                    
                    # 特别检查UPDATEDMKU.php API
                    print(f"\n   🔍 特别检查UPDATEDMKU.php API...")
                    updatedmku_response = None
                    for resp in network_responses:
                        if 'UPDATEDMKU.php' in resp.get('url', ''):
                            print(f"   ✅ 找到UPDATEDMKU.php响应: {resp['url']}")
                            if 'content' in resp:
                                content = resp['content']
                                print(f"      📄 响应内容预览: {content[:500]}")
                                
                                # 尝试解析JSON
                                try:
                                    json_data = json.loads(content)
                                    print(f"      ✅ JSON解析成功")
                                    updatedmku_response = json_data
                                    
                                    # 递归查找m3u8链接
                                    def find_m3u8(obj, path=""):
                                        urls = []
                                        if isinstance(obj, dict):
                                            for key, value in obj.items():
                                                urls.extend(find_m3u8(value, f"{path}.{key}"))
                                        elif isinstance(obj, list):
                                            for i, item in enumerate(obj):
                                                urls.extend(find_m3u8(item, f"{path}[{i}]"))
                                        elif isinstance(obj, str):
                                            if '.m3u8' in obj and obj.startswith('http'):
                                                urls.append({'path': path, 'url': obj})
                                        return urls
                                    
                                    m3u8_in_json = find_m3u8(json_data)
                                    if m3u8_in_json:
                                        print(f"      ✅ 在JSON中找到m3u8链接:")
                                        for item in m3u8_in_json:
                                            print(f"         {item['url']}")
                                except:
                                    # 不是JSON，检查文本中的m3u8
                                    if 'm3u8' in content.lower():
                                        import re
                                        m3u8_patterns = [
                                            r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
                                        ]
                                        for pattern in m3u8_patterns:
                                            matches = re.findall(pattern, content, re.IGNORECASE)
                                            for match in matches:
                                                if match.startswith('http'):
                                                    print(f"      ✅ 在响应中找到m3u8: {match}")
                            break
                    
                    # 检查网络响应中是否有m3u8链接或配置数据
                    print(f"\n   🔍 检查网络响应中的数据...")
                    m3u8_urls = []
                    config_urls = []
                    
                    for resp in network_responses:
                        # 检查URL中是否包含m3u8
                        if 'm3u8' in resp['url'].lower():
                            m3u8_urls.append(resp['url'])
                            print(f"      ✅ 找到m3u8链接（URL）: {resp['url']}")
                        
                        # 检查响应内容中是否有m3u8或配置数据
                        if 'content' in resp:
                            content = resp['content']
                            if 'm3u8' in content.lower():
                                import re
                                m3u8_patterns = [
                                    r'https?://[^\s"\'<>]+\.m3u8[^\s"\'<>]*',
                                    r'["\']([^"\']+\.m3u8[^"\']*)["\']',
                                ]
                                for pattern in m3u8_patterns:
                                    matches = re.findall(pattern, content, re.IGNORECASE)
                                    for match in matches:
                                        url = match if isinstance(match, str) else match[0] if match else None
                                        if url and url.startswith('http') and url not in m3u8_urls:
                                            m3u8_urls.append(url)
                                            print(f"      ✅ 找到m3u8链接（内容）: {url}")
                            
                            # 检查是否有配置数据（url和uid）
                            if 'found_data' in resp:
                                found = resp['found_data']
                                if found['type'] == 'm3u8':
                                    if found['value'] not in m3u8_urls:
                                        m3u8_urls.append(found['value'])
                                elif found['type'] == 'url':
                                    config_urls.append(found['value'])
                                    print(f"      ✅ 找到配置URL: {found['value']}")
                    
                    if m3u8_urls:
                        print(f"\n   ✅ 在网络响应中找到 {len(m3u8_urls)} 个m3u8链接:")
                        for url in m3u8_urls:
                            print(f"      - {url}")
                        analysis_result['m3u8_urls'] = m3u8_urls
                    
                    if config_urls:
                        print(f"\n   ✅ 在网络响应中找到 {len(config_urls)} 个配置URL:")
                        for url in config_urls:
                            print(f"      - {url}")
                        analysis_result['config_urls'] = config_urls
                    
                    if updatedmku_response:
                        analysis_result['updatedmku_response'] = updatedmku_response
                        print(f"\n   ✅ UPDATEDMKU.php API响应已保存")
                    
                    # 保存分析结果
                    with open('playerjy_analysis_result.json', 'w', encoding='utf-8') as f:
                        json.dump(analysis_result, f, indent=2, ensure_ascii=False, default=str)
                    print(f"\n✅ 分析结果已保存到: playerjy_analysis_result.json")
                    
                    # 打印总结
                    print("\n" + "=" * 60)
                    print("📊 分析总结")
                    print("=" * 60)
                    print(f"\n1. iframe URL: {iframe_url}")
                    print(f"\n2. 配置对象:")
                    print(f"   来源: {config.get('source', 'unknown')}")
                    print(f"   url: {config.get('url', 'N/A')[:100]}...")
                    print(f"   uid: {config.get('uid', 'N/A')}")
                    
                    if decrypt_function:
                        print(f"\n3. 解密函数: {decrypt_function}")
                    else:
                        print(f"\n3. 解密函数: 未找到")
                    
                    if decrypted_url:
                        print(f"\n4. 解密后的URL: {decrypted_url}")
                        print(f"\n✅ 解析逻辑分析完成！")
                    else:
                        print(f"\n4. 解密后的URL: 解密失败")
                        print(f"\n⚠️ 需要进一步分析解密逻辑")
                    
                    # 保持浏览器打开一段时间，方便查看
                    print(f"\n⏸️ 浏览器将保持打开15秒，您可以手动检查...")
                    await asyncio.sleep(15)
                    
                    await context.close()
                    await browser.close()
                    
                    return analysis_result
                        
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
            # 清理资源
            if chrome_process:
                try:
                    chrome_process.terminate()
                    chrome_process.wait(timeout=5)
                    print('[+] Chrome进程已关闭')
                except:
                    try:
                        chrome_process.kill()
                        print('[+] Chrome进程已强制关闭')
                    except:
                        pass
            
            if user_data_dir:
                cleanup_user_data(user_data_dir)
                print('[+] 临时用户数据目录已清理')


async def main():
    """主函数"""
    parser_url = "https://jx.playerjy.com"
    video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    
    # 可以手动指定Chrome路径，如果自动检测失败
    chrome_path = None  # 例如: r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    
    analyzer = PlayerJYParserAnalyzer()
    result = await analyzer.analyze_parser(parser_url, video_url, chrome_path=chrome_path)
    
    if not result:
        print("\n❌ 分析失败")


if __name__ == '__main__':
    asyncio.run(main())
