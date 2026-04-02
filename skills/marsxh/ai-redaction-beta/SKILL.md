---
name: ai-redaction
description: 脱敏用户上传的文件，支持自定义脱敏指令，处理完成后返回查询链接，可查看处理进度和下载结果
author: LianWei
version: 1.0.0
triggers:
  - "脱敏文件"
  - "文件脱敏"
  - "AI脱敏"
  - "redact file"
  - "ai-redaction"
metadata:
  clawdbot:
    emoji: 📁
    requires:
      bins: ["node", "npm"]
      nodeVersion: ">=18.0.0"
    config:
      env:
        apiKey:
          description: API key for authentication
          required: true
          secret: true
          persistent: true
---

# AI Redaction

智能脱敏工具，接收用户上传的文件和脱敏指令，自动处理后返回查询链接，可查看处理进度和下载结果。

## 功能

- 接收单个文件并识别文件类型
- 根据脱敏指令执行处理
- 返回查询链接，可查看处理进度和下载结果
- 支持多种文件格式

## 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file` | string | 是 | 待处理的文件路径或上传的文件 |
| `instruction` | string | 是 | 脱敏指令，如：`涂黑身份证号`、`移除电话号码` |
| `apiKey` | string | 是 | API 密钥，首次配置后自动持久化 |

## 使用方法

### 命令行调用

```bash
ai-redaction --file "document.pdf" --instruction "涂黑身份证号"
```

### API 调用

```javascript
const result = await aiRedaction({
  file: "document.pdf",
  instruction: "涂黑身份证号"
});
// 返回: { taskUrl: "https://...", taskId: "xxx", status: "已提交" }
```

## 配置

API key 会在首次使用时提示输入，配置后自动持久化保存。

### 查看配置

```bash
openclaw config get skills.ai-redaction.apiKey
```

### 修改配置

```bash
openclaw config set skills.ai-redaction.apiKey <your-new-api-key>
```

### 重置配置

```bash
openclaw config unset skills.ai-redaction.apiKey
```

配置文件位置：
- **macOS/Linux**: `~/.openclaw/openclaw.json`
- **Windows**: `%USERPROFILE%\.openclaw\openclaw.json`

## 返回值

| 字段 | 类型 | 说明 |
|------|------|------|
| `taskUrl` | string | 查询链接，可在网页中查看处理进度和下载结果 |

## 常见脱敏指令示例

- `涂黑身份证号`
- `移除电话号码`
- `模糊人脸区域`
- `隐藏银行卡号`
- `删除邮箱地址`

## 限制说明

- 仅支持单个文件处理
- 支持的文件格式：PDF、图片（PNG/JPG/JPEG）、Word、Excel、TXT
- 单文件大小限制：10MB
- 处理超时时间：5 分钟



## 回复模板

- 文件：`test.txt`
- 脱敏指令：`涂黑身份证号`
- 查询链接：`https://...`

打开查询链接可查看进度和下载结果。

## ⚠️ 强制规则

不要回复 API Key 、状态、日志。
