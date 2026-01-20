#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JELILIAN AI PRO - 分步骤部署助手
"""

import os
import sys
import subprocess
import time
from pathlib import Path

class DeploymentAssistant:
    def __init__(self):
        self.steps = [
            "准备服务器信息",
            "上传部署包",
            "连接服务器",
            "解压和准备",
            "运行部署脚本",
            "验证部署",
            "配置域名和SSL",
            "最终测试"
        ]
        self.current_step = 0
        
    def print_header(self):
        print("🇭🇰 JELILIAN AI PRO - 阿里云香港部署助手")
        print("=" * 60)
        print("📋 部署步骤:")
        for i, step in enumerate(self.steps, 1):
            status = "✅" if i <= self.current_step else "⏳" if i == self.current_step + 1 else "⏸️"
            print(f"   {status} {i}. {step}")
        print("=" * 60)
        
    def wait_for_user(self, message="按回车继续..."):
        input(f"\n💡 {message}")
        
    def step_1_server_info(self):
        self.current_step = 1
        self.print_header()
        
        print("\n📋 步骤1: 准备服务器信息")
        print("-" * 30)
        
        print("请确保您有以下信息:")
        print("✅ 阿里云香港ECS服务器IP地址")
        print("✅ 服务器root用户密码或SSH密钥")
        print("✅ 服务器已开放端口: 22, 80, 443")
        print("✅ 服务器配置: 2核4GB内存以上")
        
        print("\n🔍 如何获取服务器信息:")
        print("1. 登录阿里云控制台: https://ecs.console.aliyun.com")
        print("2. 选择香港地域")
        print("3. 查看ECS实例列表")
        print("4. 记录公网IP地址")
        
        server_ip = input("\n📝 请输入您的服务器IP地址: ").strip()
        if not server_ip:
            print("❌ 服务器IP不能为空")
            return False
            
        print(f"✅ 服务器IP: {server_ip}")
        
        # 测试连接
        print(f"\n🔍 测试服务器连接...")
        result = os.system(f"ping -c 1 {server_ip} > /dev/null 2>&1")
        if result == 0:
            print("✅ 服务器网络连接正常")
        else:
            print("⚠️  服务器网络连接异常，请检查IP地址")
            
        self.server_ip = server_ip
        return True
        
    def step_2_upload_package(self):
        self.current_step = 2
        self.print_header()
        
        print("\n📦 步骤2: 上传部署包")
        print("-" * 30)
        
        package_file = "jelilian-hongkong-deploy.tar.gz"
        package_path = Path(package_file)
        
        if not package_path.exists():
            print(f"❌ 部署包不存在: {package_file}")
            print("请先运行: python create_deploy_package.py")
            return False
            
        print(f"✅ 找到部署包: {package_file}")
        print(f"📏 文件大小: {package_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        print(f"\n🚀 上传方法选择:")
        print("1. SCP命令上传 (推荐)")
        print("2. FTP工具上传 (FileZilla, WinSCP等)")
        print("3. 手动上传")
        
        choice = input("请选择上传方法 (1-3): ").strip()
        
        if choice == "1":
            print(f"\n📤 使用SCP上传...")
            print(f"执行命令:")
            print(f"scp {package_file} root@{self.server_ip}:/tmp/")
            
            confirm = input("是否现在执行上传? (y/N): ").strip().lower()
            if confirm == 'y':
                result = os.system(f"scp {package_file} root@{self.server_ip}:/tmp/")
                if result == 0:
                    print("✅ 上传成功!")
                else:
                    print("❌ 上传失败，请检查网络连接和认证信息")
                    return False
            else:
                print("请手动执行上述命令完成上传")
                
        elif choice == "2":
            print(f"\n📤 使用FTP工具上传...")
            print("请使用您喜欢的FTP工具:")
            print(f"- 服务器地址: {self.server_ip}")
            print("- 用户名: root")
            print("- 上传路径: /tmp/")
            print(f"- 上传文件: {package_file}")
            
        else:
            print(f"\n📤 手动上传说明...")
            print("请将部署包上传到服务器 /tmp/ 目录")
            
        self.wait_for_user("上传完成后按回车继续...")
        return True
        
    def step_3_connect_server(self):
        self.current_step = 3
        self.print_header()
        
        print("\n🔗 步骤3: 连接服务器")
        print("-" * 30)
        
        print("连接方法:")
        print(f"ssh root@{self.server_ip}")
        
        print("\n🔍 连接测试...")
        print("如果是首次连接，会提示确认主机密钥，请输入 yes")
        print("然后输入root密码")
        
        print(f"\n💡 连接命令:")
        print(f"ssh root@{self.server_ip}")
        
        self.wait_for_user("请在新终端窗口中连接服务器，连接成功后按回车继续...")
        return True
        
    def step_4_extract_prepare(self):
        self.current_step = 4
        self.print_header()
        
        print("\n📁 步骤4: 解压和准备")
        print("-" * 30)
        
        commands = [
            "# 进入opt目录",
            "cd /opt",
            "",
            "# 解压部署包",
            "tar -xzf /tmp/jelilian-hongkong-deploy.tar.gz",
            "",
            "# 重命名目录",
            "mv jelilian-deploy jelilian-ai-pro",
            "",
            "# 进入应用目录",
            "cd jelilian-ai-pro",
            "",
            "# 查看文件",
            "ls -la",
            "",
            "# 设置执行权限",
            "chmod +x deploy/*.sh",
            "chmod +x *.py"
        ]
        
        print("请在服务器上执行以下命令:")
        print("```bash")
        for cmd in commands:
            print(cmd)
        print("```")
        
        self.wait_for_user("命令执行完成后按回车继续...")
        return True
        
    def step_5_run_deploy(self):
        self.current_step = 5
        self.print_header()
        
        print("\n🚀 步骤5: 运行部署脚本")
        print("-" * 30)
        
        print("现在运行自动部署脚本:")
        print("```bash")
        print("./deploy/hongkong_deploy.sh")
        print("```")
        
        print("\n📋 部署脚本会自动:")
        print("✅ 更新系统包")
        print("✅ 安装Python环境")
        print("✅ 安装项目依赖")
        print("✅ 配置Nginx")
        print("✅ 配置Supervisor")
        print("✅ 启动服务")
        print("✅ 配置防火墙")
        print("✅ 设置监控")
        
        print("\n⏱️  预计耗时: 5-10分钟")
        print("⚠️  如果提示上传项目文件，请按回车继续")
        
        self.wait_for_user("请执行部署脚本，完成后按回车继续...")
        return True
        
    def step_6_verify_deployment(self):
        self.current_step = 6
        self.print_header()
        
        print("\n✅ 步骤6: 验证部署")
        print("-" * 30)
        
        print("请在服务器上执行以下验证命令:")
        
        verification_commands = [
            "# 检查服务状态",
            "systemctl status jelilian",
            "systemctl status nginx",
            "",
            "# 检查端口监听",
            "netstat -tulpn | grep :8003",
            "netstat -tulpn | grep :80",
            "",
            "# 测试本地访问",
            "curl http://localhost/health",
            "",
            "# 查看应用日志",
            "tail -n 20 /var/log/jelilian/app.log"
        ]
        
        print("```bash")
        for cmd in verification_commands:
            print(cmd)
        print("```")
        
        print(f"\n🌐 外部访问测试:")
        print(f"在浏览器中访问: http://{self.server_ip}")
        
        success = input("\n❓ 部署验证是否成功? (y/N): ").strip().lower()
        if success != 'y':
            print("\n🔧 故障排除:")
            print("1. 检查防火墙设置")
            print("2. 查看错误日志: tail -f /var/log/jelilian/app.log")
            print("3. 重启服务: systemctl restart jelilian")
            return False
            
        print("✅ 部署验证成功!")
        return True
        
    def step_7_domain_ssl(self):
        self.current_step = 7
        self.print_header()
        
        print("\n🌐 步骤7: 配置域名和SSL (可选)")
        print("-" * 30)
        
        has_domain = input("是否有域名需要配置? (y/N): ").strip().lower()
        
        if has_domain == 'y':
            domain = input("请输入您的域名 (例: jelilian.example.com): ").strip()
            email = input("请输入您的邮箱 (用于SSL证书): ").strip()
            
            if domain and email:
                print(f"\n🔒 配置SSL证书:")
                print("```bash")
                print(f"./deploy/hongkong_ssl_setup.sh {domain} {email}")
                print("```")
                
                print(f"\n📋 DNS配置:")
                print("请在域名服务商处添加A记录:")
                print(f"类型: A")
                print(f"主机记录: @ (或 www)")
                print(f"记录值: {self.server_ip}")
                print(f"TTL: 600")
                
                self.wait_for_user("DNS配置完成并执行SSL脚本后按回车继续...")
                
                print(f"✅ 配置完成!")
                print(f"🌐 HTTPS访问: https://{domain}")
                self.domain = domain
            else:
                print("❌ 域名或邮箱不能为空")
                return False
        else:
            print("⏭️  跳过域名配置")
            self.domain = None
            
        return True
        
    def step_8_final_test(self):
        self.current_step = 8
        self.print_header()
        
        print("\n🧪 步骤8: 最终测试")
        print("-" * 30)
        
        if hasattr(self, 'domain') and self.domain:
            test_url = f"https://{self.domain}"
        else:
            test_url = f"http://{self.server_ip}"
            
        print(f"🌐 访问地址: {test_url}")
        
        print("\n📋 功能测试清单:")
        tests = [
            "访问首页",
            "用户注册",
            "用户登录", 
            "AI对话试用",
            "升级页面",
            "支付页面"
        ]
        
        for i, test in enumerate(tests, 1):
            print(f"   {i}. {test}")
            
        print(f"\n🔧 管理命令:")
        print("```bash")
        print("# 查看服务状态")
        print("systemctl status jelilian nginx")
        print("")
        print("# 查看日志")
        print("tail -f /var/log/jelilian/app.log")
        print("")
        print("# 重启服务")
        print("systemctl restart jelilian")
        print("")
        print("# 备份数据")
        print("./deploy/hongkong_backup.sh")
        print("```")
        
        success = input(f"\n❓ 所有功能测试是否正常? (y/N): ").strip().lower()
        if success == 'y':
            print("\n🎉 部署完全成功!")
            self.show_success_summary()
        else:
            print("\n🔧 请检查问题并重新测试")
            return False
            
        return True
        
    def show_success_summary(self):
        print("\n" + "🎉" * 20)
        print("   JELILIAN AI PRO 部署成功!")
        print("🎉" * 20)
        
        if hasattr(self, 'domain') and self.domain:
            print(f"🌐 访问地址: https://{self.domain}")
        else:
            print(f"🌐 访问地址: http://{self.server_ip}")
            
        print(f"📍 服务器: 阿里云香港 ({self.server_ip})")
        print(f"🔧 管理目录: /opt/jelilian-ai-pro")
        print(f"📋 日志目录: /var/log/jelilian")
        
        print(f"\n📞 技术支持:")
        print(f"   微信: 18501935068")
        print(f"   邮箱: 18501935068@163.com")
        print(f"   WhatsApp: +8618501935068")
        
        print(f"\n🎯 下一步建议:")
        print(f"   1. 配置CDN加速")
        print(f"   2. 设置监控告警")
        print(f"   3. 制定备份策略")
        print(f"   4. 进行压力测试")
        
    def run(self):
        """运行部署助手"""
        print("🚀 欢迎使用JELILIAN AI PRO部署助手!")
        print("我将引导您完成阿里云香港地域的部署过程。")
        
        steps_methods = [
            self.step_1_server_info,
            self.step_2_upload_package,
            self.step_3_connect_server,
            self.step_4_extract_prepare,
            self.step_5_run_deploy,
            self.step_6_verify_deployment,
            self.step_7_domain_ssl,
            self.step_8_final_test
        ]
        
        for step_method in steps_methods:
            if not step_method():
                print(f"\n❌ 步骤 {self.current_step} 失败，请解决问题后重新运行")
                return False
                
        return True

if __name__ == "__main__":
    assistant = DeploymentAssistant()
    assistant.run()