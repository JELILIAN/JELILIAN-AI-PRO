#!/usr/bin/env python3
"""
JELILIAN AI PRO 部署脚本
用于部署到香港阿里云服务器
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """运行命令并处理错误"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} 完成")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败: {e}")
        print(f"错误输出: {e.stderr}")
        return None

def check_requirements():
    """检查部署要求"""
    print("🔍 检查部署要求...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or python_version.minor < 11:
        print(f"❌ Python版本过低: {python_version.major}.{python_version.minor}")
        print("需要Python 3.11或更高版本")
        return False
    
    print(f"✅ Python版本: {python_version.major}.{python_version.minor}")
    
    # 检查必要文件
    required_files = [
        "main.py",
        "requirements.txt",
        "config/config.toml",
        "app/agent/jelilian.py"
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ 缺少必要文件: {file}")
            return False
    
    print("✅ 所有必要文件存在")
    return True

def install_dependencies():
    """安装依赖"""
    print("📦 安装依赖...")
    
    # 升级pip
    run_command("python -m pip install --upgrade pip", "升级pip")
    
    # 安装依赖
    result = run_command("pip install -r requirements.txt", "安装Python依赖")
    if result is None:
        return False
    
    # 安装playwright浏览器
    result = run_command("python -m playwright install", "安装Playwright浏览器")
    if result is None:
        return False
    
    return True

def create_systemd_service():
    """创建systemd服务文件"""
    print("🔧 创建systemd服务...")
    
    current_dir = Path.cwd()
    python_path = sys.executable
    
    service_content = f"""[Unit]
Description=JELILIAN AI PRO Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={current_dir}
Environment=PATH={os.environ.get('PATH')}
ExecStart={python_path} main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    service_file = "/etc/systemd/system/jelilian-ai-pro.service"
    
    try:
        with open(service_file, 'w') as f:
            f.write(service_content)
        print(f"✅ 服务文件已创建: {service_file}")
        
        # 重新加载systemd
        run_command("systemctl daemon-reload", "重新加载systemd")
        run_command("systemctl enable jelilian-ai-pro", "启用服务")
        
        return True
    except PermissionError:
        print("❌ 需要root权限创建systemd服务")
        return False

def create_nginx_config():
    """创建Nginx配置（如果需要Web界面）"""
    print("🌐 创建Nginx配置...")
    
    nginx_config = """server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""
    
    config_file = "/etc/nginx/sites-available/jelilian-ai-pro"
    
    try:
        with open(config_file, 'w') as f:
            f.write(nginx_config)
        
        # 创建软链接
        run_command(f"ln -sf {config_file} /etc/nginx/sites-enabled/", "启用Nginx站点")
        run_command("nginx -t", "测试Nginx配置")
        
        print(f"✅ Nginx配置已创建: {config_file}")
        print("⚠️  请记得修改域名并重启Nginx: systemctl restart nginx")
        
        return True
    except PermissionError:
        print("❌ 需要root权限创建Nginx配置")
        return False

def create_docker_files():
    """创建Docker部署文件"""
    print("🐳 创建Docker部署文件...")
    
    # Dockerfile
    dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \\
    wget \\
    gnupg \\
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装Playwright浏览器
RUN python -m playwright install --with-deps

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "main.py"]
"""
    
    # docker-compose.yml
    compose_content = """version: '3.8'

services:
  jelilian-ai-pro:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./config:/app/config
      - ./workspace:/app/workspace
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl  # SSL证书目录
    depends_on:
      - jelilian-ai-pro
    restart: unless-stopped
"""
    
    # 写入文件
    with open("Dockerfile", 'w') as f:
        f.write(dockerfile_content)
    
    with open("docker-compose.yml", 'w') as f:
        f.write(compose_content)
    
    print("✅ Docker文件已创建")
    print("📝 使用 'docker-compose up -d' 启动服务")
    
    return True

def create_deployment_guide():
    """创建部署指南"""
    print("📖 创建部署指南...")
    
    guide_content = """# JELILIAN AI PRO 部署指南

## 阿里云香港服务器部署

### 1. 服务器要求
- Ubuntu 20.04+ 或 CentOS 8+
- 至少 2GB RAM
- 至少 20GB 存储空间
- Python 3.11+

### 2. 快速部署
```bash
# 1. 克隆项目
git clone <your-repo-url>
cd JELILIAN-AI-PRO

# 2. 运行部署脚本
python deploy.py

# 3. 配置API密钥
# 编辑 config/config.toml 文件，添加你的API密钥
```

### 3. 使用Docker部署
```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 4. 使用systemd管理
```bash
# 启动服务
systemctl start jelilian-ai-pro

# 停止服务
systemctl stop jelilian-ai-pro

# 查看状态
systemctl status jelilian-ai-pro

# 查看日志
journalctl -u jelilian-ai-pro -f
```

### 5. 配置说明
- 主配置文件: `config/config.toml`
- 日志文件: 通过systemd或Docker查看
- 工作目录: `workspace/`

### 6. 安全建议
- 使用防火墙限制访问端口
- 定期更新系统和依赖
- 使用HTTPS（配置SSL证书）
- 设置强密码和密钥

### 7. 监控和维护
- 定期检查日志
- 监控系统资源使用
- 备份配置文件
- 更新AI模型和依赖

### 8. 故障排除
- 检查日志: `journalctl -u jelilian-ai-pro`
- 检查端口: `netstat -tlnp | grep 8000`
- 检查进程: `ps aux | grep python`
- 重启服务: `systemctl restart jelilian-ai-pro`
"""
    
    with open("DEPLOYMENT.md", 'w') as f:
        f.write(guide_content)
    
    print("✅ 部署指南已创建: DEPLOYMENT.md")
    return True

def main():
    """主部署函数"""
    print("🚀 JELILIAN AI PRO 部署脚本")
    print("=" * 50)
    
    # 检查要求
    if not check_requirements():
        print("❌ 部署要求检查失败")
        sys.exit(1)
    
    # 安装依赖
    if not install_dependencies():
        print("❌ 依赖安装失败")
        sys.exit(1)
    
    # 创建部署文件
    create_docker_files()
    create_deployment_guide()
    
    # 询问是否创建系统服务
    if input("是否创建systemd服务? (y/N): ").lower() == 'y':
        create_systemd_service()
    
    # 询问是否创建Nginx配置
    if input("是否创建Nginx配置? (y/N): ").lower() == 'y':
        create_nginx_config()
    
    print("\n🎉 部署准备完成!")
    print("📝 请查看 DEPLOYMENT.md 获取详细部署说明")
    print("⚠️  记得在 config/config.toml 中配置你的API密钥")

if __name__ == "__main__":
    main()