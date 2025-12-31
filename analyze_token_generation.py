"""
分析 jx.2s0.cn token 生成方式
基于捕获的网络请求数据，分析 token 是如何生成的
"""

import json
import re
import hashlib
import base64
from urllib.parse import urlparse, parse_qs
from typing import Dict, List, Optional


class TokenAnalyzer:
    """Token生成分析器"""
    
    def __init__(self, json_file: str):
        """初始化分析器"""
        with open(json_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.token = None
        self.m3u8_url = None
        self.api_calls = self.data.get('api_calls', [])
        self.video_url = self.data.get('video_url', '')
        
        # 提取 token
        self._extract_token()
    
    def _extract_token(self):
        """从数据中提取 token"""
        # 从 m3u8_urls 中提取
        for url in self.data.get('m3u8_urls', []):
            if 'token=' in url:
                parsed = urlparse(url)
                params = parse_qs(parsed.query)
                if 'token' in params:
                    self.token = params['token'][0]
                    self.m3u8_url = url
                    break
        
        # 从 captured_params 中提取
        if not self.token:
            for params in self.data.get('captured_params', []):
                if 'token' in params:
                    self.token = params['token']
                    self.m3u8_url = params.get('url', '')
                    break
        
        if self.token:
            print(f"[OK] 提取到 token: {self.token[:50]}...")
        else:
            print(f"[ERROR] 未找到 token")
        if self.m3u8_url:
            print(f"[OK] m3u8 URL: {self.m3u8_url[:100]}...")
        else:
            print(f"[ERROR] 未找到 m3u8 URL")
    
    def analyze_token_structure(self):
        """分析 token 的结构特征"""
        print("\n" + "=" * 60)
        print("[分析] Token 结构分析")
        print("=" * 60)
        
        if not self.token:
            print("❌ 没有 token 可分析")
            return
        
        print(f"\n1. Token 基本信息:")
        print(f"   长度: {len(self.token)} 字符")
        print(f"   完整内容: {self.token}")
        
        # 分析字符集
        hex_chars = set('0123456789abcdefABCDEF')
        token_chars = set(self.token)
        is_hex = token_chars.issubset(hex_chars)
        
        print(f"\n2. 字符集分析:")
        print(f"   是否为十六进制: {is_hex}")
        print(f"   唯一字符数: {len(token_chars)}")
        print(f"   字符集: {sorted(token_chars)[:20]}...")
        
        # 检查是否有模式
        print(f"\n3. 模式分析:")
        # 检查是否有重复模式
        patterns = []
        for i in range(2, min(20, len(self.token) // 2)):
            pattern = self.token[:i]
            count = self.token.count(pattern)
            if count > 1:
                patterns.append((pattern, count))
        
        if patterns:
            print(f"   发现重复模式:")
            for pattern, count in patterns[:5]:
                print(f"      '{pattern}' 出现 {count} 次")
        else:
            print(f"   未发现明显的重复模式")
        
        # 分析 token 的分布
        print(f"\n4. 字符分布:")
        char_counts = {}
        for char in self.token:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        sorted_chars = sorted(char_counts.items(), key=lambda x: x[1], reverse=True)
        print(f"   最常见的字符:")
        for char, count in sorted_chars[:10]:
            print(f"      '{char}': {count} 次 ({count/len(self.token)*100:.1f}%)")
    
    def find_api_responses(self):
        """查找 API 响应，特别是 /admin/api.php"""
        print("\n" + "=" * 60)
        print("[分析] API 调用分析")
        print("=" * 60)
        
        api_calls = []
        for call in self.api_calls:
            url = call.get('url', '')
            if 'api.php' in url or 'api' in url.lower():
                api_calls.append(call)
        
        print(f"\n找到 {len(api_calls)} 个 API 调用:")
        for i, call in enumerate(api_calls, 1):
            print(f"\n[{i}] {call.get('url', 'N/A')}")
            print(f"    方法: {call.get('method', 'N/A')}")
            print(f"    参数: {call.get('params', {})}")
            print(f"    时间戳: {call.get('timestamp', 'N/A')}")
        
        # 查找 /admin/api.php
        admin_api = None
        for call in api_calls:
            if '/admin/api.php' in call.get('url', ''):
                admin_api = call
                break
        
        if admin_api:
            print(f"\n[OK] 找到关键 API: /admin/api.php")
            print(f"   时间戳: {admin_api.get('timestamp', 'N/A')}")
            print(f"   [WARN] 注意: 响应内容未在捕获数据中，需要重新捕获")
        else:
            print(f"\n[WARN] 未找到 /admin/api.php 调用")
    
    def analyze_m3u8_url(self):
        """分析 m3u8 URL 的结构"""
        print("\n" + "=" * 60)
        print("[分析] m3u8 URL 分析")
        print("=" * 60)
        
        if not self.m3u8_url:
            print("[ERROR] 没有 m3u8 URL 可分析")
            return
        
        parsed = urlparse(self.m3u8_url)
        print(f"\n1. URL 结构:")
        print(f"   协议: {parsed.scheme}")
        print(f"   域名: {parsed.netloc}")
        print(f"   路径: {parsed.path}")
        print(f"   查询参数: {parsed.query}")
        
        # 提取路径中的 hash
        path_parts = parsed.path.strip('/').split('/')
        print(f"\n2. 路径分析:")
        for i, part in enumerate(path_parts):
            print(f"   [{i}] {part}")
            # 检查是否是 hash (32字符的十六进制)
            if len(part) == 32 and all(c in '0123456789abcdefABCDEF' for c in part):
                print(f"       [OK] 可能是 hash: {part}")
        
        # 提取查询参数
        params = parse_qs(parsed.query)
        print(f"\n3. 查询参数:")
        for key, values in params.items():
            print(f"   {key}: {values[0][:100]}...")
    
    def analyze_token_generation_hypothesis(self):
        """分析 token 生成的可能方式"""
        print("\n" + "=" * 60)
        print("[分析] Token 生成假设分析")
        print("=" * 60)
        
        if not self.token:
            print("❌ 没有 token 可分析")
            return
        
        # 假设1: token 是基于 video_url 生成的
        print(f"\n假设1: token 基于 video_url 生成")
        print(f"   video_url: {self.video_url}")
        
        # 尝试不同的 hash 算法
        hash_algorithms = ['md5', 'sha1', 'sha256']
        for algo_name in hash_algorithms:
            algo = getattr(hashlib, algo_name)
            hash_value = algo(self.video_url.encode()).hexdigest()
            print(f"   {algo_name.upper()}(video_url): {hash_value}")
            if hash_value in self.token:
                print(f"      [OK] 找到匹配！")
        
        # 假设2: token 是基于 API 响应中的某个字段生成的
        print(f"\n假设2: token 基于 API 响应字段生成")
        print(f"   [WARN] 需要获取 /admin/api.php 的响应内容")
        print(f"   [TIP] 建议: 重新运行捕获脚本，确保捕获响应内容")
        
        # 假设3: token 是加密后的数据
        print(f"\n假设3: token 是加密数据")
        print(f"   token 长度: {len(self.token)}")
        print(f"   如果是 Base64 编码: {len(self.token) % 4 == 0}")
        
        # 尝试 Base64 解码
        try:
            # token 看起来是十六进制，尝试先转换为字节再 Base64
            if all(c in '0123456789abcdefABCDEF' for c in self.token):
                bytes_data = bytes.fromhex(self.token)
                print(f"   转换为字节后长度: {len(bytes_data)}")
                
                # 尝试 Base64 编码
                base64_encoded = base64.b64encode(bytes_data).decode()
                print(f"   Base64 编码: {base64_encoded[:100]}...")
        except Exception as e:
            print(f"   [WARN] 转换失败: {e}")
        
        # 假设4: token 包含时间戳或其他动态信息
        print(f"\n假设4: token 包含时间戳")
        # 查找可能的 Unix 时间戳（10位数字）
        timestamp_pattern = r'\d{10}'
        timestamps = re.findall(timestamp_pattern, self.token)
        if timestamps:
            print(f"   找到可能的 Unix 时间戳:")
            for ts in timestamps:
                import datetime
                try:
                    dt = datetime.datetime.fromtimestamp(int(ts))
                    print(f"      {ts} -> {dt}")
                except:
                    pass
        else:
            print(f"   未找到明显的 Unix 时间戳")
    
    def generate_improved_capture_script(self):
        """生成改进的捕获脚本，确保捕获 API 响应"""
        print("\n" + "=" * 60)
        print("[建议] 改进建议")
        print("=" * 60)
        
        print("""
为了确定 token 的生成方式，需要：

1. [OK] 捕获 /admin/api.php 的完整响应内容
   - 当前脚本已经尝试读取响应，但可能响应为空或格式不对
   - 需要确保响应内容被正确保存

2. [OK] 分析 JavaScript 代码中的 token 生成逻辑
   - 查找 7zl.js 和 7zlplayer.js 中的相关代码
   - 查找 'token'、'cachem3u8'、'Cache' 等关键字

3. [OK] 监听所有网络请求，包括重定向
   - token 可能通过重定向传递
   - 需要跟踪完整的请求链

4. [OK] 在浏览器控制台中执行 JavaScript 代码
   - 尝试直接调用生成 token 的函数
   - 查看 window 对象中的相关变量

建议修改 capture_jx_m3u8_tv_params.py：
- 确保所有响应内容都被保存（包括 /admin/api.php）
- 保存响应内容到单独的文件
- 添加更详细的日志输出
        """)
    
    def run_full_analysis(self):
        """运行完整分析"""
        print("=" * 60)
        print("[分析] Token 生成方式分析")
        print("=" * 60)
        
        self.analyze_token_structure()
        self.find_api_responses()
        self.analyze_m3u8_url()
        self.analyze_token_generation_hypothesis()
        self.generate_improved_capture_script()
        
        print("\n" + "=" * 60)
        print("[总结]")
        print("=" * 60)
        print("""
关键发现：
1. token 是一个长字符串（约200+字符）
2. token 出现在 m3u8 URL 的查询参数中
3. /admin/api.php 被调用，但响应内容未捕获
4. token 的生成逻辑可能在 JavaScript 代码中

下一步行动：
1. 重新运行捕获脚本，确保捕获 /admin/api.php 的响应
2. 分析 JavaScript 代码（7zl.js、7zlplayer.js）查找 token 生成逻辑
3. 在浏览器控制台中调试，直接调用相关函数
        """)


def main():
    """主函数"""
    analyzer = TokenAnalyzer('captured_jx_m3u8_tv_params.json')
    analyzer.run_full_analysis()


if __name__ == '__main__':
    main()

