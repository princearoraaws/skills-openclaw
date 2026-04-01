# OpenClaw 记忆系统插件

> OpenClaw 多智能体工作流的持久化记忆系统 — **零外部依赖**，纯 Python BM25 + 关键词索引，DAG 关联图谱，会话生命周期钩子。

[**English**](README.md) · [**日本語**](README_ja.md)

---

## 功能特性

- **BM25 语义搜索** — 纯 Python Okapi BM25 算法，无需任何 pip 包
- **关键词索引** — 快速基于词的索引，支持 `shared` 标记和 Agent 隔离
- **生命周期钩子** — `before-task` 召回 + `after-task` 保存 CLI
- **DAG 关联图谱** — 记忆节点间带类型的双向链接，支持 BFS 路径查找
- **WAL 快照** — 写入后非阻塞索引重建，召回延迟 < 500ms
- **多 Agent 支持** — Agent 作用域隔离记忆 + 跨 Agent 共享记忆

## 安装

```bash
# 从 GitHub 安装
git clone https://github.com/0xcjl/openclaw-memory-plugin.git
openclaw plugins install ./openclaw-memory-plugin

# 或从 ClawhHub 安装（发布后）
openclaw plugins install @0xcjl/openclaw-memory-plugin
```

重启 Gateway：
```bash
openclaw gateway restart
```

## 快速上手

```bash
# 构建索引
./scripts/memory-hook.sh build

# 任务前召回（< 500ms）
./scripts/memory-hook.sh before-task "优化 Vue 渲染性能"

# 任务后保存
./scripts/memory-hook.sh after-task "完成重构" /tmp/result.md

# 记忆搜索
python3 scripts/bm25_search.py --search "Docker CI/CD" --top 5

# 构建 DAG 自动链接
python3 scripts/dag-builder.py build
```

## 项目结构

```
openclaw-memory-plugin/
├── openclaw.plugin.json   # 插件清单
├── scripts/
│   ├── memory-indexer.py  # 关键词索引 + 搜索
│   ├── bm25_search.py      # 纯 Python BM25
│   ├── memory-hook.sh      # 生命周期 CLI
│   ├── dag-builder.py       # DAG 构建
│   └── wal-snapshot.sh     # WAL 快照
├── skills/
│   └── memory-recall/
│       └── SKILL.md
└── docs/
    └── ARCHITECTURE.md
```

## 评分公式

```
combined_score = bm25_norm × 0.6 + weight × 0.2 + keyword_overlap × 0.2
```

| 组成部分 | 范围 | 权重 |
|---------|------|------|
| `bm25_norm` | 0–1 | 60% |
| `weight` | 0–1 | 20% |
| `keyword_overlap` | 0–1 | 20% |

## 记忆 TTL 分类

| 类别 | 含义 | 自动过期 |
|------|------|---------|
| P0 | 核心身份、关键配置 | 永不 |
| P1 | 项目决策、进展 | 约 90 天 |
| P2 | 调试、临时 | 约 30 天 |

## 环境要求

- Python 3（标准库 — **无需任何 pip 包**）
- Bash
- OpenClaw Gateway

## 许可证

MIT
