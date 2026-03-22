---
name: defi-scout
description: |
  On-chain DeFi intelligence for AI agents. Use when asked about wallet balances, token prices, DEX quotes, yield opportunities, protocol TVL, gas prices, or airdrop farming on Optimism and Base. Triggers on wallet checks, ETH price, best yields, swap quotes, DeFi opportunities, gas, TVL, airdrop farming, Aerodrome, Velodrome, Aave, Optimism, Base, or any on-chain financial query.
---

# DeFi Scout

On-chain financial intelligence across Optimism and Base. Uses free public APIs — no API keys required.

## Data Sources

| Source | What | Endpoint |
|--------|------|----------|
| CoinGecko | Token prices | `api.coingecko.com/api/v3/simple/price` |
| DeFiLlama | Protocol TVL, yields | `api.llama.fi` |
| Optimism RPC | Balances, gas | `mainnet.optimism.io` |
| Base RPC | Balances, gas | `mainnet.base.org` |
| Across API | Bridge quotes | `app.across.to/api/suggested-fees` |

## Core Scripts

All scripts output JSON. Run with `node scripts/<name>.js`.

| Script | Purpose |
|--------|---------|
| `wallet-balances.js` | ETH + ERC-20 balances on OP + Base |
| `token-price.js` | CoinGecko price for any token |
| `yields.js` | Top yield pools on OP + Base from DeFiLlama |
| `gas.js` | Current gas on Optimism and Base |
| `bridge-quote.js` | Across Protocol bridge fee quote (no deps, 10s timeout) |
| `aave-position.js` | Aave V3 health factor + collateral/debt on OP + Base |
| `swap-quote.js` | Price-based swap estimate via CoinGecko (price math only — not a protocol-routed quote) |

## Script Details

### aave-position.js
```bash
node scripts/aave-position.js <0x-address>
```
Queries Aave V3 Pool `getUserAccountData` on both Optimism and Base via direct JSON-RPC `eth_call`. Returns collateral, debt, available borrows, liquidation threshold, LTV, and health factor. Adds a `warning` field if health factor < 1.2 (liquidation risk). 8-second timeout per RPC call.

### swap-quote.js
```bash
node scripts/swap-quote.js <token_in> <token_out> <amount_in> [--chain optimism|base]
# Example: node scripts/swap-quote.js ETH USDC 1.5 --chain base
```
Fetches live prices from CoinGecko and computes estimated output = `(priceIn / priceOut) * amountIn * 0.997` (0.3% fee estimate). Supported tokens: ETH, WETH, USDC, USDT, OP, VELO, AERO, cbETH. **Not a real quote** — use Aerodrome/Velodrome UI for execution.

## Workflow

**Wallet check:** Run `wallet-balances.js <address>` → summarise balances + USD value.

**Opportunity scan:** Run `yields.js` → filter by chain, TVL >$1M, sort by APY. Flag stable pairs (no IL) and volatile pairs separately. Cross-reference gas cost vs position size before recommending entry.

**Bridge quote:** Run `bridge-quote.js <amount_eth> [from_chain=10] [to_chain=8453]` → returns fee, fill time, output amount.

**Price check:** Run `token-price.js <coingecko_id>` → price, 24h change.

**Aave health check:** Run `aave-position.js <address>` → health factor on both chains. Act immediately if < 1.2.

**Swap estimate:** Run `swap-quote.js <tokenIn> <tokenOut> <amount>` → rough output estimate for planning. Never use for execution.

## Key Addresses (verified)

See `references/addresses.md` for verified contract addresses on Optimism and Base.

## Risk Rules

- Never recommend pools with TVL < $1M
- Flag APY > 100% as high-risk / likely temporary incentive
- Always show gas cost as % of position before recommending entry
- Stable pairs (USDC-USDT, USDC-msUSD) = lower risk, note explicitly
