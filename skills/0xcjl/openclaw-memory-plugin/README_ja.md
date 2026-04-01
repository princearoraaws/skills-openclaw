# OpenClaw メモリシステムプラグイン

> OpenClaw マルチエージェントワークフロー向け永続メモリシステム — **外部依存ゼロ**、ピュアPython BM25 + キーワードインデックス、DAG連想グラフ、セッションライフサイクルフック。

[**English**](README.md) · [**中文**](README_zh.md)

---

## 機能

- **BM25 语义検索** — ピュアPython Okapi BM25実装、pipパッケージ不要
- **キーワードインデックス** — sharedフラグとエージェント分離に対応する高速トークンインデックス
- **ライフサイクルフック** — before-task recall + after-task save CLI
- **DAG連想グラフ** — メモリエントリ間の型付き有向リンク。BFS経路検索
- **WALスナップショット** — 書き込み後のノンブロッキングインデックス再構築
- **マルチエージェント** — エージェントスコープのメモリ分離 + 共有クロスエージェントメモリ

## インストール

```bash
git clone https://github.com/0xcjl/openclaw-memory-plugin.git
openclaw plugins install ./openclaw-memory-plugin
openclaw gateway restart
```

## クイックスタート

```bash
# インデックスビルド
./scripts/memory-hook.sh build

# タスク前のrecall
./scripts/memory-hook.sh before-task "Vueパフォーマンス最適化"

# タスク後の保存
./scripts/memory-hook.sh after-task "Vue最適化完了" /tmp/result.md

# メモリ検索
python3 scripts/bm25_search.py --search "Docker CI/CD" --top 5

# DAGリンクビルド
python3 scripts/dag-builder.py build
```

## 必要環境

- Python 3（標準ライブラリのみ — pipパッケージ不要）
- Bash
- OpenClaw Gateway

## ライセンス

MIT
