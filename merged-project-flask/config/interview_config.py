#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
面试配置管理
SparkOS API配置、面试参数设置
"""

import os
from typing import Dict, Any, Optional

class InterviewConfig:
    """面试配置类"""
    
    def __init__(self):
        """初始化配置"""
        self._config = self._load_default_config()
        self._load_env_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        return {
            # 讯飞超拟人TTS配置
            'xunfei_tts': {
                'app_id': os.getenv('XUNFEI_APP_ID', 'your-app-id'),
                'api_key': os.getenv('XUNFEI_API_KEY', 'your-api-key'),
                'api_secret': os.getenv('XUNFEI_API_SECRET', 'your-api-secret'),
                'voice': 'x5_lingyuyan_flow',  # 聆玉言（成年女）
                'base_url': 'wss://cbm01.cn-huabei-1.xf-yun.com/v1/private/mcd9m97e6',
                'timeout': 30
            },
            
            # 音频配置
            'audio': {
                'sample_rate': 16000,
                'channels': 1,
                'bit_depth': 16,
                'frame_size': 1280,
                'encoding': 'raw',
                'max_duration': 300,  # 最大录音时长（秒）
                'silence_threshold': 0.01,
                'vad_threshold': 50  # 语音活动检测阈值
            },
            
            # TTS配置
            'tts': {
                'vcn': 'x5_lingxiaoyue_flow',  # 默认女性面试官
                'speed': 50,
                'volume': 50,
                'pitch': 50,
                'encoding': 'lame',  # MP3格式
                'sample_rate': 16000
            },
            
            # 面试流程配置
            'interview': {
                'max_questions': 10,
                'max_duration': 1800,  # 30分钟
                'question_timeout': 180,  # 每题3分钟
                'stages': [
                    'introduction',
                    'technical', 
                    'behavioral',
                    'scenario',
                    'conclusion'
                ],
                'questions_per_stage': 2,
                'enable_follow_up': True,
                'auto_next_question': True
            },
            
            # 评分配置
            'scoring': {
                'weights': {
                    'content': 0.4,
                    'speech': 0.3,
                    'emotion': 0.2,
                    'timing': 0.1
                },
                'thresholds': {
                    'excellent': 90,
                    'good': 80,
                    'average': 70,
                    'poor': 60
                }
            },
            
            # 会话管理配置
            'session': {
                'max_sessions_per_user': 5,
                'session_timeout': 3600,  # 1小时
                'cleanup_interval': 86400,  # 24小时
                'max_inactive_time': 300  # 5分钟无活动自动结束
            },
            
            # 日志配置
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file_path': 'logs/interview.log',
                'max_size': 10485760,  # 10MB
                'backup_count': 5
            },
            
            # 安全配置
            'security': {
                'rate_limit': {
                    'requests_per_minute': 60,
                    'requests_per_hour': 1000
                },
                'allowed_origins': ['*'],
                'max_file_size': 52428800,  # 50MB
                'allowed_audio_formats': ['wav', 'mp3', 'webm', 'ogg']
            }
        }
    
    def _load_env_config(self):
        """从环境变量加载配置"""
        # 讯飞TTS配置
        if os.getenv('XUNFEI_APP_ID'):
            self._config['xunfei_tts']['app_id'] = os.getenv('XUNFEI_APP_ID')
        if os.getenv('XUNFEI_API_KEY'):
            self._config['xunfei_tts']['api_key'] = os.getenv('XUNFEI_API_KEY')
        if os.getenv('XUNFEI_API_SECRET'):
            self._config['xunfei_tts']['api_secret'] = os.getenv('XUNFEI_API_SECRET')
        if os.getenv('XUNFEI_VOICE'):
            self._config['xunfei_tts']['voice'] = os.getenv('XUNFEI_VOICE')
        
        # 面试配置
        if os.getenv('INTERVIEW_MAX_DURATION'):
            self._config['interview']['max_duration'] = int(os.getenv('INTERVIEW_MAX_DURATION'))
        if os.getenv('INTERVIEW_MAX_QUESTIONS'):
            self._config['interview']['max_questions'] = int(os.getenv('INTERVIEW_MAX_QUESTIONS'))
        
        # 日志配置
        if os.getenv('LOG_LEVEL'):
            self._config['logging']['level'] = os.getenv('LOG_LEVEL')
        if os.getenv('LOG_FILE_PATH'):
            self._config['logging']['file_path'] = os.getenv('LOG_FILE_PATH')
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            key: 配置键，支持点号分隔的嵌套键
            value: 配置值
        """
        keys = key.split('.')
        config = self._config
        
        # 导航到最后一级的父级
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
    
    def get_sparkos_config(self) -> Dict[str, Any]:
        """获取SparkOS配置"""
        return self._config['sparkos'].copy()
    
    def get_audio_config(self) -> Dict[str, Any]:
        """获取音频配置"""
        return self._config['audio'].copy()
    
    def get_tts_config(self) -> Dict[str, Any]:
        """获取TTS配置"""
        return self._config['tts'].copy()
    
    def get_interview_config(self) -> Dict[str, Any]:
        """获取面试配置"""
        return self._config['interview'].copy()
    
    def get_scoring_config(self) -> Dict[str, Any]:
        """获取评分配置"""
        return self._config['scoring'].copy()
    
    def get_session_config(self) -> Dict[str, Any]:
        """获取会话配置"""
        return self._config['session'].copy()
    
    def validate_config(self) -> Dict[str, Any]:
        """
        验证配置
        
        Returns:
            验证结果
        """
        errors = []
        warnings = []
        
        # 验证讯飞TTS配置
        xunfei_tts_config = self._config['xunfei_tts']
        if xunfei_tts_config['app_id'] == 'XXXXXXXX':
            errors.append('讯飞App ID未配置')
        if xunfei_tts_config['api_key'] == 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX':
            errors.append('讯飞API Key未配置')
        if xunfei_tts_config['api_secret'] == 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX':
            errors.append('讯飞API Secret未配置')
        
        # 验证音频配置
        audio_config = self._config['audio']
        if audio_config['sample_rate'] not in [8000, 16000, 24000, 48000]:
            warnings.append(f"音频采样率 {audio_config['sample_rate']} 可能不被支持")
        
        # 验证面试配置
        interview_config = self._config['interview']
        if interview_config['max_duration'] < 300:
            warnings.append('面试最大时长过短，建议至少5分钟')
        if interview_config['max_questions'] < 3:
            warnings.append('面试问题数量过少，建议至少3个问题')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def update_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """
        从字典更新配置
        
        Args:
            config_dict: 配置字典
        """
        def deep_update(base_dict, update_dict):
            for key, value in update_dict.items():
                if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                    deep_update(base_dict[key], value)
                else:
                    base_dict[key] = value
        
        deep_update(self._config, config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            配置字典
        """
        return self._config.copy()
    
    def save_to_file(self, file_path: str) -> None:
        """
        保存配置到文件
        
        Args:
            file_path: 文件路径
        """
        import json
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)
    
    def load_from_file(self, file_path: str) -> None:
        """
        从文件加载配置
        
        Args:
            file_path: 文件路径
        """
        import json
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
                self.update_from_dict(config_dict)


class InterviewPrompts:
    """面试提示词管理"""
    
    def __init__(self):
        """初始化提示词"""
        self.prompts = {
            'system': {
                'interviewer': """你是一名专业的AI面试官，名叫小星。你的任务是基于简历分析数据和岗位要求，生成精准的面试问题。

核心策略：
1. 深挖亮点(匹配点)：针对简历中与岗位强相关的项目/技能/成就，生成深入探讨的问题，验证真实性、深度和思考过程
2. 探查差距(差距点)：针对识别出的潜在能力差距维度，生成问题来评估求职者在该方面的实际水平或潜力
3. 验证基础与潜力：针对岗位必备的基础知识或技能，生成问题验证掌握程度
4. STAR原则引导：对于行为类问题，引导候选人按STAR原则(Situation, Task, Action, Result)组织回答

问题生成示例：
- 深挖亮点："您在简历中提到在项目[项目名称]中负责[职责]并取得[成果]。请详细描述您在该项目中遇到的最大技术挑战，以及您是如何解决的？请按STAR原则组织回答。"
- 探查差距："岗位要求[差距能力]，但简历中缺乏直接体现。请描述一个体现您在这方面能力的具体例子。"
- 验证基础："您提到熟悉[关键技能]，请解释[核心概念]并举例说明实际应用。"

请用自然、亲切的语调进行对话，每次回答控制在30秒以内。""",
                
                'technical': """作为技术面试官，请重点关注：
1. 技术基础知识的掌握程度
2. 实际项目经验和解决问题的能力
3. 代码质量和最佳实践的理解
4. 学习能力和技术视野
请根据候选人的技术背景调整问题难度。""",
                
                'behavioral': """作为行为面试官，请重点评估：
1. 沟通表达能力
2. 团队协作精神
3. 解决问题的思路
4. 抗压能力和适应性
5. 职业规划和发展意愿
请通过具体的情景问题来了解候选人。""",
                
                'scenario': """请设计情景化问题来评估候选人：
1. 在压力下的决策能力
2. 处理冲突的技巧
3. 创新思维和解决方案
4. 领导力和影响力
请结合具体的工作场景提问。"""
            },
            
            'questions': {
                'opening': [
                    "您好！欢迎参加今天的面试。请先简单介绍一下自己。",
                    "很高兴见到您！能否用几分钟时间介绍一下您的背景和经历？",
                    "欢迎！让我们从自我介绍开始，请告诉我您的基本情况。"
                ],
                
                'closing': [
                    "感谢您今天的面试表现。您还有什么问题想要了解的吗？",
                    "面试即将结束，您对我们公司或这个职位还有什么疑问吗？",
                    "最后，您有什么想要补充的或者想了解的吗？"
                ],
                
                'transition': [
                    "接下来我们聊聊技术方面的问题。",
                    "现在让我们转到行为问题。",
                    "下面我想了解一下您的项目经验。"
                ]
            }
        }
    
    def get_prompt(self, category: str, key: str = None) -> Optional[str]:
        """
        获取提示词
        
        Args:
            category: 提示词类别
            key: 具体键值
            
        Returns:
            提示词内容
        """
        if key:
            return self.prompts.get(category, {}).get(key)
        else:
            return self.prompts.get(category)
    
    def get_system_prompt(self, interview_type: str = 'interviewer') -> str:
        """
        获取系统提示词
        
        Args:
            interview_type: 面试类型
            
        Returns:
            系统提示词
        """
        return self.prompts['system'].get(interview_type, self.prompts['system']['interviewer'])


# 全局配置实例
interview_config = InterviewConfig()
interview_prompts = InterviewPrompts()
