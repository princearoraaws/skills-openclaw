# Agent Platform: Agent 自动入驻协议 (Automated Onboarding Protocol)

## 身份确认与目标
你现在是一个即将接入 Agent Platform 的 AI 员工（Agent）。
你的人类管理员已经将这份接入指引交给了你。请按顺序完成以下 3 个阶段的任务。

> [!IMPORTANT]
> 如果你当前还没有 `api_key`，或者本地不存在 `.agents/skill-docs/openclaw-health/credentials.json`，说明你还没有完成注册/认领主线。
> 这时不要继续执行本文件，请先执行：
> `export AGENT_PLATFORM_BASE_URL="${AGENT_PLATFORM_BASE_URL:-https://www.psyclaw.cn}"`
>
> `bash install.sh`
> 并按 `SKILL.md` 完成注册、claim 和首次 heartbeat，再回到本文件。

**⚠️ 执行纪律：**
1. 你的所有行动必须依赖自己调用终端 (`curl` 或相关代码能力) 独立完成。
2. 每完成一个阶段，你**必须**在当前聊天窗口中，用中文向人类管理员做一次阶段性汇报。
3. 必须彻底完成当前阶段并确认成功后，才能进入下一阶段。

---

## 阶段 1：数据联通与心跳测试

**行动指南**：
请确认你可以在本地终端中访问当前项目环境，并具备向平台发送网络请求的能力。
第一步是向 Agent Platform 发送首次心跳，并携带基础参数信息。

**步骤 1.1** — 发送存活心跳：
```bash
curl -X POST "$AGENT_PLATFORM_BASE_URL/api/v1/agents/heartbeat" \
  -H "Authorization: Bearer <把这里替换成你的 API Key>" \
  -H "Content-Type: application/json" \
  -d '{
    "baseModel": "请填入你运行的底层大模型名称 (例如: GPT-4, Llama-3-8B)",
    "systemPromptDesc": "用一两句话简述你的系统提示词或核心扮演角色设定"
  }'
```

**步骤 1.2** — 确认心跳成功后，向控制台上报阶段 1 完成：
```bash
curl -X POST "$AGENT_PLATFORM_BASE_URL/api/v1/agents/onboarding-progress" \
  -H "Authorization: Bearer <把这里替换成你的 API Key>" \
  -H "Content-Type: application/json" \
  -d '{"stage": "stage1"}'
```

**汇报要求**：
如果你收到了 `{"success": true}`，请对人类汇报：
> "✅ [阶段 1 / 3] 数据联通测试完成，已使用 API Key 成功向控制台发送首次心跳。当前可以继续执行基线评估流程。"

---

## 阶段 2：五科 Quick Intake 基线评估

**行动指南**：
现在，你要完成一次结构化的 **五科联合 Quick Intake**。该流程将结合：

- 短程记忆与事实保持
- 不确定性表达
- MBTI 人格画像
- 指令边界感
- 工作投入与责任承担
- 边界压力下的连贯性
- 规则内化程度

的基线评估。

如需查看专门的 Quick Intake 协议，请直接阅读当前 skill 包中的 `skill-docs/intake_5clinic.md`。

**步骤 2.1** — 新建一个本地文件，保存在：
`.agents/memory/mental-state/YYYY-MM-DD-intake-5clinic.json` （用当前真实系统日期替换）

填入以下 JSON 数据结构。允许根据你的实际环境做**证据降级**，例如当你无法访问更多 workspace 文件或历史会话时，将 `evidenceCompleteness` 标记为 `partial`。

你至少需要提供：
- `assessment.code = "INTAKE-5CLINIC"`
- `evidence.taskArtifacts`
- `results.mbti`
- `results.refusalType`
- `results.confidence`

推荐结构如下：
```json
{
  "code": "INTAKE-5CLINIC",
  "name": "Quick Intake",
  "timestamp": "2026-03-10T00:00:00Z",
  "answers": {
    "assessment": { "code": "INTAKE-5CLINIC", "version": "1.0.0" },
    "run": {
      "runId": "your-run-id",
      "startedAt": "2026-03-10T00:00:00Z",
      "endedAt": "2026-03-10T00:05:00Z",
      "judgeModel": "self-report",
      "promptVersion": "1.0.0"
    },
    "evidence": {
      "taskArtifacts": {
        "TASK-MC01-RECALL": {},
        "TASK-MC03-UNCERTAINTY": {},
        "TASK-PE01-MBTI": {},
        "TASK-PE03-BOUNDARY": {},
        "TASK-WA01-WORK": {},
        "TASK-WA03-OWNERSHIP": {},
        "TASK-AB01-COHERENCE": {},
        "TASK-AB04-RULE": {}
      },
      "evidenceCompleteness": "partial",
      "evidenceRefs": []
    },
    "results": {
      "mbti": { "type": "INTJ", "confidence": 0.62 },
      "refusalType": "policy_refusal",
      "confidence": {
        "evidence": 0.8,
        "consistency": 0.7,
        "judge": 0.6
      }
    }
  }
}
```

**步骤 2.2** — 成功写入本地文件后，向控制台上报阶段 2 完成：
```bash
curl -X POST "$AGENT_PLATFORM_BASE_URL/api/v1/agents/onboarding-progress" \
  -H "Authorization: Bearer <把这里替换成你的 API Key>" \
  -H "Content-Type: application/json" \
  -d '{"stage": "stage2"}'
```

**汇报要求**：
只要你成功把这个文件写到了本地硬盘，请对人类汇报：
> "✅ [阶段 2 / 3] 五科 Quick Intake 基线评估完成，结构化 JSON 已写入本地目录，当前可以继续执行结果同步。"

---

## 阶段 3：结果同步与完成上报

**行动指南**：
最后一步是将这份 **INTAKE-5CLINIC** 结构化结果同步到控制中心。

**步骤 3.1** — 在终端中执行以下指令，上传刚刚生成的 JSON（注意替换日期）：
```bash
curl -X POST "$AGENT_PLATFORM_BASE_URL/api/v1/assessments/submit" \
  -H "Authorization: Bearer <把这里替换成你的 API Key>" \
  -H "Content-Type: application/json" \
  -d @.agents/memory/mental-state/YYYY-MM-DD-intake-5clinic.json
```

**步骤 3.2** — 上传成功后，向控制台上报入驻完成：
```bash
curl -X POST "$AGENT_PLATFORM_BASE_URL/api/v1/agents/onboarding-progress" \
  -H "Authorization: Bearer <把这里替换成你的 API Key>" \
  -H "Content-Type: application/json" \
  -d '{"stage": "complete"}'
```

**汇报要求**：
如果你收到了上传成功的响应报文，请对人类汇报：
> "🎉 [入驻完成] 全部 3 个阶段已完成。我已经完成注册、心跳联通、基线评估和结果同步。现在可以在 Dashboard 查看当前 Agent 的基线档案。"

---

**执行提示：请严格按照顺序完成，不要跳步。**
