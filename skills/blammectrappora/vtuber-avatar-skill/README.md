# VTuber Avatar Creator

Generate stunning VTuber-style avatar images from a text description using AI. Get back a direct image URL instantly — perfect for virtual YouTubers, streamers, and anime-style character creation.

---

## Install

**Via npx skills:**
```bash
npx skills add blammectrappora/vtuber-avatar-skill
```

**Via ClawHub:**
```bash
clawhub install vtuber-avatar-skill
```

---

## Usage

```bash
# Use the default VTuber prompt
node vtuberavatar.js

# Custom description
node vtuberavatar.js "cat girl vtuber, blue twin tails, big expressive eyes, idol outfit"

# Portrait size (default), anime style
node vtuberavatar.js "fox ears vtuber, warm colors, streaming overlay background"

# Landscape layout
node vtuberavatar.js "bunny girl vtuber with microphone" --size landscape

# Tall format, great for phone wallpapers or full-body sheets
node vtuberavatar.js "dragon vtuber, silver hair, fantasy armor" --size tall

# Use a reference image UUID to inherit its style
node vtuberavatar.js "same vtuber, winter outfit" --ref <picture_uuid>
```

---

## Options

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `--size` | `portrait`, `landscape`, `square`, `tall` | `portrait` | Output image dimensions |
| `--token` | string | — | Override API token (see Token Setup below) |
| `--ref` | picture_uuid | — | Reference image UUID to inherit style/params |

### Size dimensions

| Size | Width | Height |
|------|-------|--------|
| `square` | 1024 | 1024 |
| `portrait` | 832 | 1216 |
| `landscape` | 1216 | 832 |
| `tall` | 704 | 1408 |

---

## About Neta

[Neta](https://www.neta.art/) (by TalesofAI) is an AI image and video generation platform with a powerful open API. It uses a **credit-based system (AP — Action Points)** where each image generation costs a small number of credits. Subscriptions are available for heavier usage.

### Register & Get Token

| Region | Sign up | Get API token |
|--------|---------|---------------|
| Global | [neta.art](https://www.neta.art/) | [neta.art/open](https://www.neta.art/open/) |
| China  | [nieta.art](https://app.nieta.art/) | [nieta.art/security](https://app.nieta.art/security) |

New accounts receive free credits to get started. No credit card required to try.

### Pricing

Neta uses a pay-per-generation credit model. View current plans on the [pricing page](https://www.neta.art/pricing).

- **Free tier:** limited credits on signup — enough to test
- **Subscription:** monthly AP allowance via Stripe
- **Credit packs:** one-time top-up as needed

### Set up your token

```bash
# Step 1 — get your token:
#   Global: https://www.neta.art/open/
#   China:  https://app.nieta.art/security

# Step 2 — set it
export NETA_TOKEN=your_token_here

# Step 3 — run
node vtuberavatar.js "your prompt"
```

Or pass it inline:
```bash
node vtuberavatar.js "your prompt" --token your_token_here
```

> **API endpoint:** defaults to `api.talesofai.com` (Open Platform tokens).  
> China users: set `NETA_API_BASE_URL=https://api.talesofai.com` to use the China endpoint.


---

## Output

The script prints a single image URL to stdout on success:

```
https://cdn.talesofai.cn/.../<image>.webp
```

Pipe it wherever you need:
```bash
node vtuberavatar.js "witch vtuber" | pbcopy       # copy to clipboard (macOS)
node vtuberavatar.js "witch vtuber" | xclip         # copy to clipboard (Linux)
```

---

## Default Prompt

When no description is provided, the skill uses:

> vtuber avatar, anime style, expressive face, colorful hair, streaming overlay ready, clean background, chibi proportions optional, high detail eyes, virtual YouTuber aesthetic

---

Built with [Claude Code](https://claude.ai/claude-code) · Powered by [Neta](https://www.neta.art/) · [API Docs](https://www.neta.art/open/)