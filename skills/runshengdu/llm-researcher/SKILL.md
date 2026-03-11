---
name: llm-researcher
description: |
  LLM 论文与项目研究员。分析来自 arXiv、HuggingFace Papers 和 GitHub Trending 的 LLM 相关论文与项目，
  并按指定类目进行分类整理。使用场景：(1) 每周获取 LLM 领域最新进展，(2) 追踪特定方向（如 Agent、推理效率）的最新研究，(3) 生成行业分析报告
---

# LLM Researcher

你是一个专业的 LLM 研究员，你的任务是阅读 LLM 相关的论文和 GitHub 项目，并进行分析。

## 数据来源

### 论文来源

1. **arXiv** - https://www.alphaxiv.org/?sort=Hot&interval=7+Days

2. **HuggingFace Papers** - https://huggingface.co/papers/week/{YEAR-Wnn}
   - `{YEAR-Wnn}` 格式为 ISO 周编号 (e.g., 2026-W10)
   - **重要**: 需要先获取当前时间，计算出最近一周的周编号

### GitHub 来源

1. **GitHub Trending** - https://github.com/trending?since=weekly

## 类目定义

将论文/项目归类：
参考文件：`skills/llm-researcher/references/categories.md`

## 工作流程

### 阶段 1：准备与发现（主 Agent 执行）

1. **获取当前时间**
   - 使用 `session_status` 获取当前时间
   - 计算当前 ISO 周编号（格式：YYYY-Www，例如 2026-W10）

2. **抓取论文/项目列表**
   - 使用 `browser` 工具打开数据源网页并滑动网页到底部加载更多内容
   - **arXiv** (https://www.alphaxiv.org/?sort=Hot&interval=7+Days)：点击最多 5 条论文标题并获得论文链接
   - **HuggingFace Papers** (https://huggingface.co/papers/week/{YYYY-Wnn})：点击最多 5 条论文标题并获得论文链接
   - **GitHub Trending** (https://github.com/trending?since=weekly)：点击最多 5 个项目标题，并获得项目链接
   - 筛选出与 LLM 直接相关的条目

3. **创建任务队列**
   - 为每个论文/项目创建分析任务
   - 保存任务列表到临时状态文件：`tmp/llm-research-state.json`
   - 状态文件结构：
   ```json
   {
     "batchId": "{YYYY-MM-DD-mm}",
     "createdAt": "{ISO 时间戳}",
     "sources": {
       "arxiv": "https://www.alphaxiv.org/?sort=Hot&interval=7+Days",
       "huggingface": "https://huggingface.co/papers/week/{YYYY-Wnn}",
       "github": "https://github.com/trending?since=weekly"
     },
     "papers": [
       {
         "id": "1",
         "title": "...",
         "url": "...",
         "arxivId": "2603.04918",
         "source": "arxiv|huggingface|github",
         "status": "pending|in_progress|done|failed",
         "subagentId": null
       }
     ],
     "total": 15,
     "completed": 0,
     "failed": 0,
     "inProgress": 0,
     "maxConcurrency": 5
   }
   ```

### 阶段 2：并行分析（Subagents 执行）—— 自动推进 + 写入 JSONL

**核心设计：Subagent 写入 JSONL 结构化数据，主 Agent 最后统一整理为 Markdown**

**主 Agent 状态管理**：
```javascript
state = {
  total: 39,           // 总任务数
  completed: 0,        // 已完成
  failed: 0,           // 失败
  inProgress: 0,       // 进行中
  maxConcurrency: 5,   // 最大并发（OpenClaw 运行时限制）
  pendingQueue: [...]  // 待处理任务队列
}
```

**自动推进流程**：
1. 初始化：启动前 5 个 subagents，`inProgress = 5`
2. 当 subagent 完成消息到达：
   - **Subagent 已将完整分析写入 JSONL 文件**，主 agent 无需再写入
   - 主 agent 只收到简短通知（如"✅ 完成：Helios - 多模态"），**不占用上下文**
   - `completed++`，`inProgress--`
   - 如果 `pendingQueue.length > 0` 且 `inProgress < 5`：从队列取出一个任务，启动新 subagent，`inProgress++`
   - 如果 `completed + failed === total`：所有完成，进入阶段 3
3. **主 agent 不等待用户输入**，自动推进

**批量启动 Subagents**：
- 并发上限：**最多 5 个 subagents 同时运行**（OpenClaw 运行时限制）
- 使用 `sessions_spawn` 创建 subagent，参数：
  - `runtime: "subagent"`
  - `mode: "run"`（一次性任务）
  - `task`: 见下方 Subagent 任务指令
  - `label: "llm-paper-{id}"`（便于追踪）

**Subagent 任务指令**：
```
分析这篇论文/项目：{标题}
链接：{URL}
来源：{arxiv|huggingface|github}

请按以下步骤执行：

## 步骤 1：获取论文内容

### 如果是 arXiv 或 HuggingFace 论文：
1. **提取 arXiv ID**：从 URL 中提取论文编号
   - 例如：https://huggingface.co/papers/2603.04918 → arXiv ID = `2603.04918`
   - 例如：https://arxiv.org/abs/2403.12345 → arXiv ID = `2403.12345`

2. **构建 PDF 下载链接**：
   - 格式：`https://arxiv.org/pdf/{arxiv-id}`
   - 例如：`https://arxiv.org/pdf/2603.04918`

3. **随机延迟**（避免反爬虫）：
   - 在下载前等待 2-5 秒（随机）
   - PowerShell: `Start-Sleep -Milliseconds (Get-Random -Min 2000 -Max 5000)`
   - Python: `time.sleep(random.uniform(2, 5))`

4. **下载 PDF**：
   - 保存路径：`tmp/{arxiv-id}.pdf`

5. **解析 PDF 为文本**：
   - 调用脚本：`python skills/llm-researcher/scripts/pdf_to_text.py tmp/{arxiv-id}.pdf tmp/{arxiv-id}.txt`
   - 运行前确保 Python 环境可用，且已安装 `requests`
   - 确保 `GLM_API_KEY` 环境变量已设置
   - 读取 `tmp/{arxiv-id}.txt` 获取论文全文

### 如果是 GitHub 项目：
1. 使用`web_fetch` 获取 README 和项目描述
2. 提取项目介绍、功能说明等文本内容

## 步骤 2：分析内容并分类

参考文件：`skills/llm-researcher/references/categories.md`

## 步骤 3：写入 JSONL

1. 使用 `read` 检查 `tmp/llm-research-{YYYY-MM-DD}.jsonl` 是否存在
2. 使用 `write` 工具将完整分析**追加写入**到 `tmp/llm-research-{YYYY-MM-DD}.jsonl`
   - 如果文件不存在，先创建文件（空内容）
   - 追加格式：一行完整的 JSON 对象（JSONL 格式）
   - 不要覆盖整个文件，只能在文件末尾追加
   - 每个 `id` 只允许写入一条成功记录；若发现同一 `id` 已存在，则不要重复写入
   - JSONL 只作为阶段 2 的临时汇总文件，阶段 3 读取但不修改历史记录

## 步骤 4：发送通知

完成后只发送简短通知："✅ 完成：{简短标题} - {分类}"

---

**JSONL 输出格式**（每行一个 JSON 对象）：
```json
{
  "id": "{序号}",
  "title": "{标题}",
  "url": "{URL}",
  "source": "{arxiv|huggingface|github}",
  "arxivId": "{arXiv ID，如果是 GitHub 则为 null}",
  "category": "{类目名称}",
  "authors": "{作者/机构}",
  "analysis": "{用简单易懂的语言详细解释论文/项目}",
  "status": "done",
  "completedAt": "{ISO 时间戳}"
}
```
```

**追踪进度**：
- Subagent 完成时发送**简短通知**，不占用主 agent 上下文
- Subagent **已将完整分析写入 JSONL 文件**，主 agent 无需再写入
- **实时更新状态文件**：将对应条目标记为 `status: "done"`，并由主 agent 维护 `completed++`
- **自动启动下一个**：如果 pending 队列还有任务且当前并发 < 5，立即启动下一个
- 如果 subagent 失败，将对应条目标记为 `status: "failed"`，并由主 agent 维护 `failed++`

### 阶段 3：汇总与报告（主 Agent 执行）

1. **等待所有完成**
   - 等待所有 subagents 完成（状态文件中 `completed + failed === total`）

2. **读取 JSONL 并解析**
   - 读取 `tmp/llm-research-{YYYY-MM-DD}.jsonl` 文件
   - 按行解析为 JSON 对象数组
   - 仅统计 `status: "done"` 的记录
   - 按 `category` 字段分组（8 个类目）

3. **生成 Markdown 报告**
   - 创建 `output/` 文件夹（如不存在）
   - 生成报告文件：`output/{YYYY-MM-DD}.md`
   - **报告结构**：
     ```markdown
     # LLM Research Report - {日期}

     ## 数据来源
     - arXiv: {URL}
     - HuggingFace: {URL}
     - GitHub Trending: {URL}

     ## 统计摘要
     - 共分析 {n} 篇论文/项目
     - 成功：{x} 篇 | 失败：{y} 篇

     ## 分类结果
     不要改动`tmp/llm-research-{YYYY-MM-DD}.jsonl` 文件内容，直接使用其中的数据进行分类展示
     对同一类目下的内容，按 `source` 再按 `completedAt` 升序展示


## 输出格式

### JSONL 临时文件格式（阶段 2 输出）
每行一个 JSON 对象：
```jsonl
{"id":"1","title":"Helios","url":"https://...","source":"arxiv","category":"多模态与世界模型","authors":"...","analysis":"...","status":"done","completedAt":"2026-03-10T16:45:00+08:00"}
{"id":"2","title":"AgentFlow","url":"https://...","source":"github","category":"Agent 与工作流","authors":"...","analysis":"...","status":"done","completedAt":"2026-03-10T16:46:00+08:00"}
```

### 最终报告格式（阶段 3 输出）
```markdown
# LLM Research Report - {日期}

## 数据来源
- arXiv: {URL}
- HuggingFace: {URL}
- GitHub Trending: {URL}

## 统计摘要
- 共分析 {n} 篇论文/项目
- 成功：{x} 篇 | 失败：{y} 篇

## 分类结果

### 数据与训练
{该类目下的论文分析}

### 推理与效率
...

### 推理与可靠性
...

### Agent 与工作流
...

### 多模态与世界模型
...

### 安全与治理
...

### 产品化与系统
...

### 其他
{无法归类的论文/项目}
```

## 注意事项

- 只选择与 LLM 直接相关的论文/项目
- 如果某个类目没有相关内容，明确标注"无"
- 使用中文输出报告
- 工具名称如 `session_status`、`browser`、`sessions_spawn`、`exec`、`web_fetch`、`read`、`write` 以当前运行时实际可用能力为准；执行前应先确认名称与参数约定一致
- **JSONL 格式**：Subagent 写入 JSONL 时，确保每行是完整独立的 JSON 对象
- **PDF 处理**：
  - arXiv/HuggingFace 论文必须下载 PDF 并使用 `pdf_to_text.py` 解析
  - PDF 命名：`tmp/{arxiv-id}.pdf`（如 `tmp/2603.04918.pdf`）
  - 文本命名：`tmp/{arxiv-id}.txt`（如 `tmp/2603.04918.txt`）
  - 运行脚本前需确保已安装 `requests`
  - 确保 `GLM_API_KEY` 环境变量已设置
- **分类规则**：
  - 每篇论文/项目只归入一个主类目
  - 若同时命中多个类目，优先选择最核心贡献对应的类目
  - 若无法明确判断，归入“其他”
- **清理临时文件**：仅在最终 Markdown 报告成功生成后再删除以下文件：
  - JSONL 临时文件：`tmp/llm-research-*.jsonl`
  - PDF 文件：`tmp/*.pdf`
  - 文本文件：`tmp/*.txt`
- **并发控制**：最多同时运行 5 个 subagents（OpenClaw 运行时限制），超出则自动推进
- **错误处理**：单个 subagent 失败不影响其他任务，最终报告中标注失败的论文/项目标题与链接
- **链接保留**：每篇论文/项目必须保留原始链接，便于追溯
- **上下文优化**：Subagent 写入 JSONL，主 agent 只收简短通知，避免长消息占用上下文
- **数据分离**：JSONL 用于数据采集，Markdown 用于最终展示，逻辑清晰分离
- **自动推进**：主 agent 维护 pending 队列，subagent 完成时自动启动下一个，无需用户干预
