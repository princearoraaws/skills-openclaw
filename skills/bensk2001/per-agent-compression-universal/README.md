# Per-Agent Memory Compression Skill (Universal) | 通用代理记忆压缩技能

**Version | 版本**: 1.2.2  
**Purpose | 用途**: Zero-config deployment of weekly memory consolidation for multi-agent OpenClaw systems | 为多代理 OpenClaw 系统提供零配置的每周记忆整合  
**Created | 创建**: 2026-03-18  
**Compatibility | 兼容性**: OpenClaw 2026.3.8+  
**Status | 状态**: ✅ Production Ready (lightly tested) | ✅ 生产就绪（轻量测试）

---

## 🎯 Value Proposition | 价值主张

### Why You Need This | 为什么你需要这个技能

- **⏱️ Saves Hours** - Automates the tedious process of manually reviewing daily notes and updating long-term memory across multiple agents. | **节省时间** - 自动化跨多个代理的手动审查每日笔记和更新长期记忆的繁琐过程。
- **🧠 Better Memory** - Each agent maintains its own contextual memory (USER.md, IDENTITY.md, SOUL.md, MEMORY.md) tailored to its domain, leading to more relevant and personalized interactions. | **更好记忆** - 每个代理维护自己的上下文记忆（USER.md、IDENTITY.md、SOUL.md、MEMORY.md），根据其领域定制，从而实现更相关和个性化的交互。
- **🔄 Self-Healing** - State tracking with `.compression_state.json` means if the task fails midway, it resumes from the last successful note—no duplication, no missing data. | **自愈能力** - 使用 `.compression_state.json` 进行状态跟踪，意味着如果任务中途失败，会从最后一个成功笔记处继续——无重复、无丢失数据。
- **📊 Visibility** - DingTalk summary notifications tell you exactly how many notes were compressed and how many remain for future runs. | **可见性** - 钉钉摘要通知告诉你确切压缩了多少笔记以及未来还剩多少待处理。
- **🚀 Zero Config** - Just run the installer; it auto-discovers all agents and creates staggered tasks. No manual YAML editing. | **零配置** - 只需运行安装程序；它会自动发现所有代理并创建交错任务。无需手动编辑 YAML。

---

## ✨ Key Features | 核心特性

| Feature | English | 中文 |
|---------|---------|------|
| **Auto-Discovery** | Automatically finds all agents with workspaces via `openclaw agents list` | 通过 `openclaw agents list` 自动发现所有带有工作区的代理 |
| **Per-Agent Isolation** | Each agent compresses only its own `memory/` directory and updates its own config files | 每个代理仅压缩自己的 `memory/` 目录并更新自己的配置文件 |
| **State Persistence** | `.compression_state.json` tracks processed notes, last run time, and status | `.compression_state.json` 跟踪已处理笔记、上次运行时间和状态 |
| **Deduplication** | Before appending, checks if the note's date already exists in target files | 追加前检查目标的文件是否已存在该笔记日期，避免重复 |
| **Moved-File Marking** | Processed notes are moved to `memory/processed/` for clear separation | 已处理笔记移动到 `memory/processed/` 以实现清晰分离 |
| **Domain Filtering** | Each task uses DOMAIN_CONTEXT (e.g., "HR/work", "parenting") to guide extraction | 每个任务使用 DOMAIN_CONTEXT（如"HR/工作"、"育儿"）指导提取 |
| **Remaining Notes Report** | Summary announces count of old notes still pending for the next run | 摘要播报下次运行仍待处理的老笔记数量 |
| **Staggered Schedule** | Tasks run on Sundays from 03:00 to 05:00 Shanghai (30min apart) | 任务在周日上海时间 03:00 至 05:00 运行（间隔 30 分钟） |
| **Error Isolation** | One note failing doesn't stop the whole task; errors are logged and continue | 一个笔记失败不会停止整个任务；错误被记录并继续 |
| **DingTalk Notify** | Announces completion summary via dingtalk-connector | 通过钉钉连接器广播完成摘要 |

---

## 📦 Installation | 安装

### Quick Start | 快速开始

```bash
cd /root/.openclaw/workspace
chmod +x skills/per-agent-compression-universal/install.sh
./skills/per-agent-compression-universal/install.sh
```

That's it! The installer will:
- ✅ Verify OpenClaw is running
- ✅ Discover all agents with workspaces
- ✅ Create 1 cron task per agent (staggered schedule)
- ✅ Report any issues

### What Gets Created | 创建内容

For each agent (e.g., `main`, `hrbp`, `parenting`, `decoration`, `memory_master`):
- A cron task named `per_agent_compression_<agent_id>` (normalized to `peragent_compression_<agent_id>` internally)
- Schedule: Sunday, every week, staggered 30 minutes apart starting at 03:00 Shanghai
- Timeout: 1200 seconds (20 minutes)
- Delivery: DingTalk announce to the configured account

---

## 🔧 How It Works | 工作原理

### 1. Discovery | 发现
The installer runs `openclaw agents list --json` and filters agents that have a `workspace` field.

### 2. Task Creation | 任务创建
For each discovered agent, the installer calls:

```bash
openclaw cron add \
  --name "per_agent_compression_<agent_id>" \
  --cron "<cron_expr>" \
  --tz "Asia/Shanghai" \
  --agent "main" \
  --message "<concise_execution_plan>" \
  --model "openrouter/stepfun/step-3.5-flash:free" \
  --timeout 1200 \
  --session "isolated" \
  --announce \
  --channel "dingtalk-connector" \
  --to "05566651511149398" \
  --best-effort-deliver
```

**Note on message length**: Due to CLI constraints, the `--message` is kept concise (~1200 chars) but contains all essential logic. Full details are documented in this README. If you need the ultra-detailed version (with every step and edge case), you can manually edit the task after install:

```bash
openclaw cron edit per_agent_compression_<agent_id> --message "$(cat FULL_DETAILED_MESSAGE.txt)"
```

### 3. Execution | 执行
When the cron triggers, the `main` agent executes the task instructions:

1. **Pre-check** - Verifies workspace, `memory/` dir, target files exist
2. **Load state** - Reads `{workspace}/memory/.compression_state.json` (or initializes)
3. **List notes** - Finds `memory/*.md` matching `YYYY-MM-DD.md`, filters date < today-7, excludes already processed
4. **Sort & limit** - Oldest first, max 5 notes per run
5. **Process each note**:
   - Read full content
   - Extract: user preferences, key decisions, personal info (domain-specific)
   - Dedupe: skip if target files already have entry for this note date
   - Append to:
     - `USER.md` → under `## Personal Info / Preferences`, header `### [YYYY-MM-DD]`
     - `IDENTITY.md` → under `## Notes` (create if missing), header `### [YYYY-MM-DD]`
     - `SOUL.md` → under `## Principles` or `## Boundaries` as appropriate, header `### [YYYY-MM-DD]`
     - `MEMORY.md` → under `## Key Learnings` (create if missing), format `- [YYYY-MM-DD] <summary>`
   - Move note file to `{workspace}/memory/processed/`
   - Update state: `processed_notes.append(filename)`, `last_compressed_date = note_date`
6. **Finalize** - Save state (`last_run_at`, `status="completed"`), clean working buffer
7. **Announce** - Send summary to DingTalk: agent, count processed, remaining old notes, any errors

---

## 🎯 What Gets Updated | 更新内容

Each agent's files are **appended only**; existing content is never overwritten.

**Example append to `MEMORY.md`**:
```markdown
## Key Learnings

- [2026-03-10] User prefers morning exercise and reads tech news before breakfast.
- [2026-03-12] Decoration project delayed due to material shortage; new timeline: April 15.
```

**Example append to `USER.md`**:
```markdown
## Personal Info / Preferences

### [2026-03-10]
- Preferred communication channel: DingTalk
- Working hours: 9:00-18:00 Beijing time
- Do not disturb: 12:00-14:00 lunch break
```

---

## ⚙️ Configuration | 配置

No configuration needed! But if you want to customize:

- **Schedule**: Edit the cron expression in the task (not recommended; re-run install after modifying `install.sh` offsets)
- **Timeout**: Change `--timeout` value in `install.sh` (default 1200s)
- **Delivery channel**: Modify `--channel` and `--to` in `install.sh`
- **Domain context**: Edit the `DOMAIN_CONTEXT` associative array in `install.sh` to add/change per-agent descriptions

---

## 🧪 Testing & Limitations | 测试与限制

### ⚠️ Known Limitations | 已知限制

1. **CLI message length limit**  
   `openclaw cron add --message` truncates messages > ~1KB. The skill works around this by using a concise template. For fully detailed instructions, manually edit the task post-install using `openclaw cron edit --message`.  
   **Impact**: Low—the concise template already contains all operational logic. Detailed examples are in README.

2. **No per-agent install filter**  
   The skill always discovers *all* agents. If you only want to install for one agent (e.g., `decoration`), you must either:
   - Edit `install.sh` to comment out other agents, OR
   - Run install, then immediately `openclaw cron delete` the unwanted tasks  
   **Impact**: Medium—extra manual cleanup if you need selective deployment.

3. **Requires `self-improve-agent` for full automation** (optional)  
   The skill itself does not depend on it, but if you want agents to automatically write daily notes or refine memories, you may need that separate skill.  
   **Impact**: Low—compression works without it.

4. **Memory/processed/ directory must be writable**  
   The task attempts to create `processed/` if missing. If permissions are insufficient, the task will fail on that note but continue with others.  
   **Impact**: Low—standard permissions are fine.

### ✅ Tested Scenarios | 已测试场景

- ✅ Fresh install on clean system (no pre-existing per-agent tasks)
- ✅ Reinstall over existing tasks (skips duplicates)
- ✅ Uninstall removes all skill-created tasks
- ✅ Task payload includes all expected fields (state file, processed dir, domain context)
- ✅ Gateway logs show no errors during installation
- ✅ Daily note (2026-03-18) recorded full session for future compression

### 🧪 Manual Verification | 手动验证

After install, verify with:
```bash
openclaw cron list | grep per_agent_compression
```

You should see 1 task per discovered agent. Check one task's message:
```bash
openclaw cron get <job_id> | jq '.payload.message'
```

Ensure the message includes:
- `DAILY_NOTES_DIR`
- `PROCESSED_DIR`
- `STATE_FILE`
- `TARGET_FILES`
- `DOMAIN_CONTEXT`
- Steps 1-7 including dedupe and remaining notes reporting

---

## 🗑️ Uninstall | 卸载

```bash
cd /root/.openclaw/workspace
./skills/per-agent-compression-universal/uninstall.sh
```

This removes **all** `per_agent_compression_*` tasks. It will not touch other cron jobs (e.g., `proactive_notes_compression_*`).

---

## 📚 Changelog | 更新日志

See [CHANGELOG.md](CHANGELOG.md) for version history and detailed changes.  
查看 [CHANGELOG.md](CHANGELOG.md) 了解版本历史和详细变更。

---

## 🤝 Contributing | 贡献

This skill is open for improvement. Found a bug or have an enhancement?  
此技能开放改进。发现错误或有增强建议？

- **Issues**: Report via GitHub (if published) or directly to the skill author
- **Enhancements**: Feel free to fork, modify `install.sh` and `README`, and submit a PR  
  （如果已发布）通过 GitHub 报告问题，或直接联系技能作者  
  增强建议：欢迎 fork，修改 `install.sh` 和 `README`，并提交 PR

---

## ⚠️ Disclaimer | 免责声明

**This skill is currently in active testing (迭代测试中).** While core functionality is stable, edge cases (e.g., message length limits, agent filtering) may require manual intervention. Use in production with the understanding that minor adjustments might be needed. Always backup your `MEMORY.md` and daily notes before first run.

**此技能目前处于积极测试阶段。** 虽然核心功能稳定，但边缘情况（如消息长度限制、代理过滤）可能需要进行手动调整。生产使用时请注意，可能需要进行微小调整。首次运行前务必备份您的 `MEMORY.md` 和每日笔记。

---

## 📞 Support | 支持

- **Documentation**: This README and CHANGELOG  
- **Community**: OpenClaw Discord (`#agent-skills` channel)  
- **Direct**: Contact the skill author or repository maintainer

---

**Happy Compressing! | 压缩愉快！**
