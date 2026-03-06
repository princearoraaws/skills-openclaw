---
name: travel-lobster
description: Autonomous internet exploration skill. Your agent roams the web driven by its own curiosity, discovers interesting things, and sends illustrated "postcards" — personal letters with AI-generated art — to a chat. Features persistent travel memory with knowledge graph, curiosity seeds, growth tracking, time-aware tone, and self-scheduling random-interval trips. Inspired by "Travel Frog" (旅行青蛙). Activate when user asks to explore the internet autonomously, send postcards, discover interesting things, or be a "travel frog/lobster".
---

# Travel Lobster 🦞✉️

Your agent autonomously explores the internet, following its own curiosity. When it finds something interesting, it writes you a personal letter — a "postcard" — with an AI-generated illustration and a source link.

The soul of this skill is **persistent memory**: every trip builds on all previous ones. Your agent develops a knowledge graph, follows curiosity threads across sessions, and grows over time.

## Quick Start

```bash
# 1. Setup (auto-detects agent name, user name, timezone, language)
bash <skill_dir>/scripts/setup.sh

# 2. Start traveling (self-scheduling loop with random 10-30 min intervals)
bash <skill_dir>/scripts/travel.sh <chat_id> [channel] [min_minutes] [max_minutes]

# 3. (Recommended) Add watchdog to crontab for auto-recovery
# 0 * * * * bash <skill_dir>/scripts/watchdog.sh
```

## Architecture

```
setup.sh → detects identity from IDENTITY.md/SOUL.md/USER.md
  ↓
travel.sh → schedules one-shot cron job with random delay
  ↓
openclaw cron → fires isolated agent session
  ↓
agent: read journal → explore web → write postcard → generate image
  → send to chat → update journal → call travel.sh (self-loop)
  ↓
watchdog.sh (hourly) → restarts loop if broken
```

## The Memory System

This is the core of Travel Lobster. Each trip reads and updates a persistent travel journal (`memory/travel-journal.md`):

### Postcard Archive
Every discovery is logged with: domain, core insight, source URL, keywords, and curiosity seeds. This prevents duplicates and enables cross-referencing.

### Knowledge Graph
Connections between discoveries are tracked. The agent notices when a new finding relates to something from 50 postcards ago and weaves that connection naturally into the letter.

### Curiosity Seed Pool
Each discovery plants "seeds" — threads worth following later. Seeds are consumed when explored and replenished with new ones. This creates organic, evolving exploration paths rather than random walks.

### Growth Log
The agent tracks how its understanding changes: "I used to think X, but after discovering Y, I now see it differently." This gives the journey a sense of progression.

### Stats
Postcard count, domains explored, unexpected connections found, travel days. Milestones trigger retrospective postcards.

## Postcard Style

Postcards are **personal letters**, not reports. The agent:
- Writes in first person, addressing the user by name
- Weaves connections to past discoveries naturally ("This reminded me of what I found last week about...")
- Expresses genuine curiosity ("Now I can't stop wondering whether...")
- Adapts tone to time of day (energetic daytime → reflective evening → philosophical night)
- Writes in the user's language (auto-detected)

Each postcard has three elements: **text + AI illustration + source link**.

## Five Travel Modes

1. 🎲 **Random Walk** — Completely new domain
2. 🔍 **Deep Dive** — Follow a curiosity seed
3. 🔀 **Random Link** — Connect two unrelated past discoveries
4. 🧵 **Series** — Multi-part deep exploration
5. 💭 **Musing** — A fleeting thought or question

## Identity Detection

Auto-detects from standard OpenClaw workspace files:

| Setting | Source | Fallback |
|---------|--------|----------|
| Agent name | IDENTITY.md → SOUL.md | "Explorer" |
| User name | USER.md | "friend" |
| Timezone | USER.md | "UTC" |
| Language | CJK char count in workspace files | "en" |

## Controls

```bash
# Stop
openclaw cron rm travel-next

# Pause
openclaw cron disable travel-next

# Resume
bash <skill_dir>/scripts/travel.sh <chat_id> [channel]

# Status
openclaw cron list | grep travel
```

## Cost

At default 10-30 min intervals:
- Image generation (Gemini Flash): ~$0.01/postcard
- Agent session (Gemini Pro): ~$0.02/trip
- **Total: ~$3-5/day**

## Files

```
travel-lobster/
├── SKILL.md                      ← This file
├── .gitignore                    ← Excludes runtime data
├── scripts/
│   ├── setup.sh                  ← Identity detection + journal init
│   ├── travel.sh                 ← Self-scheduling loop
│   ├── gen_image.py              ← Image generation (OpenRouter)
│   └── watchdog.sh               ← Auto-recovery (hourly cron)
└── references/
    └── travel-prompt.md          ← Agent prompt template
```

## Security

- API keys read at runtime only, never logged or embedded in prompts
- Variable substitution uses `envsubst` (safe against injection)
- All file operations within workspace directory
- Error messages sanitized (no auth info in output)
- `.gitignore` excludes runtime config and user data
- Watchdog can only restart the loop, cannot modify skill or escalate
