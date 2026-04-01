---
name: toolrouter
description: One gateway to 150+ tools for AI agents — competitor research, video production, web search, image generation, security scanning, and more. Requires a ToolRouter API key (auto-provisioned on first use at toolrouter.com).
---

# ToolRouter

Give your AI agent superpowers with access to 150+ tools on demand with just one account. One API key replaces managing dozens of provider accounts.

## Authentication

**Requires a ToolRouter API key.** Get one at [toolrouter.com](https://toolrouter.com) — auto-provisioned on first use. Set via `TOOLROUTER_API_KEY` environment variable.

```json
{
  "mcpServers": {
    "toolrouter": {
      "command": "npx",
      "args": ["-y", "toolrouter-mcp"],
      "env": {
        "TOOLROUTER_API_KEY": "your-api-key"
      }
    }
  }
}
```

## Setup

### Option A: npx (stdio bridge)

The `toolrouter-mcp` npm package ([npmjs.com/package/toolrouter-mcp](https://www.npmjs.com/package/toolrouter-mcp)) is a lightweight stdio-to-HTTP bridge that connects your local MCP client to the hosted ToolRouter API.

```
npx -y toolrouter-mcp
```

**Source:** Published on npm by [Humanleap](https://toolrouter.com). The package proxies MCP requests to `api.toolrouter.com` over HTTPS.

### Option B: Remote MCP (streamable HTTP)

Connect directly to the hosted endpoint — no local code execution:

```
https://api.toolrouter.com/mcp
```

Authentication via API key header. Works with any MCP client that supports remote/streamable HTTP transport.

## What You Get

150+ tools across these categories, growing daily:

- **Research** — competitor intelligence reports, deep research with citations, academic papers
- **Video & Audio** — video production from creative briefs, AI dubbing in any language, text-to-speech with 1000+ voices
- **Search & Data** — web search, job listings with salary data, SEC filings, lead generation
- **Security** — penetration testing, vulnerability scanning, supply chain risk auditing
- **Web Extraction** — stealth scraping through bot protection, structured data extraction
- **Image & Media** — image generation, brand logo extraction
- **Travel** — live flight search with pricing, hotel and stay comparisons
- **Documents** — Word docs, Excel, PowerPoint, PDF creation and editing
- **Marketing** — ad library search, social media analytics, app store optimization

## Usage

### Discover tools

```json
{
  "tool": "toolrouter",
  "skill": "discover",
  "input": { "query": "competitor research" }
}
```

### Call a tool

```json
{
  "tool": "toolrouter",
  "skill": "use_tool",
  "input": {
    "tool": "competitor-research",
    "skill": "analyze",
    "input": { "url": "https://example.com" }
  }
}
```

## Billing

Usage-based — pay per tool call. Most calls cost fractions of a cent. No subscriptions required.

## Links

- Website: [toolrouter.com](https://toolrouter.com)
- npm: [npmjs.com/package/toolrouter-mcp](https://www.npmjs.com/package/toolrouter-mcp)
- API: [api.toolrouter.com](https://api.toolrouter.com)
