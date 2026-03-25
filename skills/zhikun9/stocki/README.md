# Stocki — AI Financial Analyst for OpenClaw

OpenClaw skill that brings Stocki's professional AI financial analysis to WeChat via ClawBot.

## Features

- **Instant Mode** — Quick financial Q&A: market prices, news, sector outlooks, company analysis
- **Task Mode** — Complex quantitative analysis: backtesting, strategy modeling, portfolio review
- **Scheduled Monitoring** — Periodic market updates via cron-triggered tasks
- **File Upload** — Analyze your own data (CSV, XLSX, JSON, Parquet)
- **Zero Dependencies** — Python stdlib only, no pip install needed

## Quick Start

### 1. Install

```bash
npx clawhub install stocki
```

Or from GitHub:

```bash
git config --global http.postBuffer 524288000
git config --global http.lowSpeedLimit 0
git config --global http.lowSpeedTime 999999
git clone https://github.com/stocki-ai/open-stocki.git ~/.openclaw/workspace/skills/stocki
```

### 2. Configure

```bash
export STOCKI_GATEWAY_URL="https://api.stocki.com.cn"
export STOCKI_API_KEY="sk_your_key_here"
```

### 3. Use

**Instant Q&A:**
```bash
python3 scripts/stocki-instant.py "A股半导体行业前景?"
```

**Quant Analysis:**
```bash
python3 scripts/stocki-task.py create "半导体行业分析"
python3 scripts/stocki-run.py submit <task_id> "回测CSI 300动量策略"
python3 scripts/stocki-run.py status <task_id> <run_id>
python3 scripts/stocki-report.py download <task_id> summary.md
```

## Scripts

| Script | Purpose |
|--------|---------|
| `stocki-instant.py` | Quick financial Q&A |
| `stocki-task.py` | Create, list, and view task history |
| `stocki-run.py` | Submit quant runs and check status |
| `stocki-report.py` | List and download analysis reports |
| `stocki-upload.py` | Upload data files to task workspace |

## Architecture

```
User (WeChat) -> ClawBot -> OpenClaw -> Stocki Skill
                                           |
                                           v
                                  OpenStocki Gateway (FastAPI)
                                           |
                                           v
                                  Stocki Internal (LangGraph)
                                  - Instant Agent
                                  - Quant Agent
```

## License

Proprietary. All rights reserved.
