---
name: blur
version: "1.0.0"
description: "Apply image blur effects and privacy masks using Python PIL processing. Use when you need to blur, redact faces, or mask sensitive regions in images."
author: BytesAgain
homepage: https://bytesagain.com
source: https://github.com/bytesagain/ai-skills
tags: [blur, image, privacy, mask, redact, face-detection]
---

# Blur — Image Blur & Privacy Mask Tool

A comprehensive image processing skill for applying blur effects, face detection with automatic masking, region-based redaction, and batch processing. All processing metadata is tracked in JSONL format.

## Prerequisites

- `bash` (v4+)
- `python3` (v3.6+)
- `Pillow` (PIL) — Python image library (install via `pip3 install Pillow`)
- Optional: face detection libraries for the `face` command

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BLUR_INPUT` | Yes* | Input image path |
| `BLUR_OUTPUT` | No | Output image path (default: auto-generated) |
| `BLUR_RADIUS` | No | Blur radius/strength (default: 10) |
| `BLUR_TYPE` | No | Blur type: gaussian, box, motion (default: gaussian) |
| `BLUR_REGION` | No | Region to blur: x,y,width,height |
| `BLUR_DIR` | No | Directory for batch processing |
| `BLUR_ID` | No | Processing record ID for undo/lookup |
| `BLUR_FORMAT` | No | Export format: json, csv (default: json) |

## Data Storage

- Metadata: `~/.blur/data.jsonl`
- Config: `~/.blur/config.json`
- Output directory: `~/.blur/output/`

## Commands

### `apply`
Apply blur effect to an entire image.
```bash
BLUR_INPUT="/path/to/image.jpg" BLUR_RADIUS="15" BLUR_TYPE="gaussian" scripts/script.sh apply
```

### `face`
Detect and blur faces in an image for privacy.
```bash
BLUR_INPUT="/path/to/photo.jpg" BLUR_RADIUS="20" scripts/script.sh face
```

### `region`
Blur a specific rectangular region in an image.
```bash
BLUR_INPUT="/path/to/image.jpg" BLUR_REGION="100,50,200,150" scripts/script.sh region
```

### `batch`
Process multiple images in a directory.
```bash
BLUR_DIR="/path/to/images/" BLUR_RADIUS="10" scripts/script.sh batch
```

### `preview`
Generate a low-resolution preview of the blur effect.
```bash
BLUR_INPUT="/path/to/image.jpg" BLUR_RADIUS="10" scripts/script.sh preview
```

### `undo`
Revert a blur operation using the original backup.
```bash
BLUR_ID="blur_abc123" scripts/script.sh undo
```

### `config`
View or update blur configuration.
```bash
BLUR_KEY="default_radius" BLUR_VALUE="15" scripts/script.sh config
```

### `export`
Export processing history.
```bash
BLUR_FORMAT="json" scripts/script.sh export
```

### `list`
List all processed images.
```bash
scripts/script.sh list
```

### `status`
Show processing statistics.
```bash
scripts/script.sh status
```

### `help`
Display usage information.
```bash
scripts/script.sh help
```

### `version`
Display current version.
```bash
scripts/script.sh version
```

## Output Format

```json
{
  "status": "success",
  "command": "apply",
  "data": {
    "id": "blur_20240101_abc123",
    "input": "/path/to/image.jpg",
    "output": "/path/to/image_blurred.jpg",
    "blur_type": "gaussian",
    "radius": 10
  }
}
```

## Error Handling

| Exit Code | Meaning |
|-----------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Missing required parameter |
| 3 | Image not found |
| 4 | PIL/Pillow not installed |

---

Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
