"""
分析API响应，查找z参数的来源
重点分析第一个API调用的响应，z参数可能从服务器返回
"""

import asyncio
import json
import re
from typing import Dict, Optional
from playwright.async_api import async_playwright


async def capture_api_responses(video_url: str):
    """捕获API响应，查找z参数的来源"""
    print("=" * 60)
    print("分析API响应，查找z参数来源")
    print("=" * 60)
    
    parser_url = f"https://videocdn.ihelpy.net/jiexi/m1907.html?m1907jx={video_url}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        )
        
        page = await context.new_page()
        
        # 存储API响应
        api_responses = []
        
        # 监听响应
        async def handle_response(response):
            url = response.url
            
            # 重点关注这两个API
            if 'm1-z2.cloud' in url or 'm1-a1.cloud' in url or 'api/v' in url:
                try:
                    status = response.status
                    content_type = response.headers.get('content-type', '')
                    
                    print(f"\n🔍 捕获API响应:")
                    print(f"   URL: {url}")
                    print(f"   状态码: {status}")
                    print(f"   Content-Type: {content_type}")
                    
                    # 尝试读取响应
                    try:
                        # 先尝试JSON
                        try:
                            content = await response.json()
                            content_str = json.dumps(content, ensure_ascii=False, indent=2)
                            print(f"   ✅ JSON响应:")
                            print(f"   {content_str[:500]}...")
                            
                            # 搜索z参数
                            z_value = search_z_in_object(content)
                            if z_value:
                                print(f"\n   🎯 找到z参数: {z_value}")
                            
                            api_responses.append({
                                'url': url,
                                'status': status,
                                'content_type': content_type,
                                'content': content,
                                'z_value': z_value
                            })
                        except:
                            # 如果不是JSON，读取文本
                            content = await response.text()
                            print(f"   📄 文本响应 (长度: {len(content)}):")
                            print(f"   {content[:500]}...")
                            
                            # 搜索z参数
                            z_matches = re.findall(r'[?&]z=([a-f0-9]{32})', url)
                            if not z_matches:
                                z_matches = re.findall(r'["\']([a-f0-9]{32})["\']', content)
                            
                            if z_matches:
                                print(f"\n   🎯 找到z参数: {z_matches[0]}")
                            
                            api_responses.append({
                                'url': url,
                                'status': status,
                                'content_type': content_type,
                                'content': content,
                                'z_value': z_matches[0] if z_matches else None
                            })
                    except Exception as e:
                        print(f"   ⚠️ 读取响应失败: {e}")
                        api_responses.append({
                            'url': url,
                            'status': status,
                            'content_type': content_type,
                            'error': str(e)
                        })
                
                except Exception as e:
                    print(f"   ⚠️ 处理响应失败: {e}")
        
        page.on('response', handle_response)
        
        print(f"\n[步骤1] 访问页面...")
        print(f"   URL: {parser_url}")
        
        await page.goto(parser_url, wait_until='domcontentloaded', timeout=60000)
        print(f"   ✅ 页面加载完成")
        
        # 等待JavaScript执行
        print(f"\n[步骤2] 等待JavaScript执行和API调用...")
        await asyncio.sleep(15)
        
        # 尝试触发视频加载
        try:
            play_button = await page.query_selector('button, .play-btn, [class*="play"], video')
            if play_button:
                await play_button.click()
                await asyncio.sleep(5)
        except:
            pass
        
        # 再等待一下
        await asyncio.sleep(10)
        
        # 分析结果
        print(f"\n" + "=" * 60)
        print("📊 分析结果")
        print("=" * 60)
        
        # 查找第一个API调用（可能返回z参数）
        first_api = None
        for resp in api_responses:
            if 'm1-z2.cloud' in resp['url'] and 'api/v' not in resp['url']:
                first_api = resp
                break
        
        if first_api:
            print(f"\n🔍 第一个API调用（可能包含z参数）:")
            print(f"   URL: {first_api['url']}")
            print(f"   响应类型: {first_api.get('content_type', 'N/A')}")
            
            if first_api.get('z_value'):
                print(f"\n   ✅ 在响应中找到z参数: {first_api['z_value']}")
            else:
                print(f"\n   ⚠️ 响应中未直接找到z参数")
                print(f"   💡 可能的情况:")
                print(f"      1. z参数在响应的JavaScript代码中")
                print(f"      2. z参数通过其他方式生成")
                print(f"      3. z参数在响应的HTML中")
            
            # 显示完整响应
            if first_api.get('content'):
                print(f"\n   📄 完整响应内容:")
                content = first_api['content']
                if isinstance(content, dict):
                    print(json.dumps(content, indent=2, ensure_ascii=False))
                else:
                    print(content[:2000])
        
        # 查找包含z参数的API调用
        z_api = None
        for resp in api_responses:
            if 'api/v' in resp['url'] and 'z=' in resp['url']:
                z_api = resp
                break
        
        if z_api:
            print(f"\n🔍 包含z参数的API调用:")
            print(f"   URL: {z_api['url']}")
            z_match = re.search(r'[?&]z=([a-f0-9]{32})', z_api['url'])
            if z_match:
                print(f"   z参数值: {z_match.group(1)}")
        
        # 保存结果
        output = {
            'video_url': video_url,
            'parser_url': parser_url,
            'api_responses': api_responses,
            'first_api': first_api,
            'z_api': z_api
        }
        
        output_file = 'api_response_analysis.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n✅ 分析完成")
        print(f"   💾 保存到: {output_file}")
        
        # 提供建议
        print(f"\n💡 下一步建议:")
        print(f"   1. 查看 {output_file} 文件")
        print(f"   2. 重点关注第一个API调用的响应")
        print(f"   3. 如果响应是HTML，检查其中的JavaScript代码")
        print(f"   4. 如果响应是JSON，检查是否包含z参数")
        print(f"   5. 在浏览器Network标签页中，查看第一个请求的响应")
        
        # 保持浏览器打开
        print(f"\n⏸️ 浏览器将保持打开60秒，您可以手动检查Network标签页...")
        await asyncio.sleep(60)
        
        await browser.close()
        
        return output


def search_z_in_object(obj, path=""):
    """递归搜索对象中的z参数"""
    if isinstance(obj, dict):
        # 检查键名
        for key in obj.keys():
            if key.lower() == 'z' and isinstance(obj[key], str) and len(obj[key]) == 32:
                if re.match(r'^[a-f0-9]{32}$', obj[key], re.IGNORECASE):
                    return obj[key]
        
        # 递归搜索值
        for key, value in obj.items():
            result = search_z_in_object(value, f"{path}.{key}")
            if result:
                return result
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            result = search_z_in_object(item, f"{path}[{i}]")
            if result:
                return result
    elif isinstance(obj, str):
        # 检查是否是32位MD5格式
        if len(obj) == 32 and re.match(r'^[a-f0-9]{32}$', obj, re.IGNORECASE):
            return obj
    
    return None


async def main():
    # 从捕获数据中读取
    try:
        with open('captured_api_params.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        captured_params = data.get('captured_params', [])
        if captured_params:
            video_url = captured_params[-1].get('jx')
        else:
            video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    except:
        video_url = "https://www.iqiyi.com/v_1c168e2yzbk.html"
    
    result = await capture_api_responses(video_url)
    
    if result:
        print("\n✅ 分析完成！")
        print("\n💡 关键发现:")
        if result.get('first_api'):
            print(f"   - 第一个API调用: {result['first_api']['url']}")
            if result['first_api'].get('z_value'):
                print(f"   - ✅ 找到z参数: {result['first_api']['z_value']}")
            else:
                print(f"   - ⚠️ 未在响应中找到z参数，可能需要进一步分析")


if __name__ == '__main__':
    asyncio.run(main())

