#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
增强版PDF文本提取器 - 优化版
使用智能回退机制：PyPDF2 → PyMuPDF → pdfplumber
"""

import os
import sys
import logging
from typing import Optional, Dict, Any

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedPDFExtractor:
    """增强版PDF文本提取器 - 优化版"""
    
    def __init__(self):
        # 使用优化的提取方法顺序：PyPDF2 → PyMuPDF → pdfplumber
        self.extraction_methods = [
            self._extract_with_pypdf2,
            self._extract_with_pymupdf,
            self._extract_with_pdfplumber
        ]
    
    def extract_text(self, pdf_path: str, method: str = 'auto') -> Dict[str, Any]:
        """
        从PDF提取文本（优化版）
        
        Args:
            pdf_path: PDF文件路径
            method: 提取方法 ('auto', 'pypdf2', 'pymupdf', 'pdfplumber')
        
        Returns:
            包含文本内容和元数据的字典
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
        
        logger.info(f"开始提取PDF文本: {pdf_path}")
        
        if method == 'auto':
            return self._auto_extract_optimized(pdf_path)
        elif method == 'pypdf2':
            return self._extract_with_pypdf2(pdf_path)
        elif method == 'pymupdf':
            return self._extract_with_pymupdf(pdf_path)
        elif method == 'pdfplumber':
            return self._extract_with_pdfplumber(pdf_path)
        else:
            raise ValueError(f"不支持的提取方法: {method}")
    
    def _auto_extract_optimized(self, pdf_path: str) -> Dict[str, Any]:
        """
        优化的自动提取方法
        按优先级尝试：PyPDF2 → PyMuPDF → pdfplumber
        """
        for method_func in self.extraction_methods:
            try:
                result = method_func(pdf_path)
                if result['success'] and len(result['text'].strip()) > 50:
                    result['auto_selected'] = True
                    logger.info(f"自动选择方法: {result['method']}")
                    return result
            except Exception as e:
                logger.warning(f"方法 {method_func.__name__} 失败: {str(e)}")
                continue
        
        return {
            'text': '',
            'success': False,
            'method': 'auto',
            'error': '所有提取方法都失败了'
        }
    
    def _extract_with_pypdf2(self, pdf_path: str) -> Dict[str, Any]:
        """使用PyPDF2提取文本（文本最完整）"""
        try:
            import PyPDF2
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_blocks = []
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        cleaned_text = self._clean_text(page_text)
                        text_blocks.append(cleaned_text)
                
                full_text = '\n\n'.join(text_blocks)
                
                return {
                    'text': full_text,
                    'method': 'pypdf2',
                    'success': True,
                    'page_count': len(text_blocks),
                    'total_pages': len(pdf_reader.pages)
                }
                
        except ImportError:
            return {
                'text': '',
                'success': False,
                'method': 'pypdf2',
                'error': 'PyPDF2未安装'
            }
        except Exception as e:
            return {
                'text': '',
                'success': False,
                'method': 'pypdf2',
                'error': str(e)
            }
    
    def _extract_with_pymupdf(self, pdf_path: str) -> Dict[str, Any]:
        """使用PyMuPDF提取文本（速度最快）"""
        try:
            import fitz
            
            doc = fitz.open(pdf_path)
            text_blocks = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                if page_text and page_text.strip():
                    cleaned_text = self._clean_text(page_text)
                    text_blocks.append(cleaned_text)
            
            doc.close()
            full_text = '\n\n'.join(text_blocks)
            
            return {
                'text': full_text,
                'method': 'pymupdf',
                'success': True,
                'page_count': len(text_blocks)
            }
            
        except ImportError:
            return {
                'text': '',
                'success': False,
                'method': 'pymupdf',
                'error': 'PyMuPDF未安装'
            }
        except Exception as e:
            return {
                'text': '',
                'success': False,
                'method': 'pymupdf',
                'error': str(e)
            }
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> Dict[str, Any]:
        """使用pdfplumber提取文本（表格处理较好）"""
        try:
            import pdfplumber
            
            text_blocks = []
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        cleaned_text = self._clean_text(page_text)
                        text_blocks.append(cleaned_text)
            
            full_text = '\n\n'.join(text_blocks)
            
            return {
                'text': full_text,
                'method': 'pdfplumber',
                'success': True,
                'page_count': len(text_blocks)
            }
            
        except ImportError:
            return {
                'text': '',
                'success': False,
                'method': 'pdfplumber',
                'error': 'pdfplumber未安装'
            }
        except Exception as e:
            return {
                'text': '',
                'success': False,
                'method': 'pdfplumber',
                'error': str(e)
            }
    
    def _clean_text(self, text: str) -> str:
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

# 兼容性函数，保持与现有代码的兼容
def extract_text_from_pdf_enhanced(pdf_path: str, method: str = 'auto') -> Optional[str]:
    """
    增强版PDF文本提取函数（兼容接口）
    
    Args:
        pdf_path: PDF文件路径
        method: 提取方法
    
    Returns:
        提取的文本内容
    """
    try:
        extractor = EnhancedPDFExtractor()
        result = extractor.extract_text(pdf_path, method)
        return result.get('text') if result.get('success') else None
    except Exception as e:
        logger.error(f"增强版PDF提取失败: {str(e)}")
        return None

# 为了向后兼容，保留原有的函数名
def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """向后兼容的PDF文本提取函数"""
    return extract_text_from_pdf_enhanced(pdf_path, 'auto')

if __name__ == "__main__":
    # 测试代码
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        extractor = EnhancedPDFExtractor()
        result = extractor.extract_text(pdf_path)
        print(f"提取方法: {result.get('method')}")
        print(f"文本长度: {len(result.get('text', ''))}")
        print(f"成功: {result.get('success')}")
        if result.get('text'):
            preview = result['text'][:300] + "..." if len(result['text']) > 300 else result['text']
            print(f"\n文本预览:\n{preview}")
    else:
        print("用法: python enhanced_pdf_extractor.py <pdf_file_path>")
