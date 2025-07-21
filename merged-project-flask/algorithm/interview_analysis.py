#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
面试分析算法 (来自a1)
"""

from datetime import datetime

def generate_report(interview_id):
    """生成面试报告
    
    Args:
        interview_id: 面试记录ID
    
    Returns:
        面试报告字典
    """
    # 实际应从数据库中查询面试记录
    # 这里使用模拟数据
    from models.interview import Interview, db
    
    interview = Interview.query.get(interview_id)
    if not interview:
        return {
            'status': 'error',
            'message': '面试记录不存在'
        }
    
    # 获取用户历史面试数据
    user_interviews = Interview.query.filter_by(user_id=interview.user_id).order_by(Interview.interview_date).all()
    
    # 计算历史平均分
    avg_score = sum(i.overall_score for i in user_interviews) / len(user_interviews) if user_interviews else 0
    
    # 计算进步情况
    progress = interview.overall_score - avg_score if len(user_interviews) > 1 else 0
    
    # 分析优势和不足
    strengths = []
    weaknesses = []
    
    if interview.speech_score >= 80:
        strengths.append('语言表达能力强')
    elif interview.speech_score < 60:
        weaknesses.append('语言表达需要提升')
    
    if interview.emotion_score >= 80:
        strengths.append('情绪控制良好')
    elif interview.emotion_score < 60:
        weaknesses.append('情绪管理需要加强')
    
    if interview.content_score >= 80:
        strengths.append('专业知识扎实')
    elif interview.content_score < 60:
        weaknesses.append('专业知识需要补充')
    
    # 生成报告
    report = {
        'interview_id': interview.id,
        'user_id': interview.user_id,
        'date': interview.interview_date.strftime('%Y-%m-%d %H:%M:%S'),
        'question': interview.question,
        'category': interview.category,
        'scores': {
            'overall': interview.overall_score,
            'speech': interview.speech_score,
            'emotion': interview.emotion_score,
            'content': interview.content_score
        },
        'main_emotion': interview.main_emotion,
        'analysis': {
            'strengths': strengths,
            'weaknesses': weaknesses,
            'progress': progress,
            'avg_score': round(avg_score, 1),
            'interview_count': len(user_interviews)
        },
        'recommendations': recommend_learning_path({
            'overall_score': interview.overall_score,
            'speech_score': interview.speech_score,
            'emotion_score': interview.emotion_score,
            'content_score': interview.content_score
        }, interview.category)
    }
    
    return report

def recommend_learning_path(scores, category):
    """根据用户表现推荐学习路径
    
    Args:
        scores: 分数字典，包含各项得分
        category: 面试问题类别
    
    Returns:
        推荐列表
    """
    recommendations = []
    
    # 语言表达改进
    if scores.get('speech_score', 0) < 70:
        recommendations.append({
            "type": "课程",
            "title": "高效表达技巧",
            "description": "提升语言组织能力和表达流畅度",
            "url": "/learning/speech"
        })
    
    # 技术类专业知识
    if category == "技术类" and scores.get('content_score', 0) < 75:
        recommendations.append({
            "type": "题库",
            "title": "技术面试常见问题解析",
            "description": "掌握核心概念和解题思路",
            "url": "/questions/tech"
        })
    
    # 情绪管理
    if scores.get('emotion_score', 0) < 65:
        recommendations.append({
            "type": "视频",
            "title": "面试情绪管理技巧",
            "description": "学习如何在压力下保持自信",
            "url": "/videos/emotion"
        })
    
    # 如果所有分数都很高，推荐进阶内容
    if all(score > 85 for score in scores.values()):
        recommendations.append({
            "type": "模拟",
            "title": "高阶面试挑战",
            "description": "挑战更复杂的面试场景",
            "url": "/interview/advanced"
        })
    
    return recommendations 