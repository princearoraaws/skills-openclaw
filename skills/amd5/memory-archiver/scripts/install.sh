#!/bin/bash
# Memory Manager Skill - 安装脚本
# 用法：bash scripts/install.sh

set -e

WORKSPACE="${HOME}/.openclaw/workspace"
MEMORY_DAILY="${WORKSPACE}/memory/daily"
MEMORY_HOURLY="${WORKSPACE}/memory/hourly"
MEMORY_WEEKLY="${WORKSPACE}/memory/weekly"

echo "🔧 开始安装 Memory Manager Skill..."

# 确保目录存在
mkdir -p "$MEMORY_DAILY" "$MEMORY_HOURLY" "$MEMORY_WEEKLY"

echo "✅ 目录结构已准备"

# 提示用户手动添加 cron 任务 (OpenClaw cron add 需要交互式确认)
echo ""
echo "📋 请手动添加以下 cron 任务："
echo ""
echo "1️⃣  记忆及时写入 (10 分钟)"
echo "   openclaw cron add --name \"记忆及时写入\" --schedule '{\"kind\":\"every\",\"everyMs\":600000}' --payload '{\"kind\":\"systemEvent\",\"text\":\"📝 记忆及时写入检查...\"}' --session-target main"
echo ""
echo "2️⃣  记忆同步 - Hourly (每小时)"
echo "   openclaw cron add --name \"记忆同步 - Hourly\" --schedule '{\"kind\":\"every\",\"everyMs\":3600000}' --payload '{\"kind\":\"systemEvent\",\"text\":\"🕐 每小时记忆同步时间！...\"}' --session-target main"
echo ""
echo "3️⃣  记忆归档 - Daily (每天 23:00)"
echo "   openclaw cron add --name \"记忆归档 - Daily\" --schedule '{\"kind\":\"cron\",\"expr\":\"0 23 * * *\",\"tz\":\"Asia/Shanghai\"}' --payload '{\"kind\":\"systemEvent\",\"text\":\"🌙 每日记忆归档时间！...\"}' --session-target main"
echo ""
echo "4️⃣  记忆总结 - Weekly (每周日 22:00)"
echo "   openclaw cron add --name \"记忆总结 - Weekly\" --schedule '{\"kind\":\"cron\",\"expr\":\"0 22 * * 0\",\"tz\":\"Asia/Shanghai\"}' --payload '{\"kind\":\"systemEvent\",\"text\":\"📅 每周记忆总结时间！...\"}' --session-target main"
echo ""
echo "✅ 安装完成！请查看 SKILL.md 获取详细使用说明"
