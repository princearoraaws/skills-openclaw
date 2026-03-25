---
name: kyndlo-events
description: Autonomous city-scoped event creation from campaign tasks, plus full event lifecycle management — tasks, venues, images, validation — via the gokyn CLI.
version: 3.0.0
metadata:
  openclaw:
    requires:
      env:
        - KYNDLO_API_TOKEN
      bins:
        - node
        - gokyn
    primaryEnv: KYNDLO_API_TOKEN
    install:
      - kind: npm
        package: gokyn
        bins: [gokyn]
        label: npm install -g gokyn
    emoji: "🎉"
    os: [darwin, linux]
    homepage: https://github.com/kyndlo/gokyn-cli
---

# kyndlo-events — Kyndlo Event Management

Create and manage events, activities, tasks, and validations on the Kyndlo platform via the `gokyn` CLI. Supports autonomous city-scoped event creation from campaign tasks.

## Setup

```bash
npm install -g gokyn
export KYNDLO_API_TOKEN="kyndlo_..."
gokyn whoami   # verify token works
```

All commands accept `--token <token>` if the env var is not set.
Add `--json` to any command for machine-readable output.

---

## Pre-flight Checks

Before creating any events, run these checks in order. Stop if any fail.

### 1. Verify token

```bash
gokyn whoami --json
```

Confirm the token is valid and has the required permissions.

### 2. Fetch and read the event creation rules (MANDATORY)

```bash
gokyn task rules
```

Read the **full** output and internalize every rule. They govern venue selection, event formatting, images, and quality. **Follow them strictly for every event you create.** Rules are maintained in the database and may change between runs — always fetch fresh.

### 3. Resolve the city scope

```bash
gokyn task cities --state <state>
```

This shows all cities with their constituent counties and populations. Use this to:
- **If the user gave a city name:** confirm it exists in the list.
- **If the user gave a county name:** find which city contains that county and use the city name going forward. For example, Orange County FL belongs to the **Orlando** metro area — use `Orlando`. If the county is in the `Rural` bucket, use `Rural`.
- **If the user gave neither:** pick a city to target based on pending work.

### 4. Get campaign context

```bash
gokyn task context --campaign <campaign> --city <city> --json
```

Confirm the campaign exists. Report city-level progress (counties done, tasks remaining) to the user.

### 5. Report status

Tell the user: campaign name, resolved city, progress percentage, tasks remaining, and confirm rules loaded.

---

## Category Name Mapping

Task `activityCategory` values sometimes differ from activity titles in the database. Use this table when searching for the activity ID:

| Task activityCategory | Search Term for `gokyn activity list --search` |
|---|---|
| Specialty Niche Museums | Specialty & Niche Museums |
| Yoga Classes | Wellness centers |
| Restaurant/Cafes with Animal Encounters | Coffee with animal encounters |
| Community Theaters | Theater lounges |
| Craft Cafes | Craft cafés |
| Beach/Boardwalks | Beach Boardwalks |
| Food Trucks | Food truck parks |
| Planetariums | Planetarium |

If the task category is not in this table, use it as-is for the search.

---

## Day-of-Week Reference

When setting `--recurrence-days`, use these day numbers:

| Day | Number |
|-----|--------|
| Sunday | 0 |
| Monday | 1 |
| Tuesday | 2 |
| Wednesday | 3 |
| Thursday | 4 |
| Friday | 5 |
| Saturday | 6 |

Include a day ONLY if the venue is open that day. Omit closed days entirely.

---

## State Timezone Reference

| State | Timezone |
|-------|----------|
| Colorado | America/Denver |
| Florida | America/New_York |
| New York | America/New_York |

---

## The Autonomous Loop

Repeat sequentially for the target city until there are no more eligible tasks, safe progress is blocked, or the user asks you to stop. Track progress as `[Task X]`.

**Important:** If the loop exits early for any reason, run the Cleanup step to release any uncompleted tasks.

### Step 1: Claim a task

```bash
gokyn task next --campaign <campaign> --city <city> --assign --name "<agent-name>" --json
```

Use the agent name only for `--name` (e.g. `Sugar`). Do NOT pass `--priority` — the server returns tasks in priority order automatically.

If `"count": 0`, stop the loop. If the response includes a `"diagnostic"` field, report it to the user.

Extract from `tasks[0]`: `_id` (taskId), `county`, `activityCategory`, `cluster`, `state`.

### Step 2: Map the category

Check the Category Name Mapping table above. If the `activityCategory` matches a left-column entry, use the corresponding right-column search term. Otherwise use the category as-is.

### Step 3: Find the activity ID

```bash
gokyn activity list --search "<mapped-category>" --json
```

Extract the activity `_id` from the first matching result. If no results, try shorter/partial search terms. If still no match, skip the task with reason "Activity not found for category: \<category\>".

### Step 4: Research a venue

Find a real venue matching the task's `activityCategory` in `county`, `state`. **Follow the venue selection criteria, hours verification gate, and county validation gate from `gokyn task rules`.**

Collect:
- **name** — venue display name
- **address** — full street address
- **latitude** and **longitude** — GPS coordinates
- **open days** — which days the venue is open (as numbers 0-6)
- **website URL** — venue website (used as `--booking-url`) — **always collect this**
- **price** — estimated cost in USD (default 0)
- **photo URL** — a real photo of the venue (optional)

Search up to 5 candidates and use the first one that passes the hours gate and county validation. If none qualify, skip the task.

### Step 5: Create the event

Look up the timezone from the State Timezone Reference table. Format open days as comma-separated numbers for `--recurrence-days`.

```bash
gokyn event create \
  --title "<venue name>" \
  --description "<2-3 sentence description per rules>" \
  --activity <activityId>:1 \
  --start-date-time "2027-01-01T09:00:00Z" \
  --end-date-time "2028-01-01T23:59:00Z" \
  --timezone "<timezone>" \
  --location-type physical \
  --location-place "<venue name>" \
  --location-address "<address>" \
  --location-lat <latitude> \
  --location-lng="<longitude>" \
  --recurring \
  --recurrence-frequency weekly \
  --recurrence-interval 1 \
  --recurrence-days "<open days>" \
  --is-public=false \
  --is-premium-only \
  --is-active=false \
  --price <price> \
  --price-currency USD \
  --booking-url "<venue website URL>" \
  --json
```

**CLI syntax notes:**
- Negative longitude MUST use `=` syntax: `--location-lng="-104.99"`
- Boolean false requires `=`: `--is-public=false`
- End date is always `2028-01-01T23:59:00Z` (one year window for recurring events)

Extract the `eventId` from the JSON response.

### Step 6: Upload a photo

If you obtained a photo URL during research:

```bash
curl -L -o /tmp/venue-photo.jpg "<photo-url>"
gokyn image upload --file /tmp/venue-photo.jpg --event-id <eventId>
```

If no photo is available or upload fails, continue — the event is still valid.

### Step 7: Complete the task

```bash
gokyn task complete <taskId> --event-id <eventId> --venue "<venue name>"
```

### Step 8: Report progress

```
[Task X] COMPLETED: <venue name> in <county> County (<cluster>/<category>) — Event ID: <eventId>
```

If the task was skipped:
```
[Task X] SKIPPED: <county> County / <category> — Reason: <reason>
```

---

## Error Recovery

| Error | Recovery |
|---|---|
| No tasks returned (count: 0) | If `diagnostic` field present, report it. Otherwise stop the loop. |
| No venues found | Try broader search terms. If still none, skip task. |
| No venues with determinable hours | Skip task with reason "No venues with published hours". |
| Activity ID not found | Try partial/shorter search terms. If still not found, skip task. |
| Event creation fails | Log the error. Release the task: `gokyn task release <taskId>`. Continue. |
| Photo download/upload fails | Continue without photo. Still complete the task. |
| gokyn task complete fails | Log the error. Release the task: `gokyn task release <taskId>`. Report the event ID. |
| Agent interrupted or unexpected error | Release all claimed-but-uncompleted tasks. See Cleanup. |

---

## Cleanup

Before exiting — whether normally or due to an error — release any task that was claimed but not completed or skipped.

```bash
gokyn task release <taskId>
```

**Rule:** A task must NEVER be left in `in_progress` status when the agent exits. Every claimed task must end in one of three states:
- **completed** — event created successfully
- **skipped** — permanent failure (no venues, category not found)
- **released** (back to pending) — transient failure (API error, timeout)

Use `skip` for permanent failures. Use `release` for transient failures.

---

## Summary Report

After all tasks are processed (or the loop ends early), print:

```
=== Event Creation Summary ===
Campaign:   <campaign-name>
City:       <city-name>
Processed:  <total> tasks
Created:    <count>
Skipped:    <count>
Failed:     <count>

Created Events:
  - <venue name> in <county> (<category>) — Event ID: <id>
  - ...

Skipped Tasks:
  - <county> / <category> — <reason>
  - ...

Failed Tasks:
  - <county> / <category> — <error>
  - ...
```

---

## Skipping a Task

```bash
gokyn task skip <taskId> --reason "No qualifying venue found in <county> County for <category>"
```

Always provide a specific reason.

## Releasing a Task

```bash
gokyn task release <taskId>
```

---

## Starting a New State

When a campaign needs to cover a new US state:

```bash
# 1. Register the state with its counties
gokyn task register-state --state "New York" \
  --counties "New York,Kings,Queens,Bronx,Richmond,Nassau,Suffolk"

# 2. Check city/metro areas
gokyn task cities --state "New York"

# 3. Seed the campaign
gokyn task seed --campaign "newyork-2027" --state "New York" \
  --counties "New York,Kings,Queens,Bronx,Richmond" \
  --clusters-json '{
    "intellectual": ["History Museums", "Bookstore Cafes"],
    "visionary": ["Escape Rooms", "Comedy Clubs"],
    "protector": ["Yoga Classes", "Botanic Gardens"],
    "creator": ["Art Museums", "Pottery Painting Studios"]
  }'

# 4. Verify
gokyn task campaigns
gokyn task context --campaign "newyork-2027"
```

---

## Event Validation Workflow

Validations are periodic re-checks of existing events.

```bash
# Check validation stats
gokyn validation summary

# Get next validation to review
gokyn validation next --assign --json

# After reviewing the event data, submit result:
gokyn validation submit <validationId> --status valid

# Or if issues found:
gokyn validation submit <validationId> --status invalid \
  --issues-json '[{"field":"price","severity":"high","description":"Price changed","currentValue":"$0","expectedValue":"$15"}]'

# Or if minor updates needed:
gokyn validation submit <validationId> --status needs_update \
  --notes "Hours changed for summer season"
```

---

## Browsing Activities and Events

```bash
gokyn activity list --search "yoga" --limit 10
gokyn activity list --category "wellness" --json
gokyn activity get <activityId>
gokyn activity categories

gokyn event list --limit 10
gokyn event list --search "garden" --is-active --json
gokyn event get <eventId>
```

## Updating and Deleting Events

```bash
gokyn event update <eventId> --title "New Title"
gokyn event update <eventId> --is-active=false
gokyn event update <eventId> --price 25 --price-currency USD
gokyn event update <eventId> --activity <id1>:1 --activity <id2>:2
gokyn event update <eventId> \
  --location-type physical \
  --location-place "New Venue" \
  --location-address "123 Main St" \
  --location-lat 40.7 \
  --location-lng="-74.0"
gokyn event delete <eventId>
```

---

## Geographic Queries

```bash
gokyn task states                      # List registered US states
gokyn task counties --state "Colorado" # List counties in a state
gokyn task cities --state "Colorado"   # List metro areas + rural breakdown
```

---

## Command Quick Reference

| Command | Purpose |
|---|---|
| `gokyn whoami` | Verify token and permissions |
| `gokyn task rules` | **Read event creation rules (MANDATORY)** |
| `gokyn task campaigns` | List campaigns with progress |
| `gokyn task context --campaign <id>` | Campaign progress, next county |
| `gokyn task summary --campaign <id>` | Detailed stats by city and county |
| `gokyn task cities --state <s>` | Metro areas and county mappings |
| `gokyn task next --campaign <id> --city <c> --assign --name <n>` | Claim next task |
| `gokyn task complete <id> --event-id <eid>` | Mark task done |
| `gokyn task skip <id> --reason <r>` | Skip impossible task |
| `gokyn task release <id>` | Unclaim a task |
| `gokyn task seed --campaign <id> ...` | Seed tasks for counties |
| `gokyn activity list / get / categories` | Browse activities |
| `gokyn event list / get / create / update / delete` | Manage events |
| `gokyn image upload --file <f> --event-id <eid>` | Upload venue photo |
| `gokyn validation next / submit / summary` | Event validation |

## Global Flags

| Flag | Env | Description |
|---|---|---|
| `--token <token>` | `KYNDLO_API_TOKEN` | API token (required) |
| `--base-url <url>` | `KYNDLO_API_URL` | API base URL (default: https://api.kyndlo.com) |
| `--json` | | Machine-readable JSON output |
| `--timeout <ms>` | | HTTP timeout in ms (default: 30000) |
| `--no-color` | `NO_COLOR` | Disable ANSI colors |

## Tips

- Always use `--json` when parsing output programmatically
- Always pass `--name` with `--assign` to track who claimed a task
- Use `--city` to focus on a metro area: `--city "Denver"` or `--city "Rural"`
- Negative numbers need `=` syntax: `--location-lng="-104.99"`
- Boolean flags: `--is-public` = true, `--is-public=false` = false
- IDs are 24-character hex strings (MongoDB ObjectId)
- Dates are ISO 8601: `2027-01-01T09:00:00Z`
