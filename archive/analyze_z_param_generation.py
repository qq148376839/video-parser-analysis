"""
分析z参数的生成逻辑
提取JavaScript代码，找到z参数的生成方式
"""

import re
import json
import hashlib
import time
from typing import Optional, Dict, List
from urllib.parse import urlparse, parse_qs


def analyze_z_param_pattern(z_value: str) -> Dict:
    """分析z参数的模式"""
    result = {
        'value': z_value,
        'length': len(z_value),
        'is_hex': bool(re.match(r'^[a-f0-9]{32}$', z_value, re.IGNORECASE)),
        'is_md5': len(z_value) == 32 and re.match(r'^[a-f0-9]{32}$', z_value, re.IGNORECASE),
        'possible_hash': 'MD5' if len(z_value) == 32 else 'Unknown'
    }
    return result


def test_common_hash_patterns(video_url: str, z_value: str) -> List[Dict]:
    """测试常见的哈希生成模式"""
    results = []
    
    # 模式1: MD5(video_url)
    test_str = video_url
    md5_hash = hashlib.md5(test_str.encode('utf-8')).hexdigest()
    if md5_hash == z_value:
        results.append({
            'pattern': 'MD5(video_url)',
            'input': test_str,
            'result': md5_hash,
            'match': True
        })
    
    # 模式2: MD5(video_url + timestamp)
    current_timestamp = int(time.time())
    for offset in range(-10, 11):  # 测试前后10秒
        test_timestamp = current_timestamp + offset
        test_str = video_url + str(test_timestamp)
        md5_hash = hashlib.md5(test_str.encode('utf-8')).hexdigest()
        if md5_hash == z_value:
            results.append({
                'pattern': f'MD5(video_url + timestamp)',
                'input': test_str,
                'timestamp': test_timestamp,
                'result': md5_hash,
                'match': True
            })
    
    # 模式3: MD5(video_url + secret)
    common_secrets = [
        '', 'secret', 'key', 'token', 'salt',
        'videocdn', 'ihelpy', 'm1907',
        '2024', '2025', 'nnpp', 'vip'
    ]
    for secret in common_secrets:
        test_str = video_url + secret
        md5_hash = hashlib.md5(test_str.encode('utf-8')).hexdigest()
        if md5_hash == z_value:
            results.append({
                'pattern': f'MD5(video_url + secret)',
                'input': test_str,
                'secret': secret,
                'result': md5_hash,
                'match': True
            })
    
    # 模式4: MD5(domain + video_url)
    parsed = urlparse(video_url)
    domain = parsed.netloc
    test_str = domain + video_url
    md5_hash = hashlib.md5(test_str.encode('utf-8')).hexdigest()
    if md5_hash == z_value:
        results.append({
            'pattern': 'MD5(domain + video_url)',
            'input': test_str,
            'result': md5_hash,
            'match': True
        })
    
    return results


def extract_js_from_captured_data(captured_file: str = 'captured_api_params.json') -> Optional[Dict]:
    """从捕获的数据中提取信息"""
    try:
        with open(captured_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return None


def generate_z_param_candidates(video_url: str, captured_z: str = None) -> List[Dict]:
    """生成z参数的候选值（基于常见模式）"""
    candidates = []
    
    # 如果提供了捕获的z值，先分析它
    if captured_z:
        analysis = analyze_z_param_pattern(captured_z)
        print(f"📊 z参数分析:")
        print(f"   值: {captured_z}")
        print(f"   长度: {analysis['length']}")
        print(f"   格式: {'MD5哈希' if analysis['is_md5'] else '其他'}")
        
        # 测试常见模式
        matches = test_common_hash_patterns(video_url, captured_z)
        if matches:
            print(f"\n✅ 找到匹配的模式:")
            for match in matches:
                print(f"   {match['pattern']}: {match.get('input', 'N/A')}")
            return matches
    
    # 生成候选值（基于常见模式）
    patterns = [
        ('MD5(video_url)', lambda: hashlib.md5(video_url.encode('utf-8')).hexdigest()),
        ('MD5(video_url + timestamp)', lambda: hashlib.md5((video_url + str(int(time.time()))).encode('utf-8')).hexdigest()),
        ('MD5(domain + video_url)', lambda: hashlib.md5((urlparse(video_url).netloc + video_url).encode('utf-8')).hexdigest()),
    ]
    
    for pattern_name, func in patterns:
        try:
            value = func()
            candidates.append({
                'pattern': pattern_name,
                'value': value
            })
        except:
            pass
    
    return candidates


def create_z_param_api_service():
    """创建一个简单的API服务，用于获取z参数"""
    code = '''
"""
z参数获取API服务
用于在服务器上获取z参数，无需浏览器
"""

from flask import Flask, request, jsonify
import requests
import re
from typing import Optional

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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        response = requests.get(parser_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            # 从HTML中提取JavaScript代码
            html = response.text
            
            # 查找可能的z参数生成代码
            # 模式1: 在script标签中查找
            script_pattern = r'<script[^>]*>(.*?)</script>'
            scripts = re.findall(script_pattern, html, re.DOTALL | re.IGNORECASE)
            
            for script in scripts:
                # 查找z参数
                z_patterns = [
                    r'z\\s*[:=]\\s*["\']([a-f0-9]{32})["\']',
                    r'["\']z["\']\\s*[:=]\\s*["\']([a-f0-9]{32})["\']',
                    r'z\\s*=\\s*["\']([a-f0-9]{32})["\']',
                ]
                
                for pattern in z_patterns:
                    matches = re.findall(pattern, script, re.IGNORECASE)
                    if matches:
                        return matches[0]
            
            # 模式2: 从API调用URL中提取
            api_url_pattern = r'https://[^/]+/api/v/\?z=([a-f0-9]{32})'
            matches = re.findall(api_url_pattern, html, re.IGNORECASE)
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
            'error': '无法获取z参数'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
'''
    return code


def main():
    """主函数"""
    print("=" * 60)
    print("分析z参数生成逻辑")
    print("=" * 60)
    
    # 从捕获的数据中读取
    captured_data = extract_js_from_captured_data()
    
    if captured_data and captured_data.get('captured_params'):
        latest_params = captured_data['captured_params'][-1]
        video_url = latest_params.get('jx', '')
        z_value = latest_params.get('z', '')
        s1ig_value = latest_params.get('s1ig', '')
        
        print(f"\n📋 从捕获数据中读取:")
        print(f"   视频URL: {video_url}")
        print(f"   z参数: {z_value}")
        print(f"   s1ig参数: {s1ig_value}")
        
        # 分析z参数
        if z_value:
            print(f"\n🔍 分析z参数生成逻辑...")
            candidates = generate_z_param_candidates(video_url, z_value)
            
            if not candidates:
                print(f"\n⚠️ 未找到匹配的生成模式")
                print(f"\n💡 可能的解决方案:")
                print(f"   1. z参数可能是动态生成的，需要JavaScript执行")
                print(f"   2. z参数可能包含时间戳或其他动态值")
                print(f"   3. 需要从解析网站实时获取")
                
                # 创建API服务代码
                print(f"\n📝 生成API服务代码...")
                api_code = create_z_param_api_service()
                with open('z_param_api_service.py', 'w', encoding='utf-8') as f:
                    f.write(api_code)
                print(f"   ✅ 已保存到: z_param_api_service.py")
                print(f"\n💡 使用方法:")
                print(f"   1. 安装Flask: pip install flask")
                print(f"   2. 运行服务: python z_param_api_service.py")
                print(f"   3. 调用API: GET http://localhost:5000/api/get_z_param?video_url={video_url}")
    else:
        print(f"\n⚠️ 未找到捕获的数据文件")
        print(f"   💡 请先运行: python3 capture_api_params.py")


if __name__ == '__main__':
    main()

