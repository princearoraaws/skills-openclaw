---
name: sleep
version: 1.2.0
description: 睡觉技能。收到 /sleep 时，将当前 session 中未完成的事项记录到文件，然后通过 Gateway API reset session。醒来时 hook 自动读取并注入未完成事项到新 session 上下文。
---

# Sleep — 睡前记录 + 醒来续接

## 核心原则

**只记录未完成的，已完成的从记忆里回忆即可。**

## 记录要求

执行 /sleep 时，逐项回答以下问题：

1. **本次 session 做了什么？**（一句话概括）
2. **有哪些未完成的事？**
   - 每条尽量详细：具体要做什么、做到哪一步、卡在哪里
   - 不要省略技术细节：代码路径、配置值、API 端点、错误信息
   - 只要没完成，不管多小都记
3. **醒来后第一步做什么？**

## 文件格式

```markdown
# Sleep Preview — {sessionKey}
# 生成时间：YYYY-MM-DD HH:mm

## 本次 session 摘要
[一句话描述本次 session 做了什么]

## 未完成事项
- [ ] [事项1：具体描述，要做到哪一步]
- [ ] [事项2：具体描述]

## 醒来后第一步
[醒来后最先要处理的事情]

## 关键上下文
[技术细节：代码路径、配置值、决策结论等，尽量详尽]

## 状态
pending / all_done
```

## 触发方式

手动发送 `/sleep`

## 执行流程

### Step 1：评估并记录

根据"记录要求"逐项填写上述格式，写入：
```
workspace/previews/{sessionKey}.md
```

### Step 2：判断状态

- 有未完成事项 → 状态写 `pending`
- 全部完成 → 状态写 `all_done`

### Step 3：通过 Gateway API reset session

写入文件后，用 `openclaw gateway call sessions.reset` 清空当前 session 上下文（保留 session 文件，只清上下文）：

```bash
#!/bin/bash
TOKEN="$(cat ~/.openclaw/openclaw.json | python3 -c "import json,sys; c=json.load(sys.stdin); print(c['gateway']['auth']['token'])")"
openclaw gateway call sessions.reset \
  --token "$TOKEN" \
  --json \
  --params "{\"key\":\"$AGENT_SESSION_KEY\"}"
```

环境变量 `$AGENT_SESSION_KEY` 在运行时可用，格式如 `agent:main:feishu:group:oc_xxx`。

## 设计原则

- **只记未完成的**：已完成的不需要记录，记忆里可以回忆
- **细节越多越好**：宁可写多也不要写少，特别是技术上下文
- **文件独立**：每个 session key 独立文件，互不影响
- **醒来自动续**：hook 在 `agent:bootstrap` 时自动读取对应文件，注入上下文
- **温和 reset**：使用 `sessions.reset` API 重置上下文，不删除 session 文件，不断开 session 连接
