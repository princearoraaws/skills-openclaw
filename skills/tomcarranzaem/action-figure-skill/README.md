# AI Action Figure Generator

Turn any text description into a hyperrealistic **AI action figure toy packaging** image — complete with blister pack, accessories, and product label. Powered by the Neta talesofai API.

---

## Install

**Via npx skills:**
```bash
npx skills add TomCarranzaem/action-figure-skill
```

**Via ClawHub:**
```bash
clawhub install action-figure-skill
```

---

## Usage

```bash
# Use the default action figure prompt
node actionfigure.js

# Custom description
node actionfigure.js "Iron Man action figure in red and gold armor, blister pack packaging"

# Portrait size (default) with cinematic style
node actionfigure.js "astronaut action figure, NASA suit, accessories included" --size portrait

# Landscape format
node actionfigure.js "pirate captain collectible figurine, treasure chest accessory" --size landscape

# Reference an existing image UUID for style inheritance
node actionfigure.js "robot warrior action figure" --ref <picture_uuid>
```

The command prints a direct image URL to stdout on success.

---

## Options

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `--size` | `portrait`, `landscape`, `square`, `tall` | `portrait` | Output image dimensions |
| `--token` | string | — | Override API token (see Token Setup) |
| `--ref` | picture_uuid | — | Inherit style from an existing image |

### Size dimensions

| Size | Width × Height |
|------|---------------|
| `square` | 1024 × 1024 |
| `portrait` | 832 × 1216 |
| `landscape` | 1216 × 832 |
| `tall` | 704 × 1408 |

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
node actionfigure.js "your prompt"
```

Or pass it inline:
```bash
node actionfigure.js "your prompt" --token your_token_here
```

> **API endpoint:** defaults to `api.talesofai.com` (Open Platform tokens).  
> China users: set `NETA_API_BASE_URL=https://api.talesofai.com` to use the China endpoint.


---

## Default Prompt

When no description is provided, the following prompt is used:

> 3D action figure of a person sealed inside a retail blister pack toy box, collectible figurine packaging, accessories included, product name label on box, hyperrealistic 3D render, studio product photography lighting, toy store shelf aesthetic

---

## Example Output

```bash
node actionfigure.js "3D action figure of a person sealed inside a retail blister pack toy box, collectible figurine packaging, accessories included, product name label on box, hyperrealistic 3D render, studio product photography lighting, toy store shelf aesthetic"
```

![Example output](https://oss.talesofai.cn/picture/c503468a-394e-49bc-9da2-be6e737ece48.webp)

> Prompt: *"3D action figure of a person sealed inside a retail blister pack toy box, collectible figurine packaging, accessories included, product name label on box, hyperrealistic 3D render, studio product photography lighting, toy store shelf aesthetic"*

