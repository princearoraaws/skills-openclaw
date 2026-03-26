---
name: ccdb-factor-search
description: Search and select the best-fit CCDB carbon/emission factor from a Carbonstop API by extracting keywords from the user request, querying in both Chinese and English, iteratively refining search terms, screening unsuitable candidates, and returning the most suitable factor with reasoning, risks, alternatives, and search trace. Use when the user asks to find, match, compare, verify, or choose 碳因子 / 排放因子 / emission factors / carbon factors from CCDB or a connected factor API, especially when the user needs the most suitable factor rather than a raw result list.
---

# CCDB Carbon Factor Search

Use this skill to retrieve and judge CCDB carbon-factor candidates from a supplied API.

Before implementation or live querying, read `references/workflow.md`, `references/api-contract.md`, and `references/matching-strategy.md`.

## Core behavior

1. Parse the user request into structured search intent.
2. Always search both Chinese and English terms for non-trivial requests, not just one language.
3. Expand to synonyms, broader terms, and narrower process terms when the first results are weak.
4. Review returned factors for semantic fit against the user's intended material, process, geography, lifecycle stage, unit, and scenario.
5. Screen out or downgrade unsuitable results such as region-mismatched, unit-mismatched, or spend-based factors when the user wants physical activity factors.
6. Compare candidates across all search rounds and select the best-fit factor, not merely the first returned factor.
7. Return the chosen factor with reasoning, risks, alternatives, and search trace.
8. If no suitable factor is found, report the attempted terms and the missing constraints needed for a better match.

## Implementation notes

- Put API-calling logic in `scripts/query_ccdb.py`.
- Keep API-specific configuration outside SKILL.md when possible.
- If the API contract changes, update `references/api-contract.md` and the script together.
- If suitability scoring becomes complex, keep that logic in the script or a helper module instead of overloading prompt instructions.

## Expected output

Return a concise result block containing:
- selected factor or top candidates
- why it matches
- important caveats
- original and refined search terms used
- whether more user clarification is needed

## Bundled resources

- `references/workflow.md`: end-to-end query and suitability workflow
- `references/api-contract.md`: real request/response format for the Carbonstop CCDB API
- `references/matching-strategy.md`: ranking, rejection, and multi-round search rules
- `references/output-template.md`: final answer template for user-facing results
- `scripts/query_ccdb.py`: local API query helper