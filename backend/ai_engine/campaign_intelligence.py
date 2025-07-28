"""
AI-powered campaign intelligence and optimization system
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
import joblib
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import json
import openai
from core.config import settings

logger = logging.getLogger(__name__)

class CampaignIntelligenceEngine:
    """
    Advanced AI system for campaign optimization and strategy generation
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.roi_predictor = RandomForestRegressor(
            n_estimators=100, 
            random_state=42, 
            max_depth=10
        )
        self.success_classifier = GradientBoostingClassifier(
            n_estimators=100,
            random_state=42
        )
        
        self.label_encoders = {}
        self.is_trained = False
        self.feature_importance = {}
        
        # Initialize OpenAI if API key provided
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.use_openai = True
        else:
            self.use_openai = False
    
    def prepare_campaign_features(self, campaigns_df: pd.DataFrame, 
                                clusters_df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Prepare features for campaign analysis
        """
        features = campaigns_df.copy()
        
        # Time-based features
        if 'start_date' in features.columns:
            features['start_date'] = pd.to_datetime(features['start_date'])
            features['month'] = features['start_date'].dt.month
            features['quarter'] = features['start_date'].dt.quarter
            features['day_of_week'] = features['start_date'].dt.dayofweek
            features['is_weekend'] = features['day_of_week'].isin([5, 6]).astype(int)
        
        # Campaign duration
        if 'end_date' in features.columns and 'start_date' in features.columns:
            features['end_date'] = pd.to_datetime(features['end_date'])
            features['duration_days'] = (features['end_date'] - features['start_date']).dt.days
        
        # Budget per day
        if 'budget' in features.columns and 'duration_days' in features.columns:
            features['budget_per_day'] = features['budget'] / (features['duration_days'] + 1)
        
        # Target segment features
        if clusters_df is not None and 'target_segments' in features.columns:
            # Parse target segments (assuming JSON format)
            for idx, segments in enumerate(features['target_segments']):
                if isinstance(segments, str):
                    try:
                        segment_list = json.loads(segments)
                        features.loc[idx, 'num_target_segments'] = len(segment_list)
                        features.loc[idx, 'primary_segment'] = segment_list[0] if segment_list else 0
                    except:
                        features.loc[idx, 'num_target_segments'] = 1
                        features.loc[idx, 'primary_segment'] = 0
        
        # Encode categorical variables
        categorical_cols = ['status', 'created_by']
        for col in categorical_cols:
            if col in features.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    features[f'{col}_encoded'] = self.label_encoders[col].fit_transform(
                        features[col].fillna('unknown')
                    )
                else:
                    features[f'{col}_encoded'] = self.label_encoders[col].transform(
                        features[col].fillna('unknown')
                    )
        
        return features
    
    def train_roi_predictor(self, campaigns_df: pd.DataFrame) -> Dict:
        """
        Train ROI prediction model
        """
        # Filter campaigns with actual ROI data
        train_data = campaigns_df[campaigns_df['actual_roi'].notna()].copy()
        
        if len(train_data) < 10:
            logger.warning("Insufficient training data for ROI predictor")
            return {'status': 'insufficient_data', 'model_trained': False}
        
        # Prepare features
        features_df = self.prepare_campaign_features(train_data)
        
        # Select numerical features for training
        feature_cols = [
            'budget', 'duration_days', 'budget_per_day', 'month', 'quarter',
            'day_of_week', 'is_weekend', 'num_target_segments', 'primary_segment'
        ]
        
        # Filter available features
        available_features = [col for col in feature_cols if col in features_df.columns]
        
        if not available_features:
            logger.error("No features available for training")
            return {'status': 'no_features', 'model_trained': False}
        
        X = features_df[available_features].fillna(0)
        y = features_df['actual_roi']
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.roi_predictor.fit(X_train, y_train)
        
        # Evaluate
        train_score = self.roi_predictor.score(X_train, y_train)
        test_score = self.roi_predictor.score(X_test, y_test)
        
        # Predictions
        y_pred = self.roi_predictor.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        
        # Feature importance
        self.feature_importance['roi'] = dict(zip(
            available_features, 
            self.roi_predictor.feature_importances_
        ))
        
        result = {
            'status': 'success',
            'model_trained': True,
            'train_score': train_score,
            'test_score': test_score,
            'mse': mse,
            'feature_importance': self.feature_importance['roi'],
            'features_used': available_features
        }
        
        logger.info(f"ROI predictor trained: R² = {test_score:.3f}, MSE = {mse:.3f}")
        return result
    
    def predict_campaign_roi(self, campaign_data: Dict) -> Dict:
        """
        Predict ROI for a campaign
        """
        if not hasattr(self.roi_predictor, 'feature_importances_'):
            return {'error': 'Model not trained', 'predicted_roi': 0}
        
        # Convert to DataFrame
        df = pd.DataFrame([campaign_data])
        features_df = self.prepare_campaign_features(df)
        
        # Use same features as training
        feature_cols = list(self.feature_importance.get('roi', {}).keys())
        X = features_df[feature_cols].fillna(0)
        
        # Predict
        predicted_roi = self.roi_predictor.predict(X)[0]
        
        # Calculate confidence based on feature similarity to training data
        confidence = self._calculate_prediction_confidence(X.iloc[0], 'roi')
        
        return {
            'predicted_roi': float(predicted_roi),
            'confidence': confidence,
            'factors': self._explain_prediction(X.iloc[0], 'roi')
        }
    
    def _calculate_prediction_confidence(self, features: pd.Series, model_type: str) -> float:
        """
        Calculate confidence score for prediction
        """
        # Simple confidence based on feature importance alignment
        importance = self.feature_importance.get(model_type, {})
        
        if not importance:
            return 0.5
        
        # Normalize features and calculate weighted confidence
        confidence = 0.0
        total_importance = sum(importance.values())
        
        for feature, value in features.items():
            if feature in importance:
                # Higher values for important features increase confidence
                feature_confidence = min(1.0, abs(value) / 10)  # Normalize
                weight = importance[feature] / total_importance
                confidence += feature_confidence * weight
        
        return min(1.0, confidence)
    
    def _explain_prediction(self, features: pd.Series, model_type: str) -> List[Dict]:
        """
        Explain prediction factors
        """
        importance = self.feature_importance.get(model_type, {})
        explanations = []
        
        for feature, value in features.items():
            if feature in importance and importance[feature] > 0.1:
                explanations.append({
                    'feature': feature,
                    'value': float(value),
                    'importance': float(importance[feature]),
                    'impact': 'positive' if value > 0 else 'neutral'
                })
        
        return sorted(explanations, key=lambda x: x['importance'], reverse=True)[:5]
    
    def generate_campaign_strategy(self, target_segments: List[int], 
                                 budget_range: Tuple[float, float],
                                 objective: str = "engagement") -> Dict:
        """
        Generate AI-powered campaign strategy
        """
        strategy = {
            'recommended_budget': self._optimize_budget(target_segments, budget_range),
            'target_channels': self._recommend_channels(target_segments),
            'timing_strategy': self._optimize_timing(target_segments),
            'content_themes': self._suggest_content_themes(target_segments, objective),
            'predicted_metrics': {},
            'optimization_tips': []
        }
        
        # Use OpenAI for enhanced strategy if available
        if self.use_openai:
            enhanced_strategy = self._enhance_strategy_with_ai(strategy, target_segments, objective)
            strategy.update(enhanced_strategy)
        
        return strategy
    
    def _optimize_budget(self, target_segments: List[int], 
                        budget_range: Tuple[float, float]) -> Dict:
        """
        Optimize budget allocation
        """
        min_budget, max_budget = budget_range
        
        # Simple optimization based on segment characteristics
        total_segments = len(target_segments)
        base_budget = (min_budget + max_budget) / 2
        
        # Allocate more budget to high-value segments (assuming higher segment IDs = higher value)
        segment_weights = {}
        total_weight = sum(target_segments) if target_segments else 1
        
        for segment in target_segments:
            weight = segment / total_weight if total_weight > 0 else 1 / total_segments
            segment_weights[segment] = weight
        
        budget_allocation = {}
        for segment, weight in segment_weights.items():
            budget_allocation[f'segment_{segment}'] = base_budget * weight
        
        return {
            'total_budget': base_budget,
            'allocation_by_segment': budget_allocation,
            'optimization_strategy': 'weight_by_segment_value'
        }
    
    def _recommend_channels(self, target_segments: List[int]) -> List[str]:
        """
        Recommend marketing channels based on segments
        """
        channel_mapping = {
            0: ['social_media', 'mobile_app', 'influencer'],
            1: ['email', 'wechat', 'in_store'],
            2: ['digital_ads', 'website', 'retargeting'],
            3: ['events', 'experiential', 'partnerships'],
            4: ['traditional_media', 'loyalty_program', 'direct_mail'],
            5: ['flash_sales', 'limited_offers', 'push_notifications']
        }
        
        recommended_channels = set()
        for segment in target_segments:
            channels = channel_mapping.get(segment, ['digital_ads', 'social_media'])
            recommended_channels.update(channels)
        
        return list(recommended_channels)
    
    def _optimize_timing(self, target_segments: List[int]) -> Dict:
        """
        Optimize campaign timing
        """
        # Default timing based on segment characteristics
        timing_preferences = {
            0: {'best_days': ['friday', 'saturday'], 'best_hours': [18, 19, 20, 21]},
            1: {'best_days': ['tuesday', 'wednesday', 'thursday'], 'best_hours': [12, 18, 19]},
            2: {'best_days': ['weekend'], 'best_hours': [10, 11, 14, 15, 16]},
            3: {'best_days': ['friday', 'saturday', 'sunday'], 'best_hours': [11, 12, 13, 14]},
            4: {'best_days': ['monday', 'tuesday', 'wednesday'], 'best_hours': [9, 10, 11, 15, 16]},
            5: {'best_days': ['any'], 'best_hours': [9, 12, 18, 21]}
        }
        
        # Aggregate preferences across segments
        all_best_days = []
        all_best_hours = []
        
        for segment in target_segments:
            prefs = timing_preferences.get(segment, timing_preferences[0])
            all_best_days.extend(prefs['best_days'])
            all_best_hours.extend(prefs['best_hours'])
        
        # Find most common preferences
        from collections import Counter
        day_counts = Counter(all_best_days)
        hour_counts = Counter(all_best_hours)
        
        return {
            'recommended_days': [day for day, count in day_counts.most_common(3)],
            'recommended_hours': [hour for hour, count in hour_counts.most_common(5)],
            'duration_recommendation': '7-14 days',
            'frequency_recommendation': 'every_2_days'
        }
    
    def _suggest_content_themes(self, target_segments: List[int], objective: str) -> List[str]:
        """
        Suggest content themes based on segments and objective
        """
        theme_mapping = {
            'engagement': {
                0: ['tech_innovation', 'lifestyle', 'social_trends'],
                1: ['family_values', 'savings', 'convenience'],
                2: ['luxury', 'experiences', 'exclusivity'],
                3: ['community', 'events', 'entertainment'],
                4: ['quality', 'tradition', 'wellness'],
                5: ['urgency', 'value', 'limited_time']
            },
            'conversion': {
                0: ['innovation', 'early_access', 'tech_features'],
                1: ['family_benefits', 'cost_savings', 'practical_value'],
                2: ['premium_quality', 'status', 'unique_experiences'],
                3: ['social_proof', 'trending', 'popular_choices'],
                4: ['trusted_brands', 'proven_quality', 'long_term_value'],
                5: ['flash_deals', 'instant_savings', 'limited_quantity']
            }
        }
        
        themes = set()
        theme_dict = theme_mapping.get(objective, theme_mapping['engagement'])
        
        for segment in target_segments:
            segment_themes = theme_dict.get(segment, ['general_appeal', 'quality', 'value'])
            themes.update(segment_themes)
        
        return list(themes)
    
    def _enhance_strategy_with_ai(self, base_strategy: Dict, 
                                target_segments: List[int], 
                                objective: str) -> Dict:
        """
        Enhance strategy using OpenAI
        """
        try:
            prompt = f"""
            Create an enhanced marketing campaign strategy for a shopping mall with the following context:
            
            Target Segments: {target_segments}
            Objective: {objective}
            Base Strategy: {json.dumps(base_strategy, indent=2)}
            
            Please provide:
            1. Creative campaign concepts
            2. Specific promotional ideas
            3. Engagement tactics
            4. Success metrics to track
            5. Risk mitigation strategies
            
            Format the response as JSON with keys: creative_concepts, promotional_ideas, engagement_tactics, success_metrics, risk_mitigation.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            
            ai_enhancement = json.loads(response.choices[0].message.content)
            return ai_enhancement
            
        except Exception as e:
            logger.warning(f"OpenAI enhancement failed: {e}")
            return {
                'creative_concepts': ['User-generated content campaigns', 'Interactive experiences'],
                'promotional_ideas': ['Early bird discounts', 'Loyalty point multipliers'],
                'engagement_tactics': ['Social media challenges', 'In-store events'],
                'success_metrics': ['Engagement rate', 'Conversion rate', 'ROI'],
                'risk_mitigation': ['A/B testing', 'Gradual rollout', 'Performance monitoring']
            }
    
    def optimize_ongoing_campaign(self, campaign_id: str, 
                                performance_data: Dict) -> Dict:
        """
        Provide real-time optimization recommendations
        """
        current_roi = performance_data.get('current_roi', 0)
        predicted_roi = performance_data.get('predicted_roi', 0)
        
        optimization = {
            'status': 'analyzing',
            'recommendations': [],
            'priority_actions': [],
            'expected_improvement': 0
        }
        
        # Analyze performance gaps
        roi_gap = predicted_roi - current_roi
        
        if roi_gap > 0.5:  # Significant underperformance
            optimization['recommendations'].extend([
                'Increase budget allocation to high-performing segments',
                'Adjust targeting parameters',
                'Test different creative variations'
            ])
            optimization['priority_actions'].append('budget_reallocation')
        
        elif roi_gap < -0.2:  # Overperforming
            optimization['recommendations'].extend([
                'Scale up successful campaign elements',
                'Expand to similar audience segments',
                'Increase overall budget'
            ])
            optimization['priority_actions'].append('scale_up')
        
        # Analyze engagement metrics
        engagement_rate = performance_data.get('engagement_rate', 0)
        if engagement_rate < 0.03:  # Low engagement
            optimization['recommendations'].extend([
                'Refresh creative content',
                'Adjust posting times',
                'Test different messaging approaches'
            ])
        
        # Calculate expected improvement
        optimization['expected_improvement'] = abs(roi_gap) * 0.3  # Conservative estimate
        
        return optimization
    
    def save_models(self, filepath_base: str):
        """Save trained models"""
        try:
            joblib.dump(self.roi_predictor, f"{filepath_base}_roi_predictor.pkl")
            joblib.dump(self.success_classifier, f"{filepath_base}_success_classifier.pkl")
            joblib.dump(self.label_encoders, f"{filepath_base}_label_encoders.pkl")
            
            metadata = {
                'feature_importance': self.feature_importance,
                'is_trained': self.is_trained,
                'config': self.config
            }
            joblib.dump(metadata, f"{filepath_base}_metadata.pkl")
            
            logger.info(f"Campaign intelligence models saved to {filepath_base}")
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    def load_models(self, filepath_base: str):
        """Load trained models"""
        try:
            self.roi_predictor = joblib.load(f"{filepath_base}_roi_predictor.pkl")
            self.success_classifier = joblib.load(f"{filepath_base}_success_classifier.pkl")
            self.label_encoders = joblib.load(f"{filepath_base}_label_encoders.pkl")
            
            metadata = joblib.load(f"{filepath_base}_metadata.pkl")
            self.feature_importance = metadata['feature_importance']
            self.is_trained = metadata['is_trained']
            self.config = metadata.get('config', {})
            
            logger.info(f"Campaign intelligence models loaded from {filepath_base}")
        except Exception as e:
            logger.error(f"Error loading models: {e}")

class A_B_TestManager:
    """
    Manages A/B testing for campaigns
    """
    
    def __init__(self):
        self.active_tests = {}
        self.test_results = {}
    
    def create_ab_test(self, campaign_base: Dict, variations: List[Dict], 
                      traffic_split: List[float] = None) -> str:
        """
        Create A/B test configuration
        """
        import uuid
        test_id = str(uuid.uuid4())
        
        if traffic_split is None:
            # Equal split
            split_size = 1.0 / (len(variations) + 1)  # +1 for control
            traffic_split = [split_size] * (len(variations) + 1)
        
        test_config = {
            'test_id': test_id,
            'control': campaign_base,
            'variations': variations,
            'traffic_split': traffic_split,
            'status': 'active',
            'start_date': datetime.now(),
            'metrics': {},
            'statistical_significance': False
        }
        
        self.active_tests[test_id] = test_config
        return test_id
    
    def update_test_metrics(self, test_id: str, variant_id: str, metrics: Dict):
        """
        Update metrics for A/B test variant
        """
        if test_id not in self.active_tests:
            return False
        
        if 'metrics' not in self.active_tests[test_id]:
            self.active_tests[test_id]['metrics'] = {}
        
        self.active_tests[test_id]['metrics'][variant_id] = metrics
        
        # Check for statistical significance
        self._check_statistical_significance(test_id)
        
        return True
    
    def _check_statistical_significance(self, test_id: str):
        """
        Check if test results are statistically significant
        """
        # Simplified significance check
        test = self.active_tests[test_id]
        metrics = test.get('metrics', {})
        
        if len(metrics) < 2:
            return False
        
        # Compare conversion rates (simplified)
        conversion_rates = []
        sample_sizes = []
        
        for variant_id, variant_metrics in metrics.items():
            cr = variant_metrics.get('conversion_rate', 0)
            ss = variant_metrics.get('sample_size', 0)
            conversion_rates.append(cr)
            sample_sizes.append(ss)
        
        # Simple significance test (would use proper statistical test in production)
        if all(ss > 100 for ss in sample_sizes):  # Minimum sample size
            max_cr = max(conversion_rates)
            min_cr = min(conversion_rates)
            
            # If difference is > 20% and sample size is sufficient
            if (max_cr - min_cr) / max_cr > 0.2:
                test['statistical_significance'] = True
                test['winning_variant'] = list(metrics.keys())[conversion_rates.index(max_cr)]
    
    def get_test_results(self, test_id: str) -> Dict:
        """
        Get comprehensive test results
        """
        if test_id not in self.active_tests:
            return {'error': 'Test not found'}
        
        test = self.active_tests[test_id]
        
        results = {
            'test_id': test_id,
            'status': test['status'],
            'duration_days': (datetime.now() - test['start_date']).days,
            'statistical_significance': test.get('statistical_significance', False),
            'winning_variant': test.get('winning_variant', None),
            'variant_performance': test.get('metrics', {}),
            'recommendations': []
        }
        
        # Generate recommendations
        if results['statistical_significance']:
            results['recommendations'].append(
                f"Test shows statistical significance. "
                f"Recommend implementing variant: {results['winning_variant']}"
            )
        else:
            results['recommendations'].append(
                "Test has not reached statistical significance. Continue testing or extend duration."
            )
        
        return results