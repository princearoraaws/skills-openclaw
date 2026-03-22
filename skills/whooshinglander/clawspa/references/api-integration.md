# API Integration — Full Procedure

## Overview

Deep mode sends aggregated metadata (never raw content) to the ClawSpa API for AI-powered analysis. The API returns prioritized recommendations, risk scores, and a health score.

## Privacy Model

**What IS sent:**
- Machine fingerprint: SHA-256(hostname + workspace path) for identity
- File counts and sizes (number of memory files, total bytes)
- Token estimates
- Skill names, versions, and declared permissions
- Security flag summaries (e.g., "skill X contains base64 patterns in 3 files")
- Config check results (boolean: memory_flush enabled? fallback model set?)

**What is NEVER sent:**
- Raw memory content (no text from MEMORY.md, daily logs, or any user files)
- Credentials, API keys, or tokens (no credentials stored locally either)
- User names, emails, or personal information
- Conversation history
- File contents of any kind

## API Base URL

`https://clawspa.org/api/v1`

## Endpoints

### POST /scan/trial

**No auth required.** One free deep scan per unique workspace.

Request:
```json
{
  "machine_fingerprint": "sha256-of-hostname-plus-workspace-path",
  "memory_stats": {
    "file_count": 12,
    "total_bytes": 45000,
    "estimated_tokens": 11250,
    "memory_md_bytes": 8500,
    "oldest_file_days": 45,
    "newest_file_days": 0
  },
  "skills_list": [
    {
      "name": "github",
      "version": "1.0.0",
      "permissions": ["filesystem:read", "network:outbound"],
      "file_count": 5,
      "size_bytes": 12000
    }
  ],
  "security_flags": [
    {
      "skill": "suspicious-skill",
      "severity": "red",
      "patterns": ["base64_decode", "env_var_harvest"],
      "file_count_affected": 2
    }
  ],
  "config_checks": {
    "memory_flush": true,
    "fallback_model": true,
    "memory_search_directive": true,
    "backup_strategy": "git",
    "security_hygiene": "good"
  },
  "detox_flags": {
    "high_confidence": 0,
    "medium_confidence": 2,
    "patterns_found": ["unexplained_url", "tone_shift"]
  },
  "declutter_stats": {
    "active": 8,
    "idle": 3,
    "dormant": 2,
    "overlaps": 1
  }
}
```

Response:
```json
{
  "clawspa_id": "uuid-v4",
  "analysis": {
    "health_score": 72,
    "recommendations": [
      {
        "priority": 1,
        "category": "security",
        "title": "Review suspicious skill",
        "description": "...",
        "estimated_impact": "high"
      }
    ],
    "memory_optimization": {
      "estimated_savings_tokens": 3000,
      "suggestions": ["..."]
    },
    "risk_assessment": [...],
    "contradiction_analysis": "..."
  },
  "trial_remaining": 0
}
```

### POST /scan/check

Check if trial is still available.

Request:
```json
{
  "clawspa_id": "uuid-from-trial"
}
```

Response:
```json
{
  "trial_available": false,
  "upgrade_url": "https://clawspa.org/pricing"
}
```

### POST /scan

**Requires paid plan.** Include `machine_fingerprint` in request body. Server looks up plan by fingerprint.

Same request body as /scan/trial. Response includes comparison to previous scan:

```json
{
  "analysis": { ... },
  "scan_id": "uuid",
  "history_count": 5,
  "comparison_to_last": {
    "health_score_change": +3,
    "memory_change_tokens": -1500,
    "new_security_flags": 0,
    "resolved_issues": 2
  }
}
```

### GET /scans

**Requires auth.** Returns paginated scan history.

Query params: `?page=1&limit=10`

Response:
```json
{
  "scans": [
    {
      "scan_id": "uuid",
      "created_at": "2026-03-22T01:00:00Z",
      "health_score": 72,
      "summary": "..."
    }
  ],
  "total": 15,
  "page": 1,
  "limit": 10
}
```

## Error Handling

| Status | Meaning | Action |
|---|---|---|
| 200 | Success | Display results |
| 401 | No paid plan for this machine | Visit clawspa.org/pricing to subscribe |
| 402 | Plan limit reached | Show upgrade message |
| 429 | Rate limited | Wait and retry once after 60s |
| 500+ | Server error | Fall back to local mode, inform user |

On ANY network error (timeout, DNS failure, connection refused):
1. Log the error briefly
2. Fall back to local-only scan
3. Tell the user: "Deep scan unavailable. Running local scan instead. Check clawspa.org status."
4. Never block the entire spa session because the API is down

## Config File Management

`~/.openclaw/clawspa/config.md` format:

```markdown
# ClawSpa Config
clawspa_id: [uuid from trial]
last_scan: [ISO date of last deep scan]
```

No API key needed. Identity is determined by machine fingerprint (computed fresh each time).

## Scan History

Save deep scan results to `~/.openclaw/clawspa/history/scan-YYYY-MM-DD.md` with:
- Full analysis results
- Health score
- Comparison data
- Timestamp

Retain last 30 scans. On the 31st, delete the oldest.
