#!/bin/bash
# JELILIAN AI PRO 阿里云一键部署脚本
# 使用方法: chmod +x deploy.sh && ./deploy.sh

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
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

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "请不要使用root用户运行此脚本"
        exit 1
    fi
}

# 检查操作系统
check_os() {
    if [[ ! -f /etc/os-release ]]; then
        log_error "无法检测操作系统版本"
        exit 1
    fi
    
    . /etc/os-release
    if [[ "$ID" != "ubuntu" ]] && [[ "$ID" != "debian" ]]; then
        log_warning "此脚本主要针对Ubuntu/Debian系统，其他系统可能需要手动调整"
    fi
}

# 更新系统
update_system() {
    log_info "更新系统包..."
    sudo apt update
    sudo apt upgrade -y
    log_success "系统更新完成"
}

# 安装系统依赖
install_dependencies() {
    log_info "安装系统依赖..."
    
    # 安装基础包
    sudo apt install -y \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release \
        git \
        wget \
        unzip \
        supervisor \
        nginx
    
    # 安装Python 3.11
    if ! command -v python3.11 &> /dev/null; then
        log_info "安装Python 3.11..."
        sudo add-apt-repository ppa:deadsnakes/ppa -y
        sudo apt update
        sudo apt install -y python3.11 python3.11-venv python3.11-pip python3.11-dev
    fi
    
    log_success "系统依赖安装完成"
}

# 创建应用目录
create_app_directory() {
    log_info "创建应用目录..."
    
    sudo mkdir -p /opt/jelilian-ai-pro
    sudo chown $USER:$USER /opt/jelilian-ai-pro
    sudo mkdir -p /var/log/jelilian-ai-pro
    sudo chown $USER:$USER /var/log/jelilian-ai-pro
    
    log_success "应用目录创建完成"
}

# 部署应用代码
deploy_application() {
    log_info "部署应用代码..."
    
    cd /opt/jelilian-ai-pro
    
    # 如果是从本地部署，复制文件
    if [[ -d "/tmp/JELILIAN-AI-PRO" ]]; then
        cp -r /tmp/JELILIAN-AI-PRO/* .
    else
        log_warning "请先将JELILIAN-AI-PRO代码复制到 /tmp/JELILIAN-AI-PRO/"
        log_info "或者修改此脚本以从Git仓库克隆代码"
        exit 1
    fi
    
    log_success "应用代码部署完成"
}

# 创建Python虚拟环境
create_virtual_environment() {
    log_info "创建Python虚拟环境..."
    
    cd /opt/jelilian-ai-pro
    python3.11 -m venv venv
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装依赖
    pip install -r requirements.txt
    pip install gunicorn
    
    log_success "Python虚拟环境创建完成"
}

# 配置应用
configure_application() {
    log_info "配置应用..."
    
    cd /opt/jelilian-ai-pro
    
    # 复制配置文件
    if [[ ! -f config/config.toml ]]; then
        cp config/config.example-model-qwen.toml config/config.toml
        log_warning "请编辑 config/config.toml 文件，设置您的API密钥"
    fi
    
    # 创建环境变量文件
    cat > .env << EOF
ENVIRONMENT=production
DEBUG=false
QWEN_API_KEY=sk-ba31b180effe4134a4c3fc9c4f3a12a3
SECRET_KEY=$(openssl rand -hex 32)
EOF
    
    log_success "应用配置完成"
}

# 配置Nginx
configure_nginx() {
    log_info "配置Nginx..."
    
    # 复制Nginx配置
    sudo cp /opt/jelilian-ai-pro/deploy/nginx.conf /etc/nginx/sites-available/jelilian-ai-pro
    
    # 创建软链接
    sudo ln -sf /etc/nginx/sites-available/jelilian-ai-pro /etc/nginx/sites-enabled/
    
    # 删除默认配置
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # 测试Nginx配置
    sudo nginx -t
    
    log_success "Nginx配置完成"
}

# 配置Supervisor
configure_supervisor() {
    log_info "配置Supervisor..."
    
    # 复制Supervisor配置
    sudo cp /opt/jelilian-ai-pro/deploy/supervisor.conf /etc/supervisor/conf.d/jelilian-ai-pro.conf
    
    # 重新加载Supervisor配置
    sudo supervisorctl reread
    sudo supervisorctl update
    
    log_success "Supervisor配置完成"
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙..."
    
    # 安装UFW
    sudo apt install -y ufw
    
    # 配置防火墙规则
    sudo ufw --force reset
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow ssh
    sudo ufw allow 'Nginx Full'
    sudo ufw --force enable
    
    log_success "防火墙配置完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 启动并启用服务
    sudo systemctl enable nginx
    sudo systemctl enable supervisor
    
    # 重启服务
    sudo systemctl restart nginx
    sudo systemctl restart supervisor
    
    # 启动应用
    sudo supervisorctl start jelilian-ai-pro
    
    log_success "服务启动完成"
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    
    # 检查Nginx状态
    if sudo systemctl is-active --quiet nginx; then
        log_success "Nginx 运行正常"
    else
        log_error "Nginx 未运行"
    fi
    
    # 检查Supervisor状态
    if sudo systemctl is-active --quiet supervisor; then
        log_success "Supervisor 运行正常"
    else
        log_error "Supervisor 未运行"
    fi
    
    # 检查应用状态
    if sudo supervisorctl status jelilian-ai-pro | grep -q RUNNING; then
        log_success "JELILIAN AI PRO 运行正常"
    else
        log_error "JELILIAN AI PRO 未运行"
        sudo supervisorctl status jelilian-ai-pro
    fi
}

# 显示部署信息
show_deployment_info() {
    echo ""
    echo "=========================================="
    echo "🎉 JELILIAN AI PRO 部署完成！"
    echo "=========================================="
    echo ""
    echo "📍 服务器信息:"
    echo "   - 应用目录: /opt/jelilian-ai-pro"
    echo "   - 配置文件: /opt/jelilian-ai-pro/config/config.toml"
    echo "   - 日志文件: /var/log/jelilian-ai-pro.log"
    echo ""
    echo "🌐 访问信息:"
    echo "   - HTTP: http://$(curl -s ifconfig.me)"
    echo "   - 本地: http://localhost"
    echo ""
    echo "🔧 管理命令:"
    echo "   - 查看状态: sudo supervisorctl status jelilian-ai-pro"
    echo "   - 重启应用: sudo supervisorctl restart jelilian-ai-pro"
    echo "   - 查看日志: sudo tail -f /var/log/jelilian-ai-pro.log"
    echo "   - 重启Nginx: sudo systemctl restart nginx"
    echo ""
    echo "📝 下一步:"
    echo "   1. 配置域名解析指向服务器IP"
    echo "   2. 申请SSL证书: sudo certbot --nginx"
    echo "   3. 编辑配置文件设置您的API密钥"
    echo ""
    echo "🆘 如有问题，请查看日志文件或联系技术支持"
    echo "=========================================="
}

# 主函数
main() {
    echo "🚀 开始部署 JELILIAN AI PRO 到阿里云..."
    echo ""
    
    check_root
    check_os
    update_system
    install_dependencies
    create_app_directory
    deploy_application
    create_virtual_environment
    configure_application
    configure_nginx
    configure_supervisor
    configure_firewall
    start_services
    check_services
    show_deployment_info
    
    log_success "部署完成！"
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查日志"; exit 1' ERR

# 运行主函数
main "$@"