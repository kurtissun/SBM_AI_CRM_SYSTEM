"""
Advanced data cleaning and preprocessing system
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime, timedelta
import json
import re
from sklearn.preprocessing import StandardScaler, LabelEncoder
from core.config import settings
from core.database import get_db

logger = logging.getLogger(__name__)

class AdvancedDataCleaner:
    """
    Production-level data cleaning and preprocessing system
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.cleaning_stats = {}
        self.transformations_applied = []
        
        # Data quality thresholds
        self.min_completeness = self.config.get('min_completeness', 0.7)
        self.max_outlier_ratio = self.config.get('max_outlier_ratio', 0.05)
        
        # Transformation objects
        self.scalers = {}
        self.encoders = {}
        
    def clean_customer_data(self, df: pd.DataFrame, 
                           validation_rules: Dict = None) -> Dict[str, Any]:
        """
        Comprehensive customer data cleaning pipeline
        """
        logger.info(f"Starting data cleaning for {len(df)} records")
        
        original_shape = df.shape
        cleaning_report = {
            'original_shape': original_shape,
            'cleaning_steps': [],
            'data_quality_score': 0.0,
            'warnings': [],
            'transformations': []
        }
        
        # Step 1: Initial data assessment
        quality_assessment = self._assess_data_quality(df)
        cleaning_report['initial_quality'] = quality_assessment
        
        # Step 2: Handle missing values
        df_cleaned, missing_report = self._handle_missing_values(df)
        cleaning_report['cleaning_steps'].append(missing_report)
        
        # Step 3: Remove duplicates
        df_cleaned, duplicate_report = self._remove_duplicates(df_cleaned)
        cleaning_report['cleaning_steps'].append(duplicate_report)
        
        # Step 4: Data type corrections
        df_cleaned, dtype_report = self._correct_data_types(df_cleaned)
        cleaning_report['cleaning_steps'].append(dtype_report)
        
        # Step 5: Handle outliers
        df_cleaned, outlier_report = self._handle_outliers(df_cleaned)
        cleaning_report['cleaning_steps'].append(outlier_report)
        
        # Step 6: Standardize categorical values
        df_cleaned, category_report = self._standardize_categories(df_cleaned)
        cleaning_report['cleaning_steps'].append(category_report)
        
        # Step 7: Feature engineering
        df_cleaned, feature_report = self._engineer_features(df_cleaned)
        cleaning_report['cleaning_steps'].append(feature_report)
        
        # Step 8: Validate business rules
        if validation_rules:
            df_cleaned, validation_report = self._validate_business_rules(df_cleaned, validation_rules)
            cleaning_report['cleaning_steps'].append(validation_report)
        
        # Final quality assessment
        final_quality = self._assess_data_quality(df_cleaned)
        cleaning_report['final_quality'] = final_quality
        cleaning_report['final_shape'] = df_cleaned.shape
        cleaning_report['data_quality_score'] = final_quality['overall_score']
        
        # Records retained
        retention_rate = len(df_cleaned) / len(df) * 100
        cleaning_report['retention_rate'] = retention_rate
        
        logger.info(f"Data cleaning completed. Retention rate: {retention_rate:.1f}%")
        
        return {
            'cleaned_data': df_cleaned,
            'cleaning_report': cleaning_report,
            'transformations': self.transformations_applied
        }
    
    def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Comprehensive data quality assessment
        """
        assessment = {
            'shape': df.shape,
            'completeness': {},
            'consistency': {},
            'validity': {},
            'overall_score': 0.0
        }
        
        # Completeness assessment
        missing_percentages = (df.isnull().sum() / len(df) * 100).to_dict()
        assessment['completeness'] = {
            'missing_percentages': missing_percentages,
            'avg_completeness': 100 - np.mean(list(missing_percentages.values())),
            'columns_with_missing': sum(1 for pct in missing_percentages.values() if pct > 0)
        }
        
        # Consistency assessment
        duplicate_count = df.duplicated().sum()
        assessment['consistency'] = {
            'duplicate_rows': duplicate_count,
            'duplicate_percentage': duplicate_count / len(df) * 100
        }
        
        # Validity assessment (basic checks)
        validity_issues = []
        for col in df.columns:
            if df[col].dtype in ['object']:
                # Check for unusual string patterns
                if df[col].astype(str).str.len().max() > 100:
                    validity_issues.append(f"{col}: Unusually long strings detected")
            elif df[col].dtype in ['int64', 'float64']:
                # Check for outliers using IQR
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
                if outliers > len(df) * 0.1:  # More than 10% outliers
                    validity_issues.append(f"{col}: High number of outliers ({outliers})")
        
        assessment['validity'] = {
            'issues_found': validity_issues,
            'issue_count': len(validity_issues)
        }
        
        # Calculate overall score
        completeness_score = assessment['completeness']['avg_completeness'] / 100
        consistency_score = 1 - (assessment['consistency']['duplicate_percentage'] / 100)
        validity_score = max(0, 1 - (len(validity_issues) / len(df.columns)))
        
        assessment['overall_score'] = (completeness_score + consistency_score + validity_score) / 3
        
        return assessment
    
    def _handle_missing_values(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Handle missing values with intelligent strategies
        """
        df_cleaned = df.copy()
        report = {
            'step': 'handle_missing_values',
            'actions_taken': [],
            'columns_processed': [],
            'rows_affected': 0
        }
        
        initial_missing = df.isnull().sum().sum()
        
        for column in df.columns:
            missing_count = df[column].isnull().sum()
            missing_pct = missing_count / len(df) * 100
            
            if missing_count > 0:
                report['columns_processed'].append(column)
                
                if missing_pct > 50:
                    # Drop columns with >50% missing
                    df_cleaned = df_cleaned.drop(columns=[column])
                    report['actions_taken'].append(f"Dropped {column} (>{missing_pct:.1f}% missing)")
                    
                elif df[column].dtype in ['int64', 'float64']:
                    # Fill numeric columns with median
                    median_val = df[column].median()
                    df_cleaned[column] = df_cleaned[column].fillna(median_val)
                    report['actions_taken'].append(f"Filled {column} with median ({median_val})")
                    
                elif df[column].dtype == 'object':
                    # Fill categorical columns with mode or 'unknown'
                    if not df[column].mode().empty:
                        mode_val = df[column].mode()[0]
                        df_cleaned[column] = df_cleaned[column].fillna(mode_val)
                        report['actions_taken'].append(f"Filled {column} with mode ({mode_val})")
                    else:
                        df_cleaned[column] = df_cleaned[column].fillna('unknown')
                        report['actions_taken'].append(f"Filled {column} with 'unknown'")
        
        final_missing = df_cleaned.isnull().sum().sum()
        report['rows_affected'] = initial_missing - final_missing
        
        return df_cleaned, report
    
    def _remove_duplicates(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Remove duplicate records intelligently
        """
        initial_count = len(df)
        
        # First, try to identify exact duplicates
        df_cleaned = df.drop_duplicates()
        exact_duplicates = initial_count - len(df_cleaned)
        
        report = {
            'step': 'remove_duplicates',
            'exact_duplicates_removed': exact_duplicates,
            'fuzzy_duplicates_removed': 0,
            'total_removed': exact_duplicates
        }
        
        # For customer data, check for potential fuzzy duplicates
        if 'customer_id' in df.columns and 'member_name' in df.columns:
            # Check for same name but different customer_id
            name_groups = df_cleaned.groupby('member_name')
            fuzzy_duplicates = 0
            
            for name, group in name_groups:
                if len(group) > 1 and len(group['customer_id'].unique()) > 1:
                    # Keep the record with the most recent date if available
                    if 'registration_time' in df.columns:
                        df_cleaned = df_cleaned.loc[group['registration_time'].idxmax()]
                        fuzzy_duplicates += len(group) - 1
            
            report['fuzzy_duplicates_removed'] = fuzzy_duplicates
            report['total_removed'] = exact_duplicates + fuzzy_duplicates
        
        return df_cleaned, report
    
    def _correct_data_types(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Correct data types based on content analysis
        """
        df_cleaned = df.copy()
        report = {
            'step': 'correct_data_types',
            'conversions': [],
            'errors': []
        }
        
        for column in df.columns:
            original_dtype = str(df[column].dtype)
            
            # Try to convert string representations of numbers
            if df[column].dtype == 'object':
                # Check if column contains numeric strings
                sample_values = df[column].dropna().astype(str).head(100)
                
                # Check for integer pattern
                if sample_values.str.match(r'^\d+$').all():
                    try:
                        df_cleaned[column] = pd.to_numeric(df_cleaned[column], errors='coerce')
                        report['conversions'].append(f"{column}: {original_dtype} -> numeric")
                    except Exception as e:
                        report['errors'].append(f"{column}: Failed to convert to numeric: {e}")
                
                # Check for float pattern
                elif sample_values.str.match(r'^\d*\.?\d+$').all():
                    try:
                        df_cleaned[column] = pd.to_numeric(df_cleaned[column], errors='coerce')
                        report['conversions'].append(f"{column}: {original_dtype} -> numeric")
                    except Exception as e:
                        report['errors'].append(f"{column}: Failed to convert to numeric: {e}")
                
                # Check for date pattern
                elif sample_values.str.match(r'\d{4}-\d{2}-\d{2}').any():
                    try:
                        df_cleaned[column] = pd.to_datetime(df_cleaned[column], errors='coerce')
                        report['conversions'].append(f"{column}: {original_dtype} -> datetime")
                    except Exception as e:
                        report['errors'].append(f"{column}: Failed to convert to datetime: {e}")
        
        return df_cleaned, report
    
    def _handle_outliers(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Detect and handle outliers using multiple methods
        """
        df_cleaned = df.copy()
        report = {
            'step': 'handle_outliers',
            'columns_processed': [],
            'outliers_detected': {},
            'outliers_handled': {}
        }
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for column in numeric_columns:
            if column in ['customer_id', 'id']:  # Skip ID columns
                continue
                
            # IQR method for outlier detection
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = ((df[column] < lower_bound) | (df[column] > upper_bound))
            outlier_count = outliers.sum()
            
            if outlier_count > 0:
                report['columns_processed'].append(column)
                report['outliers_detected'][column] = outlier_count
                
                outlier_ratio = outlier_count / len(df)
                
                if outlier_ratio < self.max_outlier_ratio:
                    # Cap outliers to bounds
                    df_cleaned.loc[df_cleaned[column] < lower_bound, column] = lower_bound
                    df_cleaned.loc[df_cleaned[column] > upper_bound, column] = upper_bound
                    report['outliers_handled'][column] = f"Capped {outlier_count} outliers"
                else:
                    # Too many outliers, might be legitimate data variation
                    report['outliers_handled'][column] = f"Too many outliers ({outlier_ratio:.1%}), kept as-is"
        
        return df_cleaned, report
    
    def _standardize_categories(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Standardize categorical values
        """
        df_cleaned = df.copy()
        report = {
            'step': 'standardize_categories',
            'standardizations': [],
            'encodings': []
        }
        
        # Predefined standardizations for common columns
        standardizations = {
            'sex': {'女': 'female', '男': 'male', 'F': 'female', 'M': 'male'},
            'gender': {'女': 'female', '男': 'male', 'F': 'female', 'M': 'male'},
            'expanding_type_name': {'到店': 'in_store', '外拓': 'outreach'},
            'expanding_channel_name': {
                '支付宝': 'alipay',
                '微信': 'wechat', 
                '现金': 'cash',
                '银行卡': 'bank_card'
            }
        }
        
        for column in df.columns:
            if df[column].dtype == 'object':
                # Apply predefined standardizations
                if column in standardizations:
                    mapping = standardizations[column]
                    df_cleaned[column] = df_cleaned[column].map(mapping).fillna(df_cleaned[column])
                    report['standardizations'].append(f"{column}: Applied predefined mapping")
                
                # Clean string values
                df_cleaned[column] = (df_cleaned[column]
                                    .astype(str)
                                    .str.strip()
                                    .str.lower()
                                    .replace('nan', np.nan))
                
                # Encode high-cardinality categorical variables
                unique_count = df_cleaned[column].nunique()
                if 2 <= unique_count <= 20:  # Reasonable range for encoding
                    encoder = LabelEncoder()
                    valid_mask = df_cleaned[column].notna()
                    
                    if valid_mask.sum() > 0:
                        encoded_values = encoder.fit_transform(df_cleaned.loc[valid_mask, column])
                        df_cleaned.loc[valid_mask, f'{column}_encoded'] = encoded_values
                        
                        # Store encoder for future use
                        self.encoders[column] = encoder
                        report['encodings'].append(f"{column}: Label encoded to {column}_encoded")
        
        return df_cleaned, report
    
    def _engineer_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Create new features from existing data
        """
        df_cleaned = df.copy()
        report = {
            'step': 'feature_engineering',
            'features_created': [],
            'features_failed': []
        }
        
        try:
            # Age-based features
            if 'age' in df.columns:
                df_cleaned['age_group'] = pd.cut(
                    df_cleaned['age'], 
                    bins=[0, 18, 25, 35, 50, 65, 100],
                    labels=['minor', 'young_adult', 'adult', 'middle_aged', 'mature', 'senior']
                )
                report['features_created'].append('age_group: Categorical age groups')
                
                df_cleaned['is_senior'] = (df_cleaned['age'] >= 60).astype(int)
                report['features_created'].append('is_senior: Binary senior indicator')
        
        except Exception as e:
            report['features_failed'].append(f'age_features: {e}')
        
        try:
            # Rating-based features
            if 'rating_id' in df.columns:
                df_cleaned['high_rating'] = (df_cleaned['rating_id'] >= 4).astype(int)
                report['features_created'].append('high_rating: Binary high rating indicator')
                
                df_cleaned['rating_squared'] = df_cleaned['rating_id'] ** 2
                report['features_created'].append('rating_squared: Squared rating for non-linear effects')
        
        except Exception as e:
            report['features_failed'].append(f'rating_features: {e}')
        
        try:
            # Date-based features
            date_columns = df_cleaned.select_dtypes(include=['datetime64']).columns
            for date_col in date_columns:
                df_cleaned[f'{date_col}_year'] = df_cleaned[date_col].dt.year
                df_cleaned[f'{date_col}_month'] = df_cleaned[date_col].dt.month
                df_cleaned[f'{date_col}_dayofweek'] = df_cleaned[date_col].dt.dayofweek
                
                report['features_created'].append(f'{date_col}_temporal: Year, month, day of week')
        
        except Exception as e:
            report['features_failed'].append(f'date_features: {e}')
        
        try:
            # Interaction features
            if 'age' in df.columns and 'rating_id' in df.columns:
                df_cleaned['age_rating_interaction'] = df_cleaned['age'] * df_cleaned['rating_id']
                report['features_created'].append('age_rating_interaction: Age × Rating interaction')
        
        except Exception as e:
            report['features_failed'].append(f'interaction_features: {e}')
        
        return df_cleaned, report
    
    def _validate_business_rules(self, df: pd.DataFrame, 
                                validation_rules: Dict) -> Tuple[pd.DataFrame, Dict]:
        """
        Validate data against business rules
        """
        df_cleaned = df.copy()
        report = {
            'step': 'validate_business_rules',
            'rules_applied': [],
            'violations_found': [],
            'rows_filtered': 0
        }
        
        initial_count = len(df_cleaned)
        
        for rule_name, rule_config in validation_rules.items():
            try:
                column = rule_config.get('column')
                rule_type = rule_config.get('type')
                
                if rule_type == 'range':
                    min_val = rule_config.get('min')
                    max_val = rule_config.get('max')
                    
                    if column in df_cleaned.columns:
                        violations = ((df_cleaned[column] < min_val) | 
                                    (df_cleaned[column] > max_val))
                        violation_count = violations.sum()
                        
                        if violation_count > 0:
                            df_cleaned = df_cleaned[~violations]
                            report['violations_found'].append(
                                f"{rule_name}: {violation_count} rows outside range [{min_val}, {max_val}]"
                            )
                
                elif rule_type == 'allowed_values':
                    allowed = rule_config.get('values', [])
                    
                    if column in df_cleaned.columns:
                        violations = ~df_cleaned[column].isin(allowed)
                        violation_count = violations.sum()
                        
                        if violation_count > 0:
                            df_cleaned = df_cleaned[~violations]
                            report['violations_found'].append(
                                f"{rule_name}: {violation_count} rows with disallowed values"
                            )
                
                elif rule_type == 'not_null':
                    if column in df_cleaned.columns:
                        violations = df_cleaned[column].isnull()
                        violation_count = violations.sum()
                        
                        if violation_count > 0:
                            df_cleaned = df_cleaned[~violations]
                            report['violations_found'].append(
                                f"{rule_name}: {violation_count} rows with null values"
                            )
                
                report['rules_applied'].append(rule_name)
                
            except Exception as e:
                report['violations_found'].append(f"{rule_name}: Rule validation failed: {e}")
        
        final_count = len(df_cleaned)
        report['rows_filtered'] = initial_count - final_count
        
        return df_cleaned, report
    
    def save_cleaning_config(self, filepath: str):
        """
        Save cleaning configuration for reproducibility
        """
        config = {
            'transformations_applied': self.transformations_applied,
            'encoders': {k: v.classes_.tolist() for k, v in self.encoders.items()},
            'cleaning_stats': self.cleaning_stats,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Cleaning configuration saved to {filepath}")
    
    def load_cleaning_config(self, filepath: str):
        """
        Load cleaning configuration for consistent preprocessing
        """
        with open(filepath, 'r') as f:
            config = json.load(f)
        
        self.transformations_applied = config.get('transformations_applied', [])
        self.cleaning_stats = config.get('cleaning_stats', {})
        
        # Rebuild encoders
        for col, classes in config.get('encoders', {}).items():
            encoder = LabelEncoder()
            encoder.classes_ = np.array(classes)
            self.encoders[col] = encoder
        
        logger.info(f"Cleaning configuration loaded from {filepath}")

# Convenience function for quick cleaning
def clean_customer_data(input_file: str, output_file: str, 
                       validation_rules: Dict = None) -> Dict[str, Any]:
    """
    Quick function to clean customer data from file
    """
    # Load data
    if input_file.endswith('.csv'):
        df = pd.read_csv(input_file)
    elif input_file.endswith('.xlsx'):
        df = pd.read_excel(input_file)
    else:
        raise ValueError("Unsupported file format. Use CSV or Excel.")
    
    # Clean data
    cleaner = AdvancedDataCleaner()
    result = cleaner.clean_customer_data(df, validation_rules)
    
    # Save cleaned data
    result['cleaned_data'].to_csv(output_file, index=False)
    
    # Save cleaning report
    report_file = output_file.replace('.csv', '_cleaning_report.json')
    with open(report_file, 'w') as f:
        json.dump(result['cleaning_report'], f, indent=2, default=str)
    
    logger.info(f"✅ Cleaned data saved to {output_file}")
    logger.info(f"📊 Cleaning report saved to {report_file}")
    
    return result