#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
音频处理工具
用于SparkOS面试系统的音频格式转换、Base64编码处理等
"""

import base64
import io
import wave
import struct
import numpy as np
from typing import Optional, Tuple, Union
import logging

logger = logging.getLogger(__name__)

class AudioProcessor:
    """音频处理器"""
    
    def __init__(self):
        """初始化音频处理器"""
        self.target_sample_rate = 16000  # SparkOS要求的采样率
        self.target_channels = 1         # 单声道
        self.target_bit_depth = 16       # 16位深度
        self.frame_size = 1280          # SparkOS推荐的帧大小
    
    def process_web_audio(self, audio_data: str) -> Optional[str]:
        """
        处理来自Web的音频数据
        
        Args:
            audio_data: Base64编码的音频数据（可能包含data URL前缀）
            
        Returns:
            处理后的Base64编码音频数据，适合SparkOS使用
        """
        try:
            # 移除data URL前缀（如果存在）
            if ',' in audio_data:
                audio_data = audio_data.split(',')[1]
            
            # 解码Base64
            audio_bytes = base64.b64decode(audio_data)
            
            # 检测音频格式并处理
            if self._is_wav_format(audio_bytes):
                processed_audio = self._process_wav_audio(audio_bytes)
            else:
                # 假设是原始PCM数据
                processed_audio = self._process_raw_audio(audio_bytes)
            
            if processed_audio:
                # 重新编码为Base64
                return base64.b64encode(processed_audio).decode('utf-8')
            
            return None
            
        except Exception as e:
            logger.error(f"处理Web音频失败: {e}")
            return None
    
    def split_audio_frames(self, audio_data: bytes) -> list:
        """
        将音频数据分割为适合SparkOS的帧
        
        Args:
            audio_data: 音频字节数据
            
        Returns:
            音频帧列表
        """
        frames = []
        
        try:
            # 按帧大小分割
            for i in range(0, len(audio_data), self.frame_size):
                frame = audio_data[i:i + self.frame_size]
                
                # 如果最后一帧不足帧大小，用零填充
                if len(frame) < self.frame_size:
                    frame += b'\x00' * (self.frame_size - len(frame))
                
                frames.append(frame)
            
            return frames
            
        except Exception as e:
            logger.error(f"分割音频帧失败: {e}")
            return []
    
    def encode_audio_frame(self, frame_data: bytes) -> str:
        """
        编码音频帧为Base64
        
        Args:
            frame_data: 音频帧字节数据
            
        Returns:
            Base64编码的音频帧
        """
        try:
            return base64.b64encode(frame_data).decode('utf-8')
        except Exception as e:
            logger.error(f"编码音频帧失败: {e}")
            return ""
    
    def convert_sample_rate(self, audio_data: bytes, source_rate: int, target_rate: int = None) -> bytes:
        """
        转换音频采样率
        
        Args:
            audio_data: 原始音频数据
            source_rate: 源采样率
            target_rate: 目标采样率，默认使用self.target_sample_rate
            
        Returns:
            转换后的音频数据
        """
        if target_rate is None:
            target_rate = self.target_sample_rate
        
        if source_rate == target_rate:
            return audio_data
        
        try:
            # 将字节数据转换为numpy数组
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # 计算重采样比例
            ratio = target_rate / source_rate
            new_length = int(len(audio_array) * ratio)
            
            # 简单的线性插值重采样
            indices = np.linspace(0, len(audio_array) - 1, new_length)
            resampled = np.interp(indices, np.arange(len(audio_array)), audio_array)
            
            # 转换回字节数据
            return resampled.astype(np.int16).tobytes()
            
        except Exception as e:
            logger.error(f"转换采样率失败: {e}")
            return audio_data
    
    def convert_to_mono(self, audio_data: bytes, channels: int) -> bytes:
        """
        转换为单声道
        
        Args:
            audio_data: 音频数据
            channels: 原始声道数
            
        Returns:
            单声道音频数据
        """
        if channels == 1:
            return audio_data
        
        try:
            # 将字节数据转换为numpy数组
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # 重塑为多声道格式
            audio_array = audio_array.reshape(-1, channels)
            
            # 取平均值转换为单声道
            mono_array = np.mean(audio_array, axis=1).astype(np.int16)
            
            return mono_array.tobytes()
            
        except Exception as e:
            logger.error(f"转换为单声道失败: {e}")
            return audio_data
    
    def normalize_audio(self, audio_data: bytes) -> bytes:
        """
        音频标准化
        
        Args:
            audio_data: 音频数据
            
        Returns:
            标准化后的音频数据
        """
        try:
            # 将字节数据转换为numpy数组
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # 计算最大值
            max_val = np.max(np.abs(audio_array))
            
            if max_val > 0:
                # 标准化到16位整数范围
                normalized = (audio_array.astype(np.float32) / max_val * 32767).astype(np.int16)
                return normalized.tobytes()
            
            return audio_data
            
        except Exception as e:
            logger.error(f"音频标准化失败: {e}")
            return audio_data
    
    def _is_wav_format(self, audio_bytes: bytes) -> bool:
        """检查是否为WAV格式"""
        return audio_bytes.startswith(b'RIFF') and b'WAVE' in audio_bytes[:12]
    
    def _process_wav_audio(self, wav_data: bytes) -> Optional[bytes]:
        """
        处理WAV格式音频
        
        Args:
            wav_data: WAV音频字节数据
            
        Returns:
            处理后的PCM音频数据
        """
        try:
            # 使用io.BytesIO创建文件对象
            wav_io = io.BytesIO(wav_data)
            
            with wave.open(wav_io, 'rb') as wav_file:
                # 获取音频参数
                channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                frame_rate = wav_file.getframerate()
                frames = wav_file.readframes(wav_file.getnframes())
                
                logger.info(f"WAV音频参数: 声道={channels}, 位深={sample_width*8}, 采样率={frame_rate}")
                
                # 转换为目标格式
                processed_audio = frames
                
                # 转换声道
                if channels != self.target_channels:
                    processed_audio = self.convert_to_mono(processed_audio, channels)
                
                # 转换采样率
                if frame_rate != self.target_sample_rate:
                    processed_audio = self.convert_sample_rate(processed_audio, frame_rate)
                
                # 确保是16位深度
                if sample_width != 2:  # 2字节 = 16位
                    processed_audio = self._convert_bit_depth(processed_audio, sample_width * 8, 16)
                
                return processed_audio
                
        except Exception as e:
            logger.error(f"处理WAV音频失败: {e}")
            return None
    
    def _process_raw_audio(self, raw_data: bytes) -> bytes:
        """
        处理原始PCM音频数据
        
        Args:
            raw_data: 原始音频字节数据
            
        Returns:
            处理后的音频数据
        """
        try:
            # 假设输入是16位PCM数据
            # 在实际应用中，可能需要更复杂的格式检测
            
            # 简单的音量标准化
            processed_audio = self.normalize_audio(raw_data)
            
            return processed_audio
            
        except Exception as e:
            logger.error(f"处理原始音频失败: {e}")
            return raw_data
    
    def _convert_bit_depth(self, audio_data: bytes, source_depth: int, target_depth: int) -> bytes:
        """
        转换音频位深度
        
        Args:
            audio_data: 音频数据
            source_depth: 源位深度
            target_depth: 目标位深度
            
        Returns:
            转换后的音频数据
        """
        if source_depth == target_depth:
            return audio_data
        
        try:
            if source_depth == 8 and target_depth == 16:
                # 8位转16位
                audio_array = np.frombuffer(audio_data, dtype=np.uint8)
                # 转换为有符号16位
                converted = ((audio_array.astype(np.int16) - 128) * 256).astype(np.int16)
                return converted.tobytes()
            
            elif source_depth == 24 and target_depth == 16:
                # 24位转16位（简化处理）
                # 每3个字节转换为2个字节
                samples = []
                for i in range(0, len(audio_data), 3):
                    if i + 2 < len(audio_data):
                        # 取高16位
                        sample = struct.unpack('<i', audio_data[i:i+3] + b'\x00')[0] >> 8
                        samples.append(sample)
                
                return struct.pack('<' + 'h' * len(samples), *samples)
            
            elif source_depth == 32 and target_depth == 16:
                # 32位转16位
                audio_array = np.frombuffer(audio_data, dtype=np.int32)
                converted = (audio_array >> 16).astype(np.int16)
                return converted.tobytes()
            
            else:
                logger.warning(f"不支持的位深度转换: {source_depth} -> {target_depth}")
                return audio_data
                
        except Exception as e:
            logger.error(f"转换位深度失败: {e}")
            return audio_data
    
    def create_silence_frame(self, duration_ms: int = 40) -> str:
        """
        创建静音帧
        
        Args:
            duration_ms: 静音持续时间（毫秒）
            
        Returns:
            Base64编码的静音帧
        """
        try:
            # 计算样本数
            samples = int(self.target_sample_rate * duration_ms / 1000)
            
            # 创建静音数据（全零）
            silence_data = b'\x00' * (samples * 2)  # 16位 = 2字节
            
            # 确保帧大小
            if len(silence_data) > self.frame_size:
                silence_data = silence_data[:self.frame_size]
            elif len(silence_data) < self.frame_size:
                silence_data += b'\x00' * (self.frame_size - len(silence_data))
            
            return base64.b64encode(silence_data).decode('utf-8')
            
        except Exception as e:
            logger.error(f"创建静音帧失败: {e}")
            return ""
    
    def validate_audio_format(self, audio_data: bytes) -> dict:
        """
        验证音频格式
        
        Args:
            audio_data: 音频数据
            
        Returns:
            音频格式信息
        """
        result = {
            'valid': False,
            'format': 'unknown',
            'channels': 0,
            'sample_rate': 0,
            'bit_depth': 0,
            'duration': 0
        }
        
        try:
            if self._is_wav_format(audio_data):
                wav_io = io.BytesIO(audio_data)
                with wave.open(wav_io, 'rb') as wav_file:
                    result.update({
                        'valid': True,
                        'format': 'wav',
                        'channels': wav_file.getnchannels(),
                        'sample_rate': wav_file.getframerate(),
                        'bit_depth': wav_file.getsampwidth() * 8,
                        'duration': wav_file.getnframes() / wav_file.getframerate()
                    })
            else:
                # 假设是原始PCM数据
                result.update({
                    'valid': True,
                    'format': 'pcm',
                    'channels': self.target_channels,
                    'sample_rate': self.target_sample_rate,
                    'bit_depth': self.target_bit_depth,
                    'duration': len(audio_data) / (self.target_sample_rate * 2)
                })
            
        except Exception as e:
            logger.error(f"验证音频格式失败: {e}")
        
        return result


# 全局音频处理器实例
audio_processor = AudioProcessor()
