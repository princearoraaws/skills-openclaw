# GEO Audit Scoring Guide

## Composite Score Formula

```
GEO Score = Technical × 0.20 + Citability × 0.35 + Schema × 0.20 + Brand × 0.25
```

### Weight Rationale

Weights are derived from empirical research on AI citation behavior:

| Dimension | Weight | Evidence |
|-----------|--------|----------|
| Technical Accessibility | 20% | Baseline requirement — if AI crawlers can't access content, nothing else matters. Binary gate effect observed in crawler access studies. |
| Content Citability | 35% | Highest weight. Princeton GEO research (Aggarwal et al., 2023) found content optimization strategies produced 115-415% visibility improvements. Georgia Tech studies confirm quotable content blocks are the #1 citation driver. |
| Structured Data | 20% | Schema.org markup increases AI entity understanding by 40%+ (Google Search Central data). Speakable schema directly feeds voice/AI answer selection. |
| Entity & Brand Signals | 25% | Cross-source brand consistency correlates with 2.5× higher AI citation rates (BrightEdge). Knowledge graph presence is a strong trust signal for LLMs. |

---

## Score Bands

| Grade | Range | Label | Interpretation |
|-------|-------|-------|----------------|
| **A** | 85-100 | Excellent | AI-optimized site. Likely cited by major AI engines. Focus on maintaining and monitoring. |
| **B** | 70-84 | Good | Solid foundation with specific gaps. Targeted fixes can push to A-tier within 30 days. |
| **C** | 50-69 | Developing | Significant opportunities exist. Structured 30-day plan needed. Expect 15-25 point improvement potential. |
| **D** | 30-49 | Needs Work | Major gaps across multiple dimensions. Prioritize critical/high issues first. |
| **F** | 0-29 | Critical | Fundamental problems blocking AI discovery. Emergency triage required. |

---

## Business Type Weight Adjustments

Different business types have different AI visibility priorities. Apply these multipliers to sub-dimension scores before computing the dimension total:

### SaaS / Technology

| Adjustment | Rationale |
|-----------|-----------|
| Technical: Rendering +10% | SPAs common, SSR critical |
| Citability: Answer Blocks +10% | Feature comparison queries dominate |
| Schema: AI-Boost (HowTo, FAQ) +15% | Tutorial/documentation patterns |
| Brand: Community Signals +10% | Developer communities drive citations |

### E-commerce

| Adjustment | Rationale |
|-----------|-----------|
| Schema: Product/Offer +20% | Product schema directly feeds shopping AI |
| Citability: Statistical Density +15% | Price, specs, comparisons |
| Brand: Third-Party Reviews +15% | Review aggregation critical |
| Technical: Speed +10% | Performance affects crawl budget |

### Publisher / Media

| Adjustment | Rationale |
|-----------|-----------|
| Citability: All sub-dimensions +10% | Content is the product |
| Schema: Article/NewsArticle +15% | Freshness and authorship signals |
| Brand: Entity Recognition +10% | Journalist/author entities matter |
| Technical: Meta Signals +10% | Canonical, dates, authorship headers |

### Local Business

| Adjustment | Rationale |
|-----------|-----------|
| Schema: LocalBusiness +25% | NAP consistency, geo-targeting |
| Brand: Third-Party (directories) +20% | Google Business, Yelp, industry dirs |
| Citability: Self-Containment +10% | Location + service description completeness |
| Technical: Standard weights | No significant adjustment needed |

### Agency / Professional Services

| Adjustment | Rationale |
|-----------|-----------|
| Brand: Entity Recognition +15% | Thought leadership, executive profiles |
| Citability: Expertise Signals +15% | Case studies, credentials, expert quotes |
| Schema: Organization + Person +10% | Team expertise schema |
| Technical: Standard weights | No significant adjustment needed |

---

## Dimension 1: Technical Accessibility (0-100)

### AI Crawler Access (40 points)

| Check | Points | Scoring |
|-------|--------|---------|
| robots.txt existence | 5 | Present = 5, Missing = 2 (permissive default) |
| GPTBot access | 5 | Allowed = 5, Blocked = 0 |
| Google-Extended access | 5 | Allowed = 5, Blocked = 0 |
| ClaudeBot access | 4 | Allowed = 4, Blocked = 0 |
| Bytespider access | 3 | Allowed = 3, Blocked = 0 |
| PerplexityBot access | 3 | Allowed = 3, Blocked = 0 |
| Other AI bots (Applebot-Extended, CCBot, cohere-ai, Amazonbot, FacebookBot, Meta-ExternalAgent) | 6 | 1 point each |
| X-Robots-Tag headers | 4 | No restrictive AI tags = 4 |
| Meta robots tags | 5 | No noindex/nofollow for AI = 5 |

### Rendering & Content Delivery (25 points)

| Check | Points | Scoring |
|-------|--------|---------|
| Server-side rendering | 10 | Full SSR = 10, Partial/Hybrid = 7, CSR-only = 2 |
| llms.txt presence | 8 | Present + valid = 8, Present + incomplete = 4, Missing = 0 |
| Content in initial HTML | 7 | >80% content in source = 7, 50-80% = 4, <50% = 1 |

### Speed & Accessibility (20 points)

| Check | Points | Scoring |
|-------|--------|---------|
| HTTPS | 5 | Yes = 5, No = 0 |
| Response time | 5 | <1s = 5, 1-3s = 3, >3s = 1 |
| Compression (gzip/brotli) | 3 | Enabled = 3, Disabled = 0 |
| Sitemap presence | 4 | Valid XML sitemap = 4, HTML only = 2, None = 0 |
| Mobile viewport | 3 | Present = 3, Missing = 0 |

### Meta & Header Signals (15 points)

| Check | Points | Scoring |
|-------|--------|---------|
| Title tag | 3 | Present + <60 chars = 3, Present + long = 2, Missing = 0 |
| Meta description | 3 | Present + 120-160 chars = 3, Present + wrong length = 2, Missing = 0 |
| Canonical URL | 3 | Present + correct = 3, Present + wrong = 1, Missing = 0 |
| Open Graph tags | 3 | og:title + og:description + og:image = 3, Partial = 1-2, None = 0 |
| Lang attribute | 3 | Present = 3, Missing = 0 |

---

## Dimension 2: Content Citability (0-100)

### Answer Block Quality (25 points)

| Check | Points | Scoring |
|-------|--------|---------|
| Q+A pattern presence | 8 | Clear question-answer blocks = 8, Implicit = 4, None = 0 |
| Definition blocks | 6 | "[Term] is..." patterns = 6, Vague definitions = 3, None = 0 |
| FAQ content sections | 6 | Structured FAQ = 6, Informal Q&A = 3, None = 0 |
| Direct answer leads | 5 | Paragraphs starting with direct answers = 5, Buried answers = 2, None = 0 |

### Self-Containment (20 points)

| Check | Points | Scoring |
|-------|--------|---------|
| Context independence | 8 | Passages understandable standalone = 8, Need context = 3 |
| Term definitions inline | 6 | Technical terms defined at first use = 6, Assumed knowledge = 2 |
| Complete thought units | 6 | Each section is self-contained = 6, Cross-references required = 2 |

### Statistical Density (20 points)

| Check | Points | Scoring |
|-------|--------|---------|
| Quantitative data | 7 | Specific numbers/percentages present = 7, Vague = 2 |
| Source citations | 7 | Named sources for claims = 7, Unsourced = 2 |
| Data recency | 6 | Data within 2 years = 6, 2-5 years = 3, >5 years = 1 |

*Research note: Including statistics increases AI citation probability by 30% (Aggarwal et al., 2023)*

### Structural Clarity (20 points)

| Check | Points | Scoring |
|-------|--------|---------|
| Heading hierarchy | 6 | Proper H1→H2→H3 nesting = 6, Skipped levels = 3, Flat = 0 |
| Lists and tables | 5 | Present for appropriate content = 5, All prose = 1 |
| Paragraph length | 5 | Avg 2-4 sentences = 5, >6 sentences avg = 2 |
| Content chunking | 4 | Logical sections with clear breaks = 4, Wall of text = 0 |

### Expertise Signals (15 points)

| Check | Points | Scoring |
|-------|--------|---------|
| Author byline | 5 | Named author with bio = 5, Name only = 3, None = 0 |
| Expert quotes | 5 | Direct expert quotations = 5, Paraphrased = 2, None = 0 |
| Publication dates | 5 | Published + updated dates = 5, Published only = 3, None = 0 |

*Research note: Expert quotations increase AI citation by 41% (Aggarwal et al., 2023)*

---

## Dimension 3: Structured Data (0-100)

### Core Identity Schema (30 points)

| Check | Points | Scoring |
|-------|--------|---------|
| Organization/LocalBusiness | 12 | Present + complete = 12, Present + incomplete = 6, Missing = 0 |
| sameAs links | 8 | 3+ platforms linked = 8, 1-2 = 4, None = 0 |
| Logo + contactPoint | 5 | Both present = 5, One = 3, None = 0 |
| WebSite + SearchAction | 5 | Present = 5, Missing = 0 |

### Content Schema (25 points)

| Check | Points | Scoring |
|-------|--------|---------|
| Article/BlogPosting | 8 | Present on content pages = 8, Missing = 0 |
| Author markup | 7 | Person schema with details = 7, Name only = 3, None = 0 |
| datePublished/Modified | 5 | Both present = 5, Published only = 3, None = 0 |
| Speakable property | 5 | Present + valid selectors = 5, Missing = 0 |

### AI-Boost Schema (25 points)

| Check | Points | Scoring |
|-------|--------|---------|
| FAQPage | 8 | Valid FAQ schema = 8, Invalid = 2, Missing = 0 |
| HowTo | 6 | Present where appropriate = 6, Missing = 0 |
| BreadcrumbList | 5 | Present + valid = 5, Missing = 0 |
| Business-specific schema | 6 | Product/Service/Event as appropriate = 6, Missing = 0 |

### Schema Quality (20 points)

| Check | Points | Scoring |
|-------|--------|---------|
| JSON-LD format | 8 | All schemas in JSON-LD = 8, Mixed = 4, Microdata only = 2 |
| Syntax validity | 7 | No errors = 7, Minor errors = 3, Major errors = 0 |
| Required properties | 5 | All required props present = 5, Some missing = 2 |

---

## Dimension 4: Entity & Brand Signals (0-100)

### Entity Recognition (30 points)

| Check | Points | Scoring |
|-------|--------|---------|
| Wikipedia/Wikidata presence | 12 | Wikipedia article exists = 12, Wikidata only = 6, Neither = 0 |
| Knowledge panel indicators | 10 | Strong entity signals = 10, Partial = 5, None = 0 |
| sameAs/owl:sameAs linking | 8 | Bidirectional links = 8, One-way = 4, None = 0 |

### Third-Party Presence (25 points)

| Check | Points | Scoring |
|-------|--------|---------|
| LinkedIn company page | 6 | Active + complete = 6, Exists = 3, None = 0 |
| Crunchbase/industry databases | 6 | Present + detailed = 6, Basic = 3, None = 0 |
| Industry directories | 7 | 3+ relevant directories = 7, 1-2 = 4, None = 0 |
| Review platforms | 6 | G2/Capterra/Trustpilot presence = 6, One platform = 3, None = 0 |

### Community Signals (25 points)

| Check | Points | Scoring |
|-------|--------|---------|
| Reddit mentions | 8 | Active discussion threads = 8, Mentioned = 4, None = 0 |
| YouTube presence | 7 | Brand channel or reviews = 7, Mentions = 3, None = 0 |
| Forum/community activity | 5 | Active in relevant communities = 5, Passive = 2, None = 0 |
| GitHub/open source | 5 | Active repos = 5, Profile only = 2, None = 0 (tech companies) |

### Cross-Source Consistency (20 points)

| Check | Points | Scoring |
|-------|--------|---------|
| Brand name consistency | 7 | Same name across all platforms = 7, Variations = 3 |
| Description alignment | 7 | Consistent brand description = 7, Conflicting = 2 |
| Contact info consistency | 6 | NAP consistent everywhere = 6, Inconsistencies = 2 |

---

## Issue Priority Classification

Issues are classified by impact and effort:

| Priority | Impact | Typical Fix Time | Examples |
|----------|--------|-----------------|----------|
| **Critical** | >15 point potential | Immediate | AI crawlers blocked, no HTTPS, major schema errors |
| **High** | 8-15 point potential | 1-3 days | Missing llms.txt, no FAQ schema, poor answer blocks |
| **Medium** | 3-7 point potential | 1-2 weeks | Incomplete sameAs, missing author markup, paragraph length |
| **Low** | 1-2 point potential | Ongoing | Minor meta tag improvements, additional directory listings |

---

## Research Foundation

This scoring methodology synthesizes findings from:

1. **Aggarwal et al. (2023)** — "GEO: Generative Engine Optimization" (Princeton/Georgia Tech) — foundational GEO research establishing content optimization impact on AI visibility
2. **BrightEdge Research (2024-2025)** — Cross-source brand consistency and AI citation correlation studies
3. **Google Search Central** — Schema.org implementation guidelines and rich result impact data
4. **Zyppy/SparkToro studies** — Zero-click search trends and AI answer source analysis
5. **101 industry sources** — Compiled in the raw research data directory
