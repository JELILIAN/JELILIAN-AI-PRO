#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
积分管理系统
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

class CreditManager:
    def __init__(self, credits_file="user_credits.json"):
        self.credits_file = credits_file
        self.user_credits = {}
        self.load_data()
    
    def load_data(self):
        """加载积分数据"""
        try:
            if os.path.exists(self.credits_file):
                with open(self.credits_file, 'r', encoding='utf-8') as f:
                    self.user_credits = json.load(f)
        except Exception as e:
            print(f"加载积分数据失败: {e}")
    
    def save_data(self):
        """保存积分数据"""
        try:
            with open(self.credits_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_credits, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存积分数据失败: {e}")
    
    def initialize_user_credits(self, user_id: str, plan: str):
        """初始化用户积分"""
        credit_plans = {
            'free': {
                'monthly_credits': 0,
                'daily_refresh': 0,
                'concurrent_tasks': 1,
                'scheduled_tasks': 0,
                'agent_collaboration': 0,
                'credit_discount': 0
            },
            'basic': {
                'monthly_credits': 4000,
                'daily_refresh': 300,
                'concurrent_tasks': 20,
                'scheduled_tasks': 20,
                'agent_collaboration': 3,
                'credit_discount': 0
            },
            'pro': {
                'monthly_credits': 40000,
                'daily_refresh': 300,
                'concurrent_tasks': 20,
                'scheduled_tasks': 20,
                'agent_collaboration': 5,
                'credit_discount': 50  # 50%折扣
            },
            'custom': {
                'monthly_credits': 8000,
                'daily_refresh': 300,
                'concurrent_tasks': 999,  # 无限
                'scheduled_tasks': 999,   # 无限
                'agent_collaboration': 999,
                'credit_discount': 70  # 70%折扣
            }
        }
        
        plan_config = credit_plans.get(plan, credit_plans['free'])
        
        self.user_credits[user_id] = {
            'plan': plan,
            'monthly_credits': plan_config['monthly_credits'],
            'daily_refresh': plan_config['daily_refresh'],
            'concurrent_tasks': plan_config['concurrent_tasks'],
            'scheduled_tasks': plan_config['scheduled_tasks'],
            'agent_collaboration': plan_config['agent_collaboration'],
            'credit_discount': plan_config['credit_discount'],
            'current_credits': plan_config['monthly_credits'],
            'used_credits': 0,
            'last_refresh': datetime.now().isoformat(),
            'created_at': datetime.now().isoformat()
        }
        self.save_data()
    
    def get_user_credits(self, user_id: str) -> Optional[Dict]:
        """获取用户积分信息"""
        if user_id not in self.user_credits:
            self.initialize_user_credits(user_id, 'free')
        
        return self.user_credits.get(user_id)
    
    def use_credits(self, user_id: str, amount: int) -> bool:
        """使用积分（自动应用折扣）"""
        user_credit = self.get_user_credits(user_id)
        if not user_credit:
            return False
        
        # 应用积分折扣
        discount = user_credit.get('credit_discount', 0)
        if discount > 0:
            discounted_amount = int(amount * (100 - discount) / 100)
        else:
            discounted_amount = amount
        
        if user_credit['current_credits'] >= discounted_amount:
            user_credit['current_credits'] -= discounted_amount
            user_credit['used_credits'] += discounted_amount
            self.save_data()
            return True
        
        return False
    
    def calculate_discounted_cost(self, user_id: str, amount: int) -> int:
        """计算折扣后的积分消耗"""
        user_credit = self.get_user_credits(user_id)
        if not user_credit:
            return amount
        
        discount = user_credit.get('credit_discount', 0)
        if discount > 0:
            return int(amount * (100 - discount) / 100)
        return amount
    
    def daily_refresh_credits(self, user_id: str):
        """每日刷新积分"""
        user_credit = self.get_user_credits(user_id)
        if not user_credit:
            return
        
        last_refresh = datetime.fromisoformat(user_credit['last_refresh'])
        now = datetime.now()
        
        # 检查是否需要刷新（超过24小时）
        if now - last_refresh >= timedelta(days=1):
            refresh_amount = user_credit['daily_refresh']
            max_credits = user_credit['monthly_credits']
            
            # 不能超过月度积分上限
            new_credits = min(user_credit['current_credits'] + refresh_amount, max_credits)
            user_credit['current_credits'] = new_credits
            user_credit['last_refresh'] = now.isoformat()
            self.save_data()
    
    def upgrade_plan(self, user_id: str, new_plan: str):
        """升级用户计划"""
        self.initialize_user_credits(user_id, new_plan)
    
    def get_credit_stats(self) -> Dict:
        """获取积分统计"""
        total_users = len(self.user_credits)
        total_credits_used = sum(user.get('used_credits', 0) for user in self.user_credits.values())
        
        plan_distribution = {}
        for user in self.user_credits.values():
            plan = user.get('plan', 'free')
            plan_distribution[plan] = plan_distribution.get(plan, 0) + 1
        
        return {
            'total_users': total_users,
            'total_credits_used': total_credits_used,
            'plan_distribution': plan_distribution
        }

# 全局积分管理器实例
credit_manager = CreditManager()