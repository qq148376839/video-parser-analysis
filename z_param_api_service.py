"""
z参数获取API服务
用于在服务器上获取z参数，无需浏览器
通过HTTP请求解析网站，提取z参数
"""

import requests
import re
from typing import Optional
from flask import Flask, request, jsonify

app = Flask(__name__)


def get_z_param_from_website(video_url: str) -> Optional[str]:
    """
    从解析网站获取z参数
    通过HTTP请求获取页面，提取z参数
    """
    try:
        # 访问解析网站
        parser_url = f"https://videocdn.ihelpy.net/jiexi/m1907.html?m1907jx={video_url}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://videocdn.ihelpy.net/',
        }
        
        response = requests.get(parser_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            html = response.text
            
            # 方法1: 从script标签中查找z参数
            script_pattern = r'<script[^>]*>(.*?)</script>'
            scripts = re.findall(script_pattern, html, re.DOTALL | re.IGNORECASE)
            
            for script in scripts:
                # 查找z参数（多种模式）
                z_patterns = [
                    r'z\s*[:=]\s*["\']([a-f0-9]{32})["\']',
                    r'["\']z["\']\s*[:=]\s*["\']([a-f0-9]{32})["\']',
                    r'z\s*=\s*["\']([a-f0-9]{32})["\']',
                    r'z["\']?\s*[:=]\s*["\']([a-f0-9]{32})["\']',
                ]
                
                for pattern in z_patterns:
                    matches = re.findall(pattern, script, re.IGNORECASE)
                    if matches:
                        return matches[0]
            
            # 方法2: 从API调用URL中提取
            api_url_patterns = [
                r'https://[^/]+/api/v/\?[^"\'<>]*z=([a-f0-9]{32})',
                r'api/v/\?[^"\'<>]*z=([a-f0-9]{32})',
                r'["\']([^"\']*api/v/[^"\']*z=([a-f0-9]{32})[^"\']*)["\']',
            ]
            
            for pattern in api_url_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                if matches:
                    # 处理嵌套匹配
                    for match in matches:
                        if isinstance(match, tuple):
                            z_value = match[-1]  # 取最后一个（通常是z参数）
                        else:
                            z_value = match
                        if len(z_value) == 32 and re.match(r'^[a-f0-9]{32}$', z_value, re.IGNORECASE):
                            return z_value
            
            # 方法3: 从JavaScript变量中提取
            var_patterns = [
                r'var\s+z\s*=\s*["\']([a-f0-9]{32})["\']',
                r'let\s+z\s*=\s*["\']([a-f0-9]{32})["\']',
                r'const\s+z\s*=\s*["\']([a-f0-9]{32})["\']',
            ]
            
            for pattern in var_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                if matches:
                    return matches[0]
        
        return None
    
    except Exception as e:
        print(f"获取z参数失败: {e}")
        return None


@app.route('/api/get_z_param', methods=['GET'])
def get_z_param():
    """获取z参数的API端点"""
    video_url = request.args.get('video_url')
    
    if not video_url:
        return jsonify({'error': '缺少video_url参数'}), 400
    
    z_param = get_z_param_from_website(video_url)
    
    if z_param:
        return jsonify({
            'success': True,
            'z_param': z_param,
            'video_url': video_url
        })
    else:
        return jsonify({
            'success': False,
            'error': '无法获取z参数，可能需要JavaScript执行'
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    print("=" * 60)
    print("z参数获取API服务")
    print("=" * 60)
    print("启动服务...")
    print("API端点: GET /api/get_z_param?video_url=<视频URL>")
    print("健康检查: GET /health")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)

