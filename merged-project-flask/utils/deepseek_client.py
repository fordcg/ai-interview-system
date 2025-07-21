#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DeepSeek API 客户端工具类
提供与 DeepSeek API 交互的完整功能
"""

import sys
import os
import time
import json
from typing import Dict, Any, Optional, List, Union, Generator
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

try:
    from openai import OpenAI
except ImportError:
    print("警告: 未安装 openai 包，请运行: pip install openai")
    OpenAI = None

from config import Config


class DeepSeekClient:
    """DeepSeek API 客户端类"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化 DeepSeek 客户端
        
        Args:
            api_key: API 密钥，如果不提供则从配置文件读取
            base_url: API 基础URL，如果不提供则从配置文件读取
        """
        self.api_key = api_key or Config.DEEPSEEK_API_KEY
        self.base_url = base_url or Config.DEEPSEEK_BASE_URL
        self.model_chat = Config.DEEPSEEK_MODEL_CHAT
        self.model_reasoner = Config.DEEPSEEK_MODEL_REASONER
        self.enabled = Config.DEEPSEEK_ENABLED
        
        # 验证配置
        self._validate_config()
        
        # 初始化 OpenAI 客户端
        if OpenAI and self.enabled and self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        else:
            self.client = None
    
    def _validate_config(self) -> bool:
        """
        验证配置是否正确
        
        Returns:
            配置是否有效
        """
        if not self.enabled:
            print("DeepSeek API 功能未启用")
            return False
        
        if not self.api_key:
            print("DeepSeek API Key 未设置")
            return False
        
        if not OpenAI:
            print("OpenAI SDK 未安装")
            return False
        
        return True
    
    def is_available(self) -> bool:
        """
        检查 DeepSeek 客户端是否可用
        
        Returns:
            是否可用
        """
        return self.client is not None and self._validate_config()
    
    def chat(self, 
             messages: List[Dict[str, str]], 
             model: Optional[str] = None,
             temperature: float = 0.7,
             max_tokens: Optional[int] = None,
             stream: bool = False,
             **kwargs) -> Dict[str, Any]:
        """
        进行聊天对话
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            model: 使用的模型，默认为 deepseek-chat
            temperature: 温度参数，控制随机性
            max_tokens: 最大生成token数
            stream: 是否使用流式响应
            **kwargs: 其他参数
        
        Returns:
            API 响应结果
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'DeepSeek 客户端不可用',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            # 使用指定模型或默认聊天模型
            model = model or self.model_chat
            
            # 构建请求参数
            request_params = {
                'model': model,
                'messages': messages,
                'temperature': temperature,
                'stream': stream,
                **kwargs
            }
            
            if max_tokens:
                request_params['max_tokens'] = max_tokens
            
            print(f"调用 DeepSeek API: {model}")
            start_time = time.time()
            
            # 发送请求
            response = self.client.chat.completions.create(**request_params)
            
            end_time = time.time()
            print(f"API 调用完成，耗时: {end_time - start_time:.2f}秒")
            
            if stream:
                return {
                    'success': True,
                    'stream': response,
                    'model': model,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': True,
                    'content': response.choices[0].message.content,
                    'model': model,
                    'usage': response.usage.dict() if response.usage else None,
                    'timestamp': datetime.now().isoformat()
                }
        
        except Exception as e:
            print(f"DeepSeek API 调用失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def simple_chat(self, user_message: str, system_message: Optional[str] = None) -> str:
        """
        简单的聊天接口

        Args:
            user_message: 用户消息
            system_message: 系统消息（可选）

        Returns:
            AI 回复内容
        """
        messages = []

        if system_message:
            messages.append({"role": "system", "content": system_message})

        messages.append({"role": "user", "content": user_message})

        result = self.chat(messages)

        if result['success']:
            return result['content']
        else:
            return f"错误: {result['error']}"

    def generate_text(self,
                     prompt: str,
                     model: Optional[str] = None,
                     temperature: float = 0.7,
                     max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """
        文本生成接口

        Args:
            prompt: 提示文本
            model: 使用的模型
            temperature: 温度参数
            max_tokens: 最大生成token数

        Returns:
            生成结果
        """
        messages = [{"role": "user", "content": prompt}]
        return self.chat(messages, model=model, temperature=temperature, max_tokens=max_tokens)

    def chat_stream(self,
                   messages: List[Dict[str, str]],
                   model: Optional[str] = None,
                   temperature: float = 0.7,
                   max_tokens: Optional[int] = None) -> Generator[str, None, None]:
        """
        流式聊天接口

        Args:
            messages: 消息列表
            model: 使用的模型
            temperature: 温度参数
            max_tokens: 最大生成token数

        Yields:
            流式响应的文本片段
        """
        result = self.chat(messages, model=model, temperature=temperature,
                          max_tokens=max_tokens, stream=True)

        if not result['success']:
            yield f"错误: {result['error']}"
            return

        try:
            for chunk in result['stream']:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"流式响应错误: {str(e)}"

    def analyze_interview_answer(self,
                               question: str,
                               answer: str,
                               job_position: str = "通用职位") -> Dict[str, Any]:
        """
        分析面试回答

        Args:
            question: 面试问题
            answer: 用户回答
            job_position: 职位名称

        Returns:
            分析结果
        """
        system_message = """你是一名资深技术面试官，需要根据候选人的回答评估面试表现。请严格按以下要求执行：
1. 输入：面试问题 + 候选人回答
2. 分析维度：
   - 专业性和技术准确性（1-5分）
   - 逻辑清晰度和表达（1-5分）
   - 回复完整性（1-5分）
   - 岗位匹配度（1-5分）
   - 实践经验展示（1-5分）
   - overall_score（1-5分，综合平均分）
   - improvement_suggestions（具体改进建议数组）
3. 输出要求：
   • 必须生成纯JSON对象
   • 严格保持以下结构，禁止额外字段

### 输出模板
```json
{
  "评估": {
    "专业性和技术准确性": 1,
    "逻辑清晰度和表达": 1,
    "回复完整性": 1,
    "岗位匹配度": 1,
    "实践经验展示": 1,
    "overall_score": 1,
    "improvement_suggestions": [
      "具体改进建议1",
      "具体改进建议2",
      "具体改进建议3"
    ]
  }
}
```"""

        user_message = f"""
职位：{job_position}
问题：{question}
回答：{answer}

请严格按照输出模板分析这个回答的质量并给出评分和建议。
        """

        result = self.chat([
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ], model=self.model_chat)  # 使用聊天模型

        if result['success']:
            try:
                # 尝试解析JSON响应
                content = result['content']
                # 如果响应包含JSON，尝试提取
                if '{' in content and '}' in content:
                    start_idx = content.find('{')
                    end_idx = content.rfind('}') + 1
                    json_str = content[start_idx:end_idx]
                    parsed_result = json.loads(json_str)
                    return {
                        'success': True,
                        'analysis': parsed_result,
                        'raw_content': content,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {
                        'success': True,
                        'analysis': {'content': content},
                        'raw_content': content,
                        'timestamp': datetime.now().isoformat()
                    }
            except json.JSONDecodeError:
                return {
                    'success': True,
                    'analysis': {'content': result['content']},
                    'raw_content': result['content'],
                    'timestamp': datetime.now().isoformat()
                }
        else:
            return result

    def generate_interview_questions(self,
                                   job_position: str,
                                   star_workflow_data: str = "",
                                   job_analysis_result: str = "",
                                   original_workflow_content: str = "",
                                   job_resume_workflow_result: str = "",
                                   resume_upload_data: str = "") -> Dict[str, Any]:
        """
        基于5个数据模块生成深度面试问题

        Args:
            job_position: 职位名称
            star_workflow_data: 项目STAR结构数据
            job_analysis_result: 岗位要求分析结果
            original_workflow_content: 简历能力项数据
            job_resume_workflow_result: 评估结果
            resume_upload_data: 简历文本数据

        Returns:
            生成的面试问题
        """
        system_message = """你作为资深技术面试官，请基于以下5个数据模块生成6个深度面试问题。要求：
1. 必须结合所有模块数据，特别关注{job_resume_workflow_result}的评估结论
2. 问题需验证：技能缺口弥补方案、STAR经历真实性、未匹配技能的可迁移性
3. 按此JSON格式输出：
{
  "target_position": "[岗位名称]",
  "questions": [
    {"type": "技术验证", "focus": "核心技能", "text": "问题"},
    {"type": "行为深挖", "focus": "经验缺口", "text": "问题"},
    {"type": "情境推演", "focus": "能力迁移", "text": "问题"},
    ...共6个
  ]
}

数据模块说明：
### 1. starWorkflowData (项目STAR结构)：
[在此粘贴项目经历STAR详情]

### 2. jobAnalysisResult (岗位要求)：
[在此粘贴核心职责/必备技能/软技能/经验要求]

### 3. originalWorkflowContent (简历能力项)：
[在此粘贴匹配&未匹配的技能清单]

### 4. jobResumeWorkflowResult (评估结果)：
"简历技能不符合岗位要求，缺乏[具体经验]经验"

### 5. resumeUploadData (简历文本)：
[在此粘贴关键简历片段]"""

        user_message = f"""请基于以下数据为{job_position}职位生成6个深度面试问题：

### 1. starWorkflowData (项目STAR结构)：
{star_workflow_data if star_workflow_data else "暂无项目STAR数据"}

### 2. jobAnalysisResult (岗位要求)：
{job_analysis_result if job_analysis_result else "暂无岗位分析数据"}

### 3. originalWorkflowContent (简历能力项)：
{original_workflow_content if original_workflow_content else "暂无简历能力项数据"}

### 4. jobResumeWorkflowResult (评估结果)：
{job_resume_workflow_result if job_resume_workflow_result else "暂无评估结果"}

### 5. resumeUploadData (简历文本)：
{resume_upload_data if resume_upload_data else "暂无简历文本数据"}

请严格按照要求的JSON格式输出6个深度面试问题。"""

        result = self.chat([
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ], model=self.model_chat)

        if result['success']:
            try:
                # 尝试解析JSON响应
                content = result['content']
                if '{' in content and '}' in content:
                    start_idx = content.find('{')
                    end_idx = content.rfind('}') + 1
                    json_str = content[start_idx:end_idx]
                    parsed_result = json.loads(json_str)
                    return {
                        'success': True,
                        'questions': parsed_result,
                        'job_position': job_position,
                        'raw_content': content,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    # 如果不是JSON格式，尝试解析为文本列表
                    lines = [line.strip() for line in content.split('\n') if line.strip()]
                    questions = []
                    for i, line in enumerate(lines):
                        if line and not line.startswith('#') and not line.startswith('##'):
                            questions.append({
                                'id': i + 1,
                                'question': line,
                                'type': '综合问题'
                            })

                    return {
                        'success': True,
                        'questions': questions[:6],  # 固定返回6个问题
                        'job_position': job_position,
                        'question_count': len(questions[:6]),
                        'raw_content': content,
                        'timestamp': datetime.now().isoformat()
                    }
            except json.JSONDecodeError:
                return {
                    'success': True,
                    'questions': [{'question': result['content'], 'type': '综合问题'}],
                    'job_position': job_position,
                    'question_count': 1,
                    'raw_content': result['content'],
                    'timestamp': datetime.now().isoformat()
                }
        else:
            return result

    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        分析简历内容

        Args:
            resume_text: 简历文本

        Returns:
            分析结果
        """
        system_message = """你是一名专业的HR，请分析简历内容并提取关键信息。
        请从以下维度进行分析：
        1. 个人基本信息
        2. 教育背景
        3. 工作经验
        4. 技能特长
        5. 项目经验
        6. 简历质量评估

        请返回结构化的JSON格式结果。"""

        user_message = f"请分析以下简历内容：\n\n{resume_text}"

        result = self.chat([
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ], model=self.model_chat)

        return result

    def test_connection(self) -> Dict[str, Any]:
        """
        测试 API 连接

        Returns:
            连接测试结果
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'DeepSeek 客户端不可用',
                'timestamp': datetime.now().isoformat()
            }

        try:
            # 发送简单的测试请求
            test_result = self.simple_chat("你好，请回复'连接成功'")

            return {
                'success': True,
                'message': '连接测试成功',
                'response': test_result,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'连接测试失败: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }


# 使用示例和测试函数
def example_usage():
    """使用示例"""
    print("=== DeepSeek 客户端使用示例 ===")

    # 创建客户端实例
    client = DeepSeekClient()

    # 检查可用性
    if not client.is_available():
        print("DeepSeek 客户端不可用，请检查配置")
        return

    print("1. 测试连接...")
    test_result = client.test_connection()
    print(f"连接测试结果: {test_result}")

    if test_result['success']:
        print("\n2. 简单聊天测试...")
        response = client.simple_chat("请介绍一下你自己")
        print(f"AI回复: {response}")

        print("\n3. 面试回答分析测试...")
        analysis = client.analyze_interview_answer(
            question="请介绍一下你的项目经验",
            answer="我参与过多个Web开发项目，使用Python和JavaScript技术栈",
            job_position="Web开发工程师"
        )
        print(f"分析结果: {analysis}")


if __name__ == "__main__":
    example_usage()
