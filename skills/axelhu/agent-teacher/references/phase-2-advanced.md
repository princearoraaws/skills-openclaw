# 进阶课程详解

## 搜索与信息获取

### multi-search-engine（多引擎搜索）

**用途**：搜索中文/英文网络资源，支持 17 种搜索引擎

**安装**：`clawhub install multi-search-engine --dir skills`

**核心用法**：
- 支持百度、Bing、Google、搜狗等
- 支持 `site:` 搜索特定网站
- 支持时间过滤（day/week/month/year）
- 支持 `intitle:` 标题搜索

**验证**：能搜索"上海今天天气"并给出准确结果

### duckduckgo-search（隐私搜索）

**用途**：不记录隐私的搜索引擎

**安装**：`clawhub install duckduckgo-search --dir skills`

**核心用法**：
- 不需要 API key
- 适合搜索敏感话题
- 返回标题、链接、摘要

**验证**：能用 duckduckgo 搜索并返回结果

### minimax-web-search（MiniMax 网络搜索）

**用途**：中文友好的网络搜索，质量高于 Brave Search

**说明**：优先于默认的 `web_search`（Brave）使用，中文内容结果更准确

**核心用法**：
```bash
mcporter call --stdio "uvx minimax-coding-plan-mcp -y" \
  --env MINIMAX_API_KEY=你的key \
  --env MINIMAX_API_HOST=https://api.minimaxi.com \
  web_search query:"搜索内容"
```

**特点**：
- 中文搜索结果质量高
- 支持时间过滤（ freshness 参数）
- 返回标题、链接、摘要、日期

**验证**：搜索"今天上海天气"能返回准确结果

**注意**：API Key 填入 `你的key` 占位符，实际运行时由调用方替换为真实密钥。

---

## 浏览器控制

### browser（浏览器控制）

**用途**：控制 Chrome 浏览器，打开网页、截图、分析页面

**安装**：OpenClaw 内置（需启用）

**核心用法**：
```javascript
browser({ action: "open", url: "https://example.com" })
browser({ action: "snapshot" })
browser({ action: "screenshot" })
browser({ action: "act", kind: "click", ref: "..." })
```

**两种模式**：
- `profile="openclaw"`：OpenClaw 自己管理的隔离浏览器
- `profile="chrome"`：控制你已有的 Chrome 标签页（需安装 Chrome 扩展）

**验证**：能用 browser 打开一个网页并截图

---

## 外部服务调用

### mcporter（MCP 工具调用）

**用途**：调用外部 API 和工具服务，如 MiniMax 图片/视频生成

**安装**：需单独配置 MiniMax API key

**核心用法**：
```bash
mcporter call --stdio "npx -y minimax-mcp-js" \
  --env MINIMAX_API_KEY=你的key \
  text_to_image prompt:"描述文字"
```

**常用工具**：
| 工具 | 用途 |
|------|------|
| `text_to_image` | 图片生成 |
| `text_to_video` | 视频生成 |
| `text_to_audio` | TTS 语音 |
| `voice_clone` | 声音克隆 |

**验证**：能生成一张图片

---

## 视觉输出

### canvas（画布控制）

**用途**：生成图片、PPT 等视觉内容

**安装**：OpenClaw 内置

**核心用法**：
```javascript
canvas({ action: "present", url: "data:image/png;base64,..." })
canvas({ action: "snapshot" })
```

**验证**：能用 canvas 生成一张图片

---

## 技能开发

### skill-creator（创建新技能）

**用途**：创建、编辑、改进技能

**安装**：OpenClaw 内置

**核心用法**：按照 AgentSkills 规范创建 SKILL.md + 资源文件

**参考**：`skills/skill-creator/SKILL.md`

### clawhub（技能管理）

**用途**：查找、安装、发布技能

**安装**：`npm install -g clawhub`

**核心用法**：
```bash
clawhub search [关键词]          # 搜索技能
clawhub install [名称] --dir skills   # 安装技能
clawhub publish [路径]          # 发布技能
```

**验证**：能用 clawhub 搜索到一个技能

---

## 进阶课程毕业标准

1. 能用多引擎搜索找到准确信息
2. 能用 minimax web_search 搜索中文内容
3. 能用 browser 打开网页并获取内容
4. 能用 mcporter 生成图片
5. 能用 clawhub 找到并安装一个新技能
