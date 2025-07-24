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
        self.min_cluster_size = self.config.get('min_cluster_size', 50)
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
        cluster_range = range(2, min(self.max_clusters + 1, len(X) // self.min_cluster_size + 1))
        
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
    