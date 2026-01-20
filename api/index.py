#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vercel Serverless Function Entry Point
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from advanced_web import app

# Vercel 需要这个变量
handler = app
