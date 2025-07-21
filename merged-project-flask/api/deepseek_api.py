#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DeepSeek API 接口
提供基于 DeepSeek 的 AI 服务接口
"""

from flask import Blueprint, request, jsonify, current_app
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from base.response import ResMsg
from utils.deepseek_client import DeepSeekClient

# 创建蓝图
deepseek_bp = Blueprint('deepseek', __name__)


@deepseek_bp.route('/test', methods=['GET'])
def test_connection():
    """测试 DeepSeek API 连接"""
    res = ResMsg()
    
    try:
        client = DeepSeekClient()
        result = client.test_connection()
        
        if result['success']:
            res.update(code=0, data=result, msg="连接测试成功")
        else:
            res.update(code=1, data=result, msg="连接测试失败")
    
    except Exception as e:
        res.update(code=1, msg=f"测试失败: {str(e)}")
    
    return res.data





@deepseek_bp.route('/analyze/interview', methods=['POST'])
def analyze_interview():
    """分析面试回答"""
    res = ResMsg()
    
    try:
        data = request.get_json()
        
        if not data:
            res.update(code=1, msg="请求数据为空")
            return res.data
        
        question = data.get('question', '')
        answer = data.get('answer', '')
        job_position = data.get('job_position', '通用职位')
        
        if not question or not answer:
            res.update(code=1, msg="问题和回答不能为空")
            return res.data
        
        client = DeepSeekClient()
        
        if not client.is_available():
            res.update(code=1, msg="DeepSeek 服务不可用")
            return res.data
        
        # 分析面试回答
        result = client.analyze_interview_answer(question, answer, job_position)
        
        if result['success']:
            res.update(code=0, data=result, msg="分析完成")
        else:
            res.update(code=1, data=result, msg="分析失败")
    
    except Exception as e:
        res.update(code=1, msg=f"分析失败: {str(e)}")
    
    return res.data





@deepseek_bp.route('/generate/interview-question', methods=['POST'])
def generate_interview_question():
    """生成面试问题"""
    res = ResMsg()

    try:
        data = request.get_json()

        if not data:
            res.update(code=1, msg="请求数据为空")
            return res.data

        job_position = data.get('job_position', '')
        star_workflow_data = data.get('star_workflow_data', '')
        job_analysis_result = data.get('job_analysis_result', '')
        original_workflow_content = data.get('original_workflow_content', '')
        job_resume_workflow_result = data.get('job_resume_workflow_result', '')
        resume_upload_data = data.get('resume_upload_data', '')

        if not job_position:
            res.update(code=1, msg="职位名称不能为空")
            return res.data

        client = DeepSeekClient()

        if not client.is_available():
            res.update(code=1, msg="DeepSeek 服务不可用")
            return res.data

        # 生成面试问题
        result = client.generate_interview_questions(
            job_position=job_position,
            star_workflow_data=star_workflow_data,
            job_analysis_result=job_analysis_result,
            original_workflow_content=original_workflow_content,
            job_resume_workflow_result=job_resume_workflow_result,
            resume_upload_data=resume_upload_data
        )

        if result['success']:
            res.update(code=0, data=result, msg="面试问题生成完成")
        else:
            res.update(code=1, data=result, msg="面试问题生成失败")

    except Exception as e:
        res.update(code=1, msg=f"面试问题生成失败: {str(e)}")

    return res.data


@deepseek_bp.route('/config', methods=['GET'])
def get_config():
    """获取 DeepSeek 配置信息"""
    res = ResMsg()
    
    try:
        client = DeepSeekClient()
        
        config_info = {
            'enabled': client.enabled,
            'base_url': client.base_url,
            'model_chat': client.model_chat,
            'model_reasoner': client.model_reasoner,
            'api_key_set': bool(client.api_key),
            'available': client.is_available()
        }
        
        res.update(code=0, data=config_info, msg="配置信息获取成功")
    
    except Exception as e:
        res.update(code=1, msg=f"获取配置失败: {str(e)}")
    
    return res.data
