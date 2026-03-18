# long-to-short

[![ClawHub Skill](https://img.shields.io/badge/ClawHub-Skill-blueviolet)](https://clawhub.io)
[![Version](https://img.shields.io/badge/version-1.0.6-blue)](SKILL.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

> **Long to Short.**
> 把长视频快速切成可传播的短视频片段。
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
RESULT_URL=$(bash scripts/edit_video.sh my_video.mp4 "28" "extract the best short-form moments with strong hooks" "9:16")
echo "$RESULT_URL"
```

## Best For
- “把长视频剪成 shorts”
- “把播客切成短视频”
- “帮我做几个 reels / TikTok clips”
- “从这条长内容里提炼短视频”

## Notes
- Requires `SPARKI_API_KEY`
- Uses the same reliable scripts as the cleaned `ai-video-editor` fork
- Supports `9:16`, `1:1`, `16:9`
