#!/usr/bin/env python3
"""
Universal Data Analyst V2 - General Data Analysis Expert (Optimized)

Optimizations:
1. LLM Step Decoupling: Supports autonomous mode without external LLM
2. Multi-file/Multi-table Join: Supports multiple file inputs and automatic join detection
3. Quality-Driven Strategy: Automatically adjusts analysis strategy based on data quality

Workflow:
1. Load Data (data_loader) - Multi-file support
2. Data Ontology Profiling - Autonomous mode support
3. Data Quality Validation (data_validator) - Quality-driven strategy adjustment
4. Multi-table Join Analysis - Automatic join feasibility detection
5. Analysis Plan Generation - Autonomous mode support
6. Generate and Execute Analysis Scripts
7. Output Analysis Report
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime
import warnings

import pandas as pd
import numpy as np

# Add skill layers to path
SKILL_ROOT = Path(__file__).parent
sys.path.insert(0, str(SKILL_ROOT))
sys.path.insert(0, str(SKILL_ROOT / 'layers'))

from layers.data_loader import DataLoader, DataLoadResult, DataFormat
from layers.data_validator import DataValidator, ValidationReport


@dataclass
class DataOntology:
    """Data Ontology Recognition Results"""
    entity_type: str = "Feature/Attribute"
    entity_type_reason: str = "Default: Each row describes entity attributes"
    generation_mechanism: str = "Observational"
    mechanism_reason: str = "Default: Passively recorded data"
    core_dimensions: List[Dict[str, str]] = field(default_factory=list)
    quality_assessment: str = "Not Evaluated"
    is_economic: bool = False
    economic_type: Optional[str] = None
    domain_type: str = "General"
    keywords: List[str] = field(default_factory=lambda: ["data", "analysis"])
    recommended_questions: List[str] = field(default_factory=lambda: ["descriptive statistics"])
    limitations: List[str] = field(default_factory=lambda: ["No known limitations"])
    confidence: str = "Low"  # Confidence level of autonomous recognition


@dataclass
class AnalysisPlan:
    """Analysis Plan"""
    question_type: str = "Descriptive"
    question_type_reason: str = "Default: User intent does not specify causal inference"
    frameworks: List[Dict[str, str]] = field(default_factory=list)
    analysis_steps: List[Dict[str, Any]] = field(default_factory=list)
    scripts: List[Dict[str, str]] = field(default_factory=list)
    expected_outputs: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    quality_adjustments: List[str] = field(default_factory=list)  # Quality-driven adjustments


@dataclass
class MultiTableProfile:
    """Multi-table Join Analysis Results"""
    can_join: bool = False
    join_type: str = "left"  # left, inner, outer
    left_table: str = ""
    right_table: str = ""
    left_key: str = ""
    right_key: str = ""
    left_cardinality: int = 0
    right_cardinality: int = 0
    coverage: float = 0.0  # Join coverage rate
    type_conflicts: List[Dict[str, str]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class UniversalDataAnalystV2:
    """Universal Data Analysis Main Class (V2 Optimized)"""

    def __init__(self, autonomous: bool = False):
        self.loader = DataLoader()
        self.validator = DataValidator()
        self.autonomous = autonomous  # Autonomous mode switch

        # Multi-file support
        self.data_dict: Dict[str, pd.DataFrame] = {}  # Store multiple data tables
        self.load_results: Dict[str, DataLoadResult] = {}
        self.primary_table: Optional[str] = None

        # Analysis state
        self.validation_report: Optional[ValidationReport] = None
        self.ontology: Optional[DataOntology] = None
        self.analysis_plan: Optional[AnalysisPlan] = None
        self.multi_table_profile: Optional[MultiTableProfile] = None
        self.quality_strategy: Dict[str, Any] = {}  # Quality-driven strategy

    # ========== Multi-file Loading Support ==========

    def load_multiple_files(self, file_paths: List[str], **kwargs) -> Dict[str, DataLoadResult]:
        """
        Load multiple data files

        Args:
            file_paths: List of file paths
            **kwargs: Parameters passed to loader

        Returns:
            Dictionary of loading results for each file
        """
        print(f"📂 Loading {len(file_paths)} data file(s)...")

        results = {}
        for i, file_path in enumerate(file_paths, 1):
            print(f"\n  [{i}/{len(file_paths)}] Loading: {file_path}")
            result = self.loader.execute({'file_path': file_path, **kwargs})

            if result.success:
                # Use filename (without extension) as table name
                table_name = Path(file_path).stem
                self.data_dict[table_name] = result.data
                self.load_results[table_name] = result
                results[table_name] = result
                print(f"      ✓ Success: {result.rows:,} rows × {result.columns} columns")
            else:
                print(f"      ✗ Failed: {result.errors}")
                results[Path(file_path).stem] = result

        # Set primary table (first successfully loaded table)
        if self.data_dict:
            self.primary_table = list(self.data_dict.keys())[0]
            print(f"\n✅ Primary table set: {self.primary_table}")
            print(f"   Total {len(self.data_dict)} table(s) loaded")

        return results

    def analyze_join_feasibility(self, left_table: str = None, right_table: str = None,
                                  left_key: str = None, right_key: str = None) -> MultiTableProfile:
        """
        Analyze multi-table join feasibility

        Automatically detects join keys, cardinality, coverage, etc.
        """
        if len(self.data_dict) < 2:
            return MultiTableProfile(can_join=False, recommendations=["At least 2 tables required for join"])

        # If tables not specified, use first and second
        if left_table is None:
            left_table = list(self.data_dict.keys())[0]
        if right_table is None:
            right_table = list(self.data_dict.keys())[1]

        left_df = self.data_dict[left_table]
        right_df = self.data_dict[right_table]

        profile = MultiTableProfile()
        profile.left_table = left_table
        profile.right_table = right_table

        # Auto-detect join keys
        if left_key is None or right_key is None:
            left_key, right_key = self._detect_join_keys(left_df, right_df)

        if left_key is None:
            profile.recommendations.append("Unable to auto-detect join keys, please specify manually")
            return profile

        profile.left_key = left_key
        profile.right_key = right_key

        # Analyze cardinality
        left_unique = left_df[left_key].nunique()
        right_unique = right_df[right_key].nunique()
        profile.left_cardinality = left_unique
        profile.right_cardinality = right_unique

        # Check type conflicts
        left_dtype = left_df[left_key].dtype
        right_dtype = right_df[right_key].dtype

        if left_dtype != right_dtype:
            profile.type_conflicts.append({
                'left': f"{left_key} ({left_dtype})",
                'right': f"{right_key} ({right_dtype})",
                'suggestion': f"Recommend unifying to {left_dtype}"
            })

        # Calculate coverage
        left_values = set(left_df[left_key].dropna().astype(str))
        right_values = set(right_df[right_key].dropna().astype(str))

        if len(left_values) > 0:
            coverage = len(left_values & right_values) / len(left_values)
            profile.coverage = coverage

            if coverage >= 0.95:
                profile.join_type = "inner"
                profile.can_join = True
                profile.recommendations.append(f"Coverage {coverage*100:.1f}%, recommend INNER JOIN")
            elif coverage >= 0.8:
                profile.join_type = "left"
                profile.can_join = True
                profile.recommendations.append(f"Coverage {coverage*100:.1f}%, recommend LEFT JOIN (may lose some right table data)")
            elif coverage >= 0.5:
                profile.join_type = "outer"
                profile.can_join = True
                profile.recommendations.append(f"Coverage {coverage*100:.1f}%, recommend OUTER JOIN (both sides have unmatched data)")
            else:
                profile.can_join = False
                profile.recommendations.append(f"⚠️ Coverage only {coverage*100:.1f}%, join significance limited")

        # Detect duplicate keys (one-to-many relationships)
        left_duplicates = left_df[left_key].duplicated().sum()
        right_duplicates = right_df[right_key].duplicated().sum()

        if left_duplicates > 0 and right_duplicates > 0:
            profile.recommendations.append(f"Note: Both sides have duplicate keys (many-to-many), may cause Cartesian product explosion")
        elif left_duplicates > 0:
            profile.recommendations.append(f"Note: Left table join key has {left_duplicates} duplicates (one-to-many)")
        elif right_duplicates > 0:
            profile.recommendations.append(f"Note: Right table join key has {right_duplicates} duplicates (many-to-one)")

        self.multi_table_profile = profile
        return profile

    def _detect_join_keys(self, left_df: pd.DataFrame, right_df: pd.DataFrame) -> Tuple[Optional[str], Optional[str]]:
        """Auto-detect join keys"""
        # Candidate key names
        candidate_names = ['id', 'key', 'code', 'no', 'num', 'user_id', 'product_id', 'order_id']

        left_candidates = []
        right_candidates = []

        for col in left_df.columns:
            col_lower = col.lower()
            if any(cand in col_lower for cand in candidate_names):
                # Prioritize high cardinality columns
                uniqueness = left_df[col].nunique() / len(left_df)
                left_candidates.append((col, uniqueness))

        for col in right_df.columns:
            col_lower = col.lower()
            if any(cand in col_lower for cand in candidate_names):
                uniqueness = right_df[col].nunique() / len(right_df)
                right_candidates.append((col, uniqueness))

        # Sort by name match
        if left_candidates and right_candidates:
            # Look for same-name columns
            left_names = {c[0].lower() for c in left_candidates}
            right_names = {c[0].lower() for c in right_candidates}
            common = left_names & right_names

            if common:
                # Return first matching same-name column
                match = list(common)[0]
                left_key = next(c[0] for c in left_candidates if c[0].lower() == match)
                right_key = next(c[0] for c in right_candidates if c[0].lower() == match)
                return left_key, right_key

            # If no same-name columns, return highest cardinality candidate from each
            left_key = max(left_candidates, key=lambda x: x[1])[0]
            right_key = max(right_candidates, key=lambda x: x[1])[0]
            return left_key, right_key

        return None, None

    def join_tables(self, left_table: str = None, right_table: str = None,
                    left_key: str = None, right_key: str = None,
                    join_type: str = None) -> pd.DataFrame:
        """
        Execute multi-table join

        Returns:
            Joined DataFrame
        """
        if self.multi_table_profile is None:
            self.analyze_join_feasibility(left_table, right_table, left_key, right_key)

        profile = self.multi_table_profile

        if not profile.can_join:
            raise ValueError(f"Cannot join: {profile.recommendations}")

        left_df = self.data_dict[profile.left_table]
        right_df = self.data_dict[profile.right_table]

        join_type = join_type or profile.join_type

        # Handle type conflicts
        if profile.type_conflicts:
            # Unify to left table type
            right_df = right_df.copy()
            right_df[profile.right_key] = right_df[profile.right_key].astype(
                left_df[profile.left_key].dtype
            )

        # Execute join
        merged = left_df.merge(
            right_df,
            left_on=profile.left_key,
            right_on=profile.right_key,
            how=join_type,
            suffixes=('', f'_{profile.right_table}')
        )

        # Update primary table
        self.data_dict['merged'] = merged
        self.primary_table = 'merged'

        print(f"\n🔗 Join completed:")
        print(f"   Left: {profile.left_table} ({len(left_df):,} rows)")
        print(f"   Right: {profile.right_table} ({len(right_df):,} rows)")
        print(f"   Result: {len(merged):,} rows")
        print(f"   Method: {join_type.upper()} JOIN on {profile.left_key}={profile.right_key}")

        return merged

    # ========== Autonomous Mode Support ==========

    def profile_data_ontology(self, autonomous: bool = None) -> Union[str, DataOntology]:
        """
        Step 2: Data Ontology Profiling

        Args:
            autonomous: Whether to use autonomous mode (no LLM required)

        Returns:
            autonomous=True returns DataOntology object
            autonomous=False returns prompt string (requires external LLM)
        """
        autonomous = autonomous if autonomous is not None else self.autonomous

        if not self.data_dict:
            raise ValueError("Please load data first")

        # Use primary table for ontology profiling
        primary_df = self.data_dict[self.primary_table]

        print("\n🔍 Performing data ontology profiling...")

        if autonomous:
            # Autonomous mode: Rule-based inference
            self.ontology = self._autonomous_ontology_inference(primary_df)
            print(f"   ✓ Autonomous recognition complete (confidence: {self.ontology.confidence})")
            return self.ontology
        else:
            # Interactive mode: Generate prompt for external LLM
            data_profile = self._generate_data_profile(primary_df)
            prompt = self._build_ontology_prompt(data_profile)
            return prompt

    def _autonomous_ontology_inference(self, df: pd.DataFrame) -> DataOntology:
        """Rule-based automatic data ontology inference"""
        ontology = DataOntology()

        # Detect entity type
        col_names = [c.lower() for c in df.columns]

        # Time-series detection
        time_indicators = ['time', 'date', 'timestamp', 'created', 'updated', 'day', 'month', 'year']
        time_cols = [c for c in col_names if any(t in c for t in time_indicators)]

        if time_cols and len(df) > 1000:
            ontology.entity_type = "Temporal/Trajectory"
            ontology.entity_type_reason = f"Time columns detected: {time_cols[:3]}, large data volume ({len(df):,}), may contain time-series patterns"
            ontology.core_dimensions.append({"dimension": "time", "description": f"Columns: {', '.join(time_cols[:3])}"})

        # Transaction/Economic detection
        money_indicators = ['price', 'cost', 'amount', 'revenue', 'profit', 'salary', 'income', 'pay']
        money_cols = [c for c in col_names if any(m in c for m in money_indicators)]

        if money_cols:
            ontology.is_economic = True
            ontology.economic_type = "Transaction Data"
            ontology.entity_type = "Transaction/Event"
            ontology.entity_type_reason = f"Currency columns detected: {money_cols[:3]}"
            ontology.core_dimensions.append({"dimension": "economic", "description": f"Currency columns: {', '.join(money_cols[:3])}"})

        # ID/Relationship detection
        id_indicators = ['id', 'user', 'customer', 'product', 'order', 'item']
        id_cols = [c for c in col_names if any(i in c for i in id_indicators)]

        if len(id_cols) >= 2:
            if ontology.entity_type == "Feature/Attribute":
                ontology.entity_type = "Relationship/Network"
                ontology.entity_type_reason = f"Multiple entity IDs detected: {id_cols[:3]}, may contain relationships"
            ontology.core_dimensions.append({"dimension": "entity", "description": f"ID columns: {', '.join(id_cols[:3])}"})

        # Geographic detection
        geo_indicators = ['city', 'country', 'region', 'location', 'lat', 'lng', 'address']
        geo_cols = [c for c in col_names if any(g in c for g in geo_indicators)]

        if geo_cols:
            ontology.core_dimensions.append({"dimension": "geographic", "description": f"Geo columns: {', '.join(geo_cols[:3])}"})

        # Generate keywords
        ontology.keywords = list(set(
            [ontology.entity_type.split('/')[0]] +
            [ontology.economic_type] if ontology.economic_type else [] +
            time_cols[:1] + money_cols[:1] + id_cols[:1]
        ))[:5]

        # Recommended questions
        if ontology.is_economic:
            ontology.recommended_questions = ["income/expense distribution", "trend changes", "anomaly detection", "forecasting"]
        elif "Temporal" in ontology.entity_type:
            ontology.recommended_questions = ["time trends", "seasonality", "anomaly detection", "forecasting"]
        elif "Relationship" in ontology.entity_type:
            ontology.recommended_questions = ["relationship analysis", "network structure", "community detection"]
        else:
            ontology.recommended_questions = ["descriptive statistics", "distribution characteristics", "anomaly detection"]

        # Limitations
        ontology.limitations = []
        if len(df) < 100:
            ontology.limitations.append("Small sample size, limited statistical inference capability")
        if df.isnull().sum().sum() / (len(df) * len(df.columns)) > 0.1:
            ontology.limitations.append("High missing rate, watch for missing value impact")

        # Confidence
        if len(ontology.core_dimensions) >= 2 and ontology.entity_type != "Feature/Attribute":
            ontology.confidence = "High"
        elif len(ontology.core_dimensions) >= 1:
            ontology.confidence = "Medium"
        else:
            ontology.confidence = "Low"

        return ontology

    # ========== Quality-Driven Strategy Adjustment ==========

    def validate_data(self, table_name: str = None) -> ValidationReport:
        """
        Step 3: Data Quality Validation (with quality-driven strategy adjustment)
        """
        if not self.data_dict:
            raise ValueError("Please load data first")

        table_name = table_name or self.primary_table
        df = self.data_dict[table_name]

        print(f"\n🔎 Performing data quality validation on '{table_name}'...")
        self.validation_report = self.validator.execute(df)

        print(f"   Quality Score: {self.validation_report.overall_score:.1f}/100")
        print(f"   Issues Found: {len(self.validation_report.issues)}")

        # Generate quality-driven strategy adjustment
        self.quality_strategy = self._generate_quality_strategy()

        if self.quality_strategy.get('adjustments'):
            print(f"\n   📋 Quality-Driven Strategy Adjustments:")
            for adj in self.quality_strategy['adjustments']:
                print(f"      • {adj}")

        return self.validation_report

    def _generate_quality_strategy(self) -> Dict[str, Any]:
        """Generate analysis strategy based on data quality"""
        strategy = {
            'score': self.validation_report.overall_score,
            'adjustments': [],
            'recommended_methods': [],
            'avoid_methods': [],
            'confidence_level': 'normal'
        }

        if not self.validation_report:
            return strategy

        # Adjust strategy based on quality score
        score = self.validation_report.overall_score

        if score >= 90:
            strategy['confidence_level'] = 'high'
            strategy['adjustments'].append("Excellent data quality, complex inferential analysis allowed")
        elif score >= 70:
            strategy['confidence_level'] = 'normal'
            strategy['adjustments'].append("Good data quality, standard analysis workflow applicable")
        elif score >= 50:
            strategy['confidence_level'] = 'low'
            strategy['adjustments'].append("Average data quality, recommend data cleaning first")
            strategy['avoid_methods'].append("Complex causal inference (endogeneity issues may be amplified)")
        else:
            strategy['confidence_level'] = 'critical'
            strategy['adjustments'].append("⚠️ Poor data quality, analysis conclusions have low credibility")
            strategy['avoid_methods'].extend(["Predictive models", "Causal inference", "Statistical hypothesis testing"])
            strategy['recommended_methods'].append("Exploratory Data Analysis (EDA)")
            strategy['recommended_methods'].append("Data quality issue diagnosis")

        # Check specific issues and adjust
        from layers.data_validator import IssueSeverity
        critical_issues = [i for i in self.validation_report.issues if i.severity == IssueSeverity.CRITICAL]
        high_missing = [i for i in self.validation_report.issues if 'missing' in str(i).lower() and getattr(i, 'percentage', 0) > 20]

        if critical_issues:
            strategy['adjustments'].append(f"Found {len(critical_issues)} critical issues, needs priority handling")

        if high_missing:
            strategy['adjustments'].append("Some fields have >20% missing rate, recommend complete case analysis or imputation")
            strategy['avoid_methods'].append("Direct regression analysis with missing fields")

        # Time-series related checks
        if self.data_dict:
            df = list(self.data_dict.values())[0]
            time_cols = [c for c in df.columns if any(t in c.lower() for t in ['time', 'date', 'timestamp'])]

            if time_cols:
                for col in time_cols:
                    missing_pct = df[col].isnull().sum() / len(df) * 100
                    if missing_pct > 5:
                        strategy['adjustments'].append(f"Time column '{col}' has {missing_pct:.1f}% missing, time-series analysis needs caution")
                        strategy['avoid_methods'].append(f"Precise time-series analysis based on '{col}'")

        return strategy

    # ========== Analysis Plan Generation (with Quality Adjustment) ==========

    def plan_analysis(self, user_intent: str, autonomous: bool = None) -> Union[str, AnalysisPlan]:
        """
        Step 4: Analysis Plan Generation

        Combines quality strategy to adjust analysis plan
        """
        autonomous = autonomous if autonomous is not None else self.autonomous

        if not self.data_dict:
            raise ValueError("Please load data first")

        print(f"\n📋 Generating analysis plan...")
        print(f"   User Intent: {user_intent}")

        if self.quality_strategy.get('adjustments'):
            print(f"   Quality Adjustments: {len(self.quality_strategy['adjustments'])} strategies applied")

        if autonomous:
            self.analysis_plan = self._autonomous_plan_generation(user_intent)
            print(f"   ✓ Autonomous planning complete")
            return self.analysis_plan
        else:
            primary_df = self.data_dict[self.primary_table]
            prompt = self._build_planning_prompt(user_intent, primary_df)
            return prompt

    def _autonomous_plan_generation(self, user_intent: str) -> AnalysisPlan:
        """Rule-based automatic analysis plan generation"""
        plan = AnalysisPlan()

        # Determine question type
        intent_lower = user_intent.lower()

        if any(w in intent_lower for w in ['why', 'reason', 'factor', 'cause']):
            plan.question_type = "Diagnostic"
            plan.question_type_reason = "User asks for reasons"
        elif any(w in intent_lower for w in ['predict', 'future', 'will', 'forecast']):
            plan.question_type = "Predictive"
            plan.question_type_reason = "User requests prediction"
        elif any(w in intent_lower for w in ['validate', 'causal', 'impact', 'effect']):
            plan.question_type = "Causal"
            plan.question_type_reason = "User requests causal relationship validation"
        else:
            plan.question_type = "Descriptive"
            plan.question_type_reason = "Default: Descriptive analysis"

        # Apply quality adjustments
        if self.quality_strategy:
            plan.quality_adjustments = self.quality_strategy.get('adjustments', [])

            # Reduce complexity if quality is low
            if self.quality_strategy.get('confidence_level') == 'critical':
                plan.question_type = "Descriptive"
                plan.question_type_reason += " (Downgraded due to data quality issues)"
                plan.risks.append("Poor data quality, all inferential conclusions have low credibility")

        # Recommend frameworks
        if self.ontology:
            if "Temporal" in self.ontology.entity_type:
                plan.frameworks.append({"framework": "Time-series Analysis", "reason": "Data contains time dimension"})
            if self.ontology.is_economic:
                plan.frameworks.append({"framework": "Econometrics", "reason": "Economic data characteristics"})
            if "Relationship" in self.ontology.entity_type:
                plan.frameworks.append({"framework": "Network Analysis", "reason": "Multiple entity relationships"})

        # Basic framework
        plan.frameworks.append({"framework": "Descriptive Statistics", "reason": "Foundation for all analyses"})

        # Analysis steps
        steps = [
            {"step": 1, "name": "Data Overview", "content": "Basic statistics, distribution analysis"},
            {"step": 2, "name": "Quality Check", "content": "Missing values, outlier handling"},
        ]

        if plan.question_type in ["Diagnostic", "Causal"]:
            steps.append({"step": 3, "name": "Correlation Analysis", "content": "Explore variable relationships"})
            steps.append({"step": 4, "name": "Diagnostic Validation", "content": "Regression analysis, group comparison"})

        if plan.question_type == "Predictive":
            steps.append({"step": 3, "name": "Feature Engineering", "content": "Build predictive features"})
            steps.append({"step": 4, "name": "Model Training", "content": "Time-series forecasting or machine learning"})

        plan.analysis_steps = steps
        plan.expected_outputs = ["HTML Report", "Visualization Charts", "Analysis Summary"]

        return plan

    # ========== Helper Methods ==========

    def _generate_data_profile(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate data profile"""
        profile = {
            'shape': df.shape,
            'memory_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
            'columns': []
        }

        for col in df.columns:
            col_info = {
                'name': col,
                'dtype': str(df[col].dtype),
                'null_count': df[col].isnull().sum(),
                'null_pct': df[col].isnull().sum() / len(df) * 100,
                'unique_count': df[col].nunique(),
            }

            if pd.api.types.is_numeric_dtype(df[col]):
                col_info.update({
                    'type': 'numeric',
                    'min': df[col].min(),
                    'max': df[col].max(),
                    'mean': df[col].mean() if df[col].notna().any() else None,
                })
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                col_info.update({
                    'type': 'datetime',
                    'min': str(df[col].min()),
                    'max': str(df[col].max()),
                })
            else:
                col_info.update({
                    'type': 'categorical' if df[col].nunique() < 100 else 'text',
                    'sample_values': df[col].dropna().head(5).tolist(),
                })

            profile['columns'].append(col_info)

        profile['potential_time_cols'] = [
            col for col in df.columns
            if any(keyword in col.lower() for keyword in ['time', 'date', 'timestamp', 'created', 'updated'])
        ]

        profile['potential_price_cols'] = [
            col for col in df.columns
            if any(keyword in col.lower() for keyword in ['price', 'cost', 'amount', 'revenue', 'profit'])
            and pd.api.types.is_numeric_dtype(df[col])
        ]

        return profile

    def _build_ontology_prompt(self, data_profile: Dict[str, Any]) -> str:
        """Build data ontology recognition prompt"""
        prompt = f"""You are a data ontology expert. Please analyze the basic characteristics of the following data.

Data Overview:
- Rows: {data_profile['shape'][0]:,}
- Columns: {data_profile['shape'][1]}
- Memory: {data_profile['memory_mb']:.2f} MB

Column Details:
"""
        for col in data_profile['columns'][:10]:
            prompt += f"\n- {col['name']} ({col['type']}, {col['dtype']})"
            if col.get('unique_count'):
                prompt += f", Unique: {col['unique_count']: ,}"
            if col.get('null_pct') > 0:
                prompt += f", Missing: {col['null_pct']:.1f}%"

        if data_profile.get('potential_time_cols'):
            prompt += f"\n\nPotential Time Columns: {data_profile['potential_time_cols']}"
        if data_profile.get('potential_price_cols'):
            prompt += f"\nPotential Price/Currency Columns: {data_profile['potential_price_cols']}"

        prompt += """

Please answer:
1. Entity Type: Transaction/Event, State/Stock, Relationship/Network, Feature/Attribute, or Temporal/Trajectory?
2. Data Generation Mechanism: Observational/Experimental/Simulated/Measured/Reported?
3. Core Dimensions: Time? Geographic? Categorical? Network relationships?
4. Is it economic data? If yes, preliminary type judgment?
5. 3-5 keyword tags
6. What questions is it best suited to answer?
7. Obvious limitations?
"""
        return prompt

    def _build_planning_prompt(self, user_intent: str, df: pd.DataFrame) -> str:
        """Build analysis planning prompt"""
        sample = df.head(10).to_string()

        column_details = []
        for col in df.columns:
            dtype = df[col].dtype
            unique = df[col].nunique()
            null_pct = df[col].isnull().sum() / len(df) * 100

            detail = f"{col}: {dtype}, Unique {unique:,}, Missing {null_pct:.1f}%"
            if pd.api.types.is_numeric_dtype(df[col]):
                detail += f", Range[{df[col].min():.2f}, {df[col].max():.2f}]"
            column_details.append(detail)

        # Add quality strategy info
        quality_info = ""
        if self.quality_strategy:
            quality_info = f"""
Data Quality Information:
- Quality Score: {self.quality_strategy.get('score', 'N/A')}/100
- Confidence Level: {self.quality_strategy.get('confidence_level', 'unknown')}
- Methods to Avoid: {', '.join(self.quality_strategy.get('avoid_methods', []))}
- Recommended Methods: {', '.join(self.quality_strategy.get('recommended_methods', []))}
"""

        prompt = f"""You are a cross-domain data analysis expert. Please plan a complete analysis.

User Intent: {user_intent}

{quality_info}

Data Sample (first 10 rows):
{sample}

Column Details:
{chr(10).join(column_details)}

Please complete:
1. Question type determination (Descriptive/Diagnostic/Predictive/Prescriptive/Causal)
2. Recommended analysis frameworks and reasons
3. Step-by-step analysis path (specific to code logic)
4. Script file list
5. Expected outputs
"""
        return prompt

    def save_session(self, output_dir: str = "./analysis_output") -> str:
        """Save analysis session"""
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_file = os.path.join(output_dir, f"session_v2_{timestamp}.json")

        session_data = {
            'timestamp': timestamp,
            'version': '2.0',
            'autonomous': self.autonomous,
            'tables': list(self.data_dict.keys()),
            'primary_table': self.primary_table,
            'validation': self.validation_report.to_dict() if self.validation_report else None,
            'ontology': asdict(self.ontology) if self.ontology else None,
            'quality_strategy': self.quality_strategy,
            'multi_table_profile': asdict(self.multi_table_profile) if self.multi_table_profile else None,
        }

        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)

        return session_file


# ========== Command Line Entry ==========

def main():
    """Command line entry"""
    parser = argparse.ArgumentParser(description='Universal Data Analysis Tool V2 (Optimized)')
    parser.add_argument('files', nargs='+', help='Data file paths (multiple supported)')
    parser.add_argument('--intent', '-i', help='User analysis intent', default='Exploratory Data Analysis')
    parser.add_argument('--validate', '-v', action='store_true', help='Execute data quality validation')
    parser.add_argument('--output', '-o', default='./analysis_output', help='Output directory')
    parser.add_argument('--autonomous', '-a', action='store_true',
                        help='Autonomous mode: No external LLM required, auto-completes all judgments')
    parser.add_argument('--join', '-j', action='store_true',
                        help='Automatically analyze and execute multi-table joins')

    args = parser.parse_args()

    # Initialize analyzer
    analyst = UniversalDataAnalystV2(autonomous=args.autonomous)

    print("="*70)
    print("Universal Data Analyst V2 (Optimized)")
    print(f"Mode: {'Autonomous' if args.autonomous else 'Interactive'}")
    print("="*70)

    # Step 1: Load multiple data files
    results = analyst.load_multiple_files(args.files)

    if not analyst.data_dict:
        print("❌ No data files loaded successfully")
        sys.exit(1)

    # Multi-table join (if requested)
    if args.join and len(analyst.data_dict) >= 2:
        print("\n" + "="*70)
        print("【Multi-table Join Analysis】")
        print("="*70)

        profile = analyst.analyze_join_feasibility()

        print(f"\nJoin Feasibility Analysis:")
        print(f"  Left Table: {profile.left_table}")
        print(f"  Right Table: {profile.right_table}")
        print(f"  Join Keys: {profile.left_key} = {profile.right_key}")
        print(f"  Coverage: {profile.coverage*100:.1f}%")
        print(f"  Recommendation: {profile.recommendations[0] if profile.recommendations else 'N/A'}")

        if profile.can_join:
            merged = analyst.join_tables()
            print(f"\n✅ Join completed, primary table updated to 'merged'")
        else:
            print(f"\n⚠️ Join not recommended: {profile.recommendations}")

    # Step 2: Data Ontology Profiling
    print("\n" + "="*70)
    print("【Step 2】Data Ontology Profiling")
    print("="*70)

    ontology_result = analyst.profile_data_ontology()

    if args.autonomous:
        onto = ontology_result
        print(f"\n✓ Autonomous Recognition Results:")
        print(f"  Entity Type: {onto.entity_type}")
        print(f"  Generation Mechanism: {onto.generation_mechanism}")
        print(f"  Core Dimensions: {', '.join([d.get('dimension', '') for d in onto.core_dimensions])}")
        print(f"  Keywords: {', '.join(onto.keywords)}")
        print(f"  Confidence: {onto.confidence}")
    else:
        print("\nPrompt (requires LLM call):")
        print(ontology_result[:500] + "...")

    # Step 3: Data Quality Validation
    if args.validate:
        print("\n" + "="*70)
        print("【Step 3】Data Quality Validation")
        print("="*70)

        analyst.validate_data()

    # Step 4: Analysis Plan Generation
    print("\n" + "="*70)
    print("【Step 4】Analysis Plan Generation")
    print("="*70)

    plan_result = analyst.plan_analysis(args.intent)

    if args.autonomous:
        plan = plan_result
        print(f"\n✓ Autonomous Planning Results:")
        print(f"  Question Type: {plan.question_type}")
        print(f"  Analysis Frameworks: {', '.join([f.get('framework', '') for f in plan.frameworks])}")
        print(f"  Analysis Steps: {len(plan.analysis_steps)} steps")
        if plan.quality_adjustments:
            print(f"  Quality Adjustments: {len(plan.quality_adjustments)} items")
    else:
        print("\nPrompt (requires LLM call):")
        print(plan_result[:500] + "...")

    # Save session
    session_file = analyst.save_session(args.output)
    print(f"\n💾 Session saved: {session_file}")

    print("\n" + "="*70)
    print("Analysis preparation complete")
    print("="*70)


if __name__ == '__main__':
    main()
