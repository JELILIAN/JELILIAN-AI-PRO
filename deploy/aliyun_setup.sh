#!/bin/bash
# JELILIAN AI PRO 阿里云一键部署脚本
# 使用方法: curl -sSL https://你的地址/aliyun_setup.sh | bash

set -e

echo "=========================================="
echo "  JELILIAN AI PRO 阿里云部署"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}请使用 root 用户运行此脚本${NC}"
    exit 1
fi

echo -e "${GREEN}[1/7] 更新系统...${NC}"
apt update && apt upgrade -y

echo -e "${GREEN}[2/7] 安装依赖...${NC}"
apt install -y python3.11 python3.11-venv python3-pip nginx git curl

echo -e "${GREEN}[3/7] 创建项目目录...${NC}"
mkdir -p /var/www/jelilian
cd /var/www/jelilian

echo -e "${GREEN}[4/7] 设置Python环境...${NC}"
python3.11 -m venv venv
source venv/bin/activate

echo -e "${YELLOW}请上传项目文件到 /var/www/jelilian 目录${NC}"
echo -e "${YELLOW}或使用: scp -r 本地路径/* root@服务器IP:/var/www/jelilian/${NC}"
echo ""
read -p "文件上传完成后按 Enter 继续..."

# 安装依赖
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo -e "${RED}未找到 requirements.txt${NC}"
    exit 1
fi

echo -e "${GREEN}[5/7] 配置Nginx...${NC}"
cat > /etc/nginx/sites-available/jelilian << 'EOF'
server {
    listen 80;
    server_name _;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8003;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
        proxy_send_timeout 86400;
    }

    location /assets {
        alias /var/www/jelilian/assets;
        expires 30d;
    }
}
EOF

ln -sf /etc/nginx/sites-available/jelilian /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

echo -e "${GREEN}[6/7] 配置系统服务...${NC}"
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

echo -e "${GREEN}[7/7] 检查服务状态...${NC}"
sleep 3
systemctl status jelilian --no-pager

echo ""
echo "=========================================="
echo -e "${GREEN}✅ 部署完成！${NC}"
echo "=========================================="
echo ""
echo "访问地址: http://$(curl -s ifconfig.me)"
echo ""
echo "常用命令:"
echo "  查看状态: systemctl status jelilian"
echo "  重启服务: systemctl restart jelilian"
echo "  查看日志: journalctl -u jelilian -f"
echo ""
