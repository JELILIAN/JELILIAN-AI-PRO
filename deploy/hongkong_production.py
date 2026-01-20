#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JELILIAN AI PRO - 香港地域生产环境启动器
优化配置：网络延迟、并发处理、资源管理
"""

import uvicorn
import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def setup_logging():
    """配置日志系统"""
    log_dir = Path("/var/log/jelilian")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app.log"),
            logging.StreamHandler()
        ]
    )
    
    # 设置uvicorn日志
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(logging.INFO)

def get_server_config():
    """获取香港地域优化的服务器配置"""
    return {
        "host": "0.0.0.0",
        "port": 8003,
        "workers": 4,  # 香港服务器通常配置较好，可以多进程
        "worker_class": "uvicorn.workers.UvicornWorker",
        "worker_connections": 1000,
        "max_requests": 1000,
        "max_requests_jitter": 100,
        "timeout": 300,  # 5分钟超时，适应香港网络环境
        "keepalive": 65,
        "preload_app": True,
        "access_log": True,
        "error_log": "/var/log/jelilian/error.log",
        "access_logfile": "/var/log/jelilian/access.log",
        "log_level": "info"
    }

def check_environment():
    """检查运行环境"""
    print("🔍 检查运行环境...")
    
    # 检查必要文件
    required_files = [
        "advanced_web.py",
        "user_manager.py",
        "credit_manager.py",
        "trial_manager.py",
        "autogen_system.py",
        "payment_routes.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not (project_root / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
        return False
    
    # 检查配置文件
    config_dir = project_root / "config"
    if not config_dir.exists():
        print("❌ 缺少config目录")
        return False
    
    # 检查日志目录
    log_dir = Path("/var/log/jelilian")
    if not log_dir.exists():
        log_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建日志目录: {log_dir}")
    
    # 检查assets目录
    assets_dir = project_root / "assets"
    if not assets_dir.exists():
        assets_dir.mkdir(exist_ok=True)
        print(f"✅ 创建assets目录: {assets_dir}")
    
    print("✅ 环境检查通过")
    return True

def optimize_for_hongkong():
    """香港地域特定优化"""
    print("🇭🇰 应用香港地域优化...")
    
    # 设置环境变量
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    
    # 网络优化
    os.environ.setdefault("HTTPX_TIMEOUT", "60")
    os.environ.setdefault("REQUESTS_TIMEOUT", "60")
    
    # 香港时区
    os.environ.setdefault("TZ", "Asia/Hong_Kong")
    
    print("✅ 香港地域优化完成")

def main():
    """主函数"""
    print("🚀 JELILIAN AI PRO - 香港生产环境启动")
    print("=" * 50)
    
    # 检查环境
    if not check_environment():
        sys.exit(1)
    
    # 应用香港优化
    optimize_for_hongkong()
    
    # 设置日志
    setup_logging()
    
    # 获取配置
    config = get_server_config()
    
    print(f"📍 地域: 阿里云香港 (cn-hongkong)")
    print(f"🌐 监听地址: {config['host']}:{config['port']}")
    print(f"👥 工作进程: {config['workers']}")
    print(f"⏱️  超时时间: {config['timeout']}秒")
    print(f"📋 日志文件: {config['access_logfile']}")
    
    try:
        # 导入应用
        from advanced_web import app
        
        # 启动服务器
        uvicorn.run(
            "advanced_web:app",
            host=config["host"],
            port=config["port"],
            workers=config["workers"],
            timeout_keep_alive=config["keepalive"],
            access_log=config["access_log"],
            log_level=config["log_level"],
            reload=False,  # 生产环境不启用热重载
            loop="uvloop"  # 使用高性能事件循环
        )
        
    except KeyboardInterrupt:
        print("\n🛑 服务器停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        logging.error(f"服务器启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()