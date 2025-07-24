
"""
Model training script for ML and CV models
"""
import sys
import os
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
from datetime import datetime
import joblib
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.ai_engine.adaptive_clustering import AdaptiveClusteringEngine
from backend.ai_engine.campaign_intelligence import CampaignIntelligenceEngine
from backend.core.database import SessionLocal, Customer, Campaign
from backend.data_pipeline.data_cleaner import AdvancedDataCleaner
from backend.data_pipeline.data_validator import DataValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_synthetic_customer_data(n_samples: int = 1000) -> pd.DataFrame:
    """Generate synthetic customer data for training"""
    logger.info(f"Generating {n_samples} synthetic customer records...")
    
    np.random.seed(42)
    
    # Generate realistic customer data
    data = {
        'customer_id': [f'CUST{i+1:04d}' for i in range(n_samples)],
        'age': np.random.normal(35, 12, n_samples).astype(int).clip(18, 80),
        'sex': np.random.choice(['male', 'female'], n_samples),
        'rating_id': np.random.choice([1, 2, 3, 4, 5], n_samples, p=[0.1, 0.15, 0.3, 0.35, 0.1]),
        'expanding_type_name': np.random.choice(['到店', '外拓'], n_samples, p=[0.7, 0.3]),
        'expanding_channel_name': np.random.choice(['支付宝', '微信', '现金', '银行卡'], n_samples, p=[0.4, 0.35, 0.15, 0.1])
    }
    
    # Add some realistic patterns
    df = pd.DataFrame(data)
    
    # Younger people more likely to use digital payments
    young_mask = df['age'] < 30
    df.loc[young_mask, 'expanding_channel_name'] = np.random.choice(['支付宝', '微信'], young_mask.sum(), p=[0.6, 0.4])
    
    # Older people more likely to use cash/cards
    old_mask = df['age'] > 50
    df.loc[old_mask, 'expanding_channel_name'] = np.random.choice(['现金', '银行卡'], old_mask.sum(), p=[0.6, 0.4])
    
    logger.info("✅ Synthetic data generated successfully")
    return df

def generate_synthetic_campaign_data(n_samples: int = 200) -> pd.DataFrame:
    """Generate synthetic campaign data for training"""
    logger.info(f"Generating {n_samples} synthetic campaign records...")
    
    np.random.seed(42)
    
    data = {
        'campaign_id': [f'CAMP{i+1:04d}' for i in range(n_samples)],
        'budget': np.random.lognormal(10, 0.5, n_samples).clip(5000, 500000),
        'duration_days': np.random.randint(3, 90, n_samples),
        'target_segments': np.random.randint(1, 5, n_samples),
        'seasonal_factor': np.random.uniform(0.8, 1.3, n_samples),
        'channel_count': np.random.randint(1, 6, n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Generate ROI based on realistic factors
    base_roi = 1.5
    budget_factor = np.where(df['budget'] > 50000, 0.2, -0.1)  # Higher budget = slightly better ROI
    duration_factor = np.where(df['duration_days'] > 14, 0.3, -0.2)  # Longer campaigns = better ROI
    seasonal_factor = (df['seasonal_factor'] - 1) * 2  # Seasonal boost
    channel_factor = (df['channel_count'] - 3) * 0.1  # More channels = better reach
    
    df['actual_roi'] = (base_roi + budget_factor + duration_factor + seasonal_factor + channel_factor + 
                       np.random.normal(0, 0.3, n_samples)).clip(0.5, 5.0)
    
    logger.info("✅ Synthetic campaign data generated successfully")
    return df

def load_real_data(data_path: str) -> pd.DataFrame:
    """Load real customer data from file"""
    logger.info(f"Loading data from {data_path}...")
    
    try:
        if data_path.endswith('.csv'):
            df = pd.read_csv(data_path)
        elif data_path.endswith('.xlsx'):
            df = pd.read_excel(data_path)
        else:
            raise ValueError("Unsupported file format. Use CSV or Excel.")
        
        logger.info(f"✅ Loaded {len(df)} records from {data_path}")
        return df
        
    except Exception as e:
        logger.error(f"❌ Failed to load data: {e}")
        raise

def train_clustering_model(customer_data: pd.DataFrame, save_path: str = None) -> dict:
    """Train customer segmentation model"""
    logger.info("🎯 Training customer clustering model...")
    
    try:
        # Clean and validate data
        cleaner = AdvancedDataCleaner()
        cleaning_result = cleaner.clean_customer_data(customer_data)
        clean_data = cleaning_result['cleaned_data']
        
        validator = DataValidator()
        validation_result = validator.validate_dataset(clean_data)
        
        if validation_result['data_quality_score'] < 0.7:
            logger.warning(f"⚠️ Data quality score is low: {validation_result['data_quality_score']:.2f}")
        
        # Train clustering model
        clustering_engine = AdaptiveClusteringEngine({
            'max_clusters': 8,
            'min_cluster_size': 20
        })
        
        clustering_result = clustering_engine.fit_transform(clean_data)
        
        # Save model
        if save_path is None:
            save_path = "models/ml_models/adaptive_clustering_v1.pkl"
        
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        clustering_engine.save_model(save_path)
        
        logger.info(f"✅ Clustering model trained successfully")
        logger.info(f"   - Clusters: {clustering_result['n_clusters']}")
        logger.info(f"   - Silhouette score: {clustering_result['silhouette_score']:.3f}")
        logger.info(f"   - Model saved to: {save_path}")
        
        return {
            'model_type': 'clustering',
            'n_clusters': clustering_result['n_clusters'],
            'silhouette_score': clustering_result['silhouette_score'],
            'algorithm': clustering_result['algorithm_used'],
            'save_path': save_path,
            'training_samples': len(clean_data)
        }
        
    except Exception as e:
        logger.error(f"❌ Clustering model training failed: {e}")
        raise

def train_campaign_roi_model(campaign_data: pd.DataFrame, save_path: str = None) -> dict:
    """Train campaign ROI prediction model"""
    logger.info("📊 Training campaign ROI prediction model...")
    
    try:
        # Prepare campaign intelligence engine
        campaign_engine = CampaignIntelligenceEngine()
        
        # Train ROI predictor
        training_result = campaign_engine.train_roi_predictor(campaign_data)
        
        if not training_result['model_trained']:
            raise ValueError("Failed to train ROI predictor")
        
        # Save model
        if save_path is None:
            save_path = "models/ml_models/campaign_roi_predictor_v1"
        
        Path(save_path + "_roi_predictor.pkl").parent.mkdir(parents=True, exist_ok=True)
        campaign_engine.save_models(save_path)
        
        logger.info(f"✅ Campaign ROI model trained successfully")
        logger.info(f"   - R² score: {training_result['test_score']:.3f}")
        logger.info(f"   - MSE: {training_result['mse']:.3f}")
        logger.info(f"   - Features: {len(training_result['features_used'])}")
        logger.info(f"   - Model saved to: {save_path}")
        
        return {
            'model_type': 'campaign_roi',
            'r2_score': training_result['test_score'],
            'mse': training_result['mse'],
            'features_used': training_result['features_used'],
            'save_path': save_path,
            'training_samples': len(campaign_data)
        }
        
    except Exception as e:
        logger.error(f"❌ Campaign ROI model training failed: {e}")
        raise

def train_churn_prediction_model(customer_data: pd.DataFrame, save_path: str = None) -> dict:
    """Train customer churn prediction model"""
    logger.info("🔄 Training customer churn prediction model...")
    
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, classification_report
        from sklearn.preprocessing import LabelEncoder
        
        # Prepare features
        features = customer_data[['age', 'rating_id']].copy()
        
        # Encode categorical features
        if 'sex' in customer_data.columns:
            le_gender = LabelEncoder()
            features['gender_encoded'] = le_gender.fit_transform(customer_data['sex'].fillna('unknown'))
        
        # Create synthetic churn labels (for demo - in reality this would be based on actual churn data)
        # Lower rating = higher churn probability
        churn_probability = (5 - customer_data['rating_id']) / 4
        y = np.random.binomial(1, churn_probability)
        
        # Train model
        X_train, X_test, y_train, y_test = train_test_split(features, y, test_size=0.2, random_state=42)
        
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Save model
        if save_path is None:
            save_path = "models/ml_models/churn_predictor_v1.pkl"
        
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            'model': model,
            'features': list(features.columns),
            'label_encoders': {'gender': le_gender if 'sex' in customer_data.columns else None}
        }, save_path)
        
        logger.info(f"✅ Churn prediction model trained successfully")
        logger.info(f"   - Accuracy: {accuracy:.3f}")
        logger.info(f"   - Features: {list(features.columns)}")
        logger.info(f"   - Model saved to: {save_path}")
        
        return {
            'model_type': 'churn_prediction',
            'accuracy': accuracy,
            'features': list(features.columns),
            'save_path': save_path,
            'training_samples': len(X_train)
        }
        
    except Exception as e:
        logger.error(f"❌ Churn prediction model training failed: {e}")
        raise

def update_model_registry(training_results: list):
    """Update model registry with new training results"""
    logger.info("📝 Updating model registry...")
    
    try:
        registry_path = "models/model_registry.json"
        
        # Load existing registry or create new one
        if Path(registry_path).exists():
            import json
            with open(registry_path, 'r') as f:
                registry = json.load(f)
        else:
            registry = {"model_registry": {"version": "1.0", "ml_models": {}}}
        
        # Update with new training results
        for result in training_results:
            model_name = f"{result['model_type']}_v1"
            registry["model_registry"]["ml_models"][model_name] = {
                "file_path": result['save_path'],
                "version": "1.0",
                "algorithm": result.get('algorithm', result['model_type']),
                "created_date": datetime.now().isoformat(),
                "performance_metrics": {k: v for k, v in result.items() 
                                     if k not in ['model_type', 'save_path']},
                "status": "active",
                "training_date": datetime.now().isoformat()
            }
        
        # Save updated registry
        Path(registry_path).parent.mkdir(parents=True, exist_ok=True)
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=2)
        
        logger.info(f"✅ Model registry updated with {len(training_results)} models")
        
    except Exception as e:
        logger.error(f"❌ Failed to update model registry: {e}")

def main():
    """Main training function"""
    parser = argparse.ArgumentParser(description="Train ML models for SBM CRM system")
    parser.add_argument("--customer-data", help="Path to customer data file")
    parser.add_argument("--campaign-data", help="Path to campaign data file")
    parser.add_argument("--generate-synthetic", action="store_true", help="Generate synthetic data for training")
    parser.add_argument("--models", nargs="+", choices=["clustering", "campaign_roi", "churn"], 
                       default=["clustering", "campaign_roi", "churn"], help="Models to train")
    parser.add_argument("--save-dir", default="models/ml_models", help="Directory to save models")
    
    args = parser.parse_args()
    
    logger.info("🚀 Starting model training...")
    
    training_results = []
    
    try:
        # Load or generate customer data
        if args.customer_data:
            customer_data = load_real_data(args.customer_data)
        elif args.generate_synthetic:
            customer_data = generate_synthetic_customer_data(1000)
        else:
            # Try to load from database
            logger.info("Loading customer data from database...")
            with SessionLocal() as db:
                customers = db.query(Customer).all()
                if not customers:
                    logger.warning("No customer data in database, generating synthetic data...")
                    customer_data = generate_synthetic_customer_data(1000)
                else:
                    customer_data = pd.DataFrame([{
                        'customer_id': c.customer_id,
                        'age': c.age,
                        'sex': c.gender,
                        'rating_id': c.rating_id,
                        'expanding_type_name': c.expanding_type_name,
                        'expanding_channel_name': c.expanding_channel_name
                    } for c in customers])
        
        # Load or generate campaign data
        if args.campaign_data:
            campaign_data = load_real_data(args.campaign_data)
        elif args.generate_synthetic:
            campaign_data = generate_synthetic_campaign_data(200)
        else:
            # Try to load from database
            logger.info("Loading campaign data from database...")
            with SessionLocal() as db:
                campaigns = db.query(Campaign).filter(Campaign.actual_roi.isnot(None)).all()
                if not campaigns:
                    logger.warning("No campaign data in database, generating synthetic data...")
                    campaign_data = generate_synthetic_campaign_data(200)
                else:
                    campaign_data = pd.DataFrame([{
                        'budget': c.budget,
                        'duration_days': (c.end_date - c.start_date).days if c.end_date and c.start_date else 14,
                        'actual_roi': c.actual_roi,
                        'predicted_roi': c.predicted_roi,
                        'status': c.status
                    } for c in campaigns])
        
        # Train models
        if "clustering" in args.models:
            result = train_clustering_model(customer_data, f"{args.save_dir}/adaptive_clustering_v1.pkl")
            training_results.append(result)
        
        if "campaign_roi" in args.models:
            result = train_campaign_roi_model(campaign_data, f"{args.save_dir}/campaign_roi_predictor_v1")
            training_results.append(result)
        
        if "churn" in args.models:
            result = train_churn_prediction_model(customer_data, f"{args.save_dir}/churn_predictor_v1.pkl")
            training_results.append(result)
        
        # Update model registry
        update_model_registry(training_results)
        
        logger.info("🎉 Model training completed successfully!")
        logger.info(f"   - Trained {len(training_results)} models")
        for result in training_results:
            logger.info(f"   - {result['model_type']}: {result['save_path']}")
        
    except Exception as e:
        logger.error(f"❌ Model training failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

    