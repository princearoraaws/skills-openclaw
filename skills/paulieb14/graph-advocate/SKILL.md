---
name: graph-advocate
description: Route any onchain data request to the right Graph Protocol service. Given plain-English, returns a ready-to-execute tool call for Token API, Subgraph Registry, Substreams, or a protocol-specific MCP package.
version: 1.2.0
metadata:
  openclaw:
    emoji: "🗂️"
    homepage: https://github.com/PaulieB14/graph-advocate
---

# Graph Advocate

**Graph Advocate** is a routing agent for The Graph Protocol. Given a plain-English onchain data request, it returns structured JSON identifying the right service, the reason, and the exact tool call to run.

## What it covers

- 📊 **Token API** — wallet balances, swaps, NFT sales, holder rankings across EVM (Ethereum, Base, Polygon, Arbitrum), Solana, and TON
- 🔍 **Subgraph Registry** — 15,500+ indexed protocol subgraphs (Uniswap, Aave, ENS, Compound, Curve, Balancer and more)
- ⚡ **Substreams** — raw block data, event logs, real-time streaming
- 🧩 **Protocol MCP packages** — Aave, Polymarket, lending protocols, Predict.fun

## Response format

Graph Advocate returns structured JSON with a recommendation, confidence score, and ready-to-run query arguments:

```json
{
  "recommendation": "token-api",
  "reason": "getV1EvmHolders returns ranked holder lists by token contract.",
  "confidence": "high",
  "query_ready": {
    "tool": "getV1EvmHolders",
    "args": {
      "network_id": "mainnet",
      "contract": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
      "limit": 20
    }
  },
  "alternatives": []
}
```

## Example requests

- `"Top 20 USDC holders on Ethereum"`
- `"Uniswap V3 pool TVL and fee tiers"`
- `"Aave liquidation events last 7 days"`
- `"Solana NFT sales this week"`
- `"Raw event logs blocks 19000000 to 20000000"`
- `"Which package should I use for Polymarket data?"`

## Protocol MCP packages

When Graph Advocate recommends a protocol package, it returns the package name and install instructions:

| Package | Protocol |
|---|---|
| `graph-aave-mcp` | Aave V2/V3 — 7 chains, 11 subgraphs |
| `graph-polymarket-mcp` | Polymarket prediction markets |
| `graph-lending-mcp` | Cross-protocol lending (Messari standard) |
| `predictfun-mcp` | Predict.fun on BNB Chain |
| `subgraph-registry-mcp` | 15,500+ classified subgraphs |
| `substreams-search-mcp` | Substreams package browser |

## Links

- GitHub: https://github.com/PaulieB14/graph-advocate
- The Graph Protocol: https://thegraph.com
- The Graph Docs: https://thegraph.com/docs
- Token API: https://thegraph.com/docs/en/token-api
- Subgraph Studio: https://thegraph.com/studio
