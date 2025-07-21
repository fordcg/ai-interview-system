#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API模块初始化
注册所有API蓝图
"""

from flask import Blueprint
from .user_api import userBp
from .job_api import jobBp
from .interview_api import interviewBp
from .resume_api import resumeBp
from .common import commonBp
# 表情识别API
from .facial_expression_api import facial_expression_bp
from .baidu_api import baiduBp
from .alipay_api import payBp  # 修正导入名称
from .local_interview_api import local_interview_bp
from .deepseek_api import deepseek_bp
from .interview_report_api import interview_report_bp
from .health_api import health_bp

# 创建API蓝图
api_bp = Blueprint('api', __name__)

# 注册子蓝图
api_bp.register_blueprint(userBp)
api_bp.register_blueprint(jobBp)
api_bp.register_blueprint(interviewBp)
api_bp.register_blueprint(resumeBp)
api_bp.register_blueprint(commonBp)
# 注册表情识别API
api_bp.register_blueprint(facial_expression_bp)
api_bp.register_blueprint(baiduBp)
api_bp.register_blueprint(payBp)  # 修正注册名称
api_bp.register_blueprint(local_interview_bp)
api_bp.register_blueprint(deepseek_bp, url_prefix='/deepseek')
api_bp.register_blueprint(interview_report_bp, url_prefix='/interview-report')
api_bp.register_blueprint(health_bp)

# 定义API版本
API_VERSION = 'v1.0.0'

# 初始化API
def init_app(app):
    """
    初始化API
    
    Args:
        app: Flask应用实例
    """
    # 注册API蓝图
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 设置API版本
    app.config['API_VERSION'] = API_VERSION
    
    # 打印API初始化信息
    print(f"API initialized, version: {API_VERSION}")
    
    return app 