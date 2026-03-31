---
name: academic-talon
description: Use this skill when the user wants to search for academic papers, analyze PDF files, extract metadata, or save papers to Zotero.
metadata: {
  "openclaw": {
    "requires": {
      "bins": ["python"],
      "env": ["ZOTERO_API_KEY", "ZOTERO_LIBRARY_ID"],
      "config": []
    },
    "install": [
      {
        "id": "pip-install-deps",
        "kind": "pip",
        "package": "-r requirements.txt",
        "label": "Install Python dependencies (requires Python 3)"
      }
    ],
    "primaryEnv": "ZOTERO_API_KEY",
    "emoji": "🎓"
  }
}
---

# Instructions

You are an academic research assistant.

Use this skill to:
- Search for academic papers
- Download and analyze PDF files
- Extract structured metadata (BibTeX or full text)
- Archive papers into Zotero

## When to use

Trigger this skill if the user:
- asks to find or search academic papers
- provides a PDF and wants analysis or metadata extraction
- wants to save or organize papers in Zotero
- asks for BibTeX or citation generation

## Actions

You MUST choose the correct action:

- `search` → find papers
- `download` → download PDF
- `analyze` → extract metadata or full text
- `archive` → save to Zotero

## Rules

- Always select the correct action based on user intent
- Prefer `search` before `download` if no URL is provided
- Use `analyze` to extract BibTeX before archiving
- Avoid duplicate archiving
- Return structured JSON results only

# Overview (Human Readable Documentation)

This skill provides a comprehensive solution for academic paper research and management. It allows users to search for papers across multiple engines, analyze PDF files to extract metadata, and archive papers to Zotero for easy reference.

## Features

1. **Multi-engine paper search**
   - Semantic Scholar
   - arXiv
   - Google Scholar (via SerpAPI)
   - Tavily
2. **PDF analysis**
   - Header analysis (returns BibTeX format)
   - Full text analysis (returns XML format)
   - Uses GROBID API for parsing
3. **Zotero archiving**
   - Archives papers to Zotero library
   - Adds PDF URL as link
   - Avoids duplicate entries
   - Adds items to "openclaw" collection

## Quick Reference

| Situation               | Action                                                            |
| ----------------------- | ----------------------------------------------------------------- |
| Search for papers       | Use `search` action with query parameter                          |
| Analyze PDF header      | Use `analyze` action with pdf\_path and analysis\_type="header"   |
| Analyze PDF full text   | Use `analyze` action with pdf\_path and analysis\_type="fulltext" |
| Archive paper to Zotero | Use `archive` action with paper\_info parameter                   |

## OpenClaw Setup

### Installation

Via ClawdHub (recommended):

```bash
clawdhub install academic-talon
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the skill directory with the following variables:

```
# Zotero API credentials
ZOTERO_API_KEY=your_zotero_api_key
ZOTERO_LIBRARY_ID=your_zotero_library_id
ZOTERO_LIBRARY_TYPE=user # or group

# Optional API keys for additional search engines
SEMANTIC_SCHOLAR_API_KEY=your_semantic_scholar_api_key # Optional
SERPAPI_KEY=your_serpapi_key # For Google Scholar
TAVILY_API_KEY=your_tavily_api_key # For Tavily

# GROBID API URL (default: http://localhost:8070/api)
GROBID_API_URL=http://localhost:8070/api
```

### Required Services

- **GROBID server** - Follow the instructions on the [GROBID GitHub page](https://github.com/kermitt2/grobid) to start the server.

## Usage

### Search Papers

```python
from skill import skill

# Search for papers on "hallucination"
result = skill.run({
    "action": "search",
    "query": "hallucination",
    "limit": 5,
    "source": "all"
})

print(result)

# Search papers with custom engine weights
    result = skill.run({
        "action": "search",
        "query": "hallucination in AI",
        "limit": 10,
        "source": "all",
        "engine_weights": {
            "arxiv": 5,
            "google_scholar": 3,
            "semantic_scholar": 1,
            "tavily": 1
        }
    })

print(result)
```

### Download PDF

```python
from skill import skill

# Download PDF from URL with custom filename
result = skill.run({
    "action": "download",
    "url": "https://example.com/paper.pdf",
    "filename": "example_paper.pdf"
})

print(result)

# Download PDF with custom save directory
result = skill.run({
    "action": "download",
    "url": "https://example.com/paper.pdf",
    "save_dir": "/path/to/pdf/library"
})

print(result)

# Download PDF with paper info for citation key generation
result = skill.run({
    "action": "download",
    "url": "https://example.com/paper.pdf",
    "paper_info": {
        "title": "Paper Title",
        "authors": ["John Doe", "Jane Smith"],
        "year": "2024"
    }
})

print(result)
```

### Analyze PDF

```python
from skill import skill

# Analyze PDF header from local path
result = skill.run({
    "action": "analyze",
    "pdf_input": "/path/to/paper.pdf",
    "analysis_type": "header"
})

print(result)

# Analyze PDF full text from URL
result = skill.run({
    "action": "analyze",
    "pdf_input": "https://example.com/paper.pdf",
    "analysis_type": "fulltext"
})

print(result)
```

### Archive to Zotero

```python
from skill import skill

# Archive paper to Zotero
result = skill.run({
    "action": "archive",
    "paper_info": {
        "title": "Paper Title",
        "authors": ["Author 1", "Author 2"],
        "year": "2023",
        "abstract": "Paper abstract",
        "url": "https://example.com/paper",
        "pdf_url": "https://example.com/paper.pdf",
        "bibtex": "@article{...}"
    }
})

print(result)
```

## Input Schema

| Parameter       | Type    | Description                                                                      | Required       | Default                                                                 |
| --------------- | ------- | -------------------------------------------------------------------------------- | -------------- | ----------------------------------------------------------------------- |
| action          | string  | Action to perform ("search", "download", "analyze", "archive")                   | Yes            | "search"                                                                |
| query           | string  | Search query (for search action)                                                 | Yes (search)   | ""                                                                      |
| limit           | integer | Number of results to return (for search action)                                  | No             | 10                                                                      |
| source          | string  | Search source ("all", "semantic\_scholar", "arxiv", "google\_scholar", "tavily") | No             | "all"                                                                   |
| engine\_weights | object  | Dictionary of engine weights (for search action)                                 | No             | {"arxiv": 5, "google\_scholar": 3, "semantic\_scholar": 1, "tavily": 1} |
| url             | string  | URL of the PDF file (for download action)                                        | Yes (download) | ""                                                                      |
| filename        | string  | Filename to save the PDF as (for download action)                                | No             | None                                                                    |
| save\_dir       | string  | Directory to save the PDF in (for download action)                               | No             | None                                                                    |
| paper\_info     | object  | Paper information (for download and archive actions)                             | No             | {}                                                                      |
| collection      | string  | Name of the collection to add the paper to (for archive action)                  | No             | "openclaw"                                                              |
| pdf\_input      | string  | Path to local PDF file or URL to PDF (for analyze action)                        | Yes (analyze)  | ""                                                                      |
| analysis\_type  | string  | Type of analysis ("header", "fulltext")                                          | No             | "header"                                                                |

## Output Schema

### Search Action

```json
{
  "success": true,
  "action": "search",
  "query": "hallucination",
  "results": [
    {
      "title": "Paper Title",
      "authors": ["Author 1", "Author 2"],
      "year": "2023",
      "abstract": "Paper abstract",
      "url": "https://example.com/paper",
      "pdf_url": "https://example.com/paper.pdf",
      "source": "semantic_scholar"
    }
  ]
}
```

### Download Action

```json
{
  "success": true,
  "action": "download",
  "url": "https://example.com/paper.pdf",
  "pdf_path": "/path/to/downloaded/paper.pdf"
}
```

### Analyze Action

```json
{
  "success": true,
  "action": "analyze",
  "pdf_input": "/path/to/paper.pdf",
  "analysis_type": "header",
  "result": "@article{...}"
}
```

### Archive Action

```json
{
  "success": true,
  "action": "archive",
  "result": {
    "success": true,
    "item_id": "ABC123",
    "added_to_collection": true
  }
}
```

## Error Handling

The skill returns error messages in the following format:

```json
{
  "success": false,
  "error": "Error message"
}
```

Common errors include:

- Missing required parameters
- API key not configured
- GROBID server not accessible
- Zotero API errors

## Dependencies

- **Python 3.6+**
- **Required packages**:
  - requests
  - python-dotenv
  - pyzotero
  - flask

## Examples

### Example 1: Search for papers

```python
from skill import skill

# Search for papers on "artificial intelligence"
result = skill.run({
    "action": "search",
    "query": "artificial intelligence",
    "limit": 3,
    "source": "arxiv"
})

# Print results
if result["success"]:
    for i, paper in enumerate(result["results"]):
        print(f"{i+1}. {paper['title']}")
        print(f"Authors: {', '.join(paper['authors'])}")
        print(f"Year: {paper['year']}")
        print(f"URL: {paper['url']}")
        print(f"PDF URL: {paper['pdf_url']}")
        print()
else:
    print(f"Error: {result['error']}")
```

### Example 2: Analyze PDF and archive to Zotero

```python
from skill import skill
import os

# Path to PDF file
pdf_path = os.path.join(os.path.dirname(__file__), "papers", "example.pdf")

# Analyze PDF header
analyze_result = skill.run({
    "action": "analyze",
    "pdf_input": pdf_path,
    "analysis_type": "header"
})

if analyze_result["success"]:
    # Archive to Zotero
    paper_info = {
        "title": "Example Paper",
        "authors": ["John Doe", "Jane Smith"],
        "year": "2023",
        "abstract": "This is an example paper",
        "url": "https://example.com/paper",
        "pdf_url": "https://example.com/paper.pdf",
        "bibtex": analyze_result["result"]
    }
    
    archive_result = skill.run({
        "action": "archive",
        "paper_info": paper_info
    })
    
    if archive_result["success"]:
        print("Paper archived successfully!")
        print(f"Item ID: {archive_result['result']['item_id']}")
    else:
        print(f"Error archiving paper: {archive_result['error']}")
else:
    print(f"Error analyzing PDF: {analyze_result['error']}")
```

## Troubleshooting

### Common Issues

1. **GROBID server not accessible**
   - Make sure GROBID server is running
   - Check the GROBID\_API\_URL in .env file
2. **Zotero API errors**
   - Verify ZOTERO\_API\_KEY and ZOTERO\_LIBRARY\_ID in .env file
   - Check Zotero API rate limits
3. **Search engines returning empty results**
   - For Google Scholar: Ensure SERPAPI\_KEY is configured
   - For Tavily: Ensure TAVILY\_API\_KEY is configured
   - For Semantic Scholar: Consider adding SEMANTIC\_SCHOLAR\_API\_KEY for higher rate limits
4. **PDF analysis failing**
   - Ensure PDF file is accessible
   - Check GROBID server status

### Logs

The skill logs errors to the console. For detailed debugging, check the console output.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request to [paper reader github](https://github.com/bigdogaaa/academic-talon).

## License

This project is licensed under the MIT License.
