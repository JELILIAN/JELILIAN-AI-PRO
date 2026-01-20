#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JELILIAN AI PRO 订单管理系统
支持人工审核支付后激活用户订阅
"""

import json
import os
from datetime import datetime
from typing import Optional, Dict, List

ORDERS_FILE = "orders.json"

class OrderManager:
    def __init__(self):
        self.orders = self._load_orders()
    
    def _load_orders(self) -> Dict:
        """加载订单数据"""
        if os.path.exists(ORDERS_FILE):
            try:
                with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"orders": []}
        return {"orders": []}
    
    def _save_orders(self):
        """保存订单数据"""
        with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.orders, f, ensure_ascii=False, indent=2)
    
    def create_order(self, user_id: str, username: str, email: str, 
                     plan: str, amount: float, currency: str = "USD") -> Dict:
        """创建新订单"""
        order_id = f"ORDER_{datetime.now().strftime('%Y%m%d%H%M%S')}_{user_id[:8]}"
        
        order = {
            "order_id": order_id,
            "user_id": user_id,
            "username": username,
            "email": email,
            "plan": plan,
            "amount": amount,
            "currency": currency,
            "status": "pending",  # pending=待审核, approved=已通过, rejected=已拒绝
            "created_at": datetime.now().isoformat(),
            "reviewed_at": None,
            "reviewed_by": None,
            "notes": ""
        }
        
        self.orders["orders"].append(order)
        self._save_orders()
        return order
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """获取订单信息"""
        for order in self.orders["orders"]:
            if order["order_id"] == order_id:
                return order
        return None
    
    def get_user_orders(self, user_id: str) -> List[Dict]:
        """获取用户的所有订单"""
        return [o for o in self.orders["orders"] if o["user_id"] == user_id]
    
    def get_pending_orders(self) -> List[Dict]:
        """获取所有待审核订单"""
        return [o for o in self.orders["orders"] if o["status"] == "pending"]
    
    def get_all_orders(self) -> List[Dict]:
        """获取所有订单"""
        return self.orders["orders"]
    
    def approve_order(self, order_id: str, admin_name: str = "admin", notes: str = "") -> Dict:
        """审核通过订单"""
        for order in self.orders["orders"]:
            if order["order_id"] == order_id:
                order["status"] = "approved"
                order["reviewed_at"] = datetime.now().isoformat()
                order["reviewed_by"] = admin_name
                order["notes"] = notes
                self._save_orders()
                return {"success": True, "order": order}
        return {"success": False, "message": "订单不存在"}
    
    def reject_order(self, order_id: str, admin_name: str = "admin", notes: str = "") -> Dict:
        """拒绝订单"""
        for order in self.orders["orders"]:
            if order["order_id"] == order_id:
                order["status"] = "rejected"
                order["reviewed_at"] = datetime.now().isoformat()
                order["reviewed_by"] = admin_name
                order["notes"] = notes
                self._save_orders()
                return {"success": True, "order": order}
        return {"success": False, "message": "订单不存在"}
    
    def has_pending_order(self, user_id: str, plan: str) -> bool:
        """检查用户是否有待审核的同类型订单"""
        for order in self.orders["orders"]:
            if (order["user_id"] == user_id and 
                order["plan"] == plan and 
                order["status"] == "pending"):
                return True
        return False

# 全局订单管理器实例
order_manager = OrderManager()
