#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
工具函数模块初始化
"""

# 导出情感分析器相关类和函数
from .emotion_analyzer import EmotionAnalyzer, get_emotion_analyzer, EMOTION_LABELS_CN, analyze_emotion, get_emotion_distribution, reset_emotion_stats 