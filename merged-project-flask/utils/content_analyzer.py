#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
内容分析工具 (来自a1)
"""

import os
import json
import hmac
import hashlib
import base64
import requests
from datetime import datetime

def call_spark_api(question, answer, user_id):
    """调用讯飞星火大模型API进行内容分析
    
    Args:
        question: 面试问题
        answer: 用户回答
        user_id: 用户ID
    
    Returns:
        分析结果字典
    """
    try:
        # 从环境变量获取API密钥
        api_key = os.getenv("SPARK_API_KEY", "your-spark-api-key")
        api_secret = os.getenv("SPARK_API_SECRET", "your-spark-api-secret")
        app_id = os.getenv("SPARK_APP_ID", "your-spark-app-id")
        
        # 生成认证URL
        host = "spark-api.xf-yun.com"
        path = "/v3.1/chat"
        now = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        signature_origin = f"host: {host}\ndate: {now}\nGET {path} HTTP/1.1"
        signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'), digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(signature_sha).decode('utf-8')
        authorization_origin = f'api_key="{api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
        auth_url = f"https://{host}{path}?authorization={authorization}&date={now}&host={host}"
        
        # 提示词
        prompt = f"""
        你是一名专业的面试官，请根据以下面试问题和应聘者的回答，对应聘者的回答内容进行评分（0-100分），并给出评语。
        评分标准包括：专业性、逻辑性、完整性、与岗位的匹配度等方面。

        面试问题：{question}
        应聘者回答：{answer}

        请直接输出一个JSON格式的结果，包含以下字段：
        - score（分数）
        - comment（评语，不超过100字）
        - strengths（应聘者的优势，不超过50字）
        - improvements（需要改进的地方，不超过50字）
        - star_feedback（使用STAR原则分析回答的结构完整性）
        """
        
        # 构造请求数据
        data = {
            "header": {"app_id": app_id},
            "parameter": {
                "chat": {
                    "domain": "generalv3",
                    "temperature": 0.5,
                    "max_tokens": 4096
                }
            },
            "payload": {
                "message": {
                    "text": [{"role": "user", "content": prompt}]
                }
            }
        }
        
        # 添加错误重试机制
        for attempt in range(3):
            try:
                response = requests.post(auth_url, json=data, headers={"Content-Type": "application/json"}, timeout=10)
                response.raise_for_status()
                result = response.json()
                
                # 解析结果
                if 'payload' in result and 'choices' in result['payload']:
                    content = result['payload']['choices']['text'][0]['content']
                    try:
                        return json.loads(content)
                    except:
                        # 尝试提取JSON部分
                        try:
                            start_index = content.find('{')
                            end_index = content.rfind('}') + 1
                            return json.loads(content[start_index:end_index])
                        except:
                            # 记录错误日志
                            print(f"解析星火API响应失败: {content}")
                return {"score": 75, "comment": "内容评估成功，但解析失败"}
            except Exception as e:
                print(f"调用讯飞星火API失败(尝试{attempt + 1}): {e}")
                import time
                time.sleep(1)  # 重试前等待
        
        return {"score": 75, "comment": "API调用失败"}
    except Exception as e:
        print(f"内容分析错误: {e}")
        # 返回默认值
        return {
            "score": 75,
            "comment": "无法分析内容",
            "strengths": "回答了问题",
            "improvements": "需要更具体的例子",
            "error": str(e)
        } 