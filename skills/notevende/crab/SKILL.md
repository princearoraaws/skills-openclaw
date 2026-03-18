---
name: Crab Catch
description: |
  Crab Catch is a Web3 research skill that automatically collects and
  organizes project data and potential risks from social media, websites,
  code, and on-chain data, and produces a complete and objective
  research report.
metadata:
  author: NotevenDe
  version: 2.0.0
---

# Crab Catch — Research Skill Orchestration

## Prerequisites

CLAWBOT **must run** these commands at session start (not just read them):

```bash
which agent-browser || npm install -g agent-browser
agent-browser install
```

## Data Sources

CLAWBOT is the research driver — responsible for analysis, judgment, iteration,
and report generation. The APIs, scripts, and tools below are **data-fetching
methods only**.

**API Base URL**: `https://crab-skill.opsat.io`

### Signature Authentication

All API requests except `/api/health` require Crab signature headers.

1. Run `node skills/scripts/crab-sign.js` **once** at session start to get headers JSON.
   (First run auto-generates credentials; cached signature reused if still valid within 24h.)
2. Store the output and attach these four headers to **all** subsequent API requests:
   `X-Crab-Timestamp`, `X-Crab-Signature`, `X-Crab-Key`, `X-Crab-Address`.
   No need to re-run the script for each request.
3. Only re-run with `--refresh` if API returns `auth_expired`.

### Twitter & Social Data (see `twitter-analysis/SKILL.md` for full params)

**Profile & content** — who are they, what do they say:

| Research goal | Endpoint | Key params |
|------|------|------|
| User profile & stats | `/api/twitter/user` | `username` |
| User's original posts | `/api/twitter/tweets` | `username`, `product` |
| User's posts + replies | `/api/twitter/replies` | `username`, `product` |
| Deleted tweets | `/api/twitter/deleted-tweets` | `username` |
| Tweet long-form article | `/api/readx/tweet-article` | `tweet_id` |

**Engagement & spread** — how is a tweet being received:

| Research goal | Endpoint | Key params |
|------|------|------|
| Full reply thread under a tweet | `/api/readx/tweet-detail-conversation-v2` | `tweet_id`, `cursor` |
| Who quoted this tweet (KOL amplification) | `/api/readx/tweet-quotes` | `tweet_id` |
| Who retweeted (spread network) | `/api/readx/tweet-retweeters` | `tweet_id` |
| Who liked (supporter profile) | `/api/readx/tweet-favoriters` | `tweet_id` |
| Tweet detail with views/source | `/api/readx/tweet-detail-v2` | `tweet_id` |
| Batch fetch multiple tweets | `/api/readx/tweet-results-by-ids` | `tweet_ids` |

**Relationships & credibility** — who follows/endorses who:

| Research goal | Endpoint | Key params |
|------|------|------|
| KOL followers of project | `/api/twitter/kol-followers` | `username` |
| Verified (blue-check) followers | `/api/readx/user-verified-followers` | `user_id` |
| Who the project follows (inner circle) | `/api/readx/following-light` | `username` |
| Follower list | `/api/readx/followers-light` | `username` |
| Mutual follow / relationship check | `/api/readx/friendships-show` | `source_screen_name`, `target_screen_name` |
| Follow/unfollow events over time | `/api/twitter/follower-events` | `username`, `isFollow` |

**Search & discovery** — find discussions, mentions, risk signals:

| Research goal | Endpoint | Key params |
|------|------|------|
| Structured search (filters) | `/api/twitter/search` | `keywords`, `fromUser`, `mentionUser`, `minLikes`, `minReplies`... |
| Advanced search (Twitter syntax) | `/api/readx/search2` | `q` (e.g. `"project" min_faves:100 -filter:replies`) |

**AI-powered comment analysis** (see `gork-analysis/SKILL.md`):

| Research goal | Endpoint | Key params |
|------|------|------|
| Deep insight from tweet comments | `/api/gork/analyze` | `prompt` (include tweet URL + question) |

> **Gork vs conversation-v2**: Use `conversation-v2` as the **primary** comment source (fast, raw data).
> Use `gork/analyze` only when reply threads need deeper AI interpretation (mixed sentiment, technical debates).
> Limit: max 2 Gork calls per research.

### GitHub Code (see `github-analysis/SKILL.md`)

Local script `skills/scripts/github_analyze.js` — no external API.
`convertToMarkdown(url, options)` or `analyzeRepository(url, options)`.

### On-chain Data (see `onchain-audit/SKILL.md`)

**Binance API (onchain)** — `address` + `chainName` (uppercase: `BSC`/`ETHEREUM`/`BASE`/`SOLANA`):

| Endpoint | Description |
|----------|-------------|
| `/api/onchain/audit` | Contract audit (Binance + Bitget dual-source) |
| `/api/onchain/token-info` | Token metadata and market dynamics |
| `/api/onchain/wallet` | Wallet positions (BSC/BASE/SOLANA only) |
| `/api/onchain/token-search` | Token search (requires `keyword`) |

**Bitget API (onchain-2)** — `chain` + `contract` (lowercase: `bnb`/`eth`/`base`/`sol`):

| Endpoint | Description |
|----------|-------------|
| `/api/onchain-2/token-info` | Token details |
| `/api/onchain-2/token-price` | Token price |
| `/api/onchain-2/tx-info` | Transaction statistics |
| `/api/onchain-2/liquidity` | Liquidity pool info |
| `/api/onchain-2/security-audit` | Security audit |

### Website Content (see `agent-browser/SKILL.md`)

CLAWBOT uses `agent-browser` CLI to open and inspect websites.
Primary method for fetching web page content — no API proxy needed.

### Others

| Endpoint | Method | Description |
|------|------|------|
| `/api/health` | GET | Health check |

## Language Preference

Output language **matches the user's input language**; default **Chinese (zh-CN)**.
Raw API data (usernames, tickers, addresses, code) stays in original form.

## Orchestration Flow

```
User provides URL / Ticker / contract address + research intent
  │
  ▼
Step 1 — Parse input, initialize entity queue
  Extract all entities from user input:
    Twitter links, GitHub repos, contract addresses, tickers, chain
    Aggregator URLs → extract entities from path (see rules below)

  Initialize entity queue:
    entity_queue = [{ entity, depth: 0 } for each extracted entity]
    processed    = set()
    MAX_DEPTH    = 2   # prevent infinite recursion
  │
  ▼
Step 2 — Collect raw intelligence (entity-driven loop)
  Goal: maximize information density. Gather everything, filter later.
  Every data source may discover NEW entities — feed them back into the queue.

  ┌──────────────────────────────────────────────────────────────┐
  │ While entity_queue is not empty:                             │
  │                                                              │
  │   { entity, depth } = queue.pop()                            │
  │   if entity in processed: skip                               │
  │   if depth > MAX_DEPTH: note in findings, do NOT process     │
  │   processed.add(entity)                                      │
  │                                                              │
  │   Route by entity type:                                      │
  │     URL      → 2a. Website exploration                       │
  │     Twitter  → 2b. Social data collection                    │
  │     GitHub   → 2c. Code analysis                             │
  │     Contract → 2d. On-chain analysis                         │
  │     Ticker   → 2d. On-chain token-search first               │
  │                                                              │
  │   After each source returns:                                 │
  │     Extract new entities from results                        │
  │     Add to queue with depth: current_depth + 1               │
  │     (see "Entity Discovery Rules" below)                     │
  └──────────────────────────────────────────────────────────────┘

  --- 2a. Website exploration ---

  For clawhub.ai URLs: extract owner/repo → route to 2c (skip browser)
  For other URLs — use agent-browser CLI:

      # Open & orient
      agent-browser open <url>
      agent-browser wait --load networkidle
      agent-browser get title                    # confirm page loaded
      agent-browser get url                      # detect redirects

      # 1. Landing page
      agent-browser snapshot -i
      agent-browser scroll down 2000
      agent-browser snapshot -c
      agent-browser screenshot --full
      → Extract: headline, key numbers, partner logos, CTA text

      # 2. Docs / Whitepaper
      agent-browser find text "Docs" click
      agent-browser wait --load networkidle
      agent-browser snapshot -c
      agent-browser screenshot --full
      agent-browser pdf docs.pdf
      → Look for: token distribution, vesting, supply mechanics
      agent-browser back

      # 3. Team / About
      agent-browser find text "Team" click
      agent-browser wait --load networkidle
      agent-browser snapshot -c
      agent-browser screenshot --full
      → Extract: names, titles, LinkedIn/Twitter links
      → Red flag: stock photos, no real identities, fully anonymous
      agent-browser back

      # 4. App / DApp (if exists)
      agent-browser find text "App" click
      agent-browser wait --load networkidle
      agent-browser snapshot -i
      → DApp checks: UI renders? Real values or zeros? Core functions present?
      → Do NOT click "Connect Wallet" or sign anything
      agent-browser screenshot --full
      agent-browser back

      # 5. Tokenomics
      agent-browser find text "Token" click
      agent-browser wait --load networkidle
      agent-browser snapshot -c
      agent-browser screenshot --full
      → Look for: distribution chart, unlock schedule, tax rates, contract addr
      agent-browser back

      # 6. Footer
      agent-browser scroll down 9999
      agent-browser snapshot -c
      → Extract: social links, legal info, company registration

      agent-browser close

      # Security check (during browsing):
      SSL/TLS, domain age, redirect chains, suspicious popups,
      wallet-connect on landing, obfuscated scripts
      Flag issues; do NOT interact with suspicious wallet prompts

      # Fallback
      Page blank / Cloudflare → retry: agent-browser open <url> --headed
      Geo-restricted → note in report, try alternative URLs
      No website → skip, flag as risk signal

      ★ Extract new entities → add to queue (see Entity Discovery Rules below)

  --- 2b. Social data collection ---

  Layer 1 — Basic profile & content (parallel):
    - /api/twitter/user → profile, follower count, account age
    - /api/twitter/tweets (product:"Top") → highest engagement posts
    - /api/twitter/tweets (product:"Latest") → most recent posts
    - /api/twitter/replies → who they interact with
    - /api/twitter/kol-followers → credible followers
    - /api/twitter/deleted-tweets → removed content
    - /api/twitter/follower-events → follow/unfollow patterns

  Layer 2 — Deep engagement analysis (after Layer 1 returns tweets):
    Pick the 2 most valuable tweets (highest engagement + most controversial):

    For each tweet:
      - /api/readx/tweet-detail-v2 → views, source, engagement metrics
        (judge real reach: high views + low engagement = bot-inflated?)
      - /api/readx/tweet-detail-conversation-v2 → full reply thread
        (direct data, faster than Gork — use this as primary comment source)
      - /api/readx/tweet-quotes → who quoted it (KOL amplification signal)
      - /api/readx/tweet-retweeters → spread network

    If tweets contain long-form content (Twitter Articles):
      - /api/readx/tweet-article → extract full article text
        (founders often publish roadmaps, postmortems, or announcements as articles)

    If deleted-tweets returned tweet IDs:
      - /api/readx/tweet-results-by-ids → batch fetch deleted tweet snapshots
        (retrieve what was said before deletion — high-value intelligence)

    Gork analysis (supplementary, max 2 calls):
      Only use /api/gork/analyze when reply threads need deeper interpretation
      (e.g. mixed sentiment, technical debates, insider claims that need synthesis).
      If conversation-v2 already provides clear signal, skip Gork to save time.

  Layer 3 — Relationship & reach analysis:
    - /api/readx/following-light → who does the project follow back?
      (reveals inner circle, partner accounts, team alt accounts)
    - /api/readx/user-verified-followers → verified/blue-check followers
      (requires `user_id` = `rest_id` from /api/twitter/user response, NOT username)
    - /api/readx/friendships-show → verify relationships between
      team members, KOLs, and project account (mutual follows?)

  Layer 4 — Broader search & discovery:
    - /api/twitter/search keywords:{project_name} → who's talking about it
    - /api/twitter/search mentionUser:{username} → who mentions the project
    - /api/readx/search2 q:"{project_name} min_faves:100" → high-impact discussions
    - /api/readx/search2 q:"{project_name} scam OR rug OR hack" → risk signals
    - /api/twitter/search keywords:{project_name} minReplies:20 → controversial threads

  ★ Extract new entities → add to queue (see Entity Discovery Rules below)

  --- 2c. Code analysis ---

  github-analysis → analyzeRepository / convertToMarkdown
  Focus: tech stack, commit activity, code completeness, risk points

  ★ Extract new entities → add to queue (see Entity Discovery Rules below)

  --- 2d. On-chain analysis ---

  Binance + Bitget dual-source (parallel):
    audit, token-info, wallet, liquidity, tx-info, security-audit
  Cross-verify between sources when possible.

  ★ Extract new entities → add to queue (see Entity Discovery Rules below)

  │
  ▼
Step 3 — Cross-reference & verify claims
  Goal: find contradictions — they are the most valuable signals.
  If verification needs data not yet collected, go back to Step 2 to fetch it.

  Compare data across sources:
    - Twitter says X vs website says Y vs on-chain shows Z
    - Claimed team → search GitHub commit history, LinkedIn, past projects
    - Claimed partnerships → check counterparty's official channels
    - Claimed TVL/volume → compare with on-chain data
    - Claimed audit → verify firm + report link existence and date

  Website claims vs Code/On-chain verification:

    | Website/Docs claim | Verify with | How |
    |--------------------|-------------|-----|
    | "Decentralized"    | On-chain: ownership | Contract has pause/mint/blacklist? Owner is EOA or multisig? |
    | "Audited by X"     | Website + GitHub | Link valid? Deployed code matches audited version? |
    | "Max supply N"     | Code: mint function | Contract has uncapped mint()? Owner can mint? |
    | "Deflationary/Burn"| Code: burn mechanism | burn() exists? Actually called on-chain? |
    | "Locked liquidity" | On-chain: LP lock | Lock contract verified? Duration? Amount? |
    | "Governance/DAO"   | On-chain: governance | Proposals exist? Real votes or single-wallet? |
    | "Open source"      | GitHub: repo | Repo public? Code matches deployed bytecode? |
    | "Multi-chain"      | On-chain per chain | Contracts actually deployed on claimed chains? |
    | "Partnerships"     | Partner's channels | Partner acknowledges? Or one-sided claim? |

    Priority: verify claims that affect user funds first (audit, liquidity, ownership).
    If a claim cannot be verified with existing data → fetch missing data (Step 2).

  Mark each claim: ✅ Verified / ⚠️ Unverified / ❌ Contradicted
  │
  ▼
Step 4 — Deep dig (hypothesis-driven)
  Goal: follow high-value leads that emerged from Steps 2-3.

  For each significant finding, ask "what does this imply?":
    - Team member found → trigger team member analysis (see below)
    - Contract is upgradable → who holds the proxy admin? Is it a multisig?
    - Large holder detected → where did their tokens come from? Deployer?
    - Deleted tweets found → what did they say? Why deleted? Timing?
    - GitHub inactive → is the project abandoned or is code closed-source?
    - TVL mismatch → organic demand or incentivized/fake liquidity?

  Team member analysis:
    When a team member (founder, co-founder, CTO, etc.) is identified from
    any source, their Twitter handle is already queued in Step 2 and will
    be processed by 2b (Layer 1-4) automatically. Step 4 adds ADDITIONAL
    analysis that goes beyond what the entity queue covers:

    1. Cross-source identity verification:
       - Does the Twitter profile match the website Team page claims?
       - Does GitHub commit history match claimed expertise?
       - /api/readx/friendships-show → do all team members follow each other?
         (if they don't, are they really a team?)

    2. History & reputation check:
       - /api/readx/search2 q:"{name} founder OR CEO OR CTO" → past projects
       - Did those projects succeed or fail/rug?
       - On-chain (if wallet address known or linked):
         → /api/onchain/wallet → what tokens do they hold?
         → Check if their wallet deployed other contracts (pattern?)
         → Check fund flow between team wallet and project deployer

    3. Red flags to synthesize:
       - Account created same time as project (sockpuppet?)
       - No history before this project (fabricated identity?)
       - Past association with failed/rugged projects
       - Identity claims don't match across sources
       - Team members don't follow each other (fake team?)
       - Following list is mostly bots or empty accounts

  Proactive exploration patterns (only for NEW leads from Steps 2-3,
    do NOT repeat searches already done in Step 2b Layer 4):
    - Search for specific controversies discovered in Step 3:
        /api/readx/search2 q:"{project} + {specific controversy keyword}"
    - Search for team members' other projects and outcomes:
        /api/readx/search2 q:"{member_name} founder OR CEO OR CTO"
    - Check if contract deployer has deployed other tokens (pattern?)
    - Look for on-chain connections between team wallets and exchanges
    - Use Gork for deep interpretation when search results are ambiguous:
        prompt = "discussions about {project} + {specific finding}"

  If new high-value leads emerge → loop back to Step 2 (respecting MAX_DEPTH).
  Stop when: no new high-value leads, or sufficient to form a judgment.

  ─── END OF DATA COLLECTION PHASE ───
  Everything above is about gathering and verifying raw intelligence.
  Everything below is about analysis and report generation.
  │
  ▼
Step 5 — Distill & prioritize findings
  Goal: compress raw intelligence into high-density insights.

  From all collected data, select only what matters:
    - Rank findings by impact (deal-breaker > important > nice-to-know)
    - Discard noise: routine data that confirms nothing special
    - Highlight contradictions and anomalies — these are the story
    - Connect dots: A + B together imply C (CLAWBOT's analytical value)
    - Identify information gaps: what couldn't be verified and why
    - Reconstruct project timeline from all time-stamped data

  This step is pure analysis — no new data fetching.
  │
  ▼
Step 6 — Produce final research report
  Write report using distilled findings from Step 5.
  Use `REPORT_TEMPLATE.md` as the report structure.
  Report should read as curated intelligence, not a data dump.
  Language follows user input. Inline citations for all evidence.
```

### Entity Discovery Rules

During Step 2, every data source may reveal new entities. Extract and queue them
with `depth: current_depth + 1`:

**From website (2a):**

| Found in | Entity type | Example | Action |
|----------|-------------|---------|--------|
| Team / About page | Twitter handle | `@john_dev` | → queue as Twitter entity |
| Tokenomics page | Contract address | `0x1234...` | → queue as Contract entity |
| Footer / Links | GitHub repo | `github.com/org/repo` | → queue as GitHub entity |
| Docs / Partners | Partner names | `"partnered with X"` | → note for search in Layer 4 |

**From social data (2b):**

| Found in | Entity type | Example | Action |
|----------|-------------|---------|--------|
| Bio / tweets | Twitter handle | `co-founder @jane` | → queue as Twitter entity |
| Tweets | Contract address | `CA: 0x5678...` | → queue as Contract entity |
| Tweets | GitHub link | `github.com/org/repo` | → queue as GitHub entity |
| Reply threads (conversation-v2) | Person mention | `insider says @whale_x` | → queue as Twitter entity |
| Quote tweets | KOL handle | `@kol quoted with commentary` | → note who amplifies + stance |
| Following list | Inner circle account | `project follows @alt_account` | → queue as Twitter entity |
| KOL followers | Notable followers | `@vitalik follows` | → note for cross-reference |
| Deleted tweets | Tweet IDs | `deleted tweet 123456` | → fetch via tweet-results-by-ids |

**From code (2c):**

| Found in | Entity type | Example | Action |
|----------|-------------|---------|--------|
| Commit authors | GitHub/Twitter handle | `author: dev123` | → note for cross-ref |
| Source code | Hardcoded address | `admin = 0xABCD` | → queue as Contract entity |
| Dependencies | Related repos | `import from org/lib` | → note for reference |

**From on-chain (2d):**

| Found in | Entity type | Example | Action |
|----------|-------------|---------|--------|
| Contract data | Deployer address | deployer of contract | → check other deployments |
| Contract data | Admin / proxy | proxy admin, timelock | → queue as Contract entity |
| Token holders | Large holders | top 10 wallets | → note for pattern analysis |
| Liquidity | LP provider | LP creator address | → compare with deployer (insider?) |

**Depth control:**
- Depth 0: entities from user input
- Depth 1: entities discovered from depth-0 results (team members, mentioned contracts)
- Depth 2: entities discovered from depth-1 results (max depth, only follow high-value leads)
- Beyond depth 2: do NOT queue, only note in findings for manual follow-up

## Failure Handling

| Failure type | Action |
|-------------|--------|
| Timeout / 502 / 503 / 504 | Retry once after 3s (`/api/gork/analyze`: allow 120s before timeout) |
| 429 (rate limit) | Retry once after `Retry-After` or 10s |
| 401 / 403 / 400 | Do not retry; skip |
| Other errors | Do not retry; skip |

On failure: skip that data source, continue with remaining sources.
Include a **Data Coverage** note in the report listing available/unavailable sources.
Omit sections with no data; never halt the entire workflow for a single failure.

## Entity Extraction Rules

| Entity Type | Identification |
|----------|---------|
| Twitter profile | `x.com/{username}` or `twitter.com/{username}` |
| Twitter post | `x.com/{username}/status/{id}` |
| GitHub repo | `github.com/{owner}/{repo}` |
| EVM contract | `0x` + 40 hex chars |
| Solana address | base58 32–44 chars + contextual keywords (see below) |
| Ticker | `$XXX` or `ticker/symbol/token: XXX` |
| Chain attribution | URL domain / path keywords / page text keywords |

### Solana Address Contextual Keywords

A base58 string is only identified as a Solana address when at least one
contextual keyword is present in surrounding text, URL, or page content:

`solana`, `sol`, `raydium`, `jupiter`, `orca`, `meteora`, `marinade`,
`tensor`, `magic eden`, `jito`, `pump.fun`, `moonshot`, `birdeye`,
`solscan`, `solana.fm`, `solanabeach`, `spl token`, `program id`

If no keyword is found, flag as "unresolved address".

## Aggregator URL Parsing

These URLs are parsed for entities from the path (not treated as official sites):

| Platform | Path format | Parsed result |
|------|---------|---------|
| clawhub.ai | `/owner/repo` | → repo (owner/repo) — **use `github-analysis` directly, skip agent-browser** |
| dexscreener.com | `/chain/address` | → contract + chain |
| dextools.io | `/app/chain/pair/address` | → contract + chain |
| pump.fun | `/address` | → Solana contract |
| gmgn.ai | `/chain/address` | → contract + chain |
| birdeye.so | `/token/address` | → contract |
| defined.fi | `/chain/address` | → contract + chain |

## Data Display Rules

- **API latency / performance metrics**: If the data was not successfully fetched or
  the request returned an error, **do not display** API latency or performance data
  in the report. Only show latency data when it was actually measured successfully.
- Skip any metric that returned an error or timed out — leave it out entirely rather
  than showing "N/A" or error messages.

## Local Memory & Report Storage

After generating the final research report, store a copy locally:

1. Save the report as PDF to `~/.crab-catch/reports/{project_name}_{YYYY-MM-DD}.pdf`
2. Maintain an index file `~/.crab-catch/reports/index.json` with entries:
   ```json
   { "project": "name", "date": "YYYY-MM-DD", "file": "filename.pdf", "entry": "original user input" }
   ```
3. This allows past research to be retrieved in future sessions.

## Report Output

Use `REPORT_TEMPLATE.md` as the report structure, with the following constraints:

### Section constraints

**Must keep** — always present, fixed order, follow template format:
- Header (project name + timestamp)
- 📌 Basic Information
- 🧠 Core Findings (with Executive Summary)
- 📝 Conclusion & Verdict
- 📂 References

**Default keep** — included by default; user can request to skip:
- 🛡️ Verification & Cross-Reference (Claim / Contradictions / Gaps)
- ⚠️ Risk Warning

**Data-dependent** — include if data available, skip entire subsection if not:
- 📊 Deep Dive
  - 👤 Team & Key Figures (skip if no team info found)
  - 💻 GitHub Analysis (skip if no repo)
  - ⛓️ On-chain Security (skip if no contract)
  - 📈 Social Signals (skip if no Twitter)
  - 📅 Project Timeline (skip if insufficient time data)

**Free** — table row count, description text, signal count are flexible.

### Formatting rules
- Inline citations: `[[N]](url)` after every evidence claim
- Numbers: K / M / B format; prices: `$` prefix
- Highlight high-risk signals (honeypot, high tax, upgradable contracts)
- Include **Data Coverage** note when sources were unavailable
- Append DYOR disclaimer
- **Output language matches user input; default Chinese (zh-CN)**
