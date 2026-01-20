# JELILIAN AI PRO Gunicorn生产环境配置

import multiprocessing
import os

# 服务器绑定
bind = "127.0.0.1:8000"

# 工作进程数 (根据CPU核心数调整)
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"

# 连接配置
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100

# 超时配置
timeout = 30
keepalive = 2
graceful_timeout = 30

# 性能优化
preload_app = True
worker_tmp_dir = "/dev/shm"  # 使用内存文件系统

# 日志配置
accesslog = "/var/log/gunicorn-access.log"
errorlog = "/var/log/gunicorn-error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程管理
pidfile = "/var/run/gunicorn-jelilian-ai-pro.pid"
daemon = False  # Supervisor管理，不需要守护进程

# 用户和组
user = "www-data"
group = "www-data"

# 临时目录
tmp_upload_dir = "/tmp"

# SSL配置 (如果需要Gunicorn处理SSL)
# keyfile = "/path/to/private.key"
# certfile = "/path/to/certificate.crt"

# 环境变量
raw_env = [
    "ENVIRONMENT=production",
    "PYTHONPATH=/opt/jelilian-ai-pro"
]

# 钩子函数
def on_starting(server):
    """服务器启动时调用"""
    server.log.info("JELILIAN AI PRO 服务器启动中...")

def on_reload(server):
    """服务器重载时调用"""
    server.log.info("JELILIAN AI PRO 服务器重载中...")

def worker_int(worker):
    """工作进程中断时调用"""
    worker.log.info("工作进程 %s 被中断", worker.pid)

def pre_fork(server, worker):
    """工作进程fork前调用"""
    server.log.info("工作进程 %s 即将启动", worker.pid)

def post_fork(server, worker):
    """工作进程fork后调用"""
    server.log.info("工作进程 %s 已启动", worker.pid)

def post_worker_init(worker):
    """工作进程初始化后调用"""
    worker.log.info("工作进程 %s 初始化完成", worker.pid)

def worker_abort(worker):
    """工作进程异常退出时调用"""
    worker.log.info("工作进程 %s 异常退出", worker.pid)

def pre_exec(server):
    """执行前调用"""
    server.log.info("JELILIAN AI PRO 准备执行")

def when_ready(server):
    """服务器准备就绪时调用"""
    server.log.info("JELILIAN AI PRO 服务器已就绪")

def worker_exit(server, worker):
    """工作进程退出时调用"""
    server.log.info("工作进程 %s 已退出", worker.pid)

def nworkers_changed(server, new_value, old_value):
    """工作进程数量变化时调用"""
    server.log.info("工作进程数量从 %s 变更为 %s", old_value, new_value)

def on_exit(server):
    """服务器退出时调用"""
    server.log.info("JELILIAN AI PRO 服务器已退出")