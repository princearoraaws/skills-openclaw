#!/usr/bin/env python3
"""
GitLab 团队每日提交汇总 → 飞书群机器人推送
"""

import json
import os
import sys
import ssl
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timedelta, timezone
from collections import defaultdict

# 忽略自签名证书（私有部署 GitLab 常见）
_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

# ── 读取配置 ──────────────────────────────────────────────
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"[错误] 配置文件不存在: {CONFIG_FILE}")
        print("请先复制 config.example.json 为 config.json 并填写相关信息。")
        sys.exit(1)
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)

# ── GitLab API ────────────────────────────────────────────
def gitlab_get(config, path):
    """调用 GitLab API，返回解析后的 JSON。"""
    url = f"{config['gitlab_url'].rstrip('/')}/api/v4{path}"
    req = urllib.request.Request(url, headers={"PRIVATE-TOKEN": config["gitlab_token"]})
    try:
        with urllib.request.urlopen(req, timeout=15, context=_SSL_CTX) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"[错误] GitLab API 请求失败 {url}: {e.code} {e.reason}")
        return None
    except Exception as e:
        print(f"[错误] 请求异常 {url}: {e}")
        return None

def get_project_id(config, repo):
    """根据仓库路径（namespace/project）获取 project id。"""
    encoded = urllib.parse.quote(repo, safe="")
    data = gitlab_get(config, f"/projects/{encoded}")
    if data:
        return data["id"]
    return None

def get_branches(config, project_id):
    """获取仓库所有分支名。"""
    branches = []
    page = 1
    while True:
        data = gitlab_get(config, f"/projects/{project_id}/repository/branches?per_page=100&page={page}")
        if not data:
            break
        branches.extend([b["name"] for b in data])
        if len(data) < 100:
            break
        page += 1
    return branches

def get_today_commits(config, project_id, since_iso, until_iso):
    """获取指定时间段内所有分支的提交，按 commit id 去重。"""
    seen = set()
    commits = []
    branches = get_branches(config, project_id)
    for branch in branches:
        branch_enc = urllib.parse.quote(branch, safe="")
        page = 1
        while True:
            path = (
                f"/projects/{project_id}/repository/commits"
                f"?ref_name={branch_enc}&since={since_iso}&until={until_iso}&per_page=100&page={page}"
            )
            data = gitlab_get(config, path)
            if not data:
                break
            for c in data:
                if c["id"] not in seen:
                    seen.add(c["id"])
                    commits.append(c)
            if len(data) < 100:
                break
            page += 1
    return commits

# ── 构建报告 ──────────────────────────────────────────────
def build_report(config):
    import urllib.parse  # noqa: F401 (needed inside get_project_id)

    # 今天 00:00 ~ 23:59:59（本地时区，转为 UTC ISO 发给 GitLab）
    tz_offset = config.get("timezone_offset", 8)  # 默认东八区
    local_tz = timezone(timedelta(hours=tz_offset))
    now_local = datetime.now(local_tz)
    today_start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end   = now_local.replace(hour=23, minute=59, second=59, microsecond=0)
    since_iso = today_start.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    until_iso = today_end.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    date_label = now_local.strftime("%m.%d")

    # 按作者 → 仓库 → commit 列表
    author_repo_commits: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    total = 0

    for repo in config["repositories"]:
        project_id = get_project_id(config, repo)
        if not project_id:
            print(f"[警告] 找不到仓库: {repo}，跳过")
            continue
        repo_name = repo.split("/")[-1]
        commits = get_today_commits(config, project_id, since_iso, until_iso)
        for c in commits:
            title = c.get("title", "").strip()
            if not title or title.startswith("Merge"):
                continue
            author = c.get("author_name") or c.get("committer_name") or "Unknown"
            author_repo_commits[author][repo_name].append(title)
            total += 1

    return author_repo_commits, date_label, total

# ── 格式化消息 ────────────────────────────────────────────
def format_feishu_message(author_repo_commits, date_label, total):
    """生成飞书富文本卡片内容（post 类型）。"""
    if not author_repo_commits:
        return {
            "msg_type": "text",
            "content": {"text": f"📋 {date_label} 今日团队提交汇总\n\n今日暂无任何提交记录。"}
        }

    # 构建 post 富文本
    content_lines = []
    for author, repos in sorted(author_repo_commits.items()):
        commit_count = sum(len(v) for v in repos.values())
        # 作者标题行
        content_lines.append([
            {"tag": "text", "text": f"👤 {author}（{commit_count} 条）"}
        ])
        for repo_name, titles in sorted(repos.items()):
            content_lines.append([
                {"tag": "text", "text": f"  📁 {repo_name}"}
            ])
            for i, title in enumerate(titles, 1):
                content_lines.append([
                    {"tag": "text", "text": f"    {i}. {title}"}
                ])
        content_lines.append([{"tag": "text", "text": ""}])  # 空行间隔

    return {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": f"📋 {date_label} 今日团队提交汇总（共 {total} 条）",
                    "content": content_lines
                }
            }
        }
    }

# ── 飞书推送 ──────────────────────────────────────────────
def send_feishu(webhook_url, message):
    data = json.dumps(message).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15, context=_SSL_CTX) as resp:
            result = json.loads(resp.read().decode())
            if result.get("code") == 0 or result.get("StatusCode") == 0:
                print("✅ 飞书消息发送成功")
            else:
                print(f"[警告] 飞书返回异常: {result}")
    except Exception as e:
        print(f"[错误] 飞书推送失败: {e}")

# ── 主流程 ────────────────────────────────────────────────
def main():
    import urllib.parse  # noqa: F811

    config = load_config()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始拉取 GitLab 提交记录...")

    author_repo_commits, date_label, total = build_report(config)
    print(f"共汇总 {total} 条提交，涉及 {len(author_repo_commits)} 位成员")

    message = format_feishu_message(author_repo_commits, date_label, total)

    # 本地预览
    print("\n── 报告预览 ──────────────────────────────────")
    for author, repos in sorted(author_repo_commits.items()):
        cnt = sum(len(v) for v in repos.values())
        print(f"👤 {author}（{cnt} 条）")
        for repo_name, titles in sorted(repos.items()):
            print(f"  📁 {repo_name}")
            for i, t in enumerate(titles, 1):
                print(f"    {i}. {t}")
    print("──────────────────────────────────────────────\n")

    # 发送飞书（Webhook 未配置时跳过）
    for webhook in config["feishu_webhooks"]:
        if webhook.startswith("http"):
            send_feishu(webhook, message)
        else:
            print("⚠️  飞书 Webhook 未配置，跳过推送。请在 config.json 中填写 feishu_webhooks。")

if __name__ == "__main__":
    main()
