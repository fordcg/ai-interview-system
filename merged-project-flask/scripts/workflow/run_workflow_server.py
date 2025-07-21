#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
启动简历工作流服务器
"""

import os
import sys
import argparse


# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 使用绝对导入
from resume_workflow import app
import enhanced_workflow_api_chat
import document_text_extractor
from config import DEFAULT_TIMEOUT

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='启动简历工作流服务器')
    parser.add_argument('--host', default='0.0.0.0', help='服务器主机地址')
    parser.add_argument('--port', type=int, default=8000, help='服务器端口')
    parser.add_argument('--debug', action='store_true', help='是否启用调试模式')
    parser.add_argument('--test', action='store_true', help='测试增强版工作流API')
    parser.add_argument('--file', help='测试用文档文件路径')
    parser.add_argument('--text', help='测试用文本内容')
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
    
    # 测试增强版工作流API
    if args.test:
        text_content = args.text
        
        # 如果提供了文件路径但没有文本内容，则从文件中提取文本
        if args.file and not text_content:
            print(f"从文件提取文本: {args.file}")
            text_content = document_text_extractor.extract_text_from_document(args.file)
            
            if not text_content:
                print("文本提取失败，程序退出")
                sys.exit(1)
            
            print(f"成功提取文本，长度: {len(text_content)} 字符")
        
        # 如果没有提供文件路径和文本内容，使用默认文本
        if not text_content:
            text_content = "这是一份简历文本内容示例，用于测试讯飞星辰大模型工作流API。"
            print(f"使用默认文本内容: {text_content}")
        
        print(f"测试增强版工作流API，文本长度: {len(text_content)} 字符")
        

        response_data = enhanced_workflow_api_chat.call_workflow_api(text_content, args.stream, timeout=timeout)
        if response_data:          
            # 否则解析并打印完整响应
            parsed_response = enhanced_workflow_api_chat.parse_workflow_response(response_data)
            enhanced_workflow_api_chat.print_workflow_response(parsed_response)
        return
    
    print(f"启动简历工作流服务器，地址: http://{args.host}:{args.port}/")
    print(f"上传目录: {app.config['UPLOAD_FOLDER']}")
    print(f"提示: 使用 --test 参数可以测试增强版工作流API")
    
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main() 