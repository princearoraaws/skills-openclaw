---
name: browser-session-archive
description: Archive ChatGPT and Claude share links to Markdown using Chrome CDP. Captures browser sessions for offline reading.
metadata: {"openclaw": {"emoji": "📄", "requires": {"bins": ["node", "bun"], "npm": ["ws"]}, "install": [{"id": "ws", "kind": "npm", "label": "Install ws module", "packages": [{"name": "ws", "global": true}]}], "os": ["darwin", "linux"]}}
---

# Browser Session Archive

Extract ChatGPT and Claude share link content to structured Markdown files using Chrome DevTools Protocol.

## Triggers

User message contains:
1. **Keywords**: `提取 chatgpt 文档`, `提取 claude 文档`, `提取文档`, `extract chatgpt`, `extract claude`
2. **Links**:
   - `https://chatgpt.com/share/{share-id}`
   - `https://claude.ai/share/{share-id}`

## Usage

### Quick Start

```bash
# Copy script to PATH
cp ~/.openclaw/skills/ai-share-extractor/scripts/extract.sh /usr/local/bin/
chmod +x /usr/local/bin/extract.sh

# Run
extract.sh "https://chatgpt.com/share/xxx"
extract.sh "https://claude.ai/share/xxx" "~/LookBack/2026-03-26/Claude"
```

### Step by Step

```bash
# 1. Capture HTML
cd ~/.openclaw/skills/ai-share-extractor/scripts
CHROME_DEBUG_PORT=9222 TARGET_URL="https://chatgpt.com/share/xxx" \
  OUTPUT_DIR="~/LookBack/2026-03-26/ChatGPT" \
  node capture-cdp.js

# 2. Convert to Markdown
node convert-markdown.js --metadata "~/LookBack/2026-03-26/ChatGPT/.metadata.json"
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CHROME_DEBUG_PORT` | Chrome debugging port | `9222` |
| `TARGET_URL` | Share link URL | (required) |
| `OUTPUT_DIR` | Output directory | `~/LookBack/{date}/{ChatGPT\|Claude}` |

## Output Structure

```
~/LookBack/{YYYY-MM-DD}/
├── ChatGPT/
│   ├── {timestamp}-{title}.md              # Markdown file
│   ├── {timestamp}-{title}-captured.html   # HTML snapshot
│   └── .metadata.json                       # Metadata
└── Claude/
    └── ...
```

## Prerequisites

1. **Chrome Debug Mode**: Start Chrome with `--remote-debugging-port=9222`
   ```bash
   # macOS
   open -a "Google Chrome" --args --remote-debugging-port=9222
   
   # Linux
   google-chrome --remote-debugging-port=9222
   ```

2. **Install Dependencies**:
   ```bash
   npm install -g ws
   ```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Connection refused | Chrome debug port not open | Start Chrome with `--remote-debugging-port` |
| Timeout | Page loading slow | Increase wait time or refresh manually |
| Target not found | Invalid link | Verify the share link is correct |

## Scripts

| Script | Description |
|--------|-------------|
| `capture-cdp.js` | CDP capture script, extracts HTML |
| `convert-markdown.js` | HTML to Markdown converter |
| `extract.sh` | One-click entry script |

## References

- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [OpenClaw Skills](https://docs.openclaw.ai/tools/skills)