#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文档文本提取模块
用于从PDF和Word文档中提取文本内容
"""

import os
import sys
import io
import traceback
from typing import Optional

def extract_text_from_document(file_path: str) -> Optional[str]:
    """
    从文档中提取文本内容
    
    Args:
        file_path: 文档文件路径
        
    Returns:
        提取的文本内容，如果提取失败则返回None
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            print(f"错误：文件不存在: {file_path}")
            return None
            
        # 获取文件扩展名
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()
        
        # 根据文件类型选择不同的提取方法
        if file_extension == '.pdf':
            return extract_text_from_pdf(file_path)
        elif file_extension in ['.doc', '.docx']:
            return extract_text_from_word(file_path)
        else:
            print(f"不支持的文件类型: {file_extension}")
            return None
    
    except Exception as e:
        print(f"文本提取失败: {str(e)}")
        traceback.print_exc()
        return None

def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """
    从PDF文档中提取文本（优化版）
    使用智能回退机制：PyPDF2 → PyMuPDF → pdfplumber

    Args:
        pdf_path: PDF文件路径

    Returns:
        提取的文本内容，如果提取失败则返回None
    """
    if not os.path.exists(pdf_path):
        print(f"错误：PDF文件不存在: {pdf_path}")
        return None

    print(f"正在提取PDF文本: {pdf_path}")

    # 方法1: PyPDF2 (文本最完整)
    try:
        import PyPDF2

        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text_blocks = []

            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    # 清理多余空格和格式
                    cleaned_text = _clean_extracted_text(page_text)
                    text_blocks.append(cleaned_text)

            if text_blocks:
                full_text = '\n\n'.join(text_blocks)
                print(f"✅ PyPDF2提取成功，文本长度: {len(full_text)} 字符")
                return full_text
            else:
                print("⚠️ PyPDF2未提取到文本内容")

    except ImportError:
        print("⚠️ PyPDF2未安装，跳过此方法")
    except Exception as e:
        print(f"⚠️ PyPDF2提取失败: {str(e)}")

    # 方法2: PyMuPDF (速度最快)
    try:
        import fitz

        doc = fitz.open(pdf_path)
        text_blocks = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            if page_text and page_text.strip():
                cleaned_text = _clean_extracted_text(page_text)
                text_blocks.append(cleaned_text)

        doc.close()

        if text_blocks:
            full_text = '\n\n'.join(text_blocks)
            print(f"✅ PyMuPDF提取成功，文本长度: {len(full_text)} 字符")
            return full_text
        else:
            print("⚠️ PyMuPDF未提取到文本内容")

    except ImportError:
        print("⚠️ PyMuPDF未安装，跳过此方法")
    except Exception as e:
        print(f"⚠️ PyMuPDF提取失败: {str(e)}")

    # 方法3: pdfplumber (表格处理较好)
    try:
        import pdfplumber

        text_blocks = []
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    cleaned_text = _clean_extracted_text(page_text)
                    text_blocks.append(cleaned_text)

        if text_blocks:
            full_text = '\n\n'.join(text_blocks)
            print(f"✅ pdfplumber提取成功，文本长度: {len(full_text)} 字符")
            return full_text
        else:
            print("⚠️ pdfplumber未提取到文本内容")

    except ImportError:
        print("⚠️ pdfplumber未安装，跳过此方法")
    except Exception as e:
        print(f"⚠️ pdfplumber提取失败: {str(e)}")

    print("❌ 所有PDF提取方法都失败了，可能是扫描版PDF需要OCR处理")
    return None

def _clean_extracted_text(text: str) -> str:
    """
    清理提取的文本，优化格式

    Args:
        text: 原始提取的文本

    Returns:
        清理后的文本
    """
    if not text:
        return ""

    # 移除多余的空格和换行
    lines = []
    for line in text.split('\n'):
        line = line.strip()
        if line:  # 只保留非空行
            # 清理多余的空格
            line = ' '.join(line.split())
            lines.append(line)

    return '\n'.join(lines)

def extract_text_from_word(word_path: str) -> Optional[str]:
    """
    从Word文档中提取文本
    
    Args:
        word_path: Word文件路径
        
    Returns:
        提取的文本内容，如果提取失败则返回None
    """
    try:
        # 动态导入python-docx，避免全局依赖
        try:
            import docx
        except ImportError:
            print("python-docx库未安装，尝试安装...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx"])
            import docx
        
        print(f"正在从Word文档提取文本: {word_path}")
        
        # 检查文件扩展名
        _, file_extension = os.path.splitext(word_path)
        file_extension = file_extension.lower()
        
        if file_extension == '.docx':
            # 打开DOCX文件
            doc = docx.Document(word_path)
            
            # 提取所有段落的文本
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
            print(f"成功提取Word文本，长度: {len(text)} 字符")
            return text
        elif file_extension == '.doc':
            # 对于旧版DOC文件，尝试使用textract
            try:
                import textract
            except ImportError:
                print("textract库未安装，尝试安装...")
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", "textract"])
                import textract
            
            # 使用textract提取文本
            text = textract.process(word_path).decode('utf-8')
            
            print(f"成功提取DOC文本，长度: {len(text)} 字符")
            return text
    
    except Exception as e:
        print(f"Word文本提取失败: {str(e)}")
        traceback.print_exc()
        
        # 尝试使用备用方法 (antiword)
        if file_extension == '.doc':
            try:
                print("尝试使用备用方法 (antiword) 提取DOC文本...")
                
                # 检查antiword是否安装
                import shutil
                if shutil.which('antiword'):
                    # 使用antiword提取文本
                    import subprocess
                    result = subprocess.run(['antiword', word_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    text = result.stdout.decode('utf-8')
                    
                    print(f"使用备用方法成功提取DOC文本，长度: {len(text)} 字符")
                    return text
                else:
                    print("antiword未安装，无法使用备用方法")
            except Exception as e2:
                print(f"备用DOC文本提取方法也失败: {str(e2)}")
        
        return None

def main():
    """主函数，用于测试"""
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='文档文本提取工具')
    parser.add_argument('file_path', help='文档文件路径')
    
    args = parser.parse_args()
    
    # 提取文本
    text = extract_text_from_document(args.file_path)
    
    if text:
        print("\n===== 提取的文本 =====\n")
        print(text[:500] + "..." if len(text) > 500 else text)
        print(f"\n共提取 {len(text)} 字符")
    else:
        print("文本提取失败")

if __name__ == "__main__":
    main() 