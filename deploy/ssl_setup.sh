#!/bin/bash
# JELILIAN AI PRO SSL证书配置脚本
# 支持Let's Encrypt免费证书和阿里云SSL证书

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查域名参数
if [ $# -eq 0 ]; then
    log_error "请提供域名参数"
    echo "使用方法: $0 <domain> [email]"
    echo "示例: $0 example.com admin@example.com"
    exit 1
fi

DOMAIN=$1
EMAIL=${2:-"admin@$DOMAIN"}

log_info "配置SSL证书 for $DOMAIN"

# 检查域名解析
check_dns() {
    log_info "检查域名解析..."
    
    # 获取服务器公网IP
    SERVER_IP=$(curl -s ifconfig.me)
    
    # 检查域名解析
    DOMAIN_IP=$(dig +short $DOMAIN)
    
    if [ "$DOMAIN_IP" != "$SERVER_IP" ]; then
        log_warning "域名解析可能有问题:"
        log_warning "  域名IP: $DOMAIN_IP"
        log_warning "  服务器IP: $SERVER_IP"
        log_warning "请确保域名已正确解析到服务器IP"
        
        read -p "是否继续? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        log_success "域名解析正确"
    fi
}

# 安装Certbot
install_certbot() {
    log_info "安装Certbot..."
    
    # 更新包列表
    sudo apt update
    
    # 安装snapd (如果未安装)
    if ! command -v snap &> /dev/null; then
        sudo apt install -y snapd
        sudo systemctl enable --now snapd.socket
        sudo ln -sf /var/lib/snapd/snap /snap
    fi
    
    # 安装certbot
    sudo snap install --classic certbot
    sudo ln -sf /snap/bin/certbot /usr/bin/certbot
    
    log_success "Certbot安装完成"
}

# 申请Let's Encrypt证书
setup_letsencrypt() {
    log_info "申请Let's Encrypt SSL证书..."
    
    # 停止nginx以释放80端口
    sudo systemctl stop nginx
    
    # 申请证书
    sudo certbot certonly \
        --standalone \
        --non-interactive \
        --agree-tos \
        --email "$EMAIL" \
        -d "$DOMAIN" \
        -d "www.$DOMAIN"
    
    if [ $? -eq 0 ]; then
        log_success "SSL证书申请成功"
        
        # 更新Nginx配置
        update_nginx_ssl_config
        
        # 启动nginx
        sudo systemctl start nginx
        
        # 设置自动续期
        setup_auto_renewal
        
    else
        log_error "SSL证书申请失败"
        sudo systemctl start nginx
        exit 1
    fi
}

# 更新Nginx SSL配置
update_nginx_ssl_config() {
    log_info "更新Nginx SSL配置..."
    
    # 备份原配置
    sudo cp /etc/nginx/sites-available/jelilian-ai-pro /etc/nginx/sites-available/jelilian-ai-pro.backup
    
    # 更新SSL证书路径
    sudo sed -i "s|your-domain.com|$DOMAIN|g" /etc/nginx/sites-available/jelilian-ai-pro
    sudo sed -i "s|/etc/ssl/certs/jelilian-ai-pro.crt|/etc/letsencrypt/live/$DOMAIN/fullchain.pem|g" /etc/nginx/sites-available/jelilian-ai-pro
    sudo sed -i "s|/etc/ssl/private/jelilian-ai-pro.key|/etc/letsencrypt/live/$DOMAIN/privkey.pem|g" /etc/nginx/sites-available/jelilian-ai-pro
    
    # 测试配置
    sudo nginx -t
    
    if [ $? -eq 0 ]; then
        log_success "Nginx SSL配置更新成功"
        sudo systemctl reload nginx
    else
        log_error "Nginx配置有误，恢复备份"
        sudo cp /etc/nginx/sites-available/jelilian-ai-pro.backup /etc/nginx/sites-available/jelilian-ai-pro
        exit 1
    fi
}

# 设置自动续期
setup_auto_renewal() {
    log_info "设置SSL证书自动续期..."
    
    # 创建续期脚本
    cat > /tmp/renew-ssl.sh << 'EOF'
#!/bin/bash
# SSL证书自动续期脚本

/usr/bin/certbot renew --quiet --no-self-upgrade

# 如果证书更新了，重新加载nginx
if [ $? -eq 0 ]; then
    /usr/bin/systemctl reload nginx
fi
EOF
    
    sudo mv /tmp/renew-ssl.sh /usr/local/bin/renew-ssl.sh
    sudo chmod +x /usr/local/bin/renew-ssl.sh
    
    # 添加到crontab
    (crontab -l 2>/dev/null; echo "0 12 * * * /usr/local/bin/renew-ssl.sh") | crontab -
    
    log_success "SSL证书自动续期设置完成"
}

# 配置阿里云SSL证书
setup_aliyun_ssl() {
    log_info "配置阿里云SSL证书..."
    log_warning "请确保您已经从阿里云下载了SSL证书文件"
    
    read -p "请输入证书文件路径 (.crt): " CERT_PATH
    read -p "请输入私钥文件路径 (.key): " KEY_PATH
    
    if [ ! -f "$CERT_PATH" ] || [ ! -f "$KEY_PATH" ]; then
        log_error "证书文件不存在"
        exit 1
    fi
    
    # 创建SSL目录
    sudo mkdir -p /etc/ssl/certs /etc/ssl/private
    
    # 复制证书文件
    sudo cp "$CERT_PATH" /etc/ssl/certs/jelilian-ai-pro.crt
    sudo cp "$KEY_PATH" /etc/ssl/private/jelilian-ai-pro.key
    
    # 设置权限
    sudo chmod 644 /etc/ssl/certs/jelilian-ai-pro.crt
    sudo chmod 600 /etc/ssl/private/jelilian-ai-pro.key
    
    # 更新Nginx配置
    sudo sed -i "s|your-domain.com|$DOMAIN|g" /etc/nginx/sites-available/jelilian-ai-pro
    
    # 测试配置
    sudo nginx -t
    
    if [ $? -eq 0 ]; then
        log_success "阿里云SSL证书配置成功"
        sudo systemctl reload nginx
    else
        log_error "Nginx配置有误"
        exit 1
    fi
}

# 测试SSL配置
test_ssl() {
    log_info "测试SSL配置..."
    
    # 等待nginx重新加载
    sleep 2
    
    # 测试HTTPS连接
    if curl -s -I "https://$DOMAIN" | grep -q "200 OK"; then
        log_success "HTTPS连接测试成功"
    else
        log_warning "HTTPS连接测试失败，请检查配置"
    fi
    
    # 测试SSL证书
    if openssl s_client -connect "$DOMAIN:443" -servername "$DOMAIN" </dev/null 2>/dev/null | grep -q "Verify return code: 0"; then
        log_success "SSL证书验证成功"
    else
        log_warning "SSL证书验证失败"
    fi
}

# 显示SSL信息
show_ssl_info() {
    echo ""
    echo "=========================================="
    echo "🔒 SSL证书配置完成！"
    echo "=========================================="
    echo ""
    echo "🌐 HTTPS访问地址:"
    echo "   - https://$DOMAIN"
    echo "   - https://www.$DOMAIN"
    echo ""
    echo "📋 证书信息:"
    echo "   - 域名: $DOMAIN"
    echo "   - 邮箱: $EMAIL"
    echo "   - 证书路径: /etc/letsencrypt/live/$DOMAIN/"
    echo ""
    echo "🔧 管理命令:"
    echo "   - 查看证书: sudo certbot certificates"
    echo "   - 手动续期: sudo certbot renew"
    echo "   - 测试续期: sudo certbot renew --dry-run"
    echo ""
    echo "📝 注意事项:"
    echo "   - 证书有效期90天，已设置自动续期"
    echo "   - 自动续期时间: 每天12:00"
    echo "   - 如有问题请检查nginx日志"
    echo ""
    echo "🔍 SSL测试工具:"
    echo "   - https://www.ssllabs.com/ssltest/"
    echo "   - https://myssl.com/"
    echo "=========================================="
}

# 主菜单
main_menu() {
    echo "🔒 JELILIAN AI PRO SSL证书配置"
    echo "================================"
    echo "1. Let's Encrypt 免费证书 (推荐)"
    echo "2. 阿里云SSL证书"
    echo "3. 仅测试当前SSL配置"
    echo "4. 退出"
    echo ""
    read -p "请选择配置方式 (1-4): " choice
    
    case $choice in
        1)
            check_dns
            install_certbot
            setup_letsencrypt
            test_ssl
            show_ssl_info
            ;;
        2)
            setup_aliyun_ssl
            test_ssl
            show_ssl_info
            ;;
        3)
            test_ssl
            ;;
        4)
            log_info "退出SSL配置"
            exit 0
            ;;
        *)
            log_error "无效选择"
            main_menu
            ;;
    esac
}

# 检查是否为root用户
if [[ $EUID -eq 0 ]]; then
    log_error "请不要使用root用户运行此脚本"
    exit 1
fi

# 检查nginx是否安装
if ! command -v nginx &> /dev/null; then
    log_error "Nginx未安装，请先运行部署脚本"
    exit 1
fi

# 运行主菜单
main_menu