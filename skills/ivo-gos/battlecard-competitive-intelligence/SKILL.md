---
name: battlecard-competitive-intelligence
description: Get AI-powered competitive battle cards, objection handlers, and sales intelligence for any company vs any competitor. Built for sales teams who need real-time competitive data during deals.
version: 1.0.0
author: northr-ai
tags:
  - sales
  - competitive-intelligence
  - battle-cards
  - sales-enablement
  - b2b
  - mcp
openclaw:
  requires:
    env:
      - BATTLECARD_API_KEY
  primaryEnv: BATTLECARD_API_KEY
---

# Battlecard - Competitive Intelligence

Add competitive intelligence to your OpenClaw agent. Get battle cards, objection handlers, pricing comparisons, and pre-call briefings for any company vs any competitor.

## Setup

Set your Battlecard API key:

```
export BATTLECARD_API_KEY=bc_live_xxxxxxxxxxxxx
```

Get your API key at https://battlecard.northr.ai/signup (free tier available, 1 query free).

## MCP Connection

This skill connects to the Battlecard MCP server. Add to your MCP configuration:

```json
{
  "mcpServers": {
    "battlecard": {
      "url": "https://battlecard.northr.ai/mcp",
      "headers": {
        "X-Battlecard-Key": "${BATTLECARD_API_KEY}"
      }
    }
  }
}
```

## Available Tools

When connected, you can ask your agent to:

- **Get a battle card**: "Get me a battle card for Notion vs Confluence" - Returns strengths, weaknesses, positioning, objection handlers, pricing comparison.
- **Compare competitors**: "Compare HubSpot, Salesforce, and Pipedrive for our CRM needs" - Multi-competitor matrix for up to 5 competitors.
- **Get objection handlers**: "What objections will come up selling against HubSpot in an enterprise deal?" - Specific rebuttals with context.
- **Capture call intelligence**: "Extract competitive intel from these call notes: [paste notes]" - Stores structured data from sales conversations. Pro tier.
- **Get field intelligence**: "What are the most common objections against Salesforce?" - Aggregate patterns from real sales conversations. Team tier.
- **Generate pre-call briefing**: "Prepare me for my meeting tomorrow, prospect is evaluating Datadog vs New Relic" - Focused preparation document. Pro tier.

## Pricing

- Free: 1 competitive snapshot
- Starter $49/mo: 50 queries/day, 3 competitors
- Pro $99/mo: 500 queries/day, unlimited competitors, write access
- Team $149/mo: 2000 queries/day, aggregate intelligence

Full docs: https://battlecard.northr.ai/connect
