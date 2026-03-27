# Sleep Skill — 安装说明

## 依赖文件

所有文件已就绪，直接可用：

```
workspace/
├── skills/sleep/
│   ├── SKILL.md
│   └── references/
│       ├── implementation.md     # 本文件
│       └── hook-template/       # ✅ hook 模板（可直接拷贝）
│           ├── HOOK.md
│           └── handler.ts
└── previews/                   # ✅ preview 文件目录（运行时创建）
```

## 快速安装（复制给其他 agent）

其他 agent 只需要两步：

### 第一步：复制 hook 文件

把 `skills/sleep/references/hook-template/` 下的两个文件复制到：

```
~/.openclaw/workspace/hooks/session-sleep-wake/
  ├── HOOK.md       # 从模板复制
  └── handler.ts    # 从模板复制
```

```bash
mkdir -p ~/.openclaw/workspace/hooks/session-sleep-wake
cp skills/sleep/references/hook-template/HOOK.md ~/.openclaw/workspace/hooks/session-sleep-wake/
cp skills/sleep/references/hook-template/handler.ts ~/.openclaw/workspace/hooks/session-sleep-wake/
```

### 第二步：启用 hook + 重启 Gateway

```bash
openclaw hooks enable session-sleep-wake
openclaw gateway restart
```

### 第三步：验证

```bash
openclaw hooks list
# 应显示 🌙 session-sleep-wake 状态为 ready
```

## 验证方式

1. 在任意 session 发 `/sleep`
2. 检查 `workspace/previews/` 下是否生成了对应 session key 的 .md 文件
3. 再发任意消息，观察是否在开头看到 "🌙 检测到上次 session 有未完成事项"

## 触发方式

- `/sleep` — 在想睡觉的 session 里发
- 每个 session 独立文件，互不影响

## 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| hook 未显示 ready | 没重启 Gateway | 执行 `openclaw gateway restart` |
| 文件没生成 | /sleep 执行失败 | 检查 skill 是否被正确加载 |
| 醒来没注入 | preview 文件不存在或状态=all_done | 检查文件内容和状态字段 |
