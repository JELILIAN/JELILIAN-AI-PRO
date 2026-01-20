#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包项目用于部署
生成 jelilian-deploy.zip 文件
"""

import os
import zipfile
from datetime import datetime

def pack_project():
    # 需要打包的文件和文件夹
    include_files = [
        'advanced_web.py',
        'autogen_system.py',
        'credit_manager.py',
        'deploy.py',
        'Dockerfile',
        'payment_routes.py',
        'requirements.txt',
        'start_server.py',
        'start.bat',
        'translations.py',
        'trial_manager.py',
        'user_manager.py',
        'README.md',
        'README_zh.md',
        'DEPLOY_GUIDE.md',
        'vercel.json',
        '.gitignore',
    ]
    
    include_folders = [
        'app',
        'assets',
        'config',
        'deploy',
        'api',
    ]
    
    # 排除的文件
    exclude_patterns = [
        '__pycache__',
        '.pyc',
        '.venv',
        '.git',
        'logs',
        '.json',  # 排除数据文件
    ]
    
    # 创建zip文件
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_filename = f'jelilian-deploy-{timestamp}.zip'
    
    print(f"正在创建部署包: {zip_filename}")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 添加单个文件
        for file in include_files:
            if os.path.exists(file):
                zipf.write(file)
                print(f"  + {file}")
        
        # 添加文件夹
        for folder in include_folders:
            if os.path.exists(folder):
                for root, dirs, files in os.walk(folder):
                    # 排除不需要的目录
                    dirs[:] = [d for d in dirs if not any(p in d for p in exclude_patterns)]
                    
                    for file in files:
                        if not any(p in file for p in exclude_patterns):
                            filepath = os.path.join(root, file)
                            zipf.write(filepath)
                            print(f"  + {filepath}")
    
    file_size = os.path.getsize(zip_filename) / 1024 / 1024
    print(f"\n✅ 打包完成: {zip_filename} ({file_size:.2f} MB)")
    print(f"\n上传到服务器:")
    print(f"  scp {zip_filename} root@你的服务器IP:/var/www/")
    
    return zip_filename

if __name__ == "__main__":
    pack_project()
