import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil
import sys

sys.path.append(str(Path(__file__).parent.parent))

from backend.core.database import Base, engine, SessionLocal
from backend.core.config import settings
from backend.ai_engine.adaptive_clustering import AdaptiveClusteringEngine
from backend.ai_engine.campaign_intelligence import CampaignIntelligenceEngine
from backend.data_pipeline.data_cleaner import AdvancedDataCleaner
from backend.data_pipeline.data_validator import DataValidator

@pytest.fixture(scope="session")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(test_db):
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture
def sample_customer_data():
    np.random.seed(42)
    n_customers = 100
    
    data = {
        'customer_id': [f'CUST{i:03d}' for i in range(1, n_customers + 1)],
        'age': np.random.randint(18, 80, n_customers),
        'sex': np.random.choice(['男', '女'], n_customers),
        'rating_id': np.random.randint(1, 6, n_customers),
        'expanding_type_name': np.random.choice(['到店', '外拓'], n_customers),
        'expanding_channel_name': np.random.choice(['支付宝', '微信', '现金'], n_customers)
    }
    
    return pd.DataFrame(data)

@pytest.fixture
def sample_campaign_data():
    np.random.seed(42)
    n_campaigns = 50
    
    data = {
        'campaign_id': [f'CAMP{i:03d}' for i in range(1, n_campaigns + 1)],
        'budget': np.random.uniform(5000, 100000, n_campaigns),
        'duration_days': np.random.randint(3, 60, n_campaigns),
        'target_segments': np.random.randint(1, 4, n_campaigns),
        'actual_roi': np.random.uniform(0.5, 3.0, n_campaigns),
        'status': ['completed'] * n_campaigns
    }
    
    return pd.DataFrame(data)

@pytest.fixture
def clustering_engine():
    return AdaptiveClusteringEngine()

@pytest.fixture
def campaign_engine():
    return CampaignIntelligenceEngine()

@pytest.fixture
def data_cleaner():
    return AdvancedDataCleaner()

@pytest.fixture
def data_validator():
    return DataValidator()

@pytest.fixture
def temp_dir():
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)

@pytest.fixture
def sample_csv_file(sample_customer_data, temp_dir):
    csv_path = temp_dir / "test_customers.csv"
    sample_customer_data.to_csv(csv_path, index=False)
    return csv_path

@pytest.fixture
def corrupted_customer_data():
    data = {
        'customer_id': ['CUST001', 'CUST002', None, 'CUST004'],
        'age': [25, -5, 150, 30],
        'sex': ['男', '女', 'unknown', '男'],
        'rating_id': [4, 6, 3, None],
        'expanding_type_name': ['到店', '外拓', '到店', '外拓'],
        'expanding_channel_name': ['支付宝', '微信', None, '现金']
    }
    
    return pd.DataFrame(data)

@pytest.fixture
def mock_camera_data():
    return {
        'camera_id': 'CAM_001',
        'timestamp': '2024-03-15T10:30:00Z',
        'zone': 'entrance',
        'visitor_count': 15,
        'demographics': {
            'age_distribution': {'young_adult': 5, 'adult': 7, 'middle_aged': 3},
            'gender_distribution': {'male': 8, 'female': 7},
            'emotion_distribution': {'happy': 10, 'neutral': 4, 'focused': 1}
        },
        'crowd_density': 'medium'
    }