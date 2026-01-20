#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI, Form, HTTPException, Depends, status, Request, Cookie, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import sys
import json
import asyncio
from typing import Optional, Dict
from user_manager import user_manager
from translations import get_text, get_all_translations, SUPPORTED_LANGUAGES

sys.path.insert(0, '.')

app = FastAPI(title="JELILIAN AI PRO")

# 添加静态文件服务
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# 添加CORS中间件支持前后端分离
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

def get_current_user_from_cookie(session_id: Optional[str] = Cookie(None)) -> Optional[Dict]:
    """从Cookie获取当前用户"""
    if not session_id:
        return None
    return user_manager.get_user_by_session(session_id)

def get_language(request: Request, lang: Optional[str] = None) -> str:
    """获取用户语言偏好"""
    # 1. 优先使用URL参数
    if lang and lang in SUPPORTED_LANGUAGES:
        return lang
    # 2. 从Cookie获取
    cookie_lang = request.cookies.get("lang")
    if cookie_lang and cookie_lang in SUPPORTED_LANGUAGES:
        return cookie_lang
    # 3. 从Accept-Language头获取
    accept_lang = request.headers.get("accept-language", "")
    for supported in SUPPORTED_LANGUAGES.keys():
        if supported in accept_lang.lower():
            return supported
    # 4. 默认中文
    return "zh"

def get_language_selector_html(current_lang: str) -> str:
    """生成语言选择器HTML"""
    options = ""
    for code, name in SUPPORTED_LANGUAGES.items():
        selected = "selected" if code == current_lang else ""
        options += f'<option value="{code}" {selected}>{name}</option>'
    
    return f'''
    <div class="language-selector">
        <select id="langSelect" onchange="changeLanguage(this.value)">
            {options}
        </select>
    </div>
    '''

@app.get("/api/set-language")
async def set_language(lang: str = Query(...)):
    """设置语言偏好"""
    if lang not in SUPPORTED_LANGUAGES:
        return JSONResponse(status_code=400, content={"error": "Unsupported language"})
    
    response = JSONResponse({"success": True, "language": lang})
    response.set_cookie(key="lang", value=lang, max_age=365*24*60*60)
    return response

@app.get("/api/translations")
async def get_translations(lang: str = Query(default="zh")):
    """获取翻译文本"""
    return JSONResponse(get_all_translations(lang))

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, lang: Optional[str] = Query(default=None), current_user: Optional[Dict] = Depends(get_current_user_from_cookie)):
    # 获取语言
    current_lang = get_language(request, lang)
    t = lambda key: get_text(key, current_lang)
    lang_selector = get_language_selector_html(current_lang)
    
    user_info = ""
    nav_buttons = ""
    
    if current_user:
        from trial_manager import trial_manager
        from credit_manager import credit_manager
        
        trial_info = trial_manager.get_trial_info(current_user['id'])
        credit_info = credit_manager.get_user_credits(current_user['id'])
        
        # 每日刷新积分
        credit_manager.daily_refresh_credits(current_user['id'])
        credit_info = credit_manager.get_user_credits(current_user['id'])  # 重新获取
        
        trial_status = ""
        
        if current_user.get('subscription', 'free') == 'free':
            trial_check = trial_manager.can_use_trial(current_user['id'])
            if isinstance(trial_check, dict):
                can_use = trial_check.get('can_use', False)
            else:
                can_use = trial_check
            if can_use:
                trial_status = f'<span class="trial-available">{t("trial_available")}</span>'
            else:
                trial_status = f'<span class="trial-used">{t("trial_used")}</span>'
        else:
            subscription_name = {
                'basic': t('basic_plan') + ' ($20/' + t('monthly_credits').split()[0] + ')',
                'pro': t('pro_plan') + ' ($50/' + t('monthly_credits').split()[0] + ')',
                'custom': t('custom_plan')
            }.get(current_user.get('subscription'), current_user.get('subscription'))
            
            credits_display = f"{credit_info.get('current_credits', 0):,}" if credit_info else "0"
            trial_status = f'<span class="subscription-active">💎 {subscription_name}</span><span class="credits-info">💰 {credits_display}</span>'
        
        user_info = f'''
        <div class="user-info">
            <span>👋 {t("welcome")}，{current_user.get('username')}！</span>
            {trial_status}
            <a href="/logout" class="logout-btn">{t("logout")}</a>
        </div>
        '''
        nav_buttons = f'''
        <div class="nav-buttons">
            <a href="/upgrade" class="nav-btn">💎 {t("upgrade")}</a>
            <a href="/profile" class="nav-btn">👤 {t("profile")}</a>
        </div>
        '''
    else:
        nav_buttons = f'''
        <div class="nav-buttons">
            <a href="/upgrade" class="nav-btn">💎 {t("upgrade")}</a>
            <a href="/login" class="nav-btn">👤 {t("login")}</a>
            <a href="/register" class="nav-btn">📝 {t("register")}</a>
        </div>
        '''
    
    return f'''<!DOCTYPE html>
<html lang="{current_lang}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JELILIAN AI PRO - {t("app_subtitle")}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Microsoft YaHei', Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .container {{ 
            background: white; 
            border-radius: 20px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
            width: 90%;
            max-width: 800px;
            position: relative;
        }}
        .language-selector {{
            position: absolute;
            top: 15px;
            right: 15px;
        }}
        .language-selector select {{
            padding: 8px 15px;
            border: 2px solid #667eea;
            border-radius: 20px;
            background: white;
            color: #667eea;
            font-size: 14px;
            cursor: pointer;
            outline: none;
        }}
        .language-selector select:hover {{
            background: #667eea;
            color: white;
        }}
        .header {{ 
            text-align: center; 
            margin-bottom: 30px; 
        }}
        .header h1 {{ 
            color: #333; 
            font-size: 2.5em; 
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .user-info {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .subscription {{
            background: #667eea;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.9em;
        }}
        .trial-available {{
            background: #27ae60;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.9em;
        }}
        .trial-used {{
            background: #e74c3c;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.9em;
        }}
        .subscription-active {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.9em;
            margin-right: 10px;
        }}
        .credits-info {{
            background: #27ae60;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.9em;
        }}
        .logout-btn {{
            color: #e74c3c;
            text-decoration: none;
            font-weight: bold;
        }}
        .nav-buttons {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .nav-btn {{
            padding: 8px 20px;
            border: 2px solid #667eea;
            border-radius: 20px;
            color: #667eea;
            text-decoration: none;
            margin: 0 10px;
            display: inline-block;
            transition: all 0.3s;
        }}
        .nav-btn:hover {{
            background: #667eea;
            color: white;
            transform: translateY(-2px);
        }}
        .trial-notice {{
            background: linear-gradient(45deg, #ff6b6b, #ffa500);
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
            font-weight: bold;
        }}
        .chat-container {{ 
            margin-bottom: 30px; 
        }}
        .chat-form {{
            margin-bottom: 20px;
        }}
        label {{ 
            display: block; 
            margin-bottom: 8px; 
            font-weight: bold; 
            color: #333; 
        }}
        textarea {{ 
            width: 100%; 
            padding: 15px; 
            border: 2px solid #e1e5e9; 
            border-radius: 10px; 
            font-size: 16px; 
            resize: vertical; 
            min-height: 120px;
            transition: border-color 0.3s;
        }}
        textarea:focus {{ 
            outline: none; 
            border-color: #667eea; 
        }}
        .btn {{ 
            background: linear-gradient(45deg, #667eea, #764ba2); 
            color: white; 
            padding: 15px 30px; 
            border: none; 
            border-radius: 10px; 
            font-size: 16px; 
            cursor: pointer; 
            transition: transform 0.2s;
            width: 100%;
            margin-top: 15px;
        }}
        .btn:hover {{ 
            transform: translateY(-2px); 
        }}
        .btn:disabled {{
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }}
        .chat-history {{
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #e1e5e9;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            background: #f8f9fa;
        }}
        .message {{
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 8px;
        }}
        .user-message {{
            background: #667eea;
            color: white;
            margin-left: 20%;
        }}
        .ai-message {{
            background: white;
            border: 1px solid #e1e5e9;
            margin-right: 20%;
        }}
        .typing-indicator {{
            display: none;
            color: #667eea;
            font-style: italic;
            margin: 15px 0;
            padding: 20px;
            background: linear-gradient(45deg, #f8f9fa, #e9ecef);
            border-radius: 15px;
            border-left: 5px solid #667eea;
            font-size: 1.3em;
            font-weight: bold;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
            animation: indicatorPulse 2s infinite;
        }}
        .typing-indicator.show {{
            display: block;
        }}
        @keyframes indicatorPulse {{
            0% {{ transform: scale(1); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2); }}
            50% {{ transform: scale(1.02); box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3); }}
            100% {{ transform: scale(1); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2); }}
        }}
        .typing-dots {{
            display: inline-block;
            color: #ff6b6b;
            font-weight: bold;
            font-size: 1.2em;
            margin-left: 5px;
        }}
        .typing-dots::after {{
            content: '....';
            animation: typingDots 1.2s infinite;
        }}
        @keyframes typingDots {{
            0% {{ content: ''; }}
            20% {{ content: '.'; }}
            40% {{ content: '..'; }}
            60% {{ content: '...'; }}
            80% {{ content: '....'; }}
            100% {{ content: '.....'; }}
        }}
        @keyframes titlePulse {{
            0% {{ 
                transform: scale(1) rotate(0deg); 
                text-shadow: 3px 3px 8px rgba(0,0,0,0.5);
                color: #fff;
            }}
            50% {{ 
                transform: scale(1.1) rotate(1deg); 
                text-shadow: 5px 5px 15px rgba(0,0,0,0.8);
                color: #ffff00;
            }}
            100% {{ 
                transform: scale(1) rotate(0deg); 
                text-shadow: 3px 3px 8px rgba(0,0,0,0.5);
                color: #fff;
            }}
        }}
        .upgrade-notice {{
            background: linear-gradient(45deg, #ff1744, #ff9800, #ff1744);
            background-size: 200% 200%;
            color: white;
            padding: 35px;
            border-radius: 25px;
            text-align: center;
            margin: 25px 0;
            box-shadow: 0 20px 50px rgba(255, 23, 68, 0.6);
            animation: pulse 1.5s infinite, gradientShift 3s ease-in-out infinite;
            border: 4px solid rgba(255,255,255,0.5);
            position: relative;
            overflow: hidden;
        }}
        .upgrade-notice::before {{
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
            animation: shine 2s infinite;
        }}
        @keyframes gradientShift {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        @keyframes shine {{
            0% {{ transform: translateX(-100%) translateY(-100%) rotate(45deg); }}
            100% {{ transform: translateX(100%) translateY(100%) rotate(45deg); }}
        }}
        .upgrade-notice h3 {{
            font-size: 3.2em;
            margin-bottom: 20px;
            font-weight: 900;
            text-shadow: 4px 4px 10px rgba(0,0,0,0.6);
            letter-spacing: 3px;
            animation: titlePulse 1.2s ease-in-out infinite;
            text-transform: uppercase;
            position: relative;
            z-index: 1;
        }}
        .upgrade-notice p {{
            margin-bottom: 20px;
            font-size: 1.1em;
        }}
        .upgrade-btn {{
            background: white;
            color: #ff6b6b;
            padding: 12px 30px;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
            margin: 0 10px;
        }}
        .upgrade-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.02); }}
            100% {{ transform: scale(1); }}
        }}
        .examples {{ 
            margin-top: 20px; 
        }}
        .examples h3 {{ 
            color: #333; 
            margin-bottom: 15px; 
        }}
        .example-btn {{ 
            background: #f8f9fa; 
            border: 1px solid #e1e5e9; 
            padding: 10px 15px; 
            margin: 5px; 
            border-radius: 20px; 
            cursor: pointer; 
            display: inline-block; 
            transition: all 0.2s;
        }}
        .example-btn:hover {{ 
            background: #667eea; 
            color: white; 
        }}
        .upgrade-prompt, .trial-ended {{
            background: linear-gradient(45deg, #ff6b6b, #ffa500);
            color: white;
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
        }}
        .upgrade-content, .trial-ended-content {{
            text-align: center;
        }}
        .upgrade-content h3, .trial-ended-content h3 {{
            margin-bottom: 20px;
            font-size: 3.5em;
            font-weight: 900;
            text-shadow: 3px 3px 8px rgba(0,0,0,0.5);
            letter-spacing: 2px;
            animation: titlePulse 1.2s ease-in-out infinite;
            color: #fff;
            text-transform: uppercase;
            line-height: 1.1;
        }}
        .recommendations {{
            margin: 20px 0;
            background: rgba(255,255,255,0.1);
            padding: 15px;
            border-radius: 10px;
        }}
        .recommendations h4 {{
            margin-bottom: 10px;
            color: white;
        }}
        .recommendation-buttons {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
        }}
        .recommendation-btn {{
            background: rgba(255,255,255,0.2);
            color: white;
            border: 1px solid rgba(255,255,255,0.3);
            padding: 8px 15px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 0.9em;
        }}
        .recommendation-btn:hover {{
            background: rgba(255,255,255,0.3);
            transform: translateY(-2px);
        }}
        .upgrade-actions {{
            margin-top: 20px;
        }}
        .upgrade-btn {{
            background: #27ae60;
            color: white;
            padding: 12px 25px;
            border-radius: 25px;
            text-decoration: none;
            margin: 0 10px;
            display: inline-block;
            font-weight: bold;
            transition: all 0.3s;
        }}
        .upgrade-btn:hover {{
            background: #219a52;
            transform: translateY(-2px);
        }}
        .contact-btn {{
            background: transparent;
            color: white;
            border: 2px solid white;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            margin: 0 10px;
            transition: all 0.3s;
        }}
        .contact-btn:hover {{
            background: white;
            color: #ff6b6b;
        }}
        .upgrade-info ul {{
            list-style: none;
            padding: 0;
            margin: 10px 0;
        }}
        .upgrade-info li {{
            padding: 5px 0;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        {lang_selector}
        <div class="header">
            <h1>🤖 JELILIAN AI PRO</h1>
            <p>{t("app_subtitle")}</p>
        </div>
        
        {user_info}
        {nav_buttons}
        
        <div class="trial-notice">
            {t("trial_notice")}
        </div>
        
        <div class="chat-container">
            <div class="chat-history" id="chatHistory">
                <div class="message ai-message">
                    <strong>🤖 AI:</strong> {t("welcome_message")}
                </div>
            </div>
            
            <div class="typing-indicator" id="typingIndicator">
                {t("ai_thinking")}<span class="typing-dots"></span>
            </div>
            
            <form class="chat-form" id="chatForm">
                <label for="prompt">💬 {t("input_placeholder").split("...")[0]}:</label>
                <textarea name="prompt" id="prompt" placeholder="{t("input_placeholder")}" required></textarea>
                <button type="submit" class="btn" id="sendBtn">{t("send_message")}</button>
            </form>
        </div>
        
        <div class="examples">
            <h3>{t("example_questions")}</h3>
            <span class="example-btn" onclick="setPrompt('Please write a calculator program in Python')">{t("example_coding")}</span>
            <span class="example-btn" onclick="setPrompt('Please analyze the current AI technology trends')">{t("example_analysis")}</span>
            <span class="example-btn" onclick="setPrompt('Please write a README document for my project')">{t("example_writing")}</span>
            <span class="example-btn" onclick="setPrompt('Please explain the basic concepts of machine learning')">{t("example_qa")}</span>
        </div>
    </div>
    
    <script>
        function changeLanguage(lang) {{
            fetch('/api/set-language?lang=' + lang)
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        window.location.reload();
                    }}
                }});
        }}
        
        function setPrompt(text) {{
            document.getElementById('prompt').value = text;
        }}
        
        function addMessage(content, isUser = false) {{
            const chatHistory = document.getElementById('chatHistory');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${{isUser ? 'user-message' : 'ai-message'}}`;
            messageDiv.innerHTML = `<strong>${{isUser ? '👤 You' : '🤖 AI'}}:</strong> ${{content}}`;
            chatHistory.appendChild(messageDiv);
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }}
        
        function showTyping() {{
            document.getElementById('typingIndicator').classList.add('show');
        }}
        
        function hideTyping() {{
            document.getElementById('typingIndicator').classList.remove('show');
        }}
        
        document.getElementById('chatForm').addEventListener('submit', async function(e) {{
            e.preventDefault();
            
            const prompt = document.getElementById('prompt').value.trim();
            if (!prompt) return;
            
            const sendBtn = document.getElementById('sendBtn');
            sendBtn.disabled = true;
            sendBtn.textContent = '...';
            
            // 添加用户消息
            addMessage(prompt, true);
            document.getElementById('prompt').value = '';
            
            // 显示输入指示器
            showTyping();
            
            try {{
                const response = await fetch('/api/chat', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{ prompt: prompt }})
                }});
                
                if (!response.ok) {{
                    throw new Error('网络请求失败');
                }}
                
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let aiResponse = '';
                
                // 隐藏输入指示器，开始显示AI响应
                hideTyping();
                
                // 创建AI消息容器
                const chatHistory = document.getElementById('chatHistory');
                const aiMessageDiv = document.createElement('div');
                aiMessageDiv.className = 'message ai-message';
                aiMessageDiv.innerHTML = '<strong>🤖 AI助手:</strong> <span id="aiContent"></span>';
                chatHistory.appendChild(aiMessageDiv);
                
                const aiContentSpan = document.getElementById('aiContent');
                
                while (true) {{
                    const {{ done, value }} = await reader.read();
                    if (done) break;
                    
                    const chunk = decoder.decode(value);
                    const lines = chunk.split('\\n');
                    
                    for (const line of lines) {{
                        if (line.startsWith('data: ')) {{
                            const data = line.slice(6);
                            if (data === '[DONE]') {{
                                break;
                            }}
                            try {{
                                const parsed = JSON.parse(data);
                                
                                // 处理积分使用状态
                                if (parsed.credit_used) {{
                                    const creditInfo = document.createElement('div');
                                    creditInfo.className = 'message ai-message';
                                    creditInfo.innerHTML = `<strong>💰 积分状态:</strong> ${{parsed.message}}`;
                                    chatHistory.appendChild(creditInfo);
                                    chatHistory.scrollTop = chatHistory.scrollHeight;
                                }}
                                
                                // 处理积分不足错误
                                if (parsed.error && parsed.type === 'insufficient_credits') {{
                                    const errorDiv = document.createElement('div');
                                    errorDiv.className = 'message ai-message';
                                    errorDiv.style.background = '#ffe6e6';
                                    errorDiv.style.borderLeft = '4px solid #ff4444';
                                    errorDiv.innerHTML = `
                                        <strong>⚠️ 积分不足:</strong> ${{parsed.error}}<br>
                                        <a href="/upgrade" style="color: #667eea; text-decoration: none; font-weight: bold;">💎 立即充值积分</a>
                                    `;
                                    chatHistory.appendChild(errorDiv);
                                    chatHistory.scrollTop = chatHistory.scrollHeight;
                                    break;
                                }}
                                
                                // 处理错误消息
                                if (parsed.error) {{
                                    if (parsed.upgrade_required) {{
                                        showUpgradePrompt(parsed);
                                    }} else {{
                                        aiContentSpan.textContent = parsed.error;
                                    }}
                                    break;
                                }}
                                
                                // 处理试用结束消息
                                if (parsed.trial_ended) {{
                                    showTrialEndedPrompt(parsed);
                                    break;
                                }}
                                
                                // 处理正常内容
                                if (parsed.content) {{
                                    aiResponse += parsed.content;
                                    aiContentSpan.textContent = aiResponse;
                                    chatHistory.scrollTop = chatHistory.scrollHeight;
                                }}
                            }} catch (e) {{
                                // 忽略解析错误
                            }}
                        }}
                    }}
                }}
                
            }} catch (error) {{
                hideTyping();
                addMessage('抱歉，发生了错误：' + error.message, false);
            }} finally {{
                sendBtn.disabled = false;
                sendBtn.textContent = '🚀 发送消息';
            }}
        }});
        
        function showTrialExhaustedInInput(data) {{
            console.log('执行showTrialExhaustedInInput函数:', data);
            
            // 显示输入框覆盖层
            const overlay = document.getElementById('trialEndedOverlay');
            const promptTextarea = document.getElementById('prompt');
            const sendBtn = document.getElementById('sendBtn');
            
            console.log('找到的元素:', {{
                overlay: overlay ? '存在' : '不存在',
                promptTextarea: promptTextarea ? '存在' : '不存在',
                sendBtn: sendBtn ? '存在' : '不存在'
            }});
            
            if (overlay) {{
                overlay.style.display = 'flex';  // 设置为flex以居中显示内容
                console.log('设置覆盖层显示为flex');
            }}
            
            if (promptTextarea) {{
                promptTextarea.disabled = true;
                promptTextarea.placeholder = '试用已用完，请升级继续使用';
                console.log('禁用输入框');
            }}
            
            if (sendBtn) {{
                sendBtn.disabled = true;
                sendBtn.textContent = '🚫 试用已用完';
                sendBtn.style.background = '#ccc';
                console.log('禁用发送按钮');
            }}
        }}
        
        function showUpgradePrompt(data) {{
            const chatHistory = document.getElementById('chatHistory');
            const upgradeDiv = document.createElement('div');
            upgradeDiv.className = 'message upgrade-prompt';
            upgradeDiv.innerHTML = `
                <div class="upgrade-content">
                    <h3>🎉 ${{data.message}}</h3>
                    <div class="recommendations">
                        <h4>💡 为您推荐相关问题：</h4>
                        <div class="recommendation-buttons">
                            ${{data.recommendations.map(rec => 
                                `<button class="recommendation-btn" onclick="setPrompt('${{rec}}')">${{rec}}</button>`
                            ).join('')}}
                        </div>
                    </div>
                    <div class="upgrade-actions">
                        <a href="/upgrade" class="upgrade-btn">💎 立即升级</a>
                        <button class="contact-btn" onclick="contactSupport()">💬 联系客服</button>
                    </div>
                </div>
            `;
            chatHistory.appendChild(upgradeDiv);
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }}
        
        function showTrialEndedPrompt(data) {{
            const chatHistory = document.getElementById('chatHistory');
            const trialEndDiv = document.createElement('div');
            trialEndDiv.className = 'message trial-ended';
            trialEndDiv.innerHTML = `
                <div class="trial-ended-content">
                    <h3>${{data.message}}</h3>
                    <div class="upgrade-info">
                        <h4>${{data.upgrade_info}}</h4>
                        <ul>
                            ${{data.features.map(feature => `<li>✓ ${{feature}}</li>`).join('')}}
                        </ul>
                    </div>
                    <div class="recommendations">
                        <h4>💡 继续探索这些话题：</h4>
                        <div class="recommendation-buttons">
                            ${{data.recommendations.map(rec => 
                                `<button class="recommendation-btn" onclick="setPrompt('${{rec}}')">${{rec}}</button>`
                            ).join('')}}
                        </div>
                    </div>
                    <div class="upgrade-actions">
                        <a href="${{data.upgrade_url}}" class="upgrade-btn">💎 立即升级解锁</a>
                    </div>
                </div>
            `;
            chatHistory.appendChild(trialEndDiv);
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }}
        
        // 页面加载时不检查试用状态，让新用户正常使用
        // 只有在聊天时发现试用已用完才显示覆盖层
        window.addEventListener('load', function() {{
            console.log('页面加载完成');
            // 移除自动检查，让新用户正常使用
        }});
        
        function contactSupport() {{
            alert('📞 联系客服：\\n\\n微信: 18501935068\\nWhatsApp: +8618501935068\\n邮箱: 18501935068@163.com');
        }}
    </script>
</body>
</html>'''

# API路由 - 流式聊天
@app.post("/api/chat")
async def api_chat(request: Request):
    try:
        body = await request.json()
        prompt = body.get("prompt", "").strip()
        
        if not prompt:
            raise HTTPException(status_code=400, detail="请输入有效的问题")
        
        if len(prompt) > 2000:
            raise HTTPException(status_code=400, detail="问题长度不能超过2000字符")
        
        async def generate_response():
            try:
                # 检查用户试用状态
                session_id = request.cookies.get("session_id")
                current_user = None
                if session_id:
                    current_user = user_manager.get_user_by_session(session_id)
                
                # 如果是未登录用户，提示注册
                if not current_user:
                    yield f"data: {json.dumps({'error': '请先注册登录以使用AI对话功能', 'type': 'auth_required'})}\n\n"
                    return
                
                # 检查用户订阅状态
                subscription = current_user.get('subscription', 'free')
                user_id = current_user['id']
                
                # 免费用户的试用限制
                if subscription == 'free':
                    from trial_manager import trial_manager
                    
                    # 严格检查：如果试用已用完，立即返回，不调用任何AI接口
                    if not trial_manager.can_chat(user_id):
                        # 获取距离下次可试用的天数
                        days_left = trial_manager.get_days_until_next_trial(user_id)
                        msg = f'🚫 本月试用额度已用完'
                        if days_left > 0:
                            msg += f'，{days_left}天后可再次试用'
                        msg += '。请升级付费版本继续使用'
                        
                        yield f"data: {json.dumps({'upgrade_required': True, 'message': msg, 'recommendations': ['升级基础版 $20/月', '升级专业版 $50/月', '联系客服了解自定义版']})}\n\n"
                        yield f"data: [DONE]\n\n"
                        return
                    
                    # 检查是否可以使用试用（一个月限制）
                    trial_check = trial_manager.can_use_trial(
                        user_id,
                        current_user.get('username'),
                        current_user.get('email'),
                        current_user.get('phone')
                    )
                    
                    if not trial_check['can_use']:
                        yield f"data: {json.dumps({'upgrade_required': True, 'message': '🚫 ' + trial_check['reason'], 'recommendations': ['升级基础版 $20/月', '升级专业版 $50/月', '联系客服了解自定义版']})}\n\n"
                        yield f"data: [DONE]\n\n"
                        return
                    
                    # 如果是第一次使用，标记试用开始
                    trial_info = trial_manager.get_trial_info(user_id)
                    if not trial_info or not trial_info.get('used'):
                        trial_result = trial_manager.use_trial(
                            user_id,
                            current_user.get('username'),
                            current_user.get('email'),
                            current_user.get('phone')
                        )
                        if not trial_result['success']:
                            yield f"data: {json.dumps({'upgrade_required': True, 'message': '🚫 ' + trial_result['message'], 'recommendations': ['升级基础版 $20/月', '升级专业版 $50/月', '联系客服了解自定义版']})}\n\n"
                            yield f"data: [DONE]\n\n"
                            return
                
                # 付费用户的积分检查
                elif subscription in ['basic', 'pro', 'custom']:
                    from credit_manager import credit_manager
                    
                    # 每日刷新积分
                    credit_manager.daily_refresh_credits(user_id)
                    
                    # 检查积分是否足够（每次对话消耗10积分）
                    credit_cost = 10
                    if subscription == 'pro':
                        credit_cost = 5  # Pro用户享受50%折扣
                    elif subscription == 'custom':
                        credit_cost = 3  # 自定义用户享受70%折扣
                    
                    credit_info = credit_manager.get_user_credits(user_id)
                    if credit_info['current_credits'] < credit_cost:
                        error_msg = f"积分不足，需要{credit_cost}积分，当前余额{credit_info['current_credits']}积分"
                        yield f"data: {json.dumps({'error': error_msg, 'type': 'insufficient_credits'})}\n\n"
                        return
                    
                    # 扣除积分
                    credit_manager.use_credits(user_id, credit_cost)
                
                # 调用AI系统（所有可以对话的用户）
                from app.llm import LLM
                from autogen_system import autogen_system
                
                # 根据用户等级选择不同的AI处理方式
                if subscription == 'free':
                    # 免费用户：基础AI对话
                    llm = LLM()
                    response = await llm.ask([{"role": "user", "content": prompt}])
                    final_response = response
                elif subscription == 'basic':
                    # 基础版用户：多智能体协作（3个智能体）
                    result = await autogen_system.process_with_multi_agents(prompt, ['analyst', 'creative', 'technical'])
                    final_response = result['final_response']
                elif subscription == 'pro':
                    # 专业版用户：完整多智能体协作（5个智能体）+ 深度分析
                    result = await autogen_system.process_with_multi_agents(prompt, ['analyst', 'creative', 'technical', 'product', 'coordinator'])
                    final_response = "🔥 **专业版深度分析**\n\n" + result['final_response'] + "\n\n📊 **多智能体协作报告**\n本次分析由" + str(len(result.get('agents_used', []))) + "个专业智能体协作完成，为您提供全方位的专业建议。"
                elif subscription == 'custom':
                    # 自定义版用户：最高级处理 + 专属功能
                    result = await autogen_system.process_with_multi_agents(prompt, ['analyst', 'creative', 'technical', 'product', 'coordinator'])
                    final_response = "💎 **自定义版专属服务**\n\n" + result['final_response'] + "\n\n🎯 **企业级分析报告**\n本次分析采用最高级AI处理流程，由专业智能体团队为您量身定制解决方案。\n\n📞 **专属客服支持**: 如需进一步咨询，请联系您的专属客服。"
                
                # 模拟流式输出效果
                words = final_response.split()
                for i, word in enumerate(words):
                    yield f"data: {json.dumps({'content': word + ' '})}\n\n"
                    await asyncio.sleep(0.03)  # 模拟打字效果
                
                # 免费用户的试用结束提示
                if subscription == 'free':
                    from trial_manager import trial_manager
                    can_continue = trial_manager.increment_trial_chat(user_id)
                    
                    if not trial_manager.can_chat(user_id):
                        # 生成智能推荐
                        recommendations = await autogen_system.get_smart_recommendations([
                            {'role': 'user', 'content': prompt},
                            {'role': 'assistant', 'content': final_response}
                        ])
                        
                        # 发送试用结束提示和推荐
                        upgrade_msg = {
                            'trial_ended': True,
                            'message': '🎉 感谢体验JELILIAN AI PRO！您的免费试用已结束。',
                            'upgrade_info': '升级到付费版本即可享受：',
                            'features': [
                                '基础版 $20/月 - 多智能体协作，4,000积分/月',
                                '专业版 $50/月 - 深度分析，40,000积分/月，50%折扣',
                                '自定义版 - 企业级服务，专属客服，70%折扣',
                                '无限AI对话，优先技术支持'
                            ],
                            'recommendations': recommendations,
                            'upgrade_url': '/upgrade'
                        }
                        yield f"data: {json.dumps(upgrade_msg)}\n\n"
                
                # 付费用户的积分余额提示
                elif subscription in ['basic', 'pro', 'custom']:
                    from credit_manager import credit_manager
                    credit_info = credit_manager.get_user_credits(user_id)
                    
                    # 显示积分使用情况
                    credit_status = {
                        'credit_used': True,
                        'cost': credit_cost,
                        'remaining': credit_info['current_credits'],
                        'plan': subscription,
                        'message': f"💰 本次对话消耗 {credit_cost} 积分，余额 {credit_info['current_credits']} 积分"
                    }
                    yield f"data: {json.dumps(credit_status)}\n\n"
                
                yield f"data: [DONE]\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 用户API路由
@app.post("/api/register")
async def api_register(request: Request):
    try:
        body = await request.json()
        username = body.get("username", "").strip()
        email = body.get("email", "").strip()
        phone = body.get("phone", "").strip()  # 新增手机号字段
        password = body.get("password", "")
        confirm_password = body.get("confirm_password", "")
        
        # 基本验证
        if not username or not email or not password:
            raise HTTPException(status_code=400, detail="用户名、邮箱和密码都是必填的")
        
        if password != confirm_password:
            raise HTTPException(status_code=400, detail="密码和确认密码不匹配")
        
        if len(username) < 3:
            raise HTTPException(status_code=400, detail="用户名至少需要3个字符")
        
        if len(password) < 6:
            raise HTTPException(status_code=400, detail="密码至少需要6个字符")
        
        # 验证邮箱格式
        if '@' not in email or '.' not in email:
            raise HTTPException(status_code=400, detail="请输入有效的邮箱地址")
        
        # 验证手机号格式（如果提供）
        if phone:
            phone = phone.replace(' ', '').replace('-', '')
            if not phone.isdigit() or len(phone) < 10:
                raise HTTPException(status_code=400, detail="请输入有效的手机号")
        
        # 先验证是否有重复
        validation = user_manager.validate_registration(username, email, phone if phone else None)
        if not validation['valid']:
            error_response = {
                "success": False,
                "errors": validation['errors'],
                "suggestions": validation['suggestions']
            }
            return JSONResponse(status_code=400, content=error_response)
        
        # 创建用户
        user_data = user_manager.create_user(username, email, password, phone if phone else None)
        
        return JSONResponse({
            "success": True,
            "message": "注册成功！欢迎使用JELILIAN AI PRO",
            "user": {
                "id": user_data["id"],
                "username": user_data["username"],
                "email": user_data["email"]
            }
        })
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="注册失败，请稍后重试")

@app.post("/api/login")
async def api_login(request: Request):
    try:
        body = await request.json()
        username = body.get("username", "").strip()
        password = body.get("password", "")
        
        if not username or not password:
            raise HTTPException(status_code=400, detail="用户名和密码都是必填的")
        
        # 验证用户
        user_data = user_manager.authenticate_user(username, password)
        if not user_data:
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        
        # 创建会话
        session_id = user_manager.create_session(user_data["id"])
        
        response = JSONResponse({
            "success": True,
            "message": "登录成功",
            "user": {
                "id": user_data["id"],
                "username": user_data["username"],
                "email": user_data["email"],
                "subscription": user_data.get("subscription", "free")
            }
        })
        
        # 设置Cookie
        response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=7*24*60*60,  # 7天
            httponly=True,
            secure=False  # 开发环境设为False
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="登录失败")

@app.get("/api/user")
async def api_get_user(current_user: Optional[Dict] = Depends(get_current_user_from_cookie)):
    if not current_user:
        raise HTTPException(status_code=401, detail="未登录")
    
    return JSONResponse({
        "success": True,
        "user": {
            "id": current_user["id"],
            "username": current_user["username"],
            "email": current_user["email"],
            "subscription": current_user.get("subscription", "free"),
            "trial_used": current_user.get("trial_used", False),
            "chat_count": current_user.get("chat_count", 0)
        }
    })

@app.post("/api/logout")
async def api_logout():
    response = JSONResponse({"success": True, "message": "退出成功"})
    response.delete_cookie("session_id")
    return response

# 个人中心页面
@app.get("/profile", response_class=HTMLResponse)
async def profile_page(current_user: Optional[Dict] = Depends(get_current_user_from_cookie)):
    """个人中心页面"""
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    from trial_manager import trial_manager
    from credit_manager import credit_manager
    
    # 获取用户信息
    trial_info = trial_manager.get_trial_info(current_user['id'])
    credit_info = credit_manager.get_user_credits(current_user['id'])
    
    subscription = current_user.get('subscription', 'free')
    plan_names = {
        'free': '免费版',
        'basic': '基础版 ($20/月)',
        'pro': '专业版 ($50/月)',
        'custom': '自定义版'
    }
    plan_name = plan_names.get(subscription, subscription)
    
    # 试用状态
    if subscription == 'free':
        trial_check = trial_manager.can_use_trial(
            current_user['id'],
            current_user.get('username'),
            current_user.get('email'),
            current_user.get('phone')
        )
        if trial_check['can_use']:
            trial_status = '<span style="color: #27ae60;">🎁 可使用免费试用</span>'
        else:
            days_left = trial_manager.get_days_until_next_trial(current_user['id'])
            trial_status = f'<span style="color: #e74c3c;">⚠️ 本月试用已用完，{days_left}天后可再次试用</span>'
    else:
        trial_status = '<span style="color: #27ae60;">✅ 付费用户，无需试用</span>'
    
    # 积分信息
    if credit_info:
        credits_html = f'''
        <div class="info-card">
            <h3>💰 积分信息</h3>
            <div class="info-row"><span>当前积分:</span><strong>{credit_info.get('current_credits', 0):,}</strong></div>
            <div class="info-row"><span>月度积分:</span><strong>{credit_info.get('monthly_credits', 0):,}</strong></div>
            <div class="info-row"><span>已使用积分:</span><strong>{credit_info.get('used_credits', 0):,}</strong></div>
            <div class="info-row"><span>每日刷新:</span><strong>{credit_info.get('daily_refresh', 0)}</strong></div>
            <div class="info-row"><span>积分折扣:</span><strong>{credit_info.get('credit_discount', 0)}%</strong></div>
            <div class="info-row"><span>并发任务:</span><strong>{credit_info.get('concurrent_tasks', 0)}</strong></div>
            <div class="info-row"><span>定时任务:</span><strong>{credit_info.get('scheduled_tasks', 0)}</strong></div>
            <div class="info-row"><span>智能体协作:</span><strong>{credit_info.get('agent_collaboration', 0)}</strong></div>
        </div>
        '''
    else:
        credits_html = '<div class="info-card"><h3>💰 积分信息</h3><p>升级付费版本后可查看积分信息</p></div>'
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>个人中心 - JELILIAN AI PRO</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Microsoft YaHei', Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ 
            background: white; 
            border-radius: 20px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
            max-width: 800px;
            margin: 0 auto;
        }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .header h1 {{ 
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2em;
            margin-bottom: 10px;
        }}
        .back-btn {{
            background: transparent;
            color: #667eea;
            border: 2px solid #667eea;
            padding: 10px 20px;
            border-radius: 20px;
            text-decoration: none;
            display: inline-block;
            margin-bottom: 20px;
            transition: all 0.3s;
        }}
        .back-btn:hover {{ background: #667eea; color: white; }}
        .info-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .info-card {{
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
        }}
        .info-card h3 {{
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        .info-row {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #e1e5e9;
        }}
        .info-row:last-child {{ border-bottom: none; }}
        .info-row span {{ color: #666; }}
        .info-row strong {{ color: #333; }}
        .subscription-badge {{
            display: inline-block;
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .subscription-free {{ background: #e1e5e9; color: #666; }}
        .subscription-basic {{ background: #667eea; color: white; }}
        .subscription-pro {{ background: linear-gradient(45deg, #667eea, #764ba2); color: white; }}
        .subscription-custom {{ background: #27ae60; color: white; }}
        .btn {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            text-decoration: none;
            display: inline-block;
            margin: 5px;
            transition: all 0.3s;
        }}
        .btn:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4); }}
        .btn.secondary {{ background: transparent; color: #667eea; border: 2px solid #667eea; }}
        .actions {{ text-align: center; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-btn">← 返回首页</a>
        
        <div class="header">
            <h1>👤 个人中心</h1>
            <p>管理您的账户信息</p>
        </div>
        
        <div class="info-grid">
            <div class="info-card">
                <h3>📋 基本信息</h3>
                <div class="info-row"><span>用户名:</span><strong>{current_user.get('username', '-')}</strong></div>
                <div class="info-row"><span>邮箱:</span><strong>{current_user.get('email', '-')}</strong></div>
                <div class="info-row"><span>手机号:</span><strong>{current_user.get('phone', '未绑定')}</strong></div>
                <div class="info-row"><span>注册时间:</span><strong>{current_user.get('created_at', '-')[:10] if current_user.get('created_at') else '-'}</strong></div>
                <div class="info-row"><span>对话次数:</span><strong>{current_user.get('chat_count', 0)}</strong></div>
            </div>
            
            <div class="info-card">
                <h3>💎 订阅状态</h3>
                <div style="text-align: center; margin: 20px 0;">
                    <span class="subscription-badge subscription-{subscription}">{plan_name}</span>
                </div>
                <div class="info-row"><span>试用状态:</span>{trial_status}</div>
                <div style="text-align: center; margin-top: 20px;">
                    <a href="/upgrade" class="btn">💎 升级订阅</a>
                </div>
            </div>
            
            {credits_html}
        </div>
        
        <div class="actions">
            <a href="/" class="btn">🏠 返回首页</a>
            <a href="/upgrade" class="btn">💎 升级Pro</a>
            <a href="/logout" class="btn secondary">🚪 退出登录</a>
        </div>
    </div>
</body>
</html>'''

# 管理员页面 - 查看所有用户信息
@app.get("/admin", response_class=HTMLResponse)
async def admin_page(current_user: Optional[Dict] = Depends(get_current_user_from_cookie)):
    """管理员页面 - 查看用户信息"""
    # 简单的管理员验证（可以根据需要修改）
    admin_users = ['18501935068', 'admin']
    
    if not current_user or current_user.get('username') not in admin_users:
        return HTMLResponse(content='''
        <!DOCTYPE html>
        <html><head><title>访问被拒绝</title></head>
        <body style="display:flex;justify-content:center;align-items:center;height:100vh;font-family:Arial;">
            <div style="text-align:center;">
                <h1>🚫 访问被拒绝</h1>
                <p>您没有权限访问此页面</p>
                <a href="/" style="color:#667eea;">返回首页</a>
            </div>
        </body></html>
        ''', status_code=403)
    
    from trial_manager import trial_manager
    from credit_manager import credit_manager
    
    # 获取所有用户
    users_html = ""
    for user_id, user_data in user_manager.users.items():
        subscription = user_data.get('subscription', 'free')
        credit_info = credit_manager.get_user_credits(user_id)
        trial_info = trial_manager.get_trial_info(user_id)
        
        credits = credit_info.get('current_credits', 0) if credit_info else 0
        trial_used = '是' if trial_info and trial_info.get('used') else '否'
        
        users_html += f'''
        <tr>
            <td>{user_data.get('username', '-')}</td>
            <td>{user_data.get('email', '-')}</td>
            <td>{user_data.get('phone', '-')}</td>
            <td><span class="badge badge-{subscription}">{subscription}</span></td>
            <td>{credits:,}</td>
            <td>{trial_used}</td>
            <td>{user_data.get('chat_count', 0)}</td>
            <td>{user_data.get('created_at', '-')[:10] if user_data.get('created_at') else '-'}</td>
            <td>{user_data.get('last_login', '-')[:10] if user_data.get('last_login') else '从未'}</td>
        </tr>
        '''
    
    # 获取统计信息
    user_stats = user_manager.get_user_stats()
    trial_stats = trial_manager.get_trial_stats()
    credit_stats = credit_manager.get_credit_stats()
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>管理后台 - JELILIAN AI PRO</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Microsoft YaHei', Arial, sans-serif; 
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ 
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header h1 {{ font-size: 1.8em; }}
        .stats-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }}
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .stat-card h3 {{ color: #667eea; font-size: 2em; margin-bottom: 10px; }}
        .stat-card p {{ color: #666; }}
        .table-container {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            overflow-x: auto;
        }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e1e5e9; }}
        th {{ background: #f8f9fa; color: #333; font-weight: bold; }}
        tr:hover {{ background: #f8f9fa; }}
        .badge {{
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        .badge-free {{ background: #e1e5e9; color: #666; }}
        .badge-basic {{ background: #667eea; color: white; }}
        .badge-pro {{ background: #764ba2; color: white; }}
        .badge-custom {{ background: #27ae60; color: white; }}
        .btn {{
            background: white;
            color: #667eea;
            padding: 10px 20px;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            text-decoration: none;
            font-weight: bold;
        }}
        .btn:hover {{ background: rgba(255,255,255,0.9); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>🔧 管理后台</h1>
                <p>欢迎，{current_user.get('username')}！</p>
            </div>
            <div>
                <a href="/" class="btn">🏠 返回首页</a>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>{user_stats.get('total_users', 0)}</h3>
                <p>总用户数</p>
            </div>
            <div class="stat-card">
                <h3>{user_stats.get('paid_users', 0)}</h3>
                <p>付费用户</p>
            </div>
            <div class="stat-card">
                <h3>{trial_stats.get('this_month_trials', 0)}</h3>
                <p>本月试用</p>
            </div>
            <div class="stat-card">
                <h3>{credit_stats.get('total_credits_used', 0):,}</h3>
                <p>总积分消耗</p>
            </div>
        </div>
        
        <div class="table-container">
            <h2 style="margin-bottom: 20px; color: #333;">👥 用户列表</h2>
            <table>
                <thead>
                    <tr>
                        <th>用户名</th>
                        <th>邮箱</th>
                        <th>手机号</th>
                        <th>订阅</th>
                        <th>积分</th>
                        <th>试用</th>
                        <th>对话数</th>
                        <th>注册时间</th>
                        <th>最后登录</th>
                    </tr>
                </thead>
                <tbody>
                    {users_html if users_html else '<tr><td colspan="9" style="text-align:center;color:#666;">暂无用户数据</td></tr>'}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>'''

# API: 获取所有用户（管理员用）
@app.get("/api/admin/users")
async def api_admin_users(current_user: Optional[Dict] = Depends(get_current_user_from_cookie)):
    """获取所有用户信息（管理员API）"""
    admin_users = ['18501935068', 'admin']
    
    if not current_user or current_user.get('username') not in admin_users:
        return JSONResponse(status_code=403, content={"error": "无权限访问"})
    
    from credit_manager import credit_manager
    from trial_manager import trial_manager
    
    users_list = []
    for user_id, user_data in user_manager.users.items():
        credit_info = credit_manager.get_user_credits(user_id)
        trial_info = trial_manager.get_trial_info(user_id)
        
        users_list.append({
            "id": user_id,
            "username": user_data.get('username'),
            "email": user_data.get('email'),
            "phone": user_data.get('phone'),
            "subscription": user_data.get('subscription', 'free'),
            "credits": credit_info.get('current_credits', 0) if credit_info else 0,
            "trial_used": trial_info.get('used', False) if trial_info else False,
            "chat_count": user_data.get('chat_count', 0),
            "created_at": user_data.get('created_at'),
            "last_login": user_data.get('last_login')
        })
    
    return JSONResponse({
        "success": True,
        "users": users_list,
        "total": len(users_list)
    })

@app.get("/upgrade", response_class=HTMLResponse)
async def upgrade_page(current_user: Optional[Dict] = Depends(get_current_user_from_cookie)):
    """升级页面"""
    user_info = ""
    if current_user:
        from trial_manager import trial_manager
        from credit_manager import credit_manager
        
        trial_info = trial_manager.get_trial_info(current_user['id'])
        credit_info = credit_manager.get_user_credits(current_user['id'])
        
        subscription = current_user.get('subscription', 'free')
        if subscription == 'free':
            if trial_manager.can_use_trial(current_user['id']):
                trial_status = '<span class="trial-available">🎁 试用可用</span>'
            else:
                trial_status = '<span class="trial-used">⚠️ 试用已用完</span>'
        else:
            subscription_name = {
                'basic': '基础版 ($20/月)',
                'pro': '专业版 ($50/月)',
                'custom': '自定义版'
            }.get(subscription, '付费用户')
            
            credits_display = f"{credit_info.get('current_credits', 0):,}" if credit_info else "0"
            trial_status = f'<span class="subscription-active">💎 {subscription_name}</span><span class="credits-info">💰 {credits_display} 积分</span>'
        
        user_info = f'''
        <div class="user-info">
            <span>👋 欢迎，{current_user.get('username')}！</span>
            {trial_status}
            <a href="/logout" class="logout-btn">退出</a>
        </div>
        '''
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>升级Pro - JELILIAN AI PRO</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Microsoft YaHei', Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ 
            background: white; 
            border-radius: 20px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{ 
            text-align: center; 
            margin-bottom: 40px; 
        }}
        .header h1 {{ 
            color: #333; 
            font-size: 2.5em; 
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .user-info {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .trial-available {{
            background: #27ae60;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.9em;
        }}
        .trial-used {{
            background: #e74c3c;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.9em;
        }}
        .subscription-active {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.9em;
            margin-right: 10px;
        }}
        .credits-info {{
            background: #27ae60;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.9em;
        }}
        .logout-btn {{
            color: #e74c3c;
            text-decoration: none;
            font-weight: bold;
        }}
        .pricing-section {{
            margin-bottom: 40px;
        }}
        .billing-toggle {{
            display: flex;
            justify-content: center;
            margin-bottom: 30px;
            background: #f8f9fa;
            border-radius: 25px;
            padding: 5px;
            width: fit-content;
            margin-left: auto;
            margin-right: auto;
        }}
        .billing-option {{
            padding: 10px 20px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: bold;
            color: #667eea;
        }}
        .billing-option.active {{
            background: #667eea;
            color: white;
        }}
        .discount {{
            background: #ff6b6b;
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.8em;
            margin-left: 5px;
        }}
        .price-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }}
        .price-card {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            border: 2px solid #e1e5e9;
            transition: all 0.3s;
            position: relative;
        }}
        .price-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        }}
        .price-card.basic {{
            border-color: #667eea;
        }}
        .price-card.pro {{
            border-color: #764ba2;
            transform: scale(1.05);
        }}
        .price-card.pro::before {{
            content: "推荐";
            position: absolute;
            top: -10px;
            right: 20px;
            background: #ff6b6b;
            color: white;
            padding: 5px 15px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        .price-card.custom {{
            border-color: #27ae60;
        }}
        .plan-name {{
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }}
        .plan-price {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        .plan-subtitle {{
            color: #666;
            margin-bottom: 25px;
        }}
        .plan-features {{
            text-align: left;
            margin-bottom: 30px;
        }}
        .feature {{
            padding: 8px 0;
            color: #555;
            border-bottom: 1px solid #f0f0f0;
        }}
        .feature:last-child {{
            border-bottom: none;
        }}
        .feature::before {{
            content: "✓";
            color: #27ae60;
            font-weight: bold;
            margin-right: 10px;
        }}
        .select-btn {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            width: 100%;
        }}
        .select-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        .select-btn.current {{
            background: #27ae60;
            cursor: not-allowed;
        }}
        .contact-btn {{
            background: transparent;
            color: #667eea;
            border: 2px solid #667eea;
        }}
        .contact-btn:hover {{
            background: #667eea;
            color: white;
        }}
        .features-comparison {{
            background: #f8f9fa;
            padding: 30px;
            border-radius: 15px;
            margin-top: 40px;
        }}
        .features-comparison h3 {{
            text-align: center;
            margin-bottom: 30px;
            color: #333;
        }}
        .comparison-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }}
        .comparison-item {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .comparison-item h4 {{
            color: #667eea;
            margin-bottom: 15px;
        }}
        .comparison-item ul {{
            list-style: none;
            text-align: left;
        }}
        .comparison-item li {{
            padding: 5px 0;
            color: #555;
        }}
        .comparison-item li::before {{
            content: "•";
            color: #667eea;
            margin-right: 10px;
        }}
        .back-btn {{
            background: transparent;
            color: #667eea;
            border: 2px solid #667eea;
            padding: 10px 20px;
            border-radius: 20px;
            text-decoration: none;
            display: inline-block;
            margin-bottom: 20px;
            transition: all 0.3s;
        }}
        .back-btn:hover {{
            background: #667eea;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-btn">← 返回首页</a>
        
        <div class="header">
            <h1>💎 升级 JELILIAN AI PRO</h1>
            <p>选择最适合您的计划，解锁全部功能</p>
        </div>
        
        {user_info}
        
        <div class="pricing-section">
            <div class="billing-toggle">
                <span class="billing-option active" data-billing="monthly">月付</span>
                <span class="billing-option" data-billing="yearly">年付 <span class="discount">节省17%</span></span>
            </div>
            
            <div class="price-grid">
                <div class="price-card basic">
                    <div class="plan-name">基础版</div>
                    <div class="plan-price monthly-price">$20<small>/月</small></div>
                    <div class="plan-price yearly-price" style="display:none">$200<small>/年</small></div>
                    <div class="plan-subtitle">适合个人用户</div>
                    <div class="plan-features">
                        <div class="feature">4,000月度积分</div>
                        <div class="feature">300每日刷新积分</div>
                        <div class="feature">3智能体协作</div>
                        <div class="feature">20个并发任务</div>
                        <div class="feature">20个定时任务</div>
                        <div class="feature">标准AI对话</div>
                        <div class="feature">基础技术支持</div>
                        <div class="feature">Beta功能抢先体验</div>
                    </div>
                    <button class="select-btn" onclick="selectPlan('basic')">选择基础版</button>
                </div>
                
                <div class="price-card pro">
                    <div class="plan-name">专业版</div>
                    <div class="plan-price monthly-price">$50<small>/月</small></div>
                    <div class="plan-price yearly-price" style="display:none">$500<small>/年</small></div>
                    <div class="plan-subtitle">适合专业用户</div>
                    <div class="plan-features">
                        <div class="feature">40,000月度积分</div>
                        <div class="feature">300每日刷新积分</div>
                        <div class="feature">5智能体协作+深度分析</div>
                        <div class="feature">20个并发任务</div>
                        <div class="feature">20个定时任务</div>
                        <div class="feature">50%积分折扣</div>
                        <div class="feature">优先技术支持</div>
                        <div class="feature">Beta功能抢先体验</div>
                    </div>
                    <button class="select-btn" onclick="selectPlan('pro')">选择专业版</button>
                </div>
                
                <div class="price-card custom">
                    <div class="plan-name">自定义版</div>
                    <div class="plan-price">联系客服</div>
                    <div class="plan-subtitle">适合企业用户</div>
                    <div class="plan-features">
                        <div class="feature">8,000+积分/月起</div>
                        <div class="feature">300每日刷新积分</div>
                        <div class="feature">企业级AI服务</div>
                        <div class="feature">无限并发任务</div>
                        <div class="feature">无限定时任务</div>
                        <div class="feature">70%积分折扣</div>
                        <div class="feature">专属客服支持</div>
                        <div class="feature">定制化功能开发</div>
                    </div>
                    <button class="select-btn contact-btn" onclick="contactSupport()">联系客服</button>
                </div>
            </div>
        </div>
        
        <div class="features-comparison">
            <h3>🌟 功能对比</h3>
            <div class="comparison-grid">
                <div class="comparison-item">
                    <h4>🆓 免费试用</h4>
                    <ul>
                        <li>一次性试用</li>
                        <li>基础AI对话</li>
                        <li>标准响应速度</li>
                    </ul>
                </div>
                <div class="comparison-item">
                    <h4>💼 基础版</h4>
                    <ul>
                        <li>多智能体协作</li>
                        <li>月度积分制</li>
                        <li>任务管理功能</li>
                        <li>Beta功能体验</li>
                    </ul>
                </div>
                <div class="comparison-item">
                    <h4>🚀 专业版</h4>
                    <ul>
                        <li>深度分析功能</li>
                        <li>积分使用折扣</li>
                        <li>优先技术支持</li>
                        <li>高级AI模型</li>
                    </ul>
                </div>
                <div class="comparison-item">
                    <h4>💎 自定义版</h4>
                    <ul>
                        <li>企业级定制</li>
                        <li>专属客服</li>
                        <li>无限任务处理</li>
                        <li>API接口调用</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function selectPlan(plan) {{
            const orderId = 'ORDER_' + Date.now() + '_' + plan.toUpperCase();
            
            // 直接跳转到支付页面，不需要确认
            window.location.href = `/payment/${{orderId}}`;
        }}
        
        function contactSupport() {{
            const contact = `📞 JELILIAN AI PRO 客服联系方式：

🔸 微信: 18501935068
🔸 WhatsApp: +8618501935068  
🔸 邮箱: 18501935068@163.com
🔸 PayPal: +8618501935068

💬 请说明您需要的自定义功能和预算，我们将为您量身定制方案！`;
            alert(contact);
        }}
        
        // 月付/年付切换功能
        document.addEventListener('DOMContentLoaded', function() {{
            const billingOptions = document.querySelectorAll('.billing-option');
            const monthlyPrices = document.querySelectorAll('.monthly-price');
            const yearlyPrices = document.querySelectorAll('.yearly-price');
            
            billingOptions.forEach(option => {{
                option.addEventListener('click', function() {{
                    billingOptions.forEach(opt => opt.classList.remove('active'));
                    this.classList.add('active');
                    
                    const billing = this.getAttribute('data-billing');
                    
                    if (billing === 'monthly') {{
                        monthlyPrices.forEach(price => price.style.display = 'block');
                        yearlyPrices.forEach(price => price.style.display = 'none');
                    }} else {{
                        monthlyPrices.forEach(price => price.style.display = 'none');
                        yearlyPrices.forEach(price => price.style.display = 'block');
                    }}
                }});
            }});
        }});
    </script>
</body>
</html>'''

# 导入并注册支付路由
from payment_routes import add_payment_routes
add_payment_routes(app)

# 添加其他必要的路由
@app.get("/login", response_class=HTMLResponse)
async def login_page():
    """登录页面"""
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>登录 - JELILIAN AI PRO</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Microsoft YaHei', Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container { 
            background: white; 
            border-radius: 20px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
            width: 90%;
            max-width: 400px;
        }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { 
            color: #333; 
            font-size: 2em; 
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: bold; color: #333; }
        input { 
            width: 100%; 
            padding: 15px; 
            border: 2px solid #e1e5e9; 
            border-radius: 10px; 
            font-size: 16px; 
            transition: border-color 0.3s;
        }
        input:focus { outline: none; border-color: #667eea; }
        .btn { 
            background: linear-gradient(45deg, #667eea, #764ba2); 
            color: white; 
            padding: 15px 30px; 
            border: none; 
            border-radius: 10px; 
            font-size: 16px; 
            cursor: pointer; 
            transition: transform 0.2s;
            width: 100%;
            margin-top: 15px;
        }
        .btn:hover { transform: translateY(-2px); }
        .links { text-align: center; margin-top: 20px; }
        .links a { color: #667eea; text-decoration: none; margin: 0 10px; }
        .links a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 登录</h1>
            <p>欢迎回来！</p>
        </div>
        
        <form id="loginForm">
            <div class="form-group">
                <label for="username">用户名或邮箱：</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="password">密码：</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit" class="btn">🚀 登录</button>
        </form>
        
        <div class="links">
            <a href="/register">📝 注册账号</a>
            <a href="/">🏠 返回首页</a>
        </div>
    </div>
    
    <script>
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert('登录成功！');
                    window.location.href = '/';
                } else {
                    alert('登录失败：' + data.message);
                }
            } catch (error) {
                alert('登录失败：' + error.message);
            }
        });
    </script>
</body>
</html>'''

@app.get("/register", response_class=HTMLResponse)
async def register_page():
    """注册页面"""
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>注册 - JELILIAN AI PRO</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Microsoft YaHei', Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container { 
            background: white; 
            border-radius: 20px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
            width: 90%;
            max-width: 450px;
        }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { 
            color: #333; 
            font-size: 2em; 
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: bold; color: #333; }
        .optional { color: #999; font-weight: normal; font-size: 0.9em; }
        input { 
            width: 100%; 
            padding: 15px; 
            border: 2px solid #e1e5e9; 
            border-radius: 10px; 
            font-size: 16px; 
            transition: border-color 0.3s;
        }
        input:focus { outline: none; border-color: #667eea; }
        input.error { border-color: #e74c3c; }
        .btn { 
            background: linear-gradient(45deg, #667eea, #764ba2); 
            color: white; 
            padding: 15px 30px; 
            border: none; 
            border-radius: 10px; 
            font-size: 16px; 
            cursor: pointer; 
            transition: transform 0.2s;
            width: 100%;
            margin-top: 15px;
        }
        .btn:hover { transform: translateY(-2px); }
        .btn:disabled { background: #ccc; cursor: not-allowed; transform: none; }
        .links { text-align: center; margin-top: 20px; }
        .links a { color: #667eea; text-decoration: none; margin: 0 10px; }
        .links a:hover { text-decoration: underline; }
        .error-box {
            background: #ffe6e6;
            border: 1px solid #e74c3c;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            display: none;
        }
        .error-box.show { display: block; }
        .error-box h4 { color: #e74c3c; margin-bottom: 10px; }
        .error-box ul { margin-left: 20px; color: #c0392b; }
        .error-box li { margin-bottom: 5px; }
        .suggestions {
            background: #e8f5e9;
            border: 1px solid #27ae60;
            border-radius: 8px;
            padding: 10px;
            margin-top: 10px;
        }
        .suggestions h5 { color: #27ae60; margin-bottom: 8px; }
        .suggestion-btn {
            background: #27ae60;
            color: white;
            border: none;
            padding: 5px 12px;
            border-radius: 15px;
            margin: 3px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }
        .suggestion-btn:hover { background: #219a52; transform: scale(1.05); }
        .success-box {
            background: #e8f5e9;
            border: 1px solid #27ae60;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: center;
            display: none;
        }
        .success-box.show { display: block; }
        .success-box h4 { color: #27ae60; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📝 注册</h1>
            <p>加入JELILIAN AI PRO，开启AI之旅！</p>
        </div>
        
        <div class="error-box" id="errorBox">
            <h4>⚠️ 注册失败</h4>
            <ul id="errorList"></ul>
            <div class="suggestions" id="suggestionsBox" style="display:none;">
                <h5>💡 推荐可用的用户名：</h5>
                <div id="suggestionButtons"></div>
            </div>
        </div>
        
        <div class="success-box" id="successBox">
            <h4>✅ 注册成功！正在跳转到登录页面...</h4>
        </div>
        
        <form id="registerForm">
            <div class="form-group">
                <label for="username">用户名：</label>
                <input type="text" id="username" name="username" required minlength="3" placeholder="请输入用户名（至少3个字符）">
            </div>
            
            <div class="form-group">
                <label for="email">邮箱：</label>
                <input type="email" id="email" name="email" required placeholder="请输入邮箱地址">
            </div>
            
            <div class="form-group">
                <label for="phone">手机号：<span class="optional">（选填）</span></label>
                <input type="tel" id="phone" name="phone" placeholder="请输入手机号（可选）">
            </div>
            
            <div class="form-group">
                <label for="password">密码：</label>
                <input type="password" id="password" name="password" required minlength="6" placeholder="请输入密码（至少6个字符）">
            </div>
            
            <div class="form-group">
                <label for="confirm_password">确认密码：</label>
                <input type="password" id="confirm_password" name="confirm_password" required placeholder="请再次输入密码">
            </div>
            
            <button type="submit" class="btn" id="submitBtn">🚀 注册</button>
        </form>
        
        <div class="links">
            <a href="/login">👤 已有账号？登录</a>
            <a href="/">🏠 返回首页</a>
        </div>
    </div>
    
    <script>
        function showError(errors, suggestions) {
            const errorBox = document.getElementById('errorBox');
            const errorList = document.getElementById('errorList');
            const suggestionsBox = document.getElementById('suggestionsBox');
            const suggestionButtons = document.getElementById('suggestionButtons');
            
            // 清空之前的错误
            errorList.innerHTML = '';
            suggestionButtons.innerHTML = '';
            
            // 显示错误
            errors.forEach(error => {
                const li = document.createElement('li');
                li.textContent = error;
                errorList.appendChild(li);
            });
            
            // 显示推荐用户名
            if (suggestions && suggestions.length > 0) {
                suggestionsBox.style.display = 'block';
                suggestions.forEach(suggestion => {
                    const btn = document.createElement('button');
                    btn.type = 'button';
                    btn.className = 'suggestion-btn';
                    btn.textContent = suggestion;
                    btn.onclick = function() {
                        document.getElementById('username').value = suggestion;
                        errorBox.classList.remove('show');
                    };
                    suggestionButtons.appendChild(btn);
                });
            } else {
                suggestionsBox.style.display = 'none';
            }
            
            errorBox.classList.add('show');
            document.getElementById('successBox').classList.remove('show');
        }
        
        function showSuccess() {
            document.getElementById('errorBox').classList.remove('show');
            document.getElementById('successBox').classList.add('show');
        }
        
        function hideMessages() {
            document.getElementById('errorBox').classList.remove('show');
            document.getElementById('successBox').classList.remove('show');
        }
        
        document.getElementById('registerForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            hideMessages();
            
            const username = document.getElementById('username').value.trim();
            const email = document.getElementById('email').value.trim();
            const phone = document.getElementById('phone').value.trim();
            const password = document.getElementById('password').value;
            const confirm_password = document.getElementById('confirm_password').value;
            
            // 前端验证
            if (password !== confirm_password) {
                showError(['密码和确认密码不匹配！'], []);
                return;
            }
            
            const submitBtn = document.getElementById('submitBtn');
            submitBtn.disabled = true;
            submitBtn.textContent = '注册中...';
            
            try {
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, email, phone, password, confirm_password })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showSuccess();
                    setTimeout(() => {
                        window.location.href = '/login';
                    }, 1500);
                } else {
                    // 处理验证错误
                    if (data.errors) {
                        showError(data.errors, data.suggestions || []);
                    } else if (data.detail) {
                        showError([data.detail], []);
                    } else {
                        showError(['注册失败，请稍后重试'], []);
                    }
                }
            } catch (error) {
                showError(['网络错误，请检查网络连接后重试'], []);
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = '🚀 注册';
            }
        });
    </script>
</body>
</html>'''

@app.get("/logout")
async def logout():
    """退出登录"""
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("session_id")
    return response

@app.get("/test-qr", response_class=HTMLResponse)
async def test_qr_codes():
    """二维码测试页面"""
    with open("test_qr_codes.html", "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)