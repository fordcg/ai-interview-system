#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Flask应用配置文件
"""

import os

# 数据库配置
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'merged_job_interview.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False

# 应用配置
SECRET_KEY = 'merged_job_interview_2024'
JSON_AS_ASCII = False
DEBUG = True

# 上传文件配置
UPLOAD_FOLDER = os.path.join(basedir, 'static/uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 最大上传16MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

# 外部访问配置
# 设置为Nginx服务的域名或IP，例如：http://example.com 或 http://192.168.1.100
# 如果为None，则使用请求的host_url
EXTERNAL_URL_BASE = "http://192.168.43.94"

# 跨域配置
CORS_HEADERS = 'Content-Type'

# 讯飞AI简历生成API配置
XF_APPID = os.getenv('XUNFEI_APP_ID', 'your-app-id')
XF_APISECRET = os.getenv('XUNFEI_API_SECRET', 'your-api-secret')
XF_API_KEY = os.getenv('XUNFEI_API_KEY', 'your-api-key')

# RANER模型配置
RESUME_NER_MODEL_ID = 'damo/nlp_raner_named-entity-recognition_chinese-base-resume'
RESUME_NER_ENABLED = True  # 是否启用简历实体识别功能

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'your-deepseek-api-key')
DEEPSEEK_BASE_URL = 'https://api.deepseek.com'  # DeepSeek API基础URL
DEEPSEEK_MODEL_CHAT = 'deepseek-chat'  # DeepSeek对话模型
DEEPSEEK_MODEL_REASONER = 'deepseek-reasoner'  # DeepSeek推理模型
DEEPSEEK_ENABLED = True  # 是否启用DeepSeek API功能

# 基础配置类
class Config:
    # 安全配置
    SECRET_KEY = SECRET_KEY
    
    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = SQLALCHEMY_TRACK_MODIFICATIONS
    
    # 上传文件配置
    UPLOAD_FOLDER = UPLOAD_FOLDER
    MAX_CONTENT_LENGTH = MAX_CONTENT_LENGTH
    
    # 外部访问配置
    EXTERNAL_URL_BASE = EXTERNAL_URL_BASE
    
    # API配置
    JSON_AS_ASCII = JSON_AS_ASCII
    
    # 讯飞API配置
    XF_APPID = XF_APPID
    XF_APISECRET = XF_APISECRET
    XF_API_KEY = XF_API_KEY
    
    # RANER模型配置
    RESUME_NER_MODEL_ID = RESUME_NER_MODEL_ID
    RESUME_NER_ENABLED = RESUME_NER_ENABLED

    # DeepSeek API配置
    DEEPSEEK_API_KEY = DEEPSEEK_API_KEY
    DEEPSEEK_BASE_URL = DEEPSEEK_BASE_URL
    DEEPSEEK_MODEL_CHAT = DEEPSEEK_MODEL_CHAT
    DEEPSEEK_MODEL_REASONER = DEEPSEEK_MODEL_REASONER
    DEEPSEEK_ENABLED = DEEPSEEK_ENABLED
    
    @staticmethod
    def init_app(app):
        pass

# 开发环境配置
class DevelopmentConfig(Config):
    DEBUG = DEBUG
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI

# 测试环境配置
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI

# 生产环境配置
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI

# 配置字典
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 