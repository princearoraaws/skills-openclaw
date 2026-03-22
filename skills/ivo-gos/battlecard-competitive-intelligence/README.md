# Battlecard - Competitive Intelligence for OpenClaw

Add competitive intelligence to your OpenClaw agent. Get battle cards, objection handlers, pricing comparisons, and pre-call briefings for any company vs any competitor.

## What It Does

Battlecard gives your AI assistant access to real-time competitive intelligence tools. Ask your agent to generate battle cards, compare competitors, handle objections, and prepare for sales calls. All without leaving your workflow.

## Available Tools

| Tool | Description | Tier |
|------|-------------|------|
| `get_battle_card` | Compare two companies with strengths, weaknesses, positioning, objection handlers, and pricing | Free |
| `compare_competitors` | Multi-competitor comparison matrix (up to 5 competitors) | Starter |
| `get_objection_handlers` | Specific rebuttals for selling against a named competitor | Starter |
| `capture_call_intelligence` | Extract and store competitive intel from sales call notes | Pro+ |
| `get_field_intelligence` | Aggregate patterns from real sales conversations across your team | Team |
| `generate_pre_call_briefing` | Focused preparation document for upcoming meetings | Pro+ |

## Quick Start

Install via OpenClaw:

```bash
openclaw install battlecard-competitive-intelligence
```

Or add the MCP server manually:

```json
{
  "mcpServers": {
    "battlecard": {
      "url": "https://battlecard.northr.ai/mcp",
      "headers": {
        "X-Battlecard-Key": "your_api_key_here"
      }
    }
  }
}
```

Get your API key at [battlecard.northr.ai/signup](https://battlecard.northr.ai/signup). The free tier gives you 1 competitive snapshot to try it out.

## Example Usage

**Generate a battle card:**
> "Get me a battle card for Notion vs Confluence"

The agent returns a complete competitive breakdown: what Confluence does well, where Notion wins, how to position against them, scripted objection handlers, and a pricing comparison.

**Prepare for objections:**
> "What objections will come up when selling against HubSpot in an enterprise deal?"

Returns the top objections HubSpot users raise and specific rebuttals your reps can use on calls.

**Pre-call briefing:**
> "Generate a pre-call briefing for my meeting tomorrow. The prospect is evaluating Datadog vs New Relic for their observability stack."

Returns a focused briefing covering both competitors, key talking points, pricing angles, and questions to ask the prospect.

## Pricing

| Tier | Price | Queries/Day | Access |
|------|-------|-------------|--------|
| Free | $0 | 1 query | Read-only, single snapshot |
| Starter | $49/mo | 50 | Read-only, all comparison tools |
| Pro | $99/mo | 500 | Read + write (capture intelligence) |
| Team | $149/mo | 2,000 | Full access + aggregate team data |

## Links

- **Full docs:** [battlecard.northr.ai/connect](https://battlecard.northr.ai/connect)
- **Sign up:** [battlecard.northr.ai/signup](https://battlecard.northr.ai/signup)
- **Homepage:** [battlecard.northr.ai](https://battlecard.northr.ai)

Built by [Northr AI](https://northr.ai).
