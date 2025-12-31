#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
批量注册 jx.2s0.cn 账号脚本
使用浏览器自动化完成注册流程，获取uid和key
"""

import asyncio
import json
import random
import string
import subprocess
import tempfile
import socket
import time
import os
import shutil
import requests
from typing import Optional, Dict, List
from datetime import datetime, timedelta
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
            print("❌ 未找到Chrome浏览器")
            return None, None, None
    
    debug_port = get_free_port()
    temp_user_data_dir = tempfile.mkdtemp(prefix="chrome_registration_")
    
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
        try:
            shutil.rmtree(user_data_dir, ignore_errors=True)
        except:
            pass


def generate_random_user_agent() -> str:
    """生成随机User-Agent"""
    chrome_versions = ['120.0.0.0', '121.0.0.0', '122.0.0.0', '123.0.0.0', '124.0.0.0']
    chrome_version = random.choice(chrome_versions)
    webkit_version = '537.36'
    return f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{webkit_version} (KHTML, like Gecko) Chrome/{chrome_version} Safari/{webkit_version}'


def generate_random_viewport() -> Dict:
    """生成随机视口大小"""
    # 常见的屏幕分辨率
    viewports = [
        {'width': 1920, 'height': 1080},
        {'width': 1366, 'height': 768},
        {'width': 1536, 'height': 864},
        {'width': 1440, 'height': 900},
        {'width': 1600, 'height': 900},
    ]
    return random.choice(viewports)


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


def generate_random_email() -> str:
    """
    生成随机邮箱地址（使用英文名+数字的方式，更真实）
    
    返回:
        邮箱地址字符串
    """
    # 常见英文名列表
    first_names = [
        'alex', 'alice', 'amy', 'anna', 'bob', 'chris', 'david', 'emily', 'james', 'jane',
        'john', 'kate', 'lisa', 'mike', 'mary', 'nick', 'sarah', 'tom', 'will', 'zoe',
        'ben', 'carl', 'diana', 'eric', 'frank', 'grace', 'henry', 'ivy', 'jack', 'kelly',
        'lucas', 'mia', 'nina', 'oliver', 'paul', 'rose', 'sam', 'tina', 'victor', 'wendy',
        'adam', 'betty', 'cathy', 'daniel', 'ella', 'fiona', 'george', 'helen', 'ian', 'julia',
        'kevin', 'lily', 'matt', 'nancy', 'oscar', 'patty', 'quinn', 'rachel', 'steve', 'tracy'
    ]
    
    # 生成邮箱用户名的方式
    email_style = random.choice(['name_birthday', 'name_number', 'name_name', 'name_initial'])
    
    if email_style == 'name_birthday':
        # 方式1: 英文名 + 生日（如：alex1990）
        name = random.choice(first_names)
        year = random.randint(1980, 2005)  # 合理的出生年份范围
        username = f"{name}{year}"
    elif email_style == 'name_number':
        # 方式2: 英文名 + 随机数字（如：alex123）
        name = random.choice(first_names)
        number = random.randint(1, 9999)
        username = f"{name}{number}"
    elif email_style == 'name_name':
        # 方式3: 两个英文名组合（如：alexjames）
        name1 = random.choice(first_names)
        name2 = random.choice(first_names)
        # 避免两个名字相同
        while name2 == name1:
            name2 = random.choice(first_names)
        username = f"{name1}{name2}"
    else:  # name_initial
        # 方式4: 英文名 + 首字母 + 数字（如：alexj123）
        name = random.choice(first_names)
        initial = random.choice(string.ascii_lowercase)
        number = random.randint(1, 999)
        username = f"{name}{initial}{number}"
    
    # 随机添加一些变体（小概率）
    if random.random() < 0.1:  # 10%的概率添加下划线或点
        if random.random() < 0.5:
            # 在名字和数字之间添加下划线
            if '_' not in username:
                parts = username.rsplit(str(random.randint(0, 9)), 1)
                if len(parts) == 2 and parts[1]:
                    username = f"{parts[0]}_{parts[1]}"
        else:
            # 在名字和数字之间添加点
            if '.' not in username:
                parts = username.rsplit(str(random.randint(0, 9)), 1)
                if len(parts) == 2 and parts[1]:
                    username = f"{parts[0]}.{parts[1]}"
    
    # 邮箱域名（更真实的分布）
    domains = [
        'gmail.com', 'gmail.com', 'gmail.com',  # gmail更常见，增加权重
        'yahoo.com', 'yahoo.com',
        'outlook.com', 'outlook.com',
        'hotmail.com', 'hotmail.com',
        'qq.com', 'qq.com',  # 国内常用
        '163.com', '163.com',  # 国内常用
        'sina.com', 'sohu.com',  # 其他国内邮箱
    ]
    domain = random.choice(domains)
    
    return f"{username}@{domain}"


def get_proxy_ip(proxy_api_url: str = None) -> Optional[Dict]:
    """
    获取代理IP
    
    参数:
        proxy_api_url: 代理API地址（如果为None，使用默认API）
    
    返回:
        包含host和port的字典，失败返回None
    """
    if proxy_api_url is None:
        # 默认使用JSON格式的API
        proxy_api_url = "https://white.1024proxy.com/white/api?region=jp&num=1&time=10&format=0&type=json"
    
    try:
        response = requests.get(proxy_api_url, timeout=10)
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '').lower()
            
            # 尝试解析JSON格式
            if 'json' in content_type or 'application/json' in content_type:
                try:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        proxy = data[0]
                        if 'host' in proxy and 'port' in proxy:
                            return {
                                'server': f"http://{proxy['host']}:{proxy['port']}",
                                'host': proxy['host'],
                                'port': str(proxy['port'])
                            }
                    elif isinstance(data, dict) and 'host' in data and 'port' in data:
                        return {
                            'server': f"http://{data['host']}:{data['port']}",
                            'host': data['host'],
                            'port': str(data['port'])
                        }
                except json.JSONDecodeError:
                    pass
            
            # 尝试解析文本格式（IP:PORT）
            text = response.text.strip()
            if ':' in text and not text.startswith('{'):
                # 可能是 IP:PORT 格式
                parts = text.split(':')
                if len(parts) == 2:
                    host = parts[0].strip()
                    port = parts[1].strip()
                    # 验证IP和端口格式
                    if host.replace('.', '').isdigit() and port.isdigit():
                        return {
                            'server': f"http://{host}:{port}",
                            'host': host,
                            'port': port
                        }
            
            # 如果都不匹配，尝试解析JSON（即使content-type不是json）
            try:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    proxy = data[0]
                    if 'host' in proxy and 'port' in proxy:
                        return {
                            'server': f"http://{proxy['host']}:{proxy['port']}",
                            'host': proxy['host'],
                            'port': str(proxy['port'])
                        }
            except:
                pass
            
            print(f"   ⚠️  代理API返回格式异常: {text[:200]}")
            return None
        else:
            print(f"   ⚠️  代理API请求失败: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"   ⚠️  获取代理IP失败: {e}")
        return None


async def test_proxy(proxy: Dict) -> bool:
    """
    测试代理是否可用
    
    参数:
        proxy: 代理配置字典
    
    返回:
        是否可用
    """
    try:
        test_url = "http://httpbin.org/ip"
        proxies = {
            'http': proxy['server'],
            'https': proxy['server']
        }
        response = requests.get(test_url, proxies=proxies, timeout=10)
        if response.status_code == 200:
            print(f"   ✅ 代理测试成功: {proxy['host']}:{proxy['port']}")
            return True
        return False
    except Exception as e:
        print(f"   ⚠️  代理测试失败: {e}")
        return False


async def check_slider_ready(page: Page, text_xpath: str = None, timeout: int = 10) -> bool:
    """
    检查滑块是否准备好（文字为"滑动到右侧登录"）
    
    参数:
        page: Playwright页面对象
        text_xpath: 文字提示的XPath（如果为None，使用多种方式查找）
        timeout: 超时时间（秒）
    
    返回:
        是否准备好
    """
    try:
        # 如果未提供XPath，尝试多种方式查找文字元素
        if text_xpath is None:
            # 方式1: 通过class="label"查找
            try:
                label_element = page.locator('div.label:has-text("滑动到右侧登录")')
                if await label_element.count() > 0:
                    text_content = await label_element.first.text_content()
                    if text_content and "滑动到右侧登录" in text_content.strip():
                        print(f"   ✅ 滑块已准备好（通过label查找）: {text_content.strip()}")
                        return True
            except:
                pass
            
            # 方式2: 通过XPath查找（用户提供的正确XPath）
            text_xpath = "/html/body/div/div[1]/div/div/form/div/div[2]/div/div/div[1]/div/div[1]"
        
        # 等待文字元素出现
        try:
            await page.wait_for_selector(f"xpath={text_xpath}", timeout=timeout * 1000)
        except:
            # 如果XPath失败，尝试通过文本内容查找
            try:
                text_element = page.locator('text="滑动到右侧登录"')
                if await text_element.count() > 0:
                    text_content = await text_element.first.text_content()
                    if text_content and "滑动到右侧登录" in text_content.strip():
                        print(f"   ✅ 滑块已准备好（通过文本查找）: {text_content.strip()}")
                        return True
            except:
                pass
            
            print(f"   ⚠️  未找到文字元素，XPath: {text_xpath}")
            return False
        
        # 获取文字内容
        text_element = page.locator(f"xpath={text_xpath}")
        text_content = await text_element.text_content()
        
        if text_content and "滑动到右侧登录" in text_content.strip():
            print(f"   ✅ 滑块已准备好: {text_content.strip()}")
            return True
        else:
            print(f"   ⚠️  滑块未准备好，当前文字: {text_content.strip() if text_content else '无'}")
            return False
    except Exception as e:
        print(f"   ⚠️  检查滑块状态失败: {e}")
        # 尝试备用方法：直接查找包含"滑动到右侧登录"的元素
        try:
            all_text = await page.locator('body').text_content()
            if all_text and "滑动到右侧登录" in all_text:
                print(f"   ✅ 滑块已准备好（通过页面文本查找）")
                return True
        except:
            pass
        return False


async def slide_slider(page: Page, slider_xpath: str, retry_count: int = 2) -> bool:
    """
    滑动滑块验证
    
    参数:
        page: Playwright页面对象
        slider_xpath: 滑块的XPath
        retry_count: 重试次数
    
    返回:
        是否成功滑动
    """
    try:
        # 等待滑块元素出现
        await page.wait_for_selector(f"xpath={slider_xpath}", timeout=10000)
        await asyncio.sleep(0.5)  # 等待元素稳定
        
        # 检查滑块是否准备好（文字为"滑动到右侧登录"）
        print("   🔍 检查滑块状态...")
        slider_ready = await check_slider_ready(page)
        
        if not slider_ready:
            # 如果未准备好，等待一段时间后重试
            print("   ⏳ 等待滑块准备就绪...")
            for i in range(5):  # 最多等待5次
                await asyncio.sleep(1)
                slider_ready = await check_slider_ready(page, timeout=2)
                if slider_ready:
                    break
                print(f"   ⏳ 等待中... ({i+1}/5)")
            
            if not slider_ready:
                print("   ❌ 滑块未准备好，无法滑动")
                return False
        
        # 获取滑块元素（尝试多种方式）
        slider = None
        box = None
        
        # 方式1: 使用提供的XPath
        try:
            slider = page.locator(f"xpath={slider_xpath}")
            box = await slider.bounding_box()
            if box and box['width'] > 0 and box['height'] > 0:
                print(f"   ✅ 找到滑块元素（XPath）")
        except:
            pass
        
        # 方式2: 如果XPath指向的是label，尝试查找button元素
        if not slider or not box:
            try:
                # 尝试查找class="button"的元素（滑块按钮）
                button_element = page.locator('div.slider div.button')
                if await button_element.count() > 0:
                    slider = button_element.first
                    box = await slider.bounding_box()
                    if box and box['width'] > 0 and box['height'] > 0:
                        print(f"   ✅ 找到滑块元素（button class）")
            except:
                pass
        
        # 方式3: 尝试查找track内的button
        if not slider or not box:
            try:
                # 尝试查找track内的button
                button_element = page.locator('div.track div.button, div.slider div.track div.button')
                if await button_element.count() > 0:
                    slider = button_element.first
                    box = await slider.bounding_box()
                    if box and box['width'] > 0 and box['height'] > 0:
                        print(f"   ✅ 找到滑块元素（track内的button）")
            except:
                pass
        
        # 方式4: 如果slider_xpath指向的是容器，尝试查找内部的button
        if not slider or not box:
            try:
                container = page.locator(f"xpath={slider_xpath}")
                # 查找容器内的button
                button_element = container.locator('div.button')
                if await button_element.count() > 0:
                    slider = button_element.first
                    box = await slider.bounding_box()
                    if box and box['width'] > 0 and box['height'] > 0:
                        print(f"   ✅ 找到滑块元素（容器内的button）")
            except:
                pass
        
        if not slider or not box:
            print("   ❌ 无法获取滑块位置，尝试所有方法都失败")
            return False
        
        # 计算起始位置（滑块中心）
        start_x = box['x'] + box['width'] / 2
        start_y = box['y'] + box['height'] / 2
        
        # 尝试找到滑块条的容器（父元素的父元素通常是滑块条）
        try:
            # 向上查找滑块条容器
            slider_track = slider.locator('xpath=ancestor::div[contains(@class, "slider") or contains(@class, "track")]')
            track_count = await slider_track.count()
            
            if track_count > 0:
                track_box = await slider_track.first.bounding_box()
                if track_box:
                    # 滑动到滑块条的右端
                    end_x = track_box['x'] + track_box['width'] - box['width'] / 2
                    print(f"   📏 找到滑块条，宽度: {track_box['width']:.0f}px")
                else:
                    # 如果无法获取容器，使用固定距离（通常是200-300px）
                    end_x = start_x + 250
                    print(f"   📏 使用固定滑动距离: 250px")
            else:
                # 尝试查找父元素
                parent = slider.locator('..')
                parent_box = await parent.bounding_box()
                if parent_box:
                    end_x = parent_box['x'] + parent_box['width'] - box['width'] / 2
                    print(f"   📏 使用父元素宽度: {parent_box['width']:.0f}px")
                else:
                    end_x = start_x + 250
                    print(f"   📏 使用固定滑动距离: 250px")
        except Exception as e:
            print(f"   ⚠️  查找滑块条失败，使用固定距离: {e}")
            end_x = start_x + 250
        
        # 确保滑动距离合理
        if end_x <= start_x:
            end_x = start_x + 250
        
        print(f"   📍 滑动范围: {start_x:.0f}px -> {end_x:.0f}px (距离: {end_x - start_x:.0f}px)")
        
        # 执行滑动操作
        for i in range(retry_count):
            print(f"   🔄 第 {i+1} 次滑动滑块...")
            
            # 使用鼠标模拟滑动（更精确和可靠）
            # 鼠标移动到滑块中心
            await page.mouse.move(start_x, start_y)
            await asyncio.sleep(0.2)
            
            # 按下鼠标
            await page.mouse.down()
            await asyncio.sleep(0.1)
            
            # 模拟人类滑动（分段移动，添加曲线和抖动）
            steps = 30
            for step in range(steps):
                progress = (step + 1) / steps
                # 使用缓动函数，模拟人类加速和减速
                eased_progress = progress * progress * (3 - 2 * progress)  # smoothstep
                
                current_x = start_x + (end_x - start_x) * eased_progress
                # 添加轻微的垂直抖动，模拟人类手抖
                jitter_y = start_y + random.uniform(-1, 1) * (1 - abs(progress - 0.5) * 2)
                
                await page.mouse.move(current_x, jitter_y)
                await asyncio.sleep(random.uniform(0.015, 0.025))
            
            # 释放鼠标
            await page.mouse.up()
            await asyncio.sleep(0.1)
            
            # 等待0.3秒后再次滑动（如果需要）
            if i < retry_count - 1:
                await asyncio.sleep(0.3)
        
        return True
        
    except Exception as e:
        print(f"   ❌ 滑动滑块失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def fill_form(page: Page, email: str, password: str) -> bool:
    """
    填写表单（邮箱和密码）
    
    参数:
        page: Playwright页面对象
        email: 邮箱地址
        password: 密码
    
    返回:
        是否成功填写
    """
    try:
        # 填写邮箱
        email_xpath = "/html/body/div/div[1]/div/div/form/div/input[1]"
        print(f"   ✏️  填写邮箱: {email}")
        email_input = page.locator(f"xpath={email_xpath}")
        await email_input.wait_for(state='visible', timeout=10000)
        await email_input.fill(email)
        await asyncio.sleep(0.5)
        
        # 填写密码
        password_xpath = "/html/body/div/div[1]/div/div/form/div/input[2]"
        print(f"   ✏️  填写密码: {password}")
        password_input = page.locator(f"xpath={password_xpath}")
        await password_input.wait_for(state='visible', timeout=10000)
        await password_input.fill(password)
        await asyncio.sleep(0.5)
        
        return True
    except Exception as e:
        print(f"   ❌ 填写表单失败: {e}")
        return False


async def check_first_slide_status(page: Page) -> str:
    """
    检查第一次滑动后的状态
    
    参数:
        page: Playwright页面对象
    
    返回:
        'ready_for_second': 可以滑动第二次
        'anti_crawler': 触发反爬虫检测，需要更换浏览器和IP
        'unknown': 未知状态
    """
    try:
        # 检查是否存在第二次滑动的提示元素
        second_slide_xpath = "/html/body/div/div[1]/div/div/form/div/div[1]/b"
        try:
            second_slide_element = page.locator(f"xpath={second_slide_xpath}")
            if await second_slide_element.count() > 0:
                element_text = await second_slide_element.text_content()
                text_content = element_text.strip() if element_text else ""
                
                # 如果显示"请稍后"，等待0.5秒后再次检查
                if "请稍后" in text_content or "请稍候" in text_content:
                    print(f"   ⏳ 检测到'请稍后'，等待0.5秒后重新检查...")
                    await asyncio.sleep(0.5)
                    
                    # 再次检查元素文本
                    element_text = await second_slide_element.text_content()
                    text_content = element_text.strip() if element_text else ""
                    
                    # 如果0.5秒后仍然是"请稍后"，说明触发反爬虫
                    if "请稍后" in text_content or "请稍候" in text_content:
                        # 检查滑块状态
                        slider_status = None
                        try:
                            slider_elements = page.locator('div.slider, div.label, div[class*="slider"]')
                            for i in range(await slider_elements.count()):
                                slider_text = await slider_elements.nth(i).text_content()
                                if slider_text and "验证通过" in slider_text:
                                    slider_status = "验证通过"
                                    break
                        except:
                            pass
                        
                        if slider_status == "验证通过":
                            print(f"   ⚠️  触发反爬虫检测: 0.5秒后仍显示'请稍后'，且滑块显示'验证通过'")
                            return 'anti_crawler'
                        else:
                            print(f"   ⚠️  触发反爬虫检测: 0.5秒后仍显示'请稍后'")
                            return 'anti_crawler'
                    else:
                        # 如果0.5秒后不再是"请稍后"，说明可以滑动第二次
                        print(f"   ✅ 检测到第二次滑动提示元素: {text_content}")
                        return 'ready_for_second'
                else:
                    # 如果不是"请稍后"，说明可以滑动第二次
                    print(f"   ✅ 检测到第二次滑动提示元素: {text_content}")
                    return 'ready_for_second'
        except:
            pass
        
        # 检查是否有"请稍后"和"验证通过"的状态
        try:
            # 获取页面文本内容
            page_text = await page.locator('body').text_content()
            
            # 检查滑块状态
            slider_status = None
            try:
                # 尝试查找滑块状态文字
                slider_elements = page.locator('div.slider, div.label, div[class*="slider"]')
                for i in range(await slider_elements.count()):
                    element_text = await slider_elements.nth(i).text_content()
                    if element_text:
                        if "验证通过" in element_text:
                            slider_status = "验证通过"
                            break
                        elif "滑动到右侧登录" in element_text:
                            slider_status = "滑动到右侧登录"
                            break
            except:
                pass
            
            # 检查是否有"请稍后"
            has_waiting = False
            if page_text:
                if "请稍后" in page_text or "请稍候" in page_text:
                    has_waiting = True
            
            # 如果滑块显示"验证通过"且有"请稍后"，说明触发反爬虫
            if slider_status == "验证通过" and has_waiting:
                print(f"   ⚠️  检测到反爬虫状态: 滑块显示'验证通过'，页面显示'请稍后'")
                return 'anti_crawler'
            
        except Exception as e:
            print(f"   ⚠️  检查状态时出错: {e}")
        
        return 'unknown'
    except Exception as e:
        print(f"   ⚠️  检查第一次滑动状态失败: {e}")
        return 'unknown'


async def check_registration_success(page: Page, timeout: int = 5) -> bool:
    """
    检查注册是否成功（通过URL判断）
    
    参数:
        page: Playwright页面对象
        timeout: 等待超时时间（秒）
    
    返回:
        是否成功
    """
    try:
        # 等待URL变化或页面跳转
        await page.wait_for_url("**/user/index", timeout=timeout * 1000)
        return True
    except:
        # 检查当前URL
        current_url = page.url
        if "user/index" in current_url:
            return True
        
        # 等待一下，可能还在处理
        await asyncio.sleep(2)
        current_url = page.url
        return "user/index" in current_url


async def register_account(page: Page, email: str, password: str, max_retries: int = 2) -> Optional[Dict]:
    """
    注册单个账号（带重试逻辑）
    
    参数:
        page: Playwright页面对象
        email: 邮箱地址
        password: 密码
        max_retries: 最大重试次数
    
    返回:
        包含uid和key的字典，失败返回None
    """
    login_url = "https://json.2s0.cn:5678/user/login"
    slider_xpath = "/html/body/div/div[1]/div/div/form/div/div[2]/div/div/div[1]/div/div[1]"
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                print(f"\n   🔄 第 {attempt + 1} 次尝试注册...")
            
            # 1. 访问登录页面
            print(f"\n📝 访问登录页面: {login_url}")
            await page.goto(login_url, wait_until='domcontentloaded', timeout=60000)
            await asyncio.sleep(2)  # 等待页面加载
            
            # 2. 填写表单
            if not await fill_form(page, email, password):
                if attempt < max_retries - 1:
                    print("   🔄 刷新页面，重新尝试...")
                    await asyncio.sleep(1)
                    continue
                return None
            
            # 3. 滑动滑块（第一次）
            print(f"   🎯 第1次滑动滑块验证...")
            slide_success = await slide_slider(page, slider_xpath, retry_count=1)
            
            if not slide_success:
                print("   ⚠️  第1次滑块验证失败")
                
                # 第一次失败：刷新页面，重新输入
                if attempt < max_retries - 1:
                    print("   🔄 刷新页面，重新填写表单...")
                    await asyncio.sleep(1)
                    continue
                else:
                    # 最后一次尝试：先检查是否已经成功（可能滑块已经验证通过）
                    print("   🔍 检查是否已经注册成功...")
                    await asyncio.sleep(2)
                    if await check_registration_success(page, timeout=3):
                        print("   ✅ 检测到已成功跳转，继续提取信息...")
                    else:
                        print("   ❌ 滑块验证失败，且未检测到成功跳转")
                        return None
            
            # 4. 检查第一次滑动后的状态
            print("   🔍 检查第一次滑动后的状态...")
            await asyncio.sleep(2)  # 等待状态更新
            slide_status = await check_first_slide_status(page)
            
            if slide_status == 'anti_crawler':
                print("   ⚠️  触发反爬虫检测！需要更换浏览器和IP")
                # 返回特殊值，让调用者知道需要更换浏览器和IP
                return {'anti_crawler': True}
            
            # 5. 等待跳转到主页
            print("   ⏳ 等待注册完成...")
            if await check_registration_success(page, timeout=15):
                print("   ✅ 注册成功，已跳转到主页")
            else:
                # 检查是否需要第二次滑动
                slide_success_2 = False
                if slide_status == 'ready_for_second':
                    print("   ✅ 检测到可以滑动第二次，执行第二次滑动...")
                    slide_success_2 = await slide_slider(page, slider_xpath, retry_count=1)
                else:
                    # 如果第一次滑动后没有跳转，等待一段时间（代理IP可能较慢）
                    wait_time = random.uniform(3, 5)
                    print(f"   ⏳ 等待 {wait_time:.1f} 秒后尝试第2次滑动（代理IP可能较慢）...")
                    await asyncio.sleep(wait_time)
                    
                    # 再次检查是否已经跳转（可能在等待期间已经跳转）
                    if await check_registration_success(page, timeout=2):
                        print("   ✅ 等待期间已成功跳转")
                    else:
                        # 再次检查状态，看是否触发反爬虫
                        slide_status = await check_first_slide_status(page)
                        if slide_status == 'anti_crawler':
                            print("   ⚠️  触发反爬虫检测！需要更换浏览器和IP")
                            return {'anti_crawler': True}
                        elif slide_status == 'ready_for_second':
                            print("   ✅ 检测到可以滑动第二次，执行第二次滑动...")
                            slide_success_2 = await slide_slider(page, slider_xpath, retry_count=1)
                        else:
                            # 如果第一次滑动后没有跳转，尝试第二次滑动
                            print("   ⚠️  未检测到跳转，尝试第2次滑动滑块...")
                            slide_success_2 = await slide_slider(page, slider_xpath, retry_count=1)
                
                if slide_success_2:
                    # 检查第二次滑动后的状态
                    print("   🔍 检查第二次滑动后的状态...")
                    await asyncio.sleep(0.5)  # 等待状态更新
                    slide_status_2 = await check_first_slide_status(page)
                    
                    if slide_status_2 == 'anti_crawler':
                        print("   ⚠️  第二次滑动后触发反爬虫检测！需要更换浏览器和IP")
                        return {'anti_crawler': True}
                    
                    # 再次检查是否成功（代理IP可能较慢，等待更长时间）
                    wait_time = random.uniform(3, 5)
                    print(f"   ⏳ 等待 {wait_time:.1f} 秒后检查注册结果（代理IP可能较慢）...")
                    await asyncio.sleep(wait_time)
                    
                    if await check_registration_success(page, timeout=10):
                        print("   ✅ 第2次滑动后注册成功，已跳转到主页")
                    else:
                        # 第二次失败：尝试直接跳转看是否成功
                        print("   🔍 尝试直接访问主页，检查是否已注册...")
                        try:
                            await page.goto("https://json.2s0.cn:5678/user/index", wait_until='domcontentloaded', timeout=10000)
                            await asyncio.sleep(2)
                            current_url = page.url
                            if "user/index" in current_url or "user/information" in current_url:
                                print("   ✅ 直接访问成功，账号已注册")
                            else:
                                if attempt < max_retries - 1:
                                    print("   🔄 刷新页面，重新尝试...")
                                    await asyncio.sleep(1)
                                    continue
                                else:
                                    print("   ❌ 注册失败，未跳转到主页")
                                    return None
                        except:
                            if attempt < max_retries - 1:
                                print("   🔄 刷新页面，重新尝试...")
                                await asyncio.sleep(1)
                                continue
                            else:
                                print("   ❌ 注册失败")
                                return None
                else:
                    # 第二次滑动也失败：等待后尝试直接跳转
                    wait_time = random.uniform(2, 4)
                    print(f"   ⏳ 等待 {wait_time:.1f} 秒后尝试直接访问主页（代理IP可能较慢）...")
                    await asyncio.sleep(wait_time)
                    
                    print("   ⚠️  第2次滑块验证也失败，尝试直接访问主页...")
                    try:
                        await page.goto("https://json.2s0.cn:5678/user/index", wait_until='domcontentloaded', timeout=10000)
                        await asyncio.sleep(2)
                        current_url = page.url
                        if "user/index" in current_url or "user/information" in current_url:
                            print("   ✅ 直接访问成功，账号已注册")
                        else:
                            if attempt < max_retries - 1:
                                print("   🔄 刷新页面，重新尝试...")
                                await asyncio.sleep(1)
                                continue
                            else:
                                print("   ❌ 注册失败")
                                return None
                    except:
                        if attempt < max_retries - 1:
                            print("   🔄 刷新页面，重新尝试...")
                            await asyncio.sleep(1)
                            continue
                        else:
                            print("   ❌ 注册失败")
                            return None
            
            # 6. 跳转到信息页面
            info_url = "https://json.2s0.cn:5678/user/information"
            print(f"   📄 跳转到信息页面: {info_url}")
            await page.goto(info_url, wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(2)  # 等待页面加载
            
            # 7. 提取uid
            uid_xpath = "/html/body/div[2]/div/div/div[2]/div[2]/div/div/form/div[1]/input"
            print("   🔍 提取uid...")
            try:
                uid_input = page.locator(f"xpath={uid_xpath}")
                await uid_input.wait_for(state='visible', timeout=10000)
                uid = await uid_input.input_value()
                print(f"   ✅ uid: {uid}")
            except Exception as e:
                print(f"   ❌ 提取uid失败: {e}")
                if attempt < max_retries - 1:
                    print("   🔄 重新尝试...")
                    await asyncio.sleep(1)
                    continue
                return None
            
            # 8. 提取key
            key_xpath = "/html/body/div[2]/div/div/div[2]/div[2]/div/div/form/div[2]/input"
            print("   🔍 提取key...")
            try:
                key_input = page.locator(f"xpath={key_xpath}")
                await key_input.wait_for(state='visible', timeout=10000)
                key = await key_input.input_value()
                print(f"   ✅ key: {key}")
            except Exception as e:
                print(f"   ❌ 提取key失败: {e}")
                if attempt < max_retries - 1:
                    print("   🔄 重新尝试...")
                    await asyncio.sleep(1)
                    continue
                return None
            
            # 返回结果
            register_time = datetime.now()
            expire_date = register_time + timedelta(days=364)
            
            result = {
                'email': email,
                'password': password,
                'uid': uid,
                'key': key,
                'register_time': register_time.strftime('%Y-%m-%d %H:%M:%S'),
                'expire_date': expire_date.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return result
            
        except Exception as e:
            print(f"   ❌ 注册过程出错: {e}")
            if attempt < max_retries - 1:
                print("   🔄 重新尝试...")
                await asyncio.sleep(2)
                continue
            import traceback
            traceback.print_exc()
            return None
    
    return None


def save_single_result(result: Dict, filename: str = None) -> bool:
    """
    保存单个注册结果到文件（增量添加，自动去重）
    
    参数:
        result: 单个注册结果字典
        filename: 保存的文件名（如果为None，使用默认路径）
    
    返回:
        是否保存成功
    """
    if filename is None:
        # 使用脚本所在目录下的文件
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(script_dir, "registration_results.json")
    
    try:
        # 初始化数据结构
        data = {
            'current_index': 0,
            'keys': []
        }
        
        # 如果文件存在，读取现有数据
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    
                    # 支持新格式（包含 current_index 和 keys）
                    if isinstance(existing_data, dict) and 'keys' in existing_data:
                        data['current_index'] = existing_data.get('current_index', 0)
                        data['keys'] = existing_data.get('keys', [])
                    # 兼容旧格式（直接是数组）
                    elif isinstance(existing_data, list):
                        data['keys'] = existing_data
                        data['current_index'] = 0
                    else:
                        data['keys'] = [existing_data] if existing_data else []
                        data['current_index'] = 0
            except json.JSONDecodeError:
                print(f"   ⚠️  文件 {filename} 格式错误，将创建新文件")
                data = {'current_index': 0, 'keys': []}
        
        # 检查是否已存在（基于uid）
        existing_uids = {r.get('uid') for r in data['keys'] if r.get('uid')}
        uid = result.get('uid')
        
        if uid and uid not in existing_uids:
            # 添加新结果
            data['keys'].append(result)
            
            # 保存结果
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"   💾 结果已保存到: {filename}")
            print(f"   📈 总计记录: {len(data['keys'])} 条")
            return True
        elif uid:
            print(f"   ⚠️  跳过重复的uid: {uid}")
            return False
        else:
            print(f"   ⚠️  结果中没有uid，无法保存")
            return False
        
    except Exception as e:
        print(f"   ❌ 保存结果失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def save_results(results: List[Dict], filename: str = None):
    """
    保存多个注册结果到文件（增量添加，自动去重）
    
    参数:
        results: 新的注册结果列表
        filename: 保存的文件名（如果为None，使用默认路径）
    """
    if filename is None:
        # 使用脚本所在目录下的文件
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(script_dir, "registration_results.json")
    
    try:
        # 初始化数据结构
        data = {
            'current_index': 0,
            'keys': []
        }
        
        # 如果文件存在，读取现有数据
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    
                    # 支持新格式（包含 current_index 和 keys）
                    if isinstance(existing_data, dict) and 'keys' in existing_data:
                        data['current_index'] = existing_data.get('current_index', 0)
                        data['keys'] = existing_data.get('keys', [])
                    # 兼容旧格式（直接是数组）
                    elif isinstance(existing_data, list):
                        data['keys'] = existing_data
                        data['current_index'] = 0
                    else:
                        data['keys'] = [existing_data] if existing_data else []
                        data['current_index'] = 0
            except json.JSONDecodeError:
                print(f"   ⚠️  文件 {filename} 格式错误，将创建新文件")
                data = {'current_index': 0, 'keys': []}
        
        # 合并结果（去重：基于uid）
        existing_uids = {r.get('uid') for r in data['keys'] if r.get('uid')}
        new_results = []
        
        for result in results:
            uid = result.get('uid')
            if uid and uid not in existing_uids:
                new_results.append(result)
                existing_uids.add(uid)
            elif uid:
                print(f"   ⚠️  跳过重复的uid: {uid}")
        
        # 合并所有结果
        data['keys'].extend(new_results)
        
        # 保存结果
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 结果已保存到: {filename}")
        print(f"   📊 现有记录: {len(data['keys']) - len(new_results)} 条")
        print(f"   ➕ 新增记录: {len(new_results)} 条")
        print(f"   📈 总计记录: {len(data['keys'])} 条")
        
    except Exception as e:
        print(f"❌ 保存结果失败: {e}")
        import traceback
        traceback.print_exc()


async def batch_register(count: int = 5, password: str = "qwer1234!", use_proxy: bool = True):
    """
    批量注册账号
    
    参数:
        count: 注册数量
        password: 固定密码
        use_proxy: 是否使用代理IP
    """
    print("="*80)
    print("批量注册 jx.2s0.cn 账号")
    print("="*80)
    print(f"注册数量: {count}")
    print(f"固定密码: {password}")
    print(f"使用代理: {'是' if use_proxy else '否'}")
    print()
    
    chrome_process = None
    user_data_dir = None
    results = []
    
    try:
        # 启动独立浏览器
        print("[步骤1] 启动独立Chrome浏览器...")
        chrome_process, debug_port, user_data_dir = launch_chrome()
        if not chrome_process or not debug_port:
            print("❌ 启动浏览器失败")
            return
        
        print(f"✅ 浏览器已启动，调试端口: {debug_port}")
        
        async with async_playwright() as p:
            # 连接到浏览器
            browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{debug_port}")
            print("✅ 成功连接到浏览器")
            
            # 批量注册（每个账号使用新的上下文和代理）
            for i in range(count):
                print(f"\n{'='*80}")
                print(f"注册第 {i+1}/{count} 个账号")
                print(f"{'='*80}")
                
                # 获取代理IP（如果需要）
                proxy_config = None
                proxy_info = None
                if use_proxy:
                    print("   🌐 获取代理IP...")
                    proxy_info = get_proxy_ip()
                    if proxy_info:
                        proxy_config = {
                            'server': proxy_info['server']
                        }
                        print(f"   ✅ 代理IP: {proxy_info['host']}:{proxy_info['port']}")
                    else:
                        print("   ⚠️  获取代理IP失败，将使用直连")
                
                # 为每个账号创建新的上下文（使用代理，清除Cookie，随机化浏览器特征）
                # 生成随机浏览器特征
                random_viewport = generate_random_viewport()
                random_user_agent = generate_random_user_agent()
                
                context_options = {
                    'viewport': random_viewport,
                    'user_agent': random_user_agent,
                    'locale': 'zh-CN',
                    'timezone_id': 'Asia/Shanghai',
                }
                
                # 如果配置了代理，添加到上下文选项
                if proxy_config:
                    context_options['proxy'] = proxy_config
                
                print(f"   🎭 浏览器特征: {random_viewport['width']}x{random_viewport['height']}, Chrome {random_user_agent.split('Chrome/')[1].split()[0]}")
                
                context = await browser.new_context(**context_options)
                await add_stealth_script(context)
                
                # 创建新页面
                page = await context.new_page()
                
                # 生成随机邮箱
                email = generate_random_email()
                
                # 注册账号
                result = await register_account(page, email, password)
                
                # 检查是否触发反爬虫检测
                if result and isinstance(result, dict) and result.get('anti_crawler'):
                    print(f"\n⚠️  触发反爬虫检测，需要更换浏览器和IP")
                    # 关闭当前上下文
                    await page.close()
                    await context.close()
                    
                    # 获取新的代理IP
                    if use_proxy:
                        print("   🌐 获取新的代理IP...")
                        proxy_info = get_proxy_ip()
                        if proxy_info:
                            proxy_config = {
                                'server': proxy_info['server']
                            }
                            print(f"   ✅ 新代理IP: {proxy_info['host']}:{proxy_info['port']}")
                        else:
                            print("   ⚠️  获取新代理IP失败，将使用直连")
                            proxy_config = None
                    
                    # 创建新的浏览器上下文（使用新的代理和浏览器特征）
                    retry_viewport = generate_random_viewport()
                    retry_user_agent = generate_random_user_agent()
                    
                    print(f"   🎭 更换浏览器特征: {retry_viewport['width']}x{retry_viewport['height']}, Chrome {retry_user_agent.split('Chrome/')[1].split()[0]}")
                    
                    context_options = {
                        'viewport': retry_viewport,
                        'user_agent': retry_user_agent,
                        'locale': 'zh-CN',
                        'timezone_id': 'Asia/Shanghai',
                    }
                    
                    if proxy_config:
                        context_options['proxy'] = proxy_config
                    
                    context = await browser.new_context(**context_options)
                    await add_stealth_script(context)
                    page = await context.new_page()
                    
                    # 重新注册
                    result = await register_account(page, email, password)
                    
                    if result and not (isinstance(result, dict) and result.get('anti_crawler')):
                        print(f"\n✅ 更换浏览器和IP后注册成功!")
                        print(f"   邮箱: {result['email']}")
                        print(f"   uid: {result['uid']}")
                        print(f"   key: {result['key']}")
                        if proxy_info:
                            print(f"   代理: {proxy_info['host']}:{proxy_info['port']}")
                        
                        # 立即保存单个结果
                        save_single_result(result)
                        results.append(result)
                    else:
                        print(f"\n❌ 更换浏览器和IP后仍然失败")
                
                elif result:
                    print(f"\n✅ 注册成功!")
                    print(f"   邮箱: {result['email']}")
                    print(f"   uid: {result['uid']}")
                    print(f"   key: {result['key']}")
                    if proxy_info:
                        print(f"   代理: {proxy_info['host']}:{proxy_info['port']}")
                    
                    # 立即保存单个结果
                    save_single_result(result)
                    results.append(result)
                else:
                    print(f"\n❌ 注册失败")
                    # 如果使用代理失败，可以尝试不使用代理重试一次
                    if use_proxy and proxy_config:
                        print("   🔄 尝试不使用代理重新注册...")
                        await page.close()
                        await context.close()
                        
                        # 创建新的上下文（不使用代理，但使用随机浏览器特征）
                        retry_viewport = generate_random_viewport()
                        retry_user_agent = generate_random_user_agent()
                        
                        print(f"   🎭 重试浏览器特征: {retry_viewport['width']}x{retry_viewport['height']}, Chrome {retry_user_agent.split('Chrome/')[1].split()[0]}")
                        
                        context = await browser.new_context(
                            viewport=retry_viewport,
                            user_agent=retry_user_agent,
                            locale='zh-CN',
                            timezone_id='Asia/Shanghai',
                        )
                        await add_stealth_script(context)
                        page = await context.new_page()
                        
                        result = await register_account(page, email, password)
                        if result and not (isinstance(result, dict) and result.get('anti_crawler')):
                            print(f"\n✅ 不使用代理注册成功!")
                            print(f"   邮箱: {result['email']}")
                            print(f"   uid: {result['uid']}")
                            print(f"   key: {result['key']}")
                            
                            # 立即保存单个结果
                            save_single_result(result)
                            results.append(result)
                
                # 关闭页面和上下文
                await page.close()
                await context.close()
                
                # 等待一段时间再注册下一个（避免请求过快）
                if i < count - 1:
                    wait_time = random.uniform(3, 6)
                    print(f"\n⏳ 等待 {wait_time:.1f} 秒后继续下一个...")
                    await asyncio.sleep(wait_time)
            
            # 关闭浏览器
            await browser.close()
        
        # 保存结果
        if results:
            save_results(results)
            print(f"\n📊 注册统计:")
            print(f"   成功: {len(results)}/{count}")
            print(f"   失败: {count - len(results)}/{count}")
        else:
            print("\n❌ 没有成功注册的账号")
    
    except Exception as e:
        print(f"\n❌ 批量注册过程出错: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理资源
        print("\n🧹 清理资源...")
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
        
        print("✅ 清理完成")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='批量注册 jx.2s0.cn 账号')
    parser.add_argument('-n', '--count', type=int, default=5, help='注册数量（默认: 5）')
    parser.add_argument('-p', '--password', type=str, default='qwer1234!', help='固定密码（默认: qwer1234!）')
    parser.add_argument('--no-proxy', action='store_true', help='不使用代理IP（默认使用代理）')
    
    args = parser.parse_args()
    
    # 运行批量注册
    asyncio.run(batch_register(count=args.count, password=args.password, use_proxy=not args.no_proxy))


if __name__ == "__main__":
    main()
