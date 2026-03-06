---
name: email-monitor
description: 邮件自动监控系统，自动回复客户咨询，过滤垃圾邮件，商机邮件飞书通知。
metadata:
  {"openclaw": {"emoji": "📧", "requires": {"bins": ["python"]}, "primaryEnv": "FEISHU_APP_ID"}}
---

# Email Monitor - 邮件自动监控

**坐等订单上门！**

自动监控邮箱，自动回复客户咨询，自动过滤垃圾邮件，商机邮件飞书通知你！

---

## 🎯 使用场景

- **自动获客** - 客户咨询自动回复
- **订单确认** - 收款后自动确认
- **垃圾过滤** - 自动过滤广告/推销
- **飞书通知** - 商机邮件实时通知

---

## 🛠️ 核心功能

### 1. 邮件监控
- ✅ 支持 QQ/163/Gmail 邮箱
- ✅ 每 30 分钟自动检查
- ✅ 自动分类（优先/咨询/验证/垃圾）

### 2. 自动回复
- ✅ 中英双语回复
- ✅ 自定义回复模板
- ✅ 发送频次控制（防封号）

### 3. 商机识别
- ✅ 关键词匹配（定制/开发/报价）
- ✅ 飞书实时通知
- ✅ 自动记录客户信息

### 4. 垃圾过滤
- ✅ 自动识别垃圾邮件
- ✅ 自动移动到垃圾箱
- ✅ 白名单机制

---

## 📋 配置说明

### 1. 邮箱配置
```json
{
  "email": {
    "address": "你的邮箱",
    "imap": {
      "host": "imap.qq.com",
      "port": 993,
      "auth": {
        "user": "你的邮箱",
        "pass": "授权码"
      }
    }
  }
}
```

### 2. 飞书通知（可选）
```json
{
  "notifyFeishu": true,
  "feishuWebhook": "你的 webhook 地址"
}
```

---

## 💰 定价 Pricing

| 版本 | 价格 | 功能 |
|------|------|------|
| **标准版 Standard** | 免费 Free | 基础监控 + 自动回复 |
| **专业版 Pro** | $50/month (¥350/月) | 多邮箱 + 飞书通知 + 数据统计 |
| **定制版 Custom** | $1000-3000 (¥7000-20000) | 私有化部署 + 功能定制 |

---

## 📧 联系 Contact

**定制开发 Custom Development：**
- 📧 邮箱 Email：1776480440@qq.com
- 💬 微信 WeChat：私信获取 DM for details

**支持支付 Payment：**
- 国内 Domestic：私信获取
- 国际 International：私信获取（PayPal/Wise）

**售后支持 After-Sales：**
- 首年免费维护 Free for 1st year
- 次年 $100/年 (¥700/年) optional

---

## 🎯 案例展示 Cases

### 案例 1：自动化获客系统
- **客户：** 自由开发者
- **需求：** 自动回复客户咨询
- **方案：** Email Monitor + GitHub 监控
- **结果：** 月入 1W+，零人工干预

---

## 🚀 更新日志 Changelog

### v1.0.4 (2026-03-05)
- 初始发布
- 支持多邮箱监控
- 自动回复（中英双语）
- 飞书通知集成

---

**技能来源 Source：** https://clawhub.ai/sukimgit/email-monitor
**作者 Author：** Monet + 老高
**许可 License：** MIT
