#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
讯飞星辰大模型工作流API调用增强脚本
用于完整解析和打印API响应的所有字段

使用方法:
    python enhanced_workflow_api_chat.py [文本内容]

示例:
    python enhanced_workflow_api_chat.py "这是一份简历文本内容"
"""

import json
import sys
import argparse
import requests
from typing import Dict, Any, Optional, Tuple, Union
import time
import os

# 导入统一配置
from config import (
    XF_API_KEY,
    XF_API_SECRET,
    XF_FLOW_ID,
    DEFAULT_TIMEOUT,
    MAX_TEXT_LENGTH
)
try:
    from network_config import make_api_request
except ImportError:
    # 如果导入失败，使用requests直接发送请求
    def make_api_request(url, data, headers, timeout):
        response = requests.post(url, json=data, headers=headers, timeout=timeout, proxies=None)
        response.raise_for_status()
        return response

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

def parse_workflow_response(response_data: str) -> Dict[str, Any]:
    """
    解析工作流API的响应数据
    
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

def print_workflow_response(response_data: Dict[str, Any]) -> None:
    """
    打印工作流API的响应数据
    
    Args:
        response_data: 解析后的响应数据
    """
    # 如果只有content字段，直接打印content内容
    if "content" in response_data and len(response_data) == 1:
        print(response_data["content"])
        return
    
    # 打印基本信息
    print_section("基本信息", {
        "code": response_data.get("code", "未知"),
        "message": response_data.get("message", "未知"),
        "id": response_data.get("id", "未知"),
        "created": response_data.get("created", "未知")
    })
    
    # 打印工作流步骤信息
    if "workflow_step" in response_data:
        print_section("工作流步骤", response_data["workflow_step"])
    
    # 打印选择信息
    if "choices" in response_data:
        print_section("选择信息", response_data["choices"])
        
        # 单独打印内容（可能很长）
        for i, choice in enumerate(response_data["choices"]):
            if "delta" in choice and "content" in choice["delta"]:
                print_section(f"选择 {i+1} 内容", choice["delta"]["content"])
            
            if "delta" in choice and "reasoning_content" in choice["delta"]:
                print_section(f"选择 {i+1} 推理内容", choice["delta"]["reasoning_content"])
    
    # 打印用量信息
    if "usage" in response_data:
        print_section("Token用量", response_data["usage"])
    
    # 打印事件数据
    if "event_data" in response_data:
        print_section("事件数据", response_data["event_data"])
    
    # 打印原始数据
    print_section("完整原始数据", response_data)

def call_workflow_api(text_content: str, stream: bool = False, timeout: Union[int, Tuple[int, int]] = DEFAULT_TIMEOUT) -> Optional[str]:
    """
    调用讯飞星辰大模型工作流API
    
    Args:
        text_content: 文档文本内容
        stream: 是否使用流式响应
        timeout: 超时设置，可以是单一值（同时用于连接和读取超时）或元组(连接超时, 读取超时)
    
    Returns:
        API响应或None（如果失败）
    """
    print(f"调用讯飞星辰大模型工作流API，文本长度: {len(text_content)} 字符")
    print(f"API配置: KEY={XF_API_KEY[:5]}..., SECRET={XF_API_SECRET[:5]}..., FLOW_ID={XF_FLOW_ID}")
    print(f"超时设置: {timeout} 秒")
    
    # 如果文本内容太长，可能需要截断
    if len(text_content) > MAX_TEXT_LENGTH:
        print(f"警告: 文本内容过长 ({len(text_content)} 字符)，将截断到 {MAX_TEXT_LENGTH} 字符")
        text_content = text_content[:MAX_TEXT_LENGTH]
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        "Authorization": f"Bearer {XF_API_KEY}:{XF_API_SECRET}",
    }
    
    # 准备请求数据
    data = {
        "flow_id": XF_FLOW_ID,
        "uid": "13",
        "parameters": {"AGENT_USER_INPUT": text_content},
        "ext": {},
        "stream": stream,
    }
    
    api_url = "https://xingchen-api.xf-yun.com/workflow/v1/chat/completions"
    
    try:
        print("正在连接简历分析API服务器...")
        start_time = time.time()

        # 使用统一的网络配置发送请求
        response = make_api_request(api_url, data, headers, timeout)

        response_data = response.text

        end_time = time.time()
        print(f"请求完成，耗时: {end_time - start_time:.2f}秒")

        return response_data

    except requests.exceptions.Timeout:
        print("请求超时，API服务器响应时间过长")
        return None
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {str(e)}")
        return None
    except Exception as e:
        print(f"调用API失败: {str(e)}")
        return None

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='讯飞星辰大模型工作流API调用增强脚本')
    parser.add_argument('text_content', nargs='?', default="这是一份简历文本内容",
                      help='文档文本内容')
    parser.add_argument('--stream', action='store_true', help='使用流式响应')
    parser.add_argument('--timeout', type=str, default=f"{DEFAULT_TIMEOUT[0]},{DEFAULT_TIMEOUT[1]}",
                      help=f'超时设置，格式为"连接超时,读取超时"，单位为秒，默认为{DEFAULT_TIMEOUT[0]},{DEFAULT_TIMEOUT[1]}')
    
    args = parser.parse_args()
    
    # 解析超时设置
    try:
        if ',' in args.timeout:
            connect_timeout, read_timeout = map(int, args.timeout.split(','))
            timeout = (connect_timeout, read_timeout)
        else:
            timeout = int(args.timeout)
        print(f"使用超时设置: {timeout} 秒")
    except ValueError:
        print(f"无效的超时格式: {args.timeout}，使用默认值{DEFAULT_TIMEOUT}")
        timeout = DEFAULT_TIMEOUT
    
    # 调用API
    response_data = call_workflow_api(args.text_content, args.stream, timeout=timeout)
    
    if not response_data:
        print("未获取到API响应，程序退出")
        return
    
    # 解析响应
    parsed_response = parse_workflow_response(response_data)
    

    
    # 打印响应
    print_workflow_response(parsed_response)

if __name__ == "__main__":
    main() 