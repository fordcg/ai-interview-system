#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
问题模式配置文件
用于定义数字人的不同问题模式和提问逻辑
"""

import json
import os
from typing import Dict, List, Any, Optional

# 问题模式类型
MODE_INTERVIEW = "interview"  # 面试模式
MODE_SURVEY = "survey"        # 调研模式
MODE_CUSTOMER = "customer"    # 客服模式
MODE_CHAT = "chat"            # 聊天模式

class QuestionMode:
    """问题模式基类"""
    
    def __init__(self, mode_id: str, name: str, description: str):
        """
        初始化问题模式
        
        Args:
            mode_id: 模式ID
            name: 模式名称
            description: 模式描述
        """
        self.mode_id = mode_id
        self.name = name
        self.description = description
        self.questions = []
        self.current_index = 0
        self.is_completed = False
    
    def add_question(self, question: str, follow_ups: Optional[List[str]] = None) -> None:
        """
        添加问题
        
        Args:
            question: 问题内容
            follow_ups: 可选的跟进问题列表
        """
        self.questions.append({
            "question": question,
            "follow_ups": follow_ups or [],
            "asked": False,
            "answered": False
        })
    
    def get_next_question(self) -> Optional[str]:
        """
        获取下一个问题
        
        Returns:
            下一个问题内容，如果没有更多问题则返回None
        """
        if self.current_index >= len(self.questions):
            self.is_completed = True
            return None
        
        question_data = self.questions[self.current_index]
        if not question_data["asked"]:
            question_data["asked"] = True
            return question_data["question"]
        
        # 如果当前问题已经被问过但未回答，不进行下一个问题
        if not question_data["answered"]:
            return None
            
        # 移动到下一个问题
        self.current_index += 1
        return self.get_next_question()
    
    def mark_current_answered(self) -> None:
        """标记当前问题已回答"""
        if self.current_index < len(self.questions):
            self.questions[self.current_index]["answered"] = True
    
    def get_prompt(self) -> str:
        """
        获取问题模式的提示词
        
        Returns:
            提示词内容
        """
        questions_text = "\n".join([f"{i+1}. {q['question']}" for i, q in enumerate(self.questions)])
        
        prompt = f"""你是一名专业的AI助手，名叫小星。你需要按照以下问题模式主动向用户提问：

问题模式：
{questions_text}

提问规则：
- 每次只问一个问题
- 等待用户回答后再问下一个问题
- 保持友好专业的语气
- 如果用户回答不完整，可以追问
- 按顺序进行，不要跳跃

现在开始第一个问题：{self.questions[0]['question'] if self.questions else ''}"""
        
        return prompt
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            字典表示
        """
        return {
            "mode_id": self.mode_id,
            "name": self.name,
            "description": self.description,
            "questions": self.questions,
            "current_index": self.current_index,
            "is_completed": self.is_completed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuestionMode':
        """
        从字典创建问题模式
        
        Args:
            data: 字典数据
            
        Returns:
            问题模式实例
        """
        mode = cls(data["mode_id"], data["name"], data["description"])
        mode.questions = data["questions"]
        mode.current_index = data["current_index"]
        mode.is_completed = data["is_completed"]
        return mode


# 预定义的问题模式
def get_interview_mode() -> QuestionMode:
    """获取面试模式"""
    mode = QuestionMode(MODE_INTERVIEW, "面试模式", "用于面试场景的问题模式")
    
    # 添加面试问题
    mode.add_question("请简单介绍一下你自己", ["能详细说说你的教育背景吗？", "你有哪些兴趣爱好？"])
    mode.add_question("请谈谈你的工作经验", ["你在上一份工作中的主要职责是什么？", "你遇到过哪些挑战？"])
    mode.add_question("你有哪些专业技能？", ["你如何保持这些技能的更新？", "你认为自己的优势是什么？"])
    mode.add_question("你的职业规划是什么？", ["你对未来五年有什么规划？", "你希望在我们公司实现什么目标？"])
    mode.add_question("为什么想加入我们公司？", ["你对我们公司了解多少？", "你认为你能为我们公司带来什么价值？"])
    
    return mode

def get_survey_mode() -> QuestionMode:
    """获取调研模式"""
    mode = QuestionMode(MODE_SURVEY, "调研模式", "用于市场调研场景的问题模式")
    
    # 添加调研问题
    mode.add_question("您使用我们的产品有多长时间了？")
    mode.add_question("您最喜欢我们产品的哪些功能？")
    mode.add_question("您认为我们的产品有哪些需要改进的地方？")
    mode.add_question("您会向朋友推荐我们的产品吗？为什么？")
    mode.add_question("您对我们未来的产品有什么建议或期望？")
    
    return mode

def get_customer_mode() -> QuestionMode:
    """获取客服模式"""
    mode = QuestionMode(MODE_CUSTOMER, "客服模式", "用于客户服务场景的问题模式")
    
    # 添加客服问题
    mode.add_question("您好，请问有什么可以帮助您的？")
    mode.add_question("请详细描述您遇到的问题")
    mode.add_question("这个问题是什么时候开始出现的？")
    mode.add_question("您之前尝试过什么解决方法吗？")
    mode.add_question("还有其他需要我帮助的吗？")
    
    return mode

# 问题模式管理器
class QuestionModeManager:
    """问题模式管理器"""
    
    def __init__(self):
        """初始化问题模式管理器"""
        self.modes = {}
        self._load_default_modes()
    
    def _load_default_modes(self) -> None:
        """加载默认问题模式"""
        self.add_mode(get_interview_mode())
        self.add_mode(get_survey_mode())
        self.add_mode(get_customer_mode())
    
    def add_mode(self, mode: QuestionMode) -> None:
        """
        添加问题模式
        
        Args:
            mode: 问题模式实例
        """
        self.modes[mode.mode_id] = mode
    
    def get_mode(self, mode_id: str) -> Optional[QuestionMode]:
        """
        获取问题模式
        
        Args:
            mode_id: 模式ID
            
        Returns:
            问题模式实例，如果不存在则返回None
        """
        return self.modes.get(mode_id)
    
    def get_prompt(self, mode_id: str) -> Optional[str]:
        """
        获取问题模式的提示词
        
        Args:
            mode_id: 模式ID
            
        Returns:
            提示词内容，如果模式不存在则返回None
        """
        mode = self.get_mode(mode_id)
        if mode:
            return mode.get_prompt()
        return None
    
    def list_modes(self) -> List[Dict[str, Any]]:
        """
        列出所有问题模式
        
        Returns:
            问题模式列表
        """
        return [
            {
                "mode_id": mode.mode_id,
                "name": mode.name,
                "description": mode.description,
                "question_count": len(mode.questions)
            }
            for mode in self.modes.values()
        ]

# 全局问题模式管理器实例
question_mode_manager = QuestionModeManager()

# 获取问题模式管理器实例
def get_question_mode_manager() -> QuestionModeManager:
    """
    获取问题模式管理器实例
    
    Returns:
        问题模式管理器实例
    """
    return question_mode_manager
