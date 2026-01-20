#!/bin/bash
# JELILIAN AI PRO 快速部署脚本 - 适用于阿里云ECS
# 使用方法: wget -O - https://your-domain.com/quick_deploy.sh | bash

set -e

echo "🚀 JELILIAN AI PRO 快速部署到阿里云"
echo "=================================="

# 检查系统
if [[ "$EUID" -eq 0 ]]; then
    echo "❌ 请不要使用root用户运行"
    exit 1
fi

# 获取用户输入
read -p "请输入您的域名 (例: example.com): " DOMAIN
read -p "请输入您的邮箱 (用于SSL证书): " EMAIL

if [[ -z "$DOMAIN" ]]; then
    echo "❌ 域名不能为空"
    exit 1
fi

if [[ -z "$EMAIL" ]]; then
    EMAIL="admin@$DOMAIN"
fi

echo "📋 配置信息:"
echo "   域名: $DOMAIN"
echo "   邮箱: $EMAIL"
echo ""

# 更新系统
echo "📦 更新系统..."
sudo apt update && sudo apt upgrade -y

# 安装依赖
echo "🔧 安装依赖..."
sudo apt install -y python3.11 python3.11-venv python3.11-pip nginx git supervisor curl

# 创建应用目录
echo "📁 创建应用目录..."
sudo mkdir -p /opt/jelilian-ai-pro
sudo chown $USER:$USER /opt/jelilian-ai-pro

# 下载应用代码 (这里需要替换为实际的下载地址)
echo "📥 下载应用代码..."
cd /opt/jelilian-ai-pro
# git clone https://github.com/your-repo/JELILIAN-AI-PRO.git .
echo "⚠️  请手动上传JELILIAN-AI-PRO代码到此目录"
echo "   或修改此脚本添加Git仓库地址"

# 创建虚拟环境
echo "🐍 创建虚拟环境..."
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# 安装Python依赖 (基础版本)
echo "📦 安装Python依赖..."
pip install fastapi uvicorn gunicorn openai pydantic loguru tenacity

# 创建基本配置
echo "⚙️ 创建配置文件..."
mkdir -p config
cat > config/config.toml << EOF
[llm]
model = "qwen-plus"
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
api_key = "sk-ba31b180effe4134a4c3fc9c4f3a12a3"
max_tokens = 8192
temperature = 0.0

[security]
allowed_hosts = ["$DOMAIN", "www.$DOMAIN"]
EOF

# 创建简化的Web启动器
echo "🌐 创建Web启动器..."
cat > simple_web.py << 'EOF'
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI(title="JELILIAN AI PRO")

HTML = """
<!DOCTYPE html>
<html><head><title>JELILIAN AI PRO</title></head>
<body style="font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px;">
<h1>🤖 JELILIAN AI PRO</h1>
<form method="post" action="/chat">
<textarea name="prompt" style="width: 100%; height: 100px;" placeholder="请输入您的问题..."></textarea><br><br>
<button type="submit" style="padding: 10px 20px;">发送</button>
</form>
{response}
</body></html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML.format(response="")

@app.post("/chat", response_class=HTMLResponse)
async def chat(prompt: str = Form(...)):
    try:
        # 这里应该调用AI API
        response = f"<div style='margin-top: 20px; padding: 15px; background: #f0f0f0;'><strong>AI回复:</strong><br>{prompt}</div>"
        return HTML.format(response=response)
    except Exception as e:
        return HTML.format(response=f"<div style='color: red;'>错误: {str(e)}</div>")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
EOF

# 配置Nginx
echo "🌐 配置Nginx..."
sudo tee /etc/nginx/sites-available/jelilian-ai-pro > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/jelilian-ai-pro /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# 配置Supervisor
echo "👮 配置进程管理..."
sudo tee /etc/supervisor/conf.d/jelilian-ai-pro.conf > /dev/null << EOF
[program:jelilian-ai-pro]
command=/opt/jelilian-ai-pro/venv/bin/python simple_web.py
directory=/opt/jelilian-ai-pro
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/jelilian-ai-pro.log
EOF

sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start jelilian-ai-pro

# 配置SSL (Let's Encrypt)
echo "🔒 配置SSL证书..."
sudo apt install -y snapd
sudo snap install --classic certbot
sudo ln -sf /snap/bin/certbot /usr/bin/certbot

sudo systemctl stop nginx
sudo certbot certonly --standalone --non-interactive --agree-tos --email "$EMAIL" -d "$DOMAIN" -d "www.$DOMAIN"

# 更新Nginx配置支持HTTPS
sudo tee /etc/nginx/sites-available/jelilian-ai-pro > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;
    
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo systemctl start nginx
sudo nginx -t && sudo systemctl reload nginx

# 设置自动续期
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet && /usr/bin/systemctl reload nginx") | crontab -

# 启动服务
echo "🎯 启动服务..."
sudo systemctl enable nginx supervisor
sudo supervisorctl restart jelilian-ai-pro

echo ""
echo "✅ 部署完成！"
echo "=================================="
echo "🌐 访问地址: https://$DOMAIN"
echo "📊 管理命令:"
echo "   sudo supervisorctl status jelilian-ai-pro"
echo "   sudo tail -f /var/log/jelilian-ai-pro.log"
echo ""
echo "📝 下一步:"
echo "1. 上传完整的JELILIAN-AI-PRO代码"
echo "2. 安装完整依赖: pip install -r requirements.txt"
echo "3. 更新配置文件中的API密钥"
echo "4. 重启服务: sudo supervisorctl restart jelilian-ai-pro"
echo "=================================="