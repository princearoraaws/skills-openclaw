# Audio Announcement Skill 🦊

让 OpenClaw 开口说话，实时播报 AI 的一举一动！

## 概述

这是一个语音播报技能，可以让你的 AI 代理通过语音实时告诉你它在做什么。就像一只爱说话的龙虾，让你更清楚、更安心地知道 AI 的当前状态。

**版本**: 1.6.0  
**状态**: ✅ 生产就绪  
**安装**: `clawhub install audio-announcement`

### 🎯 v1.6.0 正式版更新
- ✅ **完整自动播报规则** - 6个触发时机：收到指令、授权确认、执行中、完成、发送回复、异常
- ✅ **API/网络异常播报** - Token 用完、网络超时、服务异常时自动告警
- ✅ **发送文字回复播报** - 发送回复前播报内容总结
- ✅ **自动播报集成指南** - 提供 3 种集成方案（AGENTS.md/SOUL.md/特定技能）
- ✅ **Windows 平台优化** - 自动检测并调用 pygame，无需手动选择
- ✅ **修复播放问题** - 使用 Python API，添加播放完成等待
- ✅ **统一版本号** - 所有文件版本号一致

### 📜 历史更新
- **v1.5.0**: Windows 默认使用 pygame，清理测试脚本
- **v1.4.0**: Windows 11 完整支持，新增 `announce_pygame.py`，修复新会话语音、macOS 兼容性
- **v1.3.0**: 新增 workflow-helper.sh，支持自动包装命令
- **v1.2.0**: 新增离线模式支持
- **v1.1.0**: 支持多语言（9种语言）
- **v1.0.0**: 初始版本，支持 macOS/Linux

### 📜 历史更新
- **v1.4.0**: Windows 11 完整支持，新增 `announce_pygame.py`，修复新会话语音、macOS 兼容性、跨平台哈希计算
- **v1.3.0**: 新增 workflow-helper.sh，支持自动包装命令
- **v1.2.0**: 新增离线模式支持
- **v1.1.0**: 支持多语言（9种语言）
- **v1.0.0**: 初始版本，支持 macOS/Linux

### 特性

- 🎯 **透明度**：清楚知道 AI 正在执行什么操作
- 🔒 **安全感**：实时听到操作，不用盯着日志看
- 💬 **人性化**：友好的声音，不是冷冰冰的文字
- ⚡ **效率**：专注你的工作，让 AI 用声音告诉你进度
- 🌍 **9种语言**：中文、英文、日文、韩文、西班牙语、法语、德语等
- 🔄 **队列机制**：消息永不丢失，自动重试

## 平台支持

| 平台 | 状态 | 推荐方案 | 说明 |
|------|------|----------|------|
| **macOS** | ✅ 稳定 | `announce.sh` | 原生 `afplay` 播放，无需额外依赖 |
| **Linux** | ✅ 稳定 | `announce.sh` | 需安装 `mpg123` 或 `ffmpeg` |
| **Windows** | ✅ 稳定 | `announce.sh` | 自动调用 pygame，无需 WMP |
| **Android** | ⚠️ 实验性 | `announce.sh` | 需要 Termux 环境 |

### Windows 特别说明 (v1.5.0 更新)

Windows 11 默认禁用了 Windows Media Player。从 v1.5.0 开始，`announce.sh` 在 Windows 平台会自动检测并调用 `announce_pygame.py`，无需手动选择脚本：

```powershell
# 安装依赖
pip install edge-tts pygame

# 统一使用 announce.sh（Windows 自动调用 pygame 版本）
./announce.sh complete "任务完成" zh
```

**Windows 方案对比：**

| 方案 | 依赖 | 适用场景 |
|------|------|----------|
| `announce.sh` | `pygame` | ✅ **推荐**，自动检测平台，统一接口 |
| `announce_pygame.py` | `pygame` | 直接调用，高级用户可选 |
| `announce.bat` | VLC/WMP | 备用方案，需安装 VLC |
| `announce.ps1` | PowerShell + WMP | 旧方案，Win11 可能不兼容 |

## 安装依赖

### 1. 安装 Python 依赖

```bash
pip install edge-tts
```

注意：edge-tts 需要 Python 3.7+。如果遇到安装问题，请确保网络通畅或使用国内镜像源。

### 2. 平台特定依赖

#### macOS
- 系统自带音频播放支持，无需额外安装

#### Linux
```bash
# Ubuntu/Debian
sudo apt-get install mpg123

# CentOS/RHEL/Fedora
sudo yum install mpg123
```

#### Windows

**推荐方案 - 使用 pygame（无需 VLC/WMP）：**
```powershell
pip install edge-tts pygame
```

**备用方案 - 使用 VLC：**
- 安装 [VLC](https://www.videolan.org/vlc/) 媒体播放器
- 或确保系统已安装能播放 MP3 的音频软件

## 安装方法

### 🚀 方法一：使用 ClawHub（推荐）

```bash
# 安装最新版
clawhub install audio-announcement

# 或安装特定版本
clawhub install audio-announcement@1.4.0
```

**优点**：
- 自动处理依赖和配置
- 一键安装，无需手动复制文件
- 自动版本管理
- 社区支持

### 方法二：手动安装（备用）

1. 克隆此技能仓库：
```bash
git clone https://github.com/wililam/audio-announcement-skills.git
```

2. 复制技能到 OpenClaw skills 目录：
```bash
# macOS/Linux
cp -r audio-announcement-skills/skills/audio-announcement ~/.openclaw/skills/

# Windows (PowerShell)
Copy-Item -Recurse -Force audio-announcement-skills\skills\audio-announcement $env:USERPROFILE\.openclaw\skills\
```

### 方法三：从网络直接下载（如果克隆失败）

如果 git clone 失败，可以手动下载：
1. 访问 https://github.com/wililam/audio-announcement-skills
2. 点击 "Code" → "Download ZIP"
3. 解压后复制 `skills/audio-announcement` 文件夹到 `~/.openclaw/skills/`

## 使用方法

### 测试播报

使用 `announce.sh` 脚本测试语音功能：

```bash
# 中文播报（任务完成）
./announce.sh complete "任务完成" zh

# 英文播报（任务完成）
./announce.sh complete "Task finished" en

# 日文播报（处理中）
./announce.sh task "処理中です" ja
```

### 在 OpenClaw 中使用

技能安装后，OpenClaw 会自动加载。你可以通过以下方式触发播报：

1. **在技能配置中启用**：确保 audio-announcement 技能已启用
2. **自定义事件**：在你的工作流中添加播报动作
3. **使用 Skill API**：调用 `announce.sh` 脚本

### 使用方法

#### macOS / Linux

使用 `announce.sh` 脚本：

```bash
# 中文播报（任务完成）
./announce.sh complete "任务完成" zh

# 英文播报（任务完成）
./announce.sh complete "Task finished" en

# 日文播报（处理中）
./announce.sh task "処理中です" ja
```

#### Windows

使用 `announce_pygame.py` 脚本（推荐）：

```powershell
# 中文播报
python scripts/announce_pygame.py complete "任务完成" zh

# 英文播报
python scripts/announce_pygame.py task "Processing..." en

# 日文播报
python scripts/announce_pygame.py error "エラーが発生しました" ja
```

**Windows 批处理脚本（备用）：**

```cmd
# 使用批处理脚本（需安装 VLC）
scripts\announce.bat complete "任务完成" zh
```

### 脚本参数

所有脚本支持以下参数：

```bash
./announce.sh <type> "<message>" <language>

# type: 消息类型
#   - task: 任务开始/处理中
#   - complete: 任务完成
#   - error: 错误/警告
#   - custom: 自定义消息

# message: 要播报的文字内容

# language: 语言代码
#   - zh: 中文
#   - en: 英文
#   - ja: 日文
#   - ko: 韩文
#   - es: 西班牙语
#   - fr: 法语
#   - de: 德语
```

## 故障排除

### edge-tts 安装失败
- 检查 Python 版本（需要 3.7+）
- 使用 `--trusted-host` 参数或更换镜像源
- 升级 pip: `python -m pip install --upgrade pip`

### Windows 特定问题

**问题：Windows 11 没有声音**
- ✅ 解决方案：使用 `announce_pygame.py` 替代 `announce.bat`
- 安装 pygame: `pip install pygame`
- 原因：Windows 11 默认禁用 Windows Media Player

**问题：pygame 安装失败**
- 确保 Python 3.7+ 已安装
- 尝试: `pip install pygame --upgrade`
- 或下载预编译 wheel: https://pypi.org/project/pygame/#files

### 没有声音
- **macOS**: 检查系统音量，确认 `afplay` 可用
- **Linux**: 确认 `mpg123` 或 `ffmpeg` 已安装
- **Windows**: 确认 `pygame` 已安装，或使用 VLC 方案
- 测试播放: `mpg123 test.mp3` (Linux) 或系统音频播放器

### 播报延迟
- 首次使用会有缓存延迟（首次下载语音包）
- 网络不佳时可能影响语音获取速度
- 考虑使用本地语音合成引擎替代

## 技术说明

- 使用 Microsoft Edge 的 TTS 在线服务
- 语音队列系统确保消息按顺序播放
- 支持中断和优先级管理
- 自动重试失败的播报

## 贡献

欢迎提交 Issue 和 PR！

## License

MIT License - 详见 [LICENSE](LICENSE) 文件

## 作者

miaoweilin - [GitHub](https://github.com/wililam)

## 🔧 自动播报集成指南

> **重要说明**：`audio-announcement` 是一个**工具型技能**，安装后需要额外配置才能实现**自动播报**。
> 
> 当前 OpenClaw 尚未内置自动触发机制，需要手动集成到工作流中。

### 方案一：修改 AGENTS.md（推荐）

在 OpenClaw 工作区添加全局播报支持：

```bash
# 编辑 ~/.openclaw/workspace/AGENTS.md
# 在 "Session Startup" 部分添加：

## 语音播报初始化
init_announcement() {
    local script="$HOME/.openclaw/skills/audio-announcement/scripts/announce.sh"
    if [ -f "$script" ]; then
        chmod +x "$script"
        # 播报系统就绪
        "$script" "custom" "语音播报系统已就绪" "zh" 2>/dev/null
    fi
}

# 快捷播报函数
announce_task() { "$HOME/.openclaw/skills/audio-announcement/scripts/announce.sh" "task" "$1" "${2:-zh}" 2>/dev/null; }
announce_complete() { "$HOME/.openclaw/skills/audio-announcement/scripts/announce.sh" "complete" "$1" "${2:-zh}" 2>/dev/null; }
announce_error() { "$HOME/.openclaw/skills/audio-announcement/scripts/announce.sh" "error" "$1" "${2:-zh}" 2>/dev/null; }

# 会话启动时初始化
init_announcement
```

### 方案二：修改 SOUL.md 定义播报规则

```markdown
## 语音播报规则

语音播报会在以下四个时刻触发：

1. **收到指令时** - 播报确认收到的任务内容
   - 示例："收到上传指令"、"收到搜索指令"

2. **需要授权/确认时** - 提醒用户需要确认操作
   - 示例："需要确认权限"、"请检查授权"

3. **执行过程中** - 播报当前进度和下一步操作
   - 示例："正在生成文档"、"正在处理数据"

4. **任务完成时** - 播报工作总结
   - 示例："上传完成"、"处理完毕"

### 播报内容规范
- 使用微软 Edge TTS 的 `zh-CN-XiaoxiaoNeural`（中文女声）
- 内容简洁直接，不超过 20 个字
- 不称呼名称（不说用户名、不说"我"）
- 口语化，像朋友随口说一句
- 临时文件播放后立即删除，不保留在工作区

### 播报时机与内容（v1.5.4 更新）

| 时机 | 类型 | 内容要求 | 示例 |
|------|------|----------|------|
| 收到消息 | `receive` | 收到的指令信息 | "收到上传指令" |
| 开始工作 | `task` | 工作规划 | "准备上传到GitHub" |
| 执行中 | `task` | 下一步要处理的内容 | "正在生成文档" |
| 任务完成 | `complete` | 工作总结 | "上传完成" |
| **发送回复** | `complete` | 回复内容的简短总结 | "已发送项目地址" |

### 强制播报场景
- 每次收到用户消息 → 先播报指令内容
- 开始执行任务 → 播报工作规划
- 执行过程中 → 播报下一步要做什么
- 任务完成/失败 → 播报工作总结
- **发送文字回复前 → 播报回复内容的简短总结（1句话）**
- **API/网络异常时 → 播报告警信息**
  - Token 用完 → "额度不足"
  - 网络超时 → "连接超时"  
  - 接口异常 → "服务异常"
  - 模型不可用 → "模型繁忙"
```

### 方案三：在 SKILL.md 中集成（针对特定技能）

示例：在 `code` 技能中添加播报

```markdown
## 执行流程（带播报）

1. **规划阶段**
   ```bash
   announce_task "开始代码规划"
   # ... 规划逻辑 ...
   announce_complete "代码规划完成"
   ```

2. **实现阶段**
   ```bash
   announce_task "开始代码实现"
   # ... 编码逻辑 ...
   announce_complete "代码实现完成"
   ```

3. **验证阶段**
   ```bash
   announce_task "开始代码验证"
   # ... 测试逻辑 ...
   if [ 测试通过 ]; then
       announce_complete "代码验证通过"
   else
       announce_error "代码验证失败"
   fi
   ```
```

---

## 🚀 工作流程集成

### 快速集成
```bash
# 加载助手函数
source ~/.openclaw/skills/audio-announcement/scripts/workflow-helper.sh

# 使用示例
announce_task "开始任务"
announce_complete "任务完成"
announce_error "发生错误"
```

### 自动包装命令
```bash
# 自动播报任务开始和完成
announce_wrap "文件备份" backup_script.sh
```

### 带进度播报
```bash
announce_with_progress "系统更新" 3 \
    "sudo apt update" \
    "sudo apt upgrade -y" \
    "sudo apt autoremove -y"
```

---

## 📋 常见问题

### Q: 安装后为什么没有自动播报？
**A**: 这是预期行为。`audio-announcement` 提供播报能力，但需要手动集成到工作流中。参考上方的"自动播报集成指南"。

### Q: 哪些场景适合添加播报？
**A**: 
- ✅ 长时间运行的任务（研究、代码生成、数据处理）
- ✅ 需要用户决策的节点（确认、选择、审核）
- ✅ 后台运行的监控任务（GitHub 监控、定时任务）
- ✅ 多步骤流程的里程碑（阶段完成、检查点）

### Q: 能否实现全自动播报？
**A**: 目前需要等待 OpenClaw 官方支持 skill hooks（pre/post 执行钩子）。届时可以实现：
- 每个技能执行前自动播报
- 每个技能完成后自动播报结果
- 出错时自动播报警告

---

🦊 让你的工作流程会说话，提高透明度和工作效率！
Make your workflow talk, increase transparency and productivity!

⭐ 如果这个技能对你有帮助，请给它一个 star！⭐
