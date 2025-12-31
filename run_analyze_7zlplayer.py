"""
运行 7zlplayer.js 分析脚本
"""

import subprocess
import sys

if __name__ == '__main__':
    try:
        result = subprocess.run([sys.executable, 'analyze_7zlplayer_decrypt.py'], 
                              capture_output=True, text=True, encoding='utf-8', errors='ignore')
        print(result.stdout)
        if result.stderr:
            print("错误:", result.stderr)
    except Exception as e:
        print(f"运行失败: {e}")


