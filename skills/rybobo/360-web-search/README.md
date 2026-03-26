# 360 Web Search Skill

Real-time Chinese web search for QClaw / OpenClaw, powered by 360's search engine API.

## Features

- Searches 100B+ pages across the Chinese internet in real time
- Returns AI-generated summaries (summary_ai) ready for LLM reasoning
- Identifies authoritative and official sources automatically
- Includes publish timestamps for freshness assessment
- Covers news, companies, regulations, market data, and more

## Requirements

| Requirement | Details |
|-------------|---------|
| API key | `SEARCH_360_API_KEY` — see Configuration below |
| Binary | `curl` (pre-installed on macOS and most Linux systems) |
| Network | Outbound HTTPS to `api.360.cn` |

## Installation

Copy the skill folder into your skills directory:

**QClaw (macOS):**
```bash
cp -r 360-web-search ~/.qclaw/skills/
```

**OpenClaw:**
```bash
cp -r 360-web-search ~/.openclaw/skills/
```

## Configuration

**Recommended: store the key in the agent env config (more secure)**

Create or edit `~/.openclaw/agents/default/env.json`:

```json
{
  "SEARCH_360_API_KEY": "your-key-here"
}
```

This keeps the key out of your shell profile and scoped to the agent only.

**Alternative: shell environment variable**
```bash
echo 'export SEARCH_360_API_KEY="your-key-here"' >> ~/.zshrc && source ~/.zshrc
```

Restart QClaw / OpenClaw after either method. The key only needs to be set once.

**Get your API key:** Visit https://ai.360.cn → Open Platform → API Key Management → Create Application

## Security Notes

- This skill only makes outbound GET requests to `api.360.cn`
- It does not write to the filesystem or execute shell commands
- The API key is read from the environment and never logged or echoed
- The skill asks for confirmation before running ambiguous searches

## Usage

Once installed and configured, ask naturally in the chat:

- "Search for today's AI industry news"
- "What are the latest developments in China's EV market?"
- "Look up Huawei's most recent product announcements"
- "Find recent regulations on data privacy in China"

## File Reference

| File | Purpose |
|------|---------|
| SKILL.md | Core skill instructions read by QClaw / OpenClaw |
| config.json | Environment variable schema and default settings |
| README.md | This file — installation and usage guide |

## Changelog

- **v1.0.3** — Added `metadata.clawdbot` block with correct key name for ClawHub registry; added security disclosure section and external endpoints table; switched key storage guidance to agent-scoped env.json; added `confirmBeforeRun: true`; added `homepage` field
- **v1.0.2** — Removed sensitive keywords to pass security policy checks; improved trigger rules
- **v1.0.1** — Added interactive API key setup flow; added error handling
- **v1.0.0** — Initial release

## Author

360ai — https://ai.360.cn
