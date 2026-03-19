---
name: article-publisher
description: 自媒体文章多平台发布工具，支持知乎、Bilibili、百家号、头条号、小红书等平台的一键发布。使用Playwright实现浏览器自动化，支持扫码登录和Cookie持久化。首次使用会自动安装依赖。
version: 1.2.6
author: OpenClaw
license: GPL-3.0
keywords:
  - 自媒体
  - 文章发布
  - 知乎
  - Bilibili
  - 百家号
  - 头条号
  - 小红书
  - Playwright
  - 自动化
---

# 自媒体文章发布工具

这是一个OpenClaw Skill，用于将文章自动发布到多个自媒体平台。

## 支持的平台

- 知乎 (zhihu.com)
- Bilibili (bilibili.com)
- 百家号 (baijiahao.baidu.com)
- 头条号 (mp.toutiao.com)
- 小红书 (xiaohongshu.com)

## 主要功能

1. **自动安装依赖** - 首次使用自动检测并安装所需依赖
2. **扫码登录** - 打开浏览器扫码登录各平台，自动保存Cookie
3. **登录状态检查** - 检查各平台的登录状态
4. **文章发布** - 将文章发布到指定平台或所有已登录平台
5. **Cookie管理** - 持久化存储登录状态，免重复登录，所有信息均存放在你的电脑上，确保安全和隐私

## 使用方法

### 0. 首次使用（自动安装）

首次使用时，系统会自动检测并安装依赖，无需手动操作。

### 1. 登录平台

```
请帮我登录知乎
```

### 2. 检查登录状态

```
检查我的登录状态
```

### 3. 发布文章

```
帮我发布一篇文章到知乎，标题是"xxx"，内容是"xxx"
```

### 4. 一键发布到所有平台

```
把这篇文章发布到所有已登录的平台
```

## 注意事项

- 首次使用需要手动安装依赖（见下方安装说明）
- 需要扫码登录各平台
- Cookie有效期一般为7-30天，过期后需重新登录
- 发布时请确保文章内容符合各平台规范

## 安装依赖

首次使用前，请运行以下命令安装依赖：

```bash
# 安装 npm 依赖
npm install --registry=https://registry.npmmirror.com

# 安装 Playwright 浏览器
npm run install:browser:cn
# 或者
npx playwright install chromium
```

## 安全说明

本工具使用 Playwright 进行浏览器自动化，所有操作均在本地执行：

本工具**不会**：
- 执行任意用户输入的代码
- 上传用户数据到第三方服务器
- 包含任何恶意代码或后门

所有网络请求仅限于目标自媒体平台的官方接口。
