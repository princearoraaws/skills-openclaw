---
name: xiangqin
description: 帮助用户管理相亲资料、查找匹配对象、生成开场白与聊天话题、记录互动进展，并提供约会与安全提醒。用于用户明确提到相亲、找对象、脱单、婚恋匹配、开场白、聊天建议、约会建议、接触记录、相亲安全等场景。
---

# Xiangqin

使用这个 skill 时，先把它当作一个本地辅助工具，而不是婚恋平台后端。

## 执行原则

- 先确认用户的目标：是完善资料、找匹配、生成话术、记录进展，还是看安全提醒。
- 明确告知这是本地原型工具，结果仅供参考，不应被表述为“平台级智能推荐”。
- 涉及隐私时，默认最小暴露；不要主动输出手机号、微信号、住址等敏感信息。
- 涉及见面、转账、投资、借钱、裸聊、索要验证码等情况时，优先输出安全提醒。
- 不要声称已经实现加密、照片水印、实名核验等未实现能力。

## 可用能力

- 创建和查看个人资料
- 根据已有资料做基础匹配排序
- 生成开场白
- 推荐聊天话题
- 推荐约会形式
- 记录接触历史
- 输出相亲安全提醒

## 运行方式

优先使用 CLI：

```bash
node scripts/cli.js safety
node scripts/cli.js 资料 <用户ID>
node scripts/cli.js 资料 <用户ID> 创建 '<资料JSON>'
node scripts/cli.js 匹配 <用户ID> [数量]
node scripts/cli.js 开场白 <用户ID> <对方ID>
node scripts/cli.js 话题 [initial|middle|advanced]
node scripts/cli.js 约会 [城市]
node scripts/cli.js 记录 <用户ID> <对方ID> <内容>
node scripts/cli.js 历史 <用户ID> <对方ID>
```

## 资料输入建议

创建资料时，至少包含：

- nickname
- gender
- birthYear
- height
- location
- education
- occupation

可选字段：

- income
- hometown
- hobbies
- values
- selfDescription
- ageRange
- locationPreference
- educationPreference
- otherRequirements

字段说明和建议流程详见 `references/fields-and-workflows.md`

## 数据边界

- 当前数据保存在本地目录 `~/.openclaw/skills-data/xiangqin/`
- 当前版本使用本地 JSON 文件保存数据
- 当前版本**未实现**字段级加密、照片水印、实名核验、联系方式交换控制
- 因此输出时要避免夸大安全能力，并提醒用户谨慎提供敏感信息
- 隐私与输出边界详见 `references/privacy-and-boundaries.md`

## 结果表述要求

- 把匹配结果表述为“基础规则匹配结果”或“本地推荐结果”
- 不要把分数说成真实成功率
- 若样本不足，要明确说“当前资料库候选人不足”
- 若资料不完整，先建议补齐资料再做推荐

## 安全要求

遇到以下场景时，优先提醒风险：

- 第一次见面要求去私密空间
- 很快借钱、带投资、带博彩、带虚拟币
- 拒绝视频却急于推进关系
- 索要身份证、银行卡、验证码
- 诱导裸聊、屏幕共享、下载可疑 App

必要时直接运行：

```bash
node scripts/cli.js safety
```

## 测试

运行最小测试：

```bash
node test.js
```

测试应覆盖：

- 创建资料
- 查看资料
- 双人匹配
- 开场白生成
- 接触记录
- 安全提醒
