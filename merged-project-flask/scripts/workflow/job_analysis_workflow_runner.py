#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
岗位分析工作流独立运行脚本
"""

import os
import sys
import argparse
import json

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 导入岗位分析工作流模块
from job_analysis_workflow import analyze_job_position
from config import DEFAULT_TIMEOUT

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='岗位分析工作流运行器')
    parser.add_argument('--position', type=str, help='岗位名称', default='岗位信息')
    parser.add_argument('--timeout', type=str, default=f"{DEFAULT_TIMEOUT[0]},{DEFAULT_TIMEOUT[1]}",
                      help=f'超时设置，格式为"连接超时,读取超时"，单位为秒，默认为{DEFAULT_TIMEOUT[0]},{DEFAULT_TIMEOUT[1]}')
    parser.add_argument('--output', type=str, help='输出结果到文件')
    
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
    
    print(f"开始分析岗位: {args.position}")
    
    # 调用岗位分析函数
    result = analyze_job_position(args.position)
    
    # 输出结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到: {args.output}")
    else:
        print("分析结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 检查是否成功
    if result.get("status") == "error":
        print(f"分析过程中出现错误: {result.get('message')}")
        sys.exit(1)
    
    print("岗位分析完成")

if __name__ == "__main__":
    main() 