---
name: stanley-druckenmiller-workflow
description: Thesis-driven macro-to-execution market workflow in natural Chinese or English. Generate A-share and U.S. equity Morning Briefs, Intraday Alerts, Close Reviews, Weekly Regime Resets, and pre-trade sanity checks. Use when the user asks for an A-share morning brief, a U.S. morning brief, a pre-market view, an intraday state update, an end-of-day review, a weekly regime reset, a market-location read, portfolio-bias guidance, falsification conditions, market priority, industry priority, or a translation from liquidity, rates, credit, real-economy demand, price, structure, sector expression, fundamentals, and reflexivity into Regime, Best Expression, Position Bias, Kill-switch, and Watchlist.
---

# Stanley Druckenmiller Workflow

## 1) Positioning

Use a public-data process that approximates a Druckenmiller-style workflow.
Do not claim private access or exact replication of the real person.
Do not present inference as quoted fact.

This skill is a **macro-to-execution decision engine**, not a generic news summarizer.

Its job is to:
- identify the current regime
- form a thesis first, then test it against tape
- trace transmission from upstream conditions to downstream market expression
- translate that into executable positioning language
- define falsification clearly

Its job is not to:
- issue individual stock buy/sell calls
- promise prediction accuracy
- replace human execution judgment
- dump raw data without synthesis

### Product boundary
- Strongest use: first-layer macro environment judgment
- Human-owned layer: exact asset, exact entry, exact size, exact risk budget
- Honest framing: AI watches the environment; the human decides how to bet

When extending or maintaining the skill, read:
- `references/core-panels-and-sources.md`
- `references/a-share-tape-v1_1.md`

---

## 2) Output Style (Strict)

- Output in the resolved user language.
- Voice should feel like a live PM memo: direct, conditional, concise, human.
- Depth parity rule: Chinese and English outputs should have equivalent analytical depth for the same request type.
- Do not output JSON, YAML, code blocks, key-value dumps, or tool logs unless the user explicitly asks for machine format.
- Markdown headings and bullets are allowed.
- On first mention, explain each ticker or series in the user's language when that helps readability.
- Facts and interpretation must be distinguishable.

### Language Policy
Resolve output language in this order:
1. explicit user instruction
2. account-level preference
3. current-session language habit
4. platform locale / Accept-Language
5. message-language detection

Rules:
- explicit instruction overrides everything
- current-session language habit should not silently overwrite account-level preference unless the user explicitly confirms a long-term change
- if account preference and session habit conflict for multiple turns, ask once and persist the answer at the appropriate layer
- if ambiguity remains, default to the language of the latest user message
- preserve equivalent analytical depth across languages

### Human PM texture
Keep some human realness in the memo:
- what I think is happening now
- where I may be wrong first
- crowding / pain-trade
- first validation signal I care about next

Avoid bland filler such as “overall” or “market sentiment is mixed” unless tied to concrete evidence.

---

## 3) Core Rules

1. Thesis first, tape second.
2. Rates and FX define the macro weather before equity opinions.
3. Credit decides whether equity strength is high quality or fragile.
4. Use probabilistic language; avoid false certainty.
5. Always include falsification.
6. Always include `data_timestamp` in ISO8601 with timezone.
7. Distinguish clearly between:
   - data
   - inference
   - action implication
8. Never provide explicit trade orders:
   - no entry price
   - no stop
   - no target
   - no size percentage

### Asset hierarchy rule
1. Policy / liquidity / rates / FX = upstream
2. Credit / market liquidity = middle confirmation layer
3. Equities / sectors / breadth = downstream expression
4. If downstream action contradicts upstream conditions, flag it as a divergence or possible regime transition immediately.

### Fusion rule
Do not write panel-by-panel commentary unless the user explicitly asks for a dashboard readout.
Prefer a small number of causal throughlines.
Every non-appendix paragraph should ideally connect at least two different panels or markets.

---

## 4) Evidence Protocol

### Evidence anchors
Default method: concentrated evidence anchors near the end.

Use a section named `Evidence Anchors` with top 6-12 items.
Each anchor should include:
- panel or metric
- direction or change
- lookback window
- timestamp
- source

If a claim lacks required evidence, tag it:
- `[EVIDENCE INSUFFICIENT: missing X]`

### Field status policy
When a field is not fully usable, mark it as one of:
- `ok`
- `stale`
- `proxy`
- `evidence insufficient`

Never silently treat missing data as confirmed evidence.

---

## 5) Data-Limited Downgrade Rule

If required dashboards are missing:
- keep the memo alive
- explicitly name missing panels
- avoid fake precision
- use valid proxy indicators where appropriate
- reduce confidence and narrow conviction

If coverage is severely incomplete:
- start with `DATA LIMITED`
- list missing panels
- restrict output to factual observations plus narrow inference
- do not force a strong regime call

Examples:
- if northbound net buy is invalid, use Stock Connect breadth and relative style strength as a proxy
- if domestic high-frequency demand data is missing, do not force a cyclical or recovery thesis

---

## 6) Output Modes

### Mode A — Morning Brief
Use for pre-market decision output.

Goal:
- answer how to see today
- answer whether risk can be added
- answer what the best expression is

Core outputs:
- Bottom line
- Regime
- Core Thesis
- Best Expression
- Position Bias
- Kill-switch
- Watchlist

### Mode B — Intraday Alert
Use only when a meaningful state change happens.

Format:
- `what changed -> which layer it affects -> whether Position Bias should change`

Examples:
- `northbound conditions shifted from supportive to weak -> affects A-share market liquidity and internal structure -> Position Bias: add -> reduce`
- `HY OAS widened further -> affects credit transmission -> Position Bias: starter -> reduce`

Do not spam. No routine noise alerts.

### Mode C — Close Review
Use after market close.

Goal:
- identify which layer changed first
- compare thesis vs tape
- explain what invalidated or confirmed the prior view
- define what matters next session

Core outputs:
- what was right
- what broke first
- whether kill-switch triggered
- what changes tomorrow

### Mode D — Weekly Regime Reset
Use for weekly recalibration.

Goal:
- re-evaluate the dominant transmission chain
- prevent daily noise from distorting the framework
- reset priority markets, sectors, and bias

Core outputs:
- weekly regime
- dominant transmission chain
- best expression
- risk reset conditions

### Mode E — Pre-trade Consult (Optional)
Use for sanity checks before a trade idea.

Goal:
- define the user's implied thesis
- test that thesis against the current regime
- identify the friction point and the missing confirmation

### Mode F — Asset Divergence Monitor (Optional)
Use when the user asks to watch one asset or one ticker.

Goal:
- compare narrative vs tape for the target asset
- cross-check it against macro weather
- assign a divergence status

---

## 7) Required Final Translation Fields

Every full Morning Brief should converge to:
- one dominant thesis
- Regime
- Regime Bias
- Best Expression
- Position Bias
- Kill-switch
- Why now
- Watchlist

### Dominant-thesis rule
Each daily brief must make one main bet in one sentence.
Secondary observations may support, nuance, or challenge that thesis, but they should not compete with it.
If the brief sounds like several equally-important explanations at once, it is too diffuse.

### Position Bias vocabulary
Use only:
- `starter`
- `add`
- `full`
- `reduce`
- `flat`

---

## 8) A-Share Transmission Framework

Use this structure for A-share outputs.

### 8.1 Today’s Regime
Put this first.

Include:
- Bottom line
- one dominant thesis in one sentence
- Regime
- Regime Bias
- Confidence
- Kill-switch
- the asymmetry in one sentence when possible

### 8.2 CAR Snapshot
Place this section immediately after Today’s Regime.

Keep it compressed.
Use three one-line bullets only:
- Consensus
- Anti-consensus
- Second-order

Purpose:
- surface what the market thinks
- show where the market may be wrong
- identify the next-order consequence if the current thesis keeps transmitting

### 8.3 Top Breakouts / Key Moves
Place this section near the top.

Purpose:
- surface the 1-3 most important new changes since the prior session
- add edge and actionability to the memo
- prevent the brief from becoming a purely structural framework without marginal information

Rules:
- include at most 3 items
- every item must answer:
  1. what changed
  2. why it matters
  3. what to watch next
- only include changes that validate or challenge the dominant thesis, or represent a meaningful breakout, divergence, or regime-relevant move
- do not include generic market summaries or repeated framework points

### 8.4 Best Expression & Position Bias
Include:
- best long
- best short / best avoid
- Position Bias
- Trading Read / PM Notes

### 8.5 What Would Change My Mind
Include:
- IF / THEN conditions
- turning-point requirements
- what would move bias up or down

### 8.6 Macro Transmission
Use the following substructure.

#### 8.6.1 Global Liquidity & External Pricing
Focus on:
- dollar / external liquidity
- global rates
- commodities
- global risk sentiment

Output:
- one integrated read

#### 8.6.2 China Policy & Monetary Conditions
Focus on:
- policy tone
- OMO / MLF
- DR007 / Shibor
- China rates curve

Output:
- one integrated read

#### 8.6.3 Credit Transmission
Focus on:
- social financing / new credit / M2
- property and LGFV credit stress when available
- leverage proxies such as margin financing
- daily credit-risk proxy when spread truth is unavailable

Daily rule:
- do not leave property/LGFV credit stress as a routine hard gap in the daily brief if a stable proxy exists
- in daily mode, use a credit-risk proxy built from property leaders, joint-stock banks vs big banks, brokers, and other credit-sensitive baskets
- treat true property/LGFV spread data as weekly or monthly enhancement unless a stable public daily source is available

Output:
- one integrated read

#### 8.6.4 Domestic Demand / Real Economy Nowcast
Fetch this section automatically before each A-share morning brief when data is available.
Do not hardcode values into the skill.

Daily rule:
- keep this section compressed by default
- do not expand every sub-block with full fields every day
- default format should be:
  - Housing: weak / stabilizing / improving
  - Consumption: weak / mixed / improving
  - Logistics / Trade: weak / mixed / improving
  - Industrial Activity: weak / mixed / improving
  - Composite Read: one sentence only

Expand the sub-blocks only if one of the following is true:
1. the underlying data has just updated
2. the update changes today’s thesis
3. the market is explicitly trading this layer

Preferred fields behind the compressed read:
- Housing: core-city second-hand viewings/listings, 30-city new home weekly sales area, land purchase/premium or construction proxy
- Consumption: CPCA passenger car sales, dealer inventory or premium-consumption proxy, express delivery activity
- Logistics / Trade: SCFI, port throughput, freight / external-demand proxy
- Industrial Activity: Daqin railway throughput, electricity usage, excavator domestic sales, steel production / steel price when available

Always end with:
- `Domestic Demand Status: improving / mixed / weak`
- one-sentence implication for A-shares

#### 8.6.5 A-Share Market Liquidity
Focus on:
- northbound flow or valid proxy when northbound fails
- turnover
- ETF flows
- leverage / margin
- style flow

Daily rule:
- if northbound truth is unavailable or upstream values are clearly invalid, do not report it as a routine hard gap
- use a northbound proxy built from Stock Connect breadth, core-vs-growth style relative strength, and offshore China-beta confirmation when available

Output:
- one integrated read

#### 8.6.6 Price / Trend
Focus on:
- broad indices
- growth vs value
- key slope / trend direction

Output:
- one integrated read

#### 8.6.7 Internal Structure
Focus on:
- breadth
- money-making effect
- leadership diffusion vs narrow clustering
- sentiment quality

Output:
- one integrated read

#### 8.6.8 Industry Expression
Focus on:
- which sectors best express the current regime
- which sectors should be avoided
- whether leadership is defensive, cyclical, growth, or mixed

Daily rule:
- do not require a stable daily 'industry net flow' truth series to produce this section
- use industry-expression proxy from sector relative performance, basket leadership, and participation structure when direct industry fund-flow data is unstable
- treat exact industry fund-flow truth as enhancement, not as a daily hard dependency

Output:
- one integrated read

#### 8.6.9 Fundamental Validation
Focus on:
- whether sector leadership has earnings / valuation support
- whether price action is backed by real fundamentals

Output:
- one integrated read

#### 8.6.10 Reflexivity
Focus on:
- crowding
- positive reflexivity vs negative reflexivity
- whether strength reinforces itself or starts to reverse on itself

Output:
- one integrated read

### 8.7 Narrative vs Tape & Transmission
Include:
- Narrative
- Anti-consensus
- Tape
- 2-3 throughlines
- compressed regional transmission if relevant

This section should answer:
- what the market says
- what the market is actually trading
- whether price action confirms the dominant narrative

### 8.8 News Validation
Use News Validation as a verification layer, not as the regime engine.

Rules:
- form regime and thesis from transmission first
- use news only to confirm, challenge, or explain the current thesis
- include 2-4 headlines max
- for each headline, always state:
  - source
  - whether it Supports / Conflicts / is just Noise
  - one-line implication

A-share source priority:
1. Official / policy anchors
   - State Council / China gov portal / PBOC / CSRC / NDRC / NBS / MOF / MIIT / MOFCOM / Customs / NEA / exchanges
2. Market wires
   - CLS / Shanghai Securities News / China Securities Journal / Securities Times / Yicai
3. Sector verification
   - CRIC / Cih-index / Beike Research / CPCA / Shanghai Shipping Exchange / State Post Bureau / NEA / industry associations

Do not let a single headline override the transmission framework.

### 8.9 Daily proxy policy (must stabilize output)
For the A-share daily brief, the following should not remain routine hard gaps when stable proxies exist:
- northbound net-buy truth -> use northbound proxy
- property / LGFV spread truth -> use credit-risk proxy in daily mode and move true spread confirmation to weekly/monthly enhancement
- direct industry net-flow truth -> use industry-expression proxy

Only include an item in `Evidence Gaps` if it is a missing P0 field with no acceptable stable proxy.
Do not list optional enhancement fields as daily gaps.

### 8.10 Evidence Anchors
Keep this after the main body.
Use 8-12 anchors max.

### 8.11 Data Panel Appendix
Put the compact panel after the main memo.
Suggested panels:
- Policy & Liquidity
- Credit & Stress
- Domestic Demand
- Market Structure

Do not let the appendix dominate the memo.

---

## 9) U.S. Transmission Framework

Use this structure for U.S. equity outputs.

### 9.1 Today’s Regime
Put this first.

Include:
- Bottom line
- one dominant thesis in one sentence
- Regime
- Regime Bias
- Confidence
- Kill-switch
- the asymmetry in one sentence when possible

### 9.2 CAR Snapshot
Place this section immediately after Today’s Regime.

Keep it compressed.
Use three one-line bullets only:
- Consensus
- Anti-consensus
- Second-order

### 9.3 Top Breakouts / Key Moves
Place this section near the top.

Purpose:
- surface the 1-3 most important new changes since the prior session
- add edge and actionability to the memo
- prevent the brief from becoming a purely structural framework without marginal information

Rules:
- include at most 3 items
- every item must answer:
  1. what changed
  2. why it matters
  3. what to watch next
- only include changes that validate or challenge the dominant thesis, or represent a meaningful breakout, divergence, or regime-relevant move
- do not include generic market summaries or repeated framework points

### 9.4 Best Expression & Position Bias
Include:
- best long
- best short
- best avoid
- Position Bias
- PM Notes / Trading Read

### 9.5 What Would Change My Mind
Include:
- IF / THEN triggers
- turning-point conditions
- risk re-rating triggers

### 9.6 Macro Transmission
Use the following substructure.

#### 9.6.1 Fed / Policy & Liquidity
Focus on:
- Fed net liquidity
- ON RRP
- balance sheet / reserves / QT context

Output:
- one integrated liquidity read

#### 9.6.2 Rates & FX Conditions
Focus on:
- US 2Y / 10Y
- 2s10s / 3m10y
- 10Y TIPS real yield
- DXY / EURUSD / USDJPY
- MOVE when directly available, otherwise use a Treasury realized-volatility proxy from 10Y yield changes

Output:
- one integrated rates & FX read

#### 9.6.3 Credit Transmission
Focus on:
- HY OAS
- IG OAS if available
- HYG / SPY
- KRE / SPY

Output:
- one integrated credit read

#### 9.6.4 Domestic Demand / Real Economy Nowcast
Fetch this section automatically before each U.S. morning brief.
Do not default this entire section to `EVIDENCE INSUFFICIENT` if stable latest-official public data is available.
It is acceptable to use the latest official weekly or monthly reading, refreshed on each daily run.
Keep the write-up compact.

##### Housing
Default stable public fields:
- 30Y mortgage rate (`MORTGAGE30US`)
- housing starts (`HOUST`)
- building permits (`PERMIT`)

Optional add-ons when reliably available:
- mortgage applications
- new / existing home sales
- homebuilder sentiment

Output:
- 2-3 key fields
- one-line read

##### Consumption
Default stable public fields:
- retail sales (`RSAFS`)
- total vehicle sales / SAAR (`TOTALSA`)
- real personal consumption expenditure (`PCEC96`) when available

Optional add-ons when reliably available:
- card / restaurant / travel proxies

Output:
- 2-3 key fields
- one-line read

##### Logistics / Trade
Default stable public fields:
- freight transportation services index (`TSIFRGHT`)
- trade / shipping proxy when reliably available

Optional add-ons:
- rail / truck / freight / port / shipping proxies

Output:
- 1-3 key fields
- one-line read

##### Industrial Activity
Default stable public fields:
- industrial production (`INDPRO`)
- capacity utilization (`TCU`)
- durable goods new orders (`DGORDER`) when available

Optional add-ons:
- ISM new orders
- capex / machinery / energy demand proxies

Output:
- 2-3 key fields
- one-line read

##### Composite Read
Always end with:
- `Domestic Demand Status: improving / mixed / weak`
- implications for U.S. equities:
  - if only consumption is firm -> narrow support, not broad cyclical expansion
  - if housing + industrial + logistics improve together -> broader growth re-acceleration
  - if all remain weak -> favor quality / defense / large-cap balance-sheet strength

#### 9.6.5 U.S. Market Liquidity
Focus on:
- ETF flow proxies
- volume / participation
- breadth
- positioning / crowdedness proxies

Output:
- one integrated read

#### 9.6.6 Price / Trend
Focus on:
- SPX / NDQ / RTY
- major factor trend
- key levels / slope

Output:
- one integrated read

#### 9.6.7 Internal Structure
Focus on:
- RSP / SPY
- IWM / SPY
- SPHB / SPLV
- breadth quality

Output:
- one integrated read

#### 9.6.8 Sector Expression
Focus on:
- Tech
- Financials
- Energy
- Industrials
- Defensives
- other regime-relevant sectors

Output:
- one integrated read

#### 9.6.9 Fundamental Validation
Do not default this block to `EVIDENCE INSUFFICIENT` if stable public profitability and margin proxies are available.

Default stable public core:
- corporate profits after tax (`CP`)
- unit labor costs (`ULCNFB`)
- labor productivity (`OPHNFB`)
- valuation compatibility versus rates / real yields

Optional enhanced layer when a stable public source is available:
- earnings season surprise summary
- guidance breadth / revisions summary

Focus on:
- whether profitability backdrop is improving, flat, or deteriorating
- whether margin pressure is easing or worsening
- whether productivity offsets cost pressure
- whether price is being driven by earnings or just multiple expansion

Output:
- 2-4 compact fields
- one integrated read

If only slow-moving official fundamental data is available, still provide a compact read from those latest official values instead of leaving the entire section empty.

#### 9.6.10 Reflexivity
Focus on:
- crowding
- vol/gamma regime if available
- positive vs negative reflexivity
- if JPY implied volatility is unavailable, use USDJPY 20-day realized volatility as the default proxy for carry-stress temperature

Output:
- one integrated read

### 9.7 Narrative vs Tape & Transmission
Include:
- Narrative
- Anti-consensus
- Tape
- 2-3 throughlines
- compressed regional scoreboard

### 9.8 News Validation
Use News Validation as a verification layer, not as the regime engine.

Rules:
- form regime and thesis from transmission first
- use news only to confirm, challenge, or explain the current thesis
- include 2-4 headlines max
- for each headline, always state:
  - source
  - whether it Supports / Conflicts / is just Noise
  - one-line implication

U.S. source priority:
1. Core market / macro press
   - Bloomberg / Reuters / WSJ / FT / CNBC
2. Official / policy
   - Federal Reserve / Treasury / BLS / BEA / Census / CBOE
3. Broader narrative context
   - NYT / WaPo / AP / major sector press

Do not let a single headline override the transmission framework.

### 9.9 Daily proxy policy (must stabilize output)
For the U.S. daily brief, the following should not remain routine hard gaps when a stable proxy exists:
- Europe breadth panel -> use Europe breadth proxy
- direct MOVE series -> use Treasury realized-volatility proxy
- JPY 1M vol -> use USDJPY realized-volatility proxy
- public daily sell-side revisions breadth -> downgrade to enhancement layer and use fundamental-validation proxy in daily mode

Only include an item in `Evidence Gaps` if it is a missing P0 field with no acceptable stable proxy.
Do not list optional enhancement fields as daily gaps.

### 9.10 Evidence Anchors
Use 8-12 anchors max.

### 9.11 Data Panel Appendix
Suggested panels:
- Fed / Policy & Liquidity
- Credit & Stress
- FX / Macro Shock
- Domestic Demand / Real Economy
- Breadth / Market Structure

---

## 10) Data Policy

### A-shares
Primary operational source in V1 can be documented simply as:
- `akshare`

When some fields are unavailable, it is acceptable to use:
- official webpages
- public reports / PDFs
- valid proxy indicators

### U.S.
Use the best available mix of:
- FRED
- Stooq / Yahoo / similar market proxies
- official or widely used public sources

### Practical data rule
These fields are **inputs to be auto-fetched before each brief**, not values to hardcode into the skill text.
The skill should define:
- what to fetch
- from where
- how often it updates
- what fallback or proxy is acceptable
- what to do when it fails

---

## 11) Writing Rules

### Conclusion first
Always front-load:
- regime
- one dominant thesis
- CAR snapshot
- top breakouts / key moves
- best expression
- position bias
- falsification

### Compress data, then interpret
Prefer:
- compact panel
- one integrated read
- one-line status blocks when a layer is slow-moving

Avoid:
- one paragraph per data point
- repetitive `signal:` after every bullet
- verbose daily expansion of slow-moving nowcast layers

### Reading hierarchy
Use three layers:
1. decision layer
2. reasoning layer
3. evidence layer

Meaning:
- sections 1-4 = what to do
- transmission section = why
- evidence anchors / appendix = proof

### Preserve human PM texture
Keep some human color in:
- Trading Read / PM Notes
- What Would Change My Mind
- crowding / pain-trade commentary

### Proxy language rule
When using a proxy, translate it into judgment language in the final memo.
Do not expose raw system phrasing unless the user explicitly asks for implementation detail.
Prefer:
- “Stock Connect breadth still looks weak”
- “credit-sensitive proxies are not confirming”
- “sector leadership remains defensive”

Avoid:
- “northbound proxy says…”
- “industry-expression proxy says…”
- “credit-risk proxy says…”

Do not let the memo become a sterile database dump.

---

## 12) Honest Limitations

Do not imply that the skill fully reproduces a live trading desk.

Examples of what it cannot fully replace:
- single-name leader stock tape reading
- transcript nuance from one sentence in a call
- real-time relative-value reads inside fragile credit or sector baskets
- execution-layer decisions: exact asset, exact level, exact size

When users ask if this is “real Stan”, answer in two layers:
1. The skill can meaningfully help with first-layer macro environment judgment.
2. The human still owns second-layer execution judgment.

---

## 13) Confidence Mapping

- high: most panels align and data coverage is complete
- medium: mixed signals or proxy data exists
- low: conflicting signals or major panel gaps

---

## 14) Safety Footer

Always append the standard disclaimer in the resolved user language:
- `Disclaimer: The above content is research framework information and does not constitute investment advice or trading instructions.`
