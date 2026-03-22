#!/usr/bin/env python3
"""
Orchestrator - Data Analysis Workflow Orchestrator

Integrates the complete data analysis workflow:
1. Data loading (data_loader)
2. Ontology identification -> LLM reasoning
3. Data quality validation (data_validator) - mandatory, output included in report
4. Analysis planning -> LLM reasoning
5. Script generation -> LLM reasoning
6. Execute analysis
7. Comprehensive report generation -> HTML report + MD report + charts

Features:
- Every decision invokes an LLM — no hardcoded rules
- Supports single-pass full analysis (when user intent is clear)
- Final output is a unified comprehensive report
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime

# Setup paths
SKILL_ROOT = Path(__file__).parent
sys.path.insert(0, str(SKILL_ROOT))
sys.path.insert(0, str(SKILL_ROOT / 'layers'))

from main import UniversalDataAnalyst, DataOntology, AnalysisPlan
from llm_analyzer import LLMAnalyzer, OntologyResult, AnalysisPlan as LLMAnalysisPlan
from report_generator import ReportGenerator


class DataAnalysisOrchestrator:
    """
    Data Analysis Workflow Orchestrator

    Key design:
    - Each reasoning step generates a prompt, invoking an LLM via Claude
    - Data quality diagnostics are mandatory; results integrated into the final report
    - Final output is a unified HTML + MD report
    """

    def __init__(self, output_dir: str = "./analysis_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Initialize components
        self.analyst = UniversalDataAnalyst()
        self.llm_analyzer = LLMAnalyzer()
        self.report_generator = None

        # Session state
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.output_dir / f"session_{self.session_id}"
        self.session_dir.mkdir(exist_ok=True)

        # Initialize report generator
        self.report_generator = ReportGenerator(str(self.session_dir))

        # Cached results
        self.ontology_result: Optional[OntologyResult] = None
        self.analysis_plan: Optional[LLMAnalysisPlan] = None
        self.validation_report_dict: Optional[Dict] = None
        self.data_info: Optional[Dict] = None

    def step1_load_data(self, file_path: str, **kwargs) -> Tuple[bool, str]:
        """
        Step 1: Load data
        Returns: (success, message)
        """
        print("\n" + "="*80)
        print("[Step 1/7] Data Loading")
        print("="*80)

        result = self.analyst.load_data(file_path, **kwargs)

        if result.success:
            msg = f"✅ Load successful: {result.rows:,} rows x {result.columns} columns"
            print(msg)

            # Save basic data info
            self.data_info = {
                "file_path": file_path,
                "file_name": Path(file_path).name,
                "rows": result.rows,
                "columns": result.columns,
                "memory_mb": result.memory_usage_mb,
                "column_names": list(self.analyst.data.columns),
                "report_title": f"{Path(file_path).stem} Data Analysis Report"
            }
            self._save_json("step1_data_info.json", self.data_info)
            return True, msg
        else:
            msg = f"❌ Load failed: {result.errors}"
            print(msg)
            return False, msg

    def step2_identify_ontology(self) -> Tuple[str, str]:
        """
        Step 2: Identify data ontology
        Returns: (prompt, prompt_file_path)
        """
        print("\n" + "="*80)
        print("[Step 2/7] Data Ontology Identification - LLM Reasoning")
        print("="*80)
        print("🤔 Generating data ontology identification prompt...")

        # Generate data profile
        data_profile = self.analyst._generate_data_profile()

        # Generate prompt
        prompt = self.llm_analyzer.identify_ontology(data_profile)

        # Save prompt
        prompt_file = self.session_dir / "step2_ontology_prompt.txt"
        prompt_file.write_text(prompt, encoding='utf-8')

        print(f"💾 Prompt saved: {prompt_file}")
        print("\n📋 Prompt preview (first 1000 chars):")
        print("-" * 80)
        print(prompt[:1000])
        print("...")

        return str(prompt), str(prompt_file)

    def step3_validate_data(self) -> Dict[str, Any]:
        """
        Step 3: Data quality validation (mandatory)
        Returns: validation report dictionary
        """
        print("\n" + "="*80)
        print("[Step 3/7] Data Quality Validation")
        print("="*80)

        report = self.analyst.validate_data()

        # Convert to dictionary
        self.validation_report_dict = report.to_dict()

        # Save validation results
        self._save_json("step3_validation_report.json", self.validation_report_dict)

        # Generate cleaning report
        cleaning_report = report.generate_cleaning_report()
        cleaning_file = self.session_dir / "step3_cleaning_report.txt"
        cleaning_file.write_text(cleaning_report, encoding='utf-8')

        # Display key info
        print(f"\n📊 Quality score: {report.overall_score:.1f}/100")
        print(f"📋 Issues found: {len(report.issues)}")

        warning_count = sum(1 for i in report.issues if str(i.severity) == 'IssueSeverity.WARNING')

        if report.issues:
            critical_count = len(report.issues) - warning_count
            print(f"   - Critical: {critical_count}")
            print(f"   - Warning: {warning_count}")

        summary = report.get_cleaning_summary()
        if summary.get('recommended_deletions', 0) > 0:
            print(f"🗑️  Recommended deletions: {summary['recommended_deletions']:,} rows")
        if summary.get('recommended_fills', 0) > 0:
            print(f"📝 Recommended fills: {summary['recommended_fills']:,} missing values")

        print(f"💾 Validation report saved: {cleaning_file}")

        return self.validation_report_dict

    def step4_plan_analysis(self, user_intent: str) -> Tuple[str, str]:
        """
        Step 4: Plan analysis approach
        Returns: (prompt, prompt_file_path)
        """
        print("\n" + "="*80)
        print("[Step 4/7] Analysis Planning - LLM Reasoning")
        print("="*80)
        print(f"📝 User intent: {user_intent}")

        # Need ontology result; if unavailable, use placeholder
        if self.ontology_result is None:
            print("⚠️ Warning: Ontology not yet identified, using data profile as fallback")
            data_profile = self.analyst._generate_data_profile()
            ontology = self._create_placeholder_ontology(data_profile)
        else:
            ontology = self.ontology_result

        # Get data sample and field details
        df = self.analyst.data
        data_sample = df.head(10).to_string()

        column_details = []
        for col in df.columns:
            dtype = df[col].dtype
            unique = df[col].nunique()
            null_pct = df[col].isnull().sum() / len(df) * 100
            detail = f"{col}: {dtype}, {unique:,} unique values, {null_pct:.1f}% missing"
            if hasattr(df[col], 'min'):
                import pandas as pd
                if pd.api.types.is_numeric_dtype(df[col]):
                    detail += f", range [{df[col].min():.2f}, {df[col].max():.2f}]"
            column_details.append(detail)

        # Generate prompt
        prompt = self.llm_analyzer.plan_analysis(
            ontology=ontology,
            user_intent=user_intent,
            data_sample=data_sample,
            column_details=column_details
        )

        # Save prompt
        prompt_file = self.session_dir / "step4_planning_prompt.txt"
        prompt_file.write_text(prompt, encoding='utf-8')

        print(f"💾 Prompt saved: {prompt_file}")
        print("\n📋 Prompt preview (first 1000 chars):")
        print("-" * 80)
        print(prompt[:1000])
        print("...")

        return str(prompt), str(prompt_file)

    def step5_generate_script(self) -> Tuple[str, str]:
        """
        Step 5: Generate analysis script
        Returns: (prompt, prompt_file_path)
        """
        print("\n" + "="*80)
        print("[Step 5/7] Script Generation - LLM Reasoning")
        print("="*80)

        # Need analysis plan
        if self.analysis_plan is None:
            print("❌ Error: Analysis plan not yet created")
            return "", ""

        # Use identified ontology (or placeholder)
        ontology = self.ontology_result or self._create_placeholder_ontology(
            self.analyst._generate_data_profile()
        )

        file_path = self.analyst.load_result.file_path if self.analyst.load_result else "data.csv"

        # Generate prompt
        prompt = self.llm_analyzer.generate_script(
            analysis_plan=self.analysis_plan,
            ontology=ontology,
            file_path=file_path
        )

        # Save prompt
        prompt_file = self.session_dir / "step5_script_prompt.txt"
        prompt_file.write_text(prompt, encoding='utf-8')

        print(f"💾 Prompt saved: {prompt_file}")

        return str(prompt), str(prompt_file)

    def step6_execute_analysis(self, script_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Step 6: Execute analysis script
        Returns: analysis results dictionary
        """
        print("\n" + "="*80)
        print("[Step 6/7] Execute Analysis")
        print("="*80)

        results = {
            "status": "not_executed",
            "executed": False,
            "script_output": ""
        }

        if script_path and os.path.exists(script_path):
            print(f"🚀 Executing analysis script: {script_path}")
            try:
                result = subprocess.run(
                    [sys.executable, script_path],
                    capture_output=True,
                    text=True,
                    cwd=str(self.session_dir)
                )
                print(result.stdout)
                if result.stderr:
                    print("⚠️ Warning:", result.stderr)

                results["status"] = "success"
                results["executed"] = True
                results["script_output"] = result.stdout

            except Exception as e:
                print(f"❌ Execution failed: {e}")
                results["status"] = f"failed: {e}"
        else:
            print("ℹ️ No script path provided, skipping execution")
            results["status"] = "no_script"

        # Try to read analysis results
        results_file = self.session_dir / "analysis_results.json"
        if results_file.exists():
            try:
                with open(results_file, 'r', encoding='utf-8') as f:
                    analysis_data = json.load(f)
                    results["data"] = analysis_data
                    print(f"📊 Analysis results loaded: {results_file}")
            except Exception as e:
                print(f"⚠️ Failed to read analysis results: {e}")

        return results

    def step7_generate_comprehensive_report(self,
                                            ontology_result: Optional[Dict] = None,
                                            analysis_plan_result: Optional[Dict] = None,
                                            analysis_results: Optional[Dict] = None) -> Dict[str, str]:
        """
        Step 7: Generate comprehensive report (HTML + MD + charts)

        Returns: report file path dictionary
        """
        print("\n" + "="*80)
        print("[Step 7/7] Generate Comprehensive Report")
        print("="*80)

        # Prepare data
        data_info = self.data_info or {
            "file_name": "Unknown",
            "rows": 0,
            "columns": 0,
            "report_title": "Data Analysis Report"
        }

        validation_report = self.validation_report_dict or {
            "overall_score": 0,
            "issues": [],
            "cleaning_summary": {}
        }

        # Use provided ontology result, or read from file, or use placeholder
        ontology = ontology_result or {}
        if not ontology and (self.session_dir / "ontology_result.json").exists():
            try:
                with open(self.session_dir / "ontology_result.json", 'r', encoding='utf-8') as f:
                    ontology = json.load(f)
            except:
                pass

        if not ontology:
            ontology = {
                "entity_type": "Pending identification (run Step 2 with LLM)",
                "entity_type_reason": "Ontology identification not completed",
                "generation_mechanism": "Pending identification",
                "mechanism_reason": "Ontology identification not completed",
                "core_dimensions": [],
                "is_economic": False,
                "economic_type": None,
                "domain_type": "Pending identification",
                "keywords": [],
                "limitations": ["Ontology identification not completed"]
            }

        # Use provided analysis plan, or read from file, or use placeholder
        plan = analysis_plan_result or {}
        if not plan and (self.session_dir / "analysis_plan.json").exists():
            try:
                with open(self.session_dir / "analysis_plan.json", 'r', encoding='utf-8') as f:
                    plan = json.load(f)
            except:
                pass

        if not plan:
            plan = {
                "question_type": "Pending planning",
                "question_type_reason": "Analysis planning not completed",
                "frameworks": [],
                "analysis_steps": [],
                "expected_outputs": [],
                "prerequisites": [],
                "risks": []
            }

        # Use provided analysis results, or read from file
        results = analysis_results or {}
        if not results and (self.session_dir / "analysis_results.json").exists():
            try:
                with open(self.session_dir / "analysis_results.json", 'r', encoding='utf-8') as f:
                    results = json.load(f)
            except:
                pass

        # If still no results, create placeholder
        if not results:
            results = {
                "executive_summary": ["Analysis execution not completed"],
                "findings": [],
                "detailed_findings": {},
                "conclusions": [],
                "recommendations": [],
                "limitations": ["Analysis script not executed — no detailed results available"],
                "key_metrics": {}
            }

        # Find chart files
        chart_files = []
        charts_dir = self.session_dir / "charts"
        if charts_dir.exists():
            chart_files = list(charts_dir.glob("*.png")) + list(charts_dir.glob("*.jpg"))
            chart_files = [str(f) for f in chart_files]

        # Generate reports
        report_paths = self.report_generator.generate_all_reports(
            data_info=data_info,
            validation_report=validation_report,
            ontology=ontology,
            analysis_plan=plan,
            analysis_results=results,
            chart_files=chart_files
        )

        print("\n📄 Reports generated:")
        print(f"  📘 HTML report: {report_paths['html_report']}")
        print(f"  📄 Markdown report: {report_paths['markdown_report']}")
        print(f"  🖼️  Charts directory: {report_paths['charts_dir']}")

        return report_paths

    def run_full_analysis(self, file_path: str, user_intent: str) -> Dict[str, Any]:
        """
        Run the complete analysis workflow (single-pass)

        Suitable when user intent is clear.
        """
        print("\n" + "="*80)
        print("🚀 Starting Universal Data Analysis Workflow")
        print(f"📁 Data file: {file_path}")
        print(f"🎯 Analysis goal: {user_intent}")
        print("="*80)

        results = {
            "session_dir": str(self.session_dir),
            "steps": {},
            "reports": {}
        }

        # Step 1: Load data
        success, msg = self.step1_load_data(file_path)
        results["steps"]["load"] = {"success": success, "message": msg}
        if not success:
            return results

        # Step 2: Ontology identification (generate prompt)
        ontology_prompt, ontology_file = self.step2_identify_ontology()
        results["steps"]["ontology"] = {
            "prompt_file": ontology_file,
            "note": "Send this prompt to an LLM for ontology identification; save the result as ontology_result.json"
        }

        # Step 3: Data validation (mandatory)
        validation_report = self.step3_validate_data()
        results["steps"]["validation"] = {
            "executed": True,
            "score": validation_report.get("overall_score", 0),
            "issues_count": len(validation_report.get("issues", []))
        }

        # Step 4: Analysis planning (generate prompt)
        planning_prompt, planning_file = self.step4_plan_analysis(user_intent)
        results["steps"]["planning"] = {
            "prompt_file": planning_file,
            "note": "Send this prompt to an LLM for analysis planning; save the result as analysis_plan.json"
        }

        # Step 5: Script generation (generate prompt)
        script_prompt, script_file = self.step5_generate_script()
        results["steps"]["script_generation"] = {
            "prompt_file": script_file,
            "note": "Send this prompt to an LLM to generate the analysis script; save as analysis_script.py"
        }

        # Step 6: Execute analysis (if script exists)
        analysis_results = self.step6_execute_analysis()
        results["steps"]["execution"] = analysis_results

        # Step 7: Generate comprehensive report
        report_paths = self.step7_generate_comprehensive_report()
        results["reports"] = report_paths

        # Save complete session summary
        self._save_json("SESSION_SUMMARY.json", results)

        print("\n" + "="*80)
        print("✅ Data Analysis Workflow Complete")
        print("="*80)
        print(f"\n📂 All files saved at: {self.session_dir}")
        print("\n📋 Generated files:")
        print(f"  1. Ontology identification prompt: {ontology_file}")
        print(f"  2. Data quality report: {self.session_dir / 'step3_validation_report.json'}")
        print(f"  3. Analysis planning prompt: {planning_file}")
        print(f"  4. Script generation prompt: {script_file}")
        print(f"  5. 📘 HTML report: {report_paths['html_report']}")
        print(f"  6. 📄 Markdown report: {report_paths['markdown_report']}")
        print(f"  7. 🖼️  Charts directory: {report_paths['charts_dir']}")
        print("\n💡 Usage notes:")
        print("  - View the HTML report for the full analysis results (with charts)")
        print("  - View the Markdown report for plain-text analysis content")
        print("  - Charts are saved separately in the charts/ directory")

        return results

    def _save_json(self, filename: str, data: Dict):
        """Save JSON file"""
        filepath = self.session_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    def _create_placeholder_ontology(self, data_profile: Dict) -> OntologyResult:
        """Create a placeholder ontology result (when LLM identification has not been run)"""
        return OntologyResult(
            entity_type="Pending identification",
            entity_type_reason="LLM ontology identification not yet invoked",
            generation_mechanism="Pending identification",
            mechanism_reason="LLM ontology identification not yet invoked",
            core_dimensions=[],
            is_economic=False,
            economic_type=None,
            domain_type="Pending identification",
            keywords=["pending identification"],
            recommended_questions=["pending identification"],
            limitations=["Ontology identification not completed"],
            confidence="low"
        )

    def _create_placeholder_plan(self) -> AnalysisPlan:
        """Create a placeholder analysis plan (when LLM planning has not been run)"""
        return AnalysisPlan(
            question_type="Pending planning",
            frameworks=[],
            analysis_steps=[],
            script_files=[],
            expected_outputs=["Pending planning"]
        )


def main():
    """Command-line entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Universal Data Analyst - Data Analysis Workflow Orchestrator'
    )
    parser.add_argument('file', help='Path to data file')
    parser.add_argument(
        '--intent', '-i',
        default='Exploratory data analysis to understand data characteristics and patterns',
        help='User analysis intent'
    )
    parser.add_argument(
        '--output', '-o',
        default='./analysis_output',
        help='Output directory'
    )

    args = parser.parse_args()

    # Run full analysis
    orchestrator = DataAnalysisOrchestrator(output_dir=args.output)
    results = orchestrator.run_full_analysis(
        file_path=args.file,
        user_intent=args.intent
    )

    print(f"\n✅ Analysis workflow complete. Results saved at: {results['session_dir']}")


if __name__ == '__main__':
    import pandas as pd
    main()
