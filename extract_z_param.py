#!/usr/bin/env python3
"""
从调试HTML文件中提取z参数的工具
"""
import re
import sys
from pathlib import Path

def extract_z_from_html(html: str) -> list:
    """从HTML中提取所有可能的z参数"""
    z_params = []
    
    # 方法1: 从API调用URL中提取
    api_url_patterns = [
        r'https://[^/]+/api/v/\?[^"\'<>]*z=([a-f0-9]{32})',
        r'api/v/\?[^"\'<>]*z=([a-f0-9]{32})',
        r'["\']([^"\']*api/v/[^"\']*z=([a-f0-9]{32})[^"\']*)["\']',
        r'/api/v/\?[^"\'<>]*z=([a-f0-9]{32})',
        r'api/v/\?.*?z=([a-f0-9]{32})',
    ]
    
    for pattern in api_url_patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                z_value = match[-1] if match else None
            else:
                z_value = match
            
            if z_value and len(z_value) == 32 and re.match(r'^[a-f0-9]{32}$', z_value, re.IGNORECASE):
                if z_value not in z_params:
                    z_params.append(z_value)
    
    # 方法2: 从script标签中查找
    script_pattern = r'<script[^>]*>(.*?)</script>'
    scripts = re.findall(script_pattern, html, re.DOTALL | re.IGNORECASE)
    
    for script in scripts:
        z_patterns = [
            r'z\s*[:=]\s*["\']([a-f0-9]{32})["\']',
            r'["\']z["\']\s*[:=]\s*["\']([a-f0-9]{32})["\']',
            r'z\s*=\s*["\']([a-f0-9]{32})["\']',
            r'z["\']?\s*[:=]\s*["\']([a-f0-9]{32})["\']',
            r'var\s+z\s*=\s*["\']([a-f0-9]{32})["\']',
            r'let\s+z\s*=\s*["\']([a-f0-9]{32})["\']',
            r'const\s+z\s*=\s*["\']([a-f0-9]{32})["\']',
        ]
        
        for pattern in z_patterns:
            matches = re.findall(pattern, script, re.IGNORECASE)
            for z_value in matches:
                if len(z_value) == 32 and re.match(r'^[a-f0-9]{32}$', z_value, re.IGNORECASE):
                    if z_value not in z_params:
                        z_params.append(z_value)
    
    # 方法3: 在整个HTML中搜索32位十六进制字符串
    hex_pattern = r'\b([a-f0-9]{32})\b'
    all_hex_matches = re.findall(hex_pattern, html, re.IGNORECASE)
    
    for hex_value in all_hex_matches:
        # 检查这个hex值是否在API URL附近
        context_start = max(0, html.find(hex_value) - 100)
        context_end = min(len(html), html.find(hex_value) + 100)
        context = html[context_start:context_end]
        
        if ('api/v' in context.lower() or 'z=' in context.lower()) and hex_value not in z_params:
            z_params.append(hex_value)
    
    return z_params


def main():
    """主函数"""
    # 默认使用调试文件
    debug_file = Path("data/z_param_debug.html")
    
    if len(sys.argv) > 1:
        debug_file = Path(sys.argv[1])
    
    if not debug_file.exists():
        print(f"❌ 文件不存在: {debug_file}")
        print(f"\n使用方法:")
        print(f"  python extract_z_param.py [HTML文件路径]")
        print(f"\n默认文件: data/z_param_debug.html")
        sys.exit(1)
    
    print("=" * 60)
    print("z参数提取工具")
    print("=" * 60)
    print(f"文件: {debug_file}")
    print("-" * 60)
    
    try:
        with open(debug_file, 'r', encoding='utf-8') as f:
            html = f.read()
        
        print(f"HTML长度: {len(html)} 字节")
        print("-" * 60)
        
        # 检查是否是iframe页面
        iframe_patterns = [
            r'iframe.*?src=["\']([^"\']+)["\']',
            r'ifr\.src=["\']([^"\']+)["\']',
        ]
        
        iframe_url = None
        for pattern in iframe_patterns:
            matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
            if matches:
                iframe_url = matches[0]
                if not iframe_url.startswith('http'):
                    # 从JavaScript中提取
                    js_pattern = r'ifr\.src\s*=\s*["\']([^"\']+)["\']'
                    js_matches = re.findall(js_pattern, html, re.IGNORECASE)
                    if js_matches:
                        iframe_url = js_matches[0]
                break
        
        if iframe_url:
            print(f"⚠️  检测到iframe页面")
            print(f"   iframe URL: {iframe_url}")
            print(f"\n💡 提示: z参数可能在iframe页面中")
            print(f"   请使用浏览器访问上述URL，然后:")
            print(f"   1. 打开开发者工具 (F12)")
            print(f"   2. 切换到Network标签")
            print(f"   3. 查找包含 'api/v' 的请求")
            print(f"   4. 从URL中提取 z= 参数")
        else:
            print("正在提取z参数...")
            z_params = extract_z_from_html(html)
            
            if z_params:
                print(f"\n✅ 找到 {len(z_params)} 个可能的z参数:")
                for i, z_param in enumerate(z_params, 1):
                    print(f"\n{i}. {z_param}")
                    print(f"   使用此参数创建 data/z_params.json:")
                    print(f"   {{")
                    print(f'     "z_param": "{z_param}",')
                    print(f'     "s1ig_param": "11397",')
                    print(f'     "g_param": "",')
                    print(f'     "updated_at": "2024-12-30T09:00:00"')
                    print(f"   }}")
            else:
                print("\n❌ 未能提取到z参数")
                print("\n💡 建议:")
                print("1. 使用浏览器访问解析网站")
                print("2. 打开开发者工具，查找包含 'api/v' 的网络请求")
                print("3. 从请求URL中提取 z= 参数")
                print("4. 参考 Z_PARAM_MANUAL_SETUP.md 手动设置")
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

