#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票投资深度分析技能 - 配置文件
"""

# 目标Python文件路径
TARGET_PYTHON_FILE = "scripts/agentscope_stock_advisor.py"

# 默认报告输出路径
DEFAULT_OUTPUT_PATH = "~/openclaw/workspace/reports"

# 支持的交易所后缀
SUPPORTED_EXCHANGES = {
    "SH": "上海证券交易所",
    "SZ": "深圳证券交易所"
}

# 股票代码验证正则表达式
STOCK_CODE_PATTERN = r"^\d{6}\.(SH|SZ)$"

# 分析超时时间（秒）
ANALYSIS_TIMEOUT = 1200  # 20分钟

# 日志级别
LOG_LEVEL = "INFO"
