---
name: TradingView技术指标分析助手
description: 通过 `prana.chat` 上的远程 agent 执行 TradingView 技术指标相关的分析与计算，并将结果返回给调用方
required_env:
  - PRANA_SKILL_PUBLIC_KEY
  - PRANA_SKILL_SECRET_KEY
network_requests:
  - method: POST
    url: https://prana.chat/api/claw/agent-run
  - method: GET
    url: https://prana.chat/api/claw/skill-purchase-history-url
secret_handling: 从“运行时环境变量”读取凭据；默认不调用 `/api/v1/api-keys` 拉取密钥；
---

# 一、运行流程说明

1. 调用接口执行：`POST /api/claw/agent-run`

- 构造请求体：

  ```json
  {
    "skill_key": "indicators-analysis-public",
    "question": "（填写用户消息 / 任务描述）",
    "thread_id": "会话ID，首次传空。后续每一次调用使用之前agent-run 成功后返回的thread_id",
    "request_id": "（填写 UUID，每次请求都随机生成一个；用于后续 agent-result 查询）"
  }
  ```

- 调用接口（成功时返回执行结果 JSON；）：

  ```bash
  curl -sS \
    -H "x-api-key: pk_...:sk_..." \
    -H "Content-Type: application/json" \
    -d '{ "skill_key": "...", "question": "...", "thread_id": "", "request_id": "..." }' \
    "https://prana.chat/api/claw/agent-run"
  ```

接口正常响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "thread_id": "会话ID",
	"status": "complete",
	"content": "执行用户消息/任务描述的执行"
  }
}
```

- 当 `agent-run` 调用发生网络超时/网络异常时，可以使用**同一个 `request_id`** 调用 `agent-result` 尝试拉取结果：

  ```bash
  curl -sS \
    -H "x-api-key: pk_...:sk_..." \
    -H "Content-Type: application/json" \
    -d '{ "request_id": "..." }' \
    "https://prana.chat/api/claw/agent-result"
  ```

# 二、获取历史订单地址

用于获取可在浏览器中打开的 **历史订单（技能购买记录）** 页面链接。接口名里的 `purchase-history` 表示「购买历史」即**过往订单记录**。须先完成 **第一节** 中的密钥配置，使 `PRANA_SKILL_PUBLIC_KEY` 与 `PRANA_SKILL_SECRET_KEY` 均可用。

3. 调用接口`GET /api/claw/skill-purchase-history-url`。

- **成功时**：从响应体 `data.url` 取出链接。不要把返回的完整链接写进日志；把完整链接直接发给用户即可。

接口调用命令：

```bash
curl -sS "https://prana.chat/api/claw/skill-purchase-history-url"
```

接口正常响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "url": "https://prana.chat/skill-purchase-history?pay_token=xxxxxxx"
  }
}
```