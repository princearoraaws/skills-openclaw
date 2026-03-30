---
name: clinical-trial-search
description: "Search clinical trial databases similar to ClinicalTrials.gov. Use this skill whenever the user asks about clinical trials, drug trials, indications, targets, drug names, trial phases, NCT IDs, enrollment, or recruitment. Automatically parses natural language questions into structured query parameters and calls the backend API to return matching trial records. Trigger words include: clinical trial, NCT, drug development, indication, target, phase, enrollment, recruitment, sponsor, cohort, arm, endpoint, efficacy, safety data."
---

# Clinical Trial Search Skill

This skill converts natural language questions into structured API queries against a clinical trial database, then presents the results in a readable format.

## Workflow

1. **Parse user intent** — Extract key entities from the user's question
2. **Build query parameters** — Map entities to the `ClinicalTrialSearchData` schema
3. **Execute the query** — Run `scripts/search.py`
4. **Present results** — Format and display trials to the user

## Step 1: Extract Keywords

Identify the following entity types from the user's question:

| Field | Type | Description                       | Example                                                   |
|-------|------|-----------------------------------|-----------------------------------------------------------|
| `nctid` | `List[str]` | NCT identifier(s)                 | `["NCT04280783"]`                                         |
| `acronym` | `List[str]` | Trial acronym(s)                  | `["KEYNOTE-590"]`                                         |
| `company` | `List[str]` | Sponsor company name(s)           | `["Pfizer", "Roche"]`                                     |
| `indication` | `List[str]` | Disease / indication              | `["lung cancer", "NSCLC"]`                                |
| `phase` | `List[str]` | Trial phase(s)                    | `["Phase 1", "Phase 3"]`                                  |
| `target` | `dict` | Biological target(s)              | `{"logic": "or", "data": ["PD-1", "VEGF"]}`               |
| `drug_name` | `dict` | Drug name(s)                      | `{"logic": "or", "data": ["pembrolizumab"]}`              |
| `drug_modality` | `dict` | Drug modality / type              | `{"logic": "or", "data": ["antibody", "small molecule"]}` |
| `drug_feature` | `dict` | Drug feature(s)                   | `{"logic": "or", "data": ["bispecific"]}`                 |
| `location` | `dict` | Trial location(s)                 | `{"logic": "or", "data": ["China", "USA"]}`               |
| `route_of_administration` | `dict` | Route of administration           | `{"logic": "or", "data": ["IV", "oral"]}`                 |
| `has_result_summary` | `bool` | Only trials with result summaries | `true`                                                    |
| `official_data` | `bool` | Only official data sources        | `false`                                                   |
| `page_num` | `int` | Page index (0-based)              | `0`                                                       |
| `page_size` | `int` | Results per page (1–10)          | `10`                                                       |

**Dict field format:**
```json
{"logic": "or", "data": ["value1", "value2"]}
```

- `logic` controls how multiple values are combined: `"or"` (any match) or `"and"` (all must match). Default to `"or"` unless the user explicitly wants all terms to apply simultaneously.
- `data` is the list of keyword strings to match.

**Type rules:**
- `indication`, `acronym`, `company`, `nctid`, `phase` → plain `List[str]`
- `target`, `drug_name`, `drug_modality`, `drug_feature`, `location`, `route_of_administration` → `dict` with `logic` and `data`
- Default to `page_num: 0, page_size: 5` unless the user specifies otherwise
- Prefer English keywords (the database is indexed in English); translate non-English terms

## Step 2: Execute the Query

```bash
python scripts/search.py --params '<JSON string>'
```

Or using a parameter file:

```bash
python scripts/search.py --params-file /tmp/query.json
```

Add `--raw` to receive the unformatted JSON response.

## Step 3: Interpret Results

The response contains:
- `total` — total number of matching trials
- `trials` — current page of results, each with NCT ID, title, phase, status, indication, drugs, sponsor, etc.

If results exceed 100, prompt the user to narrow the query. If no results are returned, suggest relaxing one or more filters.

## Conversion Examples

**User:** "Find Phase 3 trials of PD-1 antibodies in lung cancer that have results"

**Parameters:**
```json
{
  "target": {"logic": "or", "data": ["PD-1"]},
  "drug_modality": {"logic": "or", "data": ["antibody"]},
  "indication": ["lung cancer"],
  "phase": ["Phase 3"],
  "has_result_summary": true,
  "page_num": 0,
  "page_size": 10
}
```

---

**User:** "Look up NCT04280783"

**Parameters:**
```json
{
  "nctid": ["NCT04280783"],
  "page_num": 0,
  "page_size": 1
}
```

---

**User:** "Roche bispecific antibody trials in China"

**Parameters:**
```json
{
  "company": ["Roche"],
  "location": {"logic": "or", "data": ["China"]},
  "drug_feature": {"logic": "or", "data": ["bispecific"]},
  "page_num": 0,
  "page_size": 10
}
```

---

**User:** "Oral small molecule KRAS G12C inhibitors in colorectal cancer"

**Parameters:**
```json
{
  "target": {"logic": "or", "data": ["KRAS G12C"]},
  "drug_modality": {"logic": "or", "data": ["small molecule"]},
  "route_of_administration": {"logic": "or", "data": ["oral"]},
  "indication": ["colorectal cancer"],
  "page_num": 0,
  "page_size": 10
}
```

## Dependencies

- Python 3.8+
- `requests` library (`pip install requests`)
- Environment variable `NOAH_API_TOKEN` — API authentication token (required)
  - Register for a free account at [noah.bio](https://noah.bio) to obtain your API key.