# ai-video-editor

Render-mode Sparkii Business API skill.

## Base URLs

- API base URL: `https://business-agent-api.sparki.io`

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/setup.sh` | Create local config and validate API key |
| `scripts/health.sh` | Check prerequisites and Business API reachability |
| `scripts/edit_video.sh` | Upload MP4, create render project, poll with exponential backoff, download final MP4 |

## Main Workflow

```bash
bash scripts/edit_video.sh <video_path> <tips> [user_prompt] [aspect_ratio] [duration]
```

Examples:

```bash
bash scripts/edit_video.sh ./demo.mp4 22 "Create an energetic travel montage" 9:16 60
bash scripts/edit_video.sh ./demo.mp4 "" "Create a cinematic travel video with slow motion and dramatic pacing" 16:9 45
```

## API Contract Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/business/assets/upload` | POST | Upload file with `files` |
| `/api/v1/business/assets/batch` | POST | Get asset status |
| `/api/v1/business/projects/render` | POST | Create render project |
| `/api/v1/business/projects/batch` | POST | Get render result |

This skill follows the Business API markdown contract rather than the current backend branch implementation.

## Polling Behavior

- Asset status polling uses exponential backoff starting at `ASSET_POLL_INTERVAL` (default `2`s), capped by `ASSET_POLL_MAX_INTERVAL` (default `30`s).
- Render status polling uses exponential backoff starting at `PROJECT_POLL_INTERVAL` (default `10`s), capped by `PROJECT_POLL_MAX_INTERVAL` (default `60`s).
- Timeouts remain controlled by `ASSET_TIMEOUT` and `PROJECT_TIMEOUT`.
