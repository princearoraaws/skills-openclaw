#!/usr/bin/env python3
"""
RAG 检索脚本
从 ~/.learning-docs/<类别>/ 目录中检索相关内容
使用 MiniMax Embedding API 进行向量相似度匹配
"""

import os
import sys
import json
import glob
import math

# MiniMax API 配置
MINIMAX_API_KEY = os.environ.get("ANTHROPIC_AUTH_TOKEN", "")
MINIMAX_EMBED_URL = "https://api.minimaxi.com/v1/text/embeddings"

def get_embedding(text):
    """调用 MiniMax API 获取文本 embedding"""
    if not MINIMAX_API_KEY:
        print("ERROR: 未设置 ANTHROPIC_AUTH_TOKEN 环境变量")
        return None
    
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "ember-3",
        "input": text
    }
    
    import urllib.request
    import urllib.parse
    
    req = urllib.request.Request(
        MINIMAX_EMBED_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['data'][0]['embedding']
    except Exception as e:
        print(f"ERROR: 获取 embedding 失败: {e}")
        return None

def cosine_similarity(vec1, vec2):
    """计算余弦相似度"""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    
    if norm1 == 0 or norm2 == 0:
        return 0
    
    return dot_product / (norm1 * norm2)

def split_text(text, chunk_size=1000, overlap=100):
    """将文本分割成 chunks"""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        
        if chunk:
            chunks.append(chunk)
        
        start += chunk_size - overlap
    
    return chunks

def retrieve_from_category(category, query, top_k=5):
    """从指定类别目录检索相关内容"""
    base_dir = os.path.expanduser("~/.learning-docs")
    category_dir = os.path.join(base_dir, category)
    
    if not os.path.exists(category_dir):
        print(f"ERROR: 知识库目录不存在: {category_dir}")
        print(f"   请先使用 ingest_pdf.py 上传 PDF 文档")
        return []
    
    # 获取所有 txt 文件
    txt_files = glob.glob(os.path.join(category_dir, "*.txt"))
    
    if not txt_files:
        print(f"WARNING: 目录中没有找到任何 .txt 文件: {category_dir}")
        return []
    
    print(f"📂 已加载 {len(txt_files)} 个文档")
    
    # 获取查询的 embedding
    print(f"🔍 正在检索: {query}")
    query_embedding = get_embedding(query)
    
    if not query_embedding:
        print("ERROR: 无法获取查询 embedding，使用简单文本匹配")
        # 回退到简单匹配
        results = []
        for txt_file in txt_files:
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if query.lower() in content.lower():
                    # 找到相关段落
                    idx = content.lower().find(query.lower())
                    start = max(0, idx - 200)
                    end = min(len(content), idx + 500)
                    results.append({
                        "file": os.path.basename(txt_file),
                        "content": content[start:end],
                        "score": 1.0
                    })
        return results[:top_k]
    
    # 对每个文档进行检索
    all_chunks = []
    
    for txt_file in txt_files:
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 分割成 chunks
        chunks = split_text(content)
        
        # 获取每个 chunk 的 embedding 并计算相似度
        for i, chunk in enumerate(chunks):
            chunk_embedding = get_embedding(chunk)
            if chunk_embedding:
                score = cosine_similarity(query_embedding, chunk_embedding)
                all_chunks.append({
                    "file": os.path.basename(txt_file),
                    "chunk_id": i,
                    "content": chunk,
                    "score": score
                })
    
    # 按相似度排序
    all_chunks.sort(key=lambda x: x['score'], reverse=True)
    
    # 返回 top_k 结果
    return all_chunks[:top_k]

def main():
    if len(sys.argv) < 3:
        print("用法: retrieve.py <类别> <查询内容>")
        print("示例: retrieve.py ruankao \"系统架构设计\"")
        sys.exit(1)
    
    category = sys.argv[1]
    query = sys.argv[2]
    
    results = retrieve_from_category(category, query)
    
    if not results:
        print("未找到相关内容")
        sys.exit(1)
    
    print("\n📚 检索结果：\n")
    for i, result in enumerate(results, 1):
        print(f"--- 结果 {i} (相似度: {result['score']:.3f}) ---")
        print(f"来源: {result['file']}")
        print(f"内容: {result['content'][:300]}...")
        print()

if __name__ == "__main__":
    main()