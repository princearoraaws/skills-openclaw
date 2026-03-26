---
name: 360-web-search
version: 1.0.3
author: 360 AI Platform
homepage: https://ai.360.cn
description: >
  Real-time Chinese web search powered by 360's search engine API.
  Use this skill when the user asks to search the web, look up recent news,
  find current information, or query anything related to Chinese companies,
  products, regulations, or market data — especially when results may have
  changed after the model's training cutoff.
tags: [search, web, chinese, news, realtime, rag, agent]
metadata:
  clawdbot:
    requires:
      env:
        - SEARCH_360_API_KEY
      bins:
        - curl
    primaryEnv: SEARCH_360_API_KEY
    confirmBeforeRun: true
---

# 360 Web Search

## Security & Privacy Disclosure

**External endpoints contacted by this skill:**

| Endpoint | Purpose | Data sent |
|----------|---------|-----------|
| api.360.cn/v2/mwebsearch | Search query execution | Search query string, UUID session ID |

This skill sends the user's search query to 360's search API. No other data
is transmitted. Queries are not stored locally. The API key is read from the
environment variable `SEARCH_360_API_KEY` and is never logged or echoed.

**Trust statement:** This skill only performs outbound GET requests to
api.360.cn. It does not write to the filesystem, does not execute shell
commands, and does not access any local files or environment variables
beyond `SEARCH_360_API_KEY`.

---

## When to Use This Skill

Use 360-web-search when the user:

- Asks to "search", "look up", "find recent", or "browse the web"
- Uses Chinese phrases such as 搜索, 查一下, 联网, 最新, 帮我找
- Needs information that may have changed after the model's training cutoff
- Asks about Chinese companies, people, products, news, policies, or market data
- Wants to verify a current fact or check the live status of something

**Do not use** for math, code generation, creative writing, or questions
fully answerable from training data.

**Confirmation policy:** Before running a search, briefly confirm the query
with the user if the intent is ambiguous. For clear search requests, proceed
directly.

---

## Step 1 — Credential Check

Check whether `SEARCH_360_API_KEY` is set and non-empty.

- **Present** → proceed to API Call
- **Missing** → run the Key Setup Flow below

---

## Key Setup Flow

When the credential is not configured, tell the user:

```
To use 360 Web Search, you need an API key (takes ~2 minutes to set up):

1. Visit https://ai.360.cn and sign in
2. Go to Open Platform → API Key Management
3. Create an application and copy the key string

To store the key securely, add it to OpenClaw's agent config instead of
your shell profile. In your OpenClaw workspace, open or create the file:

   ~/.openclaw/agents/default/env.json

And add:
   {
     "SEARCH_360_API_KEY": "your-key-here"
   }

This file is agent-scoped and not sourced into your global shell environment.
Restart QClaw / OpenClaw after saving.
```

---

## API Call

- Endpoint: `api.360.cn/v2/mwebsearch`
- Protocol: HTTPS GET
- Auth: Bearer token from `SEARCH_360_API_KEY` environment variable

**Required parameters:**

| Parameter | Value |
|-----------|-------|
| q | The user's search query (Chinese or English) |
| ref_prom | Fixed value: `aiso-pro` |
| sid | Fresh UUID generated per request |

**Optional parameters:**

| Parameter | Description |
|-----------|-------------|
| count | Number of results (default 10, recommended 5) |
| fresh_day | Limit to results within last N days (e.g. 7) |
| date_range | Custom date range filter |

---

## Response Fields

Verify the response indicates success, then read the results list:

| Field | Description |
|-------|-------------|
| title | Page title |
| url | Source URL — always show this to the user |
| summary_ai | AI-generated summary — prefer this field |
| summary | Raw text excerpt — fallback if summary_ai is empty |
| site_name | Publisher name (e.g. Sina, 36Kr, Caixin) |
| page_time | Publish datetime |
| official_site | 1 = authoritative source, 0 = other |
| rank | Ranking position |

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Credential missing | Run Key Setup Flow |
| Auth failure (401) | Tell the user the key is invalid; guide them to get a new one |
| Rate limited (429) | Wait 5 seconds, retry once automatically |
| Empty results | Suggest rephrasing the query or removing date filters |
| Other errors | Show the error message and suggest retrying |

---

## Output Rules

- Always include the source URL for every result shown
- Prefer `summary_ai` over `summary` for cleaner output
- Show `page_time` so users can judge freshness
- Label results as "Official" when `official_site` equals 1
- Generate a new UUID for `sid` on every request — never reuse
