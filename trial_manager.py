#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
试用管理系统 - 一个月只能试用一次
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, List

class TrialManager:
    def __init__(self, trial_file="trial_records.json"):
        self.trial_file = trial_file
        self.trial_records = {}
        self.load_data()
    
    def load_data(self):
        """加载试用记录"""
        try:
            if os.path.exists(self.trial_file):
                with open(self.trial_file, 'r', encoding='utf-8') as f:
                    self.trial_records = json.load(f)
        except Exception as e:
            print(f"加载试用记录失败: {e}")
    
    def save_data(self):
        """保存试用记录"""
        try:
            with open(self.trial_file, 'w', encoding='utf-8') as f:
                json.dump(self.trial_records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存试用记录失败: {e}")
    
    def _get_month_key(self) -> str:
        """获取当前月份的key，格式：2026-01"""
        return datetime.now().strftime("%Y-%m")
    
    def _check_identifier_used_this_month(self, identifier: str, identifier_type: str) -> bool:
        """检查某个标识符（用户名/邮箱/手机号）本月是否已使用过试用"""
        current_month = self._get_month_key()
        
        for record in self.trial_records.values():
            # 检查是否是本月的记录
            used_at = record.get('used_at', '')
            if used_at:
                try:
                    used_month = datetime.fromisoformat(used_at).strftime("%Y-%m")
                    if used_month != current_month:
                        continue  # 不是本月的记录，跳过
                except:
                    continue
            
            # 检查标识符是否匹配
            if identifier_type == 'username' and record.get('username', '').lower() == identifier.lower():
                return True
            if identifier_type == 'email' and record.get('email', '').lower() == identifier.lower():
                return True
            if identifier_type == 'phone' and record.get('phone', '') == identifier:
                return True
        
        return False
    
    def can_use_trial(self, user_id: str, username: str = None, email: str = None, phone: str = None) -> Dict:
        """
        检查用户是否可以使用试用
        返回: {'can_use': bool, 'reason': str}
        """
        current_month = self._get_month_key()
        
        # 检查用户ID是否本月已使用
        if user_id in self.trial_records:
            trial_info = self.trial_records[user_id]
            used_at = trial_info.get('used_at', '')
            if used_at:
                try:
                    used_month = datetime.fromisoformat(used_at).strftime("%Y-%m")
                    if used_month == current_month and trial_info.get('used', False):
                        return {'can_use': False, 'reason': '您本月已使用过免费试用，下个月可以再次试用，或升级付费版本继续使用'}
                except:
                    pass
        
        # 检查用户名是否本月已被其他账号使用
        if username and self._check_identifier_used_this_month(username, 'username'):
            return {'can_use': False, 'reason': f'用户名 "{username}" 本月已使用过免费试用'}
        
        # 检查邮箱是否本月已被使用
        if email and self._check_identifier_used_this_month(email, 'email'):
            return {'can_use': False, 'reason': f'邮箱 "{email}" 本月已使用过免费试用'}
        
        # 检查手机号是否本月已被使用
        if phone and self._check_identifier_used_this_month(phone, 'phone'):
            return {'can_use': False, 'reason': f'手机号 "{phone}" 本月已使用过免费试用'}
        
        return {'can_use': True, 'reason': '可以使用免费试用'}
    
    def use_trial(self, user_id: str, username: str = None, email: str = None, phone: str = None) -> Dict:
        """
        使用试用机会 - 严格限制一个月只能试用一次
        返回: {'success': bool, 'message': str}
        """
        # 先检查是否可以使用
        check_result = self.can_use_trial(user_id, username, email, phone)
        if not check_result['can_use']:
            return {'success': False, 'message': check_result['reason']}
        
        self.trial_records[user_id] = {
            'username': username,
            'email': email,
            'phone': phone,
            'used': True,
            'used_at': datetime.now().isoformat(),
            'month': self._get_month_key(),
            'chat_count': 0,
            'max_chats': 1
        }
        self.save_data()
        return {'success': True, 'message': '试用已激活，您有1次免费对话机会'}
    
    def can_chat(self, user_id: str) -> bool:
        """检查用户是否还能继续对话"""
        if user_id not in self.trial_records:
            return True  # 还没使用过试用
        
        trial_info = self.trial_records[user_id]
        if not trial_info.get('used', False):
            return True  # 试用还没开始
        
        # 检查是否超过对话次数限制
        chat_count = trial_info.get('chat_count', 0)
        max_chats = trial_info.get('max_chats', 1)
        
        return chat_count < max_chats
    
    def increment_trial_chat(self, user_id: str) -> bool:
        """增加试用对话次数，返回是否还能继续对话"""
        if user_id in self.trial_records:
            trial_info = self.trial_records[user_id]
            trial_info['chat_count'] = trial_info.get('chat_count', 0) + 1
            self.save_data()
            
            return trial_info['chat_count'] < trial_info.get('max_chats', 1)
        return False
    
    def get_trial_info(self, user_id: str) -> Optional[Dict]:
        """获取试用信息"""
        return self.trial_records.get(user_id)
    
    def get_days_until_next_trial(self, user_id: str) -> int:
        """获取距离下次可试用的天数"""
        if user_id not in self.trial_records:
            return 0
        
        trial_info = self.trial_records[user_id]
        used_at = trial_info.get('used_at', '')
        if not used_at:
            return 0
        
        try:
            used_date = datetime.fromisoformat(used_at)
            # 计算下个月1号
            if used_date.month == 12:
                next_month = datetime(used_date.year + 1, 1, 1)
            else:
                next_month = datetime(used_date.year, used_date.month + 1, 1)
            
            days_left = (next_month - datetime.now()).days
            return max(0, days_left)
        except:
            return 0
    
    def get_trial_stats(self) -> Dict:
        """获取试用统计"""
        current_month = self._get_month_key()
        total_trials = len(self.trial_records)
        
        this_month_trials = 0
        total_chats = 0
        
        for record in self.trial_records.values():
            if record.get('month') == current_month:
                this_month_trials += 1
            total_chats += record.get('chat_count', 0)
        
        return {
            'total_trials': total_trials,
            'this_month_trials': this_month_trials,
            'total_trial_chats': total_chats
        }
    
    def get_all_trial_records(self) -> List[Dict]:
        """获取所有试用记录（管理员用）"""
        records = []
        for user_id, record in self.trial_records.items():
            records.append({
                'user_id': user_id,
                **record
            })
        return sorted(records, key=lambda x: x.get('used_at', ''), reverse=True)

# 全局试用管理器实例
trial_manager = TrialManager()
