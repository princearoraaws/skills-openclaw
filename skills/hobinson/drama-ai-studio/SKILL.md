---
name: DramaAIStudio
description: 本技能通过调用灵伴智能的AI影视工场（DramaAI）平台的多项能力，辅助AI短剧创作者更方便地参与创作，具体包括：项目的创建与管理，剧本的上传与自动分析，资产（角色、场景、道具）的智能提取与图像生成，分镜脚本生成与管理、分镜视频生成等
version: 1.0.0
---

# DramaAIStudio（灵伴智能AI影视工场）

本技能封装了灵伴智能AI影视工场（DramaAIStudio）平台提供的多项 HTTP API，帮助用户在对话中完成：

- **剧目（项目）管理**（§4）：获取剧目列表、创建剧目、获取单个剧目详情；获取剧目统计信息；获取/更新项目默认风格配置
- **剧本管理与资产分析**（§5）：获取剧本集列表、按集上传剧本、按集读取剧本内容、按集删除剧本；剧本资产智能分析，从剧本抽取人物/场景/道具资产并写入资产库
- **资产管理**（§6）：按类型/集数/名称过滤资产列表、创建资产、获取/更新单个资产；辅助生成资产提示词；基于参考图与提示词生成资产图像
- **分镜脚本管理**（§7）：按集读取分镜脚本、分析生成分镜脚本；查询镜头详情；为镜头关联资产；生成/优化镜头提示词；删除镜头
- **分镜视频生成**（§8）：创建/查询分镜视频生成任务

当用户提到「列出所有剧目（项目）」「创建剧目（项目）」「查询剧目（项目）统计信息」「短剧（项目）风格配置」「上传/读取剧本」「剧本分析」「创建资产」「更新资产」「资产列表」「查看资产详情」「生成资产提示词」「生成资产图像」「查看/分析分镜」「生成/优化镜头提示词」「生成分镜视频」等需求时，可使用本技能文档中列出的对应 API。

---

## 1. 本技能的使用方式

- 技能名称：`DramaAIStudio`
- 所有接口统一通过 HTTP 调用：
  - 基础域名示例：`https://idrama.lingban.cn/`
  - 对外网关统一前缀：`/openapi`
  - 最终访问路径形如：`https://idrama.lingban.cn/openapi/drama/...`

智能体需要选择一个支持 HTTP 的工具（如 `http_request` 或 `bash`）发起请求，并在 Header 中附带认证信息。

---

## 2. 认证

### 2.1 在 iDrama API令牌获取页面获取 Token

1. 引导用户在浏览器中打开：`https://idrama.lingban.cn/api-token`。
2. 提示用户在该页面完成登录（如果尚未登录）。
3. 登录成功后，在该页面上获取专用于 OpenClaw 的访问 Token（页面会显示一串 Token，如 `xxxx...`）。
4. 让用户将该 Token 复制并粘贴回对话中，作为后续所有接口调用的认证凭据。

请求头中携带：

```text
Authorization: Bearer <从 idrama API令牌获取页面复制的 token>
```

### 2.2 通过iDrama的账号和密码获取 Token

- 接口：`POST /openapi/uaa/oauth/token`
- 内容类型：`application/x-www-form-urlencoded`

请求参数：

| 字段       | 位置 | 必填 | 说明     |
|------------|------|------|----------|
| `username` | form | 是   | 用户名   |
| `password` | form | 是   | 登录密码 |

成功响应示例（HTTP 200）：

```json
{
  "code": 1,
  "msg": "登录成功",
  "data": {
    "access_token": "xxxx...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

失败示例（认证失败，HTTP 200 但 `code=-1`）：

```json
{
  "code": -1,
  "msg": "用户名或密码错误"
}
```

拿到 `access_token` 后，在所有需要鉴权的接口请求头中统一携带：

```text
Authorization: Bearer <access_token>
```

---

## 3. 推荐业务流程总览

整体业务围绕“剧目 → 剧本 → 资产 -> 分镜脚本 -> 分镜视频”的闭环，具体用法见 §8 实践案例。

```text
1. 登录或从 iDrama 页面获取 Token（§2）
2. 创建剧目（§4.2）
3. 查看剧目统计与风格配置（§4.8、§4.11/4.12）
4. 上传剧本、查看剧集列表、按剧集读取或删除（§5）
5. 按剧集智能分析与提取各类资产（§5.5）
6. 查看资产列表、按需创建资产（§6）
7. 按需辅助生成资产提示词（§6.5），并更新和保存至资产数据
8. 按需为资产生成图像（§6.6）
9. 按剧集智能分析与拆分镜头（§7）
10. 参考资产图像生成分镜视频（§8）
```

---

## 4. 剧目（项目）管理 API

前缀：`/openapi/drama`

### 4.1 GET /openapi/drama/list

获取剧目列表。

**查询参数（Query）：**

| 参数              | 必填 | 类型   | 说明                                         |
|-------------------|------|--------|----------------------------------------------|
| `include_deleted` | 否   | string | `'true'` 时包含已软删除剧目，默认 `'false'` |

**成功响应示例（与后端统一响应结构一致）：**

```json
{
  "code": 1,
  "msg": "success",
  "data": [
    {
      "id": "1",
      "name": "校园奇妙夜",
      "deleted": false,
      "operation_time": "2025-01-01T10:00:00"
    }
  ]
}
```

**错误响应示例：**

```json
{
  "code": -1,
  "msg": "错误描述",
  "data": {
    "error": "错误描述"
  }
}
```

---

### 4.2 POST /openapi/drama/create

创建新剧目。

**请求体（JSON）：**

```json
{
  "name": "新剧本名称"
}
```

| 字段   | 必填 | 类型   | 说明     |
|--------|------|--------|----------|
| `name` | 是   | string | 剧目名称 |

**成功响应示例：**

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "id": "2",
    "name": "新剧本名称",
    "deleted": false,
    "operation_time": "2025-01-01T12:00:00"
  }
}
```

**错误响应示例：**

```json
{
  "code": -1,
  "msg": "name required",
  "data": {
    "error": "name required"
  }
}
```

---

### 4.3 GET /openapi/drama/{play_id}

获取单个剧目详情；找不到返回 404。

**路径参数（Path）：**

| 参数      | 必填 | 类型 | 说明   |
|-----------|------|------|--------|
| `play_id` | 是   | int  | 剧目 ID |

**成功响应示例：**

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "id": "1",
    "name": "短剧实例",
    "deleted": false,
    "operation_time": "2025-01-01T12:00:00"
  }
}
```

**未找到时（HTTP 404）：**

```json
{
  "code": -1,
  "msg": "Not found",
  "data": {
    "error": "Not found"
  }
}
```

---

### 4.4 GET /openapi/drama/{play_id}/stats

获取剧目统计信息（集数、镜头数、资产数量等）。

**路径参数（Path）：** 同 4.3。

**成功响应示例：**

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "episodes_total": 12,
    "shots_total": 210,
    "estimated_duration_sec": 3600,
    "assets": {
      "scenes": 15,
      "characters": 25,
      "props": 50
    }
  }
}
```

剧本不存在或已删除时返回 404：

```json
{
  "code": -1,
  "msg": "Not found",
  "data": {
    "error": "Not found"
  }
}
```

---

### 4.5 GET /openapi/drama/{play_id}/style-config
### 4.6 PUT /openapi/drama/{play_id}/style-config

获取/更新项目默认风格配置。

**路径参数（Path）：** 同 4.3。

**GET 响应（概要）：**

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "selected_style_key": "realistic",
    "styles": {
      "realistic": { "...": "..." },
      "custom": { "...": "..." }
    }
  }
}
```

**PUT 请求体（JSON）：**

需要至少提供 `selected_style_key` 或 `styles` 之一：

| 字段                | 必填 | 类型   | 说明                                   |
|---------------------|------|--------|----------------------------------------|
| `selected_style_key`| 否   | string | 当前选中的风格 key                     |
| `styles`            | 否   | object | 风格配置字典，各 key 为风格标识       |

`selected_style_key` 取值：

- `realistic` / `oriental_fantasy` / `western_fantasy` / `cyberpunk` / `pixar` / `ghibli` / `custom`

**PUT 成功响应：**

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "selected_style_key": "custom",
    "styles": {
      "custom": { "...": "..." }
    }
  }
}
```

若既未提供 `selected_style_key` 也未提供 `styles`，返回 400，`data.error` 为错误信息。

---

## 5. 剧本管理与资产分析 API

前缀：`/openapi/drama/{play_id}/scripts`

### 5.1 GET /openapi/drama/{play_id}/scripts

获取剧本集列表。

**路径参数（Path）：**

| 参数      | 必填 | 类型 | 说明    |
|-----------|------|------|---------|
| `play_id` | 是   | int  | 剧目 ID |

**请求体 / 查询参数：** 无

**成功响应结构：**

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "episodes": [
      {
        "episode_no": 1,
        "file": "ep01.txt",
        "title": "第1集",
        "uploaded_at": "2025-01-01T12:00:00"
      }
    ]
  }
}
```

**错误响应：**

当剧目不存在或文件结构异常时，会返回：

```json
{
  "code": -1,
  "msg": "错误描述字符串"
}
```

---

### 5.2 POST /openapi/drama/{play_id}/scripts/upload

上传或更新单集剧本文本，支持 `multipart/form-data` 与 `application/json`。

#### 5.2.0 对用户上传的剧本数据进行校验和扩展
- 对用户上传的数据进行校验，如果只有一个简短的故事创意（200字以内），则帮助用户充实和扩展故事情节，最终故事情节内容需要达到800字以上，以此作为API调用中的剧本正文的内容

**路径参数（Path）：** 同 5.1。

#### 5.2.1 `multipart/form-data` 形式

| 字段         | 必填 | 类型   | 说明                                                         |
|--------------|------|--------|--------------------------------------------------------------|
| `file`       | 是   | file   | 剧本文件，要求 UTF-8 文本编码                               |
| `episode_no` | 否   | int    | 集号；不传时后端会从现有 `episodes` 中推算下一集            |
| `title`      | 否   | string | 集标题；不传时自动生成 `"第{episode_no}集"`                  |

#### 5.2.2 `application/json` 形式

```json
{
  "episode_no": 1,
  "content": "整集剧本文本",
  "title": "第1集标题"
}
```

| 字段         | 必填 | 类型   | 说明                                      |
|--------------|------|--------|-------------------------------------------|
| `content`    | 是   | string | 剧本正文内容                              |
| `episode_no` | 否   | int    | 集号；不传时自动推算为当前最大集号 + 1    |
| `title`      | 否   | string | 集标题；不传时由后端生成默认标题         |

**成功响应结构：**

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "episode_no": 1,
    "file": "ep01.txt",
    "title": "第1集标题",
    "uploaded_at": "2025-01-01T12:00:00"
  }
}
```

**错误响应示例：**

```json
{
  "code": -1,
  "msg": "错误描述"
}
```

---

### 5.3 GET /openapi/drama/{play_id}/scripts/{episode_no}/content

获取指定集剧本原文；不存在时返回 404。

**路径参数（Path）：**

| 参数         | 必填 | 类型 | 说明    |
|--------------|------|------|---------|
| `play_id`    | 是   | int  | 剧目 ID |
| `episode_no` | 是   | int  | 集号    |

**请求体：** 无

**成功响应结构：**

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "content": "整集剧本文本"
  }
}
```

**错误响应示例（HTTP 404）：**

```json
{
  "code": -1,
  "msg": "该集剧本不存在"
}
```

其他错误同样以 `"code": -1, "msg": "错误描述"` 的形式返回。

---

### 5.4 DELETE /openapi/drama/{play_id}/scripts/{episode_no}

删除指定集剧本。

**路径参数（Path）：** 同 5.3。

**请求体：** 无

**成功响应结构：**

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "deleted": true
  }
}
```

**错误响应示例：**

```json
{
  "code": -1,
  "msg": "错误描述"
}
```

---

### 5.5 POST /openapi/drama/{play_id}/scripts/analyze

剧本资产智能分析，从原文中抽取场景/角色/道具并更新资产库。

**请求体（JSON，可选）：**

```json
{
  "episode_nos": [1, 2],
  "asset_types": [1, 2, 3]
}
```

| 字段          | 类型 | 说明                                                                 |
|---------------|------|----------------------------------------------------------------------|
| `episode_nos` | 数组 | 要分析的集号列表；不传则分析所有已有集                              |
| `asset_types` | 数组 | 要分析的资产类型 ID：1=场景,2=角色,3=道具；不传或空表示三类全部分析 |

类型约束：

- `episode_nos` 存在但不是数组 → 400，`msg: "episode_nos 须为数组"`
- `asset_types` 存在但不是数组 → 400，`msg: "asset_types 须为数组"`

**成功响应结构：**

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "created": [
      {
        "id": "10",
        "type": 2,
        "name": "角色A",
        "description": "人物小传...",
        "deleted": false,
        "operation_time": "2025-01-01T12:00:00"
      }
    ],
    "merged": [
      {
        "name": "角色B",
        "type": 2,
        "id": "5"
      }
    ]
  }
}
```

其中：

- `created`：本次分析新建的资产列表（结构与资产对象一致）。
- `merged`：与已有资产合并的条目列表，至少包含 `name`、`type`、`id`。

**错误响应示例：**

```json
{
  "code": -1,
  "msg": "错误描述"
}
```

---

## 6. 资产管理 API

前缀：`/openapi/drama/{play_id}/assets`

### 6.1 GET /openapi/drama/{play_id}/assets/list

按类型、集数、名称过滤资产列表，并附带封面与是否有终稿图标记。

**路径参数（Path）：**

| 参数      | 必填 | 类型 | 说明    |
|-----------|------|------|---------|
| `play_id` | 是   | int  | 剧目 ID |

**查询参数（Query）：**

| 参数              | 必填 | 类型   | 说明                                                                 |
|-------------------|------|--------|----------------------------------------------------------------------|
| `type`            | 否   | int    | 资产类型：1=场景, 2=角色, 3=道具, 4=平面, 5=其他；不传返回所有类型   |
| `include_deleted` | 否   | string | 是否包含已软删除资产，默认 `'false'`；传 `'true'` 时包含             |
| `episode_no`      | 否   | int    | 仅返回在该集分镜中出现过的资产                                       |
| `name`            | 否   | string | 名称关键词（不区分大小写），匹配 `name` 包含该子串的资产            |

**成功响应结构：**

```json
{
  "code": 1,
  "msg": "success",
  "data": [
    {
      "id": "1",
      "type": 2,
      "name": "角色A",
      "description": "可选描述",
      "source_episode_nos": [1, 2],
      "deleted": false,
      "operation_time": "2025-01-01T12:00:00",
      "cover_url": "/openapi/drama/1/assets/2/1/general/candidates/10/image",
      "has_final_image": true
    }
  ]
}
```

字段说明（单个资产）：

| 字段                | 类型         | 说明                                                         |
|---------------------|--------------|--------------------------------------------------------------|
| `id`                | string       | 资产 ID（剧目内唯一）                                       |
| `type`              | int          | 资产类型：1 场景、2 角色、3 道具、4 平面、5 其他             |
| `name`              | string       | 资产名称                                                     |
| `description`       | string\|null | 资产描述，可为空                                             |
| `source_episode_nos`| array\<int>  | 可选，资产首次出现的集号列表                                 |
| `deleted`           | bool         | 是否已软删除                                                 |
| `operation_time`    | string       | 最后操作时间（字符串时间戳）                                 |
| `cover_url`         | string\|null | 封面图 URL（候选图 `/general/candidates/{cand_id}/image`）   |
| `has_final_image`   | bool         | 是否已有终稿图                                               |

**错误响应示例（HTTP 500）：**

```json
{
  "code": -1,
  "msg": "error",
  "data": {
    "error": "具体错误信息"
  }
}
```

---

### 6.2 POST /openapi/drama/{play_id}/assets/create

创建新资产。

**路径参数（Path）：** 同 6.1。

**请求体（JSON）：**

```json
{
  "type": 2,
  "name": "角色A",
  "description": "女主，高中生..."
}
```

| 字段          | 必填 | 类型   | 说明                                         |
|---------------|------|--------|----------------------------------------------|
| `type`        | 是   | int    | 资产类型：1 场景, 2 角色, 3 道具, 4 平面     |
| `name`        | 是   | string | 资产名称                                     |
| `description` | 否   | string | 资产描述，可为空或省略                      |

**成功响应结构：**

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "id": "2",
    "type": 2,
    "name": "角色A",
    "description": "女主，高中生...",
    "deleted": false,
    "operation_time": "2025-01-01T12:00:00"
  }
}
```

**错误响应示例：**

```json
{
  "code": -1,
  "msg": "错误描述"
}
```

---

### 6.3 GET /openapi/drama/{play_id}/assets/{asset_id}

获取单个资产详情。

**路径参数（Path）：**

| 参数       | 必填 | 类型   | 说明     |
|------------|------|--------|----------|
| `play_id`  | 是   | int    | 剧目 ID  |
| `asset_id` | 是   | string | 资产 ID  |

**请求体 / 查询参数：** 无

**成功响应结构：**

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "id": "1",
    "type": 2,
    "name": "角色A",
    "description": "可选描述",
    "source_episode_nos": [1, 2],
    "deleted": false,
    "prompt": "<该字段可能不存在>资产级主提示词，用于图像生成等综合场景",
    "candidate_image_urls": [],
    "operation_time": "2025-01-01T12:00:00"
  }
}
```

**字段说明（`data`，除与 §6.1 相同的 `id` / `type` / `name` / `description` / `source_episode_nos` / `deleted` / `operation_time` 外）：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `prompt` | string | **可选。** 资产维度的**主提示词**，供生图等流程使用；未保存过则无此键 |
| `candidate_image_urls` | array\<string> | 该资产下候选图的可访问 URL 列表；无候选图为 `[]` |

**错误响应示例：**

```json
{
  "code": -1,
  "msg": "错误描述"
}
```

---

### 6.4 PUT /openapi/drama/{play_id}/assets/{asset_id}

更新已有资产的名称、类型、描述、来源集数、**提示词**等。请求体 **至少提供一个**可更新字段；仅允许修改**未软删除**的资产。

**路径参数（Path）：**

| 参数       | 必填 | 类型   | 说明     |
|------------|------|--------|----------|
| `play_id`  | 是   | int    | 剧目 ID  |
| `asset_id` | 是   | string | 资产 ID  |

**请求体（JSON）：** 以下字段均为可选，但 **不能全部省略**（至少传一项）。

```json
{
  "name": "角色A（改名）",
  "type": 2,
  "description": "新的描述；传空字符串可清空",
  "source_episode_nos": [1, 3],
  "prompt": "更新后的资产主提示词；传空字符串可清空",
}
```

**字段说明**：参考 §6.1 和 §6.3

**成功响应结构：**

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "id": "1",
    "type": 2,
    "name": "角色A（改名）",
    "description": "新的描述",
    "prompt": "…",
    "deleted": false,
    "operation_time": "2025-01-01T12:00:00"
  }
}
```

**错误响应示例：** 参数缺失（未提供任何可更新字段）、资产不存在或已删除、类型非法等，返回 `code=-1` 及 `msg` / `data.error` 说明（HTTP 状态码以网关为准，常见为 400/500）。

---

### 6.5 POST /openapi/drama/{play_id}/assets/prompt-helper/generate

调用大模型 **辅助生成资产图像提示词**：根据资产类型、模式与描述等，经模板渲染后请求文本模型，返回一段可直接用于图像生成的中文提示词。

**说明：** 响应中的 `generated_prompt` **不会**自动写入资产；若需保存，请调用 **§6.4** `PUT /openapi/drama/{play_id}/assets/{asset_id}`，将内容写入资产的 `prompt` 字段并保存。

**路径参数（Path）：**

| 参数       | 必填 | 类型 | 说明    |
|------------|------|------|---------|
| `play_id`  | 是   | int  | 剧目 ID |

**请求体（JSON）：**

```json
{
  "asset_type": 2,
  "mode_key": "face_closeup",
  "template": "可选：自定义模板文本（可含占位符，由服务端渲染）",
  "initial_description": "资产名称、设定或剧本相关描述，供模板填充",
  "personalized_requirements": "可选：额外画面/风格/构图等约束"
}
```

| 字段                         | 必填 | 类型   | 说明                                                                 |
|------------------------------|------|--------|----------------------------------------------------------------------|
| `asset_type`                 | 是   | int    | 资产类型：1 场景、2 角色、3 道具、4 平面、5 其他                     |
| `mode_key`                   | 是   | string | 提示词模式键（须非空），与剧目侧提示词模板配置一致（如某类资产的视角/模式） |
| `template`                   | 否   | string | 模板全文；若省略或仅为空白，则由服务端根据 `play_id`、`asset_type`、`mode_key` 解析默认模板 |
| `initial_description`        | 是   | string | 资产初始描述（须非空），参与模板占位符替换并作为生成依据                 |
| `personalized_requirements`  | 否   | string | 个性化补充要求，默认空字符串                                         |

`mode_key` 可选值（按 `asset_type`）：

| `asset_type` | 类型 | `mode_key` 可选值 |
|--------------|------|-------------------|
| `1` | 场景 | `panorama`、`top_view`、`specific_angle`、`nine_grid`、`sphere_360` |
| `2` | 角色 | `face_closeup`、`full_body`、`three_view`、`tone` |
| `3` | 道具 | `front_view`、`three_view`、`prop_character_ref` |
| `4` | 平面 | `default` |
| `5` | 其他 | `default` |

**成功响应结构：**

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "generated_prompt": "由模型输出的、可直接用于图像生成的中文提示词全文…"
  }
}
```

| 字段                | 类型   | 说明                           |
|---------------------|--------|--------------------------------|
| `generated_prompt`  | string | 模型生成的一条完整图像提示词   |

**错误响应示例：**

- 参数不合法（如缺少 `asset_type`、`initial_description` 为空、`mode_key` 为空等）：HTTP **400**。
- 大模型调用失败或计费相关异常：HTTP **500**。

```json
{
  "code": -1,
  "msg": "错误描述",
  "data": {
    "error": "具体错误信息"
  }
}
```

---

### 6.6 POST /openapi/drama/{play_id}/assets/{asset_type}/{asset_id}/generate_image

资产图片生成：基于用户提示词、提示词模板与参考图调用模型生成图片，并作为新候选图写入对应资产。
该接口为**异步入队**：HTTP 立即返回 `taskId` 后，后台 worker 才会真正生成图片并落盘到候选图目录。

**请求体（JSON）示例：**

```json
{
  "user_prompt": "校园夜景，女生站在走廊窗边",
  "prompt_template": "写实风格，电影感光影",
  "reference_images": ["assets/2_角色A/general/references/1_参考图.png"],
  "reference_materials": [
    {
      "id": 12,
      "name": "走廊参考图.png",
      "path": "assets/2_角色A/general/references/1_参考图.png",
      "url": "/api/drama/1/assets/2/1/general/references/1/image",
      "source": "linked"
    }
  ],
  "prompt_mode_key": "face_closeup",
  "model": "bytedance-seed/seedream-4.5",
  "aspect_ratio": "16:9",
  "image_size": "1K"
}
```

字段说明：

| 字段               | 必填 | 类型        | 说明                                                             |
|--------------------|------|-------------|------------------------------------------------------------------|
| `user_prompt`      | 否   | string      | 用户输入的提示词                                                 |
| `prompt_template`  | 否   | string      | 提示词模板，将与 `user_prompt` 拼接成最终提示词                  |
| `reference_images` | 否   | array       | 参考图相对路径数组（相对于剧目根目录），若提供则必须实际存在     |
| `reference_materials` | 否 | array\<object> | 参考素材对象数组（`id/name/path/url/source`）；前端实际优先传该字段用于任务记录与重试 |
| `prompt_mode_key`  | 否   | string      | 当前提示词模式键（如 `face_closeup`）；用于按模式记录最近一次生图配置 |
| `model`            | 否   | string      | 生成模型；不传时使用该项目生效的默认图像模型                    |
| `aspect_ratio`     | 否   | string      | 画面宽高比，默认 `"16:9"`                                        |
| `image_size`       | 否   | string      | 图像尺寸标签，默认 `"1K"`                                       |

**成功响应结构（提交任务）：**

该接口为**异步入队**，HTTP 响应只返回任务标识；图片最终结果需要在任务完成后再查询。

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "taskId": "ci_xxxxxxxx",
    "queuePosition": 3,
    "message": "任务已提交，后台运行中，可到 AI 任务列表查看"
  }
}
```

**任务最终 `result`：**

当任务 `status=completed` 后，`GET /openapi/api/ai-tasks/tasks/<task_id>` 返回的 `data.result` 通常包含：

```json
{
  "id": "候选图ID(字符串)",
  "name": "候选图文件名中的name",
  "image": "候选图原图文件名(如 1_xxx.png)"
}
```

**错误响应结构：**

本接口所有错误都通过简单的字符串消息返回，不包含 `data.error`，基本示例如下：

```json
{
  "code": -1,
  "msg": "错误信息"
}
```

代理在判断是否成功时，应以 `code == 1` 为准。

---

## 7. 分镜脚本管理 API

前缀：`/openapi/drama/{play_id}/storyboard`

### 7.1 GET /openapi/drama/{play_id}/storyboard/{episode_no}

获取某集分镜；尚未分析时 `shots` 为空。

**路径参数（Path）：**

| 参数         | 必填 | 类型 | 说明    |
|--------------|------|------|---------|
| `play_id`    | 是   | int  | 剧目 ID |
| `episode_no` | 是   | int  | 集号    |

**请求体：** 无

**成功响应结构：**

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "play_id": "1",
    "episode_no": 1,
    "analyzed_at": null,
    "shots": []
  }
}
```

当该集已分析时，`data.shots` 为镜头数组；单个镜头对象字段（来自后端写入/编辑）：

| 字段            | 类型                | 说明 |
|-----------------|---------------------|------|
| `id`            | string              | 镜头 ID（形如 `s1`、`s2`） |
| `order`         | int                 | 镜头序号 |
| `description`   | string              | 镜头描述 |
| `original_script` | string\|null      | 对应剧本原文片段（可为空） |
| `scene_ids`     | array\<string>      | 场景资产 ID 列表（可为空） |
| `character_ids` | array\<string>      | 角色资产 ID 列表 |
| `prop_ids`      | array\<string>      | 道具资产 ID 列表 |
| `surface_ids`   | array\<string>      | 平面资产 ID 列表 |
| `other_ids`     | array\<string>      | 其他资产 ID 列表 |
| `dialogues`     | array\<object>      | 台词列表（见下） |
| `prompt`        | string\|null        | 提示词（可为空） |
| `duration_sec`  | number\|null        | 时长（可为空） |
| `shot_type`     | string\|null        | 镜头类型/景别（可为空） |

`dialogues[]` 每项字段：

| 字段            | 类型         | 说明 |
|-----------------|--------------|------|
| `speaker_id`    | string\|null | 说话人角色资产 ID（可能为空） |
| `speaker_name`  | string       | 说话人名称 |
| `content`       | string       | 台词内容 |
| `delivery`      | string       | 语气/方式 |
| `is_inner_voice`| bool         | 是否内心独白 |

**错误响应结构：**

```json
{
  "code": -1,
  "msg": "错误描述"
}
```

---

### 7.2 POST /openapi/drama/{play_id}/storyboard/{episode_no}/analyze

触发该集分镜分析：读取该集剧本 → AI 拆分为镜头序列并关联资产。

**路径参数（Path）：** 同 7.1。

**请求体：** 无

**成功响应结构：**

返回分析后分镜对象（字段同 7.1），并额外包含：

| 字段                 | 类型 | 说明 |
|----------------------|------|------|
| `related_assets_count` | int | 本集相关资产数量（供前端可选展示） |

响应示例：

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "play_id": "1",
    "episode_no": 1,
    "analyzed_at": "2025-01-01T12:00:00",
    "shots": [],
    "related_assets_count": 123
  }
}
```

**错误响应结构：**

```json
{
  "code": -1,
  "msg": "错误描述"
}
```

---

### 7.3 GET /openapi/drama/{play_id}/storyboard/{episode_no}/shots/{shot_id}

获取单个镜头详情，包含 `prompt`、`description`、`original_script` / `original_content`。

**路径参数（Path）：**

| 参数         | 必填 | 类型   | 说明    |
|--------------|------|--------|---------|
| `play_id`    | 是   | int    | 剧目 ID |
| `episode_no` | 是   | int    | 集号    |
| `shot_id`    | 是   | string | 镜头 ID |

**请求体：** 无

**成功响应结构：**

在基础镜头字段（见 7.1 的 `shots[]`）之上，额外返回：

| 字段                    | 类型            | 说明 |
|-------------------------|-----------------|------|
| `original_content`      | string          | 由镜头描述 + 剧本原文 + 关联资产名称拼接的展示文本 |
| `reference_image_paths` | array\<string>  | 参考图相对路径列表（最多 4 张，用于初始化参考图模式） |
| `reference_image_names` | array\<string>  | 与 `reference_image_paths` 对应的资产名称列表 |

响应示例（省略部分字段）：

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "id": "s1",
    "order": 1,
    "description": "镜头描述",
    "original_script": "剧本原文片段",
    "scene_ids": ["1"],
    "character_ids": ["2"],
    "prop_ids": [],
    "surface_ids": [],
    "other_ids": [],
    "dialogues": [],
    "prompt": null,
    "duration_sec": null,
    "shot_type": null,
    "original_content": "用于展示的拼接文本",
    "reference_image_paths": ["characters/2_角色A/general/candidates/10/图.png"],
    "reference_image_names": ["角色A"]
  }
}
```

**错误响应结构：**

```json
{
  "code": -1,
  "msg": "错误描述"
}
```

---

### 7.4 POST /openapi/drama/{play_id}/storyboard/{episode_no}/shots/{shot_id}/add-asset

为镜头添加资产（补标），可新建或关联已有资产。

**请求体（JSON）：**

| 字段         | 必填 | 类型        | 说明 |
|--------------|------|-------------|------|
| `asset_type` | 是   | int         | 资产类型：1=场景 2=角色 3=道具 4=平面 5=其他 |
| `name`       | 否   | string      | 新建资产时提供（与 `asset_id` 二选一） |
| `asset_id`   | 否   | string      | 绑定已有资产时提供（与 `name` 二选一） |

请求体示例：

```json
{
  "asset_type": 2,
  "name": "新角色名"
}
```

**成功响应结构：**

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "asset": {
      "id": "10",
      "type": 2,
      "name": "新角色名",
      "deleted": false,
      "operation_time": "2025-01-01T12:00:00"
    },
    "shot": {
      "id": "s1",
      "order": 1,
      "scene_ids": [],
      "character_ids": ["10"],
      "prop_ids": [],
      "surface_ids": [],
      "other_ids": []
    }
  }
}
```

**错误响应结构：**

```json
{
  "code": -1,
  "msg": "错误描述"
}
```

---

### 7.5 POST /openapi/drama/{play_id}/storyboard/{episode_no}/shots/{shot_id}/optimize-prompt

生成或优化分镜视频合成的提示词（专门针对SD2.0智能参考视频生成模式）。

**路径参数（Path）：**

| 参数         | 必填 | 类型   | 说明    |
|--------------|------|--------|---------|
| `play_id`    | 是   | int    | 剧目 ID |
| `episode_no` | 是   | int    | 集号    |
| `shot_id`    | 是   | string | 镜头 ID |

**请求体（JSON）：** 体本身可为空对象 `{}`；下列字段均为可选，但需满足文末**上下文约束**（否则返回 400）。

| 字段                       | 必填 | 类型                  | 说明 |
|----------------------------|------|-----------------------|------|
| `user_requirement`         | 否   | string                | 用户对优化结果的要求；不传则仅按其余上下文与当前提示词优化 |
| `original_script`          | 否   | string                | 原始剧本文本片段；不传则使用镜头自身 `original_script` |
| `description`              | 否   | string                | 镜头描述；不传则使用镜头自身 `description` |
| `dialogues`                | 否   | array\<object>        | 台词列表；不传则使用镜头自身 `dialogues` |
| `duration_sec`             | 否   | number\|string\|null  | 时长；不传则使用镜头自身 `duration_sec`（字符串会尝试解析为数字，失败则视为无时长） |
| `reference_explanations`   | 否   | array\<object>        | 参考图解释列表；用于在无 `reference_explanations_text` 时拼接参考说明文本 |
| `reference_explanations_text` | 否 | string             | 参考图解释汇总文本；**优先于**由 `reference_explanations` 拼接的结果；二者均为空时，后端按镜头已绑定资产生成与前端一致的默认「【@图N】…」多行说明（仍无资产则为空） |
| `current_prompt`           | 否   | string                | 当前提示词；不传则使用镜头自身 `prompt` |
| `prompt_fixed_prefix`      | 否   | string                | 固定前缀；非空时拼在模型生成结果之前（中间空一行）再返回/回写 |
| `save`                     | 否   | bool\|int\|string     | 是否回写到镜头；**默认 true**（接口层对多种形态做布尔解析） |
| `async_task`               | 否   | bool\|int\|string     | 为真时走 AI 任务队列，HTTP 立即返回 `taskId` 等；**默认 false**（同步返回 `prompt`） |

`reference_explanations[]` 每项常见字段（按后端拼接逻辑读取；**整项对象及下属字段均非必填**）：

| 字段             | 必填 | 类型 | 说明 |
|------------------|------|------|------|
| `image_index`     | 否   | int  | 图片序号（用于生成“图N”描述） |
| `asset_type_label`| 否   | string | 资产类型中文标签（如“角色/场景/道具”） |
| `asset_name`      | 否   | string | 资产名称 |
| `explain_text`    | 否   | string | 已写好的解释文本（若存在则优先使用） |

**上下文约束：** 若 `current_prompt`（及镜头上的 `prompt`）为空，且以下也全部为空——`original_script`、`description`、台词上下文、`reference_explanations_text`（及由 `reference_explanations` 或镜头资产默认生成的参考说明）——则接口返回错误，提示缺少可用于生成的上下文。

**成功响应结构（同步，`async_task` 未开启）：**

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "prompt": "优化后的提示词文本",
    "saved": true
  }
}
```

**成功响应结构（异步，`async_task` 为真）：** `data` 含任务信息，生成和优化结果在任务完成后通过任务详情/前端轮询获取。

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "taskId": "任务 ID",
    "queuePosition": 0,
    "message": "任务已提交，后台运行中，可到 AI 任务列表查看"
  }
}
```

**错误响应结构：**

```json
{
  "code": -1,
  "msg": "错误描述"
}
```

---

### 7.6 DELETE /openapi/drama/{play_id}/storyboard/{episode_no}/shots/{shot_id}

删除指定镜头。

**请求体：** 无

**成功响应结构：**

本接口成功时返回 `data=null`，由于后端统一响应实现会省略 `data` 字段，实际响应形如：

```json
{
  "code": 1,
  "msg": "success"
}
```

**错误响应结构：**

```json
{
  "code": -1,
  "msg": "错误描述"
}
```

---

## 8. 参考资产图片生成分镜视频 API

前缀：`/openapi/drama/{play_id}/storyboard-video`

### 8.1 POST /openapi/drama/{play_id}/storyboard-video/episodes/{episode_no}/shots/{shot_id}/tasks

创建分镜视频生成任务（异步入队）

**路径参数（Path）：** 同 8.1。

**请求体（JSON）示例：**

```json
{
  "mode": "reference",
  "prompt": "画面提示词",
  "asset_snapshot": { "...": "..." },
  "motion": "动作描述",
  "model": "seedance1.5",
  "duration_sec": 5,
  "ratio": "16:9",
  "resolution": "720p"
}
```

请求体字段说明（与后端校验一致）：

| 字段                  | 必填 | 类型                | 说明 |
|-----------------------|------|---------------------|------|
| `mode`                | 是   | string              | 必须为 `"reference"` |
| `reference_image_paths` | 否 | array\<string>    | 可选：若不传或为空，后端会从该镜头已绑定资产生成默认参考图路径 |
| `prompt`              | 否   | string              | 可选，生成提示词 |
| `asset_snapshot`      | 否   | object              | 可选，资产快照（原样透传进任务） |
| `motion`              | 否   | string              | 可选，运动描述 |
| `model`               | 否   | string              | 可选，视频模型 |
| `duration_sec`        | 否   | number              | 可选，时长（时长≥4，同时用于计费 quantity_key） |
| `ratio`               | 否   | string              | 可选，画幅比例（默认 `"16:9"`）|
| `resolution`          | 否   | string              | 可选，分辨率（默认为 `"720p"`） |

**成功响应结构（提交任务）：**

```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "taskId": "sv_xxxxxxxx",
    "queuePosition": 2,
    "message": "任务已提交，后台运行中，可到 AI 任务列表查看"
  }
}
```

**错误响应结构：**

```json
{
  "code": -1,
  "msg": "错误描述"
}
```

> 任务创建后，生成结果需要通过 §8.2 中的 `GET /openapi/api/ai-tasks/tasks/<task_id>` 查询任务详情，直到 `status=completed` 后从 `data.result.result_video_path` 读取最终视频路径。

---
### 8.2 GET /openapi/api/ai-tasks/tasks/<task_id>
查询 AI 任务状态与最终执行结果（异步任务通用）

该接口用于配合 §6.6、§7.5、§8.1：
当你调用这些接口的**异步模式 POST**后会得到 `taskId`，随后轮询本接口直到任务完成。

**路径参数（Path）：**

| 参数      | 必填 | 类型   | 说明     |
|-----------|------|--------|----------|
| `task_id` | 是   | string | 任务 ID |

**请求体：** 无（GET）

**成功响应示例：**
```json
{
  "code": 1,
  "msg": "success",
  "data": {
    "taskId": "ci_xxxxxxxx",
    "userId": "123",
    "taskType": "asset_candidate_image",
    "status": "completed",
    "queuePosition": 3,
    "createdAt": "2025-01-01T10:00:00.000Z",
    "startedAt": "2025-01-01T10:00:10.000Z",
    "finishedAt": "2025-01-01T10:00:20.000Z",
    "durationSec": 10,
    "result": { "...": "..." },
    "errorMessage": null,
    "isRead": false,
    "readAt": null,
    "cancelledAt": null,
    "operationContent": "任务列表展示用描述"
  }
}
```

**字段说明（`data`）：**

| 字段              | 类型            | 说明 |
|-------------------|-----------------|------|
| `taskId`          | string          | 任务 ID |
| `taskType`        | string          | 任务类型（如 `asset_candidate_image` / `shot_prompt_gen` / `shot_video_gen`） |
| `status`          | string          | 任务状态：`pending` / `running` / `completed` / `failed`（也可能为 `timeout` / `cancelled`） |
| `params`          | object\|null    | 入队参数（用于排查） |
| `resultRoute`     | object\|null   | 提交任务时透传的回调/路由信息 |
| `queuePosition`  | number          | 全局队列位置 |
| `result`          | object\|null   | 成功时的执行结果（失败时通常为 null） |
| `errorMessage`   | string\|null   | 失败原因 |

**任务队列处理机制（创建 -> 查询状态 -> 获取结果）：**

1. **创建任务（提交 POST）**：调用 §6.6（候选图）、§7.5（`optimize-prompt` 异步）、§8.1（分镜视频）后，服务端写入队列并立即返回 `taskId`。
2. **查询任务状态（轮询 GET）**：客户端轮询 `GET /openapi/api/ai-tasks/tasks/<task_id>`，观察 `status`：
   - `pending`：排队中
   - `running`：后台 worker 正在执行
   - `completed`：成功完成
   - `failed`：执行失败（可读取 `errorMessage`）
3. **获得最终执行结果（读取 result）**：当 `status=completed` 时，读取 `data.result`：
   - `asset_candidate_image`：`result.id/name/image`
   - `shot_prompt_gen`：`result.prompt` / `result.saved`
   - `shot_video_gen`：`result.result_video_path`

## 9. 关键术语和字段解释

- `play_id`：剧目 ID，对应一个短剧项目。
- `episode_no`：集号，从 1 开始。
- `shot_id`：分镜中的单个镜头 ID。
- 资产类型：

  | 值 | 含义   |
  |----|--------|
  | 1  | 场景   |
  | 2  | 角色   |
  | 3  | 道具   |
  | 4  | 平面   |
  | 5  | 其他   |

- `source_episode_nos`：资产首次出现的集号列表。
- `candidate`：候选图（五官图或造型图），通常与提示词和模型配置绑定。
- `reference`：参考图，常用作造型/场景风格的视觉参考。

---

## 10. 实践案例概览

### 10.1 从零开始一个短剧项目（剧目 + 剧本 + 资产 + 分镜）

1. **认证**（§2）：让用户在 `https://idrama.lingban.cn/api-token` 页面登录并复制 Token，或通过 `POST /openapi/uaa/oauth/token` 登录获取 `access_token`。
2. **创建剧目**（§4.2）：`POST /openapi/drama/create`，请求体 `{"name": "新剧本名称"}`，获得 `play_id`。
3. **查看或更新风格配置**（§4.11/4.12）：`GET /openapi/drama/{play_id}/style-config` 查看，`PUT /openapi/drama/{play_id}/style-config` 更新默认风格。
4. **上传剧本**（§5.2）：`POST /openapi/drama/{play_id}/scripts/upload` 上传剧本文件/粘贴剧本文本。
5. **查看剧本集列表**（§5.1）：`GET /openapi/drama/{play_id}/scripts` 确认各集上传情况。
6. **按集读取剧本内容**（§5.3）：`GET /openapi/drama/{play_id}/scripts/{episode_no}/content` 查看某集原文。
7. **剧本资产智能分析**（§5.5）：`POST /openapi/drama/{play_id}/scripts/analyze`，从剧本抽取人物/场景/道具并写入资产库。
8. **查看资产列表**（§6.1）：`GET /openapi/drama/{play_id}/assets/list`，可按 `type`、`episode_no`、`name` 过滤。
9. **创建资产**（§6.2）：若需手工补充资产，`POST /openapi/drama/{play_id}/assets/create`，传入 `type`、`name`（及可选 `description`）。
10. **生成资产图像提示词**（§6.5）：`POST /openapi/drama/{play_id}/assets/prompt-helper/generate`；将 `generated_prompt` 通过 **§6.4** `PUT .../assets/{asset_id}` 写入 `prompt` / `prompt_by_mode`。
11. **生成资产图像**（§6.6）：`POST /openapi/drama/{play_id}/assets/{asset_type}/{asset_id}/generate_image`，按接口要求传入提示词与参考图等参数，生成新图并挂接到该资产。
12. **分析生成/更新分镜**（§7.2）：`POST /openapi/drama/{play_id}/storyboard/{episode_no}/analyze` 基于剧本/资产生成分镜结构与镜头信息。
13. **按集查看分镜**（§7.1）：`GET /openapi/drama/{play_id}/storyboard/{episode_no}` 获取该集分镜结构（若不存在可先执行下一步分析生成）。
14. **查看镜头详情**（§7.3）：`GET /openapi/drama/{play_id}/storyboard/{episode_no}/shots/{shot_id}` 获取单镜头字段、已绑定资产等信息。
15. **为镜头绑定资产**（§7.4）：`POST /openapi/drama/{play_id}/storyboard/{episode_no}/shots/{shot_id}/add-asset` 将角色/场景/道具等资产关联到镜头。
16. **生成和优化分镜提示词**（§7.5）：`POST /openapi/drama/{play_id}/storyboard/{episode_no}/shots/{shot_id}/optimize-prompt` 在当前提示词基础上做 AI 优化，并按需回写（`save=true/false`）。
17. **生成分镜视频**（§8.1）：`POST /openapi/drama/{play_id}/storyboard-video/episodes/{episode_no}/shots/{shot_id}/tasks` 创建任务；按文档约定轮询/订阅任务状态直至完成。
18. **查看剧目统计**（§4.8）：`GET /openapi/drama/{play_id}/stats` 获取集数、镜头数、资产数量等。

### 10.2 按集查看、读取与删除剧本（§5）

1. **剧本集列表**：`GET /openapi/drama/{play_id}/scripts` 获取所有剧集及文件名、标题、上传时间。
2. **某集剧本内容**：`GET /openapi/drama/{play_id}/scripts/{episode_no}/content` 获取该集原文。
3. **删除某集剧本**：`DELETE /openapi/drama/{play_id}/scripts/{episode_no}` 删除指定集（需确认该集不再用于分析或已备份）。

### 10.3 查看剧目统计与风格配置（§4）

1. **单个剧目详情**：`GET /openapi/drama/{play_id}` 获取剧目名称、删除状态、操作时间。
2. **剧目统计信息**：`GET /openapi/drama/{play_id}/stats` 获取集数、镜头数、预估时长、各类型资产数量。
3. **当前风格配置**：`GET /openapi/drama/{play_id}/style-config` 获取 `selected_style_key` 与 `styles`。
4. **更新风格配置**：`PUT /openapi/drama/{play_id}/style-config`，请求体传入 `selected_style_key` 和/或 `styles`。

### 10.4 资产列表、详情与基于参考图生成图像（§6）

1. **按条件查资产**：`GET /openapi/drama/{play_id}/assets/list`，可用查询参数 `type`（1 场景/2 角色/3 道具/4 平面/5 其他）、`episode_no`、`name`、`include_deleted` 过滤。
2. **单个资产详情**：`GET /openapi/drama/{play_id}/assets/{asset_id}`（§6.3）获取该资产元数据、提示词字段、候选图 URL 等。
3. **创建资产**：`POST /openapi/drama/{play_id}/assets/create`（§6.2），传入 `type`、`name`，可选 `description`。
4. **更新资产**：`PUT /openapi/drama/{play_id}/assets/{asset_id}`（§6.4），可更新名称、类型、`prompt`、`prompt_by_mode`、生图配置、画布字段等（至少传一项）。
5. **生成资产图像提示词**（§6.5）：`POST /openapi/drama/{play_id}/assets/prompt-helper/generate`；可将返回的 `generated_prompt` 再通过 **§6.4** 写入资产。
6. **生成资产图像**（§6.6）：`POST /openapi/drama/{play_id}/assets/{asset_type}/{asset_id}/generate_image`，按接口要求传入提示词与参考图等参数，生成新图并挂接到该资产。

### 10.5 分镜脚本：按集生成、查看镜头并绑定资产（§7）

1. **读取某集分镜**：`GET /openapi/drama/{play_id}/storyboard/{episode_no}` 获取分镜结构与镜头列表。
2. **生成/更新分镜**：若分镜为空或需要重算，`POST /openapi/drama/{play_id}/storyboard/{episode_no}/analyze` 进行分析生成。
3. **查看镜头详情**：`GET /openapi/drama/{play_id}/storyboard/{episode_no}/shots/{shot_id}` 获取镜头信息、提示词、已绑定资产等。
4. **为镜头添加资产**：`POST /openapi/drama/{play_id}/storyboard/{episode_no}/shots/{shot_id}/add-asset` 绑定角色/场景/道具等（建议先用 §6 的资产列表/详情确认 `asset_id`）。
5. **生成和优化分镜提示词**：`POST /openapi/drama/{play_id}/storyboard/{episode_no}/shots/{shot_id}/optimize-prompt` 优化镜头提示词，并按需回写（`save=true`）。
6. **删除镜头（谨慎）**：若需移除镜头，`DELETE /openapi/drama/{play_id}/storyboard/{episode_no}/shots/{shot_id}`（建议先确认是否已关联生成任务或引用资源）。

### 10.6 分镜出图与视频：任务生成（§8）

1. **创建分镜视频生成任务**：`POST /openapi/drama/{play_id}/storyboard-video/episodes/{episode_no}/shots/{shot_id}/tasks` 发起该镜头视频生成任务。
2. **查询任务结果**：按照 §8.1 的返回结构与状态字段轮询/订阅，直到 `completed` 并取得 `result_video_path`（或失败时按 `status/msg` 提示处理）。