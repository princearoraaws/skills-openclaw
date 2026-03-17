---
name: meditation
description: >
  Guide meditation sessions with timers, breathing exercises, and body scans.
  Log practice sessions and view statistics. Generate audio playlists.
  Input: session duration, exercise type, log entries.
  Output: timed session prompts, breathing patterns, session logs,
  practice stats, and playlist recommendations.
version: 3.0.0
author: BytesAgain
tags:
  - meditation
  - mindfulness
  - breathing
  - wellness
  - timer
  - body-scan
---

# Meditation Skill

Time meditation sessions, guide breathing and body scans, log practice, and track stats.

## Commands

### start

Start a meditation timer with optional bell intervals.

```bash
bash scripts/script.sh start [--duration <minutes>] [--bell <interval_min>] [--type focus|open|loving-kindness]
```

### breathe

Run a guided breathing exercise.

```bash
bash scripts/script.sh breathe [--pattern 4-7-8|box|deep] [--cycles <num>]
```

### body-scan

Generate a body scan meditation guide.

```bash
bash scripts/script.sh body-scan [--duration short|medium|long] [--focus full|upper|lower]
```

### log

Record a meditation session to the journal.

```bash
bash scripts/script.sh log <duration_min> [--type <type>] [--mood <1-10>] [--note <text>]
```

### stats

View meditation practice statistics.

```bash
bash scripts/script.sh stats [--period week|month|year|all] [--format table|json]
```

### playlist

Generate a meditation audio playlist.

```bash
bash scripts/script.sh playlist [--mood calm|sleep|focus|energy] [--duration <minutes>] [--count <num>]
```

## Output

All commands print to stdout. Session logs are stored in `~/.meditation/sessions.json`. Timer and breathing commands print real-time prompts to the terminal.

## Feedback

Questions or suggestions? → [https://bytesagain.com/feedback/](https://bytesagain.com/feedback/)

---

Powered by BytesAgain | bytesagain.com
