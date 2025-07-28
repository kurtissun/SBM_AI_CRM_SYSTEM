import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Callable
import logging
from datetime import datetime, timedelta
import json
from dataclasses import dataclass
from enum import Enum
import warnings

logger = logging.getLogger(__name__)

class ValidationSeverity(Enum):
    INFO = "info"
    WARNING = "warning" 
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class ValidationRule:
    name: str
    description: str
    column: Optional[str]
    rule_type: str
    parameters: Dict[str, Any]
    severity: ValidationSeverity
    enabled: bool = True

@dataclass
class ValidationResult:
    rule_name: str
    passed: bool
    severity: ValidationSeverity
    message: str
    affected_rows: int
    details: Dict[str, Any]

class DataValidator:
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.validation_history = []
        self.custom_rules = {}
        self.standard_rules = self._initialize_standard_rules()
        
    def _initialize_standard_rules(self) -> List[ValidationRule]:
        rules = [
            ValidationRule(
                name="customer_id_not_null",
                description="Customer ID should not be null",
                column="customer_id",
                rule_type="not_null",
                parameters={},
                severity=ValidationSeverity.CRITICAL
            ),
            ValidationRule(
                name="minimum_completeness",
                description="Dataset should have minimum 70% completeness",
                column=None,
                rule_type="completeness_threshold",
                parameters={"min_completeness": 0.7},
                severity=ValidationSeverity.ERROR
            ),
            ValidationRule(
                name="age_range_valid",
                description="Age should be between 1 and 120",
                column="age",
                rule_type="range",
                parameters={"min_value": 1, "max_value": 120},
                severity=ValidationSeverity.ERROR
            ),
            ValidationRule(
                name="rating_range_valid", 
                description="Rating should be between 1 and 5",
                column="rating_id",
                rule_type="range",
                parameters={"min_value": 1, "max_value": 5},
                severity=ValidationSeverity.WARNING
            ),
            ValidationRule(
                name="email_format_valid",
                description="Email should have valid format",
                column="email",
                rule_type="regex_pattern",
                parameters={"pattern": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'},
                severity=ValidationSeverity.WARNING
            ),
            ValidationRule(
                name="phone_format_valid",
                description="Phone should have valid format",
                column="phone",
                rule_type="regex_pattern", 
                parameters={"pattern": r'^\+?1?\d{9,15}$'},
                severity=ValidationSeverity.WARNING
            ),
            ValidationRule(
                name="gender_valid_values",
                description="Gender should be male, female, or other",
                column="sex",
                rule_type="allowed_values",
                parameters={"allowed_values": ["male", "female", "other", "男", "女", "m", "f", "0", "1"]},
                severity=ValidationSeverity.WARNING
            ),
            ValidationRule(
                name="outlier_detection",
                description="Detect statistical outliers in numeric columns",
                column=None,
                rule_type="outlier_detection",
                parameters={"method": "iqr", "threshold": 1.5},
                severity=ValidationSeverity.INFO
            ),
            ValidationRule(
                name="registration_date_logical",
                description="Registration date should not be in the future",
                column="registration_time",
                rule_type="date_logical",
                parameters={"max_date": "today"},
                severity=ValidationSeverity.ERROR
            ),
            ValidationRule(
                name="age_birthdate_consistency",
                description="Age should be consistent with birth date",
                column=None,
                rule_type="cross_field_consistency",
                parameters={"field1": "age", "field2": "birthdate", "tolerance_years": 1},
                severity=ValidationSeverity.WARNING
            )
        ]
        return rules
    
    def validate_dataset(self, df: pd.DataFrame, custom_rules: List[ValidationRule] = None) -> Dict[str, Any]:
        logger.info(f"Starting validation for dataset with {len(df)} rows, {len(df.columns)} columns")
        
        validation_report = {
            'timestamp': datetime.now().isoformat(),
            'dataset_info': {
                'shape': df.shape,
                'columns': list(df.columns),
                'memory_usage': df.memory_usage(deep=True).sum()
            },
            'validation_results': [],
            'summary': {
                'total_rules': 0,
                'passed': 0,
                'failed': 0,
                'by_severity': {sev.value: 0 for sev in ValidationSeverity}
            },
            'data_quality_score': 0.0,
            'recommendations': []
        }
        
        all_rules = self.standard_rules.copy()
        if custom_rules:
            all_rules.extend(custom_rules)
        
        validation_report['summary']['total_rules'] = len(all_rules)
        
        for rule in all_rules:
            if not rule.enabled:
                continue
                
            try:
                result = self._execute_validation_rule(df, rule)
                validation_report['validation_results'].append(result)
                
                if result.passed:
                    validation_report['summary']['passed'] += 1
                else:
                    validation_report['summary']['failed'] += 1
                
                validation_report['summary']['by_severity'][result.severity.value] += 1
                
            except Exception as e:
                logger.error(f"Error executing rule {rule.name}: {e}")
                error_result = ValidationResult(
                    rule_name=rule.name,
                    passed=False,
                    severity=ValidationSeverity.ERROR,
                    message=f"Rule execution failed: {str(e)}",
                    affected_rows=0,
                    details={'error': str(e)}
                )
                validation_report['validation_results'].append(error_result)
                validation_report['summary']['failed'] += 1
        
        validation_report['data_quality_score'] = self._calculate_quality_score(validation_report)
        validation_report['recommendations'] = self._generate_recommendations(validation_report)
        self.validation_history.append(validation_report)
        
        logger.info(f"Validation completed. Quality score: {validation_report['data_quality_score']:.2f}")
        return validation_report
    
    def _execute_validation_rule(self, df: pd.DataFrame, rule: ValidationRule) -> ValidationResult:
        if rule.rule_type == "not_null":
            return self._validate_not_null(df, rule)
        elif rule.rule_type == "completeness_threshold":
            return self._validate_completeness_threshold(df, rule)
        elif rule.rule_type == "range":
            return self._validate_range(df, rule)
        elif rule.rule_type == "regex_pattern":
            return self._validate_regex_pattern(df, rule)
        elif rule.rule_type == "allowed_values":
            return self._validate_allowed_values(df, rule)
        elif rule.rule_type == "outlier_detection":
            return self._validate_outliers(df, rule)
        elif rule.rule_type == "date_logical":
            return self._validate_date_logical(df, rule)
        elif rule.rule_type == "cross_field_consistency":
            return self._validate_cross_field_consistency(df, rule)
        else:
            raise ValueError(f"Unknown rule type: {rule.rule_type}")
    
    def _validate_not_null(self, df: pd.DataFrame, rule: ValidationRule) -> ValidationResult:
        if rule.column not in df.columns:
            return ValidationResult(
                rule_name=rule.name,
                passed=False,
                severity=rule.severity,
                message=f"Column {rule.column} not found in dataset",
                affected_rows=0,
                details={'missing_column': rule.column}
            )
        
        null_count = df[rule.column].isnull().sum()
        passed = null_count == 0
        
        return ValidationResult(
            rule_name=rule.name,
            passed=passed,
            severity=rule.severity,
            message=f"Found {null_count} null values in {rule.column}" if not passed else "No null values found",
            affected_rows=int(null_count),
            details={'null_count': int(null_count), 'null_percentage': float(null_count / len(df) * 100)}
        )
    
    def _validate_completeness_threshold(self, df: pd.DataFrame, rule: ValidationRule) -> ValidationResult:
        min_completeness = rule.parameters['min_completeness']
        
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()
        completeness = 1 - (missing_cells / total_cells)
        
        passed = completeness >= min_completeness
        
        return ValidationResult(
            rule_name=rule.name,
            passed=passed,
            severity=rule.severity,
            message=f"Dataset completeness: {completeness:.2%} (threshold: {min_completeness:.2%})",
            affected_rows=int(missing_cells),
            details={
                'completeness': float(completeness),
                'threshold': min_completeness,
                'missing_cells': int(missing_cells),
                'total_cells': int(total_cells)
            }
        )
    
    def _validate_range(self, df: pd.DataFrame, rule: ValidationRule) -> ValidationResult:
        if rule.column not in df.columns:
            return ValidationResult(
                rule_name=rule.name,
                passed=False,
                severity=rule.severity,
                message=f"Column {rule.column} not found",
                affected_rows=0,
                details={'missing_column': rule.column}
            )
        
        min_val = rule.parameters.get('min_value')
        max_val = rule.parameters.get('max_value')
        
        try:
            series = pd.to_numeric(df[rule.column], errors='coerce')
        except:
            series = df[rule.column]
        
        violations = pd.Series([False] * len(df))
        
        if min_val is not None:
            violations |= (series < min_val)
        if max_val is not None:
            violations |= (series > max_val)
        
        violation_count = violations.sum()
        passed = violation_count == 0
        
        return ValidationResult(
            rule_name=rule.name,
            passed=passed,
            severity=rule.severity,
            message=f"Found {violation_count} values outside range [{min_val}, {max_val}]" if not passed else "All values within range",
            affected_rows=int(violation_count),
            details={
                'violations': int(violation_count),
                'min_value': min_val,
                'max_value': max_val,
                'actual_min': float(series.min()) if not series.empty else None,
                'actual_max': float(series.max()) if not series.empty else None
            }
        )
    
    def _validate_regex_pattern(self, df: pd.DataFrame, rule: ValidationRule) -> ValidationResult:
        if rule.column not in df.columns:
            return ValidationResult(
                rule_name=rule.name,
                passed=False,
                severity=rule.severity,
                message=f"Column {rule.column} not found",
                affected_rows=0,
                details={'missing_column': rule.column}
            )
        
        pattern = rule.parameters['pattern']
        non_null_series = df[rule.column].dropna().astype(str)
        
        if len(non_null_series) == 0:
            return ValidationResult(
                rule_name=rule.name,
                passed=True,
                severity=rule.severity,
                message="No non-null values to validate",
                affected_rows=0,
                details={'pattern': pattern}
            )
        
        matches = non_null_series.str.match(pattern, na=False)
        violations = (~matches).sum()
        passed = violations == 0
        
        return ValidationResult(
            rule_name=rule.name,
            passed=passed,
            severity=rule.severity,
            message=f"Found {violations} values not matching pattern" if not passed else "All values match pattern",
            affected_rows=int(violations),
            details={
                'pattern': pattern,
                'violations': int(violations),
                'total_checked': len(non_null_series)
            }
        )
    
    def _validate_allowed_values(self, df: pd.DataFrame, rule: ValidationRule) -> ValidationResult:
        if rule.column not in df.columns:
            return ValidationResult(
                rule_name=rule.name,
                passed=False,
                severity=rule.severity,
                message=f"Column {rule.column} not found",
                affected_rows=0,
                details={'missing_column': rule.column}
            )
        
        allowed_values = rule.parameters['allowed_values']
        series = df[rule.column].astype(str).str.lower()
        allowed_lower = [str(val).lower() for val in allowed_values]
        
        violations = ~series.isin(allowed_lower + ['nan'])
        violation_count = violations.sum()
        passed = violation_count == 0
        
        invalid_values = df.loc[violations, rule.column].unique()[:10]
        
        return ValidationResult(
            rule_name=rule.name,
            passed=passed,
            severity=rule.severity,
            message=f"Found {violation_count} disallowed values" if not passed else "All values are allowed",
            affected_rows=int(violation_count),
            details={
                'allowed_values': allowed_values,
                'violations': int(violation_count),
                'invalid_examples': invalid_values.tolist() if len(invalid_values) > 0 else []
            }
        )
    
    def _validate_outliers(self, df: pd.DataFrame, rule: ValidationRule) -> ValidationResult:
        method = rule.parameters.get('method', 'iqr')
        threshold = rule.parameters.get('threshold', 1.5)
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        outlier_summary = {}
        total_outliers = 0
        
        for column in numeric_columns:
            if column in ['customer_id', 'id']:
                continue
                
            series = df[column].dropna()
            
            if method == 'iqr':
                Q1 = series.quantile(0.25)
                Q3 = series.quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                outliers = ((series < lower_bound) | (series > upper_bound)).sum()
            
            elif method == 'zscore':
                z_scores = np.abs((series - series.mean()) / series.std())
                outliers = (z_scores > threshold).sum()
            
            else:
                outliers = 0
            
            if outliers > 0:
                outlier_summary[column] = {
                    'count': int(outliers),
                    'percentage': float(outliers / len(series) * 100)
                }
                total_outliers += outliers
        
        return ValidationResult(
            rule_name=rule.name,
            passed=True,
            severity=rule.severity,
            message=f"Detected {total_outliers} outliers across {len(outlier_summary)} columns",
            affected_rows=int(total_outliers),
            details={
                'method': method,
                'threshold': threshold,
                'outlier_summary': outlier_summary,
                'total_outliers': int(total_outliers)
            }
        )
    
    def _validate_date_logical(self, df: pd.DataFrame, rule: ValidationRule) -> ValidationResult:
        if rule.column not in df.columns:
            return ValidationResult(
                rule_name=rule.name,
                passed=False,
                severity=rule.severity,
                message=f"Column {rule.column} not found",
                affected_rows=0,
                details={'missing_column': rule.column}
            )
        
        max_date_param = rule.parameters.get('max_date', 'today')
        
        try:
            date_series = pd.to_datetime(df[rule.column], errors='coerce')
        except:
            return ValidationResult(
                rule_name=rule.name,
                passed=False,
                severity=rule.severity,
                message=f"Cannot convert {rule.column} to datetime",
                affected_rows=0,
                details={'conversion_error': True}
            )
        
        if max_date_param == 'today':
            max_date = datetime.now()
        else:
            max_date = pd.to_datetime(max_date_param)
        
        violations = (date_series > max_date)
        violation_count = violations.sum()
        passed = violation_count == 0
        
        return ValidationResult(
            rule_name=rule.name,
            passed=passed,
            severity=rule.severity,
            message=f"Found {violation_count} dates after {max_date.date()}" if not passed else "All dates are logical",
            affected_rows=int(violation_count),
            details={
                'max_allowed_date': max_date.isoformat(),
                'violations': int(violation_count),
                'latest_date': date_series.max().isoformat() if not date_series.empty else None
            }
        )
    
    def _validate_cross_field_consistency(self, df: pd.DataFrame, rule: ValidationRule) -> ValidationResult:
        field1 = rule.parameters.get('field1')
        field2 = rule.parameters.get('field2')
        tolerance_years = rule.parameters.get('tolerance_years', 1)
        
        if field1 not in df.columns or field2 not in df.columns:
            missing_fields = [f for f in [field1, field2] if f not in df.columns]
            return ValidationResult(
                rule_name=rule.name,
                passed=False,
                severity=rule.severity,
                message=f"Missing fields: {missing_fields}",
                affected_rows=0,
                details={'missing_fields': missing_fields}
            )
        
        if field1 == 'age' and 'birth' in field2.lower():
            try:
                birthdates = pd.to_datetime(df[field2], errors='coerce')
                today = datetime.now()
                calculated_ages = ((today - birthdates).dt.days / 365.25).round().astype('Int64')
                age_differences = np.abs(df[field1] - calculated_ages)
                inconsistent = age_differences > tolerance_years
                violation_count = inconsistent.sum()
                passed = violation_count == 0
                
                return ValidationResult(
                    rule_name=rule.name,
                    passed=passed,
                    severity=rule.severity,
                    message=f"Found {violation_count} age-birthdate inconsistencies" if not passed else "Age and birthdate are consistent",
                    affected_rows=int(violation_count),
                    details={
                        'tolerance_years': tolerance_years,
                        'violations': int(violation_count),
                        'max_difference': float(age_differences.max()) if not age_differences.empty else None
                    }
                )
                
            except Exception as e:
                return ValidationResult(
                    rule_name=rule.name,
                    passed=False,
                    severity=rule.severity,
                    message=f"Error validating age-birthdate consistency: {str(e)}",
                    affected_rows=0,
                    details={'error': str(e)}
                )
        
        return ValidationResult(
            rule_name=rule.name,
            passed=True,
            severity=rule.severity,
            message="Cross-field validation not implemented for these fields",
            affected_rows=0,
            details={'field1': field1, 'field2': field2}
        )
    
    def _calculate_quality_score(self, validation_report: Dict) -> float:
        results = validation_report['validation_results']
        
        if not results:
            return 0.0
        
        severity_weights = {
            ValidationSeverity.CRITICAL: 1.0,
            ValidationSeverity.ERROR: 0.8,
            ValidationSeverity.WARNING: 0.5,
            ValidationSeverity.INFO: 0.1
        }
        
        total_weight = 0
        weighted_score = 0
        
        for result in results:
            weight = severity_weights.get(result.severity, 0.5)
            total_weight += weight
            
            if result.passed:
                weighted_score += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    def _generate_recommendations(self, validation_report: Dict) -> List[str]:
        recommendations = []
        results = validation_report['validation_results']
        
        critical_failures = [r for r in results if r.severity == ValidationSeverity.CRITICAL and not r.passed]
        if critical_failures:
            recommendations.append("🚨 CRITICAL: Fix critical data issues before proceeding with analysis")
            for failure in critical_failures:
                recommendations.append(f"   • {failure.message}")
        
        error_failures = [r for r in results if r.severity == ValidationSeverity.ERROR and not r.passed]
        if error_failures:
            recommendations.append("❌ ERRORS: Address the following data quality issues:")
            for failure in error_failures[:3]:
                recommendations.append(f"   • {failure.message}")
        
        quality_score = validation_report['data_quality_score']
        if quality_score < 0.6:
            recommendations.append("📉 Low data quality score - consider data cleaning pipeline")
        elif quality_score < 0.8:
            recommendations.append("📊 Moderate data quality - review warning-level issues")
        
        completeness_results = [r for r in results if 'completeness' in r.rule_name]
        for result in completeness_results:
            if not result.passed and result.details.get('completeness', 1) < 0.7:
                recommendations.append("📋 Consider imputation strategies for missing data")
                break
        
        outlier_results = [r for r in results if 'outlier' in r.rule_name]
        for result in outlier_results:
            if result.details.get('total_outliers', 0) > 0:
                recommendations.append("📈 Review outliers - they may indicate data quality issues or interesting patterns")
                break
        
        return recommendations
    
    def add_custom_rule(self, rule: ValidationRule):
        self.custom_rules[rule.name] = rule
        logger.info(f"Added custom validation rule: {rule.name}")
    
    def get_validation_history(self, limit: int = 10) -> List[Dict]:
        return self.validation_history[-limit:] if self.validation_history else []
    
    def export_validation_report(self, validation_report: Dict, filepath: str):
        def convert_enums(obj):
            if isinstance(obj, ValidationSeverity):
                return obj.value
            elif isinstance(obj, ValidationResult):
                return {
                    'rule_name': obj.rule_name,
                    'passed': obj.passed,
                    'severity': obj.severity.value,
                    'message': obj.message,
                    'affected_rows': obj.affected_rows,
                    'details': obj.details
                }
            return obj
        
        serializable_report = json.loads(json.dumps(validation_report, default=convert_enums))
        serializable_report['validation_results'] = [
            convert_enums(result) for result in validation_report['validation_results']
        ]
        
        with open(filepath, 'w') as f:
            json.dump(serializable_report, f, indent=2, default=str)
        
        logger.info(f"Validation report exported to {filepath}")

def validate_customer_data(data_source: str, output_report: str = None) -> Dict[str, Any]:
    if data_source.endswith('.csv'):
        df = pd.read_csv(data_source)
    elif data_source.endswith('.xlsx'):
        df = pd.read_excel(data_source)
    else:
        df = data_source
    
    validator = DataValidator()
    report = validator.validate_dataset(df)
    
    if output_report:
        validator.export_validation_report(report, output_report)
        logger.info(f"📊 Validation report saved to {output_report}")
    
    print(f"\n📋 VALIDATION SUMMARY")
    print(f"Data Quality Score: {report['data_quality_score']:.2%}")
    print(f"Rules Passed: {report['summary']['passed']}/{report['summary']['total_rules']}")
    
    if report['recommendations']:
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"  {rec}")
    
    return report