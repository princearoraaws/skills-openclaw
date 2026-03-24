---
name: agent-team-skill
description: "Team collaboration and task processing flow with delegation, progress tracking, and multi-agent coordination. Use when team coordination, task delegation, or workflow management is needed."
license: MIT
homepage: https://github.com/realqiyan/agent-team-skill
allowed-tools: Bash(python3:*) Read(*.json)
compatibility: Requires Python 3.10+
metadata:
  clawdbot:
    emoji: "🤖"
    requires:
      bins:
        - python3
---

# Agent Team Skill

Manage AI agent team members with skills, roles, and task delegation.

## 👑 Leader Authority (Highest Priority - Violation = Critical Error)

**Actions only you can take:**

1. **Approve task completion**
   - Before marking any task complete, verify output meets original requirements
   - If incomplete → Send back for revision with specific feedback

2. **Reassign when delegation fails**
   - If teammate cannot complete task → Decide: reassign to another teammate OR execute yourself
   - Non-leaders should escalate to you instead of reassigning

## 🔄 Task Processing Flow (Highest Priority - Violation = Critical Error)

**Plan → Do → Check → Act**

**IMPORTANT: This is a continuous improvement cycle. If task is incomplete in Act phase, loop back to Plan.**

### 1. Plan — Planning Phase

**Goal: Prepare thoroughly, avoid blind execution**

- **Search Context**: Search historical memory first, do not respond immediately
- **Understand Requirements**: What does the user really want?
- **Clarify Questions**: Must clarify if unsure (ask clearly in one go when possible, max 3 rounds)
- **Define Goals**: What's the deliverable? Success criteria?
- **Identify Risks**: What could go wrong?
- **Determine Ownership**: Who's best suited to execute? (self or teammate)
- **Create Plan**: Output specific execution plan

### 2. Do — Execution Phase

**Goal: Execute the plan while maintaining records**

#### ⚠️ Recording (Highest Priority - Core of Memory)

**Before starting any execution, must record to `memory/YYYY-MM-DD.md`:**
```markdown
## In Progress
### [Task Name] (HH:MM start)
- Progress: xxx
```

**Update record upon completion:**
```markdown
### [Task Name] (HH:MM start)
- End time: HH:MM | Result: xxx
```

#### Execution Actions

- **Delegate or Execute**:
  - Belongs to teammate → Delegate with full context (search history + original requirements + plan)
  - Belongs to self → Execute directly
- **Create Checkpoint**: Create git commit after each sub-phase
  ```bash
  git add -A && git commit -m "checkpoint: [Task Name] sub-phase complete"
  ```

### 3. Check — Checking Phase

**Goal: Verify results, ensure quality**

- Verify results against requirements
- Check completeness and compliance with standards
- Record issues and deviations

### 4. Act — Acting Phase

**Goal: Summarize experience, decide next steps**

- **Update Record**: Mark final result in `memory/YYYY-MM-DD.md`
- **Standardize Success**: Record effective practices, consolidate into memory
- **Improve Weaknesses**: Identify optimization opportunities
- **Decide Next Steps**:
  - ✅ Task complete → End
  - ❌ Task incomplete → Loop back to Plan

### ⚡ Task Delegation Rules (Core Principle)

**Delegation Timing:**
1. First complete prep work: understand requirements, clarify goals, confirm constraints
2. When entering implementation: identify the best person for execution, delegate to them
3. Follow up after delegation: check output quality, ensure requirements are met

## Query Team Members

List all team member information:

```bash
python3 scripts/team.py list
```

Output example:
```markdown
## Team Members

**Alice** ⭐ Leader - coordination,planning,decision-making
- agent_id: alice
- expertise: task breakdown, comprehensive decisions, agent coordination
- not_good_at: code development, investment analysis

**Bob** - Backend Developer - backend,API,database
- agent_id: bob
- expertise: Python,Go,PostgreSQL
- not_good_at: frontend,design

# Total: 2 member(s), Leader: Alice (alice)
```

## Add/Update Member

Add a new member or update existing member information:

```bash
python3 scripts/team.py update \
  --agent-id "agent-001" \
  --name "Alice" \
  --role "Backend Developer" \
  --is-leader "true" \
  --enabled "true" \
  --tags "backend,api,database" \
  --expertise "python,go,postgresql" \
  --not-good-at "frontend,design"
```

Parameters:
- `--agent-id`: Member unique identifier (required)
- `--name`: Member name (required)
- `--role`: Role/position (required)
- `--is-leader`: Whether team Leader (required, true/false, only one Leader per team)
- `--enabled`: Enable status true/false (required)
- `--tags`: Tags, comma-separated (required)
- `--expertise`: Expertise skills, comma-separated (required)
- `--not-good-at`: Weak areas, comma-separated (required)

## Reset Data

Clear all team data and reset to initial state:

```bash
python3 scripts/team.py reset
```

⚠️ This operation will clear all data in `~/.agent-team/team.json`.

## Data Storage

Team data is stored in `~/.agent-team/team.json`, shared globally. Directory is auto-created if it doesn't exist.

## Use Cases

- **Team Maintenance**: Record all members and their skill information
- **Task Assignment**: Assign tasks based on member expertise and tags

## References

- [Plugin Installation Guide](https://github.com/realqiyan/agent-team-skill/blob/master/integrations/openclaw/agent-team/README.md) - How to install and configure the OpenClaw plugin
