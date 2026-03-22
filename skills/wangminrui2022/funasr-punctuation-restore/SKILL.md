---
name: Funasr-Punctuation-Restore
description: |-
  使用 FunASR 官方 ct-punc 模型，为**一段文本、单个记事本文件、或整个目录**一键恢复标点符号。
metadata:
  openclaw:
    requires:
      bins:
        - python
---

# Funasr-Punctuation-Restore

**功能**：使用 FunASR ct-punc 模型一键恢复标点（支持文本/文件/目录）。目录模式会在同级创建结构完全一致的 _punctuated 镜像目录（原目录不变）。GPU 加速 + 自动清理显存。

## 支持的模型（推荐顺序）
1. **punc_ct-transformer_cn-en-common-vocab471067-large** → 这是一个基于 Transformer 的中英文混合文本标点恢复模型，用于给 ASR 结果自动加标点。

## 执行步骤
1. **解析目录**：识别用户的源路径（支持单个音频文件或整个文件夹）。
2. **默认目标**：若未指定输出路径，默认在输入同级创建 `[原文件名]_punctuated.txt`或[原文件名]_punctuated 文件或目录。
3. **调用命令**：使用以下兼容性命令启动脚本（优先 python3，失败则 python）。脚本会自动创建虚拟环境、检测 GPU 并安装对应版本。

   ```bash
   (python3 scripts/punctuation_restore.py (--text "<文本内容>" | --file "<文件路径>" | --dir "<目录路径>")) || (python scripts/punctuation_restore.py (--text "<文本内容>" | --file "<文件路径>" | --dir "<目录路径>"))