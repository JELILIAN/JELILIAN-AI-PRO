# JELILIAN AI PRO 阿里云部署指南

## 🚀 部署方案概览

### 推荐架构
- **ECS服务器**: 运行应用程序
- **SLB负载均衡**: 提供高可用性
- **RDS数据库**: 存储用户数据(可选)
- **OSS对象存储**: 存储静态文件
- **域名备案**: 绑定自定义域名

## 📋 部署准备

### 1. 阿里云资源准备
- [ ] ECS云服务器 (推荐配置: 2核4G)
- [ ] 安全组配置 (开放80, 443, 8000端口)
- [ ] 域名解析 (可选)
- [ ] SSL证书 (HTTPS访问)

### 2. 服务器环境要求
- **操作系统**: Ubuntu 20.04 LTS / CentOS 8
- **Python版本**: 3.11+
- **内存**: 最低2GB，推荐4GB+
- **存储**: 最低20GB

## 🛠️ 自动化部署脚本

### 服务器初始化脚本
```bash
#!/bin/bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python 3.11
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-pip -y

# 安装Nginx
sudo apt install nginx -y

# 安装Git
sudo apt install git -y

# 创建应用目录
sudo mkdir -p /opt/jelilian-ai-pro
sudo chown $USER:$USER /opt/jelilian-ai-pro
```

### 应用部署脚本
```bash
#!/bin/bash
cd /opt/jelilian-ai-pro

# 克隆代码
git clone <your-repo-url> .

# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装生产环境依赖
pip install gunicorn supervisor

# 创建配置文件
cp config/config.example.toml config/config.toml
```

## 🔧 生产环境配置

### 1. Gunicorn配置
```python
# gunicorn_config.py
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
```

### 2. Nginx配置
```nginx
# /etc/nginx/sites-available/jelilian-ai-pro
server {
    listen 80;
    server_name your-domain.com;  # 替换为您的域名
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;  # 替换为您的域名
    
    # SSL证书配置
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    # 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # 应用代理
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # 静态文件
    location /static/ {
        alias /opt/jelilian-ai-pro/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 3. Supervisor配置
```ini
# /etc/supervisor/conf.d/jelilian-ai-pro.conf
[program:jelilian-ai-pro]
command=/opt/jelilian-ai-pro/venv/bin/gunicorn -c gunicorn_config.py web_launcher:app
directory=/opt/jelilian-ai-pro
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/jelilian-ai-pro.log
environment=PATH="/opt/jelilian-ai-pro/venv/bin"
```

## 🔐 安全配置

### 1. 防火墙设置
```bash
# UFW防火墙配置
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 2. 环境变量配置
```bash
# /opt/jelilian-ai-pro/.env
QWEN_API_KEY=sk-ba31b180effe4134a4c3fc9c4f3a12a3
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-secret-key-here
```

### 3. 配置文件安全
```toml
# config/config.toml (生产环境)
[llm]
model = "qwen-plus"
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
api_key = "${QWEN_API_KEY}"  # 使用环境变量
max_tokens = 8192
temperature = 0.0

[security]
allowed_hosts = ["your-domain.com", "www.your-domain.com"]
cors_origins = ["https://your-domain.com"]
```

## 📊 监控和日志

### 1. 日志配置
```python
# logging_config.py
import logging
from logging.handlers import RotatingFileHandler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('/var/log/jelilian-ai-pro.log', maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)
```

### 2. 健康检查
```python
# health_check.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "JELILIAN AI PRO"}
```

## 🚀 一键部署脚本

### 完整部署脚本
```bash
#!/bin/bash
# deploy.sh - 一键部署脚本

set -e

echo "🚀 开始部署 JELILIAN AI PRO 到阿里云..."

# 1. 更新系统
echo "📦 更新系统包..."
sudo apt update && sudo apt upgrade -y

# 2. 安装依赖
echo "🔧 安装系统依赖..."
sudo apt install -y python3.11 python3.11-venv python3.11-pip nginx git supervisor

# 3. 创建应用目录
echo "📁 创建应用目录..."
sudo mkdir -p /opt/jelilian-ai-pro
sudo chown $USER:$USER /opt/jelilian-ai-pro

# 4. 部署应用
echo "📋 部署应用代码..."
cd /opt/jelilian-ai-pro
# 这里需要替换为实际的代码路径
cp -r /path/to/local/JELILIAN-AI-PRO/* .

# 5. 创建虚拟环境
echo "🐍 创建Python虚拟环境..."
python3.11 -m venv venv
source venv/bin/activate

# 6. 安装Python依赖
echo "📦 安装Python依赖..."
pip install -r requirements.txt
pip install gunicorn

# 7. 配置文件
echo "⚙️ 配置应用..."
cp config/config.example-model-qwen.toml config/config.toml

# 8. 配置Nginx
echo "🌐 配置Nginx..."
sudo cp deploy/nginx.conf /etc/nginx/sites-available/jelilian-ai-pro
sudo ln -sf /etc/nginx/sites-available/jelilian-ai-pro /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 9. 配置Supervisor
echo "👮 配置进程管理..."
sudo cp deploy/supervisor.conf /etc/supervisor/conf.d/jelilian-ai-pro.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start jelilian-ai-pro

# 10. 启动服务
echo "🎯 启动服务..."
sudo systemctl enable nginx
sudo systemctl enable supervisor

echo "✅ 部署完成！"
echo "🌐 访问地址: http://your-server-ip"
echo "📊 查看状态: sudo supervisorctl status jelilian-ai-pro"
echo "📝 查看日志: sudo tail -f /var/log/jelilian-ai-pro.log"
```

## 📱 域名和SSL配置

### 1. 域名解析
在阿里云DNS控制台添加A记录:
- 主机记录: @ 或 www
- 记录值: 您的ECS公网IP

### 2. SSL证书申请
```bash
# 使用Let's Encrypt免费证书
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## 🔄 更新和维护

### 更新脚本
```bash
#!/bin/bash
# update.sh - 应用更新脚本

cd /opt/jelilian-ai-pro
source venv/bin/activate

# 拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt

# 重启服务
sudo supervisorctl restart jelilian-ai-pro

echo "✅ 更新完成！"
```

### 备份脚本
```bash
#!/bin/bash
# backup.sh - 数据备份脚本

BACKUP_DIR="/opt/backups/jelilian-ai-pro"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份配置文件
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /opt/jelilian-ai-pro/config/

# 备份日志
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz /var/log/jelilian-ai-pro.log*

echo "✅ 备份完成: $BACKUP_DIR"
```

## 📞 故障排除

### 常见问题
1. **服务无法启动**
   ```bash
   sudo supervisorctl status jelilian-ai-pro
   sudo tail -f /var/log/jelilian-ai-pro.log
   ```

2. **Nginx配置错误**
   ```bash
   sudo nginx -t
   sudo systemctl status nginx
   ```

3. **端口占用**
   ```bash
   sudo netstat -tlnp | grep :8000
   sudo lsof -i :8000
   ```

4. **权限问题**
   ```bash
   sudo chown -R www-data:www-data /opt/jelilian-ai-pro
   sudo chmod -R 755 /opt/jelilian-ai-pro
   ```

---

**部署完成后，您的JELILIAN AI PRO将在阿里云上稳定运行！** 🎉