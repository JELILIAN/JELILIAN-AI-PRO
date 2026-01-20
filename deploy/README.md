# JELILIAN AI PRO 阿里云部署文档

## 📋 部署概览

本目录包含了将JELILIAN AI PRO部署到阿里云ECS服务器的完整解决方案，包括自动化脚本、配置文件和详细文档。

## 🗂️ 文件结构

```
deploy/
├── README.md                    # 本文档
├── aliyun_deploy.md            # 详细部署指南
├── deploy.sh                   # 一键部署脚本
├── nginx.conf                  # Nginx配置文件
├── supervisor.conf             # Supervisor进程管理配置
├── gunicorn_config.py          # Gunicorn生产环境配置
├── production_web_launcher.py  # 生产环境Web启动器
└── ssl_setup.sh               # SSL证书配置脚本
```

## 🚀 快速部署

### 方法1: 一键部署 (推荐)

1. **准备服务器**
   - 阿里云ECS (Ubuntu 20.04 LTS)
   - 2核4G内存，20GB存储
   - 开放80、443、22端口

2. **上传代码**
   ```bash
   # 将JELILIAN-AI-PRO代码上传到服务器
   scp -r JELILIAN-AI-PRO/ user@your-server-ip:/tmp/
   ```

3. **运行部署脚本**
   ```bash
   ssh user@your-server-ip
   cd /tmp/JELILIAN-AI-PRO/deploy
   chmod +x deploy.sh
   ./deploy.sh
   ```

### 方法2: 手动部署

详细步骤请参考 [aliyun_deploy.md](./aliyun_deploy.md)

## 🔧 配置说明

### 1. 服务器要求
- **操作系统**: Ubuntu 20.04 LTS / CentOS 8
- **CPU**: 最低2核，推荐4核
- **内存**: 最低2GB，推荐4GB+
- **存储**: 最低20GB SSD
- **网络**: 公网IP，域名解析

### 2. 端口配置
- **80**: HTTP (重定向到HTTPS)
- **443**: HTTPS
- **22**: SSH管理
- **8000**: 应用端口 (内部)

### 3. 安全组设置
在阿里云控制台配置安全组规则:
```
入方向:
- SSH(22)    0.0.0.0/0
- HTTP(80)   0.0.0.0/0  
- HTTPS(443) 0.0.0.0/0

出方向:
- 全部端口  0.0.0.0/0
```

## 🌐 域名和SSL配置

### 1. 域名解析
在阿里云DNS控制台添加记录:
- **类型**: A
- **主机记录**: @ 和 www
- **记录值**: ECS公网IP
- **TTL**: 600

### 2. SSL证书配置
```bash
# 运行SSL配置脚本
cd /opt/jelilian-ai-pro/deploy
chmod +x ssl_setup.sh
./ssl_setup.sh your-domain.com your-email@domain.com
```

## 📊 服务管理

### 常用命令
```bash
# 查看应用状态
sudo supervisorctl status jelilian-ai-pro

# 重启应用
sudo supervisorctl restart jelilian-ai-pro

# 查看日志
sudo tail -f /var/log/jelilian-ai-pro.log

# 重启Nginx
sudo systemctl restart nginx

# 查看Nginx状态
sudo systemctl status nginx
```

### 配置文件位置
- **应用配置**: `/opt/jelilian-ai-pro/config/config.toml`
- **Nginx配置**: `/etc/nginx/sites-available/jelilian-ai-pro`
- **Supervisor配置**: `/etc/supervisor/conf.d/jelilian-ai-pro.conf`
- **日志文件**: `/var/log/jelilian-ai-pro.log`

## 🔄 更新和维护

### 应用更新
```bash
cd /opt/jelilian-ai-pro
git pull origin main  # 或上传新代码
source venv/bin/activate
pip install -r requirements.txt
sudo supervisorctl restart jelilian-ai-pro
```

### 系统维护
```bash
# 系统更新
sudo apt update && sudo apt upgrade -y

# 清理日志
sudo logrotate -f /etc/logrotate.conf

# 磁盘清理
sudo apt autoremove -y
sudo apt autoclean
```

## 📈 性能优化

### 1. Nginx优化
- 启用Gzip压缩
- 设置缓存策略
- 优化worker进程数

### 2. Gunicorn优化
- 根据CPU核心数调整worker数量
- 使用内存文件系统
- 启用预加载应用

### 3. 系统优化
```bash
# 调整文件描述符限制
echo "* soft nofile 65535" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65535" | sudo tee -a /etc/security/limits.conf

# 优化内核参数
echo "net.core.somaxconn = 65535" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

## 🔍 监控和日志

### 1. 日志管理
```bash
# 查看实时日志
sudo tail -f /var/log/jelilian-ai-pro.log

# 查看Nginx访问日志
sudo tail -f /var/log/nginx/jelilian-ai-pro.access.log

# 查看Nginx错误日志
sudo tail -f /var/log/nginx/jelilian-ai-pro.error.log
```

### 2. 系统监控
```bash
# 查看系统资源
htop

# 查看磁盘使用
df -h

# 查看内存使用
free -h

# 查看网络连接
netstat -tlnp
```

## 🆘 故障排除

### 常见问题

1. **应用无法启动**
   ```bash
   # 检查配置文件
   cd /opt/jelilian-ai-pro
   python -c "from app.config import Config; Config()"
   
   # 检查依赖
   source venv/bin/activate
   pip check
   ```

2. **Nginx 502错误**
   ```bash
   # 检查应用是否运行
   sudo supervisorctl status jelilian-ai-pro
   
   # 检查端口占用
   sudo netstat -tlnp | grep :8000
   ```

3. **SSL证书问题**
   ```bash
   # 检查证书状态
   sudo certbot certificates
   
   # 测试证书续期
   sudo certbot renew --dry-run
   ```

4. **性能问题**
   ```bash
   # 查看系统负载
   uptime
   
   # 查看进程资源使用
   ps aux | grep gunicorn
   ```

### 日志分析
```bash
# 分析访问日志
sudo awk '{print $1}' /var/log/nginx/jelilian-ai-pro.access.log | sort | uniq -c | sort -nr | head -10

# 分析错误日志
sudo grep "ERROR" /var/log/jelilian-ai-pro.log | tail -20
```

## 📞 技术支持

### 联系方式
- 技术文档: 查看项目README
- 问题反馈: 提交GitHub Issue
- 紧急支持: 查看日志文件排查

### 备份策略
```bash
# 创建备份脚本
cat > /opt/backup-jelilian.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/jelilian-$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/app.tar.gz /opt/jelilian-ai-pro
tar -czf $BACKUP_DIR/nginx.tar.gz /etc/nginx/sites-available/jelilian-ai-pro
tar -czf $BACKUP_DIR/logs.tar.gz /var/log/jelilian-ai-pro.log*
EOF

chmod +x /opt/backup-jelilian.sh
```

---

**部署完成后，您的JELILIAN AI PRO将在阿里云上稳定运行！** 🎉

如有问题，请参考详细文档或联系技术支持。