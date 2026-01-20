# JELILIAN AI PRO - 阿里云香港部署指南

## 🇭🇰 香港地域特点

阿里云香港地域具有以下特点：
- **地理位置**: 连接大陆和海外的桥梁
- **网络环境**: 国际网络访问良好，延迟较低
- **监管环境**: 无需ICP备案，适合国际业务
- **成本**: 相对大陆地域略高，但性价比良好

## 🚀 快速部署

### 1. 准备工作

#### 服务器要求
- **配置**: 2核4GB内存以上
- **系统**: Ubuntu 20.04 LTS 或 CentOS 8
- **带宽**: 5Mbps以上
- **存储**: 40GB以上SSD

#### 网络配置
- 开放端口：22 (SSH), 80 (HTTP), 443 (HTTPS)
- 配置安全组规则
- 确保服务器可以访问国际网络

### 2. 一键部署

```bash
# 1. 连接到服务器
ssh root@your-server-ip

# 2. 下载部署脚本
wget https://raw.githubusercontent.com/your-repo/JELILIAN-AI-PRO/main/deploy/hongkong_deploy.sh

# 3. 上传项目文件到服务器
scp -r JELILIAN-AI-PRO/* root@your-server-ip:/opt/jelilian-ai-pro/

# 4. 运行部署脚本
chmod +x hongkong_deploy.sh
./hongkong_deploy.sh
```

### 3. SSL证书配置

```bash
# 配置HTTPS（需要域名）
./hongkong_ssl_setup.sh your-domain.com your-email@example.com
```

## 📁 项目文件上传

### 方法1: SCP上传（推荐）

```bash
# 从本地上传整个项目
scp -r JELILIAN-AI-PRO/* root@your-server-ip:/opt/jelilian-ai-pro/

# 或者打包上传
tar -czf jelilian.tar.gz JELILIAN-AI-PRO/
scp jelilian.tar.gz root@your-server-ip:/tmp/
ssh root@your-server-ip "cd /opt && tar -xzf /tmp/jelilian.tar.gz && mv JELILIAN-AI-PRO jelilian-ai-pro"
```

### 方法2: Git克隆

```bash
ssh root@your-server-ip
cd /opt
git clone https://github.com/your-repo/JELILIAN-AI-PRO.git jelilian-ai-pro
```

### 方法3: FTP工具

使用FileZilla、WinSCP等工具上传文件到 `/opt/jelilian-ai-pro/`

## 🔧 部署步骤详解

### 1. 系统环境准备

```bash
# 更新系统
apt update && apt upgrade -y

# 安装基础软件
apt install -y curl wget git unzip python3 python3-pip nginx supervisor

# 安装Python依赖
pip3 install fastapi uvicorn python-multipart jinja2 requests qrcode[pil] Pillow
```

### 2. 应用配置

```bash
# 创建应用目录
mkdir -p /opt/jelilian-ai-pro
cd /opt/jelilian-ai-pro

# 设置权限
chown -R root:root /opt/jelilian-ai-pro
chmod +x *.py
```

### 3. Nginx配置

```bash
# 配置Nginx
cp deploy/nginx.conf /etc/nginx/sites-available/jelilian
ln -sf /etc/nginx/sites-available/jelilian /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试配置
nginx -t

# 重启Nginx
systemctl restart nginx
```

### 4. 服务配置

```bash
# 配置Supervisor
cp deploy/supervisor.conf /etc/supervisor/conf.d/jelilian.conf

# 配置系统服务
cp deploy/jelilian.service /etc/systemd/system/

# 启动服务
systemctl daemon-reload
systemctl enable jelilian
systemctl start jelilian
```

## 🌐 域名配置

### 1. DNS解析

在域名服务商处添加A记录：
```
类型: A
主机记录: @ 或 www
记录值: 你的服务器IP
TTL: 600
```

### 2. SSL证书

```bash
# 自动配置SSL
./deploy/hongkong_ssl_setup.sh your-domain.com admin@your-domain.com
```

## 📊 监控和维护

### 1. 服务状态检查

```bash
# 检查服务状态
systemctl status jelilian
systemctl status nginx
supervisorctl status

# 查看日志
tail -f /var/log/jelilian/app.log
tail -f /var/log/nginx/access.log
```

### 2. 性能监控

```bash
# 系统资源
htop
df -h
free -h

# 网络连接
netstat -tulpn | grep :8003
```

### 3. 自动备份

```bash
# 设置自动备份
chmod +x deploy/hongkong_backup.sh
crontab -e

# 添加定时任务（每天凌晨2点备份）
0 2 * * * /opt/jelilian-ai-pro/deploy/hongkong_backup.sh
```

## 🔒 安全配置

### 1. 防火墙设置

```bash
# Ubuntu UFW
ufw enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp

# CentOS Firewalld
systemctl enable firewalld
firewall-cmd --permanent --add-service=ssh
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload
```

### 2. SSH安全

```bash
# 修改SSH配置
vim /etc/ssh/sshd_config

# 建议配置
Port 22
PermitRootLogin yes
PasswordAuthentication yes
PubkeyAuthentication yes

# 重启SSH
systemctl restart sshd
```

### 3. 定期更新

```bash
# 系统更新
apt update && apt upgrade -y

# Python包更新
pip3 install --upgrade fastapi uvicorn
```

## 🚨 故障排除

### 1. 常见问题

#### 服务无法启动
```bash
# 检查日志
journalctl -u jelilian -f
tail -f /var/log/jelilian/app.log

# 检查端口占用
netstat -tulpn | grep :8003
```

#### Nginx配置错误
```bash
# 测试配置
nginx -t

# 查看错误日志
tail -f /var/log/nginx/error.log
```

#### SSL证书问题
```bash
# 检查证书状态
certbot certificates

# 手动续期
certbot renew --dry-run
```

### 2. 性能优化

#### 数据库优化
```bash
# 如果使用数据库，优化配置
# 根据实际情况调整
```

#### 缓存配置
```bash
# 配置Redis缓存（可选）
apt install redis-server
systemctl enable redis-server
```

## 📈 扩展配置

### 1. CDN加速

推荐使用阿里云CDN或Cloudflare：
- 配置源站为服务器IP
- 开启HTTPS
- 设置缓存规则

### 2. 负载均衡

如需高可用，可配置：
- 阿里云SLB
- 多台服务器部署
- 数据库主从复制

### 3. 监控告警

集成监控系统：
- 阿里云云监控
- Prometheus + Grafana
- 钉钉/企业微信告警

## 📞 技术支持

如遇到部署问题，请联系：
- 微信: 18501935068
- 邮箱: 18501935068@163.com
- WhatsApp: +8618501935068

## 🎯 部署检查清单

- [ ] 服务器配置满足要求
- [ ] 项目文件上传完整
- [ ] Python依赖安装成功
- [ ] Nginx配置正确
- [ ] 服务启动正常
- [ ] 域名解析生效
- [ ] SSL证书配置
- [ ] 防火墙规则设置
- [ ] 监控脚本部署
- [ ] 备份策略配置

完成以上检查后，您的JELILIAN AI PRO就可以在阿里云香港稳定运行了！