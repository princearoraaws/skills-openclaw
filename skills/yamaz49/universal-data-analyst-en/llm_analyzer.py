#!/usr/bin/env python3
"""
LLM Analyzer - Core module for LLM-based reasoning and judgment

This module handles:
1. Data ontology identification (LLM reasoning)
2. Analysis planning (LLM reasoning)
3. Analysis script generation (LLM reasoning)
4. Analysis report generation (LLM reasoning)

Key feature: Every judgment invokes an LLM — no hardcoded keyword matching
"""

import os
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class OntologyResult:
    """Data ontology identification result"""
    entity_type: str  # transaction/event, state/stock, relationship/network, feature/attribute, time-series/trajectory
    entity_type_reason: str  # reasoning basis
    generation_mechanism: str  # observation/experiment/simulation/measurement/reporting
    mechanism_reason: str  # reasoning basis
    core_dimensions: List[Dict[str, str]]  # core dimensions and descriptions
    is_economic: bool
    economic_type: Optional[str]  # if economic data, specific type
    domain_type: str  # domain type (e.g., labor market, earth science)
    keywords: List[str]  # 3-5 keyword tags
    recommended_questions: List[str]  # question types this data can answer
    limitations: List[str]  # data limitations
    confidence: str  # high/medium/low


@dataclass
class AnalysisPlan:
    """Analysis plan"""
    question_type: str  # descriptive/diagnostic/predictive/prescriptive/causal
    question_type_reason: str  # reasoning basis
    frameworks: List[Dict[str, str]]  # recommended frameworks and rationale
    analysis_steps: List[Dict[str, Any]]  # analysis step details
    scripts: List[Dict[str, str]]  # script list
    expected_outputs: List[str]  # expected outputs
    prerequisites: List[str]  # prerequisites/data requirements
    risks: List[str]  # potential risks


class LLMAnalyzer:
    """LLM Analyzer - Encapsulates all calls that require LLM reasoning"""

    def __init__(self):
        self.conversation_history = []

    def identify_ontology(self, data_profile: Dict[str, Any]) -> OntologyResult:
        """
        Step 1: Data ontology identification

        LLM reasoning to determine:
        - What type of data this is (entity type)
        - How the data was generated (generation mechanism)
        - What core dimensions exist
        - Whether this is economic data, and what type
        """

        prompt = f"""You are a data ontology expert. Please deeply analyze the fundamental characteristics of this data.

## Data Overview
- Shape: {data_profile['shape'][0]:,} rows x {data_profile['shape'][1]} columns
- Memory usage: {data_profile['memory_mb']:.2f} MB

## Field Details
"""
        for col in data_profile['columns'][:15]:  # first 15 fields
            prompt += f"\n- **{col['name']}** ({col['type']}, {col['dtype']})"
            prompt += f"\n  - Unique values: {col['unique_count']:,}, Missing rate: {col['null_pct']:.1f}%"
            if col.get('min') is not None:
                prompt += f"\n  - Range: [{col['min']:.2f}, {col['max']:.2f}], Mean: {col['mean']:.2f}" if col['mean'] else ""
            if col.get('sample_values'):
                prompt += f"\n  - Sample values: {col['sample_values'][:3]}"

        if data_profile.get('potential_time_cols'):
            prompt += f"\n\n## Potential Time Columns\n{data_profile['potential_time_cols']}"
        if data_profile.get('potential_price_cols'):
            prompt += f"\n\n## Potential Price/Currency Columns\n{data_profile['potential_price_cols']}"
        if data_profile.get('potential_id_cols'):
            prompt += f"\n\n## Potential ID/Entity Columns\n{data_profile['potential_id_cols']}"

        prompt += """

---

## Please reason deeply and answer the following questions:

### 1. Entity Type Identification
What type of existence does this data record? Choose from the following and explain your reasoning:
- **Transaction/Event**: Discrete occurrences, has timestamp, non-repeatable (e.g., orders, clicks, earthquakes)
- **State/Stock**: Point-in-time snapshot, cumulative (e.g., inventory, population, balance)
- **Relationship/Network**: Connections between entities (e.g., social relations, trade flows, citations)
- **Feature/Attribute**: Static attribute descriptions (e.g., user profiles, product specs, geological features)
- **Time-series/Trajectory**: Continuous measurements with serial dependency (e.g., stock prices, temperature, sensors)

**Your judgment**:
**Reasoning**:

### 2. Data Generation Mechanism
How was the data generated? What biases does this imply?
- **Observational**: Passively recorded — potential selection bias, survivorship bias
- **Experimental**: Has intervention/control — causal inference possible
- **Simulated**: Rule-based generation — conclusions limited to simulation scenario
- **Measured**: Instrument-collected — measurement error present
- **Reported**: Manually filled — social desirability bias

**Your judgment**:
**Reasoning**:

### 3. Core Dimension Identification
What key dimensions can be used for grouping, comparison, or tracing?
- Time dimension?
- Geographic/spatial dimension?
- Categorical/hierarchical dimension?
- Entity/relational dimension?

**List core dimensions and descriptions**:

### 4. Economic Type Determination
Does this data involve economic behavior?
- Are there price, cost, revenue, profit, or transaction fields?
- Does it describe buyer-seller relationships or supply-demand dynamics?

**If economic data**, preliminary type:
- Retail economy / Subscription economy / Rental economy / Attention economy
- Commission economy / Labor market / Financial time series / Other

**If non-economic data**, what domain:
- Earth science / Biomedicine / Social science / Engineering / Other

**Your judgment**:
**Reasoning**:

### 5. Keyword Tags
Provide 3-5 keyword tags summarizing this data:

### 6. Suitable Questions
Based on data characteristics, what type of questions is this data best suited to answer?
(descriptive/diagnostic/predictive/prescriptive/causal)
What specific questions can it answer?

### 7. Data Limitations
What are the obvious limitations of this data in terms of sample size, time span,
field completeness, and potential biases?
What questions cannot be answered?

### 8. Confidence Assessment
How confident are you in the above judgments? (high/medium/low)

---

Please output in structured JSON format:
{
  "entity_type": "",
  "entity_type_reason": "",
  "generation_mechanism": "",
  "mechanism_reason": "",
  "core_dimensions": [{"dimension": "", "description": ""}],
  "is_economic": true/false,
  "economic_type": "",
  "domain_type": "",
  "keywords": [],
  "recommended_questions": [],
  "limitations": [],
  "confidence": ""
}
"""

        # In actual use, call LLM:
        # result = call_llm(prompt)
        # return parse_ontology_result(result)

        return prompt  # Return the prompt for the caller to use

    def plan_analysis(self, ontology: OntologyResult, user_intent: str,
                     data_sample: str, column_details: List[str]) -> AnalysisPlan:
        """
        Step 2: Analysis planning

        LLM reasoning to determine:
        - What problem type the user wants to answer
        - What domain-recognized analysis methods to use
        - Specific step-by-step analysis path
        """

        prompt = f"""You are a cross-domain data analysis expert. Based on the data ontology and user intent,
plan a complete analysis approach.

---

## Part 1: Data Ontology (Identified)

**Entity type**: {ontology.entity_type}
**Reasoning**: {ontology.entity_type_reason}

**Generation mechanism**: {ontology.generation_mechanism}
**Reasoning**: {ontology.mechanism_reason}

**Core dimensions**:
"""
        for dim in ontology.core_dimensions:
            prompt += f"\n- {dim['dimension']}: {dim['description']}"

        prompt += f"""

**Economic type**: {"Yes - " + ontology.economic_type if ontology.is_economic else "No - " + ontology.domain_type}

**Keywords**: {', '.join(ontology.keywords)}

**Data limitations**:
"""
        for lim in ontology.limitations:
            prompt += f"\n- {lim}"

        prompt += f"""

---

## Part 2: User Intent

**User's words**: "{user_intent}"

Please analyze:
1. What practical problem does the user want to solve?
2. What is the user's role? (business decision-maker / researcher / student / other)
3. What is the expected output? (insight report / predictive model / visualization / other)

---

## Part 3: Data Sample (First 10 rows)

```
{data_sample}
```

---

## Part 4: Field Details

"""
        for detail in column_details[:20]:
            prompt += f"\n- {detail}"

        prompt += """

---

## Please reason deeply and output an analysis plan:

### Step 1: Problem Type Determination

What type is the user's question? Choose from the following and explain in detail:

**Descriptive (What is it?)**
- Keywords: current state, distribution, characteristics, trends, statistics
- Example: What is the average salary? How are sales distributed across regions?
- Data requirement: Representative sample

**Diagnostic (Why?)**
- Keywords: reason, why, attribution, difference, explanation
- Example: Why did conversion rate drop? Why does region A outperform region B?
- Data requirement: Multi-dimensional decomposition, time series, or group comparison

**Predictive (What will happen?)**
- Keywords: forecast, trend, future, warning, capacity
- Example: What will next quarter's sales be? When will we need to scale?
- Data requirement: Time series data or clear feature-target relationship

**Prescriptive (What should be done?)**
- Keywords: optimal, should, strategy, resource allocation, recommendation
- Example: What is the optimal pricing strategy? How to allocate resources?
- Data requirement: Clear action-outcome mapping with constraints

**Causal (Is there an effect?)**
- Keywords: causal, impact, effect, mechanism, validate
- Example: Did the promotion increase sales? Is the new drug effective?
- Data requirement: Time variation or control group; confounders can be excluded

**Your determination**:
**Reasoning** (cite keywords from user's question):
**Data support level** (high/medium/low):

---

### Step 2: Domain Analysis Method Matching

Based on data type and problem type, what are the domain-recognized analysis methods?

If **economic data**, select the appropriate framework:
- **Retail economy** → Value chain analysis, ABC-XYZ portfolio, RFM customer segmentation
- **Subscription economy** → LTV/Cohort analysis, retention curves, revenue waterfall
- **Attention/Conversion economy** → Funnel analysis, AARRR, session sequence mining
- **Commission/Platform economy** → Two-sided network effects, unit economics, matching efficiency
- **Rental/Asset economy** → Asset utilization, revenue management, asset lifecycle
- **Labor market** → Skill premium analysis, experience elasticity, supply-demand gap
- **Financial time series** → Technical analysis, volatility modeling, portfolio optimization

If **non-economic data**, select the appropriate framework:
- **Scientific measurement** → Uncertainty analysis, hypothesis testing, experimental design
- **Social network** → Centrality analysis, community detection, diffusion models
- **Spatiotemporal** → Spatial autocorrelation, hotspot analysis, geographically weighted regression
- **Text/NLP** → Topic modeling, sentiment analysis, semantic network
- **Biomedicine** → Survival analysis, differential expression, pathway enrichment

**Recommended frameworks** (1-3, in priority order):
- Framework 1: Name + reason + specific application
- Framework 2: Name + reason + specific application
- Framework 3: Name + reason + specific application (if needed)

**Why not other frameworks**:

---

### Step 3: Analysis Path Design

Design specific analysis steps. Each step must have:
- Step name
- Purpose (what sub-question to solve)
- Method (specific technique/algorithm)
- Input (what data fields are needed)
- Output (what results/charts/values to produce)
- Code logic (pseudocode or key operations)

**Opening analysis** (basic analysis for all data):
Step 1:
Step 2:
Step 3:

**Core analysis** (in-depth analysis targeting the user's question):
Step 4:
Step 5:
Step 6:

**Validation analysis** (robustness checks):
Step 7:
Step 8:

**Visualization plan**:
- Chart 1: type + purpose + key findings
- Chart 2: type + purpose + key findings

---

### Step 4: Script Planning

Plan the Python analysis scripts to generate:

**Script 1: xxx.py**
- Function:
- Dependencies:
- Input:
- Output:
- Key functions:

**Script 2: xxx.py** (if needed)
...

**Dependencies between scripts**:

---

### Step 5: Expected Output and Deliverables

**What the user will see**:
- Numerical conclusions (specific metrics):
- Visualizations (types and insights):
- Written report (structure and key points):

**Prerequisites/data requirements**:
- What conditions must be met for execution?
- If conditions are not met, what are the alternatives?

**Potential risks/considerations**:
- Under what circumstances might conclusions be unreliable?
- What should users be aware of when using the conclusions?

---

Please output in structured JSON format:
{
  "question_type": "",
  "question_type_reason": "",
  "frameworks": [{"name": "", "reason": "", "application": ""}],
  "analysis_steps": [
    {
      "step_number": 1,
      "name": "",
      "purpose": "",
      "method": "",
      "input_fields": [],
      "output": "",
      "code_logic": ""
    }
  ],
  "scripts": [{"filename": "", "function": "", "dependencies": []}],
  "expected_outputs": [],
  "prerequisites": [],
  "risks": []
}
"""

        return prompt

    def generate_script(self, analysis_plan: AnalysisPlan, ontology: OntologyResult,
                       file_path: str) -> str:
        """
        Step 3: Generate analysis script
        """

        steps_description = "\n\n".join([
            f"Step {s['step_number']}: {s['name']}\n"
            f"Purpose: {s['purpose']}\n"
            f"Method: {s['method']}\n"
            f"Input fields: {', '.join(s['input_fields'])}\n"
            f"Output: {s['output']}\n"
            f"Code logic: {s['code_logic']}"
            for s in analysis_plan.analysis_steps
        ])

        prompt = f"""You are a Python data analysis expert. Please generate a complete, executable analysis script.

## Analysis Plan

**Problem type**: {analysis_plan.question_type}

**Recommended frameworks**:
"""
        for fw in analysis_plan.frameworks:
            prompt += f"\n- {fw['name']}: {fw['reason']}"

        prompt += f"""

## Analysis Steps

{steps_description}

## Data Information

**File path**: {file_path}

**Data ontology**:
- Entity type: {ontology.entity_type}
- Economic/domain type: {ontology.economic_type if ontology.is_economic else ontology.domain_type}

---

## Generation Requirements

Please generate a complete Python script with the following requirements:

1. **Standard dependencies**
   ```python
   import sys
   from pathlib import Path
   SKILL_DIR = Path(__file__).parent
   sys.path.insert(0, str(SKILL_DIR / 'layers'))
   from data_loader import DataLoader
   from data_validator import DataValidator

   import pandas as pd
   import numpy as np
   import matplotlib.pyplot as plt
   import seaborn as sns
   ```

2. **Error handling**
   - All file operations and calculations must have try-except
   - Check for null values and outliers
   - Provide user-friendly error messages

3. **Modular design**
   - One function per analysis step
   - Functions have clear docstrings
   - Main orchestration function runs the full workflow

4. **Save results**
   - Charts saved to ./output/ directory
   - Numerical results saved to JSON
   - Generate Markdown report

5. **Complete comments**
   - Each key step explains its purpose
   - Complex logic includes explanations
   - Reference sources for analysis frameworks

---

Please output the complete Python script code directly, using the following structure:

```python
#!/usr/bin/env python3
\"\"\"
Analysis script: [name based on analysis purpose]
Data file: {file_path}

Analysis framework: {', '.join([f['name'] for f in analysis_plan.frameworks])}
Problem type: {analysis_plan.question_type}

Description:
[detailed description of script function]
\"\"\"

# Imports and configuration
...

# Global configuration
OUTPUT_DIR = "./output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Function definitions
...

# Main function
if __name__ == "__main__":
    main()
```
"""

        return prompt

    def generate_report(self, ontology: OntologyResult, analysis_plan: AnalysisPlan,
                       results: Dict[str, Any]) -> str:
        """
        Step 4: Generate analysis report
        """

        prompt = f"""You are an expert in writing data analysis reports. Based on the analysis results,
generate a professional data interpretation report.

## Data Ontology

**Entity type**: {ontology.entity_type}
**Generation mechanism**: {ontology.generation_mechanism}
**Economic/domain type**: {ontology.economic_type if ontology.is_economic else ontology.domain_type}

**Core dimensions**:
"""
        for dim in ontology.core_dimensions:
            prompt += f"\n- {dim['dimension']}: {dim['description']}"

        prompt += f"""

**Keywords**: {', '.join(ontology.keywords)}

**Data limitations**:
"""
        for lim in ontology.limitations:
            prompt += f"\n- {lim}"

        prompt += f"""

## Analysis Plan

**Problem type**: {analysis_plan.question_type}

**Frameworks used**:
"""
        for fw in analysis_plan.frameworks:
            prompt += f"\n- **{fw['name']}**: {fw['reason']}"

        prompt += f"""

## Analysis Results (Key Findings)

```json
{json.dumps(results, indent=2, ensure_ascii=False, default=str)[:2000]}
```

---

## Report Generation Requirements

Please generate a professional Markdown analysis report with the following sections:

### 1. Executive Summary
- 3-5 core findings, one sentence each
- 1 overall conclusion
- Key numbers (in **bold**)

### 2. Data Profile
- Data source and scale
- Entity type description
- Core dimensions introduction
- Quality assessment

### 3. Methodology
- Why was this analysis framework chosen?
- What specific techniques were used?
- What are the limitations of the analysis?

### 4. Key Findings
- Organized by theme, one subsection per theme
- Every finding must be supported by specific numbers
- Include descriptions of visualization charts (charts saved to output directory)
- Distinguish "data shows" (fact) from "may imply" (inference)

### 5. Conclusions & Recommendations
- Answer the user's original question
- Specific data-driven recommendations
- Next steps (if needed)

### 6. Limitations
- What questions can't the data answer?
- What to be aware of when using the conclusions?
- Under what circumstances might conclusions not apply?

---

## Writing Style Requirements

1. **Professional yet accessible**: avoid excessive academic language, but maintain professionalism
2. **Let numbers speak**: every conclusion must have specific numerical support
3. **Honest boundaries**: clearly distinguish "certain" from "speculative"
4. **Action-oriented**: conclusions should guide real decisions
5. **Format standards**: use Markdown headings, lists, tables, code blocks

Please output the complete Markdown report directly.
"""

        return prompt


def main():
    """Test entry point"""
    analyzer = LLMAnalyzer()

    # Sample data profile
    sample_profile = {
        'shape': (10000, 10),
        'memory_mb': 2.5,
        'columns': [
            {'name': 'timestamp', 'type': 'datetime', 'dtype': 'datetime64[ns]',
             'unique_count': 10000, 'null_pct': 0, 'min': '2020-01-01', 'max': '2020-12-31'},
            {'name': 'user_id', 'type': 'categorical', 'dtype': 'int64',
             'unique_count': 5000, 'null_pct': 0, 'sample_values': [1, 2, 3]},
            {'name': 'product_id', 'type': 'categorical', 'dtype': 'int64',
             'unique_count': 100, 'null_pct': 0, 'sample_values': [101, 102, 103]},
            {'name': 'category', 'type': 'categorical', 'dtype': 'object',
             'unique_count': 10, 'null_pct': 0, 'sample_values': ['A', 'B', 'C']},
            {'name': 'price', 'type': 'numeric', 'dtype': 'float64',
             'unique_count': 500, 'null_pct': 0, 'min': 10.0, 'max': 1000.0, 'mean': 150.0},
            {'name': 'quantity', 'type': 'numeric', 'dtype': 'int64',
             'unique_count': 50, 'null_pct': 0, 'min': 1, 'max': 100, 'mean': 3.5},
            {'name': 'total_amount', 'type': 'numeric', 'dtype': 'float64',
             'unique_count': 2000, 'null_pct': 0, 'min': 10.0, 'max': 50000.0, 'mean': 500.0},
        ],
        'potential_time_cols': ['timestamp'],
        'potential_price_cols': ['price', 'total_amount'],
        'potential_id_cols': ['user_id', 'product_id']
    }

    ontology_prompt = analyzer.identify_ontology(sample_profile)
    print("=" * 80)
    print("Data Ontology Identification Prompt (first 2000 chars):")
    print("=" * 80)
    print(ontology_prompt[:2000])


if __name__ == '__main__':
    main()
