---
name: session-sleep-wake
description: "在 session 重置后首次启动时，读取对应 session 的 preview 文件并注入未完成事项到新 session 上下文"
homepage: https://docs.openclaw.ai/automation/hooks
metadata:
  {
    "openclaw": {
      "emoji": "🌙",
      "events": ["agent:bootstrap"],
      "requires": { "config": ["workspace.dir"] },
      "install": [{ "id": "workspace", "kind": "workspace", "label": "Workspace hooks" }]
    }
  }
---

# Session Sleep-Wake Hook

## What It Does

每次新 session 启动时（`agent:bootstrap` 事件），根据 `event.sessionKey` 查找对应的 preview 文件：

```
workspace/previews/{sessionKey}.md
```

- **状态为 pending** → 将未完成事项注入到 `event.messages`，新 session 开头可见
- **状态为 all_done** → 不做任何事，正常启动

## Event Context

- `event.sessionKey` — 用于定位 preview 文件（如 `agent:main:main`）
- `event.context.workspaceDir` — 工作空间路径
- `event.messages` — push 到此数组的内容会在新 session 开头显示
