---
name: qstar-video-ecom
version: 1.0.1
author: qstar
emoji: "🎬"
tags:
  - video
  - ecommerce
  - ai-video
  - chinese
description: >
  一键生成带中文解说的电商产品视频，支持淘宝、小红书、抖音等六大平台。
  内置 AI 视频生成 + 中文 TTS 解说 + 平台专属参数。免费每天1次，充值后不限量。
---

# 🎬 电商 Sora 视频生成

**触发条件**：用户说「帮我生成视频」「做个产品视频」「生成电商视频」等。

---

## Step 0 — 提取用户 ID

从当前 session key 提取平台和 sender_id，拼成 `{platform}:{sender_id}`。

session key 格式：`agent:main:{platform}:{chattype}:{sender_id}`

示例：
- `agent:main:telegram:direct:5239705501` → `tg:5239705501`
- `agent:main:wechat:direct:oh8CU6xxx` → `wx:oh8CU6xxx`
- `agent:main:wecom:direct:zhangsan` → `wecom:zhangsan`
- `agent:main:feishu:direct:ou_xxx` → `feishu:ou_xxx`
- `agent:main:slack:direct:U12345` → `slack:U12345`

```bash
# 获取 session key（从上下文读取，不需要 exec）
USER_ID="{platform}:{sender_id}"  # 替换为实际值
```

---

## Step 1 — 首次问卷（仅新用户）

```bash
curl -s https://bot.guanma.top/sora-api/user/profile/{USER_ID}
```

若 `onboarded: false`，先发送开场白，再依次询问：

**开场白**（必须完整发出）：
```
🎬 欢迎使用 AI 电商视频生成！

📌 使用须知：
• 免费版：每天 1 次，仅支持通用商品视频（AI 根据文字描述生成画面）
• 付费版：不限次数，支持上传产品实拍图，生成专属个性化视频

个性化商品（有特定外观/颜色/款式要求）建议使用付费版，效果更贴合实际产品。
```

依次向用户询问：

1. 「你主要在哪个平台经营？（淘宝/小红书/抖音/其他）」
2. 「你的主营产品类目是？（服装/数码/美妆/食品/其他）」
3. 「你的微信号是？（方便后续服务，可跳过）」

收集后：

```bash
curl -s -X POST https://bot.guanma.top/sora-api/user/onboard \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "{USER_ID}",
    "main_platform": "{用户回答1}",
    "category": "{用户回答2}",
    "contact": "{用户回答3}"
  }'
```

---

## Step 2 — 选择发布平台

发送给用户：

```
请选择视频发布平台：
1️⃣ 淘宝/天猫（16:9，8秒）
2️⃣ 拼多多（16:9，4秒）
3️⃣ 小红书（9:16，8秒）
4️⃣ 抖音/TikTok（9:16，8秒）
5️⃣ 京东（16:9，8秒）
6️⃣ 视频号（9:16，8秒）
```

platform key 映射：1→taobao 2→pinduoduo 3→xiaohongshu 4→douyin 5→jingdong 6→shipinhao

---

## Step 3 — 获取产品描述

「请描述你的产品和核心卖点（例：索尼降噪耳机，主打主动降噪，目标人群职场白领）」

---

## Step 4 — 选择声音

「请选择解说声音：
🎙️ 1. 晓晓（女声·温柔）
🎙️ 2. 云希（男声·稳重）」

voice key 映射：1→female 2→male

---

## Step 5 — 产品图上传（付费用户专属）

先查询用户配额：
```bash
curl -s https://bot.guanma.top/sora-api/quota/{USER_ID}
```

**若 `credits > 0`（付费用户）**，询问：
「📸 是否上传产品实拍图？上传后视频将基于你的真实产品生成，效果更准确。
直接发图即可，或回复「跳过」使用通用风格。」

- 用户发图 → 将图片保存到本地后上传：
  ```bash
  curl -s -X POST "https://bot.guanma.top/sora-api/upload-image?user_id={USER_ID}" \
    -F "file=@{本地图片路径}"
  ```
  从返回 JSON 取 `image_url`

- 用户回复「跳过」或免费用户 → `image_url` 留空

---

## Step 6 — 生成视频

告知用户「正在生成，约需 3 分钟，请稍候...」

```bash
curl -s -X POST https://bot.guanma.top/sora-api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "{USER_ID}",
    "platform": "{platform_key}",
    "product": "{产品描述}",
    "voice": "{voice_key}",
    "image_url": "{产品图URL或空字符串}"
  }' \
  --max-time 400
```

**若返回 HTTP 200**：
- 有产品图：「🎬 个性化视频已生成！基于你的产品图定制。剩余次数：{quota_remaining}」
- 无产品图：「🎬 通用视频已生成！今日免费次数已用完，充值后可上传产品图生成专属视频。」

**若返回 HTTP 402（quota_exceeded）**：
→ 执行 Step 7 支付流程

---

## Step 7 — 支付充值（配额不足时）

### 7.1 展示套餐

发送给用户：
```
今日免费次数已用完 😅

升级付费版，解锁：
✅ 不限次数生成
✅ 上传产品实拍图，生成专属个性化视频
✅ 效果更贴合真实商品

选择套餐：
1️⃣ 5次视频 · ¥39
2️⃣ 10次视频 · ¥69（最划算）
3️⃣ 20次视频 · ¥128
```

### 7.2 选择支付方式

「请选择支付方式：
💚 1. 微信支付
💙 2. 支付宝」

channel 映射：1→wechat 2→alipay

### 7.3 创建订单，发送二维码

```bash
RESP=$(curl -s -X POST "https://bot.guanma.top/sora-api/pay/create?user_id={USER_ID}&package={price}&channel={channel}")
ORDER_ID=$(echo "$RESP" | jq -r '.order_id')
AMOUNT=$(echo "$RESP" | jq -r '.amount')
QR_URL=$(echo "$RESP" | jq -r '.qr_url')
```

先发二维码图片（直接发 URL，Telegram 会渲染为图片）：
```
{QR_URL}
```

紧接着发文字说明：
```
请扫码完成支付 👆
订单号：{ORDER_ID}
金额：¥{AMOUNT}

支付完成后系统自动到账，无需截图，稍等片刻即可继续生成视频。
```

### 7.4 轮询支付结果

每 10 秒查询一次，最多查询 18 次（3分钟）：

```bash
curl -s https://bot.guanma.top/sora-api/pay/status/{order_id}
```

若 `status == "paid"`：
「✅ 支付成功！已为你到账 {credits} 次视频额度，现在可以上传产品图生成专属视频了！」
→ 返回 Step 5 重新执行（此时 credits > 0，会询问是否上传产品图）

若超时：
「支付还未到账，可稍后发送「继续生成」重试。」

---

## 注意事项

- 生成耗时约 3 分钟，期间可告知用户进度
- 所有生成的视频已存档到七牛云，用于后续模板制作
- 用户 ID 格式必须是 `{platform}:{sender_id}`，确保跨平台配额独立
