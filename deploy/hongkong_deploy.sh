#!/bin/bash
# JELILIAN AI PRO - 阿里云香港地域部署脚本
# 适用于: 阿里云香港 (cn-hongkong)

set -e

echo "🇭🇰 JELILIAN AI PRO - 阿里云香港部署"
echo "=========================================="

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用root用户运行此脚本"
    echo "   sudo bash hongkong_deploy.sh"
    exit 1
fi

# 系统信息
echo "📋 系统信息检查..."
echo "   操作系统: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "   内核版本: $(uname -r)"
echo "   架构: $(uname -m)"

# 检查网络连接
echo "🌐 网络连接检查..."
if ping -c 1 google.com &> /dev/null; then
    echo "   ✅ 国际网络连接正常"
    USE_INTERNATIONAL_MIRRORS=true
else
    echo "   ⚠️  国际网络连接异常，使用国内镜像"
    USE_INTERNATIONAL_MIRRORS=false
fi

# 更新系统包管理器
echo "📦 更新系统包..."
if command -v apt-get &> /dev/null; then
    # Ubuntu/Debian
    if [ "$USE_INTERNATIONAL_MIRRORS" = true ]; then
        apt-get update -y
    else
        # 使用阿里云镜像
        cp /etc/apt/sources.list /etc/apt/sources.list.backup
        cat > /etc/apt/sources.list << 'EOF'
deb http://mirrors.aliyun.com/ubuntu/ focal main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ focal-security main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ focal-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ focal-backports main restricted universe multiverse
EOF
        apt-get update -y
    fi
    apt-get install -y curl wget git unzip python3 python3-pip nginx supervisor
elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    yum update -y
    yum install -y curl wget git unzip python3 python3-pip nginx supervisor
else
    echo "❌ 不支持的操作系统"
    exit 1
fi

# 安装Python依赖
echo "🐍 安装Python环境..."
if [ "$USE_INTERNATIONAL_MIRRORS" = false ]; then
    # 使用阿里云PyPI镜像
    pip3 config set global.index-url https://mirrors.aliyun.com/pypi/simple/
    pip3 config set install.trusted-host mirrors.aliyun.com
fi

pip3 install --upgrade pip
pip3 install fastapi uvicorn python-multipart jinja2 requests qrcode[pil] Pillow

# 创建应用目录
APP_DIR="/opt/jelilian-ai-pro"
echo "📁 创建应用目录: $APP_DIR"
mkdir -p $APP_DIR
cd $APP_DIR

# 下载项目文件（如果不存在）
if [ ! -f "advanced_web.py" ]; then
    echo "📥 项目文件不存在，请手动上传项目文件到 $APP_DIR"
    echo "   您可以使用以下方法之一："
    echo "   1. scp -r JELILIAN-AI-PRO/* root@your-server-ip:$APP_DIR/"
    echo "   2. 使用FTP工具上传"
    echo "   3. 使用git clone（如果有代码仓库）"
    echo ""
    echo "⏸️  部署暂停，等待文件上传..."
    read -p "文件上传完成后按回车继续..."
fi

# 设置文件权限
echo "🔐 设置文件权限..."
chown -R root:root $APP_DIR
chmod +x $APP_DIR/*.py
chmod +x $APP_DIR/deploy/*.sh

# 创建日志目录
mkdir -p $APP_DIR/logs
mkdir -p /var/log/jelilian

# 配置Nginx（香港地域优化）
echo "🌐 配置Nginx..."
cat > /etc/nginx/sites-available/jelilian << 'EOF'
server {
    listen 80;
    server_name _;
    
    # 香港地域优化配置
    client_max_body_size 10M;
    client_body_timeout 60s;
    client_header_timeout 60s;
    keepalive_timeout 65s;
    
    # Gzip压缩（减少带宽使用）
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # 静态文件缓存
    location /assets/ {
        alias /opt/jelilian-ai-pro/assets/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # API请求
    location / {
        proxy_pass http://127.0.0.1:8003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 流式响应支持
        proxy_buffering off;
        proxy_cache off;
        
        # 超时设置（香港网络优化）
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 300s;
    }
    
    # 健康检查
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# 启用站点
ln -sf /etc/nginx/sites-available/jelilian /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试Nginx配置
nginx -t
if [ $? -ne 0 ]; then
    echo "❌ Nginx配置错误"
    exit 1
fi

# 配置Supervisor
echo "⚙️ 配置Supervisor..."
cat > /etc/supervisor/conf.d/jelilian.conf << EOF
[program:jelilian-ai-pro]
command=python3 $APP_DIR/advanced_web.py
directory=$APP_DIR
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/jelilian/app.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=5
environment=PYTHONPATH="$APP_DIR"

[program:jelilian-worker]
command=python3 $APP_DIR/advanced_web.py
directory=$APP_DIR
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/jelilian/worker.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=5
environment=PYTHONPATH="$APP_DIR"
numprocs=2
process_name=%(program_name)s_%(process_num)02d
EOF

# 创建系统服务
echo "🔧 创建系统服务..."
cat > /etc/systemd/system/jelilian.service << EOF
[Unit]
Description=JELILIAN AI PRO Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR
Environment=PYTHONPATH=$APP_DIR
ExecStart=/usr/bin/python3 $APP_DIR/advanced_web.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
echo "🚀 启动服务..."
systemctl daemon-reload
systemctl enable jelilian
systemctl start jelilian

# 启动Nginx
systemctl enable nginx
systemctl restart nginx

# 启动Supervisor
systemctl enable supervisor
systemctl restart supervisor
supervisorctl reread
supervisorctl update

# 配置防火墙
echo "🔥 配置防火墙..."
if command -v ufw &> /dev/null; then
    ufw --force enable
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
elif command -v firewall-cmd &> /dev/null; then
    systemctl enable firewalld
    systemctl start firewalld
    firewall-cmd --permanent --add-service=ssh
    firewall-cmd --permanent --add-service=http
    firewall-cmd --permanent --add-service=https
    firewall-cmd --reload
fi

# 创建SSL证书目录（为后续HTTPS准备）
mkdir -p /etc/ssl/jelilian

# 创建监控脚本
echo "📊 创建监控脚本..."
cat > $APP_DIR/monitor.sh << 'EOF'
#!/bin/bash
# JELILIAN AI PRO 监控脚本

LOG_FILE="/var/log/jelilian/monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# 检查应用状态
if curl -s http://localhost:8003/health > /dev/null; then
    echo "[$DATE] ✅ 应用运行正常" >> $LOG_FILE
else
    echo "[$DATE] ❌ 应用异常，尝试重启" >> $LOG_FILE
    systemctl restart jelilian
    supervisorctl restart jelilian-ai-pro
fi

# 检查磁盘空间
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "[$DATE] ⚠️ 磁盘使用率过高: ${DISK_USAGE}%" >> $LOG_FILE
fi

# 检查内存使用
MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $MEM_USAGE -gt 80 ]; then
    echo "[$DATE] ⚠️ 内存使用率过高: ${MEM_USAGE}%" >> $LOG_FILE
fi
EOF

chmod +x $APP_DIR/monitor.sh

# 添加定时任务
echo "⏰ 添加定时监控..."
(crontab -l 2>/dev/null; echo "*/5 * * * * $APP_DIR/monitor.sh") | crontab -

# 显示部署结果
echo ""
echo "🎉 部署完成！"
echo "=========================================="
echo "📍 地域: 阿里云香港 (cn-hongkong)"
echo "🌐 访问地址: http://$(curl -s ifconfig.me)"
echo "📁 应用目录: $APP_DIR"
echo "📋 日志目录: /var/log/jelilian/"
echo ""
echo "🔧 服务管理命令:"
echo "   systemctl status jelilian    # 查看服务状态"
echo "   systemctl restart jelilian   # 重启服务"
echo "   supervisorctl status          # 查看进程状态"
echo "   nginx -t                      # 测试Nginx配置"
echo ""
echo "📊 监控命令:"
echo "   tail -f /var/log/jelilian/app.log     # 查看应用日志"
echo "   tail -f /var/log/jelilian/monitor.log # 查看监控日志"
echo "   $APP_DIR/monitor.sh                   # 手动运行监控"
echo ""
echo "🔒 安全建议:"
echo "   1. 配置SSL证书启用HTTPS"
echo "   2. 设置强密码和SSH密钥认证"
echo "   3. 定期更新系统和依赖包"
echo "   4. 配置备份策略"
echo ""

# 检查服务状态
echo "🔍 服务状态检查:"
echo "   Nginx: $(systemctl is-active nginx)"
echo "   JELILIAN: $(systemctl is-active jelilian)"
echo "   Supervisor: $(systemctl is-active supervisor)"

# 最终测试
echo ""
echo "🧪 最终测试..."
sleep 5
if curl -s http://localhost/health > /dev/null; then
    echo "✅ 部署成功！应用正在运行"
    echo "🌐 请访问: http://$(curl -s ifconfig.me)"
else
    echo "❌ 部署可能有问题，请检查日志:"
    echo "   tail -f /var/log/jelilian/app.log"
fi

echo ""
echo "🎯 下一步:"
echo "   1. 配置域名解析"
echo "   2. 申请SSL证书"
echo "   3. 配置CDN加速"
echo "   4. 设置监控告警"