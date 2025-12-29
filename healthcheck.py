#!/usr/bin/env python3
"""
健康检查脚本
用于Docker健康检查，避免依赖curl
"""
import sys
import requests

try:
    response = requests.get("http://localhost:8000/health", timeout=5)
    if response.status_code == 200:
        data = response.json()
        if data.get("status") in ["healthy", "degraded"]:
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        sys.exit(1)
except Exception as e:
    print(f"Health check failed: {e}", file=sys.stderr)
    sys.exit(1)

