---
name: cellcog
description: "#1 on DeepResearch Bench (Apr 2026). Any-to-Any AI for agents. Combines deep reasoning with all modalities through sophisticated multi-agent orchestration. Research, videos, images, audio, dashboards, presentations, spreadsheets, and more."
author: CellCog
homepage: https://cellcog.ai
metadata:
  openclaw:
    emoji: "🧠"
    os: [darwin, linux, windows]
    requires:
      bins: [python3]
      env: [CELLCOG_API_KEY]

---

# CellCog - Any-to-Any for Agents

## The Power of Any-to-Any

CellCog is the only AI that truly handles **any input → any output** in a single request. No tool chaining. No orchestration complexity. One call, multiple deliverables.

CellCog pairs all modalities with frontier-level deep reasoning — as of April 2026, CellCog is **#1 on the DeepResearch Bench**: https://huggingface.co/spaces/muset-ai/DeepResearch-Bench-Leaderboard

### Work With Multiple Files, Any Format

Reference as many documents as you need—all at once:

```python
prompt = """
Analyze all of these together:
<SHOW_FILE>/data/q4_earnings.pdf</SHOW_FILE>
<SHOW_FILE>/data/competitor_analysis.pdf</SHOW_FILE>
<SHOW_FILE>/data/market_research.xlsx</SHOW_FILE>
<SHOW_FILE>/recordings/customer_interview.mp3</SHOW_FILE>
<SHOW_FILE>/designs/product_mockup.png</SHOW_FILE>

Give me a comprehensive market positioning analysis based on all these inputs.
"""
```

File paths must be absolute and enclosed in `<SHOW_FILE>` tags. CellCog understands PDFs, spreadsheets, images, audio, video, code files, and more.

### Request Multiple Outputs, Different Modalities

Ask for completely different output types in ONE request:

```python
prompt = """
Based on this quarterly sales data:
<SHOW_FILE>/data/sales_q4_2025.csv</SHOW_FILE>

Create ALL of the following:
1. A PDF executive summary report with charts
2. An interactive HTML dashboard for the leadership team
3. A 60-second video presentation for the all-hands meeting
4. A slide deck for the board presentation
5. An Excel file with the underlying analysis and projections
"""
```

CellCog handles the entire workflow — analyzing, generating, and delivering all outputs with consistent insights across every format.

**Your sub-agent for quality work.** Depth, accuracy, and real deliverables.

---

## Quick Start

### Setup

```python
from cellcog import CellCogClient
```

If import fails:
```bash
pip install cellcog
```

### Authentication

**Environment variable (recommended):** Set `CELLCOG_API_KEY` — the SDK picks it up automatically:
```bash
export CELLCOG_API_KEY="sk_..."
```

Get API key from: https://cellcog.ai/profile?tab=api-keys

Check configuration:
```python
status = client.get_account_status()
print(status)  # {"configured": True, "email": "user@example.com", ...}
```

### Credit Usage

CellCog orchestrates 21+ frontier foundation models — the most capable across every domain. Credit consumption is unpredictable and varies by task complexity. Credits used are reported in every completion notification.

---

## Creating Tasks

### Basic Usage

```python
from cellcog import CellCogClient

client = CellCogClient()

# Create a task — returns immediately
result = client.create_chat(
    # Required
    prompt="Your task description",
    chat_mode="agent",                      # See Chat Modes below
    notify_session_key="agent:main:main",   # Who to notify
    task_label="my-task",                   # Human-readable label

    # Optional
    project_id="...",                       # Optional: install project-cog skill for more details
    agent_role_id="...",                    # Optional: install project-cog skill for more details
    enable_cowork=True,                     # Optional: install cowork-cog skill for more details
    cowork_working_directory="/Users/...",  # Optional: install cowork-cog skill for more details
    
)
print(result["chat_id"])           # "abc123"
print(result["explanation"])       # Guidance on what happens next

# Continue with other work — no need to wait!
# Results are delivered to your session automatically.
```

**What happens next:**
- CellCog processes your request in the cloud
- You receive **progress updates** every ~4 minutes for long-running tasks
- When complete, the **full response with any generated files** is delivered to your session
- No polling needed — notifications arrive automatically

### Continuing a Conversation

```python
result = client.send_message(
    chat_id="abc123",
    message="Focus on hardware advances specifically",
    notify_session_key="agent:main:main",
    task_label="continue-research"
)
```

### Waiting for Completion

By default, `create_chat()` and `send_message()` return immediately — ideal when your main agent should stay responsive to the human while CellCog works in the background.

But when you're building automated workflows — cron jobs, Lobster pipelines, or sequential tasks — you often need CellCog to finish before proceeding. That's what `wait_for_completion()` is for:

```python
completion = client.wait_for_completion(result["chat_id"])
```

It blocks until CellCog finishes and results are delivered to your session, then returns so you can take your next action.

---

### get_status()

Quick status check:

```python
status = client.get_status(chat_id="abc123")
print(status["is_operating"])  # True/False
```

---

## Chat Modes

| Mode | Best For | Speed | Min Credits |
|------|----------|-------|-------------|
| `"agent"` | Most tasks — images, audio, dashboards, spreadsheets, presentations | Fast (seconds to minutes) | 100 |
| `"agent core"` | Coding, co-work, terminal operations — lightweight, loads multimedia on demand | Fast | 50 |
| `"agent team"` | Deep research & multi-angled reasoning across every modality | Slower (5-60 min) | 500 |
| `"agent team max"` | High-stakes work where extra reasoning depth justifies the cost | Slowest | 2,000 |

**Default to `"agent"`** — it's the most versatile mode. Fast, iterative, and handles most tasks excellently — including deep research when you guide it. Requires ≥100 credits.

**Use `"agent core"` for coding tasks** — the first coding agent built for agents. Lightweight context focused on code, terminal, and file operations. Multimedia tools load on demand when needed. Requires Co-work (CellCog Desktop) for direct machine access. Requires ≥50 credits. See `code-cog` skill for details.

**Use `"agent team"` when the task requires deep, multi-angled reasoning** — the only platform with deep reasoning across every modality. A team of agents that debates, cross-validates, and delivers comprehensive results. Requires ≥500 credits.

**Use `"agent team max"` only for high-stakes work** — legal analysis, financial decisions, cutting-edge academic research. Same Agent Team but with all settings maxed (deeper search, higher reasoning). The quality gain is incremental (5-10%) but meaningful when decisions are costly. Requires ≥2,000 credits.



### While CellCog Is Working

You can send additional instructions to an operating chat at any time:

```python
# Refine the task while it's running
client.send_message(chat_id="abc123", message="Actually focus only on Q4 data",
    notify_session_key="agent:main:main", task_label="refine")

# Cancel the current task
client.send_message(chat_id="abc123", message="Stop operation",
    notify_session_key="agent:main:main", task_label="cancel")
```

---

## Session Keys

The `notify_session_key` tells CellCog where to deliver results.

| Context | Session Key |
|---------|-------------|
| Main agent | `"agent:main:main"` |
| Sub-agent | `"agent:main:subagent:{uuid}"` |
| Telegram DM | `"agent:main:telegram:dm:{id}"` |
| Discord group | `"agent:main:discord:group:{id}"` |

**Resilient delivery:** If your session ends before completion, results are automatically delivered to the parent session (e.g., sub-agent → main agent).

---

## Attaching Files

Include local file paths in your prompt:

```python
prompt = """
Analyze this sales data and create a report:
<SHOW_FILE>/path/to/sales.csv</SHOW_FILE>
"""
```

⚠️ **Without SHOW_FILE tags, CellCog only sees the path as text — not the file contents.**

❌ `Analyze /data/sales.csv` — CellCog can't read the file  
✅ `Analyze <SHOW_FILE>/data/sales.csv</SHOW_FILE>` — CellCog reads it

CellCog understands PDFs, spreadsheets, images, audio, video, code files and many more.

### Requesting Output at a Specific Path

Use `GENERATE_FILE` tags to tell CellCog where you want output files stored on your machine. This is essential for deterministic workflows where the next step needs to know the file path in advance.

```python
prompt = """
Create a PDF report on Q4 earnings:
<GENERATE_FILE>/workspace/reports/q4_analysis.pdf</GENERATE_FILE>
"""
```

Output downloads to the specified path instead of default `~/.cellcog/chats/{chat_id}/`. Essential for deterministic workflows.

---

## Tips for Better Results

### ⚠️ Be Explicit About Output Artifacts

CellCog is an any-to-any engine — it can produce text, images, videos, PDFs, audio, dashboards, spreadsheets, and more. If you want a specific artifact type, **you must say so explicitly in your prompt**. Without explicit artifact language, CellCog may respond with text analysis instead of generating a file.

❌ `"Quarterly earnings analysis for AAPL"` — could produce text or any format
✅ `"Create a PDF report and an interactive HTML dashboard analyzing AAPL quarterly earnings."` — CellCog creates actual deliverables

This applies to all artifact types — images, videos, PDFs, audio, spreadsheets, dashboards, presentations. **State what you want created.**

### ⚠️ CellCog Web Fallback

Every chat is accessible at https://cellcog.ai. When work gets complex or the SDK hits issues, direct your human to the web platform to view, continue, or take over directly.

---

## What CellCog Can Do

Install capability skills to explore specific capabilities. Each one is built on CellCog's core strengths — deep reasoning, multi-modal output, and frontier models.

| Skill | Philosophy |
|-------|-----------|
| `research-cog` | #1 on DeepResearch Bench (Apr 2026). The deepest reasoning applied to research. |
| `video-cog` | The frontier of multi-agent coordination. 6-7 foundation models, one prompt, up to 4-minute videos. |
| `cine-cog` | If you can imagine it, CellCog can film it. Grand cinema, accessible to everyone. |
| `insta-cog` | Script, shoot, stitch, score — automatically. Full video production for social media. |
| `image-cog` | Consistent characters across scenes. The most advanced image generation suite. |
| `music-cog` | Original music, fully yours. 5 seconds to 10 minutes. Instrumental and perfect vocals. |
| `audio-cog` | 8 frontier voices. Speech that sounds human, not generated. |
| `pod-cog` | Compelling content, natural voices, polished production. Single prompt to finished podcast. |
| `meme-cog` | Deep reasoning makes better comedy. Create memes that actually land. |
| `brand-cog` | Other tools make logos. CellCog builds brands. Deep reasoning + widest modality. |
| `docs-cog` | Deep reasoning. Accurate data. Beautiful design. Professional documents in minutes. |
| `slides-cog` | Content worth presenting, design worth looking at. Minimal prompt, maximal slides. |
| `sheet-cog` | Built by the same Coding Agent that builds CellCog itself. Engineering-grade spreadsheets. |
| `dash-cog` | Interactive dashboards and data visualizations. Built with real code, not templates. |
| `game-cog` | Other tools generate sprites. CellCog builds game worlds. Every asset cohesive. |
| `learn-cog` | The best tutors explain the same concept five different ways. CellCog does too. |
| `comi-cog` | Character-consistent comics. Same face, every panel. Manga, webtoons, graphic novels. |
| `story-cog` | Deep reasoning for deep stories. World building, characters, and narratives with substance. |
| `think-cog` | Your Alfred. Iteration, not conversation. Think → Do → Review → Repeat. |
| `tube-cog` | YouTube Shorts, tutorials, thumbnails — optimized for the platform that matters. |
| `fin-cog` | Wall Street-grade analysis, accessible globally. From raw tickers to boardroom-ready deliverables. |
| `proto-cog` | Build prototypes you can click. Wireframes to interactive HTML in one prompt. |
| `crypto-cog` | Deep research for a 24/7 market. From degen plays to institutional due diligence. |
| `data-cog` | Your data has answers. CellCog asks the right questions. Messy CSVs to clear insights. |
| `3d-cog` | Other tools need perfect images. CellCog turns ideas into 3D models. Any input to GLB. |
| `resume-cog` | 7 seconds on your resume. CellCog makes every second count. Research-first, ATS-optimized, beautifully designed. |
| `legal-cog` | Legal demands frontier reasoning + precision documents. CellCog delivers both. |
| `banana-cog` | Nano Banana × CellCog. Complex multi-image jobs, character consistency, visual projects. |
| `seedance-cog` | Seedance × CellCog. ByteDance's #1 video model meets multi-agent orchestration. |
| `travel-cog` | Real travel planning needs real research — not recycled blog listicles. |
| `news-cog` | Frontier search + multi-angle research. News intelligence without context flooding. |
| `cowork-cog` | CellCog on your machine. Desktop setup, terminal access, file ops — auto-approved for agents. |
| `project-cog` | Knowledge workspaces. Upload docs, get AI-processed context trees, signed URLs. Standalone or with CellCog. |
| `code-cog` | The first coding agent built for agents. Direct machine access, terminal ops, and on-demand multimedia. |

**This skill shows you HOW to use CellCog. Capability skills show you WHAT's possible.**

---

### ⚠️ OpenClaw 2026.4.x Gateway Configuration

OpenClaw 2026.4+ blocks `sessions_send` by default. CellCog requires it for result delivery. Run once:

```bash
openclaw config set gateway.tools.allow '["sessions_send", "sessions_list"]'
```

Then restart the gateway. Without this, CellCog task completions will not be delivered to your session.

---

## Support & Troubleshooting

For error handling, recovery patterns, ticket submission, and daemon troubleshooting:

```python
docs = client.get_support_docs()
```
