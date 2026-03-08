---
name: verify-claim
description: Verify factual claims against live data sources. Returns structured verdicts with confidence scores.
version: 1.0.1
metadata:
  openclaw:
    emoji: "🔍"
    homepage: https://verify.agentutil.net
    always: false
---

# verify-claim

Verify any factual claim against live data sources. Returns a structured verdict with confidence score, current truth value, and freshness indicator.

## Usage

Send a POST request to verify a claim:

```bash
curl -X POST https://verify.agentutil.net/v1/verify \
  -H "Content-Type: application/json" \
  -d '{"claim": "The USD to EUR exchange rate is 0.92"}'
```

## Response Format

```json
{
  "verdict": "confirmed",
  "confidence": 0.95,
  "current_truth": "0.921",
  "freshness": "live",
  "source_count": 2,
  "cached": false,
  "request_id": "abc-123",
  "service": "https://verify.agentutil.net"
}
```

## Verdicts

- `confirmed` — claim matches current data
- `stale` — claim was true but data has changed
- `disputed` — sources disagree
- `false` — claim contradicts current data
- `unknown` — unable to verify

## Categories

Optionally specify a category for faster routing:

- `financial` — exchange rates, crypto prices, stock prices
- `entity` — company info, population, founding dates
- `geo` — timezones, geographic data
- `factcheck` — general fact-checking via Google Fact Check API

```json
{"claim": "Bitcoin price is above $50,000", "category": "financial"}
```

## Trending Claims

Get the top 100 most-queried claims in the last 24 hours:

```bash
curl https://verify.agentutil.net/v1/trending
```

## Pricing

- Free tier: 25 queries/day, no authentication required
- Paid tier: unlimited queries via x402 protocol (USDC on Base), $0.004/query

## Agent Discovery

- Agent Card: `https://verify.agentutil.net/.well-known/agent.json`
- Service metadata: `https://verify.agentutil.net/.well-known/agent-service.json`
- MCP server: `@agentutil/verify-mcp` (npm)

## Privacy

No authentication required for free tier. Query content is not stored beyond transient cache (max 1 hour). No personal data collected. Rate limiting uses IP hashing only.
