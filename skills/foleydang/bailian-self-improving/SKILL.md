---
name: bailian-self-improving
description: "Extract and manage skills from conversations via Alibaba Cloud Bailian API with semantic deduplication. Use when: user explicitly teaches something ('remember this', 'always do this', 'learn this pattern'), user corrects a mistake and provides the correct approach, user demonstrates the same pattern multiple times, or user expresses satisfaction after completing a complex task. Agent should retrieve up to 5 most relevant existing skills for deduplication, API returns new/update/delete actions. Requires: DASHSCOPE_API_KEY environment variable."
homepage: https://bailian.console.aliyun.com
metadata:
  {
    "openclaw":
      {
        "emoji": "🧠",
        "requires": { "bins": ["curl"], "env": ["DASHSCOPE_API_KEY"] },
      },
  }
---

# Bailian Self-Improving

Extract and manage skills from conversations with semantic deduplication via Bailian API.

## Overview

This skill integrates with Alibaba Cloud Bailian's Skill Extraction API. The workflow:

1. **Detect learning signal** - Identify when user is teaching
2. **Retrieve relevant skills** - Search memory for up to 5 most relevant existing skills (may be none)
3. **Call API** - Send messages with existing_skills for deduplication
4. **Handle response** - Based on `event` field (new/update/delete)

This enables intelligent skill lifecycle management with automatic deduplication.

## Features

- 🧠 Automatic learning signal detection
- 🔄 Semantic deduplication against existing skills
- 📝 Structured skill definition output
- 🔒 Secure API key management

## Prerequisites

1. **Alibaba Cloud Account**: Register at [Alibaba Cloud Bailian](https://bailian.console.aliyun.com)
2. **API Key**: Obtain a DashScope API Key from the console

## Installation

```bash
openclaw skills install bailian-self-improving
```

## Configuration

Set the environment variable:

```bash
export DASHSCOPE_API_KEY="your-dashscope-api-key"
```

## Trigger Conditions

| Signal | Example Phrases |
|--------|-----------------|
| **Explicit teaching** | "remember this", "always do this", "learn this pattern" |
| **Correction** | "that's wrong, the right way is...", "no, you should..." |
| **Pattern demo** | User repeats same operation 3+ times |
| **Task satisfaction** | "perfect", "that's exactly it", "do this from now on" |

## Usage

### Command Line

```bash
# Basic extraction
bash scripts/extract_skill.sh '[{"role":"user","content":"..."},{"role":"assistant","content":"..."}]'

# With existing skills for deduplication
bash scripts/extract_skill.sh '[{"role":"user","content":"..."}]' '[{"name":"existing-skill","content":"..."}]'
```

### Via AI Assistant

Simply teach the AI:
- "Remember this pattern for future use"
- "Learn this approach"
- "Always handle this type of task this way"

## How It Works

```
Conversation → Detect Signal → Retrieve Relevant Skills (up to 5) → Call API → Handle Response
```

**Key Steps:**

1. Detect learning signal in conversation
2. Search memory for up to 5 relevant existing skills
3. Call API with messages and existing_skills
4. Handle response based on `event` field

## API Reference

### Endpoint

```
POST https://poc-dashscope.aliyuncs.com/api/v2/apps/poc-memory/skills/extract
```

### Request

```json
{
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "existing_skills": [
    {"name": "skill-name", "content": "skill content"}
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `messages` | array | Yes | Conversation messages (max 32000 chars each) |
| `existing_skills` | array | No | Up to 5 most relevant existing skills for deduplication |

### Response

```json
{
  "request_id": "req-xxx",
  "skills": [
    {
      "name": "kebab-case-identifier",
      "description": "One-line description (max 200 chars)",
      "instructions": "Detailed instructions",
      "event": "new | update | delete",
      "merge_target": "existing-skill-name",
      "event_details": "Reason for this action"
    }
  ]
}
```

### Event Types

| event | Meaning | merge_target | Agent Action |
|-------|---------|--------------|--------------|
| `new` | Brand new skill | `null` | Store to memory, notify user |
| `update` | Enhance existing | Target skill name | Merge with merge_target skill |
| `delete` | Replace/remove | `null` | Remove outdated skill |

## Agent Handling Guidelines

**DO NOT auto-write skill files.** Return JSON and let Agent decide:

1. **High confidence**: Store to memory automatically
2. **Medium confidence**: Notify user, ask confirmation
3. **Low confidence**: Ask user before storing

## Example

**User:** "Write a Go HTTP client, always do it this way"

**Agent:**
1. Generates HTTP client code
2. Detects learning signal: "always do it this way"
3. Searches memory for relevant skills (0-5)
4. Calls extraction API:
   ```json
   {
     "messages": [...],
     "existing_skills": [...]
   }
   ```
5. API returns:
   ```json
   {
     "skills": [{
       "name": "go-http-client-pattern",
       "description": "Go HTTP client development pattern",
       "instructions": "...",
       "event": "new"
     }]
   }
   ```
6. Agent stores new skill to memory

## Constraints

- Maximum 5 API calls per conversation
- `messages` max 32000 chars per message
- `existing_skills` max 5 items (most relevant), 5000 chars each
- Do NOT extract: passwords, API keys, PII, health data

## Troubleshooting

**Error: "DASHSCOPE_API_KEY environment variable is not set"**

Set the environment variable:
```bash
export DASHSCOPE_API_KEY="your-key"
```

**Empty skills array returned**

- The conversation may not contain clear learning signals
- Try rephrasing the teaching instruction more explicitly