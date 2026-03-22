# Universal Data Analyst

**Slug**: `universal-data-analyst`

MIT-0 License - See LICENSE file for details.

## Overview

Universal Data Analysis Expert. Performs open-ended analysis planning based on data ontology — no hardcoded keyword rules. Every run uses an LLM to reason about data type, problem type, and analysis method.

## Workflow

1. Load data with data_loader
2. Use the quick-reference card for data ontology identification ("what existence is this?")
3. Run data quality diagnostics with data_validator (mandatory — results go into the report)
4. Combine user intent with LLM to select domain-recognized analysis methods
5. Generate analysis script
6. Execute analysis script
7. Generate comprehensive report (HTML + MD + charts)

Supports both economic and non-economic data; automatically adapts the analysis framework.

## Triggers

- **File Upload**: Triggered when the user uploads a CSV/Excel/Parquet or other data file
- **Keywords**: Data analysis requests
  - "analyze.*data"
  - "help me look at this data"
  - "how to analyze.*data"
  - "explore.*dataset"
  - "interpret.*data"

## Capabilities

- Data loading (CSV, Excel, Parquet, JSON, SQL)
- Data profiling
- Data validation (missing values, outliers, duplicates)
- Analysis planning (descriptive, diagnostic, predictive, prescriptive, causal)
- Script generation
- Statistical analysis
- Multi-file join
- Autonomous mode (no LLM required)
- Quality-driven strategy adjustment

## Usage

### Command Line

```bash
python orchestrator.py data.csv --intent "Analyze sales trends"
```

### Python API

```python
from orchestrator import DataAnalysisOrchestrator

orchestrator = DataAnalysisOrchestrator()
results = orchestrator.run_full_analysis(
    file_path="data.csv",
    user_intent="Analyze sales trends"
)
```

## Files

- `orchestrator.py` - Main workflow orchestrator
- `main.py` - Core analysis engine (V2 optimized)
- `llm_analyzer.py` - LLM-based reasoning module
- `report_generator.py` - HTML/Markdown report generation
- `layers/data_loader.py` - Multi-format data loading
- `layers/data_validator.py` - Data quality validation

## Configuration

- `auto_validate`: true - Data quality validation is mandatory
- `step_by_step`: true - Generate step-by-step analysis scripts
- `output_format`: both - Generate both HTML and Markdown reports
- `autonomous_mode`: true - Support autonomous mode without external LLM

## Version

2.0.0

## Author

Claude
