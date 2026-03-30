---
name: City of Edmonton Open Data
description: "Access 2,179+ datasets from the City of Edmonton open data portal. Search, fetch, and analyze city data on transit, traffic, environment, census, and more. The skills contain API information licensed under the Open Government Licence – City of Edmonton."
permissions: Bash
triggers:
  - edmonton open data
  - city of edmonton data
  - edmonton dataset
  - data.edmonton.ca
  - edmonton transit data
  - edmonton environment data
  - edmonton census data
---

# City of Edmonton Open Data

Access and analyze 2,179+ open datasets from the City of Edmonton via the Socrata SODA API. Data covers transit, traffic, census, environment, city administration, and more.

**Portal:** https://data.edmonton.ca
**Licence:** Open Government Licence – City of Edmonton

## Quick Start

```bash
# Search for datasets
python3 scripts/edmonton_data.py search "traffic"

# List datasets by category
python3 scripts/edmonton_data.py list --category "Transit"

# View dataset info
python3 scripts/edmonton_data.py info 24uj-dj8v

# Fetch data (default JSON, 10 rows)
python3 scripts/edmonton_data.py fetch 24uj-dj8v --limit 5

# Fetch with filters
python3 scripts/edmonton_data.py fetch 24uj-dj8v --where "year='2025'" --select "job_category,address,construction_value"

# Export to CSV
python3 scripts/edmonton_data.py fetch 24uj-dj8v --limit 100 --csv > permits.csv

# List all categories
python3 scripts/edmonton_data.py categories

# View popular datasets
python3 scripts/edmonton_data.py popular

# GeoJSON export (if dataset has location columns)
python3 scripts/edmonton_data.py geojson h4ti-be2n --limit 50
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `search <query>` | Search datasets by keyword |
| `list [--category <cat>]` | List datasets, optionally filter by category |
| `info <dataset-id>` | Show dataset metadata (columns, types, row count) |
| `fetch <dataset-id>` | Download data rows (opts: `--limit`, `--where`, `--select`, `--order`, `--csv`, `--json`) |
| `categories` | List all categories with dataset counts |
| `popular` | Show most-viewed datasets |
| `geojson <dataset-id>` | Export geocoded data as GeoJSON |

## Query Parameters

The `fetch` command supports Socrata SODA query parameters:

- `--limit N` — Max rows to return (default: 10)
- `--where "condition"` — SQL-like filter (e.g., `"construction_value > 100000"`)
- `--select "col1,col2"` — Choose specific columns
- `--order "col DESC"` — Sort results
- `--offset N` — Skip N rows (pagination)
- `--csv` — Output as CSV instead of JSON

## Dataset IDs

Dataset IDs are 9-character alphanumeric codes (e.g., `24uj-dj8v`). Find them via `search` or `list`, or from the dataset URL: `data.edmonton.ca/dataset/{id}`.

## Data Sources

All data is sourced from the City of Edmonton's Open Data Portal (data.edmonton.ca) and is provided under the Open Government Licence – City of Edmonton. See [references/datasets.md](references/datasets.md) for a curated list of popular datasets.
