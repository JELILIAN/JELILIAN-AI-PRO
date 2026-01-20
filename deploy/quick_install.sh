#!/bin/bash
# JELILIAN AI PRO 一键部署脚本
# 适用于 Ubuntu 20.04/22.04

set -e

echo "=========================================="
echo "  JELILIAN AI PRO 一键部署脚本"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}请使用root用户运行此脚本${NC}"
    exit 1
fi

echo -e "${GREEN}[1/6] 更新系统...${NC}"
apt update && apt upgrade -y

echo -e "${GREEN}[2/6] 安装依赖...${NC}"
apt install -y python3.11 python3.11-venv python3-pip nginx git

echo -e "${GREEN}[3/6] 创建项目目录...${NC}"
mkdir -p /var/www/jelilian
cd /var/www/jelilian

echo -e "${GREEN}[4/6] 设置Python环境...${NC}"
python3.11 -m venv venv
source venv/bin/activate

# 如果当前目录有requirements.txt，安装依赖
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install fastapi uvicorn python-multipart aiohttp toml pydantic
fi

echo -e "${GREEN}[5/6] 配置Nginx...${NC}"
cat > /etc/nginx/sites-available/jelilian << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8003;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 86400;
    }

    location /assets {
        alias /var/www/jelilian/assets;
    }
}
EOF

ln -sf /etc/nginx/sites-available/jelilian /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

echo -e "${GREEN}[6/6] 配置系统服务...${NC}"
cat > /etc/systemd/system/jelilian.service << 'EOF'
[Unit]
Description=JELILIAN AI PRO
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/jelilian
Environment="PATH=/var/www/jelilian/venv/bin"
ExecStart=/var/www/jelilian/venv/bin/python advanced_web.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable jelilian
systemctl start jelilian

echo ""
echo -e "${GREEN}=========================================="
echo "  部署完成！"
echo "==========================================${NC}"
echo ""
echo -e "访问地址: ${YELLOW}http://$(curl -s ifconfig.me)${NC}"
echo ""
echo "常用命令:"
echo "  查看状态: systemctl status jelilian"
echo "  查看日志: journalctl -u jelilian -f"
echo "  重启服务: systemctl restart jelilian"
echo ""
