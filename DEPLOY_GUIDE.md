# JELILIAN AI PRO 部署指南

## 🚀 本地启动

### Windows
双击 `start.bat` 或运行：
```bash
python start_server.py
```

### Linux/Mac
```bash
python start_server.py
```

访问: http://localhost:8003

---

## ☁️ 阿里云ECS部署（推荐）

### 1. 购买服务器
- 地域：香港（无需备案）
- 配置：2核4G+
- 系统：Ubuntu 22.04
- 开放端口：22, 80, 443, 8003

### 2. 部署命令
```bash
# 连接服务器
ssh root@你的IP

# 安装环境
apt update && apt install -y python3.11 python3.11-venv nginx git

# 部署代码
mkdir -p /var/www/jelilian && cd /var/www/jelilian
# 上传代码或 git clone

# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 配置Nginx
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
    }
}
EOF

ln -sf /etc/nginx/sites-available/jelilian /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# 配置开机自启
cat > /etc/systemd/system/jelilian.service << 'EOF'
[Unit]
Description=JELILIAN AI PRO
After=network.target

[Service]
Type=simple
WorkingDirectory=/var/www/jelilian
Environment="PATH=/var/www/jelilian/venv/bin"
ExecStart=/var/www/jelilian/venv/bin/python advanced_web.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable jelilian
systemctl start jelilian
```

### 3. 常用命令
```bash
systemctl status jelilian   # 查看状态
systemctl restart jelilian  # 重启
journalctl -u jelilian -f   # 查看日志
```

---

## 🌐 Vercel部署（Serverless）

### 1. 创建 vercel.json
```json
{
  "builds": [{"src": "advanced_web.py", "use": "@vercel/python"}],
  "routes": [{"src": "/(.*)", "dest": "advanced_web.py"}]
}
```

### 2. 部署
```bash
npm i -g vercel
vercel
```

注意：Vercel免费版有限制，建议用于演示

---

## 🐳 Docker部署

```bash
# 构建镜像
docker build -t jelilian-ai-pro .

# 运行容器
docker run -d -p 8003:8003 --name jelilian jelilian-ai-pro
```

---

## 📋 环境变量配置

编辑 `config/config.toml`:
```toml
[llm]
model = "qwen-plus"
api_key = "你的API密钥"
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
```

---

## 🌍 多语言支持

系统支持7种语言：
- 中文 (zh)
- English (en)
- 日本語 (ja)
- 한국어 (ko)
- Español (es)
- Français (fr)
- Deutsch (de)

用户可在页面右上角切换语言。
