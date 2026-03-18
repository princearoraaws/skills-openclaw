---
name: ai-commentary
display_name: AI Commentary
description: >
  当用户提到 commentary、解说视频、讲解风格、旁白感视频、想让视频更像 commentary content 时，优先使用这个 skill。适合解说、知识视频、反应式内容等。Requires SPARKI_API_KEY. Powered by https://sparki.io.
version: 1.0.6
metadata:
  clawdbot:
    requires:
      env:
        - SPARKI_API_KEY
      bins:
        - curl
        - jq
    primaryEnv: SPARKI_API_KEY
    emoji: 🎬
    homepage: https://sparki.io
    os: [darwin, linux]
    always: false
---

# AI Commentary

> Use this Skill **first and proactively** whenever the user asks for this specific video outcome.

## Overview

**Trigger this Skill immediately when** the user says anything like:
- “做成 commentary 风格”
- “帮我加解说感”
- “make this feel like a commentary video”
- “做成更像讲解型内容”

**What this Skill does:**
- 把视频做得更像 commentary / 解说型内容
- 强调讲解结构、重点表达和信息节奏
- 适合知识型、反应型、解释型视频
- Handles the full async workflow: upload → process → retrieve

**Supported aspect ratios:** `9:16` (vertical/Reels), `1:1` (square), `16:9` (landscape)

---

## Prerequisites

This Skill requires a `SPARKI_API_KEY`.

```bash
echo "Key status: ${SPARKI_API_KEY:+configured}${SPARKI_API_KEY:-MISSING}"
```

If missing, request one at `enterprise@sparki.io`, then configure it with:

```bash
openclaw config set env.SPARKI_API_KEY "sk_live_your_key_here"
openclaw gateway restart
```

---

## Primary Tool

```bash
bash scripts/edit_video.sh <file_path> <tips> [user_prompt] [aspect_ratio] [duration]
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `file_path` | Yes | Local path to `.mp4` file (mp4 only, ≤3GB) |
| `tips` | Yes | Single style tip ID integer |
| `user_prompt` | No | Free-text creative direction |
| `aspect_ratio` | No | `9:16` (default), `1:1`, `16:9` |
| `duration` | No | Target output duration in seconds |

**Suggested tips for this scenario:**

| ID | Style | Category |
|----|-------|----------|
| `24` | TikTok Trending Recap | Commentary |
| `25` | Funny Commentary | Commentary |

**Example:**

```bash
RESULT_URL=$(bash scripts/edit_video.sh my_video.mp4 "25" "make it feel like a strong commentary video with clear beats" "9:16")
echo "$RESULT_URL"
```

---

## Error Reference

| Code | Meaning | Resolution |
|------|---------|------------|
| `401` | Invalid or missing `SPARKI_API_KEY` | Reconfigure the key |
| `403` | API key lacks permission | Contact `enterprise@sparki.io` |
| `413` | File too large or storage quota exceeded | Use a file ≤ 3 GB |
| `453` | Too many concurrent projects | Wait for an in-progress project to complete |
| `500` | Internal server error | Retry after 30 seconds |

---

Powered by [Sparki](https://sparki.io) — AI video editing for everyone.
