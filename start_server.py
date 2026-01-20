#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JELILIAN AI PRO 自动启动脚本
双击运行即可启动网站
"""

import subprocess
import sys
import os
import webbrowser
import time

def main():
    print("=" * 50)
    print("🚀 JELILIAN AI PRO 启动中...")
    print("=" * 50)
    
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    
    # 检查依赖
    print("\n📦 检查依赖...")
    try:
        import fastapi
        import uvicorn
        print("   ✅ 依赖已安装")
    except ImportError:
        print("   ⚠️ 正在安装依赖...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # 启动服务器
    print("\n🌐 启动Web服务器...")
    print("   地址: http://localhost:8003")
    print("   按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    # 3秒后自动打开浏览器
    def open_browser():
        time.sleep(3)
        webbrowser.open("http://localhost:8003")
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # 启动服务器
    import uvicorn
    uvicorn.run("advanced_web:app", host="0.0.0.0", port=8003, reload=False)

if __name__ == "__main__":
    main()
