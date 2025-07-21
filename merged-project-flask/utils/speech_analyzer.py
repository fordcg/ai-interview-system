#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
语音分析工具 (来自a1)
"""

import speech_recognition as sr
import base64
import io
import random

def analyze_speech(audio_data):
    """分析语音
    
    Args:
        audio_data: Base64编码的音频数据
    
    Returns:
        分析结果字典
    """
    try:
        # 解码Base64音频数据
        audio_bytes = base64.b64decode(audio_data.split(',')[1] if ',' in audio_data else audio_data)
        audio_io = io.BytesIO(audio_bytes)
        
        # 使用SpeechRecognition进行识别
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_io) as source:
            audio = recognizer.record(source)
            transcript = recognizer.recognize_google(audio, language='zh-CN')
        
        # 分析语音质量
        # 实际应该有更复杂的分析，这里简化处理
        words = len(transcript.split())
        speech_score = min(100, max(60, 60 + words * 2))
        
        return {
            'transcript': transcript,
            'score': speech_score,
            'words_count': words
        }
    except Exception as e:
        # 错误处理
        print(f"语音分析错误: {e}")
        # 返回模拟数据
        return {
            'transcript': '很抱歉，无法识别您的语音。',
            'score': 60,
            'words_count': 0,
            'error': str(e)
        } 