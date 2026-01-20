# 🚀 JELILIAN AI PRO - 快速部署命令

## 📋 部署前准备

### 1. 本地准备
```bash
# 创建部署包
python JELILIAN-AI-PRO/create_deploy_package.py

# 检查部署包
ls -la jelilian-hongkong-deploy.tar.gz
```

### 2. 服务器信息
- **服务器IP**: `your-server-ip`
- **用户**: `root`
- **地域**: 阿里云香港 (cn-hongkong)
- **端口**: 22 (SSH), 80 (HTTP), 443 (HTTPS)

## 🔄 一键部署命令

### 方法1: 完整一键部署
```bash
# 1. 上传部署包
scp jelilian-hongkong-deploy.tar.gz root@your-server-ip:/tmp/

# 2. 连接服务器并部署
ssh root@your-server-ip << 'EOF'
cd /opt
tar -xzf /tmp/jelilian-hongkong-deploy.tar.gz
mv jelilian-deploy jelilian-ai-pro
cd jelilian-ai-pro
chmod +x deploy/*.sh
./deploy/hongkong_deploy.sh
EOF
```

### 方法2: 分步执行
```bash
# 1. 上传文件
scp jelilian-hongkong-deploy.tar.gz root@your-server-ip:/tmp/

# 2. 连接服务器
ssh root@your-server-ip

# 3. 在服务器上执行
cd /opt
tar -xzf /tmp/jelilian-hongkong-deploy.tar.gz
mv jelilian-deploy jelilian-ai-pro
cd jelilian-ai-pro
chmod +x deploy/*.sh
./deploy/hongkong_deploy.sh
```

## 🔍 部署验证命令

```bash
# 检查服务状态
systemctl status jelilian nginx

# 检查端口监听
netstat -tulpn | grep -E ':80|:8003'

# 测试访问
curl http://localhost/health
curl http://your-server-ip/health

# 查看日志
tail -f /var/log/jelilian/app.log
```

## 🌐 域名和SSL配置

```bash
# 配置SSL证书 (需要域名)
./deploy/hongkong_ssl_setup.sh your-domain.com your-email@example.com

# 验证SSL
curl https://your-domain.com/health
```

## 🔧 常用管理命令

### 服务管理
```bash
# 启动服务
systemctl start jelilian nginx

# 停止服务
systemctl stop jelilian nginx

# 重启服务
systemctl restart jelilian nginx

# 查看状态
systemctl status jelilian nginx
```

### 日志查看
```bash
# 应用日志
tail -f /var/log/jelilian/app.log

# Nginx日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# 系统日志
journalctl -u jelilian -f
```

### 进程管理
```bash
# Supervisor管理
supervisorctl status
supervisorctl restart jelilian-ai-pro
supervisorctl stop jelilian-ai-pro
supervisorctl start jelilian-ai-pro
```

## 🚨 故障排除命令

### 端口占用问题
```bash
# 查看端口占用
netstat -tulpn | grep :8003
lsof -i :8003

# 杀死占用进程
kill -9 $(lsof -t -i:8003)
```

### 权限问题
```bash
# 设置文件权限
chown -R root:root /opt/jelilian-ai-pro
chmod +x /opt/jelilian-ai-pro/*.py
chmod +x /opt/jelilian-ai-pro/deploy/*.sh
```

### 依赖问题
```bash
# 重新安装依赖
cd /opt/jelilian-ai-pro
pip3 install -r requirements.txt --force-reinstall
```

### Nginx配置问题
```bash
# 测试Nginx配置
nginx -t

# 重新加载配置
systemctl reload nginx

# 重新生成配置
cp deploy/nginx.conf /etc/nginx/sites-available/jelilian
systemctl reload nginx
```

## 📊 监控命令

### 系统资源
```bash
# CPU和内存
htop
free -h
df -h

# 网络连接
netstat -an | grep :8003
ss -tulpn | grep :8003
```

### 应用监控
```bash
# 运行监控脚本
/opt/jelilian-ai-pro/monitor.sh

# 查看监控日志
tail -f /var/log/jelilian/monitor.log
```

## 💾 备份命令

```bash
# 手动备份
/opt/jelilian-ai-pro/deploy/hongkong_backup.sh

# 查看备份文件
ls -la /opt/backups/jelilian/

# 设置自动备份
crontab -e
# 添加: 0 2 * * * /opt/jelilian-ai-pro/deploy/hongkong_backup.sh
```

## 🔄 更新命令

### 系统更新
```bash
# Ubuntu/Debian
apt update && apt upgrade -y

# CentOS/RHEL
yum update -y
```

### 应用更新
```bash
cd /opt/jelilian-ai-pro

# 备份当前版本
cp -r . ../jelilian-ai-pro-backup-$(date +%Y%m%d)

# 上传新版本文件
# 重启服务
systemctl restart jelilian
```

## 🧪 测试命令

### 功能测试
```bash
# 健康检查
curl http://localhost/health

# API测试
curl -X POST http://localhost/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"123456","confirm_password":"123456"}'
```

### 性能测试
```bash
# 安装ab工具
apt install apache2-utils

# 并发测试
ab -n 100 -c 10 http://localhost/

# 压力测试
ab -n 1000 -c 50 http://localhost/
```

## 📞 获取帮助

如果遇到问题，请联系技术支持：
- **微信**: 18501935068
- **邮箱**: 18501935068@163.com
- **WhatsApp**: +8618501935068

或查看详细文档：
- `deploy/HONGKONG_DEPLOY_GUIDE.md`
- `HONGKONG_DEPLOYMENT_COMPLETE.md`