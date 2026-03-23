---
name: dex-quant-skill
description: >
  加密货币量化交易 AI Skill。用户用自然语言描述交易规则 → AI 生成策略脚本 → 服务器回测验证 → 实时监控。
  Use when user asks to create a trading strategy, backtest, or monitor crypto markets.
---

# DEX Quant Skill — 加密货币量化交易

## ⚠️ 行为准则（必须遵守）

1. **你是执行者**。你自己运行代码完成任务，不要给用户贴命令让他们手动跑。
2. **不要问用户选择**。不要问"你选哪种？"、"要我装依赖吗？"、"本地还是服务器？"。直接做。
3. **回测 = 把脚本源码上传到服务器**。服务器负责拉K线、跑信号、回测。本地不需要下载任何数据。
4. **依赖直接装**。不要问，直接 `pip3 install httpx loguru 2>/dev/null`。
5. **生成策略后如果用户说回测，立刻执行**，不要再确认。
6. **回测失败时自动重试一次**，不要问用户要不要重试。

---

## 配额规则

| 功能 | 是否免费 | 是否占配额 |
|------|---------|-----------|
| 生成策略脚本 | 免费 | 不占 |
| 回测（无限次） | 免费 | 不占 |
| 定时监控任务 | 免费 3 个 | 占配额 |

回测可以随便跑，不占用任何配额。配额只限制「定时监控任务」的数量（免费 3 个）。

---

## 流程

```
用户描述想法 → 你生成策略脚本(.py) → 用户说回测 → 你读取脚本源码 + 调服务器API → 展示结果
```

本地不需要运行策略脚本、不需要下载K线数据。脚本源码直接上传给服务器执行。

---

## 1. 策略制作

用户说交易想法时，生成 Python 策略脚本，保存到 `{baseDir}/strategies/` 目录。

脚本要求：
- `import sys; sys.path.insert(0, '{baseDir}/scripts')` 导入工具库
- 使用 `from data_client import DataClient` 获取数据
- 使用 `from indicators import Indicators as ind` 计算指标
- 实现 `generate_signals(mode, start_date, end_date)` 函数
- 返回 `{"strategy_name": "...", "signals": [...]}`

信号格式：`timestamp, symbol, action(buy/sell), direction(long/short), confidence, reason, price_at_signal`。可选：`suggested_stop_loss, suggested_take_profit`。

---

## 2. 回测（服务器端执行，免费无限次，不占配额）

**当用户要求回测时，立刻执行以下步骤（不要问任何问题）：**

### 步骤一：安装最少依赖
```bash
pip3 install httpx loguru 2>/dev/null
```
只需要 httpx 和 loguru。不需要 numpy/pandas/yfinance，数据在服务器端拉取。

### 步骤二：读取策略脚本源码 + 调服务器回测API
```python
import sys
sys.path.insert(0, '{baseDir}/scripts')
from api_client import QuantAPIClient

# 读取策略脚本的源码（不是运行它）
with open('{baseDir}/strategies/xxx_strategy.py', 'r') as f:
    script_content = f.read()

# 把源码上传给服务器，服务器负责一切：拉K线 → 跑脚本生成信号 → 回测引擎模拟交易
client = QuantAPIClient(timeout=300.0)
bt = client.run_server_backtest(
    script_content=script_content,
    strategy_name="策略名",
    symbol="BTCUSDT",
    timeframe="4h",
    start_date="2025-01-01",
    end_date="2025-12-31",
    leverage=3,
    initial_capital=100000,
    direction="long_short",
)

# 必须展示完整报告（不要省略，不要只说一句话总结）
client.print_metrics(bt)
client.print_trades(bt)
client.print_conclusion(bt)
```

关键：用 `run_server_backtest(script_content=...)` 而不是 `run_backtest(signals=...)`。
服务器地址和认证已内置在 api_client.py 中，无需配置。

### ⚠️ 展示规则（必须遵守）

回测完成后，你**必须**把 `print_metrics` / `print_trades` / `print_conclusion` 的完整输出展示给用户。

**禁止**只说一句"总收益为负，Sharpe < 1"这种总结。用户需要看到完整报告，包括：
- 绩效报告表：总收益率、年化收益、Sharpe、Sortino、最大回撤、胜率、盈亏比、交易笔数、最终余额
- 交易记录表：每笔交易的时间、方向、价格、盈亏
- 评估结论：通过/先模拟/驳回

如果 print 函数的输出被截断，至少要展示绩效报告表的全部指标。

---

## 3. 定时监控（占配额，免费 3 个）

用户要求监控时，运行策略脚本的 live 模式（这时候才需要本地运行和占配额）：

```bash
pip3 install numpy pandas httpx loguru yfinance 2>/dev/null
```

```python
import sys
sys.path.insert(0, '{baseDir}/scripts')
from strategies.xxx_strategy import generate_signals
result = generate_signals(mode='live')
```

---

## 项目结构

```
dex-quant-skill/
├── SKILL.md              ← 你正在读的文件
├── scripts/
│   ├── api_client.py     ← 回测服务器客户端（run_server_backtest）
│   ├── data_client.py    ← K线数据获取（服务器端使用）
│   ├── indicators.py     ← 技术指标库（服务器端使用）
│   ├── machine_auth.py   ← 自动认证
│   └── strategy_runner.py
├── strategies/           ← 生成的策略脚本放这里
└── schemas/
    └── signal_format.json
```
