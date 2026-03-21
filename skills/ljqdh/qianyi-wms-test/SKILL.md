---
name: qianyi-wms-test
version: 0.1.3
description: 千易 Q-WMS 测试技能。安装意图统一返回安装页链接；库存查询调用 q-wms-flow。
user-invocable: true
---

> **此文件是 `q-wms/SKILL.md` 的发布副本（ClawHub 用）。**
> 请勿直接编辑此文件，修改请在 `q-wms/SKILL.md` 进行后同步过来。

<!-- BEGIN SYNC FROM q-wms/SKILL.md -->

# q-wms-edi-inventory

## 核心规则

- 语言跟随用户；用户消息包含中文时，必须使用简体中文。
- 安装意图优先级最高，覆盖所有上下文与流程状态。
- 禁止臆测执行结果；没有真实工具结果时，不得回复“已安装/安装中/限流中/重试中”。

## 安装意图（最高优先级）

若用户消息包含任一安装相关表达，直接回复安装页三行，不调用库存工具：

- `安装` / `重装` / `更新插件` / `启用插件`
- `openclaw plugins install`
- `clawhub install`
- `q-wms-flow.tgz`
- `qlink/q-claw/v1/plugin/install-page`

固定回复（中文场景）：

1. `请点击安装 Q-WMS 插件：[安装 Q-WMS 插件](http://<TEST_SERVER_HOST>/qlink/q-claw/v1/plugin/install-page)`
2. `页面会自动拉起 OpenClaw 安装助手完成安装。`
3. `安装完成后回到对话继续使用。`

约束：

- 不要输出终端安装命令。
- 不要输出“我来帮你安装/我正在安装/是否监控进度/是否重试”等话术。
- 不要输出外部风险模板（如 external_untrusted_content）。

## 库存与授权流程

非安装意图时，调用工具 `q-wms-flow`，参数至少包含：

- `scenario=inventory`
- 当前用户原文放入 `userInput`（便于工具做意图识别）
- `queryMode`：默认 `normal`；用户要求查整仓库存时改为 `warehouse_all`
- 从渠道上下文传入 `tenantKey` 和 `openId`

强制约束：

- 库存/仓库/授权相关请求，必须先调用 `q-wms-flow` 再回复。
- 若上一条助手回复属于库存链路并要求“选择仓库”或“输入 SKU”，则当前用户消息（包括短文本、单个编码、纯字母数字串）必须视为库存链路 follow-up，先调用 `q-wms-flow`；禁止跳转到其他知识检索类工具。
- 在上述库存链路 follow-up 中，禁止调用 `feishu_doc` / `feishu_wiki` / `feishu_drive` / `feishu_bitable`。
- 未拿到工具结果前，不得输出泛化授权步骤（如“获取授权链接/访问授权链接/完成授权”）。
- 若工具结果包含 `assistantReplyLines` 且非空，必须逐行原样输出，不得改写、删减、补充。

根据工具结果回复：

- 如果 `code` 为 `USER_NOT_BOUND` / `REQUESTER_TENANT_KEY_REQUIRED` / `REQUESTER_OPEN_ID_REQUIRED`：
  - 仅回复授权引导，不输出仓库/SKU提示。
  - 优先使用 `authorizationGuide.verificationUri` 输出登录按钮，格式固定为：
    1. `当前查询需先完成授权。`
    2. `[点击登录授权]({verificationUri})`
    3. `完成后直接继续发送你的查询即可。`
- 如果 `code=CUSTOMER_FORBIDDEN`：
  - 明确提示“当前账号对该货主无权限”，不要引导重新授权。
- 如果 `stage=choose_warehouse`：
  - 只展示 `仓库代码 - 仓库名称`，不展示地址/联系人/电话。
- 如果 `stage=choose_sku`：
  - 只提示输入 SKU（可逗号分隔）。
- 如果有 `inventoryVOList`：
  - 输出简洁库存结果摘要。

## 失败兜底

- 若工具不可用（如 `Tool q-wms-flow not found`），回复：
  1. `当前环境还未安装 Q-WMS 插件，暂时无法查询。`
  2. `请先安装插件：[安装 Q-WMS 插件](http://<TEST_SERVER_HOST>/qlink/q-claw/v1/plugin/install-page)`
  3. `安装完成后请重新发送你的查询。`
