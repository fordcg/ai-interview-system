#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
岗位分析工作流模块
用于分析岗位信息并提供与简历匹配的建议
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

def analyze_job_position(position_name="岗位信息"):
    """
    分析岗位信息

    Args:
        position_name: 岗位名称

    Returns:
        dict: 包含分析结果的字典
    """
    print(f"开始分析岗位: {position_name}")
    print(f"API配置: KEY={config.XF_API_KEY[:5]}..., SECRET={config.XF_API_SECRET[:5]}...")

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {config.XF_API_KEY}:{config.XF_API_SECRET}",
    }

    # 岗位分析工作流ID
    job_analysis_flow_id = "7350060834797031426"

    data = {
        "flow_id": job_analysis_flow_id,
        "uid": "123",
        "parameters": {"AGENT_USER_INPUT": position_name},
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
    parser = argparse.ArgumentParser(description='岗位分析工作流')
    parser.add_argument('--position', type=str, help='岗位名称', default='岗位信息')
    args = parser.parse_args()
    
    result = analyze_job_position(args.position)
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main() 