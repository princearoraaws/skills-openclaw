---
name: wdangz-doc-converter
description: 调用文档转换全能王(https://www.wdangz.com)API进行文档格式转换。支持PDF/Word/Excel/PPT/图片等格式互转，OCR识别，PDF合并拆分加密等。转换完成后自动下载到原文件目录。
---

# 📄 文档转换全能王

调用 [文档转换全能王](https://www.wdangz.com) API 实现专业文档格式转换。

## ⚠️ 重要安全须知

**使用此工具前，请务必了解以下风险：**

| 风险类型 | 说明 |
|---------|------|
| 📤 **数据上传** | 文件将上传到 `https://www.wdangz.com` 进行转换 |
| 🔒 **隐私风险** | 请勿上传包含敏感信息、机密数据或受监管文档 |
| 💼 **商业机密** | 涉及商业秘密的文档请使用本地转换工具 |
| 🏥 **个人隐私** | 包含个人身份信息(PII)的文档请谨慎处理 |

**建议在以下情况下使用：**
- ✅ 公开文档、普通办公文档
- ✅ 已脱敏的处理后文档
- ✅ 非敏感的格式转换需求

**不建议用于：**
- ❌ 财务报表、合同文件
- ❌ 身份证件、银行卡照片
- ❌ 公司内部机密文档
- ❌ 包含个人隐私的文件

---

## ✨ 支持的转换

| 转换类型 | 示例 |
|----------|------|
| Word → PDF | "docx转PDF" |
| Excel → PDF | "xlsx转PDF" |
| PPT → PDF | "ppt转PDF" |
| PDF → Word | "PDF转Word" |
| PDF → Excel | "PDF转Excel" |
| PDF → 图片 | "PDF转图片" |
| 图片 → Word (OCR) | "图片转Word" |
| 图片 → Excel (OCR) | "图片转Excel" |
| PDF合并 | "合并PDF" |
| PDF拆分 | "拆分PDF" |
| PDF水印 | "添加水印" |
| PDF加密/解密 | "加密PDF" / "解密PDF" |

---

## 🚀 使用方式

直接告诉我：
1. **文件路径** - 例如 `E:\doc\report.docx`
2. **目标格式** - 例如 "转成PDF"、"转为Word"

**示例：**
- "把 E:\doc\报告.docx 转换成 PDF"
- "将 report.pdf 转成 Word"
- "帮我把这个Excel转成PDF"
- "PDF文件添加水印"

---

## 📥 输出

转换后的文件自动保存到 **原文件同一目录**。

---

## ⚙️ 配置 API Key

**首次使用必须配置 API Key！**

### 获取 API Key 步骤
1. 访问 [文档转换全能王](https://www.wdangz.com) 注册账号
2. 在官网菜单中找到 **「API服务」** 菜单并点击进入
3. 按照页面提示开通 API 服务
4. 获取 API Key 后进行配置

### 配置方式（推荐程度排序）

#### 方式一：环境变量（最安全 ✅ 推荐）
```bash
# Windows (临时)
set WDANGZ_API_KEY=你的API密钥

# Windows (永久 - 系统环境变量)
# 此电脑 → 属性 → 高级系统设置 → 环境变量 → 新建

# Linux/Mac
export WDANGZ_API_KEY=你的API密钥
```

#### 方式二：配置文件（需注意安全）
编辑 `config.txt` 文件：
```
WDANGZ_API_KEY=你的API密钥
```
⚠️ 注意：确保配置文件不被提交到版本控制系统

---

## 📋 技术细节

| 项目 | 说明 |
|-----|------|
| API端点 | `https://www.wdangz.com/api/v1/convert` |
| 文件限制 | 单文件最大 50MB |
| 支持格式 | doc, docx, xls, xlsx, ppt, pptx, pdf, jpg, png, bmp, gif, webp |

---

💡 **Tip:** 只需用自然语言描述你要做什么，我会自动识别转换类型！
