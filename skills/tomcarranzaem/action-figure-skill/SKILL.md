---
name: action-figure-skill
description: Generate action figure images using the Neta AI API. Returns a direct image URL.
tools: Bash
---

# AI Action Figure Generator

Generate stunning ai action figure generator toy packaging images from a text description. Get back a direct image URL instantly.

## When to use
Use when someone asks to generate or create ai action figure generator toy packaging images.

## Quick start
```bash
node actionfigure.js "your description here"
```

## Options
- `--size` — `portrait`, `landscape`, `square`, `tall` (default: `portrait`)


## Token

Requires a Neta API token via `NETA_TOKEN` env var or `--token` flag.
- Global: <https://www.neta.art/open/>
- China:  <https://app.nieta.art/security>

```bash
export NETA_TOKEN=your_token_here
```

## Install
```bash
npx skills add TomCarranzaem/action-figure-skill
```
