#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
面试相关API (来自a1)
"""

from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
import json
import random
from datetime import datetime
import base64
import io
from PIL import Image
import numpy as np
import cv2
# 删除TensorFlow导入，使用PyTorch版本的情绪分析
# from tensorflow.keras.preprocessing.image import img_to_array

from models.interview import Interview
from models.user import User
from models.progress import Progress
from models.ranking import Ranking
from base.core import db
from utils.speech_analyzer import analyze_speech
from utils.emotion_analyzer import analyze_emotion
from utils.content_analyzer import call_spark_api
from algorithm.interview_analysis import generate_report, recommend_learning_path

interviewBp = Blueprint('interview', __name__)

# 面试问题库
interview_questions = {
    "技术类": [
        "请解释一下RESTful API的设计原则",
        "如何处理数据库中的高并发问题？",
        "描述一次你解决复杂技术问题的经历",
        "什么是设计模式？你常用哪些设计模式？",
        "如何优化前端页面加载速度？"
    ],
    "行为类": [
        "描述一次你领导团队完成项目的经历",
        "当你与团队成员意见不合时如何处理？",
        "你如何应对工作中的压力？",
        "描述一次你失败的经历以及你从中学到了什么",
        "你如何确定任务的优先级？"
    ],
    "情景类": [
        "如果产品上线前发现重大bug，你会如何处理？",
        "如果客户要求的功能技术上不可行，你会怎么办？",
        "如果你发现同事的代码有严重问题，你会怎么做？",
        "如果项目进度严重落后，你会采取什么措施？"
    ]
}

@interviewBp.route('/')
@login_required
def interview():
    """面试首页"""
    return jsonify({'status': 'success', 'message': '面试系统准备就绪'})

@interviewBp.route('/get_question', methods=['GET'])
@login_required
def get_question():
    """获取面试问题"""
    category = request.args.get('category', '技术类')
    if category in interview_questions:
        question = random.choice(interview_questions[category])
        return jsonify({'status': 'success', 'question': question, 'category': category})
    return jsonify({'status': 'error', 'message': '问题类别不存在'})

@interviewBp.route('/analyze', methods=['POST'])
@login_required
def analyze():
    """分析面试回答"""
    data = request.json
    question = data.get('question')
    audio_data = data.get('audio')
    video_data = data.get('video')
    category = data.get('category', '技术类')
    
    # 分析语音
    if audio_data:
        speech_result = analyze_speech(audio_data)
        transcript = speech_result.get('transcript', '')
        speech_score = speech_result.get('score', 70)
    else:
        transcript = data.get('transcript', '')
        speech_score = 70
    
    # 分析情绪
    if video_data:
        emotion_result = analyze_emotion(video_data)
        main_emotion = emotion_result.get('main_emotion', '中性')
        emotion_score = emotion_result.get('score', 75)
    else:
        main_emotion = '中性'
        emotion_score = 75
    
    # 分析内容
    content_result = call_spark_api(question, transcript, current_user.id)
    content_score = content_result.get('score', 75)
    
    # 计算总分
    overall_score = int((speech_score + emotion_score + content_score) / 3)
    
    # 保存面试记录
    interview = Interview(
        user_id=current_user.id,
        question=question,
        transcript=transcript,
        overall_score=overall_score,
        speech_score=speech_score,
        emotion_score=emotion_score,
        content_score=content_score,
        main_emotion=main_emotion,
        category=category
    )
    db.session.add(interview)
    
    # 更新用户进度
    progress = Progress(
        user_id=current_user.id,
        metric='overall_score',
        value=overall_score
    )
    db.session.add(progress)
    
    # 更新排名
    ranking = Ranking(
        user_id=current_user.id,
        score=overall_score,
        category=category
    )
    db.session.add(ranking)
    
    db.session.commit()
    
    # 生成学习路径推荐
    scores = {
        'overall_score': overall_score,
        'speech_score': speech_score,
        'emotion_score': emotion_score,
        'content_score': content_score
    }
    recommendations = recommend_learning_path(scores, category)
    
    # 生成报告
    report = generate_report(interview.id)
    
    return jsonify({
        'status': 'success',
        'interview_id': interview.id,
        'overall_score': overall_score,
        'speech_score': speech_score,
        'emotion_score': emotion_score,
        'content_score': content_score,
        'main_emotion': main_emotion,
        'transcript': transcript,
        'feedback': content_result.get('comment', ''),
        'strengths': content_result.get('strengths', ''),
        'improvements': content_result.get('improvements', ''),
        'recommendations': recommendations,
        'report': report
    })

@interviewBp.route('/report/<int:report_id>')
@login_required
def report(report_id):
    """获取面试报告"""
    interview = Interview.query.get_or_404(report_id)
    
    # 验证权限
    if interview.user_id != current_user.id:
        return jsonify({'status': 'error', 'message': '无权限查看此报告'})
    
    # 生成报告
    report = generate_report(report_id)
    
    return jsonify({
        'status': 'success',
        'report': report,
        'interview': {
            'id': interview.id,
            'question': interview.question,
            'transcript': interview.transcript,
            'overall_score': interview.overall_score,
            'speech_score': interview.speech_score,
            'emotion_score': interview.emotion_score,
            'content_score': interview.content_score,
            'main_emotion': interview.main_emotion,
            'date': interview.interview_date.strftime('%Y-%m-%d %H:%M:%S'),
            'category': interview.category
        }
    })

@interviewBp.route('/ranking')
@login_required
def ranking():
    """获取排名信息"""
    # 获取总排名
    rankings = db.session.query(
        User.username,
        db.func.avg(Ranking.score).label('avg_score')
    ).join(Ranking).group_by(User.id).order_by(db.desc('avg_score')).limit(10).all()
    
    # 获取用户自己的排名
    user_rank = db.session.query(
        db.func.count(User.id)
    ).join(Ranking).group_by(User.id).having(
        db.func.avg(Ranking.score) > db.session.query(
            db.func.avg(Ranking.score)
        ).filter(Ranking.user_id == current_user.id).scalar()
    ).count() + 1
    
    # 获取用户的进步情况
    progress_data = db.session.query(
        Progress.date,
        Progress.value
    ).filter(
        Progress.user_id == current_user.id,
        Progress.metric == 'overall_score'
    ).order_by(Progress.date).limit(10).all()
    
    progress = [{'date': date.strftime('%m-%d'), 'value': value} for date, value in progress_data]
    
    return jsonify({
        'status': 'success',
        'rankings': [{'username': username, 'score': round(score, 1)} for username, score in rankings],
        'user_rank': user_rank,
        'progress': progress
    })

@interviewBp.route('/analyze_speech', methods=['POST'])
def analyze_speech_endpoint():
    """分析语音API端点"""
    audio_data = request.json.get('audio')
    if not audio_data:
        return jsonify({'status': 'error', 'message': '未提供音频数据'})

    result = analyze_speech(audio_data)
    return jsonify({
        'status': 'success',
        'transcript': result.get('transcript', ''),
        'score': result.get('score', 70)
    })



@interviewBp.route('/metaverse_interview')
@login_required
def metaverse_interview():
    """元宇宙面试体验"""
    return jsonify({'status': 'success', 'message': '元宇宙面试体验准备就绪'})

@interviewBp.route('/api/interview/job-resume-workflow', methods=['POST', 'OPTIONS'])
def custom_workflow_analysis():
    """调用自定义工作流进行分析 - ID: 7351285351281713152"""
    # 处理OPTIONS请求（CORS预检请求）
    if request.method == 'OPTIONS':
        response = jsonify({'code': 200, 'message': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        return response

    try:
        data = request.get_json()

        # 获取请求参数
        user_input = data.get('userInput', '默认输入内容')
        job_skill = data.get('jobSkill', '默认技能内容')

        # 导入自定义工作流
        from scripts.workflow.job_resume_workflow import execute_job_resume_workflow

        # 调用自定义工作流
        result = execute_job_resume_workflow(user_input, job_skill)

        return jsonify({
            'code': 0,
            'message': '自定义工作流执行成功',
            'data': result
        })

    except Exception as e:
        import traceback
        print(f"自定义工作流执行错误: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'code': 500,
            'message': f"自定义工作流执行错误: {str(e)}",
            'data': None
        })