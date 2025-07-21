#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
核心配置
"""

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_login import LoginManager
import json
from datetime import datetime, date
from decimal import Decimal
import os

# 初始化数据库
db = SQLAlchemy()

# 初始化Marshmallow
ma = Marshmallow()

# 初始化登录管理器
login_manager = LoginManager()
login_manager.login_view = 'user.login'

# JSON编码器
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)

# 讯飞TTS配置
def get_xunfei_tts_config():
    """获取讯飞TTS配置"""
    return {
        'XUNFEI_APP_ID': os.getenv('XUNFEI_APP_ID', 'XXXXXXXX'),
        'XUNFEI_API_KEY': os.getenv('XUNFEI_API_KEY', 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'),
        'XUNFEI_API_SECRET': os.getenv('XUNFEI_API_SECRET', 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'),
        'XUNFEI_VOICE': os.getenv('XUNFEI_VOICE', 'x5_lingyuyan_flow'),
        'XUNFEI_BASE_URL': os.getenv('XUNFEI_BASE_URL', 'wss://cbm01.cn-huabei-1.xf-yun.com/v1/private/mcd9m97e6')
    }