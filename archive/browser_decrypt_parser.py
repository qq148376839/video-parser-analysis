"""
浏览器自动化解密方案
直接在浏览器中执行JavaScript解密函数，避免Python解密逻辑的复杂性
"""

import asyncio
import json
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page


class BrowserDecryptParser:
    """使用浏览器自动化执行JavaScript解密的解析器"""
    
    def __init__(self):
        self.session = None
        self.decrypted_url = None
    
    async def extract_config_from_iframe(self, page: Page, iframe_url: str) -> Optional[dict]:
        """从iframe页面提取ConFig对象"""
        print(f"\n[步骤2] 访问iframe页面并提取ConFig...")
        print(f"   iframe URL: {iframe_url}")
        
        try:
            # 访问iframe页面
            await page.goto(iframe_url, wait_until='networkidle', timeout=60000)
            await asyncio.sleep(3)  # 等待JavaScript执行
            
            # 等待ConFig对象出现
            print(f"   等待ConFig对象出现...")
            for i in range(30):
                has_config = await page.evaluate("""
                    () => {
                        return !!(window.ConFig && window.ConFig.url && window.ConFig.config && window.ConFig.config.uid);
                    }
                """)
                if has_config:
                    print(f"   ✅ ConFig对象已出现")
                    break
                await asyncio.sleep(1)
            else:
                print(f"   ⚠️ ConFig对象未出现，继续尝试...")
            
            # 提取ConFig数据
            config_data = await page.evaluate("""
                () => {
                    if (window.ConFig) {
                        return {
                            url: window.ConFig.url,
                            uid: window.ConFig.config ? window.ConFig.config.uid : null,
                            full: window.ConFig
                        };
                    }
                    return null;
                }
            """)
            
            if config_data and config_data.get('url') and config_data.get('uid'):
                print(f"   ✅ 提取成功")
                print(f"   ✅ ConFig.url: {config_data['url'][:100]}...")
                print(f"   ✅ ConFig.config.uid: {config_data['uid']}")
                return config_data
            else:
                print(f"   ❌ 未能提取ConFig对象")
                return None
                
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def decrypt_url_in_browser(self, page: Page, encrypted_url: str) -> Optional[str]:
        """在浏览器中执行JavaScript解密函数"""
        print(f"\n[步骤3] 在浏览器中解密ConFig.url...")
        print(f"   encrypted_url长度: {len(encrypted_url)}")
        
        try:
            # 等待PlayEr对象出现
            print(f"   等待PlayEr对象出现...")
            for i in range(30):
                has_player = await page.evaluate("""
                    () => {
                        return !!(window.PlayEr && window.PlayEr.ad && window.PlayEr.ad.uic);
                    }
                """)
                if has_player:
                    print(f"   ✅ PlayEr对象已出现")
                    break
                await asyncio.sleep(1)
            else:
                print(f"   ⚠️ PlayEr对象未出现，继续尝试...")
            
            # 执行解密函数
            decrypted = await page.evaluate("""
                (encrypted_url) => {
                    try {
                        if (window.PlayEr && window.PlayEr.ad && window.PlayEr.ad.uic) {
                            const result = window.PlayEr.ad.uic(encrypted_url);
                            return {
                                success: true,
                                url: result
                            };
                        } else {
                            return {
                                success: false,
                                error: 'PlayEr.ad.uic函数不存在'
                            };
                        }
                    } catch (e) {
                        return {
                            success: false,
                            error: e.toString()
                        };
                    }
                }
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
    
    async def get_iframe_url(self, page: Page, parser_url: str, video_url: str) -> Optional[str]:
        """获取iframe URL"""
        print(f"\n[步骤1] 获取iframe URL...")
        full_url = f"{parser_url}/?url={video_url}"
        
        try:
            await page.goto(full_url, wait_until='networkidle', timeout=60000)
            await asyncio.sleep(2)
            
            # 查找iframe
            iframe_src = await page.evaluate("""
                () => {
                    const iframe = document.querySelector('iframe');
                    return iframe ? iframe.src : null;
                }
            """)
            
            if iframe_src:
                print(f"   ✅ 找到iframe URL: {iframe_src}")
                return iframe_src
            else:
                print(f"   ❌ 未找到iframe")
                return None
                
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            return None
    
    async def follow_redirect_to_final_m3u8(self, page: Page, initial_url: str) -> Optional[str]:
        """跟踪重定向获取最终m3u8"""
        print(f"\n[步骤4] 跟踪重定向...")
        print(f"   初始URL: {initial_url}")
        
        try:
            # 使用page.goto会自动跟踪重定向
            response = await page.goto(initial_url, wait_until='networkidle', timeout=30000)
            
            if response:
                final_url = response.url
                content = await response.text()
                
                if content.strip().startswith('#EXTM3U'):
                    print(f"   ✅ 这是最终的m3u8播放列表")
                    print(f"   📊 包含 {content.count('#EXTINF')} 个视频片段")
                    
                    # 保存m3u8内容
                    with open('final_m3u8_browser.m3u8', 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"   💾 已保存到: final_m3u8_browser.m3u8")
                    
                    return final_url
                else:
                    # 可能是重定向到了其他URL
                    print(f"   🔄 重定向到: {final_url}")
                    if 'api/m3u8' in final_url or 'm3u8.shipinbofang.net' in final_url:
                        return final_url
            
            return None
            
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            return None
    
    async def parse_video(self, parser_url: str, video_url: str) -> Optional[str]:
        """解析视频，获取最终m3u8"""
        print("=" * 60)
        print("浏览器自动化解密方案")
        print("=" * 60)
        print(f"解析网站: {parser_url}")
        print(f"目标视频: {video_url}")
        
        async with async_playwright() as p:
            # 启动浏览器
            browser = await p.chromium.launch(headless=False)  # headless=False 方便调试
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            )
            page = await context.new_page()
            
            try:
                # 步骤1: 获取iframe URL
                iframe_url = await self.get_iframe_url(page, parser_url, video_url)
                if not iframe_url:
                    print("\n❌ 未能获取iframe URL")
                    return None
                
                # 步骤2: 访问iframe页面并提取ConFig
                config = await self.extract_config_from_iframe(page, iframe_url)
                if not config:
                    print("\n❌ 未能提取ConFig对象")
                    return None
                
                # 步骤3: 在浏览器中解密URL
                encrypted_url = config['url']
                decrypted_url = await self.decrypt_url_in_browser(page, encrypted_url)
                if not decrypted_url:
                    print("\n❌ 解密失败")
                    return None
                
                # 步骤4: 跟踪重定向
                final_m3u8 = await self.follow_redirect_to_final_m3u8(page, decrypted_url)
                
                if final_m3u8:
                    print("\n" + "=" * 60)
                    print("✅ 解析成功！")
                    print("=" * 60)
                    print(f"\n🎬 最终的m3u8链接:")
                    print(f"   {final_m3u8}")
                    print(f"\n📥 使用ffmpeg下载:")
                    print(f'   ffmpeg -i "{final_m3u8}" -c copy output.mp4')
                    
                    # 保存完整结果
                    result = {
                        'encrypted_url': encrypted_url,
                        'uid': config['uid'],
                        'decrypted_url': decrypted_url,
                        'final_m3u8': final_m3u8,
                    }
                    with open('final_parse_result_browser.json', 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                    print(f"\n✅ 完整结果已保存到: final_parse_result_browser.json")
                    
                    # 保持浏览器打开一段时间，方便查看
                    print(f"\n⏸️ 浏览器将保持打开10秒，您可以手动检查...")
                    await asyncio.sleep(10)
                    
                    return final_m3u8
                else:
                    print("\n❌ 未能获取最终的m3u8链接")
                    return None
                    
            finally:
                await browser.close()


async def main():
    """主函数"""
    parser_url = "https://jx.789jiexi.com"
    video_url = "https://www.iqiyi.com/v_237eaj98iv0.html"
    
    parser = BrowserDecryptParser()
    final_m3u8 = await parser.parse_video(parser_url, video_url)
    
    if not final_m3u8:
        print("\n❌ 解析失败")


if __name__ == '__main__':
    asyncio.run(main())



