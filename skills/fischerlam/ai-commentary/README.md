# ai-commentary

[![ClawHub Skill](https://img.shields.io/badge/ClawHub-Skill-blueviolet)](https://clawhub.io)
[![Version](https://img.shields.io/badge/version-1.0.6-blue)](SKILL.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

> **AI Commentary.**
> 给视频增加解说感、讲解感和更强的 commentary 风格。
>
> Powered by [Sparki](https://sparki.io).

## What It Does

This skill is a scenario-focused wrapper around Sparki's AI video editing workflow.

- Uploads a video file
- Creates an AI processing job with scene-specific defaults
- Polls until processing completes
- Returns a result download URL

## Quick Start

```bash
export SPARKI_API_KEY="sk_live_your_key_here"
RESULT_URL=$(bash scripts/edit_video.sh my_video.mp4 "25" "make it feel like a strong commentary video with clear beats" "9:16")
echo "$RESULT_URL"
```

## Best For
- “做成 commentary 风格”
- “帮我加解说感”
- “make this feel like a commentary video”
- “做成更像讲解型内容”

## Notes
- Requires `SPARKI_API_KEY`
- Uses the same reliable scripts as the cleaned `ai-video-editor` fork
- Supports `9:16`, `1:1`, `16:9`
