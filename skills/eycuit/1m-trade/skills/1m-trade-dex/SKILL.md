---
name: 1m-trade-dex
description: |
  Hyperliquid DEX/Perps entrypoint. Supports queries (state/orders/fills/metadata/kline) and trading (place/cancel orders, leverage, margin updates), plus EVM wallet creation, funding/bridging to Hyperliquid L1, and account activation.
requires:
  bins: [hl1m, openclaw]
install:
  - pipx install 1m-trade
metadata:
  openclaw:
    emoji: "🚀"
    os: [darwin, linux, win32]
    tags: [crypto, news, trading, hyperliquid, wallet, dex, automation]
---

## Setup Instructions

### 1. Check if CLI is Installed

```bash
which hl1m
```
If not found, install it:
### Runtime requirements
- Python 3.11+
#### Installation steps:

If `pipx` exists, use it to install `1m-trade`.

If `pipx` is not found:
- Linux: install `pipx` via `apt` / `yum` / `dnf`
- macOS: `brew install pipx`
- Windows: `python -m pip install --user pipx` and `python -m pipx ensurepath`

```bash
pipx install 1m-trade
```
### 2. Verify Installation

```bash
hl1m --help
```

### Basic syntax
```bash
# Full command
hl1m [--testnet] <command> [command_args]
```
### Core flags
- `--testnet`: optional, use testnet (default is mainnet)

### Update CLI
Upgrade to the latest:
```bash
pipx upgrade 1m-trade
```
### Wallet / Funding / Activation (merged into `hl1m`)
## Branch A: Funding channel (deposit & activation)

### Stage 1: Generate a lightning funding wallet
**When to trigger**: when the user says things like "create account", "generate address", "fund HL", "start", "create wallet", "give me a new wallet", etc.

**Special notes**:
- You must never modify or delete any script files. You only execute commands.
- **LLM must not** open/read `.env` into the model context or paste secret values in chat. Local CLIs (`hl1m`, `openclaw`) may read `.env` on disk to perform actions; your job is to **run the right command**, not to relay the secret yourself.
- If the user asks for their private key, use Stage 3 only: call the send command so delivery goes through the **secure channel**, not through the LLM.
- If the user has created a wallet before, run Stage 3 first and remind them to back up the old wallet details to avoid mistakes, then proceed to create a new wallet.

**Actions**:
1. **Run create-wallet**:
     ```bash
     hl1m create-wallet --target "<chat user ID>" --lang "<zh or en>"
     ```
   - `<chat user ID>` is the same value used for `send-private-key` (e.g. `7677353341`). The script will **persist the wallet**, then **immediately** invoke Stage 3 (`openclaw message send`) to deliver the private key — **do not paste the key in LLM chat**.
2. Read the script output carefully.
3. **Your response**: format and send the **deposit address** and the **quick-start instructions** to the user. If Stage 3 succeeded, add only: private key was **sent via the secure channel**; ask them to save it and delete the message — **never repeat or quote the key**.
4. **Security**: do not put the private key in model memory/context or print it in chat. Only send the **deposit address** + instructions (+ the short “sent via secure channel” line if applicable). Actual key delivery is done by CLI → secure channel only.
5. If `create-wallet` reported that Stage 3 failed, **immediately** run Stage 3 manually:
   ```bash
   hl1m send-private-key --target "<chat user ID>" --lang "<zh or en, default: en>"
   ```

### Stage 2: Bridge & activate account
**When to trigger**: when the user says "deposit done", "I funded it", "check", "did it arrive", etc.

**Actions**:
1. Run: `hl1m start-listener`
2. Read the script output carefully.
   - If the script succeeds, send **all logs and success messages verbatim**. Do not add extra technical explanations.
3. After execution, call `hl1m query-user-state` to verify balances.

### Stage 3: Secure private-key delivery (CLI only; model invokes command only)
**When to trigger**:
- The user explicitly asks "what is my private key" / "send me the private key", etc.; or
- Right after wallet creation when Stage 1 did **not** pass `<chat user ID>` to `create-wallet`, or when auto Stage 3 failed — deliver the key once via the OpenClaw messaging channel.

**Actions**: The LLM **only runs** the CLI below. It must **not** read the key from disk into chat or paraphrase it. The CLI reads local state and sends via the secure channel.
1. Run:
   ```bash
   hl1m send-private-key "<chat user ID>"
   ```
   - `<chat user ID>` is the user's OpenClaw channel/user ID (e.g. `7677353341`).
2. In chat, only say: "Sent via secure channel. Please check and store it safely." Do **not** print the key in chat.


### Stage 4: Register gas address
**When to trigger**: "direct USDC deposit", "free gas", "how to deposit USDC", "can I deposit USDC directly".

**Actions**:
1. Run: `hl1m register-address`
2. Read the script output carefully.
   - If the script succeeds, send **all logs and success messages verbatim**. Do not add extra technical explanations.
3. After execution, call `hl1m query-user-state` to verify balances.


### Constraints
- If the user cannot open a position (e.g., insufficient margin), do not close other positions unless the user explicitly requests it.

### Command list
Note: for any asset name (e.g. `--coin`), you can run `query-meta` to confirm the exact symbol. For example, user input "gold" often maps to `xyz:GOLD`. Always pass the canonical symbol.

#### 1) Query commands
| Command | Description | Example |
|------|------|------|
| `query-user-state` | Query user state (positions + balances). Optional address override; structure follows the API/SDK response. | `hl1m query-user-state --address 0x123...` |
| `query-open-orders` | Query open orders | `hl1m --testnet query-open-orders` |
| `query-fills` | Query fills / trade history | `hl1m query-fills` |
| `query-meta` | Query asset metadata (all symbols) | `hl1m query-meta` |
| `query-mids` | Query mid prices (all symbols) | `hl1m query-mids` |
| `query-kline` | Query kline/candles for a symbol | `hl1m query-kline --coin BTC --period 15m --start 1772511125000 --end 1772597525000` |

**Retry rule (query commands only)**:
- If a query command returns an empty result (null/None, empty string, empty list/array, empty object/dict, or no meaningful fields), retry the **same command** exactly once.
- Do not change any args/flags/symbols/time ranges/formatting between the first attempt and the retry.
- If the second attempt is still empty, stop retrying and report: the command you ran, that it returned empty twice, and a brief possible cause (no data, endpoint delay, wrong symbol, no account activity).

### Query command arguments

#### `query-user-state`
- `--address`: optional. If omitted, the address is derived from the configured private key.

#### `query-kline`
- `--coin`: required. Symbol such as `BTC`, `ETH`, or `xyz:TSLA`. Use `query-meta` to confirm the canonical symbol first.
- `--period`: required. One of: `1m`, `3m`, `5m`, `15m`, `30m`, `1h`, `2h`, `4h`, `8h`, `12h`, `1d`, `3d`, `1w`, `1M`.
- `--start`: optional (ms). Default is the start of the last 24 hours.
- `--end`: optional (ms). Default is the current timestamp in ms.

#### 2) Trading commands
| Command | Description | Example |
|------|------|------|
| `place-order` | Place a limit order (HIP-3 supported) | `hl1m place-order --coin BTC --is-buy True --qty 0.01 --limit-px 50000 --tif Gtc` |
| `market-order` | Place a market order (recommended for HIP-3) | `hl1m --testnet market-order --coin ETH --is-buy True --qty 0.1 --slippage 0.01` |
| `market-close` | Close a position with a market order (recommended for HIP-3) | `hl1m market-close --coin ETH --qty 0.1 --slippage 0.01` |
| `cancel-order` | Cancel orders | `hl1m cancel-order --oid 123456 --coin HYPE` |
| `update-leverage` | Update leverage | `hl1m update-leverage --coin BTC --leverage 10 --is-cross True` |
| `update-isolated-margin` | Transfer isolated margin (HIP-3) | `hl1m update-isolated-margin --coin xyz:GOLD --amount 10` |

### Trading command arguments
#### General rules
1. For `--coin`, always resolve the canonical symbol (use `query-meta` if needed).
2. For `--qty`, use `query-meta` results (e.g. `szDecimals`) to format the quantity precision correctly.

#### `update-isolated-margin`
- `--coin`: required. Canonical symbol.
- `--amount`: required. Transfer amount.

#### `place-order`
- `--coin`: required.
- `--is-buy`: required (True/False). True = long, False = short.
- `--qty`: required.
- `--limit-px`: required.
- `--tif`: optional (`Gtc`/`Ioc`/`Alo`, default `Gtc`).
- `--reduce-only`: optional (default False).

#### `market-order`
- `--coin`: required.
- `--is-buy`: required (True/False). True = long, False = short.
- `--qty`: required.
- `--slippage`: optional (default 0.02 = 2%).

#### `market-close`
- `--coin`: required.
- `--qty`: required.
- `--slippage`: optional (default 0.02 = 2%).

#### `cancel-order`
- `--coin`: optional; cancel all orders for a given symbol
- `--oid`: optional; cancel a specific order id
- If neither is provided, cancel all open orders.

#### `update-leverage`
- `--coin`: required.
- `--leverage`: required (integer).
- `--is-cross`: optional (True/False, default True).

## Output
All commands print formatted JSON for easy parsing:
- Query commands: full data for the requested dimension
- Trading commands: results for order submit/cancel/leverage updates (success flags, order IDs, etc.)

## Error handling
- Network issues: handled by the SDK with error messages
- Invalid trading parameters: returns official Hyperliquid error responses

## Notes
1. Private keys are sensitive. Do not expose or share them.
2. Testnet vs mainnet are strictly separated. Confirm `--testnet` before acting.
3. Adjust slippage for market orders based on volatility; too small may fail.
4. Leverage trading is risky. Choose leverage carefully.
5. If using a proxy/private-key setup, ensure `HYPERLIQUID_WALLET_ADDRESS` is set; otherwise trading may fail.

## Summary
- `1m-trade-dex` follows your published PyPI CLI (`hl1m`): users can run queries and trading with `hl1m` after `pip install 1m-trade`, including `--testnet` switching.
- All commands output structured JSON; for wallet/funding/activation subcommands, use `hl1m --help` as the source of truth (wallet capabilities are merged into this CLI).