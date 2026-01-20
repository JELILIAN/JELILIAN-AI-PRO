#!/bin/bash
# JELILIAN AI PRO - 香港地域数据备份脚本

set -e

echo "💾 JELILIAN AI PRO - 数据备份 (香港地域)"
echo "========================================"

# 配置
APP_DIR="/opt/jelilian-ai-pro"
BACKUP_DIR="/opt/backups/jelilian"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="jelilian_backup_$DATE"
RETENTION_DAYS=30

# 创建备份目录
mkdir -p $BACKUP_DIR

echo "📋 备份配置:"
echo "   应用目录: $APP_DIR"
echo "   备份目录: $BACKUP_DIR"
echo "   备份名称: $BACKUP_NAME"
echo "   保留天数: $RETENTION_DAYS"

# 创建备份
echo "📦 创建备份..."
cd $BACKUP_DIR

# 备份应用文件
echo "   📁 备份应用文件..."
tar -czf "${BACKUP_NAME}_app.tar.gz" -C $APP_DIR \
    --exclude="logs/*" \
    --exclude="__pycache__/*" \
    --exclude="*.pyc" \
    --exclude=".git/*" \
    .

# 备份数据文件
echo "   📊 备份数据文件..."
if [ -d "$APP_DIR" ]; then
    tar -czf "${BACKUP_NAME}_data.tar.gz" -C $APP_DIR \
        users.json \
        user_credits.json \
        trial_records.json \
        sessions.json \
        2>/dev/null || echo "   ⚠️  部分数据文件不存在"
fi

# 备份日志文件
echo "   📋 备份日志文件..."
if [ -d "/var/log/jelilian" ]; then
    tar -czf "${BACKUP_NAME}_logs.tar.gz" -C /var/log jelilian/
fi

# 备份配置文件
echo "   ⚙️  备份配置文件..."
tar -czf "${BACKUP_NAME}_config.tar.gz" \
    /etc/nginx/sites-available/jelilian \
    /etc/supervisor/conf.d/jelilian.conf \
    /etc/systemd/system/jelilian.service \
    2>/dev/null || echo "   ⚠️  部分配置文件不存在"

# 备份SSL证书（如果存在）
echo "   🔒 备份SSL证书..."
if [ -d "/etc/letsencrypt" ]; then
    tar -czf "${BACKUP_NAME}_ssl.tar.gz" -C /etc letsencrypt/
fi

# 创建备份清单
echo "   📝 创建备份清单..."
cat > "${BACKUP_NAME}_manifest.txt" << EOF
JELILIAN AI PRO 备份清单
========================
备份时间: $(date)
服务器IP: $(curl -s ifconfig.me 2>/dev/null || echo "未知")
地域: 阿里云香港 (cn-hongkong)

备份文件:
- ${BACKUP_NAME}_app.tar.gz     (应用文件)
- ${BACKUP_NAME}_data.tar.gz    (数据文件)
- ${BACKUP_NAME}_logs.tar.gz    (日志文件)
- ${BACKUP_NAME}_config.tar.gz  (配置文件)
- ${BACKUP_NAME}_ssl.tar.gz     (SSL证书)

系统信息:
- 操作系统: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)
- 内核版本: $(uname -r)
- Python版本: $(python3 --version)
- Nginx版本: $(nginx -v 2>&1)

服务状态:
- JELILIAN: $(systemctl is-active jelilian 2>/dev/null || echo "未知")
- Nginx: $(systemctl is-active nginx 2>/dev/null || echo "未知")
- Supervisor: $(systemctl is-active supervisor 2>/dev/null || echo "未知")

磁盘使用:
$(df -h)

内存使用:
$(free -h)
EOF

# 计算备份大小
BACKUP_SIZE=$(du -sh ${BACKUP_NAME}_*.tar.gz ${BACKUP_NAME}_manifest.txt 2>/dev/null | awk '{sum+=$1} END {print sum}' || echo "未知")
echo "   📏 备份大小: $BACKUP_SIZE"

# 压缩所有备份文件
echo "🗜️  压缩备份文件..."
tar -czf "${BACKUP_NAME}_complete.tar.gz" ${BACKUP_NAME}_*
rm -f ${BACKUP_NAME}_app.tar.gz ${BACKUP_NAME}_data.tar.gz ${BACKUP_NAME}_logs.tar.gz ${BACKUP_NAME}_config.tar.gz ${BACKUP_NAME}_ssl.tar.gz ${BACKUP_NAME}_manifest.txt

# 清理旧备份
echo "🧹 清理旧备份..."
find $BACKUP_DIR -name "jelilian_backup_*_complete.tar.gz" -mtime +$RETENTION_DAYS -delete
DELETED_COUNT=$(find $BACKUP_DIR -name "jelilian_backup_*_complete.tar.gz" -mtime +$RETENTION_DAYS 2>/dev/null | wc -l)
echo "   🗑️  删除了 $DELETED_COUNT 个过期备份"

# 上传到云存储（可选）
if command -v ossutil &> /dev/null; then
    echo "☁️  上传到阿里云OSS..."
    # 需要配置OSS
    # ossutil cp "${BACKUP_NAME}_complete.tar.gz" oss://your-bucket/backups/
    echo "   ⚠️  请配置OSS上传"
elif command -v aws &> /dev/null; then
    echo "☁️  上传到AWS S3..."
    # aws s3 cp "${BACKUP_NAME}_complete.tar.gz" s3://your-bucket/backups/
    echo "   ⚠️  请配置S3上传"
fi

# 发送通知（可选）
if command -v curl &> /dev/null; then
    # 可以集成钉钉、企业微信等通知
    echo "📱 发送备份通知..."
    # curl -X POST "webhook_url" -d "备份完成: $BACKUP_NAME"
    echo "   ⚠️  请配置通知webhook"
fi

# 显示备份结果
echo ""
echo "✅ 备份完成！"
echo "========================"
echo "📦 备份文件: $BACKUP_DIR/${BACKUP_NAME}_complete.tar.gz"
echo "📏 文件大小: $(du -sh $BACKUP_DIR/${BACKUP_NAME}_complete.tar.gz | cut -f1)"
echo "📅 备份时间: $(date)"

# 列出所有备份
echo ""
echo "📋 所有备份文件:"
ls -lh $BACKUP_DIR/jelilian_backup_*_complete.tar.gz 2>/dev/null || echo "   无备份文件"

echo ""
echo "🔧 恢复命令:"
echo "   cd $BACKUP_DIR"
echo "   tar -xzf ${BACKUP_NAME}_complete.tar.gz"
echo "   # 然后根据需要恢复各个组件"

echo ""
echo "⏰ 自动备份:"
echo "   添加到crontab: 0 2 * * * $0"
echo "   每天凌晨2点自动备份"