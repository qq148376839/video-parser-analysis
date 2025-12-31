"""
使用 final_direct_parser_v2.py 的解密逻辑测试 jx.2s0.cn 的 token 生成
"""

import requests
import json
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
from urllib.parse import urlparse, parse_qs
from typing import Optional


class Jx2s0TokenTester:
    """使用解密逻辑测试 token 生成"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://jx.2s0.cn/',
        })
    
    def get_admin_api_response(self) -> Optional[dict]:
        """获取 /admin/api.php 的响应"""
        print("\n[步骤1] 获取 /admin/api.php 响应...")
        api_url = "https://jx.2s0.cn/admin/api.php"
        
        try:
            response = self.session.get(api_url, timeout=30)
            print(f"   状态码: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    print(f"   [OK] JSON解析成功")
                    print(f"   响应内容:")
                    print(json.dumps(json_data, indent=4, ensure_ascii=False)[:500])
                    return json_data
                except json.JSONDecodeError:
                    print(f"   [WARN] 响应不是JSON格式")
                    print(f"   响应内容: {response.text[:500]}")
                    return {'raw': response.text}
            else:
                print(f"   [ERROR] API返回错误状态码")
                return None
        except Exception as e:
            print(f"   [ERROR] 请求失败: {e}")
            return None
    
    def generate_key_iv(self, uid: str = None, config_data: dict = None):
        """生成密钥和IV，使用与 final_direct_parser_v2.py 相同的逻辑"""
        print("\n[步骤2] 生成密钥和IV...")
        
        # 如果没有提供 uid，尝试从 config_data 中提取
        if not uid and config_data:
            # 尝试从响应中提取 uid 或 id
            if isinstance(config_data, dict):
                if 'data' in config_data:
                    data = config_data['data']
                    uid = data.get('uid') or data.get('id') or data.get('user_id')
                else:
                    uid = config_data.get('uid') or config_data.get('id')
        
        # 如果还是没有 uid，使用默认值或从 token 中推测
        if not uid:
            print(f"   [WARN] 未找到 uid，尝试使用默认逻辑")
            # 可能需要从其他来源获取 uid
        
        # Key生成方式（与 final_direct_parser_v2.py 相同）
        if uid:
            key_str = '2890' + uid + 'tB959C'
        else:
            # 如果没有 uid，尝试其他可能的组合
            key_str = '2890' + 'tB959C'  # 默认值
        
        key_bytes = key_str.encode('utf-8')
        print(f"   Key字符串: {key_str}")
        print(f"   Key长度: {len(key_bytes)} 字节")
        
        # 生成多种密钥方式
        key_methods = []
        
        # 方式1: MD5哈希（16字节）- 最常用
        key_methods.append(("MD5哈希", hashlib.md5(key_bytes).digest()))
        
        # 方式2: SHA256哈希（前16字节）
        key_methods.append(("SHA256前16字节", hashlib.sha256(key_bytes).digest()[:16]))
        
        # 方式3: SHA256哈希（前24字节）
        key_methods.append(("SHA256前24字节", hashlib.sha256(key_bytes).digest()[:24]))
        
        # 方式4: SHA256哈希（前32字节）
        key_methods.append(("SHA256前32字节", hashlib.sha256(key_bytes).digest()[:32]))
        
        # IV生成方式（与 final_direct_parser_v2.py 相同）
        iv_str = '2F131BE91247866E'
        iv_methods = [
            ("UTF-8编码(16字节)", iv_str.encode('utf-8')),
            ("十六进制解析+填充", bytes.fromhex(iv_str).ljust(16, b'\0')),
            ("重复填充", (bytes.fromhex(iv_str) * 2)[:16]),
        ]
        
        return key_methods, iv_methods, uid
    
    def test_token_encryption(self, token: str, data_to_encrypt: str, key_methods: list, iv_methods: list):
        """测试 token 是否是加密后的数据"""
        print("\n[步骤3] 测试 token 加密逻辑...")
        print(f"   Token: {token[:50]}...")
        print(f"   Token长度: {len(token)} 字符 ({len(token)//2} 字节)")
        
        # Token 是十六进制字符串，转换为字节
        try:
            token_bytes = bytes.fromhex(token)
            print(f"   Token字节长度: {len(token_bytes)} 字节")
        except Exception as e:
            print(f"   [ERROR] Token不是有效的十六进制: {e}")
            return None
        
        # 尝试解密 token（反向操作）
        print(f"\n   尝试解密 token（使用 {len(key_methods)} x {len(iv_methods)} = {len(key_methods) * len(iv_methods)} 种组合）...")
        
        for key_name, key in key_methods:
            # 确保key长度正确
            if len(key) not in [16, 24, 32]:
                continue
            
            for iv_name, iv in iv_methods:
                # 确保IV长度为16字节
                if len(iv) != 16:
                    if len(iv) < 16:
                        iv = iv.ljust(16, b'\0')
                    else:
                        iv = iv[:16]
                
                try:
                    # AES-CBC解密
                    cipher = AES.new(key, AES.MODE_CBC, iv)
                    decrypted = cipher.decrypt(token_bytes)
                    
                    # 尝试移除PKCS7填充
                    try:
                        decrypted_unpadded = unpad(decrypted, AES.block_size)
                        result = decrypted_unpadded.decode('utf-8')
                        
                        print(f"\n   [OK] 解密成功！")
                        print(f"   密钥方式: {key_name}")
                        print(f"   IV方式: {iv_name}")
                        print(f"   解密结果: {result[:200]}")
                        return {
                            'key_method': key_name,
                            'iv_method': iv_name,
                            'decrypted': result
                        }
                    except ValueError:
                        # 填充移除失败，尝试手动移除
                        try:
                            padding_len = decrypted[-1]
                            if 1 <= padding_len <= 16:
                                decrypted_manual = decrypted[:-padding_len]
                                result_manual = decrypted_manual.decode('utf-8')
                                
                                print(f"\n   [OK] 手动移除填充后解密成功！")
                                print(f"   密钥方式: {key_name}")
                                print(f"   IV方式: {iv_name}")
                                print(f"   解密结果: {result_manual[:200]}")
                                return {
                                    'key_method': key_name,
                                    'iv_method': iv_name,
                                    'decrypted': result_manual
                                }
                        except:
                            pass
                
                except Exception:
                    continue
        
        print(f"\n   [WARN] 无法解密 token")
        return None
    
    def test_token_generation(self, config_data: dict, video_url: str, token: str):
        """测试 token 的生成方式"""
        print("\n[步骤4] 测试 token 生成方式...")
        
        # 提取可能的输入数据
        input_data_candidates = []
        
        if isinstance(config_data, dict):
            if 'data' in config_data:
                data = config_data['data']
                # 可能的输入数据
                if 'url' in data:
                    input_data_candidates.append(('config.url', data['url']))
                if 'id' in data:
                    input_data_candidates.append(('config.id', data['id']))
                if 'uid' in data:
                    input_data_candidates.append(('config.uid', data['uid']))
        
        # 添加 video_url
        input_data_candidates.append(('video_url', video_url))
        
        # 组合数据
        if len(input_data_candidates) > 1:
            combined = '|'.join([str(v) for _, v in input_data_candidates])
            input_data_candidates.append(('combined', combined))
        
        print(f"   找到 {len(input_data_candidates)} 个可能的输入数据")
        
        # 生成密钥和IV
        uid = None
        if isinstance(config_data, dict) and 'data' in config_data:
            uid = config_data['data'].get('uid') or config_data['data'].get('id')
        
        key_methods, iv_methods, uid = self.generate_key_iv(uid, config_data)
        
        # 尝试加密每个输入数据，看是否能生成 token
        print(f"\n   尝试加密输入数据生成 token...")
        
        for data_name, data_value in input_data_candidates:
            data_str = str(data_value)
            data_bytes = data_str.encode('utf-8')
            
            # 需要填充到16字节的倍数
            if len(data_bytes) % 16 != 0:
                data_bytes = pad(data_bytes, AES.block_size)
            
            for key_name, key in key_methods:
                if len(key) not in [16, 24, 32]:
                    continue
                
                for iv_name, iv in iv_methods:
                    if len(iv) != 16:
                        if len(iv) < 16:
                            iv = iv.ljust(16, b'\0')
                        else:
                            iv = iv[:16]
                    
                    try:
                        # AES-CBC加密
                        cipher = AES.new(key, AES.MODE_CBC, iv)
                        encrypted = cipher.encrypt(data_bytes)
                        
                        # 转换为十六进制
                        encrypted_hex = encrypted.hex()
                        
                        # 检查是否与 token 匹配（完全匹配或部分匹配）
                        if encrypted_hex == token:
                            print(f"\n   [OK] 完全匹配！")
                            print(f"   输入数据: {data_name} = {data_value[:100]}")
                            print(f"   密钥方式: {key_name}")
                            print(f"   IV方式: {iv_name}")
                            print(f"   生成的token: {encrypted_hex[:50]}...")
                            return {
                                'input_data': data_name,
                                'input_value': data_value,
                                'key_method': key_name,
                                'iv_method': iv_name,
                                'generated_token': encrypted_hex
                            }
                        elif encrypted_hex.startswith(token[:32]) or token.startswith(encrypted_hex[:32]):
                            print(f"\n   [PARTIAL] 部分匹配（前32字符）")
                            print(f"   输入数据: {data_name} = {data_value[:100]}")
                            print(f"   密钥方式: {key_name}")
                            print(f"   IV方式: {iv_name}")
                            print(f"   生成的token: {encrypted_hex[:50]}...")
                            print(f"   实际token: {token[:50]}...")
                    
                    except Exception:
                        continue
        
        print(f"\n   [WARN] 无法通过加密生成匹配的 token")
        return None
    
    def run_test(self, video_url: str, token: str):
        """运行完整测试"""
        print("=" * 60)
        print("使用解密逻辑测试 jx.2s0.cn token 生成")
        print("=" * 60)
        print(f"视频URL: {video_url}")
        print(f"Token: {token[:50]}...")
        
        # 步骤1: 获取 API 响应
        config_data = self.get_admin_api_response()
        
        # 步骤2: 生成密钥和IV
        uid = None
        if config_data and isinstance(config_data, dict) and 'data' in config_data:
            uid = config_data['data'].get('uid') or config_data['data'].get('id')
        
        key_methods, iv_methods, uid = self.generate_key_iv(uid, config_data)
        
        # 步骤3: 测试 token 解密
        if config_data and isinstance(config_data, dict) and 'data' in config_data:
            data_url = config_data['data'].get('url', '')
            if data_url:
                decrypt_result = self.test_token_encryption(token, data_url, key_methods, iv_methods)
                if decrypt_result:
                    print("\n[成功] Token 解密成功！")
                    return decrypt_result
        
        # 步骤4: 测试 token 生成
        if config_data:
            gen_result = self.test_token_generation(config_data, video_url, token)
            if gen_result:
                print("\n[成功] Token 生成成功！")
                return gen_result
        
        # 步骤5: 尝试直接解密 token（不依赖 API 响应）
        print("\n[步骤5] 尝试直接解密 token...")
        decrypt_result = self.test_token_encryption(token, '', key_methods, iv_methods)
        
        if decrypt_result:
            print("\n[成功] Token 直接解密成功！")
            return decrypt_result
        
        print("\n[失败] 所有测试都未找到匹配的 token 生成方式")
        print("\n[建议]")
        print("   1. 确保捕获了 /admin/api.php 的完整响应")
        print("   2. 检查响应中是否包含 uid 或其他关键字段")
        print("   3. 尝试在浏览器控制台中查看 token 的生成过程")
        
        return None


def main():
    """主函数"""
    # 从捕获的数据中提取信息
    with open('captured_jx_m3u8_tv_params.json', 'r', encoding='utf-8') as f:
        captured_data = json.load(f)
    
    video_url = captured_data['video_url']
    
    # 提取 token
    token = None
    for params in captured_data.get('captured_params', []):
        if 'token' in params:
            token = params['token']
            break
    
    if not token:
        print("[ERROR] 未找到 token")
        return
    
    print(f"视频URL: {video_url}")
    print(f"Token: {token[:50]}...")
    
    # 运行测试
    tester = Jx2s0TokenTester()
    result = tester.run_test(video_url, token)
    
    # 保存结果
    if result:
        with open('token_test_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n[OK] 测试结果已保存到: token_test_result.json")


if __name__ == '__main__':
    main()


