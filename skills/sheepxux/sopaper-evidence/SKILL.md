---
name: sopaper-evidence
description: Evidence-first research workflow for paper writing. Use when the task requires searching, verifying, and organizing real papers, datasets, benchmarks, case studies, and project artifacts for research writing without fabricating results, citations, or claims.
---

# Sopaper Evidence

Sopaper Evidence is an evidence-first research skill. Its job is to build a reliable evidence pack before supporting any paper outline, abstract, related work summary, experiment plan, or draft section.

Version: `v0.2`

## Use this skill when

- The user wants to turn a project into a paper without inventing evidence
- The task requires finding prior papers, datasets, benchmarks, baselines, or case studies
- The task requires mapping claims to verified sources
- The task requires identifying evidence gaps before writing
- The user wants related work or experiment planning grounded in real sources

## Hard rules

- Do not fabricate papers, authors, venues, dates, citations, datasets, benchmarks, experiments, or numerical results
- Prefer primary sources over summaries, reposts, or blog interpretations
- Separate verified facts from inference and open questions
- If evidence is missing, say it is missing and recommend what to collect next
- Do not state that the user's method outperforms baselines unless there is explicit evidence
- Every writing-oriented output must be traceable to evidence items

## Source priority

Use the highest-quality source available for each claim.

1. User-provided project artifacts: experiment logs, tables, code, configs, internal notes
2. Primary external sources: papers, official docs, benchmark leaderboards, dataset pages, project repos
3. Secondary summaries: blogs, news posts, third-party explainers

Read [references/source-priority.md](references/source-priority.md) when source quality or conflicts matter.

## Core workflow

### 1. Scope the task

Collect or infer:

- Project name
- Research topic
- Core problem
- Method summary
- Existing evidence and file paths
- Target venue or paper style if known

If the project scope is unclear, produce a short working scope and label assumptions.

### 2. Search for evidence

Search for:

- Prior work
- Benchmarks and datasets
- Baseline methods
- Comparable case studies
- Official metrics definitions
- Relevant project artifacts in the local repository

For each source, capture the title, URL or path, source type, and why it matters.

Use [references/prior-work-search-playbook.md](references/prior-work-search-playbook.md) for a repeatable search process.

### 3. Verify and classify

For each evidence item, classify it as:

- `verified_fact`
- `project_evidence`
- `inference`
- `unverified`

Do not merge these labels. If a statement depends on inference, say so explicitly.

### 4. Extract structured evidence

Use the schema in [references/evidence-schema.md](references/evidence-schema.md).

At minimum, extract:

- Claim or observation
- Source
- Evidence type
- Scope and limitations
- Relevance to the user's paper

### 5. Build the evidence map

Organize findings into:

- `related_work`
- `datasets_and_benchmarks`
- `baselines`
- `case_studies`
- `project_results`
- `claim_to_evidence`
- `evidence_gaps`

Use [assets/claim-evidence-map-template.md](assets/claim-evidence-map-template.md) when the user needs a reusable deliverable.
Use [assets/related-work-matrix-template.md](assets/related-work-matrix-template.md) when comparing papers, baselines, and benchmark coverage.

### 6. Support writing

Only after the evidence map is complete, support tasks such as:

- contribution candidates
- related work summary
- abstract support points
- experiment plan
- paper outline

Before writing, run the checks in [references/claim-audit-rules.md](references/claim-audit-rules.md).
Use [assets/paper-outline-from-evidence-template.md](assets/paper-outline-from-evidence-template.md) when the user needs a draft-safe paper structure.

## Output requirements

Unless the user asks for something else, default to this output shape:

1. `Evidence brief`
2. `Key sources`
3. `Claim-to-evidence map`
4. `Evidence gaps`
5. `Safe writing notes`

See the example set in:

- [examples/openclaw-input.md](examples/openclaw-input.md)
- [examples/openclaw-search-plan.md](examples/openclaw-search-plan.md)
- [examples/openclaw-evidence-brief.md](examples/openclaw-evidence-brief.md)
- [examples/openclaw-claim-map.md](examples/openclaw-claim-map.md)
- [examples/openclaw-paper-outline.md](examples/openclaw-paper-outline.md)

## Writing constraints

When supporting paper writing:

- Tie each major claim to one or more evidence items
- Avoid precise quantitative wording unless the number is verified
- Mark missing comparisons, missing ablations, and missing real-world validation
- Prefer conservative wording over overstated conclusions

## OpenClaw-specific guidance

When the user is working on OpenClaw or a similar embodied AI / robotics project, prioritize:

- manipulation benchmarks
- long-horizon task evidence
- policy or planner comparisons
- real-world versus simulation evidence
- ablations on perception, planning, or control components

Do not assume OpenClaw has capabilities, datasets, or benchmark wins unless they are present in project artifacts or verified sources.
Use [references/benchmark-baseline-checklist.md](references/benchmark-baseline-checklist.md) before accepting benchmark-fit or baseline coverage claims.
