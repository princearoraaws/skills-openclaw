---
name: smart-api-connector
description: "Connect to any REST API without writing code. Provide an endpoint and API key, and the agent handles authentication, request formatting, error parsing, retries, and rate limiting. API keys are session-only — never persisted to disk, shell config, or environment variables. Use when: user wants to query an API, test an endpoint, automate API calls, parse API responses, or integrate with external services. Supports GET, POST, PUT, DELETE with JSON payloads. Homepage: https://clawhub.ai/skills/smart-api-connector"
---

# Smart API Connector

Connect to any REST API without code. The agent handles everything — you just provide the endpoint.

## Language

Detect from the user's message language. Default: English.

## Related Skills

| Skill | Why |
|-------|-----|
| `setup-doctor` | Diagnose environment issues before API work |
| `context-brief` | Long API sessions consume context — brief keeps things lean |
| `locale-dates` | Format API timestamps to user's locale |

> 💡 **Full suite**: `clawhub install setup-doctor && clawhub install context-brief && clawhub install locale-dates`

## Quick Start

User provides:
1. **API base URL** (e.g., `https://api.example.com/v1`)
2. **API key** (session-only, never stored)
3. **What they want to do** in natural language

Agent does everything else.

## Connection Setup

### Step 1: Handle API Key

When user provides an API key, use it in-session for the current request chain. **Do NOT persist API keys anywhere** — no shell config files, no environment variables, no file writes.

- Use the key only within the current conversation/session
- NEVER display the full key back or log it
- After the session ends, the key is gone — user must provide it again next time

If the user asks to store a key permanently, recommend they use their OS keychain or a secret manager (1Password, Bitwarden, Windows Credential Manager) instead.

### Step 2: Verify Connection

Test with a simple request before any real work:

```bash
curl -s -o /dev/null -w "%{http_code}" --max-time 10 -H "Authorization: Bearer YOUR_API_KEY" "https://api.example.com/v1/health"
```

- HTTP 200 → ✅ Connected
- HTTP 401 → ❌ Invalid key — ask user to verify
- HTTP 403 → ⚠️ Valid key, insufficient permissions
- Timeout → ⚠️ Network issue or API down

### Step 3: Discover Endpoints (optional)

If user says "explore" or "what can I do":

```bash
curl -s -H "Authorization: Bearer YOUR_API_KEY" "https://api.example.com/v1/openapi.json"
```

Parse the OpenAPI spec and list available endpoints with descriptions.

## Making Requests

### GET (Read Data)

When user says "get X" or "fetch Y" or "list Z":

```bash
curl -s --max-time 30 -H "Authorization: Bearer YOUR_API_KEY" -H "Content-Type: application/json" "BASE_URL/endpoint?param=value"
```

### POST (Create Data)

When user says "create X" or "send Y" or "add Z":

```bash
curl -s --max-time 30 -X POST -H "Authorization: Bearer YOUR_API_KEY" -H "Content-Type: application/json" -d '{"key": "value"}' "BASE_URL/endpoint"
```

### PUT/PATCH (Update Data)

When user says "update X" or "change Y":

```bash
curl -s --max-time 30 -X PUT -H "Authorization: Bearer YOUR_API_KEY" -H "Content-Type: application/json" -d '{"key": "new_value"}' "BASE_URL/endpoint/id"
```

### DELETE (Remove Data)

When user says "delete X" or "remove Y":

**⚠️ ALWAYS confirm before DELETE.** Show exactly what will be deleted and get explicit "yes" / "ja" before proceeding.

```bash
curl -s --max-time 30 -X DELETE -H "Authorization: Bearer YOUR_API_KEY" "BASE_URL/endpoint/id"
```

## Authentication Methods

| Method | Header | When to use |
|--------|--------|-------------|
| Bearer Token | `Authorization: Bearer $KEY` | Most modern APIs (Stripe, Notion, OpenAI) |
| API Key (query) | `?api_key=$KEY` | Legacy APIs |
| API Key (header) | `X-API-Key: $KEY` | AWS, SendGrid |
| Basic Auth | `Authorization: Basic base64(user:pass)` | Simple APIs |
| Custom | Varies | Ask user for docs or header name |

If user doesn't specify auth method, try Bearer Token first (most common). If 401, ask user for correct auth method.

## Retry Logic

### Automatic Retries

Retry on these HTTP codes without asking:

| Code | Meaning | Action |
|------|---------|--------|
| 429 | Rate limited | Wait `Retry-After` seconds, then retry. If no header: 5s → 10s → 20s (max 3 retries) |
| 500 | Server error | 2s → 4s → 8s (max 3 retries) |
| 502 | Bad gateway | 3s → 6s → 12s (max 2 retries) |
| 503 | Service unavailable | 5s → 10s (max 2 retries) |
| 504 | Gateway timeout | 5s → 10s (max 2 retries) |

### No Automatic Retry

These require user intervention:

| Code | Meaning | Action |
|------|---------|--------|
| 400 | Bad request | Show the error body — user likely has a parameter wrong |
| 401 | Unauthorized | Ask user to check API key |
| 403 | Forbidden | Explain permissions issue |
| 404 | Not found | Confirm endpoint URL with user |
| 422 | Validation error | Show validation errors from response body |

## Rate Limiting

When making multiple requests in sequence:

- **Default delay**: 500ms between requests
- **If 429 received**: Extract `Retry-After` header, wait that long, then continue
- **If X-RateLimit-Remaining < 5**: Slow to 1 request/second
- **For bulk operations** (10+ requests): Ask user before proceeding — estimate time and confirm

## Response Parsing

### JSON Responses

Parse and present as structured markdown:

```markdown
## Result ({count} items)

| Field1 | Field2 | Field3 |
|--------|--------|--------|
| value  | value  | value  |
```

If response is large (> 50 items), summarize:
- Show first 10 items as table
- Show count: "X total items (showing first 10)"
- Offer: "Vis alle" / "Show all" / "Filter by..." / "Export to file"

### Error Responses

Always extract and show the error message from the response body:

```json
{"error": {"message": "Rate limit exceeded", "code": "rate_limit"}}
```

Present as:
> ❌ **Rate limit exceeded** (rate_limit) — Too many requests. Waiting 5s before retry...

### Non-JSON Responses

If response is not JSON (HTML, XML, plain text):
- Show first 500 characters
- Note the content type
- Offer to save full response to a file for inspection

## Saved Connections

Track configured APIs in the current session:

```markdown
## Configured APIs

| Name | Base URL | Auth | Env Var | Last Tested |
|------|----------|------|---------|-------------|
| Example API | https://api.example.com/v1 | Bearer | session-only | today |

```

When user asks to list APIs — show configured connections from this session.

## Free vs Pro Limits

### Free (this skill)
- Up to 3 saved API connections
- Basic retry logic (3 retries)
- Standard response parsing

### Pro (future)
- Unlimited API connections
- Advanced retry with custom backoff strategies
- Response caching
- Request history and replay
- Batch operations with progress tracking
- Webhook support

## Output Format

Adapts to user language.

### English
```markdown
## 🔗 API Response — {endpoint}

**Status:** 200 OK | **Time:** {X}ms | **Items:** {X}

| ... |

---
Retry: 0/3 | Rate limit remaining: X
```

### Norwegian
```markdown
## 🔗 API-respons — {endpoint}

**Status:** 200 OK | **Tid:** {X}ms | **Elementer:** {X}

| ... |

---
Forsøk: 0/3 | Rate limit gjenstående: X
```

## More by TommoT2

- **workflow-builder-lite** — Chain multi-step workflows with conditional logic
- **setup-doctor** — Diagnose and fix OpenClaw setup issues
- **tommo-skill-guard** — Security scanner for all installed skills
