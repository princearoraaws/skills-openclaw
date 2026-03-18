# Changelog | 更新日志

All notable changes to this skill will be documented in this file.  
本技能的所有重要变更都会记录在此文件中。

---

## [1.2.2] - 2026-03-18 (Final Testing & Optimization | 最终测试与优化)

### Added | 新增
- **Full bilingual documentation** - README and CHANGELOG now available in both Chinese and English for broader adoption | 完整双语文档 - README 和 CHANGELOG 现已提供中英文版本，便于更广泛的使用
- **Testing artifacts section** - Documented test results, known limitations, and manual verification steps | 测试文档部分 - 记录测试结果、已知限制和手动验证步骤
- **Production readiness checklist** - Clear status indicators for each feature | 生产就绪清单 - 每个功能都有清晰的状态指示

### Changed | 变更
- **Installation approach**: Simplified from two-step (add + edit) to single-step with concise message template (~1200 chars) to avoid CLI length limits reliably | 安装方式：从两步（add + edit）简化为单步简洁消息模板（约1200字符），可靠避免 CLI 长度限制
- **Message content**: Now includes all essential execution logic in a single line with `\n` escapes; full details maintained in README for reference | 消息内容：现在在单行中包含所有基本执行逻辑（使用 `\n` 转义）；完整细节保存在 README 中供参考
- **Task discovery**: Skill now creates 5 tasks (hrbp, parenting, decoration, memory_master, main) automatically; manual pre-filtering not supported (requires skill modification if needed) | 任务发现：技能现在自动创建5个任务（hrbp, parenting, decoration, memory_master, main）；不支持手动预过滤（需要时可修改技能）
- **Error handling**: Installer provides clearer feedback when tasks already exist or when edit operations fail | 错误处理：安装程序在任务已存在或编辑操作失败时提供更清晰的反馈

### Fixed | 修复
- **cron edit command confusion**: Resolved earlier misunderstanding about `cron update` (non-existent); confirmed correct command is `openclaw cron edit --message` | cron edit 命令混淆：解决了之前对 `cron update` 的误解（不存在）；确认正确命令是 `openclaw cron edit --message`
- **Over-deletion issue**: Testing procedure refined to avoid removing unrelated pre-existing tasks; uninstall script only removes skill-created tasks | 过度删除问题：优化测试流程，避免删除不相关的预存在任务；卸载脚本仅删除技能创建的任务
- **Heredoc quoting problems**: Eliminated by using single-line message with escaped newlines, improving script reliability | Heredoc 引号问题：通过使用带转义换行的单行消息消除，提高了脚本可靠性

### Known Issues | 已知问题
- **CLI length limit persists**: `openclaw cron add --message` truncates messages > ~1KB. Workaround: use concise template. For fully detailed messages, manual `cron edit --message` after install is required (user must do this if needed). | CLI 长度限制仍然存在：`openclaw cron add --message` 会截断超过 ~1KB 的消息。变通方法：使用简洁模板。如需完整详细消息，安装后需手动 `cron edit --message`（用户需自行操作）。
- **No agent filtering**: Skill auto-discovers all agents; cannot limit to a single agent via flag. To test one agent, either edit the skill's `install.sh` or manually create that agent's task after uninstall. | 无代理过滤：技能自动发现所有代理；无法通过标志限制单个代理。要测试单个代理，可编辑技能的 `install.sh` 或在卸载后手动创建该代理的任务。
- **Self-improve-agent dependency**: The skill itself does not require it, but system-level learning relies on separate `self-improve-agent` skill (optional, needs API key). | Self-improve-agent 依赖：技能本身不需要它，但系统级学习依赖于独立的 `self-improve-agent` 技能（可选，需要 API key）。

### Tested | 已测试
- ✅ Uninstall + reinstall flow works without leaving orphaned tasks | ✅ 卸载+重新安装流程工作正常，不会留下孤立任务
- ✅ All 5 tasks created with correct schedule (staggered Sundays 03:00-05:00 Shanghai) | ✅ 所有5个任务创建正确调度（上海时间周日 03:00-05:00 错开）
- ✅ Task payload includes state tracking, dedupe, domain context, moved-file marking | ✅ 任务负载包含状态跟踪、去重、领域上下文、移动文件标记
- ✅ No errors in gateway logs during installation | ✅ 安装期间网关日志无错误
- ✅ Daily notes (2026-03-18) capture complete session history | ✅ 每日笔记 (2026-03-18) 捕获完整会话历史

### Documentation | 文档
- **README_EN.md** - English version with quickstart, technical notes, and troubleshooting | **README_EN.md** - 英文版，包含快速入门、技术说明和故障排除
- **README_ZH.md** - Chinese version with same content | **README_ZH.md** - 中文版，内容相同
- **CHANGELOG.md** - Now bilingual entries from v1.2.0 onward | **CHANGELOG.md** - 从 v1.2.0 开始为双语条目

---

## [1.2.1] - 2026-03-18 (Two-Step Message Injection Attempt)

### Added | 新增
- **Two-step message injection attempt**: Due to CLI length limits, installer first creates task with short message, then attempts to update with full details via `cron edit` | 两步消息注入尝试：由于 CLI 长度限制，安装程序首先创建带短消息的任务，然后尝试通过 `cron edit` 更新为完整详细信息
- **Improved error reporting**: Installer now warns if full message update fails | 改进的错误报告：如果完整消息更新失败，安装程序现在会警告

### Changed | 变更
- **Installer script**: Added state validation and better error handling | 安装脚本：添加状态验证和更好的错误处理

### Fixed | 修复
- **Command confusion**: Early misstatement about `cron update` corrected to `cron edit` | 命令混淆：早期关于 `cron update` 的错误陈述已修正为 `cron edit`

---

## [1.2.0] - 2026-03-18

### Added | 新增
- **State persistence & checkpoint resilience** - Each agent task maintains `.compression_state.json` to resume from interruptions | 状态持久化与断点续传 - 每个代理任务维护 `.compression_state.json` 以从中断处恢复
- **Deduplication** - Checks target files before appending to avoid duplicate entries from same daily note | 去重 - 在追加前检查目标文件，避免同一 daily note 产生重复条目
- **Remaining notes reporting** - Summary includes count of old notes still pending for future runs | 剩余笔记报告 - 摘要包含仍待处理的老笔记数量
- **Enhanced error handling** - Individual note failures don't stop the entire task; errors logged and continue | 增强错误处理 - 单个笔记失败不会停止整个任务；错误被记录并继续
- **Moved-file marking** - Processed notes moved to `memory/processed/` directory for clear separation | 移动文件标记 - 已处理笔记移动到 `memory/processed/` 目录，清晰分离
- **Domain-specific extraction guidelines** - Each task includes DOMAIN_CONTEXT to tailor extraction (general, HR/work, parenting, renovation) | 领域特定提取指南 - 每个任务包含 DOMAIN_CONTEXT 以定制提取（通用、HR/工作、育儿、装修）
- **Pre-check validation** - Script verifies agents list, workspace existence, and memory directory before registration | 预检查验证 - 脚本在注册前验证代理列表、工作区存在性和 memory 目录

### Changed | 变更
- **Task naming** - Changed from `peragent_compression_` to `per_agent_compression_` for better readability | 任务命名 - 从 `peragent_compression_` 改为 `per_agent_compression_` 以提高可读性
- **Timeout increased** - From 300s to 1200s to accommodate larger note sets | 超时增加 - 从 300 秒增加到 1200 秒以适应更大的笔记集
- **Message payload enriched** - Detailed execution plan with specific file paths, state structure, and date header format (`### [YYYY-MM-DD]`) | 消息负载丰富化 - 包含具体文件路径、状态结构和日期头格式的详细执行计划
- **Delivery mode** - Uses `--best-effort-deliver` to ensure notifications are attempted even if partial failures occur | 交付模式 - 使用 `--best-effort-deliver` 确保即使部分失败也尝试通知

### Fixed | 修复
- **State file path** - Now properly defined as `{workspace}/memory/.compression_state.json` | 状态文件路径 - 正确定义为 `{workspace}/memory/.compression_state.json`
- **Processed directory** - Explicitly created as `{workspace}/memory/processed/` | 处理目录 - 显式创建为 `{workspace}/memory/processed/`
- **Target sections** - Clear append locations: USER.md (`## Personal Info / Preferences`), IDENTITY.md (`## Notes`), SOUL.md (`## Principles`/`## Boundaries`), MEMORY.md (`## Key Learnings`) | 目标章节 - 清晰的追加位置：USER.md (`## Personal Info / Preferences`), IDENTITY.md (`## Notes`), SOUL.md (`## Principles`/`## Boundaries`), MEMORY.md (`## Key Learnings`)

### Known Issues | 已知问题
- No dry-run mode for testing (future enhancement) | 无干运行模式用于测试（未来增强）
- No performance optimizations (caching, indexing) - acceptable for typical workloads | 无性能优化（缓存、索引）- 对典型工作量可接受

## [1.1.0] - 2026-03-18 (Initial Public Release)

### Added | 新增
- Auto-discovery of all agents via `openclaw agents list --json` | 通过 `openclaw agents list --json` 自动发现所有代理
- Staggered weekly scheduling (Sundays, 30-minute intervals starting 03:00) | 交错每周调度（周日，从 03:00 开始，间隔 30 分钟）
- Workspace isolation - each agent compresses its own memory files | 工作区隔离 - 每个代理压缩自己的 memory 文件
- Basic extraction of preferences, decisions, and personal information | 偏好、决策和个人信息的基本提取
- Markdown date headers for all appended entries | 所有追加条目的 Markdown 日期头
- Summary notifications via DingTalk connector | 通过钉钉连接器发送摘要通知
- Uninstall script to remove all `per_agent_compression_*` tasks | 卸载脚本以删除所有 `per_agent_compression_*` 任务
- Comprehensive README with troubleshooting guide | 包含故障排除指南的全面 README

---

## Upgrade Notes | 升级说明

### From 1.1.0/1.2.0 to 1.2.2
1. Run `./uninstall.sh` to remove old tasks | 运行 `./uninstall.sh` 删除旧任务
2. Replace skill directory with v1.2.2 | 替换技能目录为 v1.2.2
3. Run `./install.sh` to register tasks | 运行 `./install.sh` 注册任务
4. Existing `.compression_state.json` files will be preserved (backward compatible) | 现有的 `.compression_state.json` 文件将被保留（向后兼容）
5. If you need fully detailed task messages, manually run `openclaw cron edit <task_name> --message "$(cat FULL_MESSAGE.txt)"` after install | 如果需要完整详细的任务消息，请在安装后手动运行 `openclaw cron edit <task_name> --message "$(cat FULL_MESSAGE.txt)"`

### Fresh Install | 全新安装
Simply run `./install.sh` after placing the skill in `/root/.openclaw/workspace/skills/`. | 只需将技能放置在 `/root/.openclaw/workspace/skills/` 后运行 `./install.sh`。

---

## 📊 Version Comparison | 版本对比

| Feature | 1.1.0 | 1.2.0 | 1.2.1 | 1.2.2 |
|---------|-------|-------|-------|-------|
| Auto-discovery | ✅ | ✅ | ✅ | ✅ |
| State persistence | ❌ | ✅ | ✅ | ✅ |
| Deduplication | ❌ | ✅ | ✅ | ✅ |
| Domain filtering | ❌ | ✅ | ✅ | ✅ |
| Moved-file marking | ❌ | ✅ | ✅ | ✅ |
| Bilingual docs | ❌ | ❌ | ❌ | ✅ |
| Test artifacts | ❌ | ❌ | ❌ | ✅ |
| Production readiness label | ❌ | ❌ | ❌ | ✅ |
| CLI length workaround | ❌ | ❌ | ⚠️ two-step attempt | ✅ concise template |

---

**📌 Note | 注意**  
This skill is actively iterated and tested. While core functionality is stable, edge cases (e.g., message length limits) may require manual intervention. Check CHANGELOG for latest updates.  
此技能正在积极迭代和测试中。虽然核心功能稳定，但边缘情况（如消息长度限制）可能需要进行手动干预。查看 CHANGELOG 获取最新更新。
