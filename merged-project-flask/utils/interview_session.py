#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
面试会话管理器
管理面试流程、问题序列、状态跟踪
"""

import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class InterviewSession:
    """面试会话类"""
    
    def __init__(self, session_id: str = None, user_id: int = None, job_info: Dict = None):
        """
        初始化面试会话
        
        Args:
            session_id: 会话ID，如果为None则自动生成
            user_id: 用户ID
            job_info: 职位信息
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.user_id = user_id
        self.job_info = job_info or {}
        
        # 会话状态
        self.status = "created"  # created, started, in_progress, paused, completed, failed
        self.created_at = datetime.now()
        self.started_at = None
        self.ended_at = None
        
        # 面试进度
        self.current_stage = "introduction"  # introduction, technical, behavioral, scenario, conclusion
        self.current_question_index = 0
        self.total_questions = 0
        
        # 面试数据
        self.questions = []
        self.answers = []
        self.interactions = []  # 所有交互记录
        self.scores = {}
        self.feedback = {}
        
        # 配置参数
        self.config = {
            "max_questions_per_stage": 3,
            "max_total_time": 30 * 60,  # 30分钟
            "max_answer_time": 3 * 60,  # 3分钟每题
            "enable_follow_up": True,
            "difficulty_level": "medium"
        }
        
        # 实时状态
        self.current_question = None
        self.current_answer = None
        self.question_start_time = None
        self.answer_start_time = None
        
    def start_session(self) -> bool:
        """开始面试会话"""
        try:
            if self.status != "created":
                logger.warning(f"会话{self.session_id}状态不正确，无法开始")
                return False
            
            self.status = "started"
            self.started_at = datetime.now()
            self.current_stage = "introduction"
            
            # 记录开始事件
            self._add_interaction("session_start", {
                "message": "面试会话开始",
                "job_info": self.job_info
            })
            
            logger.info(f"面试会话{self.session_id}已开始")
            return True
            
        except Exception as e:
            logger.error(f"开始面试会话失败: {e}")
            return False
    
    def add_question(self, question: str, question_type: str = "general", metadata: Dict = None) -> str:
        """
        添加面试问题
        
        Args:
            question: 问题内容
            question_type: 问题类型
            metadata: 问题元数据
            
        Returns:
            问题ID
        """
        question_id = str(uuid.uuid4())
        question_data = {
            "id": question_id,
            "content": question,
            "type": question_type,
            "stage": self.current_stage,
            "asked_at": datetime.now(),
            "metadata": metadata or {}
        }
        
        self.questions.append(question_data)
        self.current_question = question_data
        self.question_start_time = datetime.now()
        self.total_questions += 1
        
        # 记录问题事件
        self._add_interaction("question_asked", {
            "question_id": question_id,
            "question": question,
            "type": question_type,
            "stage": self.current_stage
        })
        
        logger.info(f"添加问题: {question[:50]}...")
        return question_id
    
    def add_answer(self, answer: str, question_id: str = None, metadata: Dict = None) -> str:
        """
        添加面试回答
        
        Args:
            answer: 回答内容
            question_id: 对应的问题ID
            metadata: 回答元数据
            
        Returns:
            回答ID
        """
        answer_id = str(uuid.uuid4())
        
        # 如果没有指定问题ID，使用当前问题
        if not question_id and self.current_question:
            question_id = self.current_question["id"]
        
        # 计算回答时长
        answer_duration = None
        if self.question_start_time:
            answer_duration = (datetime.now() - self.question_start_time).total_seconds()
        
        answer_data = {
            "id": answer_id,
            "content": answer,
            "question_id": question_id,
            "answered_at": datetime.now(),
            "duration": answer_duration,
            "metadata": metadata or {}
        }
        
        self.answers.append(answer_data)
        self.current_answer = answer_data
        
        # 记录回答事件
        self._add_interaction("answer_given", {
            "answer_id": answer_id,
            "question_id": question_id,
            "answer": answer,
            "duration": answer_duration
        })
        
        logger.info(f"添加回答: {answer[:50]}...")
        return answer_id
    
    def update_stage(self, new_stage: str) -> bool:
        """
        更新面试阶段
        
        Args:
            new_stage: 新的面试阶段
            
        Returns:
            是否更新成功
        """
        valid_stages = ["introduction", "technical", "behavioral", "scenario", "conclusion"]
        
        if new_stage not in valid_stages:
            logger.warning(f"无效的面试阶段: {new_stage}")
            return False
        
        old_stage = self.current_stage
        self.current_stage = new_stage
        
        # 记录阶段变更
        self._add_interaction("stage_change", {
            "from_stage": old_stage,
            "to_stage": new_stage
        })
        
        logger.info(f"面试阶段从{old_stage}变更为{new_stage}")
        return True
    
    def add_score(self, category: str, score: float, details: Dict = None) -> None:
        """
        添加评分
        
        Args:
            category: 评分类别
            score: 分数
            details: 评分详情
        """
        self.scores[category] = {
            "score": score,
            "details": details or {},
            "scored_at": datetime.now()
        }
        
        # 记录评分事件
        self._add_interaction("score_added", {
            "category": category,
            "score": score,
            "details": details
        })
        
        logger.info(f"添加评分 {category}: {score}")
    
    def add_feedback(self, category: str, feedback: str, feedback_type: str = "general") -> None:
        """
        添加反馈
        
        Args:
            category: 反馈类别
            feedback: 反馈内容
            feedback_type: 反馈类型
        """
        if category not in self.feedback:
            self.feedback[category] = []
        
        feedback_data = {
            "content": feedback,
            "type": feedback_type,
            "created_at": datetime.now()
        }
        
        self.feedback[category].append(feedback_data)
        
        # 记录反馈事件
        self._add_interaction("feedback_added", {
            "category": category,
            "feedback": feedback,
            "type": feedback_type
        })
        
        logger.info(f"添加反馈 {category}: {feedback[:50]}...")
    
    def pause_session(self) -> bool:
        """暂停面试会话"""
        if self.status not in ["started", "in_progress"]:
            return False
        
        self.status = "paused"
        self._add_interaction("session_paused", {"message": "面试会话暂停"})
        logger.info(f"面试会话{self.session_id}已暂停")
        return True
    
    def resume_session(self) -> bool:
        """恢复面试会话"""
        if self.status != "paused":
            return False
        
        self.status = "in_progress"
        self._add_interaction("session_resumed", {"message": "面试会话恢复"})
        logger.info(f"面试会话{self.session_id}已恢复")
        return True
    
    def end_session(self, reason: str = "completed") -> bool:
        """
        结束面试会话
        
        Args:
            reason: 结束原因
            
        Returns:
            是否成功结束
        """
        try:
            if self.status in ["completed", "failed"]:
                return False
            
            self.status = "completed" if reason == "completed" else "failed"
            self.ended_at = datetime.now()
            
            # 记录结束事件
            self._add_interaction("session_ended", {
                "reason": reason,
                "total_duration": self.get_duration(),
                "total_questions": len(self.questions),
                "total_answers": len(self.answers)
            })
            
            logger.info(f"面试会话{self.session_id}已结束，原因: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"结束面试会话失败: {e}")
            return False
    
    def get_duration(self) -> Optional[float]:
        """获取面试持续时间（秒）"""
        if not self.started_at:
            return None
        
        end_time = self.ended_at or datetime.now()
        return (end_time - self.started_at).total_seconds()
    
    def get_current_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            "session_id": self.session_id,
            "status": self.status,
            "stage": self.current_stage,
            "duration": self.get_duration(),
            "question_count": len(self.questions),
            "answer_count": len(self.answers),
            "current_question": self.current_question,
            "scores": self.scores,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """获取面试总结"""
        # 计算平均分
        avg_score = 0
        if self.scores:
            total_score = sum(score_data["score"] for score_data in self.scores.values())
            avg_score = total_score / len(self.scores)
        
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "job_info": self.job_info,
            "status": self.status,
            "duration": self.get_duration(),
            "stages_completed": self._get_completed_stages(),
            "total_questions": len(self.questions),
            "total_answers": len(self.answers),
            "average_score": avg_score,
            "scores": self.scores,
            "feedback": self.feedback,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None
        }
    
    def export_data(self) -> Dict[str, Any]:
        """导出完整面试数据"""
        return {
            "session_info": self.get_summary(),
            "questions": self.questions,
            "answers": self.answers,
            "interactions": self.interactions,
            "config": self.config
        }
    
    def _add_interaction(self, event_type: str, data: Dict[str, Any]) -> None:
        """添加交互记录"""
        interaction = {
            "id": str(uuid.uuid4()),
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.interactions.append(interaction)
    
    def _get_completed_stages(self) -> List[str]:
        """获取已完成的阶段"""
        stages = []
        for interaction in self.interactions:
            if interaction["type"] == "stage_change":
                stages.append(interaction["data"]["from_stage"])
        
        # 添加当前阶段（如果有问题）
        if self.questions:
            stages.append(self.current_stage)
        
        return list(set(stages))


class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        """初始化会话管理器"""
        self.sessions: Dict[str, InterviewSession] = {}
        self.user_sessions: Dict[int, List[str]] = {}  # 用户ID -> 会话ID列表
    
    def create_session(self, user_id: int, job_info: Dict = None) -> InterviewSession:
        """
        创建新的面试会话
        
        Args:
            user_id: 用户ID
            job_info: 职位信息
            
        Returns:
            面试会话实例
        """
        session = InterviewSession(user_id=user_id, job_info=job_info)
        self.sessions[session.session_id] = session
        
        # 记录用户会话
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = []
        self.user_sessions[user_id].append(session.session_id)
        
        logger.info(f"创建面试会话: {session.session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        """获取面试会话"""
        return self.sessions.get(session_id)
    
    def get_user_sessions(self, user_id: int) -> List[InterviewSession]:
        """获取用户的所有面试会话"""
        session_ids = self.user_sessions.get(user_id, [])
        return [self.sessions[sid] for sid in session_ids if sid in self.sessions]
    
    def remove_session(self, session_id: str) -> bool:
        """删除面试会话"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            
            # 从用户会话列表中移除
            if session.user_id in self.user_sessions:
                self.user_sessions[session.user_id].remove(session_id)
            
            # 删除会话
            del self.sessions[session_id]
            logger.info(f"删除面试会话: {session_id}")
            return True
        
        return False
    
    def cleanup_expired_sessions(self, max_age_hours: int = 24) -> int:
        """
        清理过期会话
        
        Args:
            max_age_hours: 最大保留时间（小时）
            
        Returns:
            清理的会话数量
        """
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if session.created_at < cutoff_time:
                expired_sessions.append(session_id)
        
        # 删除过期会话
        for session_id in expired_sessions:
            self.remove_session(session_id)
        
        logger.info(f"清理了{len(expired_sessions)}个过期会话")
        return len(expired_sessions)


# 全局会话管理器实例
session_manager = SessionManager()
