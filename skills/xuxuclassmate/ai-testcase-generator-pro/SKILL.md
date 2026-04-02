---
name: ai-testcase-generator-pro
version: 2.1.0
description: AI-powered test case generator with three-persona review loop. Supports PDF, Word, TXT, images, video. Exports Excel, Markdown, XMind.
author: XuXuClassMate
license: MIT
tags: [testing, qa, testcases, ai-testing, automation, openclaw]
category: Development
metadata:
  openclaw:
    requires:
      env:
        - ANTHROPIC_API_KEY
      bins:
        - node
        - npm
    primaryEnv: ANTHROPIC_API_KEY
    emoji: 🧪
    homepage: https://github.com/XuXuClassMate/testcase-generator
    safety:
      level: safe
      audit: manual
      notes: Uses OpenClaw exec API for ffmpeg calls. All LLM calls use official SDKs. No shell execution.
---

# AI Test Case Generator Skill

🧪 AI-powered test case generator with three-persona review loop for OpenClaw.

---

## 🚀 Quick Start for OpenClaw Users

### Step 1: Install the Skill

```bash
# Install from ClawHub (recommended)
openclaw skills install xuxuclassmate/ai-testcase-generator-pro

# Or install from local source (development mode)
git clone https://github.com/XuXuClassMate/testcase-generator
cd testcase-generator
openclaw skills install -l .
```

### Step 2: Configure API Keys

Edit your OpenClaw config (`~/.openclaw/config.yaml`):

```yaml
plugins:
  entries:
    ai-testcase-generator-pro:
      enabled: true
      config:
        models:
          - id: claude-generator
            vendor: anthropic
            model: claude-opus-4-5
            apiKey: "sk-ant-..."  # Your Anthropic API key
            role: generator
          - id: gpt4o-reviewer
            vendor: openai
            model: gpt-4o
            apiKey: "sk-..."      # Your OpenAI API key
            role: reviewer
        language: en              # or 'zh' for Chinese
        enableReviewLoop: true
        reviewScoreThreshold: 90
        maxReviewRounds: 5
```

**Minimum config** (just one API key):

```yaml
plugins:
  entries:
    ai-testcase-generator-pro:
      enabled: true
      config:
        models:
          - vendor: anthropic
            model: claude-opus-4-5
            apiKey: "sk-ant-..."
```

### Step 3: Restart OpenClaw Gateway

```bash
openclaw gateway restart
```

### Step 4: Verify Installation

```bash
openclaw skills list
# You should see: ai-testcase-generator-pro ✅
```

---

## 💬 How to Use

### Method 1: Chat Commands

In your OpenClaw chat (Feishu, Telegram, Discord, etc.):

```
/testgen User login: phone+password, OAuth, lock after 5 failed attempts
```

Or with file attachments:

```
/testgen [attach your PDF/Word/image/video files]
```

### Method 2: As an AI Tool

The skill automatically registers as a tool. Just ask your AI assistant:

> "Generate test cases for the checkout flow: add to cart → payment → order confirmation"

The AI will automatically invoke the `generate_test_cases` tool.

### Method 3: Advanced Options

```
/testgen /path/to/requirements.pdf --prompt "Focus on security testing" --stage development --language zh
```

**Options:**
- `--prompt`: Custom focus hint (e.g., "Focus on performance", "Add edge cases")
- `--stage`: `requirement` | `development` | `prerelease` (default: `requirement`)
- `--language`: `en` | `zh` (default: `en`)
- `--enableReview`: `true` | `false` (default: `true`)

---

## 📦 What You Get

### Output Formats

After generation, you can download test cases in:

1. **Excel (.xlsx)** - Professional test case format with columns:
   - Test Case ID
   - Title
   - Preconditions
   - Test Steps
   - Expected Result
   - Priority (P0/P1/P2)
   - Tags

2. **Markdown (.md)** - Clean, readable format for documentation

3. **XMind (.xmind)** - Mind map for visual test planning

### Three-Persona Review Loop

Every test case is reviewed by three AI personas:

| Persona | Focus Area |
|---------|------------|
| 🎯 Test Manager | Coverage, executability, boundary scenarios |
| 💻 Dev Manager | Technical feasibility, API tests, security |
| 📋 Product Manager | Business logic, user journey, requirements alignment |

Each persona scores the test cases (0-100). The loop continues until the average score meets your threshold (default: 90).

---

## ⚙️ Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | - | Anthropic API key (required) |
| `OPENAI_API_KEY` | - | OpenAI API key (optional) |
| `DEEPSEEK_API_KEY` | - | DeepSeek API key (optional) |
| `QWEN_API_KEY` | - | Qwen (Aliyun) API key (optional) |
| `LANGUAGE` | `en` | Output language (`en` / `zh`) |
| `ENABLE_REVIEW` | `true` | Enable review loop |
| `REVIEW_THRESHOLD` | `90` | Score threshold to stop review |
| `MAX_REVIEW_ROUNDS` | `5` | Maximum review iterations |

### Supported AI Providers

| Provider | Vendor ID | Recommended Model |
|----------|-----------|-------------------|
| Anthropic | `anthropic` | claude-opus-4-5 |
| OpenAI | `openai` | gpt-4o |
| DeepSeek | `deepseek` | deepseek-chat |
| Qwen | `qwen` | qwen-max |
| Gemini | `gemini` | gemini-2.0-flash |

---

## 🔧 Development & Contributing

This is an **open source project** under the MIT License. Contributions are welcome!

### Ways to Contribute

- 🐛 **Report bugs**: Open an issue on GitHub
- 💡 **Request features**: Suggest new features or improvements
- 🔧 **Submit PRs**: Fix bugs, add features, improve docs
- 📝 **Improve docs**: Better examples, translations, tutorials

### Development Workflow

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/testcase-generator
cd testcase-generator

# Install dependencies
npm install

# Make your changes
# ...

# Test locally
npm run build
npm run standalone

# Commit and push
git commit -m "feat: add new feature"
git push origin main

# Open a Pull Request on GitHub
```

---

## 📞 Support & Links

- **📂 GitHub Repository**: https://github.com/XuXuClassMate/testcase-generator
- **🐳 Docker Hub**: https://hub.docker.com/r/xuxuclassmate/testcase-generator
- **📦 npm Package**: https://www.npmjs.com/package/@classmatexuxu/ai-testcase-generator-pro
- **🌐 ClawHub**: https://clawhub.ai/xuxuclassmate/ai-testcase-generator-pro
- **📖 Documentation**: https://xuxuclassmate.github.io/testcase-generator/
- **🐛 Issues**: https://github.com/XuXuClassMate/testcase-generator/issues

**Found a bug? Have a feature request?** Open an issue on GitHub — we love contributions! 🎉

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

Made with ❤️ by [XuXuClassMate](https://github.com/XuXuClassMate)
