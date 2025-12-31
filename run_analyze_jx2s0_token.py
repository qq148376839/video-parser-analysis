"""
运行 jx.2s0.cn token 分析脚本
"""

import asyncio
from analyze_jx2s0_token import Jx2s0TokenAnalyzer

if __name__ == '__main__':
    print("🚀 启动 jx.2s0.cn token 分析...")
    asyncio.run(Jx2s0TokenAnalyzer().analyze())

