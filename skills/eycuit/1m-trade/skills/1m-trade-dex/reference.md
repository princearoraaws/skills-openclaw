# hl1m Reference

`hl1m` is the CLI entrypoint installed from the `1m-trade` package. It combines Hyperliquid queries, trading, wallet initialization, and Relay bridging workflows.

---

## 1. Install & Entrypoint

### 1.1 Install
```bash
pipx install 1m-trade
```

### 1.2 Show help
```bash
hl1m --help
```

### 1.3 Global flags
- `--testnet`: use Hyperliquid testnet (default: mainnet)

---

## 3. Command overview

### 3.1 Query commands
- `query-user-state`: query user positions and balances
- `query-open-orders`: query open orders
- `query-fills`: query filled trades
- `query-meta`: query exchange metadata
- `query-mids`: query all symbols mid prices
- `query-kline`: query kline/candles

### 3.2 Trading commands
- `place-order`: place a limit order
- `market-order`: place a market order
- `cancel-order`: cancel orders
- `update-leverage`: update leverage
- `market-close`: close with market order
- `update-isolated-margin`: transfer margin into isolated position

### 3.3 Wallet & funding commands
- `create-wallet`: create a wallet
- `init-wallet`: initialize wallet config with user-provided private key (proxy wallet supported)
- `send-private-key`: securely deliver private key to current user through secure channel
- `start-listener`: after deposit arrives, execute bridge flow

---

## 4. Query command details

### 4.1 `query-user-state`
Query user state (positions + balances).

```bash
hl1m query-user-state [--address 0x...]
```

- `--address` optional; if omitted, address is derived from env/private key.

### 4.2 `query-open-orders`
```bash
hl1m query-open-orders
```

### 4.3 `query-fills`
```bash
hl1m query-fills
```

### 4.4 `query-meta`
```bash
hl1m query-meta
```

### 4.5 `query-mids`
```bash
hl1m query-mids
```

### 4.6 `query-kline`
```bash
hl1m query-kline --coin BTC --period 1m [--start <ms>] [--end <ms>]
```

- `--coin` required
- `--period` required, supports: `1m,3m,5m,15m,30m,1h,2h,4h,8h,12h,1d,3d,1w,1M`
- `--start` default: now minus 24h (milliseconds)
- `--end` default: now (milliseconds)

---

## 5. Trading command details

### 5.1 `place-order`
```bash
hl1m place-order --coin BTC --is-buy true --qty 0.01 --limit-px 60000 [--tif Gtc] [--reduce-only]
```

- `--coin` required
- `--is-buy` required: `true/false`
- `--qty` required
- `--limit-px` required
- `--tif` optional: `Gtc | Ioc | Alo`, default `Gtc`
- `--reduce-only` optional

### 5.2 `market-order`
```bash
hl1m market-order --coin BTC --is-buy true --qty 0.01 [--slippage 0.02]
```

### 5.3 `cancel-order`
```bash
hl1m cancel-order [--oid 123] [--coin BTC]
```

- Without `--oid` and `--coin`: cancel all open orders
- With `--coin`: cancel all open orders for that symbol
- With `--oid`: cancel specific order

### 5.4 `update-leverage`
```bash
hl1m update-leverage --coin BTC --leverage 5 [--is-cross true]
```

### 5.5 `market-close`
```bash
hl1m market-close --coin BTC --qty 0.01 [--slippage 0.02]
```

### 5.6 `update-isolated-margin`
```bash
hl1m update-isolated-margin --coin BTC --amount 100
```

---

## 6. Wallet command details

### 6.1 `create-wallet`
Generate a new wallet and write the private key to `.env` using the unified encryption scheme.

```bash
hl1m create-wallet --target <openclaw_target> --lang <zh_or_en>
```

- `--target` required, current OpenClaw session user ID
- `--lang` user language, `zh` or `en`, default `en`
- Optional positional arg `openclaw_target`: if provided, Stage 3 (send private key via `openclaw`) is triggered automatically
- Protection logic: if `.env` already contains any wallet-related fields, overwrite is rejected

### 6.2 `init-wallet` / `init_wallet`
Initialize `.env` using a user-provided private key (optional address).

```bash
hl1m init-wallet --pri_key 0x...
hl1m init-wallet --address 0x... --pri_key 0x...
```

- `--pri_key` required
- `--address` optional; if omitted, derived from private key
- If `--address` is provided, current behavior uses it directly (to support proxy-private-key scenarios, no strict matching check)
- Protection logic: if `.env` already has address/encrypted key/encryption password, overwrite is rejected

### 6.3 `send-private-key`
Send private key through `openclaw` secure channel (does not pass through LLM output).

```bash
hl1m send-private-key --target <openclaw_target> --lang <zh_or_en>
```

- `--target` required, current OpenClaw session user ID
- `--lang` user language, `zh` or `en`, default `en`

### 6.4 `start-listener`
Run the funding pipeline:
1) check Arbitrum USDC balance  
2) request Relay quote and execute steps (including approve handling)  
3) set Hyperliquid referrer to activate trading channel

```bash
hl1m start-listener
```

---

## 7. Output and exit codes

- Most commands print JSON or human-readable logs
- Failures usually exit with `SystemExit(1)` or print `❌ ...` error messages
- `start-listener` failures return non-zero (CLI normalizes to exit code 1)

---