#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Flask应用入口文件
"""

import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from config import Config

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

def create_app(config_class=Config):
    """
    创建Flask应用
    
    Args:
        config_class: 配置类
    
    Returns:
        Flask应用实例
    """
    # 创建应用
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config_class)
    
    # 配置情感模型路径
    app.config['EMOTION_MODEL_PATH'] = os.path.join(app.root_path, 'weights', 'model_best.pth.tar')
    # 如果新模型不存在，使用备用模型
    if not os.path.exists(app.config['EMOTION_MODEL_PATH']):
        app.config['EMOTION_MODEL_PATH'] = os.path.join(app.root_path, 'weights', 'efficientface.pth.tar')
        # 如果备用模型也不存在，使用原始模型
        if not os.path.exists(app.config['EMOTION_MODEL_PATH']):
            app.config['EMOTION_MODEL_PATH'] = os.path.join(app.root_path, 'weights', 'emotion.pth')
    
    # 配置RANER模型路径
    app.config['RESUME_NER_MODEL_PATH'] = os.path.join(app.root_path, 'models', 'nlp', 'raner_resume')
    app.config['RESUME_NER_ENABLED'] = True
    
    # 启用CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 注册蓝图
    from api import init_app
    init_app(app)
    
    # 注册错误处理
    register_error_handlers(app)
    
    # 添加根路由处理程序
    @app.route('/')
    def index():
        """
        根路由处理程序
        
        Returns:
            JSON响应，包含应用信息
        """
        return jsonify({
            'name': 'Merged Project Flask API',
            'version': app.config.get('API_VERSION', 'v1.0.0'),
            'status': 'running',
            'api_base_url': '/api'
        })
    
    # 添加静态文件路由，直接提供上传文件的访问
    @app.route('/api/uploads/<filename>')
    def uploaded_file(filename):
        """
        静态文件路由，直接提供上传文件的访问
        
        Args:
            filename: 文件名
            
        Returns:
            文件内容
        """
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    return app

def register_error_handlers(app):
    """
    注册错误处理
    
    Args:
        app: Flask应用实例
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'code': 404,
            'message': 'Not Found'
        }), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'code': 500,
            'message': 'Internal Server Error'
        }), 500

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 启动应用
    app.run(debug=True, host='0.0.0.0', port=5000) 