#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户管理系统
"""

import json
import os
import hashlib
import uuid
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, List

class UserManager:
    def __init__(self, users_file="users.json", sessions_file="sessions.json"):
        self.users_file = users_file
        self.sessions_file = sessions_file
        self.users = {}
        self.sessions = {}
        self.load_data()
    
    def load_data(self):
        """加载用户数据"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
            
            if os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    self.sessions = json.load(f)
        except Exception as e:
            print(f"加载数据失败: {e}")
    
    def save_data(self):
        """保存用户数据"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
            
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(self.sessions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存数据失败: {e}")
    
    def hash_password(self, password: str) -> str:
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def check_username_exists(self, username: str) -> bool:
        """检查用户名是否已存在"""
        for user_data in self.users.values():
            if user_data.get('username', '').lower() == username.lower():
                return True
        return False
    
    def check_email_exists(self, email: str) -> bool:
        """检查邮箱是否已存在"""
        for user_data in self.users.values():
            if user_data.get('email', '').lower() == email.lower():
                return True
        return False
    
    def check_phone_exists(self, phone: str) -> bool:
        """检查手机号是否已存在"""
        if not phone:
            return False
        # 标准化手机号（去除空格和横线）
        normalized_phone = phone.replace(' ', '').replace('-', '')
        for user_data in self.users.values():
            user_phone = user_data.get('phone', '')
            if user_phone:
                normalized_user_phone = user_phone.replace(' ', '').replace('-', '')
                if normalized_user_phone == normalized_phone:
                    return True
        return False
    
    def suggest_usernames(self, base_username: str, count: int = 3) -> List[str]:
        """推荐可用的用户名"""
        suggestions = []
        
        # 策略1: 添加数字后缀
        for i in range(1, 100):
            candidate = f"{base_username}{i}"
            if not self.check_username_exists(candidate):
                suggestions.append(candidate)
                if len(suggestions) >= count:
                    return suggestions
        
        # 策略2: 添加随机数字
        for _ in range(20):
            random_suffix = random.randint(100, 9999)
            candidate = f"{base_username}{random_suffix}"
            if not self.check_username_exists(candidate) and candidate not in suggestions:
                suggestions.append(candidate)
                if len(suggestions) >= count:
                    return suggestions
        
        # 策略3: 添加下划线和数字
        for i in range(1, 50):
            candidate = f"{base_username}_{i}"
            if not self.check_username_exists(candidate) and candidate not in suggestions:
                suggestions.append(candidate)
                if len(suggestions) >= count:
                    return suggestions
        
        return suggestions
    
    def validate_registration(self, username: str, email: str, phone: str = None) -> Dict:
        """
        验证注册信息，返回验证结果
        返回: {
            'valid': bool,
            'errors': list,
            'suggestions': list (如果用户名被占用)
        }
        """
        errors = []
        suggestions = []
        
        # 检查用户名
        if self.check_username_exists(username):
            errors.append(f"用户名 '{username}' 已被占用")
            suggestions = self.suggest_usernames(username)
        
        # 检查邮箱
        if self.check_email_exists(email):
            errors.append(f"邮箱 '{email}' 已被注册，请使用其他邮箱或直接登录")
        
        # 检查手机号
        if phone and self.check_phone_exists(phone):
            errors.append(f"手机号 '{phone}' 已被注册，请使用其他手机号或直接登录")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'suggestions': suggestions
        }
    
    def create_user(self, username: str, email: str, password: str, phone: str = None) -> Dict:
        """创建新用户"""
        # 验证注册信息
        validation = self.validate_registration(username, email, phone)
        if not validation['valid']:
            error_msg = '\n'.join(validation['errors'])
            if validation['suggestions']:
                error_msg += f"\n\n推荐可用的用户名: {', '.join(validation['suggestions'])}"
            raise ValueError(error_msg)
        
        # 创建新用户
        user_id = str(uuid.uuid4())
        user_data = {
            'id': user_id,
            'username': username,
            'email': email,
            'phone': phone,
            'password_hash': self.hash_password(password),
            'created_at': datetime.now().isoformat(),
            'subscription': 'free',
            'trial_used': False,
            'chat_count': 0,
            'last_login': None
        }
        
        self.users[user_id] = user_data
        self.save_data()
        return user_data
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """用户认证"""
        password_hash = self.hash_password(password)
        
        for user_data in self.users.values():
            if (user_data.get('username') == username or user_data.get('email') == username) and \
               user_data.get('password_hash') == password_hash:
                # 更新最后登录时间
                user_data['last_login'] = datetime.now().isoformat()
                self.save_data()
                return user_data
        
        return None
    
    def create_session(self, user_id: str) -> str:
        """创建用户会话"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=7)).isoformat()
        }
        self.save_data()
        return session_id
    
    def get_user_by_session(self, session_id: str) -> Optional[Dict]:
        """通过会话获取用户"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        if datetime.fromisoformat(session['expires_at']) < datetime.now():
            del self.sessions[session_id]
            self.save_data()
            return None
        
        user_id = session['user_id']
        return self.users.get(user_id)
    
    def update_user_subscription(self, user_id: str, subscription: str):
        """更新用户订阅状态"""
        if user_id in self.users:
            self.users[user_id]['subscription'] = subscription
            self.save_data()
            
            # 同时更新积分系统
            try:
                from credit_manager import credit_manager
                credit_manager.upgrade_plan(user_id, subscription)
            except ImportError:
                pass
    
    def increment_chat_count(self, user_id: str):
        """增加用户对话次数"""
        if user_id in self.users:
            self.users[user_id]['chat_count'] = self.users[user_id].get('chat_count', 0) + 1
            self.save_data()
    
    def use_trial(self, user_id: str):
        """使用试用"""
        if user_id in self.users:
            self.users[user_id]['trial_used'] = True
            self.save_data()
    
    def get_user_stats(self) -> Dict:
        """获取用户统计"""
        total_users = len(self.users)
        free_users = sum(1 for user in self.users.values() if user.get('subscription') == 'free')
        paid_users = total_users - free_users
        
        return {
            'total_users': total_users,
            'free_users': free_users,
            'paid_users': paid_users,
            'active_sessions': len(self.sessions)
        }

# 全局用户管理器实例
user_manager = UserManager()