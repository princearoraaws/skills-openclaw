---
name: trading-agents
description: 股票投资深度分析技能，调用agentscope_stock_advisor.py执行完整的多智能体股票分析流程，生成包含7大模块的深度分析报告。
---

# 股票投资深度分析技能

## 系统概述

这是一个Trading Agent版本的智能股票分析技能。通过多智能体协作，提供全面的技术面分析、基本面分析、舆情分析、研究辩论、风险评估和最终投资决策的股票诊断服务，目前只支持中国A股市场。



## 核心功能

### 多智能体架构

- **分析师团队** (ReActAgent): 自主调用工具的数据采集智能体
  - 市场分析师 - 技术面分析
  - 基本面分析师 - 财务指标分析
  - 舆情分析师 - 新闻情绪分析
  
- **研究员团队** (AgentBase): 看多看空辩论机制
  - 看多研究员 - 买入论证
  - 看空研究员 - 卖出论证
  - 研究协调员 - 主持辩论
  
- **交易员**: 综合所有分析制定交易策略
  
- **风险管理团队**: 从不同角度评估风险
  - 激进风控官
  - 中性风控官
  - 保守风控官
  - 风控协调员
  
- **基金经理**: 做出最终投资决策

### 数据来源
- **Tushare**: 股票行情、财务指标、估值数据
- **AKShare**: 新闻资讯、市场情绪分析

### 输出成果
- 各智能体的详细 markdown 报告
- 包含所有分析的完整 PDF 报告
- JSON 格式的完整诊断报告
- 最终的买入/卖出/持有建议

## 🚀 快速开始

### 前置条件

1. **Python 3.8+** 必需

2. **安装依赖**:
```bash
pip install -r requirements.txt
```

3. **环境配置**:
在技能根目录创建 `.env` 文件：
```bash
# Tushare API Token (从 https://tushare.pro/ 获取)
TUSHARE_TOKEN=your_tushare_token_here

# 阿里云百炼 API Key (用于 LLM 模型)
ALIYUN_BAILIAN_API_KEY=your_bailian_api_key_here

# 可选：指定默认模型
MODEL_NAME=qwen3.5-plus
```

### 基本用法

#### 1. 运行股票诊断

```bash
python scripts/agentscope_stock_advisor.py --stock 600519.SH
```

**命令行选项**:
```bash
python scripts/agentscope_stock_advisor.py --stock <股票代码> --output <输出目录>

# 示例:
python scripts/agentscope_stock_advisor.py -s 600519.SH          # 使用默认输出目录
python scripts/agentscope_stock_advisor.py -s 000001.SZ -o my_reports  # 自定义输出目录
python scripts/agentscope_stock_advisor.py --stock 600519.SH --output report
```

#### 2. 编程方式使用

```python
from agentscope_stock_advisor import StockAdvisorSystem

# 创建系统实例
advisor = StockAdvisorSystem()

# 执行诊断
result = advisor.diagnose("600519.SH", base_report_dir="report")

# 保存完整报告 (JSON + PDF)
report_path = advisor.save_report(result)

# 访问各个报告
print(f"股票：{result['stock_name']} ({result['ts_code']})")
print(f"技术面分析：{result['analyst_reports']['MarketAnalyst']}")
print(f"最终决策：{result['final_decision']}")
```

## 📁 项目结构

```
scripts/
├── agentscope_stock_advisor.py    # 主入口程序
├── config.py                       # 配置管理
├── requirements.txt                # Python 依赖
│
├── agents/                        # 智能体实现
│   ├── analysts.py                # 市场/基本面/舆情分析师
│   ├── researchers.py             # 看多/看空研究员
│   ├── trader.py                  # 交易决策员
│   ├── risk_managers.py           # 风险管理团队
│   └── manager.py                 # 基金经理
│
└── tools/                         # 数据采集工具
    ├── tushare_tools.py           # Tushare 数据接口
    ├── akshare_tools.py           # AKShare 新闻/情绪工具
    └── toolkit.py                 # AgentScope 工具注册
```

## 🔧 配置说明

### 模型配置

系统使用阿里云百炼平台进行 LLM 推理，默认模型为 `qwen3.5-plus`。


切换模型方法:
```bash
export MODEL_NAME=qwen-max-2025-01-25
# 或编辑 .env 文件
```

### 分析参数

编辑 `config.py` 自定义:

```python
# 数据采集
market_data_days: int = 60      # 历史行情天数
news_days: int = 7              # 新闻采集天数

# 辩论配置
debate_rounds: int = 2          # 研究员辩论轮数
risk_discussion_rounds: int = 2 # 风控讨论轮数

# 权重配置 (用于评分)
tech_weight: float = 0.25       # 技术面权重
fund_weight: float = 0.35       # 基本面权重
news_weight: float = 0.20       # 舆情面权重
research_weight: float = 0.20   # 研究员共识权重
```

## 📊 输出文件

运行诊断后，您将获得:

### 目录结构
```
report/<股票代码>_<时间戳>/
├── MarketAnalyst_技术面分析.md      # 技术面分析
├── FundamentalsAnalyst_基本面分析.md # 基本面分析
├── NewsAnalyst_舆情面分析.md        # 舆情面分析
├── 研究员辩论报告.md                 # 研究员辩论记录
├── 交易员决策报告.md                 # 交易策略
├── 风险管理讨论报告.md               # 风险评估
├── 最终决策报告.md                   # 最终投资决策
├── complete_diagnosis_report.json  # 完整 JSON 报告
└── <股票名称>_<股票代码>_<时间戳>_<结果>.pdf  # PDF 报告
```

### 报告内容

每个智能体生成详细的 markdown 报告，包括:
- **市场分析师**: 价格趋势、均线、MACD、RSI、支撑/阻力位
- **基本面分析师**: PE/PB 比率、ROE/ROA、增长指标、估值水平
- **舆情分析师**: 最新新闻、情绪分析、市场氛围
- **研究辩论**: 看多论点 vs 看空反驳
- **交易员**: 入场/出场点、仓位大小、止损位
- **风控官**: 多角度风险因素
- **最终决策**: 买入/卖出/持有建议及理由

## 🛠️ 高级用法

### 自定义智能体

可以通过编辑 `agents/` 目录下的文件修改智能体行为:

```python
# 示例：修改分析师提示词
# agents/analysts.py
class MarketAnalystAgent(ReActAgent):
    def __init__(self):
        super().__init__(
            name="Market Analyst",
            model_config=model_config,
            prompt_template="Your custom prompt here...",
            toolkit=create_market_analyst_toolkit()
        )
```

### 添加新工具

在 `tools/` 目录下添加新的数据源或分析工具:

```python
# tools/custom_tool.py
class CustomAnalysisTool:
    def analyze(self, stock_code: str) -> dict:
        # 你的自定义分析逻辑
        return {"metric": "value"}
```

然后在 `tools/toolkit.py` 中注册。

### 与其他系统集成

系统返回包含所有结果的字典，便于集成:

```python
result = advisor.diagnose("600519.SH")

# 提取特定信息
final_decision = result['final_decision']
technical_score = extract_score(result['analyst_reports']['MarketAnalyst'])

# 存储到数据库
save_to_database(result)

# 发送通知
send_email_alert(final_decision)
```

## ⚠️ 重要提示

1. **API Keys 必需**: 
   - Tushare token (在 tushare.pro 可免费获取)
   - 阿里云百炼 API Key (LLM 模型必需)

2. **数据质量**: 分析质量取决于:
   - 底层数据源的准确性
   - LLM 模型能力
   - 配置参数

3. **免责声明**: 本系统仅用于研究和教育目的，不构成投资建议。投资前请务必自行研究。

4. **运行时间**: 完整诊断通常需要 2-5 分钟，具体取决于:
   - 网络状况
   - LLM 响应时间
   - 辩论/讨论轮数

## 🐛 故障排除

### 常见问题

**问题**: "Missing TUSHARE_TOKEN"
- **解决方案**: 在 `.env` 文件中添加 `TUSHARE_TOKEN=xxx`

**问题**: "Model not supported"
- **解决方案**: 检查模型名称是否与 `config.supported_models` 中的匹配

**问题**: PDF 显示乱码
- **解决方案**: 确保系统安装了中文字体。系统会自动检测常见字体路径。

**问题**: "akshare not installed" 警告
- **解决方案**: 使用 `pip install akshare` 安装或忽略 (系统将使用模拟数据)

### 获取帮助

查看日志获取详细错误信息。系统在每一步都提供全面的日志记录。

## 📝 示例工作流程

```bash
# 1. 设置环境
cp .env.example .env
# 在 .env 中填写你的 API keys

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行诊断
python scripts/agentscope_stock_advisor.py -s 600519.SH

# 4. 查看输出
# - 终端查看实时进度
# - 打开 PDF 报告查看综合分析
# - 查看各个 MD 文件了解智能体详细推理
# - 解析 JSON 用于程序化访问
```

## 🎓 更多学习资源

- **AgentScope 文档**: https://agentscope.io/
- **Tushare API**: https://tushare.pro/document/2
- **AKShare 文档**: https://akshare.akfamily.xyz/
- **阿里云百炼**: https://help.aliyun.com/product/42154.html



