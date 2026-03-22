---
name: workspace-backup
description: 定期将 Agent 工作空间备份到 GitHub 仓库。支持两个 workspace（main 和 formulas）分别推送到不同的 GitHub 分支。每天 03:00 自动执行。
---

# Workspace Backup

自动备份 OpenClaw 两个 Agent 的工作空间到 GitHub。

## 功能

- 备份 `~/.openclaw/workspace/` → GitHub `main` 分支
- 备份 `~/.openclaw/workspace-formulas/` → GitHub `formulas` 分支
- 每天 03:00 自动执行（通过 OpenClaw cron）

## 使用方式

### 手动执行备份

```bash
~/.openclaw/workspace/skills/workspace-backup/scripts/backup.sh
```

### 查看备份状态

```bash
~/.openclaw/workspace/skills/workspace-backup/scripts/status.sh
```

### 定时任务

已在 OpenClaw cron 中配置，每天 03:00 执行。

## 脚本说明

| 脚本 | 说明 |
|------|------|
| `backup.sh` | 执行备份（git add → commit → push） |
| `status.sh` | 查看各 workspace 的 git 状态 |

## 注意事项

- 确保 SSH Key 已配置好，可以直接 git push
- 首次执行前需要手动 git clone 或在现有目录初始化 git
- 备份失败会发送企微通知
