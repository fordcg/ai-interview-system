#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简历处理工作流脚本
将ResumeUploader.vue组件上传的PDF文档与讯飞星辰大模型API调用集成，并调用简历处理API
"""

import os
import sys
import json
import http.client
import requests
from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename

# 修改相对导入为绝对导入
# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import enhanced_workflow_api_chat
import document_text_extractor
from config import (
    UPLOAD_FOLDER, 
    TEMP_UPLOAD_FOLDER, 
    ALLOWED_EXTENSIONS, 
    MAX_CONTENT_LENGTH,
    DEFAULT_TIMEOUT,
    allowed_file
)

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

def call_workflow_api(text_content):
    """
    调用讯飞星辰大模型工作流API
    
    Args:
        text_content: 文档文本内容
    
    Returns:
        API响应
    """
    print(f"调用讯飞星辰大模型工作流API，文本长度: {len(text_content)} 字符")
    
    # 使用增强版工作流API调用模块，设置更长的超时时间
    response_data = enhanced_workflow_api_chat.call_workflow_api(text_content, stream=False, timeout=DEFAULT_TIMEOUT)
    
    if response_data:
        # 解析并打印响应
        parsed_response = enhanced_workflow_api_chat.parse_workflow_response(response_data)
        enhanced_workflow_api_chat.print_workflow_response(parsed_response)
        
        return response_data
    else:
        print("调用API失败")
        return None

def parse_resume_templates(response_data):
    """
    调用简历模板解析API
    
    Args:
        response_data: 讯飞API返回的JSON字符串
    
    Returns:
        API响应
    """
    print("调用简历模板解析API")
    
    api_url = "http://localhost:5000/api/resume/parse_templates"
    headers = {"Content-Type": "application/json"}
    data = {"response_data": response_data}
    
    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        print(f"简历模板解析结果: {json.dumps(result, ensure_ascii=False, indent=2)[:200]}...")
        return result
    
    except Exception as e:
        print(f"调用简历模板解析API失败: {str(e)}")
        return None

def complete_resume_workflow(text_content):
    """
    完整的简历处理工作流
    
    Args:
        text_content: 简历文本内容
    
    Returns:
        处理结果
    """
    print("\n===== 开始简历处理工作流 =====\n")
    
    # 步骤1: 调用讯飞星辰大模型工作流API
    print("\n--- 步骤1: 调用讯飞星辰大模型工作流API ---\n")
    workflow_response = call_workflow_api(text_content)
    
    if not workflow_response:
        print("错误: 调用讯飞星辰大模型工作流API失败")
        return {
            'success': False,
            'message': "调用讯飞星辰大模型工作流API失败",
            'data': None
        }
    
    # 步骤2: 解析简历模板
    print("\n--- 步骤2: 解析简历模板 ---\n")
    templates_result = parse_resume_templates(workflow_response)
    
    if not templates_result or templates_result.get('code') != 0:
        error_message = "解析简历模板失败"
        if templates_result and templates_result.get('message'):
            error_message = templates_result.get('message')
        
        print(f"错误: {error_message}")
        return {
            'success': False,
            'message': error_message,
            'data': None
        }
    
    # 整合结果
    result = {
        'success': True,
        'message': "简历处理工作流完成",
        'data': {
            'templates': templates_result.get('data', {}).get('templates', [])
        }
    }
    
    print("\n===== 简历处理工作流完成 =====\n")
    return result

# 创建一个简单的Flask应用来测试集成
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 配置CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# 处理所有OPTIONS请求
@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    response = app.make_default_options_response()
    # CORS头部已在@app.after_request中统一设置，此处不再重复添加
    return response

@app.route('/')
def index():
    """根路径处理程序，显示欢迎页面和API使用说明"""
    return """
    <html>
        <head>
            <title>简历工作流API服务</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                }
                h1 {
                    color: #2c3e50;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 10px;
                }
                h2 {
                    color: #3498db;
                    margin-top: 20px;
                }
                pre {
                    background: #f8f8f8;
                    border: 1px solid #ddd;
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                }
                .endpoint {
                    margin-bottom: 20px;
                    background: #f9f9f9;
                    padding: 15px;
                    border-radius: 5px;
                    border-left: 4px solid #3498db;
                }
                .method {
                    font-weight: bold;
                    color: #e74c3c;
                }
            </style>
        </head>
        <body>
            <h1>简历工作流API服务</h1>
            <p>这是一个用于处理简历文档的工作流API服务，基于讯飞星辰大模型API。</p>
            
            <h2>可用的API端点</h2>
            
            <div class="endpoint">
                <h3><span class="method">POST</span> /api/upload</h3>
                <p>上传简历文件（PDF或Word文档）</p>
                <pre>
curl -X POST -F "file=@resume.pdf" http://localhost:8000/api/upload
                </pre>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">GET</span> /api/uploads/&lt;filename&gt;</h3>
                <p>获取已上传的文件</p>
                <pre>
curl http://localhost:8000/api/uploads/filename.pdf
                </pre>
            </div>
            
            <div class="endpoint">
                <h3><span class="method">POST</span> /api/workflow/resume</h3>
                <p>处理简历文档，调用讯飞星辰大模型工作流API</p>
                <p>支持三种参数格式：</p>
                <ol>
                    <li><code>file_path</code>：文件路径（推荐）</li>
                    <li><code>text_content</code>：文本内容（推荐）</li>
                    <li><code>pdf_link</code>：PDF文档链接（兼容旧版，不推荐）</li>
                </ol>
                <pre>
# 方式1：使用文件路径（推荐）
curl -X POST -H "Content-Type: application/json" \
    -d '{"file_path": "/path/to/resume.pdf"}' \
    http://localhost:8000/api/workflow/resume

# 方式2：使用文本内容（推荐）
curl -X POST -H "Content-Type: application/json" \
    -d '{"text_content": "简历文本内容..."}' \
    http://localhost:8000/api/workflow/resume

# 方式3：使用PDF链接（兼容旧版，不推荐）
curl -X POST -H "Content-Type: application/json" \
    -d '{"pdf_link": "http://example.com/resume.pdf"}' \
    http://localhost:8000/api/workflow/resume
                </pre>
            </div>
            
            <h2>使用示例</h2>
            <p>1. 上传简历文件</p>
            <pre>
curl -X POST -F "file=@resume.pdf" http://localhost:8000/api/upload
            </pre>
            
            <p>2. 使用返回的文件路径调用工作流API</p>
            <pre>
curl -X POST -H "Content-Type: application/json" \
    -d '{"file_path": "/uploads/123456_resume.pdf"}' \
    http://localhost:8000/api/workflow/resume
            </pre>
            
            <p>更多信息请参考 <a href="https://github.com/your-username/your-repo">项目文档</a></p>
        </body>
    </html>
    """

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """文件上传API"""
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '没有文件部分',
                'data': None
            }), 400
        
        file = request.files['file']
        
        # 检查文件名是否为空
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '没有选择文件',
                'data': None
            }), 400
        
        # 检查文件类型是否允许
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': '文件类型不允许，请上传PDF或Word文档',
                'data': None
            }), 400
        
        # 保存文件
        filename = secure_filename(file.filename)
        # 添加UUID前缀，确保文件名唯一
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        print(f"\n===== 文件上传成功 =====")
        print(f"文件名: {filename}")
        print(f"唯一文件名: {unique_filename}")
        print(f"文件路径: {file_path}")
        
        # 从文件中提取文本
        print(f"\n===== 开始提取文本 =====")
        text_content = document_text_extractor.extract_text_from_document(file_path)
        
        if not text_content:
            return jsonify({
                'success': False,
                'message': '无法从文件中提取文本',
                'data': None
            }), 500
        
        print(f"成功提取文本，长度: {len(text_content)} 字符")
        print(f"文本预览: {text_content[:200]}...")
        
        # 自动调用工作流处理（异步方式，不阻塞响应）
        def process_workflow_async():
            print(f"\n===== 开始异步处理工作流 =====")
            print(f"文本长度: {len(text_content)} 字符")
            
            # 调用增强版工作流API，使用提取的文本内容
            response_data = enhanced_workflow_api_chat.call_workflow_api(text_content, stream=False)
            
            if response_data:
                # 解析并打印响应
                parsed_response = enhanced_workflow_api_chat.parse_workflow_response(response_data)
                enhanced_workflow_api_chat.print_workflow_response(parsed_response)
                
                # 解析简历模板
                templates_result = parse_resume_templates(response_data)
                
                print(f"\n===== 工作流处理完成 =====")
                if templates_result and templates_result.get('code') == 0:
                    print(f"成功提取 {len(templates_result.get('data', {}).get('templates', []))} 个简历模板")
                else:
                    print("未能成功解析简历模板")
            else:
                print(f"\n===== 工作流处理失败 =====")
        
        # 在新线程中启动工作流处理
        import threading
        thread = threading.Thread(target=process_workflow_async)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': '文件上传成功，文本提取完成，工作流处理已在后台启动',
            'data': {
                'filename': filename,
                'file_path': file_path,
                'text_length': len(text_content),
                'text_preview': text_content[:200] + ('...' if len(text_content) > 200 else '')
            }
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f"服务器错误: {str(e)}",
            'data': None
        }), 500

@app.route('/api/uploads/<filename>')
def uploaded_file(filename):
    """获取上传的文件"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/workflow/resume', methods=['POST', 'OPTIONS'])
def resume_workflow_api():
    """简历工作流API"""
    if request.method == 'OPTIONS':
        response = jsonify({'code': 200, 'message': 'OK'})
        # CORS头部已在@app.after_request中统一设置，此处不再重复添加
        return response
    try:
        print(f"\n===== 接收到工作流处理请求 =====")
        print(f"请求内容类型: {request.content_type}")
        print(f"请求数据: {request.data.decode('utf-8') if request.data else '无数据'}")
        print(f"请求表单: {request.form}")
        print(f"请求文件: {request.files}")
        print(f"请求参数: {request.args}")
        print(f"请求JSON: {request.json if request.is_json else '非JSON请求'}")
        
        # 初始化变量
        text_content = None

        
        # 处理JSON请求

        
        data = request.get_json()
           
                
         
        text_content = data.get('text_content', '')

        # 使用已导入的enhanced_workflow_api_chat模块
        result = enhanced_workflow_api_chat.call_workflow_api(text_content)
        print(f"调用工作流API返回结果: {result}")
        return jsonify({'code': 0, 'message': '成功调用工作流API', 'data': result})
    except Exception as e:
        import traceback
        print(f"调用简历分析工作流API异常: {e}")
        print(traceback.format_exc())
        return jsonify({
            'code': 500,
            'message': f"服务器错误: {str(e)}",
            'data': None
        })

@app.route('/api/workflow/star', methods=['POST', 'OPTIONS'])
def star_workflow_api():
    """STAR工作流API"""
    if request.method == 'OPTIONS':
        response = jsonify({'code': 200, 'message': 'OK'})
        # CORS头部已在@app.after_request中统一设置，此处不再重复添加
        return response
    try:
        print(f"\n===== 接收到STAR工作流处理请求 =====")
        print(f"请求内容类型: {request.content_type}")
        print(f"请求JSON: {request.json if request.is_json else '非JSON请求'}")

        # 获取文本内容
        data = request.get_json()
        text_content = data.get('text', '') or data.get('text_content', '')

        if not text_content:
            return jsonify({
                'code': 400,
                'message': '缺少文本内容参数',
                'data': None
            })

        # 调用STAR工作流分析
        import resume_star_workflow
        result = resume_star_workflow.analyze_resume_star(text_content)
        print(f"调用STAR工作流API返回结果: {result}")
        return jsonify({'code': 0, 'message': '成功调用STAR工作流API', 'data': result})
    except Exception as e:
        import traceback
        print(f"调用STAR分析工作流API异常: {e}")
        print(traceback.format_exc())
        return jsonify({
            'code': 500,
            'message': f"服务器错误: {str(e)}",
            'data': None
        })
    

if __name__ == "__main__":
    # 如果提供了命令行参数，则使用命令行参数作为文件路径
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        print(f"从命令行参数获取文件路径: {file_path}")
        
        # 从文件中提取文本
        text_content = document_text_extractor.extract_text_from_document(file_path)
        
        if text_content:
            print(f"成功提取文本，长度: {len(text_content)} 字符")
            complete_resume_workflow(text_content)
        else:
            print("文本提取失败")
    else:
        # 启动Flask应用
        print(f"启动Flask应用，访问 http://localhost:8000/api/workflow/resume 测试集成")
        print(f"上传目录: {app.config['UPLOAD_FOLDER']}")
        app.run(host='0.0.0.0', port=8000, debug=True) 