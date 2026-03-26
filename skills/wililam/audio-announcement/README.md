# Audio Announcement Skill

<div align="center">

![Version](https://img.shields.io/badge/version-1.6.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows%20%7C%20Android-lightgrey.svg)

# 🦊 A Chatty Lobster | 一只多嘴的龙虾

**Hear what your AI agent is doing in real-time. Stay informed, stay safe.**

**实时语音播报AI的一举一动，让你更安心、更放心。**

*"I'm generating your report..."* • *"Task completed!"* • *"I need your permission..."*

不再是冷冰冰的日志，而是一只爱说话的龙虾朋友 🦊

[English](#english) | [中文](#中文)

</div>

---

<a name="english"></a>
## 🇺🇸 English

### Why A Chatty Lobster?

Your AI agent shouldn't be a black box. With this skill, OpenClaw becomes a **talkative companion** that keeps you informed:

- 🎯 **Transparency**: Know exactly what your AI is doing
- 🔒 **Security Feel**: Hear actions in real-time, no need to watch logs
- 💬 **Human Touch**: A friendly voice, not cold text
- ⚡ **Efficiency**: Focus on your work, let the lobster speak

### Features

- 🌍 **9 Languages**: Chinese, English, Japanese, Korean, Spanish, French, German
- 💻 **4 Platforms**: macOS, Linux, Windows, Android
- 🔄 **Queue System**: Messages never lost, auto-retry on failure
- 🦊 **Human-Friendly**: Make your AI feel safer and more approachable

### Quick Start

```bash
# Install
pip install edge-tts

# Clone
git clone https://github.com/wililam/audio-announcement-skills.git

# Copy to your skills
cp -r audio-announcement-skills/skills/audio-announcement ~/.openclaw/skills/
```

### Usage

**macOS / Linux:**
```bash
# The lobster speaks Chinese
./announce.sh complete "任务完成" zh

# The lobster speaks English
./announce.sh complete "Task finished" en

# The lobster speaks Japanese
./announce.sh task "処理中です" ja
```

**Windows (Recommended - PyGame):**
```powershell
# Install PyGame for best Windows 11 support
pip install pygame

# The lobster speaks Chinese (v1.5.0+: announce.sh auto-detects Windows)
./announce.sh complete "任务完成" zh

# The lobster speaks English
./announce.sh task "Processing..." en
```

---

<a name="中文"></a>
## 🇨🇳 中文

### 为什么需要一只多嘴的龙虾？

AI 不应该是一个"黑盒"。有了这个技能，OpenClaw 变成了一只**爱说话的龙虾朋友**：

- 🎯 **透明度**：清楚知道 AI 在做什么
- 🔒 **安全感**：实时听到操作，不用盯着日志看
- 💬 **人性化**：朋友般的声音，不是冷冰冰的文字
- ⚡ **效率**：专注你的工作，让龙虾用声音告诉你进度

### 特性

- 🌍 **9种语言**：中文、英文、日文、韩文、西班牙语、法语、德语
- 💻 **4个平台**：macOS、Linux、Windows、Android
- 🔄 **队列机制**：消息永不丢失，自动重试
- 🦊 **人性化**：让你的 AI 更安全、更亲切

### 使用方法

**macOS / Linux:**
```bash
# 安装依赖
pip install edge-tts

# 克隆
git clone https://github.com/wililam/audio-announcement-skills.git

# 使用
./announce.sh complete "任务完成" zh
```

**Windows (推荐 - PyGame):**
```powershell
# 安装依赖
pip install edge-tts pygame

# 克隆
git clone https://github.com/wililam/audio-announcement-skills.git

# 使用（v1.5.0+: announce.sh 自动检测 Windows 平台）
./announce.sh complete "任务完成" zh
```

---

## 📁 Project Structure

```
audio-announcement-skills/
├── README.md
├── LICENSE
├── package.json
├── .gitignore
└── skills/
    └── audio-announcement/
        ├── SKILL.md              # 详细使用文档（含自动播报集成指南）
        ├── WINDOWS_FIX.md        # Windows 11 修复指南
        ├── USAGE.md              # 使用示例
        ├── version.txt
        └── scripts/
            ├── announce.sh           # 主脚本 (v1.5.0+: Windows 自动调用 pygame)
            ├── announce_pygame.py    # Windows pygame 方案
            ├── announce.bat          # Windows 批处理 (备用)
            ├── announce.ps1          # PowerShell 脚本
            ├── announce-offline.sh   # 离线模式
            └── workflow-helper.sh    # 工作流助手
```

## ⚠️ 重要提示

**安装后不会自动播报！** 本技能提供播报能力，但需要额外配置才能自动工作。

### 语音播报触发时机

配置完成后，语音播报会在以下六个时刻触发：

| 时机 | 类型 | 播报内容示例 |
|------|------|-------------|
| **收到指令时** | `receive` | "收到上传指令"、"收到搜索指令" |
| **需要授权/确认时** | `error` | "需要确认权限"、"请检查授权" |
| **执行过程中** | `task` | "正在生成文档"、"正在处理数据" |
| **任务完成时** | `complete` | "上传完成"、"处理完毕" |
| **发送文字回复时** | `complete` | "已发送项目地址"、"回复完成" |
| **API/网络异常时** | `error` | "额度不足"、"连接超时"、"模型繁忙" |

**播报规范：** 使用微软 Edge TTS 中文女声，内容简洁（≤20字），不称呼名称，临时文件播放后立即删除。

### 快速启用自动播报

1. **编辑 `~/.openclaw/workspace/AGENTS.md`**
2. **在 Session Startup 部分添加：**

```bash
# 语音播报初始化
announce_task() { "$HOME/.openclaw/skills/audio-announcement/scripts/announce.sh" "task" "$1" "${2:-zh}" 2>/dev/null; }
announce_complete() { "$HOME/.openclaw/skills/audio-announcement/scripts/announce.sh" "complete" "$1" "${2:-zh}" 2>/dev/null; }
announce_error() { "$HOME/.openclaw/skills/audio-announcement/scripts/announce.sh" "error" "$1" "${2:-zh}" 2>/dev/null; }

# 播报系统就绪
announce_complete "语音播报系统已就绪"
```

3. **详细集成方案请参考 SKILL.md 中的"自动播报集成指南"**

## 📝 License

MIT License - see [LICENSE](LICENSE) file.

## 👤 Author

**miaoweilin** - [GitHub](https://github.com/wililam)

---

<div align="center">

**🦊 让你的龙虾开口说话，让你更安心！**

**Make your lobster talk, make yourself feel safer!**

⭐ If this helped you, give it a star! ⭐

</div>