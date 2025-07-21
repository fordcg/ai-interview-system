#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
增强版工作流API独立运行脚本
"""

import os
import sys
import argparse

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 导入增强版工作流API和文本提取模块
import enhanced_workflow_api_chat
import document_text_extractor
from config import DEFAULT_TIMEOUT

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='讯飞星辰大模型工作流API调用增强脚本')
    parser.add_argument('file_path', nargs='?', default=None,
                      help='文档文件路径')
    parser.add_argument('--text', help='直接使用文本内容而不是文件')
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
    
    # 获取文本内容
    text_content = args.text
    
    # 如果提供了文件路径，则从文件中提取文本
    if args.file_path and not text_content:
        print(f"从文件提取文本: {args.file_path}")
        text_content = document_text_extractor.extract_text_from_document(args.file_path)
        
        if not text_content:
            print("文本提取失败，程序退出")
            sys.exit(1)
        
        print(f"成功提取文本，长度: {len(text_content)} 字符")
    
    # 如果没有提供文件路径和文本内容，使用默认文本
    if not text_content:
        text_content = "这是一份简历文本内容示例，用于测试讯飞星辰大模型工作流API。"
        print(f"使用默认文本内容: {text_content}")
    
    print(f"运行增强版工作流API，文本长度: {len(text_content)} 字符")
    
    # 调用API，传递超时设置
    response_data = enhanced_workflow_api_chat.call_workflow_api(text_content, args.stream, timeout=timeout)
    
    if not response_data:
        print("未获取到API响应，程序退出")
        sys.exit(1)
    
    # 解析响应
    parsed_response = enhanced_workflow_api_chat.parse_workflow_response(response_data)
    
    # 打印响应
    enhanced_workflow_api_chat.print_workflow_response(parsed_response)

if __name__ == "__main__":
    main() 