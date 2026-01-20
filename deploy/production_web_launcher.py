#!/usr/bin/env python3
"""
JELILIAN AI PRO 生产环境Web启动器
优化的生产环境配置，支持高并发和稳定性
"""

import asyncio
import sys
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 生产环境导入
from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/jelilian-ai-pro.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="JELILIAN AI PRO",
    description="基于千问大模型的智能AI助手",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None
)

# 中间件配置
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# 信任的主机
trusted_hosts = ["*"]  # 生产环境应该限制具体域名
if os.getenv("ENVIRONMENT") == "production":
    trusted_hosts = ["your-domain.com", "www.your-domain.com"]

app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)

# 安全配置
security = HTTPBearer(auto_error=False)

# 请求限制
request_count = {}
MAX_REQUESTS_PER_MINUTE = 60

def rate_limit_check(request: Request):
    """简单的请求频率限制"""
    client_ip = request.client.host
    current_time = datetime.now()
    
    if client_ip not in request_count:
        request_count[client_ip] = []
    
    # 清理1分钟前的请求记录
    request_count[client_ip] = [
        req_time for req_time in request_count[client_ip]
        if (current_time - req_time).seconds < 60
    ]
    
    # 检查请求频率
    if len(request_count[client_ip]) >= MAX_REQUESTS_PER_MINUTE:
        raise HTTPException(status_code=429, detail="请求过于频繁，请稍后再试")
    
    request_count[client_ip].append(current_time)

# 生产环境HTML模板
PRODUCTION_HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="JELILIAN AI PRO - 基于千问大模型的智能AI助手">
    <meta name="keywords" content="AI助手,人工智能,千问,智能对话">
    <title>JELILIAN AI PRO - 智能AI助手</title>
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Microsoft YaHei', 'PingFang SC', Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            line-height: 1.6;
        }
        .container { 
            background: white; 
            border-radius: 20px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
            width: 90%;
            max-width: 900px;
            animation: fadeIn 0.5s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
        }
        .header h1 { 
            color: #333; 
            font-size: 2.5em; 
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .header p { 
            color: #666; 
            font-size: 1.1em; 
        }
        .chat-form { 
            margin-bottom: 30px; 
        }
        .input-group { 
            margin-bottom: 20px; 
        }
        label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: bold; 
            color: #333; 
        }
        textarea { 
            width: 100%; 
            padding: 15px; 
            border: 2px solid #e1e5e9; 
            border-radius: 10px; 
            font-size: 16px; 
            resize: vertical; 
            min-height: 120px;
            transition: all 0.3s ease;
            font-family: inherit;
        }
        textarea:focus { 
            outline: none; 
            border-color: #667eea; 
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .btn { 
            background: linear-gradient(45deg, #667eea, #764ba2); 
            color: white; 
            padding: 15px 30px; 
            border: none; 
            border-radius: 10px; 
            font-size: 16px; 
            cursor: pointer; 
            transition: all 0.3s ease;
            width: 100%;
            font-weight: bold;
        }
        .btn:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        .btn:active {
            transform: translateY(0);
        }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .response { 
            background: #f8f9fa; 
            border-radius: 10px; 
            padding: 20px; 
            margin-top: 20px; 
            border-left: 4px solid #667eea;
            animation: slideIn 0.3s ease-out;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        .response h3 { 
            color: #333; 
            margin-bottom: 10px; 
            display: flex;
            align-items: center;
        }
        .response-content { 
            color: #555; 
            line-height: 1.8; 
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .loading { 
            text-align: center; 
            color: #667eea; 
            font-style: italic;
            padding: 20px;
        }
        .loading::after {
            content: '';
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid #667eea;
            border-radius: 50%;
            border-top-color: transparent;
            animation: spin 1s linear infinite;
            margin-left: 10px;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .examples { 
            margin-top: 20px; 
        }
        .examples h3 { 
            color: #333; 
            margin-bottom: 15px; 
        }
        .example-btn { 
            background: #f8f9fa; 
            border: 1px solid #e1e5e9; 
            padding: 10px 15px; 
            margin: 5px; 
            border-radius: 20px; 
            cursor: pointer; 
            display: inline-block; 
            transition: all 0.2s ease;
            font-size: 14px;
        }
        .example-btn:hover { 
            background: #667eea; 
            color: white; 
            transform: translateY(-1px);
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e1e5e9;
            color: #666;
            font-size: 14px;
        }
        .error {
            background: #fee;
            border-left: 4px solid #f56565;
            color: #c53030;
        }
        @media (max-width: 768px) {
            .container {
                margin: 20px;
                padding: 20px;
            }
            .header h1 {
                font-size: 2em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 JELILIAN AI PRO</h1>
            <p>基于千问大模型的智能AI助手</p>
        </div>
        
        <form class="chat-form" method="post" action="/chat" id="chatForm">
            <div class="input-group">
                <label for="prompt">💬 请输入您的问题或需求：</label>
                <textarea name="prompt" id="prompt" placeholder="例如：请帮我写一个Python函数来计算斐波那契数列..." required></textarea>
            </div>
            <button type="submit" class="btn" id="submitBtn">🚀 发送消息</button>
        </form>
        
        <div class="examples">
            <h3>💡 示例问题：</h3>
            <span class="example-btn" onclick="setPrompt('请用Python写一个计算器程序')">编程助手</span>
            <span class="example-btn" onclick="setPrompt('请帮我分析一下当前AI技术的发展趋势')">技术分析</span>
            <span class="example-btn" onclick="setPrompt('请为我的项目写一份README文档')">文档写作</span>
            <span class="example-btn" onclick="setPrompt('请解释一下机器学习的基本概念')">知识问答</span>
            <span class="example-btn" onclick="setPrompt('请帮我优化这段代码的性能')">代码优化</span>
            <span class="example-btn" onclick="setPrompt('请写一个创业计划书大纲')">商业策划</span>
        </div>
        
        {% if response %}
        <div class="response {% if error %}error{% endif %}">
            <h3>{% if error %}❌ 错误信息：{% else %}🤖 AI回复：{% endif %}</h3>
            <div class="response-content">{{ response }}</div>
        </div>
        {% endif %}
        
        <div class="footer">
            <p>© 2024 JELILIAN AI PRO. Powered by Qwen AI Model.</p>
            <p>智能AI助手 | 安全可靠 | 持续优化</p>
        </div>
    </div>
    
    <script>
        function setPrompt(text) {
            document.getElementById('prompt').value = text;
            document.getElementById('prompt').focus();
        }
        
        // 表单提交处理
        document.getElementById('chatForm').addEventListener('submit', function(e) {
            const submitBtn = document.getElementById('submitBtn');
            const prompt = document.getElementById('prompt').value.trim();
            
            if (!prompt) {
                e.preventDefault();
                alert('请输入您的问题');
                return;
            }
            
            // 显示加载状态
            submitBtn.disabled = true;
            submitBtn.innerHTML = '🤔 AI思考中...';
            
            // 添加加载提示
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'loading';
            loadingDiv.innerHTML = '正在处理您的请求，请稍候...';
            document.querySelector('.chat-form').appendChild(loadingDiv);
        });
        
        // 键盘快捷键
        document.getElementById('prompt').addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                document.getElementById('chatForm').submit();
            }
        });
        
        // 自动调整文本框高度
        document.getElementById('prompt').addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 300) + 'px';
        });
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """主页"""
    rate_limit_check(request)
    return PRODUCTION_HTML_TEMPLATE.replace("{% if response %}", "{% if False %}").replace("{{ response }}", "")

@app.post("/chat", response_class=HTMLResponse)
async def chat(request: Request, prompt: str = Form(...)):
    """处理聊天请求"""
    try:
        rate_limit_check(request)
        
        # 输入验证
        if not prompt or len(prompt.strip()) == 0:
            raise HTTPException(status_code=400, detail="请输入有效的问题")
        
        if len(prompt) > 2000:
            raise HTTPException(status_code=400, detail="问题长度不能超过2000字符")
        
        logger.info(f"收到请求: {prompt[:100]}...")
        
        # 导入LLM
        from app.llm import LLM
        llm = LLM()
        
        # 调用AI
        response = await llm.ask([{"role": "user", "content": prompt.strip()}])
        
        logger.info(f"AI回复长度: {len(response)}")
        
        # 返回结果
        html = PRODUCTION_HTML_TEMPLATE.replace("{% if response %}", "").replace("{% endif %}", "")
        html = html.replace("{{ response }}", response)
        html = html.replace("{% if error %}", "{% if False %}")
        return html
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}", exc_info=True)
        
        error_msg = "抱歉，处理您的请求时遇到了问题，请稍后再试。"
        if "API" in str(e):
            error_msg = "AI服务暂时不可用，请稍后再试。"
        elif "timeout" in str(e).lower():
            error_msg = "请求超时，请稍后再试。"
        
        html = PRODUCTION_HTML_TEMPLATE.replace("{% if response %}", "").replace("{% endif %}", "")
        html = html.replace("{{ response }}", error_msg)
        html = html.replace("{% if error %}", "")
        return html

@app.get("/health")
async def health_check():
    """健康检查端点"""
    try:
        # 检查AI服务
        from app.config import Config
        config = Config()
        
        return JSONResponse({
            "status": "healthy",
            "service": "JELILIAN AI PRO",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "model": config.llm['default'].model
        })
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

@app.get("/favicon.ico")
async def favicon():
    """Favicon处理"""
    return JSONResponse(status_code=204, content={})

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"全局异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "服务器内部错误，请稍后再试"}
    )

def main():
    """启动生产环境Web服务器"""
    logger.info("🚀 启动JELILIAN AI PRO生产环境Web服务器...")
    
    # 生产环境配置
    config = {
        "host": "127.0.0.1",
        "port": 8000,
        "log_level": "info",
        "access_log": True,
        "use_colors": False,
        "server_header": False,
        "date_header": False
    }
    
    logger.info(f"📍 服务器配置: {config}")
    
    try:
        uvicorn.run(app, **config)
    except KeyboardInterrupt:
        logger.info("👋 服务器已停止")
    except Exception as e:
        logger.error(f"服务器启动失败: {str(e)}")
        raise

if __name__ == "__main__":
    main()