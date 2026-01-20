# 阿里云部署指南 - JELILIAN AI PRO

## 方式一：阿里云ECS服务器部署（推荐）

### 1. 购买ECS服务器
- 登录阿里云控制台：https://ecs.console.aliyun.com
- 选择地域：香港（推荐，无需备案）
- 配置：2核4G以上，Ubuntu 22.04
- 开放端口：22(SSH), 80(HTTP), 443(HTTPS), 8003

### 2. 连接服务器
```bash
ssh root@你的服务器IP
```

### 3. 安装环境
```bash
# 更新系统
apt update && apt upgrade -y

# 安装Python 3.11
apt install -y python3.11 python3.11-venv python3-pip

# 安装Nginx
apt install -y nginx

# 安装Git
apt install -y git
```

### 4. 部署代码
```bash
# 创建项目目录
mkdir -p /var/www/jelilian
cd /var/www/jelilian

# 上传代码（或使用Git克隆）
# 方式1: 使用scp上传
# scp -r /本地路径/* root@服务器IP:/var/www/jelilian/

# 方式2: Git克隆
# git clone https://github.com/你的仓库/jelilian-ai-pro.git .

# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 5. 配置Nginx
```bash
# 创建Nginx配置
cat > /etc/nginx/sites-available/jelilian << 'EOF'
server {
    listen 80;
    server_name 你的域名或IP;

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

# 启用配置
ln -sf /etc/nginx/sites-available/jelilian /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
```

### 6. 配置Systemd服务（开机自启）
```bash
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

# 启动服务
systemctl daemon-reload
systemctl enable jelilian
systemctl start jelilian

# 查看状态
systemctl status jelilian
```

### 7. 配置SSL证书（可选）
```bash
# 安装Certbot
apt install -y certbot python3-certbot-nginx

# 获取证书（需要域名）
certbot --nginx -d 你的域名
```

### 8. 常用命令
```bash
# 查看日志
journalctl -u jelilian -f

# 重启服务
systemctl restart jelilian

# 停止服务
systemctl stop jelilian
```

---

## 方式二：阿里云函数计算FC部署

### 1. 安装Serverless Devs
```bash
npm install -g @serverless-devs/s
s config add --AccessKeyID xxx --AccessKeySecret xxx --AccountID xxx
```

### 2. 创建s.yaml配置（已创建）
```bash
s deploy
```

---

## 方式三：阿里云容器服务ACK

### 1. 构建Docker镜像
```bash
docker build -t jelilian-ai-pro .
```

### 2. 推送到阿里云镜像仓库
```bash
docker tag jelilian-ai-pro registry.cn-hongkong.aliyuncs.com/你的命名空间/jelilian:latest
docker push registry.cn-hongkong.aliyuncs.com/你的命名空间/jelilian:latest
```

### 3. 在ACK中部署
使用阿里云容器服务控制台创建Deployment

---

## 快速一键部署脚本

在服务器上运行：
```bash
curl -sSL https://raw.githubusercontent.com/你的仓库/jelilian-ai-pro/main/deploy/quick_install.sh | bash
```
