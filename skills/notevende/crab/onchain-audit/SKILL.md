---
name: onchain-audit
description: |
  On-chain data and contract security analysis.
  Includes Binance API and Bitget API for audit, token info, wallet,
  and contract analysis. CLAWBOT decides which to use based on context.
metadata:
  author: NotevenDe
  version: 1.3.0
---

# On-chain Audit — Contract & On-chain Analysis

Two data sources; CLAWBOT chooses based on context.
Binance and Bitget data can be cross-verified.

---

## 1. Binance API (onchain)

`POST https://crab-skill.opsat.io/api/onchain/*` (requires Crab signature)

Fields: `address` + `chainName` (uppercase: `BSC`/`ETHEREUM`/`BASE`/`SOLANA`)

| Endpoint | Description |
|----------|-------------|
| `/api/onchain/audit` | Contract security audit (Binance + Bitget dual-source) |
| `/api/onchain/token-info` | Token metadata and market dynamics |
| `/api/onchain/wallet` | Wallet positions (BSC/BASE/SOLANA only) |
| `/api/onchain/token-search` | Token search (requires `keyword` instead of `address`) |

---

## 2. Bitget API (onchain-2)

`POST https://crab-skill.opsat.io/api/onchain-2/*` (requires Crab signature)

Fields: `chain` + `contract` (lowercase: `bnb`/`eth`/`base`/`sol`)

> Note: field names and chain format differ from Binance endpoints.

| Endpoint | Description |
|----------|-------------|
| `/api/onchain-2/token-info` | Token details (symbol, name, market cap, etc.) |
| `/api/onchain-2/token-price` | Token price summary |
| `/api/onchain-2/tx-info` | Token transaction statistics |
| `/api/onchain-2/liquidity` | Liquidity pool info |
| `/api/onchain-2/security-audit` | Security audit (risk/warn/low checks) |

---

## Fallback Behavior

| Scenario                     | Behavior                     |
|-----------------------------|------------------------------|
| Unknown contract chain      | Skip audit                   |
| No token search results     | Skip token search            |
| Wallet chain not supported  | Skip wallet query            |
