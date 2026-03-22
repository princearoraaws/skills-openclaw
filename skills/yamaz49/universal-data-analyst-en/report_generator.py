#!/usr/bin/env python3
"""
Report Generator - Generate unified comprehensive analysis reports

Output:
- HTML report (integrates all content with embedded charts)
- Markdown report (text content only)
- Charts directory (charts saved separately)
"""

import os
import json
import base64
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import re


class ReportGenerator:
    """Unified report generator"""

    def __init__(self, session_dir: str):
        self.session_dir = Path(session_dir)
        self.output_dir = self.session_dir / "output"
        self.output_dir.mkdir(exist_ok=True)
        self.charts_dir = self.output_dir / "charts"
        self.charts_dir.mkdir(exist_ok=True)

    def generate_all_reports(self,
                            data_info: Dict,
                            validation_report: Dict,
                            ontology: Dict,
                            analysis_plan: Dict,
                            analysis_results: Dict,
                            chart_files: List[str] = None) -> Dict[str, str]:
        """
        Generate all report formats

        Returns:
            {
                'html_report': path to HTML file,
                'markdown_report': path to MD file,
                'charts_dir': charts directory
            }
        """
        # Generate HTML report
        html_content = self._generate_html_report(
            data_info, validation_report, ontology,
            analysis_plan, analysis_results, chart_files or []
        )
        html_path = self.output_dir / "analysis_report.html"
        html_path.write_text(html_content, encoding='utf-8')

        # Generate Markdown report
        md_content = self._generate_markdown_report(
            data_info, validation_report, ontology,
            analysis_plan, analysis_results
        )
        md_path = self.output_dir / "analysis_report.md"
        md_path.write_text(md_content, encoding='utf-8')

        return {
            'html_report': str(html_path),
            'markdown_report': str(md_path),
            'charts_dir': str(self.charts_dir)
        }

    def _generate_html_report(self,
                             data_info: Dict,
                             validation_report: Dict,
                             ontology: Dict,
                             analysis_plan: Dict,
                             analysis_results: Dict,
                             chart_files: List[str]) -> str:
        """Generate HTML report"""

        # Embed charts as base64
        charts_html = self._embed_charts(chart_files)

        # Extract key numbers
        key_numbers = self._extract_key_numbers(analysis_results, data_info)

        # Generate report
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Analysis Report - {data_info.get('file_name', 'Unknown')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            line-height: 1.5;
            color: #1a1a1a;
            background: #fff;
            font-size: 12px;
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 30px 40px;
        }}

        /* Header */
        .header {{
            border-bottom: 2px solid #1a1a1a;
            padding-bottom: 15px;
            margin-bottom: 25px;
        }}

        .header h1 {{
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 5px;
        }}

        .header .meta {{
            font-size: 11px;
            color: #666;
        }}

        /* Key metrics cards */
        .key-metrics {{
            display: flex;
            gap: 15px;
            margin: 20px 0;
            flex-wrap: wrap;
        }}

        .metric-card {{
            flex: 1;
            min-width: 140px;
            padding: 12px 15px;
            background: #f8f9fa;
            border-left: 3px solid #333;
        }}

        .metric-card.warning {{
            border-left-color: #c00;
        }}

        .metric-card.success {{
            border-left-color: #27ae60;
        }}

        .metric-value {{
            font-size: 18px;
            font-weight: 600;
            color: #1a1a1a;
        }}

        .metric-label {{
            font-size: 10px;
            color: #666;
            margin-top: 3px;
        }}

        /* Section */
        .section {{
            margin-bottom: 25px;
        }}

        .section-title {{
            font-size: 14px;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 12px;
            padding-bottom: 6px;
            border-bottom: 1px solid #ddd;
        }}

        .section-note {{
            font-size: 10px;
            color: #999;
            margin: -8px 0 12px 0;
            font-style: italic;
        }}

        /* Dimension block */
        .dimension-block {{
            margin-left: 15px;
            margin-bottom: 18px;
        }}

        .dimension-title {{
            font-size: 12px;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }}

        /* Insight item */
        .insight-item {{
            margin-left: 30px;
            margin-bottom: 15px;
            padding-left: 12px;
            border-left: 2px solid #ddd;
        }}

        .insight-item.high {{ border-left-color: #c00; }}
        .insight-item.medium {{ border-left-color: #666; }}
        .insight-item.low {{ border-left-color: #bbb; }}

        .insight-header {{
            display: flex;
            align-items: baseline;
            gap: 8px;
            margin-bottom: 6px;
        }}

        .insight-title {{
            font-size: 12px;
            font-weight: 600;
        }}

        .significance-tag {{
            font-size: 10px;
            font-weight: 600;
        }}

        .tag-high {{ color: #c00; }}
        .tag-medium {{ color: #666; }}
        .tag-low {{ color: #999; }}

        .insight-line {{
            margin-left: 0;
            margin-bottom: 4px;
            font-size: 11px;
            line-height: 1.6;
        }}

        .insight-line .label {{
            color: #666;
            font-size: 10px;
        }}

        .highlight-red {{
            color: #c00;
            font-weight: 600;
        }}

        .highlight-green {{
            color: #27ae60;
            font-weight: 600;
        }}

        /* Field summary */
        .field-summary {{
            margin-left: 15px;
            margin-bottom: 10px;
            font-size: 11px;
        }}

        .field-item {{
            display: inline-block;
            margin-right: 25px;
            margin-bottom: 5px;
        }}

        .field-label {{
            color: #666;
        }}

        .field-value {{
            font-weight: 600;
        }}

        /* Financial-style table */
        .financial-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 11px;
            margin: 8px 0 15px 15px;
            max-width: 600px;
        }}

        .financial-table thead {{
            border-top: 1px solid #1a1a1a;
            border-bottom: 1px solid #1a1a1a;
        }}

        .financial-table th {{
            padding: 6px 8px;
            text-align: left;
            font-weight: 600;
            background: #fafafa;
            font-size: 10px;
        }}

        .financial-table td {{
            padding: 5px 8px;
            border-bottom: 1px solid #eee;
        }}

        .financial-table .num {{
            text-align: right;
            font-family: 'Helvetica Neue', monospace;
        }}

        /* Issue list */
        .issue-list {{
            margin-left: 15px;
            margin-bottom: 12px;
        }}

        .issue-item {{
            margin-bottom: 8px;
            padding: 8px 10px;
            background: #f8f9fa;
            border-left: 2px solid #ddd;
            font-size: 11px;
        }}

        .issue-item.critical {{
            border-left-color: #c00;
            background: #fff5f5;
        }}

        .issue-item.warning {{
            border-left-color: #f39c12;
            background: #fffbf0;
        }}

        .issue-field {{
            font-weight: 600;
            color: #1a1a1a;
        }}

        .issue-count {{
            color: #c00;
            font-weight: 600;
        }}

        /* Chart container */
        .chart-container {{
            margin: 10px 0 15px 30px;
            text-align: center;
        }}

        .chart-container img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #eee;
        }}

        .chart-caption {{
            font-size: 10px;
            color: #666;
            margin-top: 5px;
            font-style: italic;
        }}

        /* Action list */
        .action-list {{
            margin-left: 15px;
            list-style: none;
            counter-reset: action-counter;
        }}

        .action-item {{
            margin-left: 0;
            margin-bottom: 6px;
            padding-left: 20px;
            text-indent: -15px;
            font-size: 11px;
            line-height: 1.5;
        }}

        .action-item::before {{
            counter-increment: action-counter;
            content: counter(action-counter) ". ";
            color: #999;
        }}

        .priority-mark {{
            font-size: 10px;
            font-weight: 600;
            margin-right: 6px;
        }}

        .priority-high {{ color: #c00; }}

        /* Footer */
        .footer {{
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #ddd;
            font-size: 10px;
            color: #999;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{data_info.get('report_title', 'Data Analysis Report')}</h1>
            <div class="meta">
                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} |
                Data source: {data_info.get('file_name', 'Unknown')} |
                AI-assisted data analysis
            </div>
        </div>

        <!-- Key metrics cards -->
        <div class="key-metrics">
            {key_numbers}
        </div>

        <!-- 1. Data Quality Diagnostics -->
        <div class="section">
            <h2 class="section-title">1. Data Quality Diagnostics</h2>
            <div class="section-note">Data quality issues automatically detected by data_validator</div>

            {self._generate_quality_section(validation_report)}
        </div>

        <!-- 2. Data Profile -->
        <div class="section">
            <h2 class="section-title">2. Data Profile</h2>
            <div class="section-note">Ontology identification results: entity type, generation mechanism, core dimensions</div>

            {self._generate_ontology_section(ontology)}
        </div>

        <!-- 3. Analysis Planning -->
        <div class="section">
            <h2 class="section-title">3. Analysis Planning</h2>
            <div class="section-note">Problem type determination, domain framework matching, analysis path design</div>

            {self._generate_planning_section(analysis_plan)}
        </div>

        <!-- 4. Analysis Results -->
        <div class="section">
            <h2 class="section-title">4. Analysis Results</h2>
            <div class="section-note">Findings and insights from executed analysis scripts</div>

            {self._generate_results_section(analysis_results)}

            <!-- Charts -->
            {charts_html}
        </div>

        <!-- 5. Conclusions & Recommendations -->
        <div class="section">
            <h2 class="section-title">5. Conclusions & Recommendations</h2>
            {self._generate_conclusions_section(analysis_results)}
        </div>

        <!-- Footer -->
        <div class="footer">
            Report generated by Universal Data Analyst |
            Data limitations noted in each section
        </div>
    </div>
</body>
</html>"""
        return html

    def _generate_markdown_report(self,
                                 data_info: Dict,
                                 validation_report: Dict,
                                 ontology: Dict,
                                 analysis_plan: Dict,
                                 analysis_results: Dict) -> str:
        """Generate Markdown report (text content only)"""

        md = f"""# {data_info.get('report_title', 'Data Analysis Report')}

> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> Data source: {data_info.get('file_name', 'Unknown')}
> AI-assisted data analysis

---

## 1. Data Quality Diagnostics

### 1.1 Data Scale
- **Original data**: {data_info.get('rows', 0):,} rows x {data_info.get('columns', 0)} columns
- **Quality score**: {validation_report.get('overall_score', 0):.1f}/100

### 1.2 Issues Found

"""

        # Add data quality issues
        issues = validation_report.get('issues', [])
        if issues:
            for issue in issues[:10]:  # Show at most 10 issues
                severity = issue.get('severity', 'info')
                col = issue.get('column', 'entire table')
                desc = issue.get('description', '')
                affected = issue.get('affected_rows', 0)
                pct = issue.get('affected_percent', 0)

                md += f"- **[{severity.upper()}]** `{col}`: {desc}\n"
                md += f"  - Impact: {affected:,} rows ({pct:.1f}%)\n"

                # Add cleaning action note
                action = issue.get('cleaning_action', {})
                if action:
                    md += f"  - Action: {action.get('description', 'Manual review needed')}\n"
                md += "\n"
        else:
            md += "✅ No significant data quality issues detected\n\n"

        # Data profile
        md += """---

## 2. Data Profile

### 2.1 Entity Type
"""
        md += f"- **Determination**: {ontology.get('entity_type', 'Pending identification')}\n"
        md += f"- **Reasoning**: {ontology.get('entity_type_reason', '')}\n\n"

        md += "### 2.2 Generation Mechanism\n"
        md += f"- **Determination**: {ontology.get('generation_mechanism', 'Pending identification')}\n"
        md += f"- **Reasoning**: {ontology.get('mechanism_reason', '')}\n\n"

        md += "### 2.3 Core Dimensions\n"
        for dim in ontology.get('core_dimensions', []):
            md += f"- **{dim.get('dimension', '')}**: {dim.get('description', '')}\n"

        md += f"\n### 2.4 Economic Type\n"
        if ontology.get('is_economic'):
            md += f"- **Type**: {ontology.get('economic_type', 'Unknown')}\n"
        else:
            md += f"- **Domain**: {ontology.get('domain_type', 'Pending identification')}\n"

        md += f"\n### 2.5 Data Limitations\n"
        for lim in ontology.get('limitations', []):
            md += f"- {lim}\n"

        # Analysis planning
        md += """\n---

## 3. Analysis Planning

"""
        md += f"### 3.1 Problem Type\n"
        md += f"- **Determination**: {analysis_plan.get('question_type', 'Pending planning')}\n"
        md += f"- **Reasoning**: {analysis_plan.get('question_type_reason', '')}\n\n"

        md += "### 3.2 Recommended Frameworks\n"
        for fw in analysis_plan.get('frameworks', []):
            md += f"- **{fw.get('name', '')}**: {fw.get('reason', '')}\n"
            md += f"  - Application: {fw.get('application', '')}\n"

        md += "\n### 3.3 Analysis Steps\n"
        for step in analysis_plan.get('analysis_steps', []):
            md += f"\n**Step {step.get('step_number', '?')}: {step.get('name', '')}**\n"
            md += f"- Purpose: {step.get('purpose', '')}\n"
            md += f"- Method: {step.get('method', '')}\n"
            md += f"- Output: {step.get('output', '')}\n"

        # Analysis results
        md += """\n---

## 4. Analysis Results

"""
        # Executive summary
        md += "### 4.1 Executive Summary\n"
        exec_summary = analysis_results.get('executive_summary', [])
        if exec_summary:
            for item in exec_summary:
                md += f"- {item}\n"
        else:
            findings = analysis_results.get('findings', [])
            for finding in findings[:5]:
                md += f"- {finding}\n"

        # Detailed findings
        md += "\n### 4.2 Detailed Findings\n"
        detailed = analysis_results.get('detailed_findings', {})
        for section, content in detailed.items():
            md += f"\n#### {section}\n"
            if isinstance(content, list):
                for item in content:
                    md += f"- {item}\n"
            elif isinstance(content, dict):
                for key, value in content.items():
                    md += f"- **{key}**: {value}\n"
            else:
                md += f"{content}\n"

        # Conclusions and recommendations
        md += """\n---

## 5. Conclusions & Recommendations

"""
        md += "### 5.1 Main Conclusions\n"
        conclusions = analysis_results.get('conclusions', [])
        for conclusion in conclusions:
            md += f"- {conclusion}\n"

        md += "\n### 5.2 Recommendations\n"
        recommendations = analysis_results.get('recommendations', [])
        for i, rec in enumerate(recommendations, 1):
            md += f"{i}. {rec}\n"

        md += "\n### 5.3 Data Limitations\n"
        limitations = analysis_results.get('limitations', [])
        if limitations:
            for lim in limitations:
                md += f"- {lim}\n"
        else:
            md += "- Analysis based on current data snapshot — survivorship bias possible\n"
            md += "- Limited time dimension makes long-term trend analysis difficult\n"

        md += """\n---

> **Notes**:
> - Charts are saved in the `output/charts/` directory
> - Detailed data results are saved in `analysis_results.json`
> - Keep the original data file if you need to re-run the analysis
"""

        return md

    def _embed_charts(self, chart_files: List[str]) -> str:
        """Embed charts into HTML (base64 encoded)"""
        if not chart_files:
            return ""

        html = '<div class="dimension-block">\n'
        html += '<div class="dimension-title">Visualizations</div>\n'

        for chart_path in chart_files:
            chart_file = Path(chart_path)
            if not chart_file.exists():
                continue

            try:
                with open(chart_file, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode('utf-8')

                # Determine MIME type from file extension
                ext = chart_file.suffix.lower()
                mime = 'image/png' if ext == '.png' else 'image/jpeg' if ext in ['.jpg', '.jpeg'] else 'image/svg+xml'

                caption = chart_file.stem.replace('_', ' ').replace('-', ' ').title()

                html += f'''
                <div class="chart-container">
                    <img src="data:{mime};base64,{img_data}" alt="{caption}" />
                    <div class="chart-caption">{caption}</div>
                </div>
                '''
            except Exception as e:
                html += f'<div class="chart-container">Failed to load chart: {e}</div>\n'

        html += '</div>\n'
        return html

    def _extract_key_numbers(self, analysis_results: Dict, data_info: Dict) -> str:
        """Extract key numbers and generate metric cards"""
        cards = []

        # Data scale
        cards.append({
            'value': f"{data_info.get('rows', 0):,}",
            'label': 'Rows',
            'class': ''
        })

        # Extract key metrics from analysis results
        key_metrics = analysis_results.get('key_metrics', {})
        for name, value in list(key_metrics.items())[:3]:
            cards.append({
                'value': str(value),
                'label': name,
                'class': 'warning' if any(w in name.lower() for w in ['churn', 'risk', 'error']) else 'success'
            })

        # If no key metrics, show default
        if len(cards) < 2:
            cards.append({
                'value': f"{data_info.get('columns', 0)}",
                'label': 'Columns',
                'class': ''
            })

        html = ''
        for card in cards:
            html += f'''
            <div class="metric-card {card['class']}">
                <div class="metric-value">{card['value']}</div>
                <div class="metric-label">{card['label']}</div>
            </div>
            '''

        return html

    def _generate_quality_section(self, validation_report: Dict) -> str:
        """Generate data quality section HTML"""
        html = ''

        # Quality score
        score = validation_report.get('overall_score', 0)
        score_class = 'highlight-red' if score < 60 else 'highlight-green' if score >= 80 else ''

        html += f'''
        <div class="dimension-block">
            <div class="dimension-title">Quality Score: <span class="{score_class}">{score:.1f}/100</span></div>
        </div>
        '''

        # Issue list
        issues = validation_report.get('issues', [])
        if issues:
            html += '<div class="dimension-block">\n'
            html += '<div class="dimension-title">Issues Found</div>\n'
            html += '<div class="issue-list">\n'

            for issue in issues[:15]:  # Show at most 15 issues
                severity = issue.get('severity', 'info')
                col = issue.get('column', 'entire table')
                desc = issue.get('description', '')
                affected = issue.get('affected_rows', 0)
                pct = issue.get('affected_percent', 0)

                css_class = 'critical' if severity == 'critical' else 'warning' if severity == 'warning' else ''

                html += f'''
                <div class="issue-item {css_class}">
                    <span class="issue-field">{col}</span>:
                    {desc}<br/>
                    <span style="color:#666;font-size:10px;">
                        Impact: <span class="issue-count">{affected:,}</span> rows ({pct:.1f}%) |
                        Severity: {severity.upper()}
                    </span>
                </div>
                '''

            html += '</div>\n</div>\n'

        # Cleaning recommendations
        cleaning = validation_report.get('cleaning_summary', {})
        if cleaning:
            html += '<div class="dimension-block">\n'
            html += '<div class="dimension-title">Cleaning Recommendations</div>\n'

            deletions = cleaning.get('recommended_deletions', 0)
            fills = cleaning.get('recommended_fills', 0)
            reviews = cleaning.get('recommended_reviews', 0)

            if deletions > 0:
                html += f'<div class="insight-line"><span class="label">Recommended deletions: </span>{deletions:,} rows</div>\n'
            if fills > 0:
                html += f'<div class="insight-line"><span class="label">Recommended fills: </span>{fills:,} missing values</div>\n'
            if reviews > 0:
                html += f'<div class="insight-line"><span class="label">Recommended reviews: </span>{reviews:,} rows</div>\n'

            html += '</div>\n'

        return html

    def _generate_ontology_section(self, ontology: Dict) -> str:
        """Generate data profile section HTML"""
        html = ''

        # Entity type
        html += '<div class="dimension-block">\n'
        html += '<div class="dimension-title">Entity Type</div>\n'
        html += f'<div class="insight-item medium">\n'
        html += f'<div class="insight-title">{ontology.get("entity_type", "Pending identification")}</div>\n'
        html += f'<div class="insight-line">{ontology.get("entity_type_reason", "")}</div>\n'
        html += '</div>\n</div>\n'

        # Generation mechanism
        html += '<div class="dimension-block">\n'
        html += '<div class="dimension-title">Generation Mechanism</div>\n'
        html += f'<div class="insight-item medium">\n'
        html += f'<div class="insight-title">{ontology.get("generation_mechanism", "Pending identification")}</div>\n'
        html += f'<div class="insight-line">{ontology.get("mechanism_reason", "")}</div>\n'
        html += '</div>\n</div>\n'

        # Core dimensions
        html += '<div class="dimension-block">\n'
        html += '<div class="dimension-title">Core Dimensions</div>\n'
        html += '<table class="financial-table">\n'
        html += '<thead><tr><th>Dimension</th><th>Description</th></tr></thead>\n<tbody>\n'
        for dim in ontology.get('core_dimensions', []):
            html += f'<tr><td>{dim.get("dimension", "")}</td><td>{dim.get("description", "")}</td></tr>\n'
        html += '</tbody></table>\n</div>\n'

        # Economic type
        html += '<div class="dimension-block">\n'
        html += '<div class="dimension-title">Economic/Domain Type</div>\n'
        if ontology.get('is_economic'):
            html += f'<div class="insight-item high">\n'
            html += f'<div class="insight-title">{ontology.get("economic_type", "Unknown")}</div>\n'
        else:
            html += f'<div class="insight-item low">\n'
            html += f'<div class="insight-title">{ontology.get("domain_type", "Pending identification")}</div>\n'
        html += '</div>\n</div>\n'

        # Keywords
        html += '<div class="dimension-block">\n'
        html += '<div class="dimension-title">Keyword Tags</div>\n'
        html += '<div class="field-summary">\n'
        for kw in ontology.get('keywords', []):
            html += f'<span class="field-item"><span class="field-value">{kw}</span></span>\n'
        html += '</div>\n</div>\n'

        return html

    def _generate_planning_section(self, analysis_plan: Dict) -> str:
        """Generate analysis planning section HTML"""
        html = ''

        # Problem type
        html += '<div class="dimension-block">\n'
        html += '<div class="dimension-title">Problem Type</div>\n'
        html += f'<div class="insight-item high">\n'
        html += f'<div class="insight-title">{analysis_plan.get("question_type", "Pending planning")}</div>\n'
        html += f'<div class="insight-line">{analysis_plan.get("question_type_reason", "")}</div>\n'
        html += '</div>\n</div>\n'

        # Recommended frameworks
        html += '<div class="dimension-block">\n'
        html += '<div class="dimension-title">Recommended Frameworks</div>\n'
        for fw in analysis_plan.get('frameworks', []):
            html += f'<div class="insight-item medium">\n'
            html += f'<div class="insight-title">{fw.get("name", "")}</div>\n'
            html += f'<div class="insight-line">{fw.get("reason", "")}</div>\n'
            html += f'<div class="insight-line"><span class="label">Application: </span>{fw.get("application", "")}</div>\n'
            html += '</div>\n'
        html += '</div>\n'

        # Analysis steps
        html += '<div class="dimension-block">\n'
        html += '<div class="dimension-title">Analysis Steps</div>\n'
        html += '<table class="financial-table">\n'
        html += '<thead><tr><th>Step</th><th>Name</th><th>Method</th><th>Output</th></tr></thead>\n<tbody>\n'
        for step in analysis_plan.get('analysis_steps', []):
            html += f'<tr>\n'
            html += f'<td>{step.get("step_number", "?")}</td>\n'
            html += f'<td>{step.get("name", "")}</td>\n'
            html += f'<td>{step.get("method", "")}</td>\n'
            html += f'<td>{step.get("output", "")}</td>\n'
            html += '</tr>\n'
        html += '</tbody></table>\n</div>\n'

        # Prerequisites
        if analysis_plan.get('prerequisites'):
            html += '<div class="dimension-block">\n'
            html += '<div class="dimension-title">Prerequisites</div>\n'
            html += '<ul class="action-list">\n'
            for pre in analysis_plan.get('prerequisites', []):
                html += f'<li class="action-item">{pre}</li>\n'
            html += '</ul>\n</div>\n'

        return html

    def _generate_results_section(self, analysis_results: Dict) -> str:
        """Generate analysis results section HTML"""
        html = ''

        # Executive summary
        html += '<div class="dimension-block">\n'
        html += '<div class="dimension-title">Executive Summary</div>\n'

        exec_summary = analysis_results.get('executive_summary', [])
        if exec_summary:
            for item in exec_summary:
                html += f'<div class="insight-item high">\n'
                html += f'<div class="insight-line">{item}</div>\n'
                html += '</div>\n'
        else:
            findings = analysis_results.get('findings', [])
            for finding in findings[:5]:
                html += f'<div class="insight-item medium">\n'
                html += f'<div class="insight-line">{finding}</div>\n'
                html += '</div>\n'

        html += '</div>\n'

        # Detailed findings
        detailed = analysis_results.get('detailed_findings', {})
        if detailed:
            html += '<div class="dimension-block">\n'
            html += '<div class="dimension-title">Detailed Findings</div>\n'

            for section, content in detailed.items():
                html += f'<div class="insight-item medium">\n'
                html += f'<div class="insight-title">{section}</div>\n'

                if isinstance(content, list):
                    for item in content:
                        html += f'<div class="insight-line">• {item}</div>\n'
                elif isinstance(content, dict):
                    html += '<table class="financial-table">\n<tbody>\n'
                    for key, value in content.items():
                        html += f'<tr><td>{key}</td><td class="num">{value}</td></tr>\n'
                    html += '</tbody></table>\n'
                else:
                    html += f'<div class="insight-line">{content}</div>\n'

                html += '</div>\n'

            html += '</div>\n'

        return html

    def _generate_conclusions_section(self, analysis_results: Dict) -> str:
        """Generate conclusions and recommendations section HTML"""
        html = ''

        # Main conclusions
        html += '<div class="dimension-block">\n'
        html += '<div class="dimension-title">Main Conclusions</div>\n'

        conclusions = analysis_results.get('conclusions', [])
        if conclusions:
            for conclusion in conclusions:
                html += f'<div class="insight-item high">\n'
                html += f'<div class="insight-line">{conclusion}</div>\n'
                html += '</div>\n'
        else:
            html += '<div class="insight-line">The above findings are derived from data analysis. Specific conclusions should be interpreted in the context of your actual business scenario.</div>\n'

        html += '</div>\n'

        # Recommendations
        html += '<div class="dimension-block">\n'
        html += '<div class="dimension-title">Recommendations</div>\n'
        html += '<ol class="action-list">\n'

        recommendations = analysis_results.get('recommendations', [])
        for rec in recommendations:
            priority = 'high' if any(w in rec.lower() for w in ['priority', 'urgent', 'critical']) else 'medium'
            html += f'<li class="action-item"><span class="priority-mark priority-{priority}">●</span>{rec}</li>\n'

        html += '</ol>\n</div>\n'

        # Limitations
        html += '<div class="dimension-block">\n'
        html += '<div class="dimension-title">Data Limitations</div>\n'

        limitations = analysis_results.get('limitations', [])
        if limitations:
            for lim in limitations:
                html += f'<div class="insight-item low">\n'
                html += f'<div class="insight-line">{lim}</div>\n'
                html += '</div>\n'
        else:
            html += '<div class="insight-item low">\n'
            html += '<div class="insight-line">Analysis based on current data snapshot — survivorship bias possible; limited time dimension makes long-term trend analysis difficult.</div>\n'
            html += '</div>\n'

        html += '</div>\n'

        return html


def main():
    """Test entry point"""
    import tempfile

    # Create test data
    test_session_dir = tempfile.mkdtemp()
    generator = ReportGenerator(test_session_dir)

    # Mock data
    data_info = {
        'file_name': 'test_data.csv',
        'rows': 10000,
        'columns': 20,
        'report_title': 'Test Analysis Report'
    }

    validation_report = {
        'overall_score': 85.5,
        'issues': [
            {
                'severity': 'warning',
                'column': 'price',
                'description': 'Outliers detected',
                'affected_rows': 50,
                'affected_percent': 0.5,
                'cleaning_action': {'description': 'Manual review recommended'}
            }
        ],
        'cleaning_summary': {
            'recommended_deletions': 0,
            'recommended_fills': 100,
            'recommended_reviews': 50
        }
    }

    ontology = {
        'entity_type': 'Transaction/Event',
        'entity_type_reason': 'Each row is an independent transaction event',
        'generation_mechanism': 'Observational',
        'mechanism_reason': 'System passively records',
        'core_dimensions': [
            {'dimension': 'Time', 'description': 'Transaction timestamp'},
            {'dimension': 'User', 'description': 'Buyer ID'}
        ],
        'is_economic': True,
        'economic_type': 'Retail economy',
        'domain_type': 'Commerce',
        'keywords': ['e-commerce', 'transaction', 'retail'],
        'limitations': ['Missing returns/refunds data']
    }

    analysis_plan = {
        'question_type': 'Diagnostic',
        'question_type_reason': 'User asks why',
        'frameworks': [{'name': 'RFM', 'reason': 'Suitable for customer segmentation', 'application': 'Identify high-value customers'}],
        'analysis_steps': [
            {'step_number': 1, 'name': 'Data cleaning', 'method': 'Missing value handling', 'output': 'Cleaned data'}
        ],
        'prerequisites': ['Complete data']
    }

    analysis_results = {
        'executive_summary': ['Key finding 1', 'Key finding 2'],
        'findings': ['Finding 1', 'Finding 2', 'Finding 3'],
        'conclusions': ['Conclusion 1', 'Conclusion 2'],
        'recommendations': ['Recommendation 1', 'Recommendation 2'],
        'limitations': ['Limitation 1'],
        'key_metrics': {'Churn rate': '26.5%', 'CLTV': '$5,400'}
    }

    result = generator.generate_all_reports(
        data_info, validation_report, ontology,
        analysis_plan, analysis_results, []
    )

    print(f"HTML report: {result['html_report']}")
    print(f"MD report: {result['markdown_report']}")


if __name__ == '__main__':
    main()
