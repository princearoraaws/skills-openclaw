# Self-Improving Intent Security Agent

<p align="center">
  <a href="https://clawhub.ai/nishantapatil3/self-improving-intent-security-agent"><img src="https://img.shields.io/badge/Clawhub-Install%20Skill-blueviolet?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cGF0aCBkPSJNMTIgMkM2LjQ4IDIgMiA2LjQ4IDIgMTJzNC40OCAxMCAxMCAxMCAxMC00LjQ4IDEwLTEwUzE3LjUyIDIgMTIgMnoiIGZpbGw9IndoaXRlIi8+Cjwvc3ZnPgo=" alt="Install on Clawhub"></a>
  <a href="https://nishantapatil3.github.io/self-improving-intent-security-agent/"><img src="https://img.shields.io/badge/Docs-GitHub%20Pages-blue?style=for-the-badge&logo=github" alt="Documentation"></a>
  <a href="https://github.com/nishantapatil3/self-improving-intent-security-agent/actions/workflows/pages.yml"><img src="https://img.shields.io/github/actions/workflow/status/nishantapatil3/self-improving-intent-security-agent/pages.yml?branch=main&style=for-the-badge&label=Build" alt="Documentation Build Status"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
</p>

An autonomous agent skill that combines **intent-based security** with **continuous self-improvement**. Every action is validated against user intent before execution, with automatic rollback on violations and learning from outcomes.

## Why Intent Security?

Traditional security models ask: *"Do you have permission?"*
Intent security asks: *"Should you do this for this goal?"*

This fundamental shift enables autonomous agents to:
- ✓ Validate actions against stated objectives
- ✓ Detect goal drift and misalignment early
- ✓ Rollback automatically on violations
- ✓ Learn safe, effective strategies over time

## Features

### 🛡️ Intent-Based Security
- **Pre-Execution Validation**: Every action checked against intent
- **Real-Time Monitoring**: Anomaly detection during execution
- **Automatic Rollback**: Checkpoint-based state restoration
- **Audit Trail**: Complete transparency log

### 🧠 Self-Improvement
- **Pattern Extraction**: Learn from successful executions
- **Strategy Evolution**: A/B test and adopt better approaches
- **Failure Prevention**: Remember and avoid antipatterns
- **Bounded Learning**: Safety guardrails prevent harmful modifications

### 🔍 Transparency & Oversight
- **Complete Logging**: All decisions and actions recorded
- **Human Approval Gates**: High-risk actions require permission
- **Explainable Learning**: Traceable improvements
- **Rollback Capability**: Undo at any time

## Quick Start

### Installation

#### Option 1: Install via Clawhub (Recommended)

Visit [Clawhub](https://clawhub.ai/nishantapatil3/self-improving-intent-security-agent) to install this skill with one click.

Or use the CLI:
```bash
# Install from Clawhub
npx skills add nishantapatil3/self-improving-intent-security-agent
```

#### Option 2: Clone Repository

```bash
# Clone from GitHub
git clone https://github.com/nishantapatil3/self-improving-intent-security-agent.git
cd self-improving-intent-security-agent
./scripts/setup.sh
```

### Basic Usage

```bash
# 1. Create directory structure (or run: npm run setup)
mkdir -p .agent/{intents,violations,learnings,audit}

# 2. Set environment variables (optional - defaults shown)
export AGENT_INTENT_PATH=".agent/intents"       # Default: .agent/intents
export AGENT_AUDIT_PATH=".agent/audit"          # Default: .agent/audit
export AGENT_LEARNING_ENABLED="true"            # Optional: enable learning
export AGENT_AUTO_ROLLBACK="true"               # Optional: enable auto-rollback

# 3. Create intent specification
cat > .agent/intents/INT-$(date +%Y%m%d)-001.md <<'EOF'
## [INT-$(date +%Y%m%d)-001] my_task

**Created**: $(date -Iseconds)
**Risk Level**: medium
**Status**: active

### Goal
Process customer feedback files and extract sentiment

### Constraints
- Only read files in ./feedback directory
- Do not modify original files
- Respect PII privacy rules

### Expected Behavior
- Read files sequentially
- Apply NLP analysis
- Generate summary report

### Context
- Relevant files: ./feedback/*.txt
- Environment: development
EOF

# 4. Execute task with agent
# (Your agent implementation validates against intent automatically)

# 5. Review outcomes
cat .agent/violations/VIOLATIONS.md    # Any violations?
cat .agent/learnings/LEARNINGS.md      # What was learned?
./scripts/report.sh                     # Summary report
```

## Documentation

📚 **[Full Documentation Site](https://nishantapatil3.github.io/self-improving-intent-security-agent/)** - Interactive guides, demos, and examples

🔧 **[Install on Clawhub](https://clawhub.ai/nishantapatil3/self-improving-intent-security-agent)** - One-click installation

### Quick Reference

| Document | Description |
|----------|-------------|
| [SKILL.md](SKILL.md) | Complete usage guide and quick reference |
| [examples/](examples/) | Practical examples with step-by-step walkthroughs |
| [references/architecture.md](references/architecture.md) | System design and components |
| [references/intent-security.md](references/intent-security.md) | Intent validation and authorization |
| [references/self-improvement.md](references/self-improvement.md) | Learning mechanisms and safety |

## Architecture

```
User Intent → Validation → Authorization → Execution → Monitoring
                                              ↓
                                          Anomaly Detection
                                              ↓
                                    [Violation?] → Rollback
                                              ↓
                                       Outcome Analysis
                                              ↓
                                       Pattern Extraction
                                              ↓
                                      Strategy Evolution
                                              ↓
                                      Knowledge Store
                                              ↓
                                     Apply to Next Task
```

### Key Components

- **Intent Capture**: Structures user goals into formal specifications
- **Intent Validator**: Pre-execution validation (goal, constraints, behavior)
- **Authorization Engine**: Multi-layer permission checks
- **Execution Monitor**: Real-time behavioral monitoring
- **Anomaly Detector**: Goal drift, capability misuse, side effects
- **Rollback Manager**: Checkpoint-based state restoration
- **Outcome Analyzer**: Extract insights from task results
- **Pattern Extractor**: Identify reusable approaches
- **Strategy Optimizer**: A/B test and evolve strategies
- **Knowledge Store**: Persist learnings and strategies

## Configuration

### Environment Variables

**Important**: All environment variables are **optional**. The skill works with sensible defaults without any configuration.

**Security Note**: This skill does NOT require any credentials or secrets. All data stays local in the `.agent/` directory.

```bash
# Paths (optional - defaults shown)
export AGENT_INTENT_PATH=".agent/intents"       # Default: .agent/intents
export AGENT_AUDIT_PATH=".agent/audit"          # Default: .agent/audit

# Security (optional tuning)
export AGENT_RISK_THRESHOLD="medium"            # low | medium | high
export AGENT_AUTO_ROLLBACK="true"               # true | false
export AGENT_ANOMALY_THRESHOLD="0.8"            # 0.0 - 1.0

# Learning (optional tuning)
export AGENT_LEARNING_ENABLED="true"            # true | false
export AGENT_MIN_SAMPLE_SIZE="10"               # Minimum samples before learning
export AGENT_AB_TEST_RATIO="0.1"                # 0.0 - 1.0

# Monitoring (optional tuning)
export AGENT_METRICS_INTERVAL="1000"            # milliseconds
export AGENT_AUDIT_LEVEL="detailed"             # minimal | standard | detailed
```

### Configuration File

Create `.agent/config.json`:

```json
{
  "security": {
    "requireApproval": ["file_delete", "api_write", "command_execution"],
    "autoRollback": true,
    "anomalyThreshold": 0.8,
    "maxPermissionScope": "read-write"
  },
  "learning": {
    "enabled": true,
    "minSampleSize": 10,
    "abTestRatio": 0.1,
    "maxStrategyComplexity": 100
  },
  "monitoring": {
    "metricsInterval": 1000,
    "auditLevel": "detailed",
    "retentionDays": 90
  }
}
```

## Safety Guarantees

1. **Intent Alignment**: All actions validated against user goals
2. **Permission Boundaries**: Cannot exceed authorized scope
3. **Reversibility**: Checkpoint-based rollback capability
4. **Auditability**: Complete action history with rationale
5. **Bounded Learning**: Self-modification limited by guardrails
6. **Human Oversight**: Approval gates for high-risk operations

## Use Cases

### Development & DevOps
- Automated refactoring with safety constraints
- Deployment automation with rollback
- Infrastructure changes with approval gates

### Data Processing
- Batch processing with checkpoints
- API integration with rate limiting
- ETL pipelines with validation

### Security & Compliance
- Code security scanning with learning
- Policy enforcement with violations tracking
- Audit trail for compliance

## Examples

### Example 1: File Processing with Validation

```yaml
Intent:
  Goal: "Process customer feedback files"
  Constraints: ["Only read ./feedback", "No file modifications"]
  Risk: low

Action: Delete ./feedback/old_file.txt
Result: BLOCKED (violates "no modifications")
Logged: VIO-20250115-001.md
```

### Example 2: Learning from Experience

```yaml
Observation:
  - Tasks with <150 files: 100% success
  - Tasks with >150 files: 0% success (timeout)

Learning:
  Pattern: "batch-processing-with-checkpoints"
  Approach: "Process in batches of 100, checkpoint between"
  Improvement: 60% → 95% success rate

Action: Adopt new strategy via A/B testing
```

### Example 3: High-Risk with Approval

```yaml
Intent:
  Goal: "Deploy to production"
  Risk: high

Pre-checks:
  - Tests: PASSED
  - Backup: CREATED
  - Monitoring: ENABLED

Action: Requires approval → User prompted → Approved → Execute
```

## Utilities

```bash
# Setup agent structure
./scripts/setup.sh

# Validate intent format
./scripts/validate-intent.sh .agent/intents/INT-20250115-001.md

# Generate activity report
./scripts/report.sh

# Review violations
grep -l "Severity**: high" .agent/violations/*.md

# Check learning progress
cat .agent/learnings/STRATEGIES.md
```

## Integration

Works with multiple AI coding agents:

- **Claude Code**: Full support with hooks
- **Codex CLI**: Full support with hooks
- **GitHub Copilot**: Manual integration
- **OpenClaw**: Native integration

See [references/multi-agent.md](references/multi-agent.md) for details.

## Contributing

Contributions welcome! Please:
1. Read [CONTRIBUTING.md](CONTRIBUTING.md)
2. Fork the repository
3. Create a feature branch
4. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE)

## Support

- **Issues**: [GitHub Issues](https://github.com/nishantapatil3/self-improving-intent-security-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/nishantapatil3/self-improving-intent-security-agent/discussions)
- **Documentation**: [references/](references/)

## Acknowledgments

Based on concepts from:
- Intent-based security research
- AI agent alignment and safety
- Self-improving systems with bounded learning
- Autonomous agent monitoring and control

---

**⚠️ Important**: This skill provides strong safety mechanisms but requires proper configuration. Always:
- Define clear, specific intents
- Review violation logs regularly
- Monitor learning effectiveness
- Keep approval gates enabled for high-risk operations
- Test in non-production environments first

**Intent-based security is powerful, but human judgment remains essential.**
