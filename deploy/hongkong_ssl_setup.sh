#!/bin/bash
# JELILIAN AI PRO - 香港地域SSL证书配置脚本

set -e

echo "🔒 JELILIAN AI PRO - SSL证书配置 (香港地域)"
echo "============================================="

# 检查参数
if [ $# -lt 1 ]; then
    echo "❌ 使用方法: $0 <域名> [邮箱]"
    echo "   示例: $0 jelilian.example.com admin@example.com"
    exit 1
fi

DOMAIN=$1
EMAIL=${2:-"admin@$DOMAIN"}

echo "📋 配置信息:"
echo "   域名: $DOMAIN"
echo "   邮箱: $EMAIL"

# 检查域名解析
echo "🌐 检查域名解析..."
if ! nslookup $DOMAIN > /dev/null 2>&1; then
    echo "❌ 域名解析失败，请先配置DNS解析"
    echo "   请将域名 $DOMAIN 解析到服务器IP: $(curl -s ifconfig.me)"
    exit 1
fi

RESOLVED_IP=$(nslookup $DOMAIN | grep -A1 "Name:" | tail -1 | awk '{print $2}')
SERVER_IP=$(curl -s ifconfig.me)

if [ "$RESOLVED_IP" != "$SERVER_IP" ]; then
    echo "⚠️  域名解析IP ($RESOLVED_IP) 与服务器IP ($SERVER_IP) 不匹配"
    echo "   请确认DNS解析是否正确"
    read -p "是否继续？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 安装Certbot
echo "📦 安装Certbot..."
if command -v apt-get &> /dev/null; then
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
elif command -v yum &> /dev/null; then
    yum install -y epel-release
    yum install -y certbot python3-certbot-nginx
else
    echo "❌ 不支持的操作系统"
    exit 1
fi

# 更新Nginx配置以支持SSL
echo "🌐 更新Nginx配置..."
cat > /etc/nginx/sites-available/jelilian << EOF
# HTTP重定向到HTTPS
server {
    listen 80;
    server_name $DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

# HTTPS配置
server {
    listen 443 ssl http2;
    server_name $DOMAIN;
    
    # SSL证书配置（Certbot会自动填充）
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # SSL安全配置（香港地域优化）
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS安全头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # 香港地域网络优化
    client_max_body_size 10M;
    client_body_timeout 60s;
    client_header_timeout 60s;
    keepalive_timeout 65s;
    
    # Gzip压缩
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
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # 流式响应支持
        proxy_buffering off;
        proxy_cache off;
        
        # 超时设置
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

# 测试Nginx配置
nginx -t
if [ $? -ne 0 ]; then
    echo "❌ Nginx配置错误"
    exit 1
fi

# 重启Nginx
systemctl reload nginx

# 申请SSL证书
echo "🔒 申请SSL证书..."
certbot --nginx -d $DOMAIN --email $EMAIL --agree-tos --non-interactive --redirect

if [ $? -eq 0 ]; then
    echo "✅ SSL证书申请成功！"
else
    echo "❌ SSL证书申请失败"
    echo "   可能的原因："
    echo "   1. 域名解析未生效"
    echo "   2. 防火墙阻止了80/443端口"
    echo "   3. 服务器无法访问Let's Encrypt服务器"
    exit 1
fi

# 设置自动续期
echo "⏰ 设置SSL证书自动续期..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

# 创建SSL监控脚本
cat > /opt/jelilian-ai-pro/ssl_monitor.sh << 'EOF'
#!/bin/bash
# SSL证书监控脚本

DOMAIN=$1
LOG_FILE="/var/log/jelilian/ssl_monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

if [ -z "$DOMAIN" ]; then
    echo "使用方法: $0 <域名>"
    exit 1
fi

# 检查证书有效期
EXPIRY_DATE=$(echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -dates | grep notAfter | cut -d= -f2)
EXPIRY_TIMESTAMP=$(date -d "$EXPIRY_DATE" +%s)
CURRENT_TIMESTAMP=$(date +%s)
DAYS_LEFT=$(( ($EXPIRY_TIMESTAMP - $CURRENT_TIMESTAMP) / 86400 ))

echo "[$DATE] SSL证书还有 $DAYS_LEFT 天过期" >> $LOG_FILE

if [ $DAYS_LEFT -lt 30 ]; then
    echo "[$DATE] ⚠️ SSL证书即将过期，还有 $DAYS_LEFT 天" >> $LOG_FILE
    # 这里可以添加邮件通知或其他告警
fi

if [ $DAYS_LEFT -lt 7 ]; then
    echo "[$DATE] 🚨 SSL证书即将过期，尝试续期" >> $LOG_FILE
    certbot renew --quiet
fi
EOF

chmod +x /opt/jelilian-ai-pro/ssl_monitor.sh

# 添加SSL监控到定时任务
(crontab -l 2>/dev/null; echo "0 6 * * * /opt/jelilian-ai-pro/ssl_monitor.sh $DOMAIN") | crontab -

# 测试HTTPS访问
echo "🧪 测试HTTPS访问..."
sleep 5
if curl -s https://$DOMAIN/health > /dev/null; then
    echo "✅ HTTPS配置成功！"
else
    echo "❌ HTTPS访问失败，请检查配置"
fi

# 显示配置结果
echo ""
echo "🎉 SSL配置完成！"
echo "================================"
echo "🌐 HTTPS地址: https://$DOMAIN"
echo "🔒 证书路径: /etc/letsencrypt/live/$DOMAIN/"
echo "📋 证书信息:"
openssl x509 -in /etc/letsencrypt/live/$DOMAIN/cert.pem -text -noout | grep -A2 "Validity"

echo ""
echo "🔧 管理命令:"
echo "   certbot certificates              # 查看证书列表"
echo "   certbot renew --dry-run          # 测试续期"
echo "   certbot renew                    # 手动续期"
echo "   /opt/jelilian-ai-pro/ssl_monitor.sh $DOMAIN  # 检查证书状态"

echo ""
echo "📊 监控:"
echo "   tail -f /var/log/jelilian/ssl_monitor.log  # 查看SSL监控日志"

echo ""
echo "🎯 安全评级测试:"
echo "   访问 https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
echo "   检查SSL配置安全性"