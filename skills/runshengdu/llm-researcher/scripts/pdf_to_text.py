#!/usr/bin/env python3
"""
PDF to Text Converter for LLM Researcher

Usage:
    python pdf_to_text.py <pdf_path> [output_path]

Arguments:
    pdf_path    - Path to the PDF file to convert
    output_path - Optional: Path to write output (default: stdout)

Environment Variables:
    GLM_API_KEY   - Required

Returns:
    Extracted text content (to stdout or file)
"""

import sys
import os

def parse_with_zhipu(pdf_path):
    """Parse PDF using GLM API"""
    import requests
    
    api_key = os.environ.get('GLM_API_KEY')
    if not api_key:
        raise RuntimeError("GLM_API_KEY environment variable not set")
    
    url = "https://open.bigmodel.cn/api/paas/v4/files/parser/sync"
    
    with open(pdf_path, 'rb') as f:
        files = {"file": (os.path.basename(pdf_path), f)}
        payload = {
            "tool_type": "prime-sync",
            "file_type": "PDF"
        }
        headers = {"Authorization": f"Bearer {api_key}"}
        
        response = requests.post(url, data=payload, files=files, headers=headers, timeout=60)
        
        if response.status_code != 200:
            raise RuntimeError(f"GLM API error: {response.status_code} - {response.text}")
        
        result = response.json()
        if 'data' in result and 'text' in result['data']:
            return result['data']['text']
        else:
            raise RuntimeError(f"Unexpected API response: {result}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_text.py <pdf_path> [output_path]", file=sys.stderr)
        print("Environment: GLM_API_KEY", file=sys.stderr)
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        text = parse_with_zhipu(pdf_path)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"Text extracted to: {output_path}", file=sys.stderr)
        else:
            print(text)
            
    except Exception as e:
        print(f"Error parsing PDF: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
