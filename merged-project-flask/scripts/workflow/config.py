#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
工作流模块统一配置文件
集中管理API密钥、超时设置等配置信息
"""

import os

# 讯飞星辰大模型API配置
XF_API_KEY = os.getenv("XUNFEI_API_KEY", "your-api-key")
XF_API_SECRET = os.getenv("XUNFEI_API_SECRET", "your-api-secret")
XF_FLOW_ID = "7349366686812278786"

# 超时设置（秒）- 支持3分钟工作流处理
CONNECT_TIMEOUT = 60
READ_TIMEOUT = 300  # 5分钟读取超时，支持3分钟工作流
DEFAULT_TIMEOUT = (CONNECT_TIMEOUT, READ_TIMEOUT)

# 上传文件配置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '../../'))
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, '../uploads')
TEMP_UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'upload')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB

# 文本处理配置
MAX_TEXT_LENGTH = 8000  # 最大文本长度

# 确保上传目录存在
for folder in [UPLOAD_FOLDER, TEMP_UPLOAD_FOLDER]:
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
            print(f"创建目录: {folder}")
        except Exception as e:
            print(f"无法创建目录 {folder}: {str(e)}")

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS 