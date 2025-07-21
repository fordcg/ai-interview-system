#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
本地面试API接口
替代SparkOS API，提供稳定的本地面试功能
"""

import os
import uuid
import asyncio
import logging
import time
import sys
from pathlib import Path
from flask import Blueprint, request, jsonify, current_app

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from utils.xunfei_tts_client import get_interview_controller
from question_modes import MODE_INTERVIEW, MODE_SURVEY

logger = logging.getLogger(__name__)

# 创建蓝图
local_interview_bp = Blueprint('local_interview', __name__, url_prefix='/interview/local')

# 全局会话管理
active_sessions = {}

@local_interview_bp.route('/create_session', methods=['POST'])
def create_session():
    """创建面试会话"""
    try:
        data = request.get_json() or {}
        
        # 生成会话ID
        session_id = str(uuid.uuid4())
        
        # 获取问题模式
        mode_id = data.get('mode_id', MODE_INTERVIEW)
        
        # 获取面试控制器
        controller = get_interview_controller()
        
        # 创建会话（同步调用）
        result = controller.create_session(session_id, mode_id)
        
        if result['success']:
            # 保存会话信息
            active_sessions[session_id] = {
                'session_id': session_id,
                'mode_id': mode_id,
                'created_at': time.time(),
                'status': 'active'
            }
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'message': '面试会话创建成功',
                'mode_id': mode_id
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', '会话创建失败')
            }), 500
            
    except Exception as e:
        logger.error(f"创建面试会话失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@local_interview_bp.route('/user_response', methods=['POST'])
def handle_user_response():
    """处理用户回答"""
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id')
        response_text = data.get('response_text', '')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': '缺少会话ID'
            }), 400
        
        if session_id not in active_sessions:
            return jsonify({
                'success': False,
                'error': '会话不存在或已过期'
            }), 404
        
        # 获取面试控制器
        controller = get_interview_controller()
        
        # 处理用户回答（同步调用）
        result = controller.handle_user_response(session_id, response_text)
        
        if result['success']:
            # 更新会话状态
            if not result.get('has_next_question', True):
                active_sessions[session_id]['status'] = 'completed'
            
            return jsonify({
                'success': True,
                'has_next_question': result.get('has_next_question', True),
                'progress': result.get('progress', {}),
                'message': '回答处理成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', '回答处理失败')
            }), 500
            
    except Exception as e:
        logger.error(f"处理用户回答失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@local_interview_bp.route('/next_question', methods=['POST'])
def get_next_question():
    """获取下一个问题（手动触发）"""
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': '缺少会话ID'
            }), 400
        
        if session_id not in active_sessions:
            return jsonify({
                'success': False,
                'error': '会话不存在或已过期'
            }), 404
        
        # 获取面试控制器
        controller = get_interview_controller()
        
        # 触发下一个问题
        result = controller.handle_user_response(session_id)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"获取下一个问题失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@local_interview_bp.route('/session_status/<session_id>', methods=['GET'])
def get_session_status(session_id):
    """获取会话状态"""
    try:
        if session_id not in active_sessions:
            return jsonify({
                'success': False,
                'error': '会话不存在'
            }), 404
        
        session_info = active_sessions[session_id]
        
        # 获取面试进度
        controller = get_interview_controller()
        progress = controller.tts_client.get_interview_progress()
        
        return jsonify({
            'success': True,
            'session_info': session_info,
            'progress': progress
        })
        
    except Exception as e:
        logger.error(f"获取会话状态失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@local_interview_bp.route('/end_session', methods=['POST'])
def end_session():
    """结束面试会话"""
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': '缺少会话ID'
            }), 400
        
        # 获取面试控制器
        controller = get_interview_controller()
        result = controller.end_session(session_id)
        
        # 清理会话记录
        if session_id in active_sessions:
            del active_sessions[session_id]
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"结束面试会话失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@local_interview_bp.route('/available_modes', methods=['GET'])
def get_available_modes():
    """获取可用的问题模式"""
    try:
        from question_modes import get_question_mode_manager
        
        manager = get_question_mode_manager()
        modes = []
        
        for mode_id, mode in manager.modes.items():
            modes.append({
                'mode_id': mode_id,
                'name': mode.name,
                'description': mode.description,
                'question_count': len(mode.questions)
            })
        
        return jsonify({
            'success': True,
            'modes': modes
        })
        
    except Exception as e:
        logger.error(f"获取问题模式失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@local_interview_bp.route('/test_tts', methods=['POST'])
def test_tts():
    """测试TTS功能"""
    try:
        data = request.get_json() or {}
        text = data.get('text', '这是一个TTS测试。')

        if not text or not isinstance(text, str):
            return jsonify({
                'success': False,
                'error': '无效的文本输入'
            }), 400

        # 获取面试控制器
        controller = get_interview_controller()

        # 测试TTS
        success = controller.tts_client.speak_text(text)

        return jsonify({
            'success': success,
            'message': 'TTS测试完成' if success else 'TTS测试失败',
            'text': text
        })

    except Exception as e:
        logger.error(f"TTS测试失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@local_interview_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    try:
        import time
        return jsonify({
            'success': True,
            'service': 'Local Interview API',
            'status': 'healthy',
            'timestamp': time.time(),
            'active_sessions': len(active_sessions)
        })
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 错误处理
@local_interview_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': '接口不存在'
    }), 404

@local_interview_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': '服务器内部错误'
    }), 500
