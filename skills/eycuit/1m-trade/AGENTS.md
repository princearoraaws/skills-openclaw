# Agent Composition Handbook

This document defines a set of preset Agents used to automate complex on-chain workflows composed of the `1m-trade-news`, and `1m-trade-dex` skills. You can invoke these Agents directly to achieve specific goals.

## Agent list

### 1) Agent: Market Scout
- **Invocation name**: `market-scout`
- **Description**: Runs a daily market health check. If the user provides no specific instructions, this agent can produce a comprehensive market snapshot.
- **Workflow**:
  1. **Trigger**: user asks "How is the market today?" or a scheduled run.
  2. **Execution**:
     a. Call `1m-trade-news` → Scenario 1: Market snapshot.
     b. Fetch sentiment indicator, important newsflashes, BTC ETF net flow, and daily on-chain tx volume in parallel.
  3. **Output**: a formatted report with a data summary and brief interpretation (e.g. if sentiment < 20, highlight a potential opportunity zone).
- **Use cases**: pre-open review, quick market sentiment check, decision support.

### 2) Agent: Funding Flash
- **Invocation name**: `funding-flash`
- **Description**: A one-stop "from zero to tradable" funding and activation flow for a new user or a new wallet.
- **Workflow**:
  1. **Trigger**: user expresses intent like "I want to start trading" / "deposit to Hyperliquid".
  2. **Execution**:
     a. Call `1m-trade-dex` → Branch A, Stage 1 to generate a deposit address.
     b. Wait for the user to confirm the transfer.
     c. After confirmation, call `1m-trade-dex` → Branch A, Stage 2 to bridge/activate.
  3. **Output**: provide the address and step-by-step logs; never print private keys in chat.
- **Security note**: The agent must not read private keys into context or send them as chat text. If the user needs the key, **invoke** the CLI secure-delivery flow in `1m-trade-dex` (e.g. `hl1m send-private-key`); delivery goes through the platform secure channel, not through the model.

### 3) Agent: Trend Trader
- **Invocation name**: `trend-trader`
- **Description**: Combines macro fund flows and micro price action to produce conditional trade ideas or simulated trades.
- **Workflow**:
  1. **Trigger**: user asks "Can I buy BTC now?" or "Where is money flowing?"
  2. **Execution**:
     a. Call `1m-trade-news` → Scenario 2: Fund flow analysis.
     b. Call `1m-trade-news` → Scenario 3: Macro environment.
     c. If conditions are met (e.g. stablecoin expansion + top net inflow on a chain + macro not bearish):
        i. Call `1m-trade-dex` to query live market data.
        ii. Generate a trade idea report including target, macro rationale, on-chain rationale, and current price.
  3. **Output**: a report with bullish/bearish rationale and recommended targets. **Do not execute trades automatically**; require final user confirmation.
- **Use cases**: data-driven decision support for manual traders.

### 4) Agent: News-driven Trade Alert
- **Invocation name**: `news-alert-trader`
- **Description**: Monitors configured news keywords and, when triggered, checks related asset market data to provide fast reaction context.
- **Workflow**:
  1. **Configure**: user pre-defines keywords (e.g. "ETF approval", "hack", "mainnet launch").
  2. **Trigger**: periodically call `1m-trade-news` → Scenario 5: Keyword search (e.g. every 5 minutes).
  3. **Execution**: when new items contain keywords:
     a. Extract related assets from the news text (e.g. "Ethereum" → ETH).
     b. Call `1m-trade-dex` to query latest price/order book.
     c. Call `1m-trade-dex` to get recent kline.
  4. **Output**: alert including title, summary, related assets, price before/after, order book pressure change, and short-term kline trend.
- **Use cases**: capture sudden news-driven moves for short-term traders.

### 5) Agent: HIP-3 TradFi Arb Monitor
- **Invocation name**: `hip3-arb-monitor`
- **Description**: Monitors HIP-3 markets (e.g. stocks/commodities) around TradFi open to find spread/arb opportunities.
- **Workflow**:
  1. **Trigger**: run around US equity open (ET 9:30 AM).
  2. **Execution**:
     a. Call `1m-trade-dex` to list HIP-3 markets and filter targets (e.g. `xyz:AAPL`, `xyz:GOLD`).
     b. For each target in parallel:
        i. Get Hyperliquid price.
        ii. (Simulated) fetch TradFi open/spot price from an external API (not provided; mark as TODO).
        iii. Compute spread percentage.
  3. **Output**: spread report highlighting assets above a threshold (e.g. 2%) and optionally search related news via `1m-trade-news`.
- **Use cases**: cross-market arbitrage and tokenized TradFi monitoring.

## How to use these agents
You can invoke agents via natural language or structured commands.

Examples:
- Natural language: "Start `market-scout` and give me a morning report."
- Structured: `/agent run market-scout`
- Combined: "Run `market-scout` first; if sentiment is bullish, then run `funding-flash` to prepare a 100 USDT funding route."

## Configuration & extension
Each agent definition is a "script". You can modify this file to:
1. **Adjust flows**: change internal skill call order or condition logic.
2. **Create new agents**: combine skills with new logic using the same format.
3. **Parameterize**: extract fixed parameters (keywords, thresholds) into configurable variables.

---
*`AGENTS.md` together with the root `SKILL.md` forms the "strategy layer" and "tactics layer" of this skill library: automation workflows and interactive service definitions.*