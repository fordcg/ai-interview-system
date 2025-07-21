#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
百度API (来自a2)
"""

from flask import Blueprint, request, jsonify
import os
import time
from base.response import ResMsg

baiduBp = Blueprint('baidu', __name__)

def idocr(filename):
    """身份证OCR识别"""
    # 这里应该是实际的百度OCR API调用
    # 由于是示例，我们直接返回模拟数据
    
    # 模拟处理延迟
    time.sleep(0.5)
    
    # 返回模拟的身份证号和姓名
    return ['123456789012345678', '张三']

@baiduBp.route('/ocr', methods=['POST'])
def ocr():
    """OCR识别接口"""
    res = ResMsg()
    
    if 'file' not in request.files:
        res.update(code=1, msg="未上传文件")
        return res.data
    
    file = request.files['file']
    
    if file.filename == '':
        res.update(code=1, msg="文件名为空")
        return res.data
    
    # 保存文件
    basedir = os.path.abspath(os.path.dirname(__file__))
    upload_dir = os.path.join(basedir, '..', 'upload')
    
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    # 生成唯一文件名
    unix_time = int(time.time())
    ext = file.filename.rsplit('.', 1)[1] if '.' in file.filename else 'jpg'
    new_filename = f"{unix_time}.{ext}"
    
    file_path = os.path.join(upload_dir, new_filename)
    file.save(file_path)
    
    # 调用OCR识别
    idno, name = idocr(new_filename)
    
    res.update(code=0, data={
        'idno': idno,
        'name': name,
        'pic': new_filename
    })
    return res.data 