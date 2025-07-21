#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简历数据获取辅助工具
用于从各种来源获取和整合简历分析数据
"""

import json
import logging
from typing import Dict, Any, Optional, List
from flask import session, current_app

logger = logging.getLogger(__name__)

class ResumeDataHelper:
    """简历数据辅助类"""
    
    def __init__(self):
        """初始化"""
        self.data_keys = {
            'EXTRACTED_SKILLS': 'extractedSkills',
            'RESUME_UPLOAD_DATA': 'resumeUploadData', 
            'STAR_WORKFLOW_DATA': 'starWorkflowData',
            'JOB_ANALYSIS_RESULT': 'jobAnalysisResult',
            'ORIGINAL_WORKFLOW_CONTENT': 'originalWorkflowContent',
            'JOB_RECOMMEND_WORKFLOW_DATA': 'jobRecommendWorkflowData',
            'JOB_RESUME_WORKFLOW_RESULT': 'jobResumeWorkflowResult'
        }
    
    def get_resume_data_from_session(self, user_id: int = None) -> Dict[str, Any]:
        """
        从会话中获取简历数据
        
        Args:
            user_id: 用户ID（可选）
            
        Returns:
            简历数据字典
        """
        resume_data = {}
        
        try:
            # 从Flask session中获取数据
            for key, storage_key in self.data_keys.items():
                if storage_key in session:
                    resume_data[storage_key] = session[storage_key]
                    logger.debug(f"从session获取到 {storage_key}")
            
            return resume_data
            
        except Exception as e:
            logger.error(f"从session获取简历数据失败: {e}")
            return {}
    
    def get_resume_data_from_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        从请求数据中获取简历数据
        
        Args:
            request_data: 请求数据
            
        Returns:
            简历数据字典
        """
        resume_data = {}
        
        try:
            # 直接从请求中获取resume_data
            if 'resume_data' in request_data:
                resume_data = request_data['resume_data']
            
            # 或者从各个字段中获取
            for key, storage_key in self.data_keys.items():
                if storage_key in request_data:
                    resume_data[storage_key] = request_data[storage_key]
            
            return resume_data
            
        except Exception as e:
            logger.error(f"从请求获取简历数据失败: {e}")
            return {}
    
    def format_resume_data_for_ai(self, resume_data: Dict[str, Any]) -> str:
        """
        格式化简历数据供AI使用
        
        Args:
            resume_data: 简历数据
            
        Returns:
            格式化后的文本
        """
        try:
            formatted_text = ""
            
            # 提取的技能
            if resume_data.get('extractedSkills'):
                skills_data = resume_data['extractedSkills']
                if isinstance(skills_data, str):
                    skills_data = json.loads(skills_data)
                
                formatted_text += f"\n【技能分析】\n"
                if isinstance(skills_data, dict):
                    for category, skills in skills_data.items():
                        if skills:
                            formatted_text += f"{category}: {', '.join(skills) if isinstance(skills, list) else skills}\n"
                else:
                    formatted_text += f"技能列表: {skills_data}\n"
            
            # STAR工作流数据
            if resume_data.get('starWorkflowData'):
                star_data = resume_data['starWorkflowData']
                if isinstance(star_data, str):
                    star_data = json.loads(star_data)
                
                formatted_text += f"\n【项目经历分析(STAR)】\n"
                formatted_text += f"{star_data}\n"
            
            # 岗位分析结果
            if resume_data.get('jobAnalysisResult'):
                job_analysis = resume_data['jobAnalysisResult']
                if isinstance(job_analysis, str):
                    job_analysis = json.loads(job_analysis)
                
                formatted_text += f"\n【岗位匹配分析】\n"
                formatted_text += f"{job_analysis}\n"
            
            # 简历岗位匹配度
            if resume_data.get('jobResumeWorkflowResult'):
                match_result = resume_data['jobResumeWorkflowResult']
                if isinstance(match_result, str):
                    match_result = json.loads(match_result)
                
                formatted_text += f"\n【简历岗位匹配度】\n"
                formatted_text += f"{match_result}\n"
            
            # 原始工作流内容
            if resume_data.get('originalWorkflowContent'):
                original_content = resume_data['originalWorkflowContent']
                if isinstance(original_content, str):
                    original_content = json.loads(original_content)
                
                formatted_text += f"\n【详细分析报告】\n"
                formatted_text += f"{original_content}\n"
            
            return formatted_text.strip()
            
        except Exception as e:
            logger.error(f"格式化简历数据失败: {e}")
            return ""
    
    def extract_key_points(self, resume_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        提取简历关键点
        
        Args:
            resume_data: 简历数据
            
        Returns:
            关键点字典
        """
        key_points = {
            'strengths': [],      # 优势/亮点
            'gaps': [],           # 差距/不足
            'skills': [],         # 核心技能
            'projects': [],       # 重要项目
            'experiences': []     # 关键经历
        }
        
        try:
            # 从技能数据中提取
            if resume_data.get('extractedSkills'):
                skills_data = resume_data['extractedSkills']
                if isinstance(skills_data, str):
                    skills_data = json.loads(skills_data)
                
                if isinstance(skills_data, dict):
                    for category, skills in skills_data.items():
                        if skills:
                            if isinstance(skills, list):
                                key_points['skills'].extend(skills)
                            else:
                                key_points['skills'].append(str(skills))
            
            # 从匹配分析中提取优势和差距
            if resume_data.get('jobResumeWorkflowResult'):
                match_result = resume_data['jobResumeWorkflowResult']
                if isinstance(match_result, str):
                    match_result = json.loads(match_result)
                
                # 这里可以根据实际的数据结构来提取优势和差距
                # 示例逻辑，需要根据实际数据格式调整
                if isinstance(match_result, dict):
                    if 'strengths' in match_result:
                        key_points['strengths'] = match_result['strengths']
                    if 'gaps' in match_result:
                        key_points['gaps'] = match_result['gaps']
            
            # 从STAR数据中提取项目经历
            if resume_data.get('starWorkflowData'):
                star_data = resume_data['starWorkflowData']
                if isinstance(star_data, str):
                    star_data = json.loads(star_data)
                
                # 提取项目信息
                if isinstance(star_data, dict) and 'projects' in star_data:
                    key_points['projects'] = star_data['projects']
            
            return key_points
            
        except Exception as e:
            logger.error(f"提取关键点失败: {e}")
            return key_points
    
    def generate_interview_context(self, resume_data: Dict[str, Any], job_info: Dict[str, Any]) -> str:
        """
        生成面试上下文
        
        Args:
            resume_data: 简历数据
            job_info: 职位信息
            
        Returns:
            面试上下文文本
        """
        try:
            context = ""
            
            # 职位信息
            context += f"【目标职位】\n"
            context += f"职位: {job_info.get('position', '未知')}\n"
            context += f"公司: {job_info.get('company', '未知')}\n"
            context += f"类型: {job_info.get('type', '综合面试')}\n"
            context += f"难度: {job_info.get('difficulty', '中级')}\n\n"
            
            # 简历分析数据
            formatted_resume = self.format_resume_data_for_ai(resume_data)
            if formatted_resume:
                context += formatted_resume + "\n\n"
            
            # 关键点提取
            key_points = self.extract_key_points(resume_data)
            
            if key_points['strengths']:
                context += f"【候选人优势】\n"
                for strength in key_points['strengths'][:5]:  # 最多5个
                    context += f"- {strength}\n"
                context += "\n"
            
            if key_points['gaps']:
                context += f"【需要验证的能力差距】\n"
                for gap in key_points['gaps'][:3]:  # 最多3个
                    context += f"- {gap}\n"
                context += "\n"
            
            if key_points['skills']:
                context += f"【核心技能】\n"
                skills_text = ', '.join(key_points['skills'][:10])  # 最多10个技能
                context += f"{skills_text}\n\n"
            
            return context.strip()
            
        except Exception as e:
            logger.error(f"生成面试上下文失败: {e}")
            return ""
    
    def validate_resume_data(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证简历数据完整性
        
        Args:
            resume_data: 简历数据
            
        Returns:
            验证结果
        """
        result = {
            'valid': True,
            'missing_fields': [],
            'invalid_fields': [],
            'warnings': []
        }
        
        try:
            # 检查必要字段
            required_fields = ['extractedSkills', 'starWorkflowData']
            for field in required_fields:
                if field not in resume_data or not resume_data[field]:
                    result['missing_fields'].append(field)
                    result['valid'] = False
            
            # 检查数据格式
            for key, value in resume_data.items():
                if value and isinstance(value, str):
                    try:
                        json.loads(value)
                    except json.JSONDecodeError:
                        # 如果不是JSON格式，检查是否是有效的文本
                        if len(value.strip()) == 0:
                            result['invalid_fields'].append(key)
            
            # 生成警告
            if not resume_data.get('jobAnalysisResult'):
                result['warnings'].append('缺少岗位分析结果，可能影响问题针对性')
            
            if not resume_data.get('jobResumeWorkflowResult'):
                result['warnings'].append('缺少简历匹配度分析，可能影响问题精准度')
            
            return result
            
        except Exception as e:
            logger.error(f"验证简历数据失败: {e}")
            result['valid'] = False
            result['invalid_fields'].append('validation_error')
            return result


# 全局实例
resume_data_helper = ResumeDataHelper()
