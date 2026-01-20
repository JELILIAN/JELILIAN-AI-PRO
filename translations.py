#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JELILIAN AI PRO 多语言翻译系统
支持: 中文(zh), 英文(en), 日文(ja), 韩文(ko), 西班牙文(es), 法文(fr), 德文(de)
"""

TRANSLATIONS = {
    # 通用
    "app_name": {
        "zh": "JELILIAN AI PRO",
        "en": "JELILIAN AI PRO",
        "ja": "JELILIAN AI PRO",
        "ko": "JELILIAN AI PRO",
        "es": "JELILIAN AI PRO",
        "fr": "JELILIAN AI PRO",
        "de": "JELILIAN AI PRO"
    },
    "app_subtitle": {
        "zh": "智能AI助手",
        "en": "Intelligent AI Assistant",
        "ja": "インテリジェントAIアシスタント",
        "ko": "지능형 AI 어시스턴트",
        "es": "Asistente de IA Inteligente",
        "fr": "Assistant IA Intelligent",
        "de": "Intelligenter KI-Assistent"
    },
    
    # 导航
    "home": {
        "zh": "首页",
        "en": "Home",
        "ja": "ホーム",
        "ko": "홈",
        "es": "Inicio",
        "fr": "Accueil",
        "de": "Startseite"
    },
    "login": {
        "zh": "登录",
        "en": "Login",
        "ja": "ログイン",
        "ko": "로그인",
        "es": "Iniciar sesión",
        "fr": "Connexion",
        "de": "Anmelden"
    },
    "register": {
        "zh": "注册",
        "en": "Register",
        "ja": "登録",
        "ko": "회원가입",
        "es": "Registrarse",
        "fr": "S'inscrire",
        "de": "Registrieren"
    },
    "logout": {
        "zh": "退出",
        "en": "Logout",
        "ja": "ログアウト",
        "ko": "로그아웃",
        "es": "Cerrar sesión",
        "fr": "Déconnexion",
        "de": "Abmelden"
    },
    "upgrade": {
        "zh": "升级Pro",
        "en": "Upgrade Pro",
        "ja": "Proにアップグレード",
        "ko": "Pro 업그레이드",
        "es": "Actualizar a Pro",
        "fr": "Passer à Pro",
        "de": "Auf Pro upgraden"
    },
    "profile": {
        "zh": "个人中心",
        "en": "Profile",
        "ja": "マイページ",
        "ko": "마이페이지",
        "es": "Mi perfil",
        "fr": "Mon profil",
        "de": "Mein Profil"
    },
    
    # 欢迎消息
    "welcome": {
        "zh": "欢迎",
        "en": "Welcome",
        "ja": "ようこそ",
        "ko": "환영합니다",
        "es": "Bienvenido",
        "fr": "Bienvenue",
        "de": "Willkommen"
    },
    "welcome_message": {
        "zh": "您好！我是JELILIAN AI PRO，基于千问大模型的智能助手。请问有什么可以帮助您的吗？",
        "en": "Hello! I'm JELILIAN AI PRO, an intelligent assistant powered by Qwen. How can I help you today?",
        "ja": "こんにちは！私はJELILIAN AI PROです。Qwenを搭載したインテリジェントアシスタントです。何かお手伝いできることはありますか？",
        "ko": "안녕하세요! 저는 Qwen 기반의 지능형 어시스턴트 JELILIAN AI PRO입니다. 무엇을 도와드릴까요?",
        "es": "¡Hola! Soy JELILIAN AI PRO, un asistente inteligente impulsado por Qwen. ¿En qué puedo ayudarte hoy?",
        "fr": "Bonjour ! Je suis JELILIAN AI PRO, un assistant intelligent propulsé par Qwen. Comment puis-je vous aider aujourd'hui ?",
        "de": "Hallo! Ich bin JELILIAN AI PRO, ein intelligenter Assistent powered by Qwen. Wie kann ich Ihnen heute helfen?"
    },
    
    # 试用相关
    "free_trial": {
        "zh": "免费试用",
        "en": "Free Trial",
        "ja": "無料トライアル",
        "ko": "무료 체험",
        "es": "Prueba gratuita",
        "fr": "Essai gratuit",
        "de": "Kostenlose Testversion"
    },
    "trial_notice": {
        "zh": "🎁 新用户福利：免费试用一次！试用后升级享受完整功能",
        "en": "🎁 New user benefit: One free trial! Upgrade after trial for full features",
        "ja": "🎁 新規ユーザー特典：1回無料トライアル！トライアル後にアップグレードで全機能を利用可能",
        "ko": "🎁 신규 사용자 혜택: 1회 무료 체험! 체험 후 업그레이드하여 전체 기능 이용",
        "es": "🎁 Beneficio para nuevos usuarios: ¡Una prueba gratuita! Actualiza después de la prueba para todas las funciones",
        "fr": "🎁 Avantage nouveaux utilisateurs : Un essai gratuit ! Passez à la version supérieure après l'essai pour toutes les fonctionnalités",
        "de": "🎁 Vorteil für neue Benutzer: Eine kostenlose Testversion! Nach dem Test upgraden für alle Funktionen"
    },
    "trial_available": {
        "zh": "🎁 试用可用",
        "en": "🎁 Trial Available",
        "ja": "🎁 トライアル利用可能",
        "ko": "🎁 체험 가능",
        "es": "🎁 Prueba disponible",
        "fr": "🎁 Essai disponible",
        "de": "🎁 Testversion verfügbar"
    },
    "trial_used": {
        "zh": "⚠️ 试用已用完",
        "en": "⚠️ Trial Used",
        "ja": "⚠️ トライアル使用済み",
        "ko": "⚠️ 체험 사용됨",
        "es": "⚠️ Prueba utilizada",
        "fr": "⚠️ Essai utilisé",
        "de": "⚠️ Testversion verwendet"
    },
    
    # 聊天相关
    "input_placeholder": {
        "zh": "请输入您的问题或需求...",
        "en": "Enter your question or request...",
        "ja": "質問やリクエストを入力してください...",
        "ko": "질문이나 요청을 입력하세요...",
        "es": "Ingrese su pregunta o solicitud...",
        "fr": "Entrez votre question ou demande...",
        "de": "Geben Sie Ihre Frage oder Anfrage ein..."
    },
    "send_message": {
        "zh": "🚀 发送消息",
        "en": "🚀 Send Message",
        "ja": "🚀 メッセージを送信",
        "ko": "🚀 메시지 보내기",
        "es": "🚀 Enviar mensaje",
        "fr": "🚀 Envoyer le message",
        "de": "🚀 Nachricht senden"
    },
    "ai_thinking": {
        "zh": "🤖 AI正在思考中",
        "en": "🤖 AI is thinking",
        "ja": "🤖 AIが考え中",
        "ko": "🤖 AI가 생각 중",
        "es": "🤖 La IA está pensando",
        "fr": "🤖 L'IA réfléchit",
        "de": "🤖 KI denkt nach"
    },
    
    # 示例问题
    "example_questions": {
        "zh": "💡 示例问题：",
        "en": "💡 Example Questions:",
        "ja": "💡 質問例：",
        "ko": "💡 예시 질문:",
        "es": "💡 Preguntas de ejemplo:",
        "fr": "💡 Questions exemples :",
        "de": "💡 Beispielfragen:"
    },
    "example_coding": {
        "zh": "编程助手",
        "en": "Coding Assistant",
        "ja": "コーディングアシスタント",
        "ko": "코딩 어시스턴트",
        "es": "Asistente de programación",
        "fr": "Assistant de programmation",
        "de": "Programmierassistent"
    },
    "example_analysis": {
        "zh": "技术分析",
        "en": "Tech Analysis",
        "ja": "技術分析",
        "ko": "기술 분석",
        "es": "Análisis técnico",
        "fr": "Analyse technique",
        "de": "Technische Analyse"
    },
    "example_writing": {
        "zh": "文档写作",
        "en": "Doc Writing",
        "ja": "ドキュメント作成",
        "ko": "문서 작성",
        "es": "Redacción de documentos",
        "fr": "Rédaction de documents",
        "de": "Dokumentenerstellung"
    },
    "example_qa": {
        "zh": "知识问答",
        "en": "Q&A",
        "ja": "Q&A",
        "ko": "Q&A",
        "es": "Preguntas y respuestas",
        "fr": "Questions-réponses",
        "de": "Fragen & Antworten"
    },
    
    # 订阅计划
    "basic_plan": {
        "zh": "基础版",
        "en": "Basic",
        "ja": "ベーシック",
        "ko": "베이직",
        "es": "Básico",
        "fr": "Basique",
        "de": "Basis"
    },
    "pro_plan": {
        "zh": "专业版",
        "en": "Professional",
        "ja": "プロフェッショナル",
        "ko": "프로페셔널",
        "es": "Profesional",
        "fr": "Professionnel",
        "de": "Professionell"
    },
    "custom_plan": {
        "zh": "自定义版",
        "en": "Custom",
        "ja": "カスタム",
        "ko": "커스텀",
        "es": "Personalizado",
        "fr": "Personnalisé",
        "de": "Benutzerdefiniert"
    },
    "monthly_credits": {
        "zh": "月度积分",
        "en": "Monthly Credits",
        "ja": "月間クレジット",
        "ko": "월간 크레딧",
        "es": "Créditos mensuales",
        "fr": "Crédits mensuels",
        "de": "Monatliche Credits"
    },
    "daily_refresh": {
        "zh": "每日刷新积分",
        "en": "Daily Refresh Credits",
        "ja": "毎日リフレッシュクレジット",
        "ko": "일일 새로고침 크레딧",
        "es": "Créditos de actualización diaria",
        "fr": "Crédits de rafraîchissement quotidien",
        "de": "Tägliche Auffrischungs-Credits"
    },
    "concurrent_tasks": {
        "zh": "并发任务",
        "en": "Concurrent Tasks",
        "ja": "同時タスク",
        "ko": "동시 작업",
        "es": "Tareas concurrentes",
        "fr": "Tâches simultanées",
        "de": "Gleichzeitige Aufgaben"
    },
    "contact_support": {
        "zh": "联系客服",
        "en": "Contact Support",
        "ja": "サポートに連絡",
        "ko": "고객 지원 문의",
        "es": "Contactar soporte",
        "fr": "Contacter le support",
        "de": "Support kontaktieren"
    },
    
    # 登录注册
    "username": {
        "zh": "用户名",
        "en": "Username",
        "ja": "ユーザー名",
        "ko": "사용자 이름",
        "es": "Nombre de usuario",
        "fr": "Nom d'utilisateur",
        "de": "Benutzername"
    },
    "email": {
        "zh": "邮箱",
        "en": "Email",
        "ja": "メールアドレス",
        "ko": "이메일",
        "es": "Correo electrónico",
        "fr": "E-mail",
        "de": "E-Mail"
    },
    "phone": {
        "zh": "手机号",
        "en": "Phone",
        "ja": "電話番号",
        "ko": "전화번호",
        "es": "Teléfono",
        "fr": "Téléphone",
        "de": "Telefon"
    },
    "password": {
        "zh": "密码",
        "en": "Password",
        "ja": "パスワード",
        "ko": "비밀번호",
        "es": "Contraseña",
        "fr": "Mot de passe",
        "de": "Passwort"
    },
    "confirm_password": {
        "zh": "确认密码",
        "en": "Confirm Password",
        "ja": "パスワード確認",
        "ko": "비밀번호 확인",
        "es": "Confirmar contraseña",
        "fr": "Confirmer le mot de passe",
        "de": "Passwort bestätigen"
    },
    "register_success": {
        "zh": "注册成功！欢迎使用JELILIAN AI PRO",
        "en": "Registration successful! Welcome to JELILIAN AI PRO",
        "ja": "登録成功！JELILIAN AI PROへようこそ",
        "ko": "가입 성공! JELILIAN AI PRO에 오신 것을 환영합니다",
        "es": "¡Registro exitoso! Bienvenido a JELILIAN AI PRO",
        "fr": "Inscription réussie ! Bienvenue sur JELILIAN AI PRO",
        "de": "Registrierung erfolgreich! Willkommen bei JELILIAN AI PRO"
    },
    "login_success": {
        "zh": "登录成功",
        "en": "Login successful",
        "ja": "ログイン成功",
        "ko": "로그인 성공",
        "es": "Inicio de sesión exitoso",
        "fr": "Connexion réussie",
        "de": "Anmeldung erfolgreich"
    },
    
    # 支付
    "payment": {
        "zh": "支付",
        "en": "Payment",
        "ja": "お支払い",
        "ko": "결제",
        "es": "Pago",
        "fr": "Paiement",
        "de": "Zahlung"
    },
    "payment_completed": {
        "zh": "我已完成支付",
        "en": "I have completed payment",
        "ja": "支払いを完了しました",
        "ko": "결제를 완료했습니다",
        "es": "He completado el pago",
        "fr": "J'ai effectué le paiement",
        "de": "Ich habe die Zahlung abgeschlossen"
    },
    "select_plan": {
        "zh": "选择您的订阅计划",
        "en": "Select your subscription plan",
        "ja": "サブスクリプションプランを選択",
        "ko": "구독 플랜 선택",
        "es": "Seleccione su plan de suscripción",
        "fr": "Sélectionnez votre plan d'abonnement",
        "de": "Wählen Sie Ihren Abonnementplan"
    },
    
    # 错误消息
    "error_login_required": {
        "zh": "请先登录",
        "en": "Please login first",
        "ja": "まずログインしてください",
        "ko": "먼저 로그인하세요",
        "es": "Por favor inicie sesión primero",
        "fr": "Veuillez d'abord vous connecter",
        "de": "Bitte melden Sie sich zuerst an"
    },
    "error_trial_used": {
        "zh": "本月试用已用完，请升级付费版本",
        "en": "Monthly trial used, please upgrade to paid version",
        "ja": "今月のトライアルは使用済みです。有料版にアップグレードしてください",
        "ko": "이번 달 체험이 사용되었습니다. 유료 버전으로 업그레이드하세요",
        "es": "Prueba mensual utilizada, actualice a la versión de pago",
        "fr": "Essai mensuel utilisé, veuillez passer à la version payante",
        "de": "Monatliche Testversion verwendet, bitte auf kostenpflichtige Version upgraden"
    },
    
    # 语言选择
    "language": {
        "zh": "语言",
        "en": "Language",
        "ja": "言語",
        "ko": "언어",
        "es": "Idioma",
        "fr": "Langue",
        "de": "Sprache"
    },
    "chinese": {
        "zh": "中文",
        "en": "Chinese",
        "ja": "中国語",
        "ko": "중국어",
        "es": "Chino",
        "fr": "Chinois",
        "de": "Chinesisch"
    },
    "english": {
        "zh": "英文",
        "en": "English",
        "ja": "英語",
        "ko": "영어",
        "es": "Inglés",
        "fr": "Anglais",
        "de": "Englisch"
    },
    "japanese": {
        "zh": "日文",
        "en": "Japanese",
        "ja": "日本語",
        "ko": "일본어",
        "es": "Japonés",
        "fr": "Japonais",
        "de": "Japanisch"
    },
    "korean": {
        "zh": "韩文",
        "en": "Korean",
        "ja": "韓国語",
        "ko": "한국어",
        "es": "Coreano",
        "fr": "Coréen",
        "de": "Koreanisch"
    }
}

def get_text(key: str, lang: str = "zh") -> str:
    """获取翻译文本"""
    if key in TRANSLATIONS:
        return TRANSLATIONS[key].get(lang, TRANSLATIONS[key].get("en", key))
    return key

def get_all_translations(lang: str = "zh") -> dict:
    """获取指定语言的所有翻译"""
    result = {}
    for key, translations in TRANSLATIONS.items():
        result[key] = translations.get(lang, translations.get("en", key))
    return result

SUPPORTED_LANGUAGES = {
    "zh": "中文",
    "en": "English",
    "ja": "日本語",
    "ko": "한국어",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch"
}
