#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
自定义工作流模块 - ID: 7351285351281713152
通用工作流处理模块，可根据具体需求进行定制
"""

import json
import argparse
import requests
import time
# 修改导入方式，使用相对导入
try:
    from scripts.workflow import config
except ImportError:
    import config

try:
    from network_config import make_api_request
except ImportError:
    # 如果导入失败，使用requests直接发送请求
    import requests
    def make_api_request(url, data, headers, timeout):
        response = requests.post(url, json=data, headers=headers, timeout=timeout, proxies=None)
        response.raise_for_status()
        return response

def execute_job_resume_workflow(user_input="默认输入内容", job_skill="默认技能内容"):
    """
    执行自定义工作流

    Args:
        user_input: 用户输入内容，将作为工作流的输入参数
        job_skill: 岗位技能要求

    Returns:
        dict: 包含工作流执行结果的字典
    """
    print(f"开始执行自定义工作流，输入内容: {user_input} 技能内容: {job_skill}")
    
    print(f"API配置: KEY={config.XF_API_KEY[:5]}..., SECRET={config.XF_API_SECRET[:5]}...")

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {config.XF_API_KEY}:{config.XF_API_SECRET}",
    }

    # 自定义工作流ID
    custom_workflow_id = "7351285351281713152"

    data = {
        "flow_id": custom_workflow_id,
        "uid": "123",
        "parameters": {"AGENT_USER_INPUT": user_input, "job_skill": job_skill},
        "ext": {},
        "stream": False,
    }

    api_url = "https://xingchen-api.xf-yun.com/workflow/v1/chat/completions"

    try:
        print("正在连接API服务器...")
        start_time = time.time()

        # 使用统一的网络配置发送请求
        response = make_api_request(api_url, data, headers, config.DEFAULT_TIMEOUT)

        response_data = response.text

        end_time = time.time()
        print(f"请求完成，耗时: {end_time - start_time:.2f}秒")

        # 尝试解析JSON响应
        try:
            parsed_data = json.loads(response_data)
            return {"status": "success", "data": parsed_data}
        except json.JSONDecodeError:
            return {"status": "success", "data": response_data}

    except requests.exceptions.Timeout:
        error_msg = "请求超时，API服务器响应时间过长"
        print(error_msg)
        return {"status": "error", "message": error_msg}
    except requests.exceptions.RequestException as e:
        error_msg = f"请求错误: {str(e)}"
        print(error_msg)
        return {"status": "error", "message": error_msg}
    except Exception as e:
        error_msg = f"调用API失败: {str(e)}"
        print(error_msg)
        return {"status": "error", "message": error_msg}

def main():
    """命令行入口函数"""
    parser = argparse.ArgumentParser(description='自定义工作流 - ID: 7351285351281713152')
    parser.add_argument('--input', type=str, help='用户输入内容', default='默认输入内容')
    parser.add_argument('--job-skill', type=str, help='岗位技能要求', default='默认技能内容')
    parser.add_argument('--verbose', action='store_true', help='显示详细输出')
    args = parser.parse_args()

    if args.verbose:
        print(f"工作流ID: 7351285351281713152")
        print(f"输入参数: {args.input}")
        print(f"技能要求: {args.job_skill}")

    result = execute_job_resume_workflow(args.input, args.job_skill)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
