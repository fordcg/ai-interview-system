#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
公共API
"""

from flask import Blueprint, request, jsonify, send_from_directory
import os
import time
from werkzeug.utils import secure_filename

from base.response import ResMsg

commonBp = Blueprint('common', __name__)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx'}

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@commonBp.route('/upload', methods=['POST'])
def upload_file():
    """文件上传接口"""
    res = ResMsg()
    
    if 'file' not in request.files:
        res.update(code=1, msg="未上传文件")
        return res.data
    
    file = request.files['file']
    
    if file.filename == '':
        res.update(code=1, msg="文件名为空")
        return res.data
    
    if file and allowed_file(file.filename):
        # 获取上传目录
        basedir = os.path.abspath(os.path.dirname(__file__))
        upload_dir = os.path.join(basedir, '..', 'upload')
        
        # 确保目录存在
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        # 生成安全的文件名
        unix_time = int(time.time())
        ext = file.filename.rsplit('.', 1)[1].lower()
        new_filename = f"{unix_time}.{ext}"
        
        # 保存文件
        file_path = os.path.join(upload_dir, new_filename)
        file.save(file_path)
        
        res.update(code=0, data={'filename': new_filename})
        return res.data
    
    res.update(code=1, msg="不允许的文件类型")
    return res.data

@commonBp.route('/download/<filename>')
def download_file(filename):
    """文件下载接口"""
    basedir = os.path.abspath(os.path.dirname(__file__))
    upload_dir = os.path.join(basedir, '..', 'upload')
    
    return send_from_directory(upload_dir, filename, as_attachment=True)

@commonBp.route('/view/<filename>')
def view_file(filename):
    """文件查看接口"""
    basedir = os.path.abspath(os.path.dirname(__file__))
    upload_dir = os.path.join(basedir, '..', 'upload')
    
    return send_from_directory(upload_dir, filename, as_attachment=False) 