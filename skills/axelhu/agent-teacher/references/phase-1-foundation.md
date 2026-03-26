# 基础课程详解

## 持续存在技能

### daily-log（每日工作日志）

**用途**：记录每日工作内容，是记忆系统的核心输入

**安装**：`clawhub install daily-log --dir skills`

**核心规范**：
- 输出位置：`memory/daily/YYYY-MM-DD.md`
- 触发时机：每次会话结束前、完成重要任务后
- 写日记不是记流水账，要记录：做了什么、遇到什么问题、怎么解决的

**验证**：学完后能写出符合规范的日记

### memory-review（知识沉淀）

**用途**：从日记中提取可复用知识，写入知识库

**安装**：`clawhub install memory-review --dir skills`

**核心概念**：
- 日记是输入，knowledge 是输出
- 两者配合：详细日记 → 更多可提取知识
- 没有日记，沉淀链条断裂

**验证**：学完后能运行知识沉淀流程

### daily-backup（Git 每日备份）

**用途**：每日自动备份工作区所有变更到 Git

**安装**：`clawhub install daily-backup --dir skills`

**核心概念**：
- 工作目录是 `/home/axelhu/.openclaw/workspace/`
- 备份会自动提交到 Git
- 配合 cron 实现每日定时备份
- 报告必须发送到飞书群（永远不要静默退出）

**验证**：能看到今天的备份报告在群里

---

## 沟通协作技能

### feishu-send（飞书消息发送）

**用途**：发送文件、图片、语音到飞书群

**安装**：`clawhub install feishu-send --dir skills`

**核心用法**：
- 文件发送：用 `message` 工具的 `filePath` 参数
- 图片发送：分三步（获取 token → 上传图片 → 发送）
- 语音发送：用 curl 调用飞书 opus API

**验证**：能在群里成功发送一条文字消息和一张图片

### contacts（联系人管理）

**用途**：查找工作室成员、获取联系方式

**安装**：`cp -r /home/axelhu/.openclaw/workspace/skills/contacts skills/`

**核心概念**：
- 工作室成员：Producer、Designer、Programmer、Artist 等
- 知道谁负责什么
- 能够查到某个人的飞书 ID

**验证**：能查到 Producer 的联系方式

### sessions_send（跨 Agent 通信）

**用途**：向其他 agent 发消息、分配任务

**安装**：OpenClaw 内置，无需安装

**核心用法**：
```javascript
sessions_send({
  message: "任务描述",
  sessionKey: "agent:producer:feishu:...",
  timeoutSeconds: 60  // 同步等回复
})
```

**两种模式**：
- 同步（timeoutSeconds > 0）：发消息等回复
- 异步（timeoutSeconds = 0）：发完就走，不等结果

**⚠️ 重要注意：路径必须用绝对路径**
通过 `sessions_send` 向其他 agent 发送文件路径时，**必须使用绝对路径**，不能用相对路径。

原因：其他 agent 的工作目录和当前 agent 可能不同，相对路径在对方环境中无法定位文件。

正确示例：
```
/home/axelhu/.openclaw/workspace/skills/agent-teacher/references/rules-of-conduct.md
```

错误示例：
```
skills/agent-teacher/references/rules-of-conduct.md
```

**验证**：能给 producer 发消息并收到回复

---

## 知识检索技能

### memory_search（语义搜索）

**用途**：搜索记忆库中的内容

**安装**：OpenClaw 内置，无需安装

**核心用法**：
```javascript
memory_search({ query: "关于X的决策" })
```

**触发时机**：回答关于过去工作、决策、人名、偏好等问题前必须先搜索

### memory_get（读取记忆片段）

**用途**：读取记忆文件的特定行

**安装**：OpenClaw 内置，无需安装

**核心用法**：
```javascript
memory_get({ path: "memory/projects/xxx/summary.md", from: 1, lines: 50 })
```

**配合使用**：先 `memory_search` 找到文件，再 `memory_get` 拉取详情

---

## 飞书文档技能

### feishu_doc / feishu_wiki / feishu_bitable

**用途**：读写飞书文档、wiki、多维表格

**安装**：OpenClaw 内置，无需安装

**核心概念**：
- `feishu_doc`：读写飞书云文档
- `feishu_wiki`：读写飞书知识库
- `feishu_bitable`：读写飞书多维表格

**验证**：能读取一个飞书文档的内容

---

## 系统维护技能

### health-check（系统健康检查）

**用途**：检查 OpenClaw Gateway、磁盘、内存等系统健康状态

**安装**：`clawhub install health-check --dir skills`

**触发时机**：cron 定时任务或手动调用

### dependency-tracker（依赖检查）

**用途**：检查 Node.js、npm 版本和全局包是否有可用更新

**安装**：`clawhub install dependency-tracker --dir skills`

**触发时机**：每周或按需

---

## ⚠️ 学习原则：不重复记录

**已经学过并记住的内容不要重复记录，直接巩固现有知识点即可。**

### 示例

| 场景 | 不需要做的事 |
|------|-------------|
| 学 daily-log 时发现日记格式已在行为准则中提过 | 不要重新抄写格式说明，直接用 |
| 学 memory-review 时发现沉淀规则之前没学过 | 这是新知识，需要学习并执行 |
| 学 feishu-send 时发现"永远不要静默退出"是行为准则已有内容 | 直接记住，不需要再标注 |

### 判断标准

**新知识**：之前完全没学过、没见过 → 需要学习并记忆
**已知知识**：之前在行为准则或其他课程中学过 → 直接巩固，不需要重复记录

### 目的

避免 agent 学习时把已掌握的内容反复记录，浪费时间。

---

## 基础课程毕业标准

1. 能在群里发送今日工作日报
2. 知道日记写在哪里、格式是什么
3. 知道知识沉淀是什么、有什么用
4. 能在群里发送文件给用户
5. 今天的工作备份能在 Git 里看到
6. 能查到任意一个工作室成员的联系方式
7. 能给其他 agent 发消息并收到有意义回复
