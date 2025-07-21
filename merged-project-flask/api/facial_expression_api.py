#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
面部表情分析API
提供面部表情分析相关功能
"""

import os
import sys
import base64
import json
import time
import uuid
import cv2
import numpy as np
from flask import Blueprint, request, jsonify, current_app, render_template
from werkzeug.utils import secure_filename
from datetime import datetime

# 导入新的情感分析器
from utils.emotion_analyzer import EmotionAnalyzer, get_emotion_analyzer, get_emotion_distribution, reset_emotion_stats, get_current_emotion

def convert_expression_results(expressions):
    """
    将新版表情分析结果转换为前端兼容格式
    
    Args:
        expressions: 表情分析结果列表
        
    Returns:
        converted_expressions: 转换后的表情分析结果列表
    """
    converted_expressions = []
    if not expressions:
        current_app.logger.warning("表情分析结果为空，无法转换")
        return converted_expressions
    
    current_app.logger.info(f"开始转换表情分析结果，共 {len(expressions)} 个表情数据")
        
    for expr in expressions:
        # 创建兼容性表情结果
        converted_expr = {
            'face_id': expr['face_id'],
            'expression': expr['expression'],
            'confidence': float(expr['confidence']),  # 确保是浮点数
            'details': {
                'en_emotion': expr.get('details', {}).get('en_emotion', 'neutral')  # 确保包含英文表情标签
            }
        }
        
        current_app.logger.debug(f"处理人脸 #{expr['face_id']} 的表情: {expr['expression']}, 置信度: {expr['confidence']}, 英文标签: {converted_expr['details']['en_emotion']}")
        
        # 处理详细信息
        if 'details' in expr:
            details = expr['details']
            
            # 保留已有的en_emotion字段
            en_emotion = details.get('en_emotion', 'neutral')
            converted_expr['details']['en_emotion'] = en_emotion
            
            # 转换表情分数
            if 'scores' in details:
                scores = {}
                for emotion, score in details['scores'].items():
                    # 确保所有分数都是浮点数
                    scores[emotion] = float(score)
                    current_app.logger.debug(f"表情 '{emotion}' 得分: {score}")
                converted_expr['details']['scores'] = scores
            else:
                # 创建基本的分数字典
                default_scores = {
                    '中性': 0.3,
                    '微笑': 0.0,
                    '惊讶': 0.0,
                    '生气': 0.0,
                    '悲伤': 0.0,
                    '恐惧': 0.0,
                    '厌恶': 0.0
                }
                # 根据当前表情设置相应的高分
                if expr['expression'] in default_scores:
                    default_scores[expr['expression']] = float(expr['confidence'])
                converted_expr['details']['scores'] = default_scores
                current_app.logger.warning("未找到表情分数数据，创建了默认分数")
                
            # 如果有详细的情绪分数，也保留
            if 'detailed_emotions' in details:
                converted_expr['details']['detailed_emotions'] = details['detailed_emotions']
        else:
            current_app.logger.warning(f"人脸 #{expr['face_id']} 的表情数据缺少详细信息")
            # 创建默认的详情数据
            default_scores = {
                '中性': 0.7,
                '微笑': 0.0,
                '惊讶': 0.0,
                '生气': 0.0,
                '悲伤': 0.0,
                '恐惧': 0.0,
                '厌恶': 0.0
            }
            # 根据当前表情设置相应的高分
            if expr['expression'] in default_scores:
                default_scores[expr['expression']] = float(expr['confidence'])
            
            converted_expr['details']['scores'] = default_scores
        
        converted_expressions.append(converted_expr)
    
    current_app.logger.info(f"表情分析结果转换完成，转换后数据: {json.dumps(converted_expressions, ensure_ascii=False)}")
    return converted_expressions

# 创建蓝图
facial_expression_bp = Blueprint('facial_expression', __name__, url_prefix='/facial-expression')

# 全局变量
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = 'static/uploads/facial_expression'

# 确保上传目录存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 初始化面部表情分析器
facial_analyzer = None

def get_facial_analyzer(debug_mode=False):
    """获取面部表情分析器单例"""
    global facial_analyzer
    if facial_analyzer is None:
        try:
            # 初始化情感分析器
            facial_analyzer = get_emotion_analyzer(debug_mode)
            current_app.logger.info("情感分析器初始化成功")
        except Exception as e:
            current_app.logger.error(f"情感分析器初始化失败: {str(e)}")
            raise
    
    return facial_analyzer

def allowed_file(filename):
    """检查文件是否允许上传"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@facial_expression_bp.route('/analyze', methods=['POST'])
def analyze_expression():
    """
    分析面部表情
    
    请求参数:
        - image: Base64编码的图像
        
    返回:
        - success: 是否成功
        - message: 消息
        - data: 
            - face_count: 检测到的人脸数量
            - expressions: 表情分析结果
            - image: 处理后的图像Base64
    """
    try:
        # 获取参数
        data = request.get_json()
        if not data or 'image' not in data:
            current_app.logger.error("缺少image参数")
            return jsonify({
                'success': False,
                'message': '缺少image参数',
                'data': None
            }), 400
        
        image_data = data['image']
        
        # 获取面部表情分析器
        try:
            analyzer = get_facial_analyzer()
            current_app.logger.debug("成功获取面部表情分析器")
        except Exception as e:
            current_app.logger.error(f"获取面部表情分析器失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'获取面部表情分析器失败: {str(e)}',
                'data': None
            }), 500
        
        # 解码图像
        try:
            # 如果图像数据是以data:开头的，则提取Base64部分
            if ',' in image_data:
                image_data = image_data.split(',', 1)[1]
            
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                current_app.logger.error("无法解码图像数据")
                return jsonify({
                    'success': False,
                    'message': '无法解码图像数据',
                    'data': None
                }), 400
            
            current_app.logger.debug(f"成功解码图像，尺寸: {image.shape}")
        except Exception as e:
            current_app.logger.error(f"解码图像数据失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'解码图像数据失败: {str(e)}',
                'data': None
            }), 500
        
        # 处理图像
        try:
            current_app.logger.info("开始处理图像...")
            processed_image, results = analyzer.process_frame(image)
            current_app.logger.info(f"图像处理完成，检测到 {results['face_count']} 个人脸")
            
            if results['face_count'] == 0:
                current_app.logger.warning("未检测到人脸")
                return jsonify({
                    'success': True,
                    'message': '未检测到人脸',
                    'data': {
                        'face_count': 0,
                        'expressions': [],
                        'image': None
                    }
                })
        except Exception as e:
            current_app.logger.error(f"处理图像失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'处理图像失败: {str(e)}',
                'data': None
            }), 500
        
        # 编码为Base64
        try:
            _, buffer = cv2.imencode('.jpg', processed_image)
            processed_image_base64 = base64.b64encode(buffer).decode('utf-8')
            current_app.logger.debug("成功将处理后的图像编码为Base64")
        except Exception as e:
            current_app.logger.error(f"编码处理后的图像失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'编码处理后的图像失败: {str(e)}',
                'data': None
            }), 500
        
        # 转换表情分析结果，确保前端兼容性
        try:
            current_app.logger.info("开始转换表情分析结果...")
            converted_expressions = convert_expression_results(results.get('expressions', []))
            current_app.logger.info(f"表情分析结果转换完成，共 {len(converted_expressions)} 个结果")
        except Exception as e:
            current_app.logger.error(f"转换表情分析结果失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'转换表情分析结果失败: {str(e)}',
                'data': None
            }), 500
        
        # 构建响应
        response_data = {
            'face_count': results['face_count'],
            'expressions': converted_expressions,
            'image': f'data:image/jpeg;base64,{processed_image_base64}'
        }
        
        current_app.logger.info(f"表情分析完成，检测到 {results['face_count']} 个人脸")
        
        return jsonify({
            'success': True,
            'message': f'检测到{results["face_count"]}个人脸',
            'data': response_data
        })
    
    except Exception as e:
        current_app.logger.error(f"面部表情分析错误: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'处理失败: {str(e)}',
            'data': None
        }), 500

@facial_expression_bp.route('/upload', methods=['POST'])
def upload_and_analyze():
    """
    上传图像并分析面部表情
    
    请求参数:
        - file: 图像文件
        
    返回:
        - success: 是否成功
        - message: 消息
        - data: 
            - face_count: 检测到的人脸数量
            - expressions: 表情分析结果
            - image_url: 处理后的图像URL
    """
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            current_app.logger.error("没有文件上传")
            return jsonify({
                'success': False,
                'message': '没有文件上传',
                'data': None
            }), 400
        
        file = request.files['file']
        
        # 检查文件名是否为空
        if file.filename == '':
            current_app.logger.error("未选择文件")
            return jsonify({
                'success': False,
                'message': '未选择文件',
                'data': None
            }), 400
        
        # 检查文件后缀
        filename = secure_filename(file.filename)
        if not allowed_file(filename):
            current_app.logger.error(f"不支持的文件类型: {file.filename}")
            return jsonify({
                'success': False,
                'message': f'不支持的文件类型，允许的类型: {", ".join(ALLOWED_EXTENSIONS)}',
                'data': None
            }), 400
        
        # 保存上传的文件
        try:
            # 生成唯一文件名
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, unique_filename)
            
            # 确保上传目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 保存文件
            file.save(file_path)
            current_app.logger.info(f"文件已保存到: {file_path}")
        except Exception as e:
            current_app.logger.error(f"保存文件失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'保存文件失败: {str(e)}',
                'data': None
            }), 500
        
        # 获取可视化模式参数（如果有）
        debug_mode = request.form.get('debug', 'false').lower() == 'true'
        
        # 获取面部表情分析器
        try:
            analyzer = get_facial_analyzer(debug_mode)
            current_app.logger.debug("成功获取面部表情分析器")
        except Exception as e:
            current_app.logger.error(f"获取面部表情分析器失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'获取面部表情分析器失败: {str(e)}',
                'data': None
            }), 500
        
        # 读取保存的图像
        try:
            image = cv2.imread(file_path)
            if image is None:
                current_app.logger.error(f"无法读取图像文件: {file_path}")
                return jsonify({
                    'success': False,
                    'message': '无法读取上传的图像文件',
                    'data': None
                }), 400
            
            current_app.logger.debug(f"成功读取图像，尺寸: {image.shape}")
        except Exception as e:
            current_app.logger.error(f"读取图像文件失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'读取图像文件失败: {str(e)}',
                'data': None
            }), 500
        
        # 处理图像
        try:
            current_app.logger.info("开始处理图像...")
            processed_image, results = analyzer.process_frame(image)
            current_app.logger.info(f"图像处理完成，检测到 {results['face_count']} 个人脸")
            
            if results['face_count'] == 0:
                current_app.logger.warning("未检测到人脸")
                return jsonify({
                    'success': True,
                    'message': '未检测到人脸',
                    'data': {
                        'face_count': 0,
                        'expressions': [],
                        'image_url': None
                    }
                })
        except Exception as e:
            current_app.logger.error(f"处理图像失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'处理图像失败: {str(e)}',
                'data': None
            }), 500
        
        # 保存处理后的图像
        try:
            processed_filename = f"processed_{unique_filename}"
            processed_path = os.path.join(UPLOAD_FOLDER, processed_filename)
            cv2.imwrite(processed_path, processed_image)
            current_app.logger.info(f"处理后的图像已保存: {processed_path}")
        except Exception as e:
            current_app.logger.error(f"保存处理后的图像失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'保存处理后的图像失败: {str(e)}',
                'data': None
            }), 500
        
        # 构建图像URL
        image_url = f"/static/uploads/facial_expression/{processed_filename}"
        
        # 转换表情分析结果，确保前端兼容性
        try:
            current_app.logger.info("开始转换表情分析结果...")
            converted_expressions = convert_expression_results(results.get('expressions', []))
            current_app.logger.info(f"表情分析结果转换完成，共 {len(converted_expressions)} 个结果")
        except Exception as e:
            current_app.logger.error(f"转换表情分析结果失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'转换表情分析结果失败: {str(e)}',
                'data': None
            }), 500
        
        # 构建响应
        response_data = {
            'face_count': results['face_count'],
            'expressions': converted_expressions,
            'image_url': image_url
        }
        
        return jsonify({
            'success': True,
            'message': f'检测到{results["face_count"]}个人脸',
            'data': response_data
        })
    
    except Exception as e:
        current_app.logger.error(f"面部表情分析错误: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'处理失败: {str(e)}',
            'data': None
        }), 500

@facial_expression_bp.route('/test-landmarks', methods=['GET'])
def test_landmarks():
    """
    特征点可视化测试页面
    
    返回:
        测试页面HTML
    """
    try:
        return render_template('landmark_test.html')
    except Exception as e:
        current_app.logger.error(f"加载特征点测试页面失败: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'加载特征点测试页面失败: {str(e)}',
            'data': None
        }), 500 

@facial_expression_bp.route('/emotion-distribution', methods=['GET'])
def get_emotion_stats():
    """
    获取情绪分布统计信息
    
    返回:
        - success: 是否成功
        - message: 消息
        - data: 
            - counts: 各情绪的计数
            - percentages: 各情绪的百分比
            - total: 总处理帧数
    """
    try:
        # 获取情绪分布统计信息
        stats = get_emotion_distribution()
        
        return jsonify({
            'success': True,
            'message': '获取情绪分布统计信息成功',
            'data': stats
        })
    
    except Exception as e:
        current_app.logger.error(f"获取情绪分布统计信息错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取情绪分布统计信息失败: {str(e)}',
            'data': None
        }), 500

@facial_expression_bp.route('/reset-stats', methods=['POST'])
def reset_stats():
    """
    重置情绪分布统计信息
    
    返回:
        - success: 是否成功
        - message: 消息
    """
    try:
        # 重置情绪分布统计信息
        reset_emotion_stats()
        
        return jsonify({
            'success': True,
            'message': '重置情绪分布统计信息成功'
        })
    
    except Exception as e:
        current_app.logger.error(f"重置情绪分布统计信息错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'重置情绪分布统计信息失败: {str(e)}'
        }), 500 

@facial_expression_bp.route('/current-emotion', methods=['GET'])
def get_current_emotion_api():
    """
    获取当前检测到的表情状态
    
    返回:
        - success: 是否成功
        - message: 消息
        - data: 当前表情状态
    """
    try:
        # 获取当前表情状态
        current_emotion = get_current_emotion()
        
        # 确保返回数据包含英文表情标签
        if 'main_emotion' in current_emotion:
            en_emotion = current_emotion['main_emotion']
            cn_emotion = current_emotion.get('cn_emotion', '')
            
            # 记录日志
            current_app.logger.info(f"当前表情: {en_emotion} ({cn_emotion}), 置信度: {current_emotion.get('confidence', 0)}")
            
            # 添加表情表达式数据以兼容前端
            expressions = [{
                'face_id': 0,
                'expression': cn_emotion,
                'confidence': current_emotion.get('confidence', 0),
                'details': {
                    'en_emotion': en_emotion,
                    'scores': current_emotion.get('detailed_emotions', {})
                }
            }]
            
            # 构建响应数据
            response_data = {
                'main_emotion': current_emotion['main_emotion'],
                'cn_emotion': cn_emotion,
                'confidence': current_emotion.get('confidence', 0),
                'timestamp': current_emotion.get('timestamp', time.time()),
                'face_count': 1,
                'expressions': expressions
            }
        else:
            response_data = current_emotion
        
        return jsonify({
            'success': True,
            'message': '获取当前表情成功',
            'data': response_data
        })
    
    except Exception as e:
        current_app.logger.error(f"获取当前表情错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取当前表情失败: {str(e)}',
            'data': None
        }), 500 