#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
人脸检测API
提供人脸网格检测相关功能
"""

import os
import sys
import base64
import json
import time
import uuid
import cv2
import numpy as np
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from datetime import datetime

# 导入人脸检测模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from algorithm.face_detection.face_mesh import FaceMeshDetector

# 修改utils导入路径
import algorithm.face_detection.utils as face_utils

# 创建蓝图
face_detection_bp = Blueprint('face_detection', __name__, url_prefix='/api/face')

# 全局变量
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = 'static/uploads/face_detection'

# 确保上传目录存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 初始化人脸检测器
face_detector = None

def get_face_detector():
    """获取人脸检测器单例"""
    global face_detector
    if face_detector is None:
        face_detector = FaceMeshDetector(static_image_mode=False, max_num_faces=2)
    return face_detector

def allowed_file(filename):
    """检查文件是否允许上传"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@face_detection_bp.route('/detect', methods=['POST'])
def detect_face():
    """
    检测人脸
    
    请求参数:
        - image: Base64编码的图像数据
        - draw_mode: 绘制模式，可选值：'all', 'tesselation', 'contours', 'irises'
        
    返回:
        - success: 是否成功
        - message: 消息
        - data: 
            - face_count: 检测到的人脸数量
            - image: Base64编码的标注后的图像
    """
    try:
        # 获取参数
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({
                'success': False,
                'message': '缺少必要参数',
                'data': None
            }), 400
        
        # 获取图像数据
        image_data = data['image']
        # 去除Base64前缀
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        # 解码Base64图像
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # 获取绘制模式
        draw_mode = data.get('draw_mode', 'all')
        if draw_mode not in ['all', 'tesselation', 'contours', 'irises']:
            draw_mode = 'all'
        
        # 转换为RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 检测人脸网格
        detector = get_face_detector()
        results = detector.face_mesh.process(image_rgb)
        
        # 可视化
        annotated_image = image.copy()
        face_count = 0
        
        if results.multi_face_landmarks:
            face_count = len(results.multi_face_landmarks)
            
            for face_landmarks in results.multi_face_landmarks:
                # 绘制人脸网格
                annotated_image = face_utils.draw_face_mesh(annotated_image, face_landmarks, mode=draw_mode)
            
            # 添加信息
            annotated_image = face_utils.draw_face_mesh_info(annotated_image, face_count)
        
        # 编码为Base64
        _, buffer = cv2.imencode('.jpg', annotated_image)
        annotated_image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'message': f'检测到{face_count}个人脸',
            'data': {
                'face_count': face_count,
                'image': f'data:image/jpeg;base64,{annotated_image_base64}'
            }
        })
    
    except Exception as e:
        current_app.logger.error(f"人脸检测错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'处理失败: {str(e)}',
            'data': None
        }), 500 