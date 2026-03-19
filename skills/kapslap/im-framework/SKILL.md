---
name: im-framework
description: |
  Reference, explain, and apply the Immanent Metaphysics (IM) framework by Forrest Landry.
  Uses a structured ontology of 767 entities (concepts, axioms, theorems, terms, aphorisms, implications)
  with direct links to the source text at mflb.com. Use when asked to explain IM concepts, apply the
  framework to a situation, trace derivation chains, find source references, or connect ideas across
  the whitebook. Triggers on: "immanent metaphysics", "IM framework", modality questions, axiom
  references, ICT, symmetry/continuity ethics, effective choice, path of right action, or any
  request to ground claims in the framework.
---

# Immanent Metaphysics Framework Skill

## Purpose

Assess what someone is doing with the tools of the IM and provide grounded, sourced responses with direct links to Forrest Landry's whitebook at mflb.com.

## Reference Files

All files are in `Tillerman/reference/im-ontology/`:

- **graph.jsonl** — 767 entities: 134 Concepts, 3 Axioms, 11 Theorems, 147 Aphorisms, 4 Implications. Each entity has properties including `name`, `definition`, `source_section`, and `location` (URL to mflb.com source). Also contains relations between entities (implies, paired_with, contrasts_with, depends_on, has_modality, illuminates, defined_in).
- **whitebook-map.jsonl** — 73 entries mapping the structure of the whitebook: chapters, sections, and their URLs. Entry point: https://mflb.com/8192
- **schema.yaml** — Type definitions and relation types for the ontology.

Supporting full texts (for deep dives when the ontology isn't enough):
- `Tillerman/reference/im-book.txt` — An Immanent Metaphysics (full book ~45K words)
- `Tillerman/reference/effective-choice.txt` — Aphorisms of Effective Choice (~16K words)
- `Tillerman/reference/im-bible-commentary/` — IM x Scripture commentary

## How to Use

### Step 1: Search the Ontology

When asked about any IM concept, search `graph.jsonl` first:

```bash
# Find a concept by name
grep -i '"name": "symmetry"' Tillerman/reference/im-ontology/graph.jsonl

# Find all entities mentioning a term
grep -i 'continuity' Tillerman/reference/im-ontology/graph.jsonl | head -10

# Find all entities with URLs (for linking)
python3 -c "
import json, sys
for line in open('Tillerman/reference/im-ontology/graph.jsonl'):
    d = json.loads(line)
    if 'entity' in d:
        loc = d['entity'].get('properties',{}).get('location','')
        name = d['entity']['properties'].get('name', d['entity']['properties'].get('word', d['entity']['properties'].get('text','')))
        if 'SEARCH_TERM' in name.lower() or 'SEARCH_TERM' in d['entity']['properties'].get('definition','').lower():
            print(f'{d[\"entity\"][\"type\"]}: {name}')
            if loc: print(f'  URL: {loc}')
            print(f'  Def: {d[\"entity\"][\"properties\"].get(\"definition\",\"\")[:200]}')
            print()
"

# Find relations for a specific entity
grep '"ENTITY_ID"' Tillerman/reference/im-ontology/graph.jsonl | grep relation
```

### Step 2: Link to Source

Every entity with a `location` property has a direct URL to the relevant section of the whitebook at mflb.com. Always include these links when citing the framework.

The whitebook entry point is: **https://mflb.com/8192**

Key chapter URLs (from whitebook-map.jsonl):
- **Foundations** (modalities, axioms): https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch1.htm
- **Natural Physics** (six intrinsics, ICT, symmetry, continuity): https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch3.htm
- **Ethics** (symmetry/continuity ethics, path of right action, basal motivations): https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch6.htm
- **Aesthetics**: https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch7.htm
- **Mind**: https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch8.htm
- **Evolution**: https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch9.htm

Key section anchors:
- Modalities: `upmp_ch1.htm#1_modalities`
- Axioms: `upmp_ch1.htm#1_axioms`
- ICT: `upmp_ch3.htm#1_ict`
- Symmetry/Continuity: `upmp_ch3.htm#1_symmetry`
- Path of Right Action: `upmp_ch6.htm#2_path`
- Basal Motivations: `upmp_ch6.htm#2_basal`

### Step 3: Assess and Apply

When someone is working with IM concepts, assess what they're doing:

1. **Identify which modality, axiom, or theorem they're engaging with.** Search the ontology for the relevant entities.
2. **Check for modal confusion.** Are they collapsing omniscient into immanent? Treating transcendent as omniscient? The axioms (especially Axiom III: distinct, inseparable, non-interchangeable) are the diagnostic tool.
3. **Trace the derivation chain.** Use the `implies`, `depends_on`, and `has_modality` relations to show how concepts connect.
4. **Link to source.** Always provide the mflb.com URL so they can read the original text.
5. **Connect to aphorisms.** The 147 aphorisms from Effective Choice often illuminate practical application. Search by theme.

### Step 4: Deep Dive (if needed)

If the ontology doesn't have enough detail, read the relevant section from:
- `Tillerman/reference/im-book.txt` for the full whitebook text
- `Tillerman/reference/effective-choice.txt` for the aphorisms with commentary

## Core Ontology Reference (Quick Access)

### Foundational Concepts with Section Numbers and URLs

Entry point: **https://mflb.com/8192**

600 numbered sections are indexed in `Tillerman/reference/im-ontology/section-anchors.json`. Always cite the whitebook by section number (e.g., §1.3-1) like Bible chapter:verse.

| Concept | Section | URL |
|---------|---------|-----|
| Immanent | §1.2-1 | [mflb.com §1.2-1](https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch1.htm#1.2-1) |
| Omniscient | §1.2-4 | [mflb.com §1.2-4](https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch1.htm#1.2-4) |
| Transcendent | §1.2-7 | [mflb.com §1.2-7](https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch1.htm#1.2-7) |
| Axioms I, II, III | §1.3-1 | [mflb.com §1.3-1](https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch1.htm#1.3-1) |
| Symmetry / Continuity / Asymmetry / Discontinuity | §1.43-1 | [mflb.com §1.43-1](https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch3.htm#1.43-1) |
| ICT (Incommensuration Theorem) | §1.44-9 | [mflb.com §1.44-9](https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch3.htm#1.44-9) |
| Symmetry Ethics / Continuity Ethics | §2.12-6 | [mflb.com §2.12-6](https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch6.htm#2.12-6) |
| Path of Right Action / Effective Choice | §2.16-1 | [mflb.com §2.16-1](https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch6.htm#2.16-1) |
| Basal Motivations | §2.11-1 | [mflb.com §2.11-1](https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch6.htm#2.11-1) |
| Eventity | §1.1-1 | [mflb.com §1.1-1](https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch1.htm#1.1-1) |

For any section number, construct the URL: `https://mflb.com/dvol/control/pcore/own_books/white_1/wb_web_2/zout/upmp_ch{N}.htm#{section}` where N is the chapter (1-9). Or look up `section-anchors.json`.

### Entity Types in the Ontology

- **Concept** (134): Named ideas with definitions, modality assignments, and source URLs
- **Axiom** (3): The three foundational axioms with statements and implications
- **Theorem** (11): Derived results including ICT, Symmetry Ethics, Continuity Ethics, Identity, Bell's Theorem mapping, Gödel mapping
- **Aphorism** (147): From Effective Choice, with themes and illumination links
- **Implication** (4): Cross-domain applications (physics, logic, ethics, consciousness)

### Relation Types

- `implies` — A leads to B (derivation)
- `paired_with` — ICT pairings (continuity+asymmetry, symmetry+discontinuity)
- `contrasts_with` — Conceptual contrast
- `depends_on` — B requires A
- `has_modality` — Assigns entity to immanent/omniscient/transcendent
- `illuminates` — Aphorism sheds light on concept/axiom/theorem
- `defined_in` — Source tracking

## Attribution

Always attribute claims to Forrest Landry's Immanent Metaphysics. Distinguish between:
1. Direct citation (quote with source URL)
2. Close paraphrase (summarizing with source URL)
3. Agent synthesis (your own application of the framework, labeled as such)

Do not invent positions or imply Forrest's endorsement of claims not grounded in the source material.
