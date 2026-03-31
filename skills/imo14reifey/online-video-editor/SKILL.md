---
name: online-video-editor
version: "1.0.0"
displayName: "Online Video Editor — Edit Videos Online Free with AI No Download Required"
description: >
  Edit videos online with AI — trim, cut, merge, add captions, background music, transitions, color correction, text overlays, speed adjustments, and multi-format export directly through chat. NemoVideo is the online video editor that requires no software download, no account setup, and no timeline learning curve. Describe your edit and the AI executes it: professional results from conversational instructions. Works on any device with an internet connection. Online video editor free, edit video online no download, AI video editor online, free video editing tool, browser video editor, cloud video editor, edit videos without software.
metadata: {"openclaw": {"emoji": "🌐", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Online Video Editor — Professional Editing Without Installing Anything

Desktop video editing software requires: downloading a multi-gigabyte installer, meeting minimum hardware requirements (most require 8GB+ RAM and a dedicated GPU), learning a complex interface with hundreds of buttons and menus, and keeping the software updated through regular patches. Mobile editing apps require: downloading from an app store, limited functionality compared to desktop, tiny screen for precise editing work, and storage space on an already-full phone. NemoVideo requires: an internet connection. That is it. No download. No installation. No hardware requirements beyond what runs a web browser. No interface to learn because there is no visual interface — you describe the edit in words and the AI executes it. This fundamentally changes who can edit video. A teacher preparing a lesson on a school Chromebook: can edit. A small business owner on a tablet during lunch: can edit. A student on a library computer: can edit. A marketing team collaborating across different operating systems: can edit. A person on a phone with 2GB of free storage: can edit. The constraint that kept video editing locked to expensive hardware and specialized software is gone. The editing power that previously required Premiere Pro or Final Cut is now accessible through a text description.

## Use Cases

1. **Quick Trim — Remove Start and End (any length)** — A meeting recording has 2 minutes of "is everyone here?" at the beginning and 3 minutes of "okay bye" at the end. NemoVideo: trims the first 2 minutes and last 3 minutes, adds a 0.5-second fade-in at the new start and fade-out at the new end, and exports. A 5-second description replaces 10 minutes of importing into editing software and finding the right cut points.
2. **Social Media Repurpose — One Video, Four Formats (any length)** — A creator has a 16:9 YouTube video that needs to be posted on TikTok (9:16), Instagram Feed (4:5), Instagram Reels (9:16 with captions), and LinkedIn (1:1). NemoVideo: intelligently reframes for each aspect ratio (face tracking for vertical crops), adds word-by-word captions for the Reels version, applies platform-specific color optimization, and exports all four formats from one command. Multi-platform publishing from a single source video.
3. **Combine Clips — Merge Multiple Videos (any number)** — A teacher recorded a lesson in 5 separate phone clips because they kept getting interrupted. NemoVideo: merges all 5 clips in sequence, color-matches across clips (phone auto-exposure created different looks), adds crossfade transitions between clips (smooths the interruption gaps), normalizes audio levels, and exports as one continuous video. Five fragments become one cohesive lesson.
4. **Full Edit — Talking-Head Polish (5-25 min)** — A YouTuber records a raw video and describes the complete edit: "Remove silences, add zoom-cuts, put in lo-fi music, add word-by-word captions, and make a Shorts clip from the best 55 seconds." NemoVideo executes the entire pipeline: silence removal (0.8s threshold), zoom-cuts (100%/120% alternating every 10 seconds), color grade (warm-clean), music at -20dB with ducking, captions in trending style, chapter detection, and Shorts extraction. The complete YouTube post-production workflow from one description.
5. **Emergency Edit — Fix Before Deadline (any length)** — A presenter realizes 30 minutes before a meeting that their video has a 10-second section where they said the wrong number ("$5 million" instead of "$50 million"). NemoVideo: cuts the 10-second error segment (specified by timestamp), smooths the audio transition, and re-exports in 2 minutes. Crisis averted without opening editing software.

## How It Works

### Step 1 — Upload Video
Upload from any device: phone, tablet, laptop, desktop. Any format accepted. No software to install first.

### Step 2 — Describe the Edit
Type what you want in plain language. Simple edits: "trim the first 30 seconds." Complex edits: "remove silences, add captions, music, and color correction, then export in three formats." NemoVideo understands both.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "online-video-editor",
    "prompt": "Edit a 15-minute raw talking-head video. Full professional edit: remove silences over 1 second, add zoom-cuts every 10 seconds, apply warm-clean color grade, add lo-fi music at -20dB with speech ducking, generate word-by-word captions (white text, yellow highlight, dark pill background), auto-detect chapters, extract best 55-second Shorts clip (9:16 with captions). Export main video as 16:9 1080p.",
    "edits": ["silence-removal", "zoom-cuts", "color-grade", "music", "captions", "chapters", "shorts"],
    "silence_threshold": 1.0,
    "zoom_cuts_interval": 10,
    "color_grade": "warm-clean",
    "music": "lo-fi",
    "music_volume": "-20dB",
    "captions": {"style": "word-highlight", "text": "#FFFFFF", "highlight": "#FFD700", "bg": "pill-dark"},
    "chapters": true,
    "shorts": {"duration": "55 sec"},
    "format": "16:9"
  }'
```

### Step 4 — Download
Preview the edited video and Shorts clip. Download directly to your device. Upload to any platform.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the edit in plain language |
| `edits` | array | | Specific edits to apply |
| `trim` | object | | {start, end} or {remove: "0:00-0:30"} |
| `merge` | boolean | | Combine multiple uploaded clips |
| `silence_threshold` | float | | Remove silences above N seconds |
| `zoom_cuts_interval` | integer | | Seconds between zoom changes |
| `color_grade` | string | | "warm-clean", "cinematic", "bright", "none" |
| `music` | string | | "lo-fi", "upbeat", "corporate", "none" |
| `music_volume` | string | | "-14dB" to "-22dB" |
| `captions` | object | | {style, text, highlight, bg} |
| `speed` | float | | Playback speed (0.25-4.0) |
| `chapters` | boolean | | Auto-detect chapters |
| `shorts` | object | | {duration} for Shorts extraction |
| `formats` | array | | ["16:9","9:16","1:1","4:5"] |

## Output Example

```json
{
  "job_id": "ove-20260328-001",
  "status": "completed",
  "source_duration": "15:22",
  "edited_duration": "10:48",
  "edits_applied": {
    "silences_removed": "4:34 (112 cuts)",
    "zoom_cuts": 65,
    "color_grade": "warm-clean",
    "music": "lo-fi at -20dB with ducking",
    "captions": "word-highlight (326 lines)"
  },
  "outputs": {
    "main_video": {
      "file": "edited-16x9.mp4",
      "duration": "10:48",
      "resolution": "1920x1080"
    },
    "chapters": [
      {"title": "Introduction", "timestamp": "0:00"},
      {"title": "The Core Problem", "timestamp": "2:15"},
      {"title": "Solution Framework", "timestamp": "5:02"},
      {"title": "Implementation Steps", "timestamp": "7:38"},
      {"title": "Closing Thoughts", "timestamp": "9:45"}
    ],
    "shorts": {
      "file": "shorts-9x16.mp4",
      "duration": "0:55"
    }
  }
}
```

## Tips

1. **Start simple, refine later** — "Make this video look professional" is a valid first instruction. If the result is 90% right but the music is too loud, follow up with "lower the music to -22dB." Iterative editing through conversation is faster than getting every parameter right on the first try.
2. **Multi-format export in one request saves time** — Instead of editing once for YouTube, then again for TikTok, then again for Instagram, request all formats in one generation. The AI handles the reframing, and you get all versions simultaneously.
3. **Silence removal is the highest-impact single edit** — If you only apply one edit to raw footage, make it silence removal. It instantly tightens pacing by 20-35% and makes any video feel more engaging. Everything else is refinement.
4. **Captions are the second-highest-impact edit** — Adding captions increases social media watch time by 12-40%. The combination of silence removal + captions transforms amateur footage into professional content with just two instructions.
5. **No learning curve is the real advantage** — The point of an online editor is not just convenience — it is accessibility. Someone who has never opened Premiere Pro can describe a complex multi-step edit and get professional results. The AI replaces the learning curve entirely.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube / website |
| MP4 9:16 | 1080x1920 | TikTok / Reels / Shorts |
| MP4 1:1 | 1080x1080 | Instagram / LinkedIn |
| MP4 4:5 | 1080x1350 | Instagram feed |
| MOV | 1080p | Professional workflow |
| WebM | 720p+ | Web embed |

## Related Skills

- [gaming-video-editor](/skills/gaming-video-editor) — Gaming video editing
- [video-splitter](/skills/video-splitter) — Video splitting
- [speed-ramp-video](/skills/speed-ramp-video) — Speed ramp effects
