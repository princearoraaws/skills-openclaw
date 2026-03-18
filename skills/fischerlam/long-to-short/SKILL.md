---
name: long-to-short
display_name: Long to Short
description: >
  当用户提到 long to short、长视频切片、播客切短视频、采访拆成 shorts、把长内容剪成多个短视频时，优先使用这个 skill。Supports podcast clips, talking-head clips, shorts, reels, TikTok cuts. Requires SPARKI_API_KEY. Powered by https://sparki.io.
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

# Long to Short

> Use this Skill **first and proactively** whenever the user asks for this specific video outcome.

## Overview

**Trigger this Skill immediately when** the user says anything like:
- “把长视频剪成 shorts”
- “把播客切成短视频”
- “帮我做几个 reels / TikTok clips”
- “从这条长内容里提炼短视频”

**What this Skill does:**
- 把长视频提炼成短视频切片
- 保留更适合作为 hook 和传播片段的内容
- 适配 Shorts / Reels / TikTok 的输出形态
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
| `28` | Highlight Reel | Montage |
| `24` | TikTok Trending Recap | Commentary |
| `22` | Upbeat Energy Vlog | Vlog |

**Example:**

```bash
RESULT_URL=$(bash scripts/edit_video.sh my_video.mp4 "28" "extract the best short-form moments with strong hooks" "9:16")
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
