# CCDB Factor Search

Find the **best-fit CCDB / Carbonstop emission factor** for a real business scenario — not just a raw result list.

`ccdb-factor-search` is designed for carbon accounting, LCA modeling, PCF work, and factor-matching tasks where the key question is:

> **“Which factor should I actually use?”**

Instead of stopping at search results, this skill tries to identify the most suitable candidate, explain why it fits, flag risks, and show alternatives when the match is imperfect.

---

## What this skill is good at

Use this skill when you need to:

- find the most suitable **CCDB emission factor / carbon factor**
- compare multiple factor candidates and decide which one is usable
- search across **Chinese + English** terms for the same material / process
- reject mismatched results such as wrong region, wrong unit, or spend-based factors
- return a conservative `not_suitable` / `api_unavailable` result instead of forcing a weak recommendation

Typical use cases:

- product carbon footprint (PCF) modeling
- LCA inventory building
- supplier data factor matching
- sustainability consulting delivery
- bilingual factor lookup in CCDB / Carbonstop APIs

---

## Why this is better than a plain factor search

A normal search flow often gives you **a list of possible factors**.

This skill is built to go further:

- **bilingual search**: searches in Chinese and English, not just one language
- **iterative refinement**: broadens / narrows the search when first-pass results are weak
- **mismatch filtering**: downgrades wrong-region, wrong-unit, or spend-based candidates
- **best-fit recommendation**: selects one recommended factor when possible
- **risk-aware output**: explains caveats and shows alternatives
- **conservative fallback**: prefers `not_suitable` over a misleading answer

In short:

- **plain search** → “here are 10 factors”
- **this skill** → “this is the best candidate, here’s why, here are the risks, and here are the backups”

---

## Example prompts

### Example 1 — Chinese factor matching

> 请帮我找中国全国电网电力因子，单位最好是 tCO2e/MWh。

Expected behavior:
- searches electricity-related terms in both Chinese and English
- prioritizes China-related candidates
- checks unit fit
- explains whether the result is direct / close / fallback

### Example 2 — bilingual material lookup

> 帮我检索聚酯切片的碳因子，如果中文结果不好就切英文继续找。

Expected behavior:
- derives terms like 聚酯切片 / PET resin / PET chip / polyester resin
- compares candidates across rounds
- returns one recommended factor and alternatives

### Example 3 — conservative screening

> 请帮我找原铝的排放因子，优先物理量单位，不要误选成按金额计算的因子。

Expected behavior:
- rejects or downgrades spend-based / monetary-unit candidates
- prefers physical activity factors
- explains why the chosen candidate is safer to use

### Example 4 — no guessing when evidence is weak

> 我要找英国蒸汽因子，如果查不到合适的，不要猜，直接告诉我。

Expected behavior:
- returns `not_suitable` or `api_unavailable` when evidence is weak
- does not fabricate a confident recommendation

---

## Example output structure

A typical result should contain:

- **selected factor** (or top candidates)
- **match classification**
  - `direct_match`
  - `close_match`
  - `fallback_generic`
  - `not_suitable`
  - `api_unavailable`
- **why it was selected**
- **important risks / caveats**
- **alternatives considered**
- **search trace**
- **what clarification would improve matching**

---

## Runtime dependency

This skill depends on the Carbonstop CCDB API.

Current default endpoint:
- `https://gateway.carbonstop.com/management/system/website/queryFactorListClaw`

Current signing rule:
- `sign = md5("openclaw_ccdb" + name)`

Optional environment variables:
- `CCDB_API_BASE_URL`
- `CCDB_SIGN_PREFIX`

---

## Error handling / fallback behavior

This skill is intentionally conservative.

- if the API request fails, times out, or returns malformed data, it should report the failure instead of guessing
- if no suitable candidate is found, it should prefer `not_suitable`
- if constraints like region / unit / year are missing, it should surface that gap clearly
- if only weak candidates are available, it should return them as fallback candidates with risk notes, not as a fake direct match

This matters because **a wrong factor is often worse than no factor** in carbon accounting workflows.

---

## Known limitations

- some factor values are encrypted in the API response
- some scenarios may only yield close/fallback matches rather than direct matches
- steam-related queries may still return broader heat/steam fallback candidates depending on data coverage
- data quality and API coverage directly affect result quality

---

## Included resources

- `scripts/query_ccdb.py` — API query + ranking helper
- `references/api-contract.md` — API contract notes
- `references/matching-strategy.md` — matching / rejection rules
- `references/output-template.md` — output format guidance
- `references/domain-lexicon.md` — domain vocabulary
- `references/workflow.md` — end-to-end search workflow
- `evals/evals.json` — example eval set
