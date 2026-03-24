#!/usr/bin/env python3
"""
PDF 文档摄取脚本
将 PDF 文本提取并存储到 ~/.learning-docs/<类别>/ 目录
"""

import os
import sys
import json

try:
    import pdfplumber
except ImportError:
    print("ERROR: pdfplumber not installed. Run: pip install pdfplumber")
    sys.exit(1)

def extract_text_from_pdf(pdf_path):
    """从 PDF 提取文本"""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def save_to_knowledge_base(pdf_path, category, custom_name=None):
    """保存 PDF 文本到知识库"""
    base_dir = os.path.expanduser("~/.learning-docs")
    category_dir = os.path.join(base_dir, category)
    
    # 创建目录
    os.makedirs(category_dir, exist_ok=True)
    
    # 确定文件名
    if custom_name:
        # 如果指定了自定义名称，直接使用
        filename = custom_name if custom_name.endswith('.txt') else custom_name + '.txt'
    else:
        # 否则使用 PDF 原文件名
        pdf_name = os.path.basename(pdf_path)
        filename = os.path.splitext(pdf_name)[0] + '.txt'
    
    output_path = os.path.join(category_dir, filename)
    
    # 提取文本
    print(f"正在读取 PDF: {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    
    if not text.strip():
        print("WARNING: PDF 中未能提取到文本内容")
        return None
    
    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    print(f"✅ 已保存到: {output_path}")
    print(f"   文本长度: {len(text)} 字符")
    
    return output_path

def main():
    if len(sys.argv) < 3:
        print("用法: ingest_pdf.py <pdf路径> <类别> [自定义文件名]")
        print("示例: ingest_pdf.py ~/Downloads/软考冲刺.pdf ruankao")
        print("       ingest_pdf.py ~/Downloads/书.pdf ruankao my_notes")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    category = sys.argv[2]
    custom_name = sys.argv[3] if len(sys.argv) > 3 else None
    
    if not os.path.exists(pdf_path):
        print(f"ERROR: 文件不存在: {pdf_path}")
        sys.exit(1)
    
    result = save_to_knowledge_base(pdf_path, category, custom_name)
    
    if result:
        print("\n📚 PDF 已就绪，可以使用 sigma 学习相关章节内容")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()