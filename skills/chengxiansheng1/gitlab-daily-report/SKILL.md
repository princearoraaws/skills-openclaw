---
name: gitlab-daily-report
description: 自动拉取 GitLab 团队每日提交记录，汇总成报告推送到飞书群机器人。当用户需要生成团队提交汇总报告、配置每日自动化任务、或将提交记录推送到飞书时使用此技能。
---

# GitLab 团队每日提交汇总

## Overview

本技能用于自动化收集 GitLab 团队成员的每日代码提交，生成格式化的汇总报告，并通过飞书群机器人推送到指定群组。支持配置多个仓库、定时任务自动执行。

## 使用场景

1. **生成每日提交汇总**：自动拉取当日所有提交，按成员和仓库分组展示
2. **推送到飞书**：将汇总结果以富文本卡片形式推送到飞书群
3. **配置定时任务**：设置自动化定时执行（如每天下班前）

## 快速开始

### 1. 配置脚本

进入 skill 目录并复制配置模板：

```bash
cd skills/gitlab-daily-report/scripts/
cp config.example.json config.json
```

### 2. 填写配置

编辑 `config.json`，填入以下信息：

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `gitlab_url` | GitLab 实例地址 | `https://gitlab.yourcompany.com` |
| `gitlab_token` | Personal Access Token | 在 GitLab 个人设置中生成 |
| `repositories` | 要监控的仓库列表 | `["team/project-a", "team/project-b"]` |
| `feishu_webhooks` | 飞书机器人 Webhook 地址 | `https://open.feishu.cn/open-apis/bot/v2/hook/xxx` |
| `timezone_offset` | 时区偏移（小时） | `8`（中国时区） |

**获取 GitLab Token**：
1. 登录 GitLab → 点击右上角头像 → Preferences
2. 左侧菜单选择 Access Tokens
3. 创建新 Token，勾选 `read_api` 权限

**获取飞书 Webhook**：
1. 飞书群设置 → 群机器人 → 添加机器人 → 自定义机器人
2. 复制 Webhook 地址

### 3. 运行脚本

```bash
python gitlab_report.py
```

脚本会：
1. 拉取配置中所有仓库当日的提交记录
2. 按成员和仓库分组汇总
3. 本地打印预览
4. 推送到飞书群

## 配置定时任务（可选）

### Windows 计划任务

```powershell
# 每天 18:00 执行
schtasks /create /tn "GitLab Daily Report" /tr "python C:\path\to\gitlab_report.py" /sc daily /st 18:00
```

### 使用 WorkBuddy 自动化

可通过 WorkBuddy 的自动化功能配置每周一至周五下午6点执行：

```
FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=18;BYMINUTE=0
```

## 输出示例

脚本运行后会输出类似以下格式：

```
👤 张三（3 条）
  📁 project-a
    1. feat: 添加用户登录接口
    2. fix: 修复缓存失效问题
  📁 project-b
    1. refactor: 优化数据库查询
👤 李四（2 条）
  📁 project-a
    1. docs: 更新 README
    2. chore: 升级依赖版本
```

飞书收到的消息会格式化为富文本卡片，包含标题、成员头像（emoji）、仓库名称和提交标题。

## 脚本说明

- **支持私有部署 GitLab**：自动忽略自签名证书
- **跨分支去重**：遍历所有分支，按 commit ID 自动去重
- **过滤 Merge 提交**：自动跳过以 "Merge" 开头的提交标题
- **多仓库支持**：可同时监控多个仓库
- **多 Webhook**：支持推送到多个飞书群

## 依赖

- Python 3.7+
- 无需额外安装依赖（仅使用标准库）

## 常见问题

**Q: 提示 "配置文件不存在"**
A: 需要将 `config.example.json` 复制为 `config.json` 并填入真实配置

**Q: GitLab API 请求失败**
A: 检查 `gitlab_url` 是否正确、Token 是否有 `read_api` 权限、是否可访问 GitLab

**Q: 提交数量为 0**
A: 确认仓库路径正确，或当日确实没有提交记录

**Q: 飞书消息发送失败**
A: 检查 Webhook 地址是否正确、群机器人是否启用
