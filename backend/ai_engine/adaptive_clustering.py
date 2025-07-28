"""
Advanced adaptive clustering system for customer segmentation
"""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.manifold import TSNE
import joblib
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class AdaptiveClustering:
    """
    Advanced clustering engine that automatically determines optimal clusters
    and adapts to seasonal patterns and business context
    """

    
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.max_clusters = self.config.get('max_clusters', 20)
        self.min_cluster_size = self.config.get('min_cluster_size', 10)
        self.random_state = self.config.get('random_state', 42)
        
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=0.95)  # Keep 95% variance
        self.best_model = None
        self.cluster_profiles = {}
        self.feature_importance = {}

    def enable_hyper_personalization(self, customer_data: pd.DataFrame) -> Dict[str, Any]:
        from .hyper_personalization import hyper_personalization_engine
        personalization_results = {
        "customers_processed": 0,
        "profiles_created": 0,
        "personalization_enabled": True,
        "summary": {}
        }
    
        for _, customer in customer_data.iterrows():
            try:
                # Create individual profile
                profile = hyper_personalization_engine.create_individual_profile(
                    customer['customer_id'],
                    customer.to_dict()
                )
            
                personalization_results["profiles_created"] += 1
            
            except Exception as e:
                logger.error(f"Failed to create profile for {customer['customer_id']}: {e}")
        
            personalization_results["customers_processed"] += 1
    
        personalization_results["summary"] = {
            "success_rate": personalization_results["profiles_created"] / personalization_results["customers_processed"] * 100,
            "ready_for_hyper_personalization": True
        }
        return personalization_results

    
        
    def prepare_features(self, df: pd.DataFrame, seasonal_weights: Dict = None) -> np.ndarray:
        """
        Prepare and engineer features for clustering
        """
        # Base features
        features = df.select_dtypes(include=[np.number]).copy()
        
        # Feature engineering
        if 'age' in features.columns:
            features['age_group'] = pd.cut(features['age'], 
                                         bins=[0, 25, 35, 50, 65, 100], 
                                         labels=[1, 2, 3, 4, 5])
            features['age_group'] = features['age_group'].astype(float)
        
        if 'rating_id' in features.columns:
            features['high_rating'] = (features['rating_id'] >= 4).astype(int)
            features['rating_squared'] = features['rating_id'] ** 2
        
        # Apply seasonal weights if provided
        if seasonal_weights:
            for feature, weight in seasonal_weights.items():
                if feature in features.columns:
                    features[feature] = features[feature] * weight
        
        # Handle missing values
        features = features.fillna(features.mean())
        
        return features.values, features.columns.tolist()
    
    def find_optimal_clusters(self, X: np.ndarray) -> Dict:
        """
        Find optimal number of clusters using multiple metrics
        """
        results = {}
        max_possible_clusters = min(self.max_clusters, len(X) // 2)  # At least 2 points per cluster
        cluster_range = range(2, max(3, max_possible_clusters + 1))
        
        for n_clusters in cluster_range:
            # KMeans
            kmeans = KMeans(n_clusters=n_clusters, random_state=self.random_state, n_init=10)
            labels_kmeans = kmeans.fit_predict(X)
            
            # Calculate metrics
            silhouette = silhouette_score(X, labels_kmeans)
            calinski_harabasz = calinski_harabasz_score(X, labels_kmeans)
            davies_bouldin = davies_bouldin_score(X, labels_kmeans)
            
            results[n_clusters] = {
                'silhouette': silhouette,
                'calinski_harabasz': calinski_harabasz,
                'davies_bouldin': davies_bouldin,
                'model': kmeans,
                'labels': labels_kmeans
            }
        
        # Select best based on composite score
        best_n_clusters = self._select_best_clusters(results)
        return results
    
    def _select_best_clusters(self, results: Dict) -> int:
        """Select best number of clusters based on composite score"""
        scores = {}
        for n_clusters, metrics in results.items():
            # Composite score (higher is better)
            score = (
                metrics['silhouette'] * 0.4 +
                (metrics['calinski_harabasz'] / 1000) * 0.3 -
                metrics['davies_bouldin'] * 0.3
            )
            scores[n_clusters] = score
        
        return max(scores.keys(), key=lambda k: scores[k])
    
    def fit_transform(self, data: pd.DataFrame, seasonal_weights: Dict = None) -> Dict[str, Any]:
        """
        Main method to perform adaptive clustering
        """
        try:
            logger.info(f"Starting adaptive clustering for {len(data)} customers")
            
            # Prepare features
            X, feature_names = self.prepare_features(data, seasonal_weights)
            
            if len(data) < self.min_cluster_size:
                raise ValueError(f"Need at least {self.min_cluster_size} customers for clustering")
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Apply PCA if needed
            if X_scaled.shape[1] > 10:
                X_scaled = self.pca.fit_transform(X_scaled)
            
            # Find optimal clusters
            cluster_results = self.find_optimal_clusters(X_scaled)
            best_n_clusters = self._select_best_clusters(cluster_results)
            
            # Get best model and labels
            best_result = cluster_results[best_n_clusters]
            self.best_model = best_result['model']
            labels = best_result['labels']
            
            # Generate cluster profiles
            cluster_profiles = self._generate_cluster_profiles(data, labels, feature_names)
            
            # Generate insights
            insights = self._generate_insights(data, labels, cluster_profiles)
            
            result = {
                'labels': labels.tolist(),
                'n_clusters': int(best_n_clusters),
                'silhouette_score': float(best_result['silhouette']),
                'algorithm_used': 'adaptive_kmeans',
                'cluster_profiles': self._convert_to_json_serializable(cluster_profiles),
                'transformations': {
                    'features_used': feature_names,
                    'scaling_applied': True,
                    'pca_applied': X_scaled.shape[1] != X.shape[1]
                },
                'insights': self._convert_to_json_serializable(insights)
            }
            
            logger.info(f"Clustering completed: {best_n_clusters} clusters with silhouette score {best_result['silhouette']:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"Clustering failed: {e}")
            raise
    
    def _generate_cluster_profiles(self, data: pd.DataFrame, labels: np.ndarray, feature_names: List[str]) -> Dict:
        """Generate descriptive profiles for each cluster"""
        profiles = {}
        
        for cluster_id in np.unique(labels):
            cluster_data = data[labels == cluster_id]
            
            profile = {
                'size': len(cluster_data),
                'percentage': len(cluster_data) / len(data) * 100,
                'demographics': {}
            }
            
            # Age statistics
            if 'age' in cluster_data.columns:
                profile['demographics']['avg_age'] = float(cluster_data['age'].mean())
                profile['demographics']['age_std'] = float(cluster_data['age'].std())
            
            # Rating statistics  
            if 'rating_id' in cluster_data.columns:
                profile['demographics']['avg_rating'] = float(cluster_data['rating_id'].mean())
                profile['demographics']['rating_std'] = float(cluster_data['rating_id'].std())
            
            # Gender distribution
            if 'gender' in cluster_data.columns:
                profile['demographics']['gender_dist'] = cluster_data['gender'].value_counts().to_dict()
            
            # Channel preferences
            if 'expanding_channel_name' in cluster_data.columns:
                profile['demographics']['channel_pref'] = cluster_data['expanding_channel_name'].value_counts().to_dict()
            
            profiles[cluster_id] = profile
        
        return profiles
    
    def _generate_insights(self, data: pd.DataFrame, labels: np.ndarray, profiles: Dict) -> Dict:
        """Generate business insights for each cluster"""
        insights = {}
        
        for cluster_id, profile in profiles.items():
            cluster_insights = {
                'predicted_value': 'high' if profile['demographics'].get('avg_rating', 0) >= 4.0 else 'medium' if profile['demographics'].get('avg_rating', 0) >= 3.0 else 'low',
                'description': self._get_cluster_description(profile),
                'recommended_actions': self._get_recommended_actions(profile)
            }
            insights[cluster_id] = cluster_insights
        
        return insights
    
    def _get_cluster_description(self, profile: Dict) -> str:
        """Generate human-readable cluster description"""
        avg_age = profile['demographics'].get('avg_age', 0)
        avg_rating = profile['demographics'].get('avg_rating', 0)
        
        age_group = "Young" if avg_age < 35 else "Middle-aged" if avg_age < 50 else "Senior"
        value_tier = "Premium" if avg_rating >= 4.0 else "Regular" if avg_rating >= 3.0 else "Basic"
        
        return f"{age_group} {value_tier} customers"
    
    def _get_recommended_actions(self, profile: Dict) -> List[str]:
        """Generate recommended marketing actions"""
        actions = []
        avg_rating = profile['demographics'].get('avg_rating', 0)
        
        if avg_rating >= 4.0:
            actions.extend(["premium_campaigns", "loyalty_programs", "upselling"])
        elif avg_rating >= 3.0:
            actions.extend(["engagement_campaigns", "satisfaction_surveys"])
        else:
            actions.extend(["retention_campaigns", "value_proposition_improvement"])
        
        return actions
    
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """Predict cluster labels for new data"""
        if self.best_model is None:
            raise ValueError("Model not fitted. Call fit_transform first.")
        
        X, _ = self.prepare_features(data)
        X_scaled = self.scaler.transform(X)
        
        if hasattr(self.pca, 'transform'):
            X_scaled = self.pca.transform(X_scaled)
        
        return self.best_model.predict(X_scaled)
    
    def save_model(self, path: str):
        """Save the trained model"""
        model_data = {
            'best_model': self.best_model,
            'scaler': self.scaler,
            'pca': self.pca,
            'config': self.config
        }
        joblib.dump(model_data, path)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load a trained model"""
        model_data = joblib.load(path)
        self.best_model = model_data['best_model']
        self.scaler = model_data['scaler'] 
        self.pca = model_data['pca']
        self.config = model_data['config']
        logger.info(f"Model loaded from {path}")
    
    def _convert_to_json_serializable(self, obj):
        """Convert numpy types to JSON serializable types"""
        import numpy as np
        
        if isinstance(obj, dict):
            return {k: self._convert_to_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_json_serializable(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj


class SeasonalClusteringManager:
    """Manages seasonal variations in clustering"""
    
    def __init__(self):
        self.seasonal_weights = {
            'spring': {'age': 1.0, 'rating_id': 1.2, 'channel_weight': 0.8},
            'summer': {'age': 0.9, 'rating_id': 1.1, 'channel_weight': 1.0},
            'fall': {'age': 1.1, 'rating_id': 1.0, 'channel_weight': 1.2},
            'winter': {'age': 1.2, 'rating_id': 0.9, 'channel_weight': 1.1}
        }
    
    def get_seasonal_weights(self, season: str) -> Dict[str, float]:
        """Get seasonal weights for clustering"""
        return self.seasonal_weights.get(season, {'age': 1.0, 'rating_id': 1.0, 'channel_weight': 1.0})
    