# Auto-Backup-Openclaw-User-Data

> OpenClaw 用户数据自动备份技能

[![Version](https://img.shields.io/badge/version-1.0.2.20260331-blue.svg)](https://github.com/hjj345/auto-backup-openclaw-user-data)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-v2026.3.1+-purple.svg)](https://openclaw.ai)

---

## 简介

`Auto-Backup-Openclaw-User-Data` 是一个专为 OpenClaw 设计的自动备份skill技能，使用本skill能够更好完成自动备份用户数据目录，支持全量/选择性备份、定时执行、ZIP 压缩、日志记录、消息通知和保留策略管理。

## 功能特性

- ✅ **自动备份** - 定时备份 `.openclaw` 目录
- ✅ **选择性备份** - 支持全量或部分备份（交互式选择文件/文件夹）
- ✅ **ZIP 压缩** - 自动压缩并按规则命名
- ✅ **定时执行** - 支持 HEARTBEAT 心跳和 Cron 定时任务两种方式
- ✅ **日志记录** - 完整记录执行过程
- ✅ **消息通知** - 支持多渠道推送结果
- ✅ **保留策略** - 自动清理旧备份
- ✅ **跨平台** - Windows / Linux / macOS 全支持

## 安装

### 方式一：ClawHub 安装

```bash
openclaw skill install auto-backup-openclaw-user-data
```

### 方式二：本地文件安装

```bash
openclaw skill install /path/to/auto-backup-openclaw-user-data.skill
```

### 方式三：GitHub 安装

```bash
openclaw skill install https://github.com/hjj345/auto-backup-openclaw-user-data
```

## 快速开始

### 立即执行备份

```
/backup_now
```

### 查看备份状态

```
/backup_status
```

### 配置备份选项

```
/backup_config
```

### 列出备份文件

```
/backup_list
```

### 清理旧备份

```
/backup_clean
```

## 命令说明

| 命令 | 功能 | 参数 |
|------|------|------|
| `/backup_now` | 立即执行备份 | `--full`, `--partial` |
| `/backup_status` | 查看备份状态 | - |
| `/backup_config` | 配置向导 | `[1-4]` |
| `/backup_list` | 列出备份文件 | `--all` |
| `/backup_clean` | 清理旧备份 | `--preview`, `--confirm` |

## 定时任务配置

本 skill 支持两种定时执行方式，请根据实际需求选择：

### 方式对比

| 特性 | HEARTBEAT 心跳 | Cron 定时任务 |
|------|---------------|---------------|
| 定时精度 | 约 30 分钟漂移 | 精确到分钟 |
| 运行上下文 | 主会话（共享） | 隔离会话 |
| 配置复杂度 | 较简单 | 需 CLI 配置 |
| 推送控制 | 需手动实现 | 内置支持 |
| 适用场景 | 周期性监控检查 | 精确时间执行 |

### 方式一：HEARTBEAT 心跳（推荐新手）

适用于周期性监控检查，不要求精确执行时间。

**配置步骤**：

1. 查看项目根目录中的 `HEARTBEAT_prompt_example.md` 文件
2. 根据模板内容，修改你的 Agent 工作区的 `HEARTBEAT.md` 文件
3. 修改模板中的配置变量（备份时间、skill 路径、推送目标等）
4. 确保 Gateway 正在运行

**详细说明**：见 [HEARTBEAT_prompt_example.md](HEARTBEAT_prompt_example.md)

### 方式二：Cron 定时任务（推荐高级用户）

适用于需要精确时间执行的场景（如每天凌晨 3:20）。

**配置步骤**：

1. 查看项目根目录中的 `cron_prompt_example.md` 文件
2. 准备配置信息（skill 路径、飞书群 ID、Telegram Bot Token 等）
3. 编辑 `~/.openclaw/cron/jobs.json` 或使用 CLI 命令添加定时任务
4. 重启 Gateway

**详细说明**：见 [cron_prompt_example.md](cron_prompt_example.md)

## 配置

配置文件位置：`~/.openclaw/workspace/Auto-Backup-Openclaw-User-Data/config.json`

### 默认配置

```json
{
  "backup": {
    "mode": "full",
    "exclude": ["logs", "cache", "tmp", "node_modules"]
  },
  "schedule": {
    "enabled": true,
    "cron": "0 3 * * *"
  },
  "retention": {
    "enabled": true,
    "mode": "count",
    "count": 10
  },
  "notification": {
    "enabled": true,
    "channels": ["feishu"],
    "targets": {}
  }
}
```

详细配置说明请参考 [references/config-schema.md](references/config-schema.md)

## 文件结构

```
~/.openclaw/workspace/Auto-Backup-Openclaw-User-Data/
├── config.json       # 用户配置
├── backup.log        # 备份日志
└── backups/          # 备份文件存储
    └── auto-backup-openclaw-user-data_YYYYMMDD_HHMM_vX.X.X_XX.zip
```

## ZIP 文件命名规则

```
auto-backup-openclaw-user-data_{YYYYMMDD}_{HHMM}_{version}_{序号}.zip

示例：
auto-backup-openclaw-user-data_20260326_0300_v2026.3.23-2_01.zip
```

## 故障排查

遇到问题？请参考 [references/troubleshooting.md](references/troubleshooting.md)

## 技术架构

```
auto-backup-openclaw-user-data/
├── SKILL.md              # 技能说明
├── scripts/
│   ├── backup.js         # 主备份逻辑
│   ├── compressor.js     # ZIP 压缩
│   ├── scheduler.js      # 定时调度
│   ├── cleaner.js        # 清理策略
│   ├── notifier.js       # 消息通知
│   ├── config.js         # 配置管理
│   ├── logger.js         # 日志记录
│   └── cli.js            # CLI 入口
├── references/
│   ├── config-schema.md  # 配置说明
│   └── troubleshooting.md # 故障排查
└── templates/
    └── config.template.json
```

## 依赖

- Node.js >= 18.0.0
- archiver ^6.0.0
- fs-extra ^11.0.0
- dayjs ^1.11.0

## 开发

```bash
# 克隆仓库
git clone https://github.com/hjj345/auto-backup-openclaw-user-data.git

# 安装依赖
cd auto-backup-openclaw-user-data
npm install

# 测试
npm test
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

[MIT License](LICENSE)

## 作者

- **Jack·Huang**
- Email: jack698698@gmail.com

## 更新日志

### v1.0.2.20260331 (2026-03-31)

- 新增：HEARTBEAT 心跳定时任务模板（`HEARTBEAT_prompt_example.md`）
- 新增：Cron 定时任务模板（`cron_prompt_example.md`）
- 新增：选择性备份交互式文件选择功能
- 新增：文件选择确认/重新选择功能
- 优化：交互式配置步骤从 6 步调整为 7 步（新增文件选择步骤）
- 优化：选择性备份时列出 `~/.openclaw/` 目录文件清单
- 文档：README.md 和 USAGE.md 新增定时任务配置说明

### v1.0.1.20260326 (2026-03-26)

- 新增：消息推送目标配置功能
- 新增：读取 OpenClaw 配置自动获取可用推送目标
- 新增：推送失败时通过当前对话提醒用户
- 优化：`/backup_list` 只显示本 skill 产生的备份文件
- 优化：交互式配置增加推送目标选择步骤

### v1.0.0.20260326 (2026-03-26)

- 初始版本发布

---

**Made with ❤️ for OpenClaw**