---
name: 1m-trade
description: |
  An integrated on-chain operations hub that orchestrates three major modules: BlockBeats API intelligence, Hyperliquid wallet funding/activation, and Hyperliquid DEX trading. It supports end-to-end workflows from market monitoring and macro analysis to funding and spot/perp/HIP-3 asset trading, and can run automated trading based on user-defined or AI-generated strategies.
metadata:
  openclaw:
    emoji: "🚀"
    always: false
    requires:
      bins:
        - curl
        - node
        - hl1m
        - openclaw
      configPaths:
        - ~/.openclaw/.1m-trade/.env
        - $OPENCLAW_STATE_DIR/.1m-trade/.env
      env:
        - BLOCKBEATS_API_KEY
        - HYPERLIQUID_PRIVATE_KEY_ENC
        - HYPERLIQUID_PK_ENC_PASSWORD
        - HYPERLIQUID_WALLET_ADDRESS
    os:
      - darwin
      - linux
      - win32
    tags:
      - crypto
      - news
      - trading
      - hyperliquid
      - wallet
      - dex
      - automation
---

# 1m-trade Aggregator - On-chain Operations Hub
## After first install
Scan and verify all required dependencies for sub-skills and install what is needed.

Optional runtime override:
- `OPENCLAW_STATE_DIR` can be set to change where local `.1m-trade` state files are read/written.
- If not set, tools default to `~/.openclaw/.1m-trade/`.

Secret source-of-truth policy:
- API key and wallet credentials are expected in the local state `.env` file under the paths above.
- Process environment variables may be used only as explicit runtime overrides by underlying tools.
- **LLM boundary**: The model must **not** read `.env` or private keys into its context, quote them, or type them into chat. It may only **invoke CLI commands** (e.g. `hl1m …`, `openclaw …`) whose implementations read local state and deliver secrets **via the platform secure channel**—the key never passes through the model.
- Never print secret values in assistant-visible chat or user-facing logs from the model.

## Overview
This skill (`1m-trade`) is an orchestration hub that integrates multiple sub-skills into a single coherent workflow. You describe your goal (e.g., "check today's sentiment then fund my account", "analyze BTC fund flows and open a long with half my balance", "generate a wallet", "auto-trade BTC"), and this skill decomposes the request and calls `1m-trade-news`, and `1m-trade-dex` to complete the operation.

## Core workflows
Based on **intent keywords**, this skill routes into one of the workflows below (or composes them).

### Workflow 1: Market intelligence (Data & News)
**Triggers**: `market`, `price`, `news`, `macro`, `fund flows`, `perps`, `search [keyword]`

**Skill**: `1m-trade-news`

**Logic**:
1. Parse the user query and map it to a scenario / intent mapping.
2. Call the relevant BlockBeats API endpoints in parallel.
3. Format and aggregate results into a market report with brief interpretation.

**Example output**:

```
📰 Market Report · 202X-XX-XX
===
1. 📊 Snapshot
   Sentiment: 35 → Neutral
   BTC ETF: +$120M net inflow today
   On-chain tx volume: +15% vs yesterday

2. 💰 Hot flows (Solana)
   1. JTO net inflow $4.2M
   2. ...

3. 🌐 Macro
   Global M2: +4.5% YoY → Liquidity easing
   DXY: 104.2 → Relatively strong
   Overall: Macro backdrop is neutral-to-bullish for crypto.
```

### Workflow 2: Wallet & funding channel (Wallet & Funding)
**Triggers**: `open account`, `fund`, `deposit`, `generate address`, `arrived?`, `check balance`

**Skill**: `1m-trade-dex`

**Logic**:
1. **Stage A - generate address**: run the relevant `1m-trade-dex` skill.
2. **Stage B - bridge & activate**: when the user confirms funding, run the relevant `1m-trade-dex` skill and return the full logs. If the private key is missing, inform the user that funds tied to the old address cannot be recovered and a new address must be created.

### Workflow 3: Trading execution & management (Trading & Management)
**Triggers**: `trade`, `order`, `open`, `close`, `positions`, `price`, `kline`, `HIP3`, `AAPL`, `GOLD`

**Skill**: `1m-trade-dex`

**Logic**:
1. **Market data**: query kline/mids/meta as requested and format results.
2. **Pre-trade checks**: ensure `1m-trade-dex` is installed and run `node auto_check.js` to verify prerequisites. If it fails, do not execute any trades.
3. **Execution**: follow the `1m-trade-dex` documentation for the specific command.

### Workflow 4: Hybrid orchestration (Hybrid Workflow)
**Trigger examples**: "check the market then decide whether to buy BTC", "fund me then buy some ETH"

**Logic**:
1. Call Workflow 1 to fetch the market report.
2. Present the report and ask whether to continue (e.g., "sentiment is greedy and ETF inflows persist; proceed to funding?").
3. After confirmation, call Workflow 2 or Workflow 3.

## Examples
**User**: "How is the crypto market today? If sentiment is good, generate a Hyperliquid deposit address."
**`1m-trade`**:
1. Generate a market snapshot report (Workflow 1).
2. At the end: "Detected funding intent; generating a Hyperliquid deposit address..."
3. Return address and instructions; the private key is stored locally and should not be printed in chat.

**User**: "Search for the latest news about 'Bitcoin halving', then show BTC kline."
**`1m-trade`**:
1. Call search (Workflow 1, Scenario 5) and return relevant items.
2. Call kline query (Workflow 3) and return recent candles.

### Workflow 5: Fully autonomous mode (AI Auto-Trader)
**Triggers**: `enable auto trading`, `autonomous trading`, `managed`, `AI trade for me`, `run every N minutes`, `auto trade BTC`

**Logic**:
1. Run the checker once before enabling cron:
   - Repo root: `node auto_check.js`
   - If installed under the OpenClaw workspace: run `node <skill_bundle_root>/auto_check.js`
   If it fails, do not enable auto trading.
2. Check whether the `1m-trade-auto-trader` cron job exists:
   - Run `openclaw cron list` to verify whether it still exists.
   - If it exists, ask the user to stop/remove it before creating a new one.
   - If the user confirms it should be removed and it is still present, attempt to remove it with `openclaw cron rm <task id>`, then re-run `openclaw cron list` to confirm it is gone.

3. Create a periodic workflow using the command below. `--session isolated` is fixed and must not be changed. The default interval is every 20 minutes (`*/20`); replace with `*/N` if needed. Send the trading report to the user.
   Security constraints for the cron message:
   - Include ONLY the "#### Workflow content" block as the job prompt template.
   - Never include any secrets (API keys, private keys, passwords, `.env` contents, tokens).
   - Never include unrelated user/system text, terminal logs, or file contents.
   - Keep shell commands/placeholders unchanged, but you may translate natural-language instructions for locale.
4. ``
```bash
openclaw cron add \
  --name "1m-trade-auto-trader" \
  --cron "*/20 * * * *" \
  --session isolated \
  --message "<Paste ONLY the '#### Workflow content' template. Do not include any secrets or unrelated text. Translate natural-language text to the user's language faithfully (no summary/rewrites), keep commands/placeholders unchanged, keep structure/line breaks unchanged, and output ONLY the final trading report. Replace this placeholder ONLY.>" \
  --timeoutSeconds 600 \
  --announce \
  --channel <channel e.g. telegram> \
  --to "<user id>" \
```

#### Workflow content
Pre-start: dependency memory check
All skills are installed locally.
1. Try reading: `$OPENCLAW_STATE_DIR/.1m-trade/dependencies-status.md`
   - If missing → first run, treat as "not confirmed installed"
   - If present, look for any marker:
     - Installed: true
     - DependencyStatus: Installed
     - SkillsReady: true
   - Record status as "installed" or "not installed/unknown"

2. Decide based on the status:
   - If clearly "installed" → skip checks/install and go to step 4
   - Otherwise → run step 3

3. Only when initialization is needed:
   Ensure these skills are available in order:
   - 1m-trade-news
   - 1m-trade-dex
   If a skill is unavailable, attempt to install/enable it via the system's mechanism.
   Then record success in the memory file.

4. Must execute: update/create the dependency memory file by overwriting:
```
# Dependency install marker - do not edit manually
Installed: true
Skills: 1m-trade-news (or others)
Skills Path: <skill paths>
LastChecked: 2026-03-15 14:30:00 UTC
```
Start execution

### Workflow: Fully autonomous trading mode (AI Auto-Trader)

## Execution Guidelines
- Evaluate the full market universe (scan multiple assets). Trades are determined by risk controls; 0 to multiple trades are allowed.
- Output must be a trading report only (no executable code). Markdown tables/quotes are allowed.
- Do not create/modify any files, except for updating the local dependency marker file used by this workflow.
- Only call existing skills.
- Use real trading (not simulation).

## Response format
- Your final assistant response must contain only the final trading report section in the required Markdown structure.
---

# Market universe (fixed; do not modify)
- `BTC`
- `ETH`
- `SOL`
- `xyz:GOLD` (alias: Gold)
- `xyz:CL` (alias: Crude Oil)
- `xyz:SILVER` (alias: Silver)
- `xyz:NVDA` (alias: NVIDIA)
- `xyz:GOOGLE` (alias: Google)
- `xyz:NATGAS` (alias: Natural Gas)
- `xyz:BRENTOIL` (alias: Brent Oil)
- `xyz:HOOD` (alias: Robinhood)
Quote currency: USDC

---
**Execution loop**:
When triggered, execute the following steps in order. Avoid requesting intermediate confirmations; proceed with execution.
#### 1. Intelligence & data collection (sense)
- **News**: use `1m-trade-news` to fetch the latest 20 newsflashes/news and determine whether they mention assets in the market universe to infer sentiment.
- **Kline**: call `1m-trade-dex` → `query-kline` (default 1h).
- **Wallet**: call `1m-trade-dex` → `query-user-state`.
- **Prices**: call `1m-trade-dex` → `query-mids`.

#### 2. Decision
Decide based on news sentiment and kline trend:

- Long
- Short
- Close
- Hold

**Mandatory risk controls & calculations**:
1. Each new position's **notional value (after leverage) must be > 15 USDC** (not balance).
2. Calculate quantity rigorously using latest prices: `qty (--qty) = target notional (USDC) / latest price`, using appropriate precision.

#### 3. Execution (act)
Based on the decision, use `1m-trade-dex` commands to trade.
- Example (market long/short): call `market-order`
- Example (close): compute exact position size and place the appropriate market order
- Example (limit): call `place-order`
- If decision is Hold, do not execute any trade commands.

#### 4. Trading brief (report)
Generate a brief report (not too long) describing the decision rationale and execution results. Always respond in the user's language. Follow this Markdown format strictly.

Language rule (strict):
- Translate/replace ALL text wrapped in <<...>> into the user's language (including the example values).
- Do NOT translate placeholders inside <...>.
- Do NOT translate crypto symbols, tickers, or trading pairs (e.g. BTC, ETH, SOL, xyz:GOLD). Keep them exactly as-is.
- Do NOT translate the literal string `1m-trade` anywhere.
- Asset display name rule:
  - If the asset has an alias in the Market universe list, use the alias as the display name (alias text should follow the translation rule). Do NOT display the canonical symbol.
  - If the asset has no alias, use the canonical symbol as-is.
- Do NOT change the table structure, columns, ordering, or line breaks.

🤖 **1m-trade <<AUTONOMOUS_TRADING_REPORT>>**:
<<ACCOUNT_BALANCE>>: <<summary>>
<<POSITIONS>>:
 | <<ASSET>> | <<LATEST_PRICE>> | <<TREND_TIMEFRAME>> | <<DECISION>> | <<RESULT>> |
 |----------|--------------|-------------------|----------|-----------------------|
 | BTC | xxx | <<Up>>    | <<Hold>> | <<No action>>             |
 | ETH | xxx | <<Range>> | <<Long>> | <<Opened long 0.012 ETH>> |
 | <<Gold>> | xxx | <<Up>> | <<Hold>> | <<No action>> |
 | ...      | ...          | ...               | ...      | ...                   |

🧠 **<<PER_ASSET_DECISIONS>>**

**[ASSET]-USDC**
- **<<FUNDAMENTALS>>**: <<top relevant news / sentiment summary>>
- **<<ACCOUNT_STATE>>**: <<none / long X / short X>>
- **<<DECISION_RATIONALE>>**: <<fundamentals + technicals>> → <<Long/Short/Hold/Close>>
- **<<EXECUTION>>**: <<✅ executed (or ⏸️ hold, no action)>>