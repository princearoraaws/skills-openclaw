---
name: doc-analysis
description: "Doc Analysis - analyze the structure and content of Word (.doc/.docx) documents using MinerU. Returns structured Markdown with headings, paragraphs, and layout preserved."
homepage: https://mineru.net
metadata: {"openclaw": {"emoji": "📄", "requires": {"bins": ["mineru-open-api"], "env": ["MINERU_TOKEN"]}, "primaryEnv": "MINERU_TOKEN", "install": [{"id": "npm", "kind": "node", "package": "mineru-open-api", "bins": ["mineru-open-api"], "label": "Install via npm"}, {"id": "go", "kind": "go", "package": "github.com/opendatalab/MinerU-Ecosystem/cli/mineru-open-api", "bins": ["mineru-open-api"], "label": "Install via go install", "os": ["darwin", "linux"]}]}}
---

# Doc Analysis

Analyze and extract structured content from Word (.doc/.docx) files using MinerU. Returns Markdown with layout, headings, and structure preserved.

## Install

```bash
npm install -g mineru-open-api
# or via Go (macOS/Linux):
go install github.com/opendatalab/MinerU-Ecosystem/cli/mineru-open-api@latest
```

## Quick Start

```bash
# Analyze a .docx file (requires token)
mineru-open-api extract report.docx -o ./out/

# Analyze a .doc file (requires token)
mineru-open-api extract report.doc -o ./out/

# Specify language
mineru-open-api extract report.docx --language en -o ./out/
```

## Authentication

Token required:

```bash
mineru-open-api auth             # Interactive token setup
export MINERU_TOKEN="your-token" # Or via environment variable
```

Create token at: https://mineru.net/apiManage/token

## Capabilities

- Supported input: .doc, .docx (local file or URL)
- Preserves document structure: headings, paragraphs, lists, tables
- Requires token (`mineru-open-api auth` or `MINERU_TOKEN` env)
- Language hint with `--language` (default: `ch`, use `en` for English)

## Notes

- `.doc` (legacy Word format) is only supported by `extract` (requires token)
- `.docx` supports both `flash-extract` (no token, quick) and `extract` (full features)
- Output goes to stdout by default; use `-o <dir>` to save to a file or directory
- All progress/status messages go to stderr; document content goes to stdout
- MinerU is open-source by OpenDataLab (Shanghai AI Lab): https://github.com/opendatalab/MinerU
