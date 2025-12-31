#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试单个注册流程
用于验证XPath和注册流程是否正确
"""

import asyncio
from batch_register_jx2s0 import (
    launch_chrome,
    cleanup_user_data,
    add_stealth_script,
    generate_random_email,
    register_account
)
from playwright.async_api import async_playwright


async def test_single_register():
    """测试单个注册"""
    print("="*80)
    print("测试单个注册流程")
    print("="*80)
    
    chrome_process = None
    user_data_dir = None
    
    try:
        # 启动独立浏览器
        print("\n[步骤1] 启动独立Chrome浏览器...")
        chrome_process, debug_port, user_data_dir = launch_chrome()
        if not chrome_process or not debug_port:
            print("❌ 启动浏览器失败")
            return
        
        print(f"✅ 浏览器已启动，调试端口: {debug_port}")
        
        async with async_playwright() as p:
            # 连接到浏览器
            browser = await p.chromium.connect_over_cdp(f"http://127.0.0.1:{debug_port}")
            print("✅ 成功连接到浏览器")
            
            # 创建上下文并添加反爬虫脚本
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='zh-CN',
            )
            await add_stealth_script(context)
            
            # 创建页面
            page = await context.new_page()
            
            # 生成测试邮箱和密码
            email = generate_random_email()
            password = "qwer1234!"
            
            print(f"\n📧 测试邮箱: {email}")
            print(f"🔑 测试密码: {password}")
            
            # 执行注册
            result = await register_account(page, email, password)
            
            if result:
                print("\n" + "="*80)
                print("✅ 注册成功!")
                print("="*80)
                print(f"邮箱: {result['email']}")
                print(f"密码: {result['password']}")
                print(f"uid: {result['uid']}")
                print(f"key: {result['key']}")
                print(f"注册时间: {result['register_time']}")
            else:
                print("\n" + "="*80)
                print("❌ 注册失败")
                print("="*80)
                print("请检查:")
                print("1. 网络连接是否正常")
                print("2. XPath是否正确")
                print("3. 网站是否可访问")
                print("4. 查看上面的错误信息")
            
            # 保持浏览器打开一段时间，方便查看
            print("\n⏳ 浏览器将保持打开10秒，方便查看结果...")
            await asyncio.sleep(10)
            
            # 关闭上下文和浏览器
            await context.close()
            await browser.close()
    
    except Exception as e:
        print(f"\n❌ 测试过程出错: {e}")
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


if __name__ == "__main__":
    asyncio.run(test_single_register())
