#!/usr/bin/env python
# encoding: UTF-8
import json
import base64
import requests
import sys
from typing import List, Dict, Any, Optional

def parse_resume_api_response(response_data: str) -> List[Dict[str, str]]:
    """
    解析简历API返回的数据，提取所有简历模板链接
    
    Args:
        response_data: API返回的JSON字符串
    
    Returns:
        简历模板列表，每个模板包含图片URL和Word文档URL
    """
    try:
        # 解析JSON数据
        result = json.loads(response_data)
        
        # 检查返回结果
        code = result['header']['code']
        if code != 0:
            error_msg = result['header'].get('message', '未知错误')
            print(f"API错误: {error_msg}")
            return []
        
        # 获取生成的简历内容
        text_base64 = result['payload']['resData']['text']
        print(f"Base64编码: {text_base64[:50]}...") # 只打印前50个字符
        
        # 解码
        resume_bytes = base64.b64decode(text_base64)
        resume_text = resume_bytes.decode('utf-8')
        print(f"解码后: {resume_text[:100]}...") # 只打印前100个字符
        
        # 解析JSON
        resume_json = json.loads(resume_text)
        print(f"解析JSON成功")
        
        # 检查是否包含links字段
        if 'links' in resume_json and isinstance(resume_json['links'], list) and len(resume_json['links']) > 0:
            return resume_json['links']
        else:
            print("未找到简历模板链接")
            return []
    
    except Exception as e:
        print(f"解析API返回数据失败: {str(e)}")
        return []

def display_resume_templates(templates: List[Dict[str, str]]) -> None:
    """
    显示所有可用的简历模板
    
    Args:
        templates: 简历模板列表
    """
    if not templates:
        print("没有可用的简历模板")
        return
    
    print("\n=== 可用的简历模板 ===")
    for i, template in enumerate(templates, 1):
        img_url = template.get('img_url', '无预览图')
        word_url = template.get('word_url', '无下载链接')
        
        print(f"模板 {i}:")
        print(f"  预览图: {img_url}")
        print(f"  下载链接: {word_url}")
        print("-" * 50)

def select_template(templates: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
    """
    让用户选择一个简历模板
    
    Args:
        templates: 简历模板列表
    
    Returns:
        用户选择的模板，如果用户取消选择则返回None
    """
    if not templates:
        return None
    
    while True:
        try:
            choice = input("\n请选择一个模板 (输入编号，或输入'q'退出): ")
            
            if choice.lower() == 'q':
                return None
            
            index = int(choice) - 1
            if 0 <= index < len(templates):
                selected_template = templates[index]
                print(f"\n已选择模板 {index + 1}")
                return selected_template
            else:
                print(f"无效的选择，请输入1到{len(templates)}之间的数字")
        
        except ValueError:
            print("请输入有效的数字")
        except Exception as e:
            print(f"发生错误: {str(e)}")
            return None

def get_recommended_jobs(resume_info: Dict[str, Any], api_url: str = None) -> List[Dict[str, Any]]:
    """
    基于简历信息获取推荐职位
    
    Args:
        resume_info: 简历信息，包含教育背景、技能等
        api_url: 职位推荐API的URL，如果为None则使用默认API
    
    Returns:
        推荐职位列表
    """
    try:
        # 如果没有提供API URL，使用默认的推荐API
        if api_url is None:
            api_url = "http://localhost:5000/job/getRecomendation"
        
        # 提取简历中的关键信息
        education = resume_info.get('education', '')
        skills = resume_info.get('skills', [])
        experience = resume_info.get('experience', '')
        
        # 构建请求参数
        params = {
            'education': education,
            'skills': ','.join(skills) if isinstance(skills, list) else skills,
            'experience': experience
        }
        
        # 发送请求获取推荐职位
        print(f"正在获取推荐职位...")
        response = requests.get(api_url, params=params)
        
        if response.status_code != 200:
            print(f"API请求失败，状态码: {response.status_code}")
            return []
        
        # 解析返回结果
        result = response.json()
        
        if result.get('code') != 0:
            print(f"获取推荐职位失败: {result.get('msg', '未知错误')}")
            return []
        
        # 返回推荐职位列表
        jobs = result.get('data', [])
        return jobs
    
    except Exception as e:
        print(f"获取推荐职位时发生错误: {str(e)}")
        return []

def display_jobs(jobs: List[Dict[str, Any]]) -> None:
    """
    显示推荐的职位列表
    
    Args:
        jobs: 职位列表
    """
    if not jobs:
        print("\n没有找到推荐职位")
        return
    
    print("\n=== 推荐职位 ===")
    for i, job in enumerate(jobs, 1):
        position_name = job.get('position_name', '未知职位')
        company_name = job.get('company_name', '未知公司')
        salary = f"{job.get('salary0', 0)}-{job.get('salary1', 0)}k" if 'salary0' in job and 'salary1' in job else '薪资未知'
        city = job.get('city', '未知城市')
        education_req = job.get('education', '学历要求未知')
        
        print(f"职位 {i}: {position_name}")
        print(f"  公司: {company_name}")
        print(f"  薪资: {salary}")
        print(f"  城市: {city}")
        print(f"  学历要求: {education_req}")
        print("-" * 50)

def main(api_response_file: str = None, resume_info: Dict[str, Any] = None, job_api_url: str = None):
    """
    主函数，整合所有功能
    
    Args:
        api_response_file: 包含API响应的JSON文件路径，如果为None则从标准输入读取
        resume_info: 简历信息，如果为None则使用默认信息
        job_api_url: 职位推荐API的URL
    """
    try:
        # 获取API响应数据
        if api_response_file:
            print(f"从文件 {api_response_file} 读取API响应...")
            with open(api_response_file, 'r', encoding='utf-8') as f:
                response_data = f.read()
        else:
            print("请输入API响应JSON数据 (输入完成后按Ctrl+D结束):")
            response_data = sys.stdin.read()
        
        # 解析API响应
        templates = parse_resume_api_response(response_data)
        
        if not templates:
            print("未找到有效的简历模板，程序退出")
            return
        
        # 显示所有模板
        display_resume_templates(templates)
        
        # 选择模板
        selected_template = select_template(templates)
        
        if not selected_template:
            print("未选择模板，程序退出")
            return
        
        
        # 获取推荐职位
        jobs = get_recommended_jobs(resume_info, job_api_url)
        
        # 显示推荐职位
        display_jobs(jobs)
        
        print("\n处理完成！")
    
    except Exception as e:
        print(f"程序运行出错: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 解析命令行参数
    import argparse
    
    parser = argparse.ArgumentParser(description='简历API返回数据解析和职位选择工具')
    parser.add_argument('-f', '--file', help='包含API响应的JSON文件路径')
    parser.add_argument('-u', '--api-url', help='职位推荐API的URL')
    
    args = parser.parse_args()
    
    main(api_response_file=args.file, job_api_url=args.api_url) 