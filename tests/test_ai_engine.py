import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock

def test_adaptive_clustering_basic(clustering_engine, sample_customer_data):
    result = clustering_engine.fit_transform(sample_customer_data)
    
    assert 'labels' in result
    assert 'n_clusters' in result
    assert 'silhouette_score' in result
    assert 'cluster_profiles' in result
    assert 'insights' in result
    
    assert result['n_clusters'] > 0
    assert len(result['labels']) == len(sample_customer_data)
    assert -1 <= result['silhouette_score'] <= 1

def test_clustering_with_seasonal_weights(clustering_engine, sample_customer_data):
    seasonal_weights = {'age': 1.2, 'rating_id': 0.8}
    result = clustering_engine.fit_transform(sample_customer_data, seasonal_weights)
    
    assert result['n_clusters'] > 0
    assert 'transformations' in result

def test_clustering_save_load(clustering_engine, sample_customer_data, temp_dir):
    result = clustering_engine.fit_transform(sample_customer_data)
    
    model_path = temp_dir / "test_clustering_model.pkl"
    clustering_engine.save_model(str(model_path))
    
    new_engine = AdaptiveClusteringEngine()
    new_engine.load_model(str(model_path))
    
    predictions = new_engine.predict(sample_customer_data.head(10))
    assert len(predictions) == 10

def test_campaign_intelligence_roi_prediction(campaign_engine, sample_campaign_data):
    training_result = campaign_engine.train_roi_predictor(sample_campaign_data)
    
    if training_result['model_trained']:
        campaign_data = {
            'budget': 25000,
            'duration_days': 14,
            'target_segments': 2,
            'seasonal_factor': 1.1
        }
        
        prediction = campaign_engine.predict_campaign_roi(campaign_data)
        
        assert 'predicted_roi' in prediction
        assert 'confidence' in prediction
        assert prediction['predicted_roi'] > 0

def test_campaign_strategy_generation(campaign_engine):
    target_segments = [0, 1, 2]
    budget_range = (10000, 50000)
    
    strategy = campaign_engine.generate_campaign_strategy(
        target_segments, budget_range, "engagement"
    )
    
    assert 'recommended_budget' in strategy
    assert 'target_channels' in strategy
    assert 'timing_strategy' in strategy
    assert 'content_themes' in strategy

@patch('openai.ChatCompletion.create')
def test_campaign_strategy_with_ai_enhancement(mock_openai, campaign_engine):
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"creative_concepts": ["test"], "promotional_ideas": ["test"]}'
    mock_openai.return_value = mock_response
    
    campaign_engine.use_openai = True
    
    strategy = campaign_engine.generate_campaign_strategy([0, 1], (10000, 30000))
    
    assert 'creative_concepts' in strategy or 'recommended_budget' in strategy

def test_insight_generator_comprehensive_analysis():
    from backend.ai_engine.insight_generator import IntelligentInsightGenerator
    
    generator = IntelligentInsightGenerator()
    
    cluster_data = {
        'cluster_profiles': {
            0: {'size': 50, 'percentage': 25.0, 'demographics': {'avg_age': 28.5}},
            1: {'size': 75, 'percentage': 37.5, 'demographics': {'avg_age': 42.1}},
            2: {'size': 75, 'percentage': 37.5, 'demographics': {'avg_age': 35.8}}
        },
        'insights': {
            0: {'predicted_value': 'high', 'description': 'Young professionals'},
            1: {'predicted_value': 'medium', 'description': 'Families'},
            2: {'predicted_value': 'high', 'description': 'Premium shoppers'}
        },
        'silhouette_score': 0.742
    }
    
    insights = generator.generate_comprehensive_insights(cluster_data)
    
    assert 'executive_summary' in insights
    assert 'segment_insights' in insights
    assert 'business_opportunities' in insights
    assert 'campaign_recommendations' in insights
    assert 'action_plan' in insights

def test_clustering_quality_metrics(clustering_engine, sample_customer_data):
    result = clustering_engine.fit_transform(sample_customer_data)
    
    assert result['silhouette_score'] > 0.0
    assert result['n_clusters'] >= 2
    assert result['n_clusters'] <= clustering_engine.max_clusters

def test_clustering_edge_cases(clustering_engine):
    # Test with minimal data
    minimal_data = pd.DataFrame({
        'age': [25, 30],
        'rating_id': [4, 5]
    })
    
    with pytest.raises(ValueError):
        clustering_engine.fit_transform(minimal_data)

def test_campaign_ab_testing():
    from backend.ai_engine.campaign_intelligence import A_B_TestManager
    
    manager = A_B_TestManager()
    
    campaign_base = {'name': 'Base Campaign', 'budget': 10000}
    variations = [
        {'name': 'Variation A', 'budget': 12000},
        {'name': 'Variation B', 'budget': 8000}
    ]
    
    test_id = manager.create_ab_test(campaign_base, variations)
    
    assert test_id in manager.active_tests
    assert len(manager.active_tests[test_id]['variations']) == 2

def test_seasonal_clustering_manager():
    from backend.ai_engine.adaptive_clustering import SeasonalClusteringManager
    
    manager = SeasonalClusteringManager()
    
    spring_weights = manager.get_seasonal_weights('spring')
    winter_weights = manager.get_seasonal_weights('winter')
    
    assert 'age' in spring_weights
    assert 'rating_id' in spring_weights
    assert spring_weights != winter_weights