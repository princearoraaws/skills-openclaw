#!/bin/bash
# 股票分析并自动发送PDF报告脚本

# 参数检查
if [ $# -lt 1 ]; then
    echo "用法: $0 <股票代码> [输出目录]"
    echo "示例: $0 601868.SH"
    echo "      $0 000960.SZ ~/openclaw/workspace/reports"
    exit 1
fi

STOCK_CODE=$1
OUTPUT_DIR=${2:-"~/openclaw/workspace/reports"}

# 获取股票名称（简单映射，可根据需要扩展）
get_stock_name() {
    local code=$1
    case "$code" in
        "601868.SH") echo "中国能建" ;;
        "600519.SH") echo "贵州茅台" ;;
        "000960.SZ") echo "锡业股份" ;;
        "002922.SZ") echo "德赛西威" ;;
        "600219.SH") echo "南山铝业" ;;
        "600312.SH") echo "平高电气" ;;
        *) echo "股票" ;;
    esac
}

STOCK_NAME=$(get_stock_name "$STOCK_CODE")
echo "=========================================="
echo "📊 开始分析: $STOCK_NAME ($STOCK_CODE)"
echo "📁 输出目录: $OUTPUT_DIR"
echo "=========================================="

# 执行分析
python3 scripts/agentscope_stock_advisor.py \
    -s "$STOCK_CODE" \
    -o "$OUTPUT_DIR"

ANALYSIS_EXIT_CODE=$?

if [ $ANALYSIS_EXIT_CODE -ne 0 ]; then
    echo "❌ 分析过程出错，退出码: $ANALYSIS_EXIT_CODE"
    exit $ANALYSIS_EXIT_CODE
fi

# 查找最新生成的报告目录
LATEST_REPORT_DIR=$(find "$OUTPUT_DIR" -maxdepth 1 -type d -name "${STOCK_CODE}_*" | sort -r | head -1)

if [ -z "$LATEST_REPORT_DIR" ]; then
    echo "⚠️ 未找到生成的报告目录"
    exit 1
fi

echo ""
echo "✅ 分析完成！"
echo "📂 报告目录: $LATEST_REPORT_DIR"

# 查找PDF文件
PDF_FILE=$(find "$LATEST_REPORT_DIR" -name "*.pdf" | head -1)

if [ -n "$PDF_FILE" ] && [ -f "$PDF_FILE" ]; then
    echo "📄 PDF报告: $PDF_FILE"
    echo ""
    echo "正在发送PDF报告..."
    
    # 使用OpenClaw的message工具发送文件
    # 注意：需要在OpenClaw环境中执行
    if command -v openclaw &> /dev/null; then
        openclaw message send --file "$PDF_FILE" --caption "$STOCK_NAME($STOCK_CODE) 深度分析报告"
        echo "✅ PDF报告已发送！"
    else
        echo "📎 PDF报告路径: $PDF_FILE"
        echo "请手动发送或使用当前对话工具的附件功能上传"
    fi
else
    echo "⚠️ 未找到PDF文件，可能生成失败"
    echo "📄 可用文件列表:"
    ls -la "$LATEST_REPORT_DIR"
fi

echo ""
echo "=========================================="
echo "🎉 分析流程结束"
echo "=========================================="
