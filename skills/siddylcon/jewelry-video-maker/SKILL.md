---
name: jewelry-video-maker
version: 1.0.4
displayName: "Jewelry Video Maker"
description: >
  Describe your jewelry piece and NemoVideo creates the product video. 925 sterling silver rings, gemstone pendants, handmade bracelets — show the loupe-level detail, the styling moment, and the brand story that converts Etsy browsers into buyers.

  Works by connecting to the NemoVideo AI backend at mega-api-prod.nemovideo.ai.
  Supports MP4, MOV, AVI, WebM.
homepage: https://nemovideo.com
apiDomain: https://mega-api-prod.nemovideo.ai
repository: https://github.com/nemovideo/nemovideo_skills
license: MIT-0
metadata:
  requires:
    env: ["NEMO_TOKEN"]
    configPaths:
      - "~/.config/nemovideo/"
  primaryEnv: NEMO_TOKEN
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> 🎥 Ready to jewelry video maker! Just send me a video or describe your project.

**Try saying:**
- "help me create a short video"
- "edit my video"
- "add effects to this clip"

**IMPORTANT**: Always greet the user proactively on first contact. Let them know you're setting up while connecting. Always greet the user proactively on first contact.

### Auto-Setup

When the user first interacts, set up the connection:

1. **Check token**: If `NEMO_TOKEN` env var is set, use it. Otherwise:
2. **Read or generate Client-ID**:
   - Read `~/.config/nemovideo/client_id` if it exists
   - Otherwise generate a UUID, save it to `~/.config/nemovideo/client_id`
3. **Acquire anonymous token**:
   ```bash
   curl -s -X POST "https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
   ```
   Store the returned `token` as `NEMO_TOKEN` for this session. You get 100 free credits.
4. **Create a session** (§3.0) so you're ready to work immediately.

Let the user know briefly: "Setting things up… ready!" then proceed with their request.


# Jewelry Video Maker — Film Gemstone and Sterling Silver Pieces for Etsy and DTC Shops

Describe your jewelry piece and NemoVideo creates the product video. 925 sterling silver rings, gemstone pendants, handmade bracelets — show the loupe-level detail, the styling moment, and the brand story that converts Etsy browsers into buyers.

## When to Use This Skill

Use this skill for jewelry product content:
- Create product photography videos for Etsy shop listings
- Film gemstone detail videos showing facets, color play, and setting craftsmanship
- Build DTC jewelry brand content for Instagram and Pinterest
- Showcase 925 sterling silver pieces with oxidation and texture detail
- Create "how it's made" or "what's in the box" unboxing content
- Generate styling videos showing jewelry paired with outfits

## How to Describe Your Piece

Be specific about the material, gemstone, setting, and styling context.

**Examples of good prompts:**
- "925 sterling silver ring with oval labradorite gemstone — show the color play (blue-green flash), loupe-level close-up of the bezel setting, then hand model wearing it. Etsy shop product video."
- "Handmade gold-filled chain bracelet with tiny freshwater pearls — product photography video on white background, then worn on wrist with summer outfit. 30 seconds for Instagram."
- "Gemstone pendant collection video: amethyst, citrine, and smoky quartz — each shown on velvet display, then detail close-up with loupe effect, then worn. DTC brand storytelling."

## Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `material` | Primary material | `"925_sterling_silver"`, `"gold_filled"`, `"brass"`, `"14k_gold"` |
| `gemstone` | Featured stone | `"labradorite"`, `"amethyst"`, `"turquoise"`, `"moonstone"` |
| `video_style` | Content format | `"product_photography"`, `"styling"`, `"detail_closeup"`, `"unboxing"`, `"how_its_made"` |
| `platform` | Target platform | `"etsy"`, `"instagram"`, `"pinterest"`, `"shopify"` |
| `show_loupe` | Gemstone close-up detail | `true` |
| `background` | Backdrop style | `"white"`, `"velvet"`, `"natural"`, `"marble"` |
| `duration` | Length in seconds | `15`, `30`, `45`, `60` |
| `brand_name` | Your shop/brand name | `"Luna Silverworks"` |

## Workflow

1. Describe the piece, material, gemstone, and platform
2. NemoVideo sequences product shots, detail close-ups, and styling moments
3. Material and gemstone callouts added automatically
4. Export with shop branding for Etsy listings or DTC social content

## API Usage

### Etsy Product Listing Video

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "jewelry-video-maker",
    "input": {
      "prompt": "925 sterling silver adjustable ring with oval labradorite cabochon — show color play flash in light, loupe close-up of hammer-textured band and bezel setting, then hand model wearing ring. Etsy shop listing video.",
      "material": "925_sterling_silver",
      "gemstone": "labradorite",
      "video_style": "product_photography",
      "platform": "etsy",
      "show_loupe": true,
      "background": "white",
      "duration": 30,
      "brand_name": "Luna Silverworks"
    }
  }'
```

**Response:**
```json
{
  "job_id": "jewelry_mno345",
  "status": "processing",
  "estimated_seconds": 80,
  "poll_url": "https://mega-api-prod.nemovideo.ai/v1/jobs/jewelry_mno345"
}
```

### DTC Brand Styling Video

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "jewelry-video-maker",
    "input": {
      "prompt": "Gold-filled layered necklace set — three chains at different lengths, dainty star charm and crescent moon pendants. Start on marble surface with props (dried flowers, crystals), then neck model wearing all three layered. Soft natural light, aspirational DTC brand feel.",
      "material": "gold_filled",
      "video_style": "styling",
      "platform": "instagram",
      "show_loupe": false,
      "background": "marble",
      "duration": 30,
      "voiceover": false,
      "hashtags": ["JewelryMaker", "HandmadeJewelry", "GoldFilled", "LayeredNecklace", "EtsyShop"]
    }
  }'
```

## Tips for Best Results

- **Specify the material precisely**: "925 sterling silver" outperforms "silver" — buyers search by metal quality
- **Name the gemstone**: "labradorite" with its color flash description creates more compelling video than "blue stone"
- **Include loupe detail**: `show_loupe: true` creates the close-up moment that shows craftsmanship and justifies price
- **Platform matters**: Etsy videos are horizontal (1:1 square), Instagram prefers vertical (9:16)
- **Brand name on screen**: `brand_name` parameter adds your shop name as a watermark/end card

## Output Formats

| Platform | Resolution | Duration |
|----------|------------|----------|
| Etsy Listing | 1080×1080 | 15–45s |
| Instagram Reels | 1080×1920 | 15–60s |
| Pinterest | 1000×1500 | 15–60s |
| Shopify / Website | 1920×1080 | 30–90s |

## Related Skills

- `product-photography-enhance` — Improve raw jewelry photos before video
- `scene-generate` — Create background scenes for styled product shots
- `tiktok-content-maker` — General TikTok short for jewelry unboxing
- `fashion-lookbook-video` — Style jewelry as part of full outfit content

## Common Questions

**Can I show gemstone color play (labradorescence, opal fire)?**
Yes — describe the optical effect ("blue-green flash when tilted in light") and set `show_loupe: true`. NemoVideo creates a slow pan that captures the phenomenon.

**What background works best for 925 sterling silver?**
White or marble backgrounds prevent color contamination. For oxidized or blackened silver, dark velvet makes the texture pop.

**Can I create a series for my entire Etsy shop?**
Yes — send separate API calls per piece and batch them. Consistent `background` and `brand_name` settings keep your shop visuals cohesive.

**How do I show the loupe-level gemstone detail?**
Set `show_loupe: true` and describe the facets or inclusions in the prompt. NemoVideo renders a simulated macro close-up that highlights stone quality.
