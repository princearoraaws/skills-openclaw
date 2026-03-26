---
name: xiabb
description: "虾BB — 免费 macOS 语音转文字，专为 Vibe Coding 设计。按住 Globe 键说话，文字自动出现在光标位置。Powered by Google Gemini。Apple Notarized。"
version: 1.1.5
metadata:
  openclaw:
    requires:
      env:
        - GEMINI_API_KEY
      config:
        - ~/Tools/xiabb/.api-key
    primaryEnv: GEMINI_API_KEY
---

# 虾BB / XiaBB

**按住 Globe 键，说话，文字出现。** 专为 Vibe Coding 设计的免费语音转文字。

- 🆓 完全免费 — Google Gemini 免费额度 250次/天
- 🌏 中英完美混输 — "帮我把这个 component 改成 async 的" → 完美识别
- 🔴 实时流式预览 — 边说边看文字出现（Gemini Live API）
- ⚡ 341KB 纯 Swift — 零依赖，macOS 原生
- 🧠 LLM 引擎 — 不是 Whisper ASR，是 Gemini 大语言模型理解语义
- 📖 开源 MIT — 已通过 Apple 公证

## 安装

下载已通过 Apple 公证的 DMG（app release v1.1.3）：

```bash
curl -L -o /tmp/XiaBB.dmg "https://github.com/dyz2102/xiabb/releases/download/v1.1.3/XiaBB-v1.1.3-macOS-arm64.dmg"
```

**安装前验证校验和：**

```bash
echo "ce53a5b0ccc3b0993b284686ab05716f3e616969f98395d1baf8aec083f8d784  /tmp/XiaBB.dmg" | shasum -a 256 -c
```

打开 DMG 并将 XiaBB.app 拖到 Applications：

```bash
open /tmp/XiaBB.dmg
```

已使用 Developer ID 签名并通过 Apple 公证，不会出现 Gatekeeper 警告。

### 从源码编译（可选）

如需自行审查和编译：

```bash
git clone https://github.com/dyz2102/xiabb.git /tmp/xiabb-build
cd /tmp/xiabb-build
# 运行前请先审查 install.sh 和 native/main.swift
cat install.sh
bash install.sh
```

需要 Xcode 命令行工具（`xcode-select --install`）。

## 配置

### Gemini API Key

前往 https://aistudio.google.com/apikey 获取免费 Key，然后配置：

```bash
# 推荐：环境变量
export GEMINI_API_KEY="你的key"
```

或通过菜单栏 → "配置 Gemini API Key..." 配置。

Key 存储在本地 `~/Tools/xiabb/.api-key`（建议 chmod 600）。

### 权限

首次启动时 macOS 会请求：
- **辅助功能**：用于检测 Globe 键（CGEventTap）
- **麦克风**：用于语音录制

两者都是语音输入应用的标准 macOS 权限。在系统设置 → 隐私与安全性中授权。

## 使用

| 操作 | 效果 |
|------|------|
| 按住 🌐 Globe 键 | 开始录音，HUD 显示实时预览 |
| 松开 🌐 Globe 键 | 转写完成，文字粘贴到光标位置 |
| 点击 HUD 📋 | 复制转写结果 |

## 安全与隐私

- **开源**：完整源码 https://github.com/dyz2102/xiabb — 使用前可审查
- **Apple 公证**：Developer ID 签名，Apple 验证通过
- **无需账号**：无注册、无追踪、无遥测
- **音频处理**：音频发送至 Google Gemini API 进行转录
- **本地存储**：API Key 和配置仅存本地

## 链接

- 🌐 官网：https://xiabb.lol
- 📦 GitHub：https://github.com/dyz2102/xiabb
- 📄 MIT License
