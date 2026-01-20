#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
支付相关路由
"""

from fastapi import Depends, Cookie, Request
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, Dict

def add_payment_routes(app):
    """添加支付相关路由"""
    
    # 导入用户管理器
    from user_manager import user_manager
    from order_manager import order_manager
    
    def get_current_user_from_cookie(session_id: Optional[str] = Cookie(None)) -> Optional[Dict]:
        """从Cookie获取当前用户"""
        if not session_id:
            return None
        return user_manager.get_user_by_session(session_id)
    
    @app.post("/api/submit-order")
    async def submit_order(request: Request, current_user: Optional[Dict] = Depends(get_current_user_from_cookie)):
        """提交支付订单（待审核）"""
        if not current_user:
            return JSONResponse(status_code=401, content={"success": False, "error": "请先登录"})
        
        body = await request.json()
        plan = body.get("plan", "")
        
        # 验证计划类型
        valid_plans = {'basic': 20, 'pro': 50, 'custom': 0}
        if plan not in valid_plans:
            return JSONResponse(status_code=400, content={
                "success": False, 
                "error": f"无效的订阅计划"
            })
        
        # 检查是否已有待审核订单
        if order_manager.has_pending_order(current_user['id'], plan):
            return JSONResponse(status_code=400, content={
                "success": False,
                "error": "您已有一个待审核的订单，请等待审核完成"
            })
        
        # 创建订单
        order = order_manager.create_order(
            user_id=current_user['id'],
            username=current_user.get('username', ''),
            email=current_user.get('email', ''),
            plan=plan,
            amount=valid_plans[plan],
            currency="USD"
        )
        
        plan_names = {'basic': '基础版 ($20/月)', 'pro': '专业版 ($50/月)', 'custom': '自定义版'}
        
        return JSONResponse({
            "success": True,
            "message": f"订单已提交！请等待管理员审核。",
            "order_id": order["order_id"],
            "plan": plan_names.get(plan, plan),
            "status": "pending",
            "note": "审核通过后将自动开通服务，请保持联系方式畅通。"
        })
    
    @app.get("/api/my-orders")
    async def get_my_orders(current_user: Optional[Dict] = Depends(get_current_user_from_cookie)):
        """获取用户的订单列表"""
        if not current_user:
            return JSONResponse(status_code=401, content={"success": False, "error": "请先登录"})
        
        orders = order_manager.get_user_orders(current_user['id'])
        return JSONResponse({"success": True, "orders": orders})
    
    @app.post("/api/confirm-payment")
    async def confirm_payment(request_data: dict, current_user: Optional[Dict] = Depends(get_current_user_from_cookie)):
        """确认支付并升级用户订阅（保留旧接口兼容）"""
        from credit_manager import credit_manager
        
        if not current_user:
            return JSONResponse(status_code=401, content={"success": False, "error": "请先登录"})
        
        order_id = request_data.get("order_id", "")
        plan = request_data.get("plan", "")
        
        # 从订单号解析计划类型（如果没有直接提供）
        if not plan and "_" in order_id:
            parts = order_id.split("_")
            if len(parts) >= 3:
                plan = parts[-1].lower()
        
        # 验证计划类型
        valid_plans = ['basic', 'pro', 'custom']
        if plan not in valid_plans:
            return JSONResponse(status_code=400, content={
                "success": False, 
                "error": f"无效的订阅计划: {plan}，有效计划: {', '.join(valid_plans)}"
            })
        
        try:
            # 更新用户订阅状态
            user_manager.update_user_subscription(current_user['id'], plan)
            
            # 初始化用户积分
            credit_manager.initialize_user_credits(current_user['id'], plan)
            
            # 获取更新后的积分信息
            credit_info = credit_manager.get_user_credits(current_user['id'])
            
            plan_names = {
                'basic': '基础版 ($20/月)',
                'pro': '专业版 ($50/月)',
                'custom': '自定义版'
            }
            
            return JSONResponse({
                "success": True,
                "message": f"恭喜！您已成功升级到 {plan_names.get(plan, plan)}",
                "plan": plan,
                "credits": {
                    "monthly_credits": credit_info.get('monthly_credits', 0),
                    "current_credits": credit_info.get('current_credits', 0),
                    "daily_refresh": credit_info.get('daily_refresh', 0),
                    "concurrent_tasks": credit_info.get('concurrent_tasks', 0),
                    "scheduled_tasks": credit_info.get('scheduled_tasks', 0)
                }
            })
        except Exception as e:
            return JSONResponse(status_code=500, content={
                "success": False,
                "error": f"升级失败: {str(e)}"
            })
    
    @app.get("/api/subscription-status")
    async def get_subscription_status(current_user: Optional[Dict] = Depends(get_current_user_from_cookie)):
        """获取用户订阅状态"""
        from credit_manager import credit_manager
        
        if not current_user:
            return JSONResponse(status_code=401, content={"success": False, "error": "请先登录"})
        
        credit_info = credit_manager.get_user_credits(current_user['id'])
        subscription = current_user.get('subscription', 'free')
        
        plan_names = {
            'free': '免费版',
            'basic': '基础版 ($20/月)',
            'pro': '专业版 ($50/月)',
            'custom': '自定义版'
        }
        
        return JSONResponse({
            "success": True,
            "subscription": subscription,
            "plan_name": plan_names.get(subscription, subscription),
            "credits": credit_info
        })
    
    @app.get("/payment/{order_id}", response_class=HTMLResponse)
    async def payment_page(order_id: str, current_user: Optional[Dict] = Depends(get_current_user_from_cookie)):
        """支付页面 - 包含联系方式和支付信息"""
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>支付 - JELILIAN AI PRO</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Microsoft YaHei', Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .payment-container {{ 
            background: white; 
            padding: 40px; 
            border-radius: 20px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 900px;
            width: 100%;
        }}
        .payment-header {{ 
            text-align: center; 
            margin-bottom: 40px; 
        }}
        .payment-header h2 {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2em;
            margin-bottom: 10px;
        }}
        .trial-notice {{
            background: linear-gradient(45deg, #ff6b6b, #ffa500);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 30px;
            font-weight: bold;
        }}
        .pricing-info {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .pricing-info h3 {{
            margin-bottom: 25px;
            font-size: 1.5em;
        }}
        .billing-toggle {{
            display: flex;
            justify-content: center;
            margin-bottom: 30px;
            background: rgba(255,255,255,0.2);
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
        }}
        .billing-option.active {{
            background: rgba(255,255,255,0.3);
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
        .price-list {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .price-item {{
            background: rgba(255,255,255,0.95);
            color: #333;
            padding: 25px;
            border-radius: 15px;
            text-align: left;
            transition: all 0.3s;
            border: 2px solid transparent;
        }}
        .price-item:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .price-item.basic {{
            border-color: #667eea;
        }}
        .price-item.pro {{
            border-color: #764ba2;
            position: relative;
        }}
        .price-item.pro::before {{
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
        .price-item.custom {{
            border-color: #27ae60;
        }}
        .plan-header {{
            text-align: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #eee;
        }}
        .plan-header strong {{
            display: block;
            font-size: 1.3em;
            margin-bottom: 10px;
            color: #333;
        }}
        .price {{
            font-size: 1.8em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        .subtitle {{
            color: #666;
            font-size: 0.9em;
        }}
        .plan-features {{
            text-align: left;
        }}
        .feature {{
            padding: 8px 0;
            color: #555;
            font-size: 0.95em;
            border-bottom: 1px solid #f0f0f0;
        }}
        .feature:last-child {{
            border-bottom: none;
        }}
        .trial-info {{
            background: #27ae60;
            color: white;
            padding: 8px 12px;
            border-radius: 15px;
            text-align: center;
            margin-top: 10px;
            font-weight: bold;
            font-size: 0.9em;
        }}
        .payment-section {{
            background: #f8f9fa;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 40px;
            text-align: center;
        }}
        .payment-header {{
            margin-bottom: 30px;
        }}
        .payment-header h3 {{
            color: #333;
            font-size: 2em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .payment-header p {{
            color: #666;
            font-size: 1.1em;
        }}
        .payment-qr-container {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            align-items: center;
            max-width: 800px;
            margin: 0 auto;
        }}
        .qr-display {{
            text-align: center;
        }}
        .payment-qr-code {{
            width: 300px;
            height: 300px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border: 3px solid #667eea;
        }}
        .payment-info {{
            text-align: left;
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .payment-info h4 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.3em;
        }}
        .payment-steps p {{
            margin-bottom: 15px;
            color: #333;
        }}
        .payment-steps ul, .payment-steps ol {{
            margin: 15px 0;
            padding-left: 20px;
        }}
        .payment-steps li {{
            margin-bottom: 8px;
            color: #555;
        }}
        .payment-steps strong {{
            color: #667eea;
        }}
        @media (max-width: 768px) {{
            .payment-qr-container {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}
            .payment-qr-code {{
                width: 250px;
                height: 250px;
            }}
        }}
        .contact-info {{
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
            margin-top: 30px;
        }}
        .contact-info h3 {{
            color: #333;
            margin-bottom: 20px;
            text-align: center;
            font-size: 1.2em;
        }}
        .contact-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .contact-item {{
            background: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid #e1e5e9;
            transition: all 0.3s;
        }}
        .contact-item:hover {{
            border-color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
        }}
        .contact-item strong {{
            color: #667eea;
            display: block;
            margin-bottom: 8px;
            font-size: 1.1em;
        }}
        .contact-item span {{
            color: #555;
            font-size: 0.9em;
        }}
        .btn {{
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 12px 25px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            margin: 8px;
            font-size: 16px;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
        }}
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        .btn.secondary {{
            background: transparent;
            color: #667eea;
            border: 2px solid #667eea;
        }}
        .button-group {{
            text-align: center;
            margin-top: 30px;
        }}
        .features {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
        }}
        .features h4 {{
            color: #333;
            margin-bottom: 15px;
            text-align: center;
        }}
        .features ul {{
            list-style: none;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }}
        .features li {{
            padding: 8px;
            background: white;
            border-radius: 8px;
            text-align: center;
        }}
        .features li::before {{
            content: "✓";
            color: #667eea;
            font-weight: bold;
            margin-right: 8px;
        }}
    </style>
</head>
<body>
    <div class="payment-container">
        <div class="payment-header">
            <h2>🤖 JELILIAN AI PRO</h2>
            <p>订单号: {order_id}</p>
        </div>
        
        <div class="trial-notice">
            🎁 新用户福利：免费试用一次！试用后升级享受完整功能
        </div>
        
        <div class="pricing-info">
            <h3>💎 订阅价格方案</h3>
            <div class="billing-toggle">
                <span class="billing-option active" data-billing="monthly">月付</span>
                <span class="billing-option" data-billing="yearly">年付 <span class="discount">节省17%</span></span>
            </div>
            <div class="price-list">
                <div class="price-item free">
                    <div class="plan-header">
                        <strong>免费试用</strong>
                        <div class="price">免费</div>
                        <div class="subtitle">一次性试用</div>
                    </div>
                    <div class="plan-features">
                        <div class="feature">✓ 一个月免费试用一次</div>
                        <div class="feature">✓ 基础AI对话功能</div>
                        <div class="feature">✓ 标准输出内容</div>
                    </div>
                </div>
                
                <div class="price-item basic">
                    <div class="plan-header">
                        <strong>基础版</strong>
                        <div class="price monthly-price">$20/月</div>
                        <div class="price yearly-price" style="display:none">$200/年</div>
                        <div class="subtitle">月度用量升级</div>
                    </div>
                    <div class="plan-features">
                        <div class="feature">✓ 4,000月度积分</div>
                        <div class="feature">✓ G300每日刷新积分</div>
                        <div class="feature">✓ 日常任务的深度研究</div>
                        <div class="feature">✓ 专业网站的标准输出</div>
                        <div class="feature">✓ 常规内容的分析型幻灯片</div>
                        <div class="feature">✓ 任务扩展支持</div>
                        <div class="feature">✓ 广泛研究</div>
                        <div class="feature">✓ 抢先体验Beta功能</div>
                        <div class="feature">✓ 20个并发任务</div>
                        <div class="feature">✓ 20个定时任务</div>
                    </div>
                </div>
                
                <div class="price-item pro">
                    <div class="plan-header">
                        <strong>专业版</strong>
                        <div class="price monthly-price">$50/月</div>
                        <div class="price yearly-price" style="display:none">$500/年</div>
                        <div class="subtitle">提升生产力的用量</div>
                    </div>
                    <div class="plan-features">
                        <div class="feature">✓ 40,000月度积分</div>
                        <div class="feature">✓ G300每日刷新积分</div>
                        <div class="feature">✓ 大规模任务的深度研究</div>
                        <div class="feature">✓ 具备数据分析的专业网站</div>
                        <div class="feature">✓ 批量制作的分析型幻灯片</div>
                        <div class="feature">✓ 持续高负荷的广泛研究</div>
                        <div class="feature">✓ 抢先体验Beta功能</div>
                        <div class="feature">✓ 20个并发任务</div>
                        <div class="feature">✓ 20个定时任务</div>
                        <div class="feature">✓ 优先技术支持</div>
                    </div>
                </div>
                
                <div class="price-item custom">
                    <div class="plan-header">
                        <strong>自定义版</strong>
                        <div class="price">联系客服</div>
                        <div class="subtitle">可自定义月度用量</div>
                    </div>
                    <div class="plan-features">
                        <div class="feature">✓ 8,000积分/每月起</div>
                        <div class="feature">✓ G300每日刷新积分</div>
                        <div class="feature">✓ 自定义用量的深度研究</div>
                        <div class="feature">✓ 应对变化需求的专业网站</div>
                        <div class="feature">✓ 稳定创作的分析型幻灯片</div>
                        <div class="feature">✓ 根据您选择计划的广泛研究</div>
                        <div class="feature">✓ 抢先体验Beta功能</div>
                        <div class="feature">✓ 无限并发任务</div>
                        <div class="feature">✓ 无限定时任务</div>
                        <div class="feature">✓ 专属客服支持</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="features">
            <h4>🌟 升级后享受的功能</h4>
            <ul>
                <li>无限AI对话</li>
                <li>代码生成优化</li>
                <li>文档自动生成</li>
                <li>优先响应速度</li>
                <li>24/7客服支持</li>
                <li>API接口调用</li>
                <li>高级模型访问</li>
                <li>批量处理功能</li>
            </ul>
        </div>
        
        <div class="payment-section">
            <div class="payment-header">
                <h3>💰 聚合支付</h3>
                <p>支付宝扫码联系我或转账</p>
            </div>
            
            <div class="payment-qr-container">
                <div class="qr-display">
                    <img src="/assets/qr_codes/alipay_pay.png" alt="支付宝收款码" class="payment-qr-code">
                </div>
                
                <div class="payment-info">
                    <h4>📋 支付说明</h4>
                    <div class="payment-steps">
                        <p><strong>订单号:</strong> {order_id}</p>
                        <p><strong>扫码后可以:</strong></p>
                        <ul>
                            <li>支付宝转账: 18501935068</li>
                            <li>添加微信: 18501935068</li>
                            <li>WhatsApp: +8618501935068</li>
                            <li>邮箱联系: 18501935068@163.com</li>
                        </ul>
                        <p><strong>支付步骤:</strong></p>
                        <ol>
                            <li>扫描上方二维码</li>
                            <li>选择支付宝转账或添加微信</li>
                            <li>备注订单号: {order_id}</li>
                            <li>联系客服确认支付</li>
                        </ol>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="contact-info">
            <h3>📞 多种联系方式</h3>
            <div class="contact-grid">
                <div class="contact-item">
                    <strong>PayPal</strong>
                    <span>+8618501935068</span>
                </div>
                <div class="contact-item">
                    <strong>WhatsApp</strong>
                    <span>+8618501935068</span>
                </div>
                <div class="contact-item">
                    <strong>邮箱</strong>
                    <span>18501935068@163.com</span>
                </div>
                <div class="contact-item">
                    <strong>微信</strong>
                    <span>18501935068</span>
                </div>
            </div>
        </div>
        
        <div class="plan-selection" style="background: #f8f9fa; padding: 25px; border-radius: 15px; margin: 30px 0; text-align: center;">
            <h3 style="color: #333; margin-bottom: 20px;">📋 选择您的订阅计划</h3>
            <select id="planSelect" style="padding: 15px 30px; font-size: 16px; border: 2px solid #667eea; border-radius: 10px; background: white; cursor: pointer; min-width: 300px;">
                <option value="">-- 请选择订阅计划 --</option>
                <option value="basic">基础版 - $20/月 (4,000积分/月)</option>
                <option value="pro">专业版 - $50/月 (40,000积分/月) 【推荐】</option>
                <option value="custom">自定义版 - 联系客服 (8,000+积分/月)</option>
            </select>
            <div id="planDetails" style="margin-top: 20px; display: none;">
                <div id="basicDetails" class="plan-detail" style="display: none; background: white; padding: 20px; border-radius: 10px; border: 2px solid #667eea;">
                    <h4 style="color: #667eea; margin-bottom: 15px;">💼 基础版 - $20/月</h4>
                    <ul style="text-align: left; list-style: none; padding: 0;">
                        <li style="padding: 5px 0;">✓ 4,000 月度积分</li>
                        <li style="padding: 5px 0;">✓ 300 每日刷新积分</li>
                        <li style="padding: 5px 0;">✓ 3 智能体协作</li>
                        <li style="padding: 5px 0;">✓ 20 个并发任务</li>
                        <li style="padding: 5px 0;">✓ 20 个定时任务</li>
                        <li style="padding: 5px 0;">✓ 标准AI对话</li>
                        <li style="padding: 5px 0;">✓ Beta功能抢先体验</li>
                    </ul>
                </div>
                <div id="proDetails" class="plan-detail" style="display: none; background: white; padding: 20px; border-radius: 10px; border: 2px solid #764ba2;">
                    <h4 style="color: #764ba2; margin-bottom: 15px;">🚀 专业版 - $50/月</h4>
                    <ul style="text-align: left; list-style: none; padding: 0;">
                        <li style="padding: 5px 0;">✓ 40,000 月度积分</li>
                        <li style="padding: 5px 0;">✓ 300 每日刷新积分</li>
                        <li style="padding: 5px 0;">✓ 5 智能体协作 + 深度分析</li>
                        <li style="padding: 5px 0;">✓ 20 个并发任务</li>
                        <li style="padding: 5px 0;">✓ 20 个定时任务</li>
                        <li style="padding: 5px 0;">✓ 50% 积分折扣</li>
                        <li style="padding: 5px 0;">✓ 优先技术支持</li>
                        <li style="padding: 5px 0;">✓ Beta功能抢先体验</li>
                    </ul>
                </div>
                <div id="customDetails" class="plan-detail" style="display: none; background: white; padding: 20px; border-radius: 10px; border: 2px solid #27ae60;">
                    <h4 style="color: #27ae60; margin-bottom: 15px;">💎 自定义版 - 联系客服</h4>
                    <ul style="text-align: left; list-style: none; padding: 0;">
                        <li style="padding: 5px 0;">✓ 8,000+ 积分/月起</li>
                        <li style="padding: 5px 0;">✓ 300 每日刷新积分</li>
                        <li style="padding: 5px 0;">✓ 企业级AI服务</li>
                        <li style="padding: 5px 0;">✓ 无限并发任务</li>
                        <li style="padding: 5px 0;">✓ 无限定时任务</li>
                        <li style="padding: 5px 0;">✓ 70% 积分折扣</li>
                        <li style="padding: 5px 0;">✓ 专属客服支持</li>
                        <li style="padding: 5px 0;">✓ 定制化功能开发</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <div class="button-group">
            <button class="btn" onclick="confirmPayment()" id="confirmBtn">📋 提交订单（待审核）</button>
            <button class="btn secondary" onclick="contactSupport()">💬 联系客服</button>
            <a href="/" class="btn secondary">🏠 返回首页</a>
        </div>
        
        <div id="resultMessage" style="display: none; margin-top: 20px; padding: 20px; border-radius: 10px; text-align: center;"></div>
    </div>
    
    <script>
        // 计划选择变化时显示详情
        document.getElementById('planSelect').addEventListener('change', function() {{
            const plan = this.value;
            const planDetails = document.getElementById('planDetails');
            const allDetails = document.querySelectorAll('.plan-detail');
            
            // 隐藏所有详情
            allDetails.forEach(d => d.style.display = 'none');
            
            if (plan) {{
                planDetails.style.display = 'block';
                document.getElementById(plan + 'Details').style.display = 'block';
            }} else {{
                planDetails.style.display = 'none';
            }}
        }});
        
        async function confirmPayment() {{
            const plan = document.getElementById('planSelect').value;
            const orderId = '{order_id}';
            const confirmBtn = document.getElementById('confirmBtn');
            const resultMessage = document.getElementById('resultMessage');
            
            if (!plan) {{
                alert('⚠️ 请先选择您的订阅计划！');
                return;
            }}
            
            // 确认提交订单
            const planNames = {{
                'basic': '基础版 ($20/月)',
                'pro': '专业版 ($50/月)',
                'custom': '自定义版'
            }};
            
            if (!confirm(`确认提交 ${{planNames[plan]}} 订单？\\n\\n支付完成后，管理员将在24小时内审核并开通服务。`)) {{
                return;
            }}
            
            confirmBtn.disabled = true;
            confirmBtn.textContent = '提交中...';
            
            try {{
                const response = await fetch('/api/submit-order', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ plan: plan }})
                }});
                
                const data = await response.json();
                
                if (data.success) {{
                    resultMessage.style.display = 'block';
                    resultMessage.style.background = '#fff3cd';
                    resultMessage.style.border = '2px solid #ffc107';
                    resultMessage.innerHTML = `
                        <h3 style="color: #856404; margin-bottom: 15px;">📋 订单已提交</h3>
                        <p style="margin-bottom: 10px;"><strong>订单号:</strong> ${{data.order_id}}</p>
                        <p style="margin-bottom: 10px;"><strong>订阅计划:</strong> ${{data.plan}}</p>
                        <p style="margin-bottom: 10px;"><strong>状态:</strong> ⏳ 待审核</p>
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin: 15px 0;">
                            <p style="color: #666; font-size: 14px;">
                                📌 请完成支付后联系客服确认：<br>
                                微信/WhatsApp: 18501935068<br>
                                邮箱: 18501935068@163.com<br><br>
                                管理员确认收款后将在24小时内开通服务
                            </p>
                        </div>
                        <p style="margin-top: 15px;"><a href="/" style="color: #667eea; font-weight: bold;">返回首页 →</a></p>
                    `;
                    confirmBtn.textContent = '📋 订单已提交';
                    confirmBtn.style.background = '#ffc107';
                    confirmBtn.style.color = '#333';
                }} else {{
                    resultMessage.style.display = 'block';
                    resultMessage.style.background = '#ffe6e6';
                    resultMessage.style.border = '2px solid #e74c3c';
                    resultMessage.innerHTML = `
                        <h3 style="color: #e74c3c; margin-bottom: 10px;">⚠️ 提交失败</h3>
                        <p>${{data.error || '请联系客服'}}</p>
                    `;
                    confirmBtn.disabled = false;
                    confirmBtn.textContent = '📋 提交订单';
                }}
            }} catch (error) {{
                resultMessage.style.display = 'block';
                resultMessage.style.background = '#ffe6e6';
                resultMessage.style.border = '2px solid #e74c3c';
                resultMessage.innerHTML = `
                    <h3 style="color: #e74c3c; margin-bottom: 10px;">⚠️ 网络错误</h3>
                    <p>请检查网络连接后重试，或联系客服</p>
                `;
                confirmBtn.disabled = false;
                confirmBtn.textContent = '📋 提交订单';
            }}
        }}
        
        function contactSupport() {{
            const contact = `📞 JELILIAN AI PRO 客服联系方式：

🔸 微信: 18501935068
🔸 WhatsApp: +8618501935068  
🔸 邮箱: 18501935068@163.com
🔸 PayPal: +8618501935068

📋 请提供您的订单号: {order_id}

我们将在24小时内回复您的咨询！`;
            alert(contact);
        }}
        
        // 复制联系方式功能
        function copyContact(text) {{
            navigator.clipboard.writeText(text).then(function() {{
                alert('已复制到剪贴板: ' + text);
            }});
        }}
        
        // 月付/年付切换功能
        document.addEventListener('DOMContentLoaded', function() {{
            const billingOptions = document.querySelectorAll('.billing-option');
            const monthlyPrices = document.querySelectorAll('.monthly-price');
            const yearlyPrices = document.querySelectorAll('.yearly-price');
            
            billingOptions.forEach(option => {{
                option.addEventListener('click', function() {{
                    // 移除所有active类
                    billingOptions.forEach(opt => opt.classList.remove('active'));
                    // 添加active类到当前选项
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
    
    # ==================== 管理后台 ====================
    
    @app.get("/admin", response_class=HTMLResponse)
    async def admin_page(key: str = ""):
        """管理后台页面（需要密钥访问）"""
        # 简单的密钥验证
        ADMIN_KEY = "jelilian2026"
        if key != ADMIN_KEY:
            return HTMLResponse("""
            <html>
            <head><title>管理后台 - JELILIAN AI PRO</title></head>
            <body style="font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; background: #f5f5f5;">
                <div style="background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h2>🔐 管理后台</h2>
                    <form method="get">
                        <input type="password" name="key" placeholder="请输入管理密钥" style="padding: 10px; width: 200px; border: 1px solid #ddd; border-radius: 5px;">
                        <button type="submit" style="padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer;">进入</button>
                    </form>
                </div>
            </body>
            </html>
            """)
        
        # 获取订单数据
        pending_orders = order_manager.get_pending_orders()
        all_orders = order_manager.get_all_orders()
        
        # 生成待审核订单HTML
        pending_html = ""
        for order in pending_orders:
            pending_html += f"""
            <tr>
                <td>{order['order_id']}</td>
                <td>{order['username']}<br><small>{order['email']}</small></td>
                <td>{order['plan']}</td>
                <td>${order['amount']}</td>
                <td>{order['created_at'][:19]}</td>
                <td>
                    <button onclick="approveOrder('{order['order_id']}')" style="background: #27ae60; color: white; border: none; padding: 5px 15px; border-radius: 5px; cursor: pointer; margin: 2px;">✅ 通过</button>
                    <button onclick="rejectOrder('{order['order_id']}')" style="background: #e74c3c; color: white; border: none; padding: 5px 15px; border-radius: 5px; cursor: pointer; margin: 2px;">❌ 拒绝</button>
                </td>
            </tr>
            """
        
        if not pending_html:
            pending_html = "<tr><td colspan='6' style='text-align: center; color: #999;'>暂无待审核订单</td></tr>"
        
        # 生成所有订单HTML
        all_orders_html = ""
        for order in reversed(all_orders[-50:]):  # 最近50条
            status_badge = {
                'pending': '<span style="background: #ffc107; color: #333; padding: 2px 8px; border-radius: 10px;">待审核</span>',
                'approved': '<span style="background: #27ae60; color: white; padding: 2px 8px; border-radius: 10px;">已通过</span>',
                'rejected': '<span style="background: #e74c3c; color: white; padding: 2px 8px; border-radius: 10px;">已拒绝</span>'
            }.get(order['status'], order['status'])
            
            all_orders_html += f"""
            <tr>
                <td>{order['order_id']}</td>
                <td>{order['username']}</td>
                <td>{order['plan']}</td>
                <td>${order['amount']}</td>
                <td>{status_badge}</td>
                <td>{order['created_at'][:19]}</td>
            </tr>
            """
        
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>管理后台 - JELILIAN AI PRO</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                h1 {{ color: #333; }}
                .card {{ background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
                th {{ background: #f8f9fa; font-weight: bold; }}
                .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 20px; }}
                .stat-card {{ background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .stat-number {{ font-size: 2em; font-weight: bold; color: #667eea; }}
                .stat-label {{ color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔧 JELILIAN AI PRO 管理后台</h1>
                
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number">{len(pending_orders)}</div>
                        <div class="stat-label">待审核订单</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len([o for o in all_orders if o['status'] == 'approved'])}</div>
                        <div class="stat-label">已通过订单</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len([o for o in all_orders if o['status'] == 'rejected'])}</div>
                        <div class="stat-label">已拒绝订单</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{len(all_orders)}</div>
                        <div class="stat-label">总订单数</div>
                    </div>
                </div>
                
                <div class="card">
                    <h2>⏳ 待审核订单</h2>
                    <table>
                        <tr>
                            <th>订单号</th>
                            <th>用户</th>
                            <th>计划</th>
                            <th>金额</th>
                            <th>提交时间</th>
                            <th>操作</th>
                        </tr>
                        {pending_html}
                    </table>
                </div>
                
                <div class="card">
                    <h2>📋 所有订单（最近50条）</h2>
                    <table>
                        <tr>
                            <th>订单号</th>
                            <th>用户</th>
                            <th>计划</th>
                            <th>金额</th>
                            <th>状态</th>
                            <th>时间</th>
                        </tr>
                        {all_orders_html}
                    </table>
                </div>
            </div>
            
            <script>
                async function approveOrder(orderId) {{
                    if (!confirm('确认通过此订单？用户将立即获得订阅权益。')) return;
                    
                    const response = await fetch('/admin/approve-order', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ order_id: orderId, key: '{ADMIN_KEY}' }})
                    }});
                    
                    const data = await response.json();
                    if (data.success) {{
                        alert('✅ 订单已通过，用户已开通服务！');
                        location.reload();
                    }} else {{
                        alert('❌ 操作失败: ' + data.error);
                    }}
                }}
                
                async function rejectOrder(orderId) {{
                    const reason = prompt('请输入拒绝原因（可选）:');
                    if (reason === null) return;
                    
                    const response = await fetch('/admin/reject-order', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ order_id: orderId, key: '{ADMIN_KEY}', reason: reason }})
                    }});
                    
                    const data = await response.json();
                    if (data.success) {{
                        alert('订单已拒绝');
                        location.reload();
                    }} else {{
                        alert('❌ 操作失败: ' + data.error);
                    }}
                }}
            </script>
        </body>
        </html>
        """)
    
    @app.post("/admin/approve-order")
    async def admin_approve_order(request: Request):
        """审核通过订单"""
        from credit_manager import credit_manager
        
        body = await request.json()
        order_id = body.get("order_id")
        key = body.get("key")
        
        ADMIN_KEY = "jelilian2026"
        if key != ADMIN_KEY:
            return JSONResponse(status_code=403, content={"success": False, "error": "无权限"})
        
        # 获取订单
        order = order_manager.get_order(order_id)
        if not order:
            return JSONResponse({"success": False, "error": "订单不存在"})
        
        if order["status"] != "pending":
            return JSONResponse({"success": False, "error": "订单已处理"})
        
        # 审核通过
        result = order_manager.approve_order(order_id, "admin")
        
        if result["success"]:
            # 更新用户订阅
            user_manager.update_user_subscription(order["user_id"], order["plan"])
            # 初始化积分
            credit_manager.initialize_user_credits(order["user_id"], order["plan"])
            
            return JSONResponse({
                "success": True,
                "message": f"订单 {order_id} 已通过，用户 {order['username']} 已开通 {order['plan']} 服务"
            })
        
        return JSONResponse({"success": False, "error": "操作失败"})
    
    @app.post("/admin/reject-order")
    async def admin_reject_order(request: Request):
        """拒绝订单"""
        body = await request.json()
        order_id = body.get("order_id")
        key = body.get("key")
        reason = body.get("reason", "")
        
        ADMIN_KEY = "jelilian2026"
        if key != ADMIN_KEY:
            return JSONResponse(status_code=403, content={"success": False, "error": "无权限"})
        
        result = order_manager.reject_order(order_id, "admin", reason)
        
        if result["success"]:
            return JSONResponse({"success": True, "message": f"订单 {order_id} 已拒绝"})
        
        return JSONResponse({"success": False, "error": result.get("message", "操作失败")})