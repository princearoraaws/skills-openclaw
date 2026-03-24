---
name: pdf-learning
description: PDF 学习助手，帮助用户从 PDF 文档中学习知识。当用户说"辅助学习"、"用 sigma 学习"、"帮我学习这本书"时触发。功能：(1) 读取 PDF 并按类别存储在 ~/.learning-docs/ 下，(2) 对 PDF 内容做 RAG 检索，(3) 结合通用知识用 sigma 技能对用户进行提问式学习。
metadata:
  {
    "openclaw": { "emoji": "📚", "requires": { "anyBins": ["pdfplumber", "curl"] } },
  }
---

# PDF Learning Assistant

帮助用户从 PDF 文档中通过提问式学习掌握知识。

## 工作流程

### 1. 存储 PDF 内容

当用户上传 PDF 并指定学习类别时：

```bash
# 存储 PDF 文本到 ~/.learning-docs/<类别>/
python3 ~/.openclaw/extensions/skills/pdf-learning/scripts/ingest_pdf.py <pdf路径> <类别> [文件名]

# 示例：用户上传软考冲刺.pdf，类别是 ruankao
python3 ~/.openclaw/extensions/skills/pdf-learning/scripts/ingest_pdf.py ~/Downloads/软考冲刺.pdf ruankao
```

存储位置：`~/.learning-docs/ruankao/软考冲刺.txt`

### 2. RAG 检索

当用户询问具体知识点时，从已存储的 PDF 中检索相关内容：

```bash
# 检索相关段落
python3 ~/.openclaw/extensions/skills/pdf-learning/scripts/retrieve.py <类别> <查询内容>

# 示例：查询"系统架构设计"相关内容
python3 ~/.openclaw/extensions/skills/pdf-learning/scripts/retrieve.py ruankao "系统架构设计"
```

### 3. Sigma 学习模式

当用户说"用 sigma 学习"、"开始学习第X章"时：

1. 从 PDF 中 RAG 检索相关章节内容
2. 联网搜索补充材料
3. 调用 sigma 技能进行提问式学习

## 使用示例

**场景 1：上传 PDF**
> 用户：请帮我学习这本软考冲刺.pdf，这是软考资料
> → 执行：ingest_pdf.py 处理并存储

**场景 2：开始学习章节**
> 用户：我们开始学习系统架构设计章节吧
> → 执行：retrieve.py 检索 + sigma 提问式学习

## 重要提示

- PDF 文本存储在 `~/.learning-docs/<类别>/` 目录
- 使用 MiniMax Embedding API 做向量检索
- 确保 MiniMax API Key 已配置（与主模型相同）