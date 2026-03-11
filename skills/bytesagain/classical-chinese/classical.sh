#!/usr/bin/env bash
CMD="$1"; shift 2>/dev/null; INPUT="$*"
case "$CMD" in
  translate) cat << 'PROMPT'
You are an expert. Help with: 文言文翻译. Provide detailed, practical output. Use Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  annotate) cat << 'PROMPT'
You are an expert. Help with: 逐字注释. Provide detailed, practical output. Use Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  poetry) cat << 'PROMPT'
You are an expert. Help with: 古诗赏析. Provide detailed, practical output. Use Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  essay) cat << 'PROMPT'
You are an expert. Help with: 古文写作. Provide detailed, practical output. Use Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  compare) cat << 'PROMPT'
You are an expert. Help with: 古今对比. Provide detailed, practical output. Use Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  learn) cat << 'PROMPT'
You are an expert. Help with: 学习计划. Provide detailed, practical output. Use Chinese.
User request:
PROMPT
    echo "$INPUT" ;;
  *) cat << 'EOF'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Classical Chinese — 使用指南
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  translate       文言文翻译
  annotate        逐字注释
  poetry          古诗赏析
  essay           古文写作
  compare         古今对比
  learn           学习计划

  Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
EOF
    ;;
esac
