#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PDF处理配置文件
"""

import os

# PDF处理配置
PDF_CONFIG = {
    # 默认提取方法
    'default_method': 'auto',  # auto, pymupdf, pdfplumber, ocr, unstructured
    
    # 质量阈值
    'quality_threshold': 50,  # 文本质量评分阈值
    'min_text_length': 50,    # 最小文本长度
    
    # OCR配置
    'ocr_config': {
        'use_angle_cls': True,    # 是否使用角度分类
        'lang': 'ch',             # 语言：ch(中文), en(英文)
        'confidence_threshold': 0.5,  # 置信度阈值
        'image_resolution': 2.0,   # 图像分辨率倍数
    },
    
    # PyMuPDF配置
    'pymupdf_config': {
        'extract_images': False,   # 是否提取图像
        'extract_tables': True,    # 是否提取表格
        'preserve_layout': True,   # 是否保持布局
    },
    
    # pdfplumber配置
    'pdfplumber_config': {
        'extract_tables': True,    # 是否提取表格
        'table_settings': {
            'vertical_strategy': 'lines',
            'horizontal_strategy': 'lines',
            'snap_tolerance': 3,
        }
    },
    
    # unstructured配置
    'unstructured_config': {
        'strategy': 'auto',        # auto, fast, ocr_only, hi_res
        'extract_images': False,   # 是否提取图像
        'infer_table_structure': True,  # 是否推断表格结构
    },
    
    # 文件处理配置
    'file_config': {
        'max_file_size': 50 * 1024 * 1024,  # 50MB
        'temp_dir': None,          # 临时目录，None表示使用系统默认
        'cleanup_temp': True,      # 是否清理临时文件
    },
    
    # 性能配置
    'performance_config': {
        'max_pages': 100,          # 最大处理页数
        'timeout': 300,            # 超时时间（秒）
        'parallel_processing': False,  # 是否并行处理
        'memory_limit': '2GB',     # 内存限制
    },
    
    # 输出配置
    'output_config': {
        'preserve_formatting': True,   # 是否保持格式
        'include_metadata': True,      # 是否包含元数据
        'include_page_numbers': True,  # 是否包含页码信息
        'clean_text': True,            # 是否清理文本
    }
}

# 根据环境变量覆盖配置
def load_config():
    """加载配置，支持环境变量覆盖"""
    config = PDF_CONFIG.copy()
    
    # 从环境变量读取配置
    if os.getenv('PDF_DEFAULT_METHOD'):
        config['default_method'] = os.getenv('PDF_DEFAULT_METHOD')
    
    if os.getenv('PDF_OCR_LANG'):
        config['ocr_config']['lang'] = os.getenv('PDF_OCR_LANG')
    
    if os.getenv('PDF_MAX_FILE_SIZE'):
        try:
            config['file_config']['max_file_size'] = int(os.getenv('PDF_MAX_FILE_SIZE'))
        except ValueError:
            pass
    
    if os.getenv('PDF_TIMEOUT'):
        try:
            config['performance_config']['timeout'] = int(os.getenv('PDF_TIMEOUT'))
        except ValueError:
            pass
    
    return config

# 获取当前配置
def get_config():
    """获取当前配置"""
    return load_config()

# 验证配置
def validate_config(config):
    """验证配置的有效性"""
    errors = []
    
    # 验证方法
    valid_methods = ['auto', 'pymupdf', 'pdfplumber', 'ocr', 'unstructured']
    if config['default_method'] not in valid_methods:
        errors.append(f"无效的默认方法: {config['default_method']}")
    
    # 验证语言
    valid_langs = ['ch', 'en', 'fr', 'german', 'korean', 'japan']
    if config['ocr_config']['lang'] not in valid_langs:
        errors.append(f"无效的OCR语言: {config['ocr_config']['lang']}")
    
    # 验证文件大小
    if config['file_config']['max_file_size'] <= 0:
        errors.append("最大文件大小必须大于0")
    
    # 验证超时时间
    if config['performance_config']['timeout'] <= 0:
        errors.append("超时时间必须大于0")
    
    return errors

# 打印配置信息
def print_config():
    """打印当前配置信息"""
    config = get_config()
    print("=== PDF处理配置 ===")
    print(f"默认方法: {config['default_method']}")
    print(f"OCR语言: {config['ocr_config']['lang']}")
    print(f"最大文件大小: {config['file_config']['max_file_size'] / 1024 / 1024:.1f}MB")
    print(f"超时时间: {config['performance_config']['timeout']}秒")
    print(f"最大页数: {config['performance_config']['max_pages']}")
    print("==================")

if __name__ == "__main__":
    # 测试配置
    config = get_config()
    errors = validate_config(config)
    
    if errors:
        print("配置错误:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("配置验证通过")
        print_config()
