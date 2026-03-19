---
name: memory-manager
description: 记忆管理技能 - 自动化管理五层记忆架构 (hourly/daily/weekly/monthly/yearly)
version: 2.0.0
author: 前端 ⚡
---

# Memory Manager Skill - 记忆管理技能

**版本**: 2.0  
**创建日期**: 2026-03-11  
**更新日期**: 2026-03-19  
**作者**: 前端 ⚡

---

## 📋 技能描述

自动化管理五层记忆架构（hourly/daily/weekly/monthly/yearly）的定时同步任务。

---

## 🎯 功能清单

| 任务 | 频率 | 说明 |
|------|------|------|
| **记忆及时写入** | 10 分钟 | 检查并写入重要信息到 daily 文件 |
| **记忆同步 - Hourly** | 每小时 | 更新 hourly 记忆文件 |
| **记忆归档 - Daily** | 每天 23:00 | 提炼 hourly 到 daily |
| **记忆总结 - Weekly** | 每周日 22:00 | 提炼 daily 到 weekly/MEMORY.md |
| **记忆总结 - Monthly** | 每月末 22:00 | 提炼 weekly 到 monthly |
| **记忆总结 - Yearly** | 每年 12/31 21:00 | 提炼 monthly 到 yearly |

---

## 📂 文件结构

```
skills/memory-manager/
├── SKILL.md                      # 本文件
├── scripts/
│   ├── sync-hourly.sh            # 每小时同步脚本
│   ├── sync-daily.sh             # 每日归档脚本
│   ├── sync-weekly.sh            # 每周总结脚本
│   ├── sync-monthly.sh           # 每月总结脚本
│   ├── sync-yearly.sh            # 每年总结脚本
│   └── write-timely.sh           # 及时写入脚本
└── config.json                   # 配置文件 (可选)
```

---

## 🔧 安装/启用

### 方法 1: 手动注册 cron 任务

```bash
# 1. 记忆及时写入 (10 分钟)
openclaw cron add --name "记忆及时写入" \
  --schedule '{"kind":"every","everyMs":600000}' \
  --payload '{"kind":"systemEvent","text":"📝 记忆及时写入检查..."}' \
  --session-target main

# 2. 记忆同步 - Hourly (每小时)
openclaw cron add --name "记忆同步 - Hourly" \
  --schedule '{"kind":"every","everyMs":3600000}' \
  --payload '{"kind":"systemEvent","text":"🕐 每小时记忆同步时间！..."}' \
  --session-target main

# 3. 记忆归档 - Daily (每天 23:00)
openclaw cron add --name "记忆归档 - Daily" \
  --schedule '{"kind":"cron","expr":"0 23 * * *","tz":"Asia/Shanghai"}' \
  --payload '{"kind":"systemEvent","text":"🌙 每日记忆归档时间！..."}' \
  --session-target main

# 4. 记忆总结 - Weekly (每周日 22:00)
openclaw cron add --name "记忆总结 - Weekly" \
  --schedule '{"kind":"cron","expr":"0 22 * * 0","tz":"Asia/Shanghai"}' \
  --payload '{"kind":"systemEvent","text":"📅 每周记忆总结时间！..."}' \
  --session-target main

# 5. 记忆总结 - Monthly (每月末 22:00)
openclaw cron add --name "记忆总结 - Monthly" \
  --schedule '{"kind":"cron","expr":"0 22 L * *","tz":"Asia/Shanghai"}' \
  --payload '{"kind":"systemEvent","text":"📆 每月记忆总结时间！..."}' \
  --session-target main

# 6. 记忆总结 - Yearly (每年 12/31 21:00)
openclaw cron add --name "记忆总结 - Yearly" \
  --schedule '{"kind":"cron","expr":"0 21 31 12 *","tz":"Asia/Shanghai"}' \
  --payload '{"kind":"systemEvent","text":"🎆 年度记忆总结时间！..."}' \
  --session-target main
```

### 方法 2: 使用技能脚本

```bash
cd ~/.openclaw/workspace/skills/memory-manager
bash scripts/install.sh
```

---

## 📝 任务详情

### 1️⃣ 记忆及时写入 (10 分钟)

**触发**: 每 10 分钟  
**行为**:
1. 回顾最近 10 分钟的对话
2. 识别重要信息：
   - 新决策
   - 配置变更
   - 问题解决
   - 技术笔记
3. 写入 `memory/daily/YYYY-MM-DD.md`
4. 更新时间戳

**静默规则**:
- ✅ 正常 → `NO_REPLY`
- ⚠️ 异常 → 输出提醒

---

### 2️⃣ 记忆同步 - Hourly (每小时)

**触发**: 每小时整点  
**行为**:
1. 检查 `memory/hourly/YYYY-MM-DD.md` 是否存在
2. 添加新的小时段落
3. 记录：
   - 完成事项
   - 技术笔记
   - 状态
4. 更新时间戳

**输出**: 更新 hourly 文件

---

### 3️⃣ 记忆归档 - Daily (每天 23:00)

**触发**: 每天 23:00 (Asia/Shanghai)  
**行为**:
1. 回顾当天所有 hourly 记忆
2. 提炼重要内容到 daily 文件
3. 记录：
   - 今日完成
   - 重要决策
   - 技术笔记
   - 问题与解决
4. 标记值得长期保存的内容

**输出**: 更新 daily 文件

---

### 4️⃣ 记忆总结 - Weekly (每周日 22:00)

**触发**: 每周日 22:00 (Asia/Shanghai)  
**行为**:
1. 回顾本周所有 daily 记忆文件
2. 提炼核心知识、最佳实践、模式识别
3. 更新 `MEMORY.md` 长期记忆文件
4. 更新 `memory/weekly/YYYY-Www.md`
5. 记录：
   - 本周目标完成情况
   - 项目进展
   - 核心知识沉淀
6. 制定下周计划

**输出**: 更新 MEMORY.md 和 weekly 文件

---

### 5️⃣ 记忆总结 - Monthly (每月末 22:00)

**触发**: 每月最后一天 22:00 (Asia/Shanghai)  
**行为**:
1. 回顾本月所有 weekly 记忆文件 (`memory/weekly/`)
2. 提炼月度核心成果、重要决策、技术沉淀
3. 创建/更新 `memory/monthly/YYYY-MM.md`
4. 记录：
   - 本月目标完成情况
   - 重大项目进展与里程碑
   - 核心知识与技能提升
   - 问题与经验教训
   - 下月计划/展望
5. 将高价值内容同步到 `MEMORY.md`

**输出**: 更新 monthly 文件和 MEMORY.md

---

### 6️⃣ 记忆总结 - Yearly (每年 12/31 21:00)

**触发**: 每年 12月31日 21:00 (Asia/Shanghai)  
**行为**:
1. 回顾本年所有 monthly 记忆文件 (`memory/monthly/`)
2. 提炼年度核心成果、重大决策、技术演进
3. 创建/更新 `memory/yearly/YYYY.md`
4. 记录：
   - 年度目标完成情况
   - 重大项目成果与里程碑
   - 核心技能成长与知识图谱
   - 重要经验教训
   - 下年规划/展望
5. 精选最高价值内容更新到 `MEMORY.md`

**输出**: 更新 yearly 文件和 MEMORY.md

---

## 🎛️ 配置选项

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MEMORY_WORKSPACE` | `~/.openclaw/workspace` | 工作区路径 |
| `MEMORY_DAILY_PATH` | `memory/daily` | daily 文件目录 |
| `MEMORY_HOURLY_PATH` | `memory/hourly` | hourly 文件目录 |
| `MEMORY_WEEKLY_PATH` | `memory/weekly` | weekly 文件目录 |
| `MEMORY_MONTHLY_PATH` | `memory/monthly` | monthly 文件目录 |
| `MEMORY_YEARLY_PATH` | `memory/yearly` | yearly 文件目录 |
| `MEMORY_LONGTERM_FILE` | `MEMORY.md` | 长期记忆文件 |

### 静默模式配置

在 cron 任务的 `delivery` 中设置：

```json
{
  "delivery": {
    "mode": "none"
  }
}
```

或添加静默指令到 payload text。

---

## 🔍 诊断命令

```bash
# 查看所有记忆管理任务
openclaw cron list | grep -E "记忆|memory"

# 查看任务运行历史
openclaw cron runs --jobId <job-id>

# 手动触发 hourly 同步
openclaw cron run --jobId <hourly-job-id>

# 检查记忆文件
ls -la ~/.openclaw/workspace/memory/
```

---

## 📊 记忆架构

```
五层记忆架构:

┌─────────────────────────────────────┐
│  Yearly (每年 12/31 21:00)          │
│  memory/yearly/YYYY.md              │
│  MEMORY.md (长期记忆)               │
└─────────────────┬───────────────────┘
                  │ 提炼
┌─────────────────▼───────────────────┐
│  Monthly (每月末 22:00)             │
│  memory/monthly/YYYY-MM.md          │
└─────────────────┬───────────────────┘
                  │ 提炼
┌─────────────────▼───────────────────┐
│  Weekly (每周日 22:00)              │
│  memory/weekly/YYYY-Www.md          │
└─────────────────┬───────────────────┘
                  │ 提炼
┌─────────────────▼───────────────────┐
│  Daily (每天 23:00)                 │
│  memory/daily/YYYY-MM-DD.md         │
└─────────────────┬───────────────────┘
                  │ 提炼
┌─────────────────▼───────────────────┐
│  Hourly (每小时)                    │
│  memory/hourly/YYYY-MM-DD.md        │
└─────────────────┬───────────────────┘
                  │ 写入
┌─────────────────▼───────────────────┐
│  及时写入 (10 分钟)                  │
│  从会话→daily                       │
└─────────────────────────────────────┘
```

---

## ⚠️ 注意事项

1. **时区设置**: 所有 cron 任务使用 `Asia/Shanghai` 时区
2. **静默模式**: 日常任务默认静默，仅异常时提醒
3. **文件权限**: 确保 memory 目录可写
4. **时间戳**: 每次更新后同步更新时间戳

---

## 📝 更新日志

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-03-11 | 1.0 | 初始版本，封装 4 个记忆管理任务 (三层架构) |
| 2026-03-19 | 2.0 | 新增 Monthly + Yearly 层，升级为五层记忆架构 |

---

*技能位置：`~/.openclaw/workspace/skills/memory-manager/`*
