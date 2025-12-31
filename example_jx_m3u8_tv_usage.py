"""
jx.m3u8.tv 解析使用示例
演示如何使用捕获脚本和直接调用脚本
"""

import asyncio
import json
from capture_jx_m3u8_tv_params import JxM3u8TvParamsCapturer
from direct_jx_m3u8_tv_parser import DirectJxM3u8TvParser


async def example_capture_and_parse():
    """示例：捕获参数并解析"""
    
    video_url = "https://v.youku.com/v_show/id_XMTA0MTc5NzI4.html"
    
    print("=" * 60)
    print("示例：捕获参数并解析视频")
    print("=" * 60)
    
    # 步骤1: 捕获参数
    print("\n[步骤1] 捕获API参数...")
    capturer = JxM3u8TvParamsCapturer()
    result = await capturer.capture_params(video_url, headless=False)
    
    if not result:
        print("❌ 参数捕获失败")
        return
    
    # 步骤2: 分析捕获的参数
    print("\n[步骤2] 分析捕获的参数...")
    if result.get('captured_params'):
        print(f"✅ 捕获到 {len(result['captured_params'])} 组参数")
        latest_params = result['captured_params'][-1]
        print("最新参数:")
        for k, v in latest_params.items():
            if k not in ['url', 'timestamp']:
                print(f"   {k}: {v}")
    
    if result.get('m3u8_urls'):
        print(f"\n✅ 直接找到 {len(result['m3u8_urls'])} 个m3u8链接:")
        for i, url in enumerate(result['m3u8_urls'][:3], 1):
            print(f"   [{i}] {url[:100]}...")
        return result['m3u8_urls'][0]
    
    # 步骤3: 使用捕获的参数直接调用API
    print("\n[步骤3] 使用捕获的参数直接调用API...")
    parser = DirectJxM3u8TvParser()
    m3u8_url = parser.parse_video(video_url, 'captured_jx_m3u8_tv_params.json')
    
    if m3u8_url:
        print(f"\n✅ 解析成功！")
        print(f"m3u8链接: {m3u8_url}")
        return m3u8_url
    else:
        print(f"\n⚠️ 解析失败")
        return None


def example_direct_parse():
    """示例：直接解析（需要先运行捕获脚本）"""
    
    video_url = "https://v.youku.com/v_show/id_XMTA0MTc5NzI4.html"
    
    print("=" * 60)
    print("示例：直接解析视频（使用已捕获的参数）")
    print("=" * 60)
    
    parser = DirectJxM3u8TvParser()
    m3u8_url = parser.parse_video(video_url, 'captured_jx_m3u8_tv_params.json')
    
    if m3u8_url:
        print(f"\n✅ 解析成功！")
        print(f"m3u8链接: {m3u8_url}")
        return m3u8_url
    else:
        print(f"\n⚠️ 解析失败")
        print("💡 请先运行 capture_jx_m3u8_tv_params.py 捕获参数")
        return None


def example_analyze_captured_params():
    """示例：分析已捕获的参数"""
    
    print("=" * 60)
    print("示例：分析已捕获的参数")
    print("=" * 60)
    
    try:
        with open('captured_jx_m3u8_tv_params.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"\n📊 捕获统计:")
        print(f"   API调用数: {len(data.get('api_calls', []))}")
        print(f"   参数组数: {len(data.get('captured_params', []))}")
        print(f"   m3u8链接数: {len(data.get('m3u8_urls', []))}")
        print(f"   ConFig对象数: {len(data.get('config_objects', []))}")
        
        if data.get('captured_params'):
            print(f"\n📋 参数详情:")
            for i, params in enumerate(data['captured_params'], 1):
                print(f"\n[组 {i}]")
                for k, v in params.items():
                    if k not in ['url', 'timestamp']:
                        print(f"   {k}: {v}")
                if params.get('url'):
                    print(f"   URL: {params['url'][:100]}...")
        
        if data.get('m3u8_urls'):
            print(f"\n🎬 m3u8链接:")
            for i, url in enumerate(data['m3u8_urls'], 1):
                print(f"   [{i}] {url[:100]}...")
        
        if data.get('js_analysis'):
            print(f"\n🔍 JavaScript分析结果:")
            for pattern_name, matches in data['js_analysis'].items():
                if matches:
                    print(f"   {pattern_name}: {len(matches)} 个匹配")
        
    except FileNotFoundError:
        print("❌ 未找到 captured_jx_m3u8_tv_params.json 文件")
        print("💡 请先运行 capture_jx_m3u8_tv_params.py 捕获参数")
    except Exception as e:
        print(f"❌ 分析失败: {e}")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        mode = 'direct'
    
    if mode == 'capture':
        # 捕获参数并解析
        asyncio.run(example_capture_and_parse())
    elif mode == 'direct':
        # 直接解析（需要先运行捕获脚本）
        example_direct_parse()
    elif mode == 'analyze':
        # 分析已捕获的参数
        example_analyze_captured_params()
    else:
        print("使用方法:")
        print("  python example_jx_m3u8_tv_usage.py capture   # 捕获参数并解析")
        print("  python example_jx_m3u8_tv_usage.py direct    # 直接解析（需要先运行捕获脚本）")
        print("  python example_jx_m3u8_tv_usage.py analyze   # 分析已捕获的参数")


