#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用付费key获取m3u8 URL（支持多key轮询和过期管理）
这是最简单可靠的方法，不需要逆向算法
"""

import requests
import re
import json
import os
from urllib.parse import quote
from typing import Optional, Dict, List
from datetime import datetime, timedelta

class PaidKeyM3U8Getter:
    """使用付费key获取m3u8 URL（支持多key轮询）"""
    
    def __init__(self, json_file: str = "registration_results.json"):
        """
        初始化
        
        参数:
            json_file: 包含key信息的JSON文件路径
                      可以是绝对路径或相对路径（相对于当前工作目录）
        """
        # 如果是相对路径，尝试从项目根目录查找
        if not os.path.isabs(json_file):
            # 获取项目根目录（假设脚本在 archive/jx2s0_analysis/ 目录下）
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(script_dir))
            root_path = os.path.join(project_root, json_file)
            
            # 优先使用项目根目录的文件
            if os.path.exists(root_path):
                self.json_file = root_path
            elif os.path.exists(json_file):
                self.json_file = os.path.abspath(json_file)
            else:
                self.json_file = json_file
        else:
            self.json_file = json_file
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        })
        self.current_uid = None
        self.current_key = None
    
    def load_keys(self) -> Dict:
        """加载key信息"""
        if not os.path.exists(self.json_file):
            raise FileNotFoundError(f"JSON文件不存在: {self.json_file}")
        
        with open(self.json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data
    
    def save_keys(self, data: Dict) -> None:
        """保存key信息"""
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def update_json_structure(self, keys: List[Dict]) -> tuple:
        """更新JSON结构，添加expire_date字段"""
        updated = False
        for key_info in keys:
            # 添加expire_date字段（如果不存在）
            if 'expire_date' not in key_info:
                register_time = datetime.strptime(key_info['register_time'], '%Y-%m-%d %H:%M:%S')
                expire_date = register_time + timedelta(days=355)
                key_info['expire_date'] = expire_date.strftime('%Y-%m-%d %H:%M:%S')
                updated = True
        return keys, updated
    
    def is_key_expired(self, key_info: Dict) -> bool:
        """检查key是否过期"""
        if 'expire_date' not in key_info:
            return False
        
        expire_date = datetime.strptime(key_info['expire_date'], '%Y-%m-%d %H:%M:%S')
        return datetime.now() > expire_date
    
    def get_next_valid_key(self) -> Optional[Dict]:
        """获取下一个有效的key"""
        data = self.load_keys()
        
        # 处理JSON格式：如果是列表，转换为带元数据的格式
        if isinstance(data, list):
            # 首次加载列表格式，转换为带元数据的格式
            keys = data
            current_index = getattr(self, '_current_index', 0)
            # 转换为新格式
            data = {
                'current_index': current_index,
                'keys': keys
            }
            # 保存新格式
            self.save_keys(data)
        elif isinstance(data, dict) and 'keys' in data:
            keys = data['keys']
            current_index = data.get('current_index', 0)
        else:
            raise ValueError(f"JSON格式不正确: 期望list或dict with 'keys'")
        
        # 更新JSON结构（添加expire_date）
        keys, updated = self.update_json_structure(keys)
        if updated:
            data['keys'] = keys
            self.save_keys(data)
        
        # 如果keys为空，返回None
        if not keys:
            return None
        
        # 确保current_index在有效范围内
        if current_index >= len(keys):
            current_index = 0
        
        # 查找下一个有效的key
        original_length = len(keys)
        attempts = 0
        
        while attempts < original_length * 2:  # 最多尝试2倍长度，防止无限循环
            # 如果keys为空，返回None
            if not keys:
                return None
            
            # 确保current_index在有效范围内
            if current_index >= len(keys):
                current_index = 0
            
            key_info = keys[current_index]
            
            # 检查是否过期
            if self.is_key_expired(key_info):
                print(f"⚠️ Key已过期: uid={key_info.get('uid')}, email={key_info.get('email')}")
                # 删除过期的key
                keys.pop(current_index)
                
                # 更新数据
                data['keys'] = keys
                
                # 如果删除后没有key了，返回None
                if not keys:
                    data['current_index'] = 0
                    self.save_keys(data)
                    return None
                
                # 更新current_index（如果删除后索引超出范围，重置为0）
                if current_index >= len(keys):
                    current_index = 0
                
                data['current_index'] = current_index
                self.save_keys(data)
                
                # 继续尝试当前索引（因为删除后，当前索引指向下一个元素）
                attempts += 1
                continue
            
            # 找到有效的key，更新current_index到下一个
            next_index = (current_index + 1) % len(keys) if keys else 0
            
            # 保存更新后的current_index
            data['current_index'] = next_index
            data['keys'] = keys
            self.save_keys(data)
            self._current_index = next_index
            
            return key_info
        
        # 所有key都过期了
        return None
    
    def get_m3u8_url(self, video_url: str, retry: bool = True) -> Optional[str]:
        """
        获取m3u8 URL（自动轮询key）
        
        参数:
            video_url: 视频URL（如：https://www.iqiyi.com/v_1c168e2yzbk.html）
            retry: 如果失败是否重试下一个key
        
        返回:
            m3u8 URL或None
        """
        # 获取下一个有效的key
        key_info = self.get_next_valid_key()
        if not key_info:
            print("❌ 没有可用的key")
            return None
        
        uid = key_info['uid']
        key = key_info['key']
        self.current_uid = uid
        self.current_key = key
        
        url = f"https://json.2s0.cn:5678/player/analysis.php/?uid={uid}&key={key}&url={quote(video_url)}"
        
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                html = response.text
                
                # 提取m3u8 URL
                m3u8_match = re.search(r'var url = "([^"]+)"', html)
                if m3u8_match:
                    m3u8_url = m3u8_match.group(1)
                    print(f"✅ 使用key: uid={uid}, email={key_info.get('email', 'N/A')}")
                    return m3u8_url
                else:
                    print(f"❌ 未找到m3u8 URL (uid={uid})")
                    # 如果允许重试，尝试下一个key
                    if retry:
                        print("   尝试下一个key...")
                        return self.get_m3u8_url(video_url, retry=False)
                    return None
            else:
                print(f"❌ 请求失败: {response.status_code} (uid={uid})")
                # 如果允许重试，尝试下一个key
                if retry:
                    print("   尝试下一个key...")
                    return self.get_m3u8_url(video_url, retry=False)
                return None
        except Exception as e:
            print(f"❌ 错误: {e} (uid={uid})")
            # 如果允许重试，尝试下一个key
            if retry:
                print("   尝试下一个key...")
                return self.get_m3u8_url(video_url, retry=False)
            return None
    
    def get_m3u8_info(self, video_url: str) -> Optional[dict]:
        """
        获取m3u8 URL的详细信息（包括hash和token）
        
        参数:
            video_url: 视频URL
        
        返回:
            包含m3u8_url、hash、token的字典或None
        """
        m3u8_url = self.get_m3u8_url(video_url)
        if not m3u8_url:
            return None
        
        # 提取hash和token
        hash_match = re.search(r'/Cache/Ff/([a-f0-9]+)\.m3u8', m3u8_url)
        token_match = re.search(r'token=([^"]+)', m3u8_url)
        
        result = {
            'm3u8_url': m3u8_url,
            'hash': hash_match.group(1) if hash_match else None,
            'token': token_match.group(1) if token_match else None,
        }
        
        return result
    
    def download_m3u8_file(self, m3u8_url: str, output_path: str = None) -> Optional[str]:
        """
        下载m3u8文件本身（文本文件）
        
        参数:
            m3u8_url: m3u8 URL
            output_path: 输出文件路径（如果不指定，自动生成）
        
        返回:
            下载的m3u8文件路径或None
        """
        if not m3u8_url:
            print("❌ m3u8 URL为空")
            return None
        
        print(f"\n📥 开始下载m3u8文件...")
        print(f"   m3u8 URL: {m3u8_url[:100]}...")
        
        try:
            # 下载m3u8文件内容
            response = self.session.get(m3u8_url, timeout=30)
            response.raise_for_status()
            m3u8_content = response.text
            
            # 生成输出文件名
            if not output_path:
                # 从URL提取hash
                hash_match = re.search(r'/Cache/[^/]+/([a-f0-9]+)\.m3u8', m3u8_url)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                if hash_match:
                    # 使用hash + 时间戳避免冲突
                    base_name = f"m3u8_{hash_match.group(1)}_{timestamp}"
                else:
                    # 如果没有hash，只使用时间戳
                    base_name = f"m3u8_{timestamp}"
                
                output_path = f"{base_name}.m3u8"
                
                # 如果文件已存在，添加序号
                counter = 1
                original_path = output_path
                while os.path.exists(output_path):
                    output_path = f"{base_name}_{counter}.m3u8"
                    counter += 1
                    if counter > 1000:  # 防止无限循环
                        break
            
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path) if os.path.dirname(output_path) else '.'
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            # 保存m3u8文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(m3u8_content)
            
            file_size = os.path.getsize(output_path)
            print(f"✅ m3u8文件下载成功！")
            print(f"   文件路径: {os.path.abspath(output_path)}")
            print(f"   文件大小: {file_size} 字节")
            print(f"   包含片段数: {m3u8_content.count('#EXTINF')}")
            
            return os.path.abspath(output_path)
            
        except Exception as e:
            print(f"❌ 下载失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def download_m3u8_from_video(self, video_url: str, output_path: str = None) -> Optional[str]:
        """
        从视频URL获取m3u8并下载m3u8文件
        
        参数:
            video_url: 原始视频URL
            output_path: 输出文件路径
        
        返回:
            下载的m3u8文件路径或None
        """
        print("="*80)
        print("获取并下载m3u8文件")
        print("="*80)
        
        # 1. 获取m3u8 URL
        m3u8_url = self.get_m3u8_url(video_url)
        if not m3u8_url:
            print("❌ 无法获取m3u8 URL")
            return None
        
        # 2. 下载m3u8文件
        return self.download_m3u8_file(m3u8_url, output_path)

def main():
    """主函数 - 使用示例"""
    # 创建获取器（自动从JSON文件加载keys）
    # 尝试从项目根目录查找JSON文件
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    json_file = os.path.join(project_root, "registration_results.json")
    
    # 如果项目根目录不存在，使用当前目录
    if not os.path.exists(json_file):
        json_file = "registration_results.json"
    
    getter = PaidKeyM3U8Getter(json_file)
    
    # 测试视频URL
    test_urls = [
        "https://v.youku.com/v_show/id_XMTA0MTc5NjU2.html",
        "https://v.youku.com/v_show/id_XMTA0MTc5NjU2.html#2",
    ]
    
    print("="*80)
    print("使用付费key获取m3u8 URL（多key轮询）")
    print("="*80)
    print()
    
    # 显示当前key统计
    try:
        data = getter.load_keys()
        if isinstance(data, dict) and 'keys' in data:
            keys = data['keys']
            current_index = data.get('current_index', 0)
        elif isinstance(data, list):
            keys = data
            current_index = 0
        else:
            keys = []
            current_index = 0
        
        print(f"📊 Key统计:")
        print(f"   总key数: {len(keys)}")
        print(f"   当前索引: {current_index}")
        
        # 统计过期和有效的key
        expired_count = sum(1 for k in keys if getter.is_key_expired(k))
        valid_count = len(keys) - expired_count
        print(f"   有效key数: {valid_count}")
        print(f"   过期key数: {expired_count}")
        
        # 显示当前使用的key信息
        if keys and current_index < len(keys):
            current_key_info = keys[current_index]
            print(f"   当前key: uid={current_key_info.get('uid')}, email={current_key_info.get('email', 'N/A')}")
            if 'expire_date' in current_key_info:
                print(f"   过期日期: {current_key_info['expire_date']}")
        print()
    except Exception as e:
        print(f"⚠️ 无法加载key统计: {e}")
        import traceback
        traceback.print_exc()
        print()
    
    for video_url in test_urls:
        print(f"视频URL: {video_url}")
        print("-"*80)
        
        # 获取m3u8信息（自动轮询key）
        info = getter.get_m3u8_info(video_url)
        
        if info:
            print(f"✅ m3u8 URL: {info['m3u8_url']}")
            print(f"✅ Hash: {info['hash']}")
            print(f"✅ Token: {info['token'][:50]}...")
            
            # 提示并下载m3u8文件
            print("\n💡 提示: token有时效性，建议立即保存m3u8文件")
            print("   正在下载m3u8文件...")
            
            # 下载m3u8文件
            output_file = getter.download_m3u8_file(info['m3u8_url'])
            if output_file:
                print(f"\n🎉 m3u8文件已保存到: {output_file}")
            else:
                print("\n⚠️ 下载失败，但m3u8 URL仍然有效（token未过期）")
        else:
            print("❌ 获取失败")
        
        print()

if __name__ == "__main__":
    main()

