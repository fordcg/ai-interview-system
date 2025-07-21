#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简历STAR工作流API调用脚本
用于调用讯飞星辰大模型的简历STAR分析工作流

使用方法:
    python resume_star_workflow.py [文本内容]

示例:
    python resume_star_workflow.py "这是一份简历文本内容"
"""

import json
import argparse
import requests
from typing import Dict, Any, Optional, Tuple, Union
import time

# 导入统一配置
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


# 简历STAR工作流ID

def analyze_resume_star(text):

    print(f"开始分析简历经历: {text}")
    print(f"API配置: KEY={config.XF_API_KEY[:5]}..., SECRET={config.XF_API_SECRET[:5]}...")

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {config.XF_API_KEY}:{config.XF_API_SECRET}",
    }

    # 岗位分析工作流ID
    XF_STAR_FLOW_ID = "7350503750390169602"

    data = {
        "flow_id": XF_STAR_FLOW_ID,
        "uid": "12",
        "parameters": {"AGENT_USER_INPUT": text},
        "ext": {},
        "stream": False,
    }

    api_url = "https://xingchen-api.xf-yun.com/workflow/v1/chat/completions"

    try:
        print("正在连接STAR API服务器...")
        start_time = time.time()

        # 使用统一的网络配置发送请求
        response = make_api_request(api_url, data, headers, config.DEFAULT_TIMEOUT)

        response_data = response.text

        end_time = time.time()
        print(f"请求完成，耗时: {end_time - start_time:.2f}秒")

        # 尝试解析JSON响应
        try:
            parsed_data = json.loads(response_data)
            return parsed_data
        except json.JSONDecodeError:
            return {"error": "JSON解析失败", "raw_data": response_data}

    except requests.exceptions.Timeout:
        error_msg = "请求超时，API服务器响应时间过长"
        print(error_msg)
        return {"error": error_msg, "code": 408}
    except requests.exceptions.RequestException as e:
        error_msg = f"请求错误: {str(e)}"
        print(error_msg)
        return {"error": error_msg, "code": 500}
    except Exception as e:
        error_msg = f"调用API失败: {str(e)}"
        print(error_msg)
        return {"error": error_msg, "code": 500}

def format_json(data: Dict[str, Any], indent: int = 2) -> str:
    """
    格式化JSON数据为易读的字符串
    
    Args:
        data: JSON数据
        indent: 缩进空格数
    
    Returns:
        格式化后的JSON字符串
    """
    return json.dumps(data, ensure_ascii=False, indent=indent)

def print_section(title: str, content: Any) -> None:
    """
    打印带有标题的内容区块
    
    Args:
        title: 区块标题
        content: 区块内容
    """
    print(f"\n{'=' * 20} {title} {'=' * 20}")
    if isinstance(content, dict) or isinstance(content, list):
        print(format_json(content))
    else:
        print(content)
    print('=' * (42 + len(title)))

def parse_star_workflow_response(response_data: str) -> Dict[str, Any]:
    """
    解析STAR工作流API的响应数据
    
    Args:
        response_data: API响应的JSON字符串
    
    Returns:
        解析后的数据字典，如果存在content则只返回content内容
    """
    try:
        # 解析JSON数据
        result = json.loads(response_data)
        
        # 如果存在choices且包含content，只返回content内容
        if "choices" in result and len(result["choices"]) > 0:
            choice = result["choices"][0]
            if "delta" in choice and "content" in choice["delta"]:
                return {"content": choice["delta"]["content"]}
        
        # 否则返回完整结果
        return result
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {str(e)}")
        return {"error": "JSON解析错误", "raw_data": response_data}
    except Exception as e:
        print(f"解析错误: {str(e)}")
        return {"error": str(e), "raw_data": response_data}

def print_star_workflow_response(response_data: Dict[str, Any]) -> None:
    """
    打印STAR工作流API的响应数据
    
    Args:
        response_data: 解析后的响应数据
    """
    # 如果只有content字段，直接打印content内容
    if "content" in response_data and len(response_data) == 1:
        print("=== 简历STAR分析结果 ===")
        print(response_data["content"])
        print("=" * 30)
        return
    
    # 打印基本信息
    print_section("STAR工作流基本信息", {
        "code": response_data.get("code", "未知"),
        "message": response_data.get("message", "未知"),
        "id": response_data.get("id", "未知"),
        "created": response_data.get("created", "未知")
    })
    
    # 打印工作流步骤信息
    if "workflow_step" in response_data:
        print_section("STAR工作流步骤", response_data["workflow_step"])
    
    # 打印选择信息
    if "choices" in response_data:
        print_section("STAR分析选择信息", response_data["choices"])
        
        # 单独打印内容（可能很长）
        for i, choice in enumerate(response_data["choices"]):
            if "delta" in choice and "content" in choice["delta"]:
                print_section(f"STAR分析结果 {i+1}", choice["delta"]["content"])
            
            if "delta" in choice and "reasoning_content" in choice["delta"]:
                print_section(f"STAR分析推理 {i+1}", choice["delta"]["reasoning_content"])
    
    # 打印用量信息
    if "usage" in response_data:
        print_section("Token用量", response_data["usage"])
    
    # 打印完整原始数据
    print_section("完整原始数据", response_data)


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='讯飞星辰大模型简历STAR工作流API调用脚本')
    parser.add_argument('--text_content', nargs='?', default="这是一份简历文本内容",
                      help='简历文本内容')
    parser.add_argument('--stream', action='store_true', help='使用流式响应')
    parser.add_argument('--timeout', type=str, default=f"{config.DEFAULT_TIMEOUT[0]},{config.DEFAULT_TIMEOUT[1]}",
                      help=f'超时设置，格式为"连接超时,读取超时"，单位为秒，默认为{config.DEFAULT_TIMEOUT[0]},{config.DEFAULT_TIMEOUT[1]}')
    
    args = parser.parse_args()
    result = analyze_resume_star(args.text_content)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    # 解析超时设置
    try:
        if ',' in args.timeout:
            connect_timeout, read_timeout = map(int, args.timeout.split(','))
            timeout = (connect_timeout, read_timeout)
        else:
            timeout = int(args.timeout)
        print(f"使用超时设置: {timeout} 秒")
    except ValueError:
        print(f"无效的超时格式: {args.timeout}，使用默认值{config.DEFAULT_TIMEOUT}")
        timeout = config.DEFAULT_TIMEOUT
    


if __name__ == "__main__":
    main()
