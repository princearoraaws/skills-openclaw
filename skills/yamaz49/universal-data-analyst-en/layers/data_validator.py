"""
Data Validator

Validates data quality and detects common issues:
- Missing values
- Outliers
- Duplicate records
- Data type inconsistencies
- Business rule violations
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IssueSeverity(Enum):
    """Issue severity level"""
    CRITICAL = "critical"    # Must fix
    WARNING = "warning"      # Recommended to fix
    INFO = "info"            # For reference only


class CleaningActionType(Enum):
    """Cleaning action type"""
    DELETE_ROWS = "delete_rows"       # Delete rows
    DELETE_COLUMN = "delete_column"   # Delete column
    FILL_NA = "fill_na"               # Fill missing values
    CLIP = "clip"                     # Clip outliers
    CONVERT_TYPE = "convert_type"     # Type conversion
    KEEP = "keep"                     # Keep but flag
    REVIEW = "review"                 # Manual review


@dataclass
class CleaningAction:
    """Cleaning action recommendation"""
    action_type: CleaningActionType
    target: str                       # Operation target (column name or whole table)
    affected_rows: int                # Number of affected rows
    description: str                  # Action description
    reason: str                       # Reason for action
    recommended: bool = True          # Whether recommended to execute


@dataclass
class ValidationIssue:
    """Validation issue"""
    severity: IssueSeverity
    category: str                    # missing/duplicate/outlier/type/business
    column: Optional[str]            # Related column
    description: str
    affected_rows: int
    affected_percent: float
    suggestion: str
    cleaning_action: Optional[CleaningAction] = None  # Recommended cleaning action


@dataclass
class ValidationReport:
    """Validation report"""
    total_rows: int
    total_columns: int
    overall_score: float   # 0-100
    issues: List[ValidationIssue] = field(default_factory=list)
    passed_checks: List[str] = field(default_factory=list)

    def has_critical_issues(self) -> bool:
        return any(i.severity == IssueSeverity.CRITICAL for i in self.issues)

    def get_issues_by_severity(self, severity: IssueSeverity) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == severity]

    def get_cleaning_summary(self) -> Dict[str, Any]:
        """Get cleaning action summary"""
        summary = {
            'total_issues': len(self.issues),
            'recommended_deletions': 0,
            'recommended_fills': 0,
            'recommended_conversions': 0,
            'recommended_reviews': 0,
            'columns_to_delete': [],
            'rows_to_delete_estimate': 0,
            'actions_by_type': {}
        }

        for issue in self.issues:
            if issue.cleaning_action:
                action = issue.cleaning_action
                action_type = action.action_type.value

                # Count each action type
                if action_type not in summary['actions_by_type']:
                    summary['actions_by_type'][action_type] = []
                summary['actions_by_type'][action_type].append({
                    'target': action.target,
                    'rows': action.affected_rows,
                    'description': action.description
                })

                # Count recommended deletions
                if action.action_type == CleaningActionType.DELETE_ROWS:
                    summary['recommended_deletions'] += action.affected_rows
                    summary['rows_to_delete_estimate'] += action.affected_rows
                elif action.action_type == CleaningActionType.DELETE_COLUMN:
                    summary['columns_to_delete'].append(action.target)
                elif action.action_type == CleaningActionType.FILL_NA:
                    summary['recommended_fills'] += action.affected_rows
                elif action.action_type == CleaningActionType.CONVERT_TYPE:
                    summary['recommended_conversions'] += action.affected_rows
                elif action.action_type == CleaningActionType.REVIEW:
                    summary['recommended_reviews'] += action.affected_rows

        return summary

    def generate_cleaning_report(self) -> str:
        """Generate cleaning report text"""
        summary = self.get_cleaning_summary()
        lines = ["\n=== Data Cleaning Recommendation Report ===\n"]

        # Overall statistics
        lines.append(f"Original data: {self.total_rows:,} rows x {self.total_columns} columns")
        lines.append(f"Issues found: {summary['total_issues']}")
        lines.append("")

        # Recommended row deletions
        if summary['recommended_deletions'] > 0:
            lines.append(f"[Recommended Row Deletions] Total: {summary['recommended_deletions']:,} rows")
            if 'delete_rows' in summary['actions_by_type']:
                for action in summary['actions_by_type']['delete_rows']:
                    lines.append(f"  - {action['target']}: {action['rows']:,} rows - {action['description']}")
            lines.append("")
        else:
            lines.append("[Recommended Row Deletions] None")
            lines.append("  Strategy: Retain all rows, do not delete data directly")
            lines.append("")

        # Recommended column deletions
        if summary['columns_to_delete']:
            lines.append(f"[Recommended Column Deletions] Total: {len(summary['columns_to_delete'])} columns")
            for col in summary['columns_to_delete']:
                lines.append(f"  - {col}")
            lines.append("")

        # Missing value field analysis
        missing_issues = [i for i in self.issues if i.category == 'missing' and i.affected_rows > 0]
        if missing_issues:
            lines.append("[Missing Value Field Handling Notes]")
            lines.append(f"  {len(missing_issues)} fields have missing values. All original rows are retained; handle per-field as needed during analysis:")
            lines.append("")
            for issue in missing_issues:
                col = issue.column
                missing_count = issue.affected_rows
                missing_pct = issue.affected_percent
                valid_rows = self.total_rows - missing_count
                lines.append(f"  ▶ Field '{col}':")
                lines.append(f"    - Missing values: {missing_count:,} ({missing_pct:.2f}%)")
                lines.append(f"    - Valid data: {valid_rows:,} rows")
                lines.append(f"    - Handling: When analyzing this field, use {valid_rows:,} valid rows and note the data source")
                if issue.cleaning_action:
                    lines.append(f"    - Recommendation: {issue.cleaning_action.description}")
                lines.append("")

        # Recommended type conversions
        if summary['recommended_conversions'] > 0:
            lines.append("[Recommended Type Conversions]")
            if 'convert_type' in summary['actions_by_type']:
                for action in summary['actions_by_type']['convert_type']:
                    lines.append(f"  - {action['target']}: {action['description']}")
            lines.append("")

        # Recommended manual reviews
        if summary['recommended_reviews'] > 0:
            lines.append(f"[Recommended Manual Reviews] Total: {summary['recommended_reviews']:,} rows")
            if 'review' in summary['actions_by_type']:
                for action in summary['actions_by_type']['review']:
                    lines.append(f"  - {action['target']}: {action['rows']:,} rows - {action['description']}")
            lines.append("")

        # Anomalous but retained
        if 'keep' in summary['actions_by_type']:
            keep_actions = summary['actions_by_type']['keep']
            # Filter out non-missing keep items
            outlier_keep = [a for a in keep_actions if 'missing' not in a['description'].lower()]
            if outlier_keep:
                lines.append("[Outliers Retained]")
                for action in outlier_keep:
                    lines.append(f"  - {action['target']}: {action['description']}")
                lines.append("")

        # Estimated result after cleaning
        remaining_rows = self.total_rows - summary['rows_to_delete_estimate']
        lines.append("[Estimated Cleaning Result]")
        lines.append(f"  - Original rows: {self.total_rows:,}")
        lines.append(f"  - Rows to delete: {summary['rows_to_delete_estimate']:,}")
        lines.append(f"  - Rows retained: {remaining_rows:,} (100%)")
        lines.append("  - Note: All original data retained; each field handled independently based on its valid row count")

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_rows': self.total_rows,
            'total_columns': self.total_columns,
            'overall_score': round(self.overall_score, 1),
            'issue_count': len(self.issues),
            'critical_count': len(self.get_issues_by_severity(IssueSeverity.CRITICAL)),
            'warning_count': len(self.get_issues_by_severity(IssueSeverity.WARNING)),
            'passed_checks': self.passed_checks,
            'cleaning_summary': self.get_cleaning_summary(),
        }


class DataValidator:
    """
    Data Validator

    Automatically detects data quality issues.
    """

    tool_name = "data_validator"
    tool_description = "Validate data quality: detect missing values, outliers, duplicates, etc."

    # Threshold configuration (can be loaded from config file)
    DEFAULT_THRESHOLDS = {
        'missing_critical': 0.5,    # >50% missing is critical
        'missing_warning': 0.1,     # >10% missing is warning
        'duplicate_critical': 0.1,  # >10% duplicates is critical
        'duplicate_warning': 0.01,  # >1% duplicates is warning
        'outlier_zscore': 3,        # Z-score > 3 is outlier
        'outlier_iqr': 1.5,         # IQR multiplier
        'cardinality_ratio': 0.9,   # High cardinality ratio (unique/total)
    }

    def __init__(self, thresholds: Optional[Dict] = None):
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS

    def execute(self, data: pd.DataFrame,
                params: Optional[Dict] = None) -> ValidationReport:
        """
        Execute data validation

        Args:
            params: {
                'business_rules': [...],     # Business rules
                'custom_thresholds': {...},  # Custom thresholds
            }
        """
        issues = []
        passed = []

        params = params or {}
        custom_rules = params.get('business_rules', [])
        custom_thresholds = params.get('custom_thresholds', {})
        thresholds = {**self.thresholds, **custom_thresholds}

        # 1. Check missing values
        missing_issues = self._check_missing_values(data, thresholds)
        issues.extend(missing_issues)
        if not missing_issues:
            passed.append("Missing value check")

        # 2. Check duplicates
        duplicate_issues = self._check_duplicates(data, thresholds)
        issues.extend(duplicate_issues)
        if not duplicate_issues:
            passed.append("Duplicate check")

        # 3. Check outliers
        outlier_issues = self._check_outliers(data, thresholds)
        issues.extend(outlier_issues)
        if not outlier_issues:
            passed.append("Outlier check")

        # 4. Check data types
        type_issues = self._check_data_types(data)
        issues.extend(type_issues)
        if not type_issues:
            passed.append("Data type check")

        # 5. Check business rules
        if custom_rules:
            rule_issues = self._check_business_rules(data, custom_rules)
            issues.extend(rule_issues)

        # Calculate overall score
        score = self._calculate_score(data, issues)

        report = ValidationReport(
            total_rows=len(data),
            total_columns=len(data.columns),
            overall_score=score,
            issues=issues,
            passed_checks=passed
        )

        # Generate and log cleaning report
        cleaning_report = report.generate_cleaning_report()
        logger.info(cleaning_report)

        logger.info(f"Data validation complete: score {score:.1f}/100, "
                   f"{len(issues)} issues found")

        return report

    def interpret_results(self, results: Dict[str, Any]) -> str:
        """Interpret validation results"""
        report = ValidationReport(**results)

        if report.overall_score >= 90:
            return f"Excellent data quality ({report.overall_score:.0f}/100) — ready for analysis"
        elif report.overall_score >= 70:
            return f"Good data quality ({report.overall_score:.0f}/100) — recommended to address warnings"
        elif report.overall_score >= 50:
            return f"Fair data quality ({report.overall_score:.0f}/100) — cleaning needed"
        else:
            return f"Poor data quality ({report.overall_score:.0f}/100) — fix critical issues first"

    def _check_missing_values(self, data: pd.DataFrame,
                              thresholds: Dict) -> List[ValidationIssue]:
        """Check missing values"""
        issues = []
        total_rows = len(data)

        for col in data.columns:
            missing_count = data[col].isnull().sum()
            missing_pct = missing_count / total_rows

            if missing_pct > thresholds['missing_critical']:
                # Critical missing: recommend deleting the column (not rows)
                cleaning_action = CleaningAction(
                    action_type=CleaningActionType.DELETE_COLUMN,
                    target=col,
                    affected_rows=0,  # Don't delete rows
                    description=f"Delete column '{col}' (missing rate {missing_pct:.1%} is too high)",
                    reason=f"Missing rate {missing_pct:.1%} exceeds critical threshold {thresholds['missing_critical']:.1%}; recommend deleting the column rather than rows"
                )
                issues.append(ValidationIssue(
                    severity=IssueSeverity.CRITICAL,
                    category='missing',
                    column=col,
                    description=f"Column '{col}' has {missing_pct:.1%} missing rate ({missing_count:,} values)",
                    affected_rows=missing_count,
                    affected_percent=missing_pct * 100,
                    suggestion=f"Column is heavily missing; recommend deleting it. If needed for analysis, temporarily remove {missing_count:,} missing rows",
                    cleaning_action=cleaning_action
                ))
            elif missing_pct > thresholds['missing_warning']:
                # Warning-level missing: retain all rows, handle per-analysis
                cleaning_action = CleaningAction(
                    action_type=CleaningActionType.KEEP,
                    target=col,
                    affected_rows=0,  # Don't delete rows
                    description=f"Retain all rows; handle {missing_count:,} missing values in '{col}' when analyzing that field",
                    reason=f"Missing rate {missing_pct:.1%}; recommend retaining all data and noting when analyzing '{col}'"
                )
                issues.append(ValidationIssue(
                    severity=IssueSeverity.WARNING,
                    category='missing',
                    column=col,
                    description=f"Column '{col}' has {missing_pct:.1%} missing rate ({missing_count:,} values)",
                    affected_rows=missing_count,
                    affected_percent=missing_pct * 100,
                    suggestion=f"Retain all rows; when analyzing '{col}', temporarily exclude {missing_count:,} missing rows and note this",
                    cleaning_action=cleaning_action
                ))

        return issues

    def _check_duplicates(self, data: pd.DataFrame,
                         thresholds: Dict) -> List[ValidationIssue]:
        """Check duplicates"""
        issues = []
        total_rows = len(data)

        # Fully duplicate rows
        dup_count = data.duplicated().sum()
        dup_pct = dup_count / total_rows

        if dup_pct > thresholds['duplicate_critical']:
            cleaning_action = CleaningAction(
                action_type=CleaningActionType.DELETE_ROWS,
                target="entire table",
                affected_rows=dup_count,
                description=f"Delete {dup_count:,} fully duplicate records",
                reason=f"Duplicate rate {dup_pct:.1%} exceeds critical threshold — must delete"
            )
            issues.append(ValidationIssue(
                severity=IssueSeverity.CRITICAL,
                category='duplicate',
                column=None,
                description=f"Found {dup_count} fully duplicate records ({dup_pct:.1%})",
                affected_rows=dup_count,
                affected_percent=dup_pct * 100,
                suggestion="Delete duplicates and review data collection process",
                cleaning_action=cleaning_action
            ))
        elif dup_pct > thresholds['duplicate_warning']:
            cleaning_action = CleaningAction(
                action_type=CleaningActionType.DELETE_ROWS,
                target="entire table",
                affected_rows=dup_count,
                description=f"Delete {dup_count:,} fully duplicate records",
                reason=f"Duplicate rate {dup_pct:.1%} exceeds warning threshold — recommended to delete"
            )
            issues.append(ValidationIssue(
                severity=IssueSeverity.WARNING,
                category='duplicate',
                column=None,
                description=f"Found {dup_count} fully duplicate records ({dup_pct:.1%})",
                affected_rows=dup_count,
                affected_percent=dup_pct * 100,
                suggestion="Review and remove duplicate records",
                cleaning_action=cleaning_action
            ))

        return issues

    def _check_outliers(self, data: pd.DataFrame,
                       thresholds: Dict) -> List[ValidationIssue]:
        """Check outliers"""
        issues = []

        # Exclude boolean columns (bool is a subclass of np.number but can't do arithmetic)
        numeric_cols = data.select_dtypes(include=[np.number], exclude=['bool']).columns

        for col in numeric_cols:
            series = data[col].dropna()
            if len(series) < 10:
                continue

            # IQR method
            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - thresholds['outlier_iqr'] * IQR
            upper_bound = Q3 + thresholds['outlier_iqr'] * IQR

            outliers = series[(series < lower_bound) | (series > upper_bound)]
            outlier_pct = len(outliers) / len(series)

            if outlier_pct > 0.05:  # More than 5% outliers
                # Decide cleaning strategy based on outlier proportion
                if outlier_pct > 0.2:  # >20%: recommend clipping
                    cleaning_action = CleaningAction(
                        action_type=CleaningActionType.CLIP,
                        target=col,
                        affected_rows=len(outliers),
                        description=f"Clip outliers in column '{col}' (lower: {lower_bound:.2f}, upper: {upper_bound:.2f})",
                        reason=f"Outlier rate {outlier_pct:.1%} is high; recommend clipping rather than deleting"
                    )
                elif outlier_pct > 0.1:  # 10-20%: recommend manual review
                    cleaning_action = CleaningAction(
                        action_type=CleaningActionType.REVIEW,
                        target=col,
                        affected_rows=len(outliers),
                        description=f"Manually review {len(outliers):,} outliers in column '{col}'",
                        reason=f"Outlier rate {outlier_pct:.1%}; manual judgment needed"
                    )
                else:  # <10%: recommend deleting rows
                    cleaning_action = CleaningAction(
                        action_type=CleaningActionType.DELETE_ROWS,
                        target=col,
                        affected_rows=len(outliers),
                        description=f"Delete {len(outliers):,} rows containing outliers in '{col}'",
                        reason=f"Outlier rate {outlier_pct:.1%}; recommend removing outlier rows"
                    )

                issues.append(ValidationIssue(
                    severity=IssueSeverity.WARNING,
                    category='outlier',
                    column=col,
                    description=f"Column '{col}' has {len(outliers)} outliers ({outlier_pct:.1%})",
                    affected_rows=len(outliers),
                    affected_percent=outlier_pct * 100,
                    suggestion="Check if data error; or use robust statistical methods",
                    cleaning_action=cleaning_action
                ))

        return issues

    def _check_data_types(self, data: pd.DataFrame) -> List[ValidationIssue]:
        """Check data type issues"""
        issues = []

        # Check string columns that may be dates
        for col in data.select_dtypes(include=['object']).columns:
            sample = data[col].dropna().head(100)
            if len(sample) == 0:
                continue

            # Simple check for date-like formats
            date_patterns = [
                r'^\d{4}-\d{2}-\d{2}',
                r'^\d{4}/\d{2}/\d{2}',
                r'^\d{2}/\d{2}/\d{4}',
            ]

            date_like_count = 0
            for val in sample:
                for pattern in date_patterns:
                    if re.match(pattern, str(val)):
                        date_like_count += 1
                        break

            if date_like_count / len(sample) > 0.8:
                cleaning_action = CleaningAction(
                    action_type=CleaningActionType.CONVERT_TYPE,
                    target=col,
                    affected_rows=data[col].notna().sum(),
                    description=f"Convert column '{col}' from string to datetime type",
                    reason="Column content matches date format — converting enables time series analysis"
                )
                issues.append(ValidationIssue(
                    severity=IssueSeverity.INFO,
                    category='type',
                    column=col,
                    description=f"Column '{col}' looks like a date but is currently a string type",
                    affected_rows=len(sample),
                    affected_percent=100.0,
                    suggestion="Consider converting to datetime type for time series analysis",
                    cleaning_action=cleaning_action
                ))

        return issues

    def _check_business_rules(self, data: pd.DataFrame,
                             rules: List[Dict]) -> List[ValidationIssue]:
        """Check business rules"""
        issues = []

        for rule in rules:
            name = rule.get('name', 'Unnamed rule')
            condition = rule.get('condition')  # lambda or column name
            threshold = rule.get('threshold', 0)
            action = rule.get('action', 'review')  # delete/review/keep

            if callable(condition):
                violated = data.apply(condition, axis=1).sum()
            elif isinstance(condition, str) and condition in data.columns:
                violated = data[condition].sum() if data[condition].dtype == bool else 0
            else:
                continue

            violation_pct = violated / len(data)

            if violation_pct > threshold:
                # Determine cleaning action based on rule config
                if action == 'delete':
                    cleaning_action = CleaningAction(
                        action_type=CleaningActionType.DELETE_ROWS,
                        target=name,
                        affected_rows=violated,
                        description=f"Delete {violated:,} rows violating business rule '{name}'",
                        reason="Business rule violation — recommend deletion"
                    )
                elif action == 'keep':
                    cleaning_action = CleaningAction(
                        action_type=CleaningActionType.KEEP,
                        target=name,
                        affected_rows=violated,
                        description=f"Retain but flag {violated:,} rows violating business rule '{name}'",
                        reason="Business rule violation but data can be retained for analysis"
                    )
                else:  # default review
                    cleaning_action = CleaningAction(
                        action_type=CleaningActionType.REVIEW,
                        target=name,
                        affected_rows=violated,
                        description=f"Manually review {violated:,} rows violating business rule '{name}'",
                        reason="Manual judgment needed on whether to delete"
                    )

                issues.append(ValidationIssue(
                    severity=IssueSeverity.WARNING,
                    category='business',
                    column=None,
                    description=f"Business rule '{name}' violated {violated} times ({violation_pct:.1%})",
                    affected_rows=violated,
                    affected_percent=violation_pct * 100,
                    suggestion=rule.get('suggestion', 'Review business rule'),
                    cleaning_action=cleaning_action
                ))

        return issues

    def _calculate_score(self, data: pd.DataFrame,
                        issues: List[ValidationIssue]) -> float:
        """Calculate data quality score"""
        score = 100.0

        for issue in issues:
            if issue.severity == IssueSeverity.CRITICAL:
                score -= 20 * (issue.affected_percent / 100)
            elif issue.severity == IssueSeverity.WARNING:
                score -= 10 * (issue.affected_percent / 100)
            elif issue.severity == IssueSeverity.INFO:
                score -= 2 * (issue.affected_percent / 100)

        return max(0, min(100, score))


# Global instance
validator = DataValidator()

# Convenience function
def validate(data: pd.DataFrame, **kwargs) -> ValidationReport:
    """Convenience validation function"""
    return validator.execute(data, kwargs)
