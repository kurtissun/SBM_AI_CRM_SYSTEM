
"""
Database setup and initialization script
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.core.database import engine, Base, SessionLocal, Customer, Campaign, CameraData, Report
from backend.core.config import settings
import logging
from datetime import datetime
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """Create all database tables"""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        return False

def check_database_connection():
    """Check if database is accessible"""
    try:
        with SessionLocal() as db:
            db.execute("SELECT 1")
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def seed_sample_data():
    """Seed database with sample data for development"""
    try:
        logger.info("Seeding sample data...")
        
        with SessionLocal() as db:
            # Check if data already exists
            existing_customers = db.query(Customer).count()
            if existing_customers > 0:
                logger.info(f"Database already has {existing_customers} customers, skipping seed")
                return True
            
            # Generate sample customers
            np.random.seed(42)
            customers_data = []
            
            for i in range(100):
                customer = Customer(
                    customer_id=f"CUST{i+1:03d}",
                    age=np.random.randint(18, 80),
                    gender=np.random.choice(['male', 'female']),
                    rating_id=np.random.randint(1, 6),
                    expanding_type_name=np.random.choice(['到店', '外拓']),
                    expanding_channel_name=np.random.choice(['支付宝', '微信', '现金', '银行卡']),
                    segment_id=np.random.randint(0, 6) if np.random.random() > 0.3 else None
                )
                customers_data.append(customer)
            
            db.add_all(customers_data)
            
            # Generate sample campaigns
            campaigns_data = []
            for i in range(20):
                campaign = Campaign(
                    name=f"Campaign {i+1}",
                    description=f"Sample marketing campaign {i+1}",
                    target_segments=f"[{np.random.randint(0, 6)}, {np.random.randint(0, 6)}]",
                    start_date=datetime.now(),
                    budget=np.random.uniform(5000, 100000),
                    predicted_roi=np.random.uniform(1.2, 3.5),
                    actual_roi=np.random.uniform(0.8, 4.0) if np.random.random() > 0.5 else None,
                    status=np.random.choice(['draft', 'active', 'completed', 'paused']),
                    created_by='system'
                )
                campaigns_data.append(campaign)
            
            db.add_all(campaigns_data)
            
            # Generate sample camera data
            camera_data_list = []
            for i in range(50):
                camera_data = CameraData(
                    camera_id=f"CAM_{(i % 5) + 1:03d}",
                    visitor_count=np.random.randint(1, 50),
                    demographics='{"age_avg": 35, "gender_dist": {"male": 0.6, "female": 0.4}}',
                    emotions='{"happy": 0.7, "neutral": 0.2, "focused": 0.1}',
                    dwell_time=np.random.uniform(30, 300),
                    location_zone=np.random.choice(['entrance', 'main_hall', 'food_court', 'retail_north'])
                )
                camera_data_list.append(camera_data)
            
            db.add_all(camera_data_list)
            
            db.commit()
            
        logger.info("✅ Sample data seeded successfully")
        logger.info(f"   - Added {len(customers_data)} customers")
        logger.info(f"   - Added {len(campaigns_data)} campaigns")
        logger.info(f"   - Added {len(camera_data_list)} camera records")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to seed sample data: {e}")
        return False

def setup_indexes():
    """Create database indexes for performance"""
    try:
        logger.info("Setting up database indexes...")
        
        with engine.begin() as conn:
            # Customer indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_customer_segment ON customers(segment_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_customer_rating ON customers(rating_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_customer_created ON customers(created_at)")
            
            # Campaign indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_campaign_status ON campaigns(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_campaign_created ON campaigns(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_campaign_dates ON campaigns(start_date, end_date)")
            
            # Camera data indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_camera_timestamp ON camera_data(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_camera_zone ON camera_data(location_zone)")
            
        logger.info("✅ Database indexes created successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create indexes: {e}")
        return False

def verify_setup():
    """Verify database setup is correct"""
    try:
        logger.info("Verifying database setup...")
        
        with SessionLocal() as db:
            # Check table counts
            customer_count = db.query(Customer).count()
            campaign_count = db.query(Campaign).count()
            camera_count = db.query(CameraData).count()
            
            logger.info(f"   - Customers: {customer_count}")
            logger.info(f"   - Campaigns: {campaign_count}")
            logger.info(f"   - Camera data: {camera_count}")
            
            # Test queries
            high_rating_customers = db.query(Customer).filter(Customer.rating_id >= 4).count()
            active_campaigns = db.query(Campaign).filter(Campaign.status == 'active').count()
            
            logger.info(f"   - High rating customers: {high_rating_customers}")
            logger.info(f"   - Active campaigns: {active_campaigns}")
        
        logger.info("✅ Database verification completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database verification failed: {e}")
        return False

def main():
    """Main setup function"""
    logger.info("🚀 Starting database setup...")
    
    success = True
    
    # Step 1: Check connection
    if not check_database_connection():
        logger.error("Cannot proceed without database connection")
        sys.exit(1)
    
    # Step 2: Create tables
    if not create_tables():
        success = False
    
    # Step 3: Setup indexes
    if not setup_indexes():
        success = False
    
    # Step 4: Seed sample data (only in development)
    if settings.ENVIRONMENT == 'development':
        if not seed_sample_data():
            success = False
    
    # Step 5: Verify setup
    if not verify_setup():
        success = False
    
    if success:
        logger.info("🎉 Database setup completed successfully!")
    else:
        logger.error("❌ Database setup completed with errors")
        sys.exit(1)

if __name__ == "__main__":
    main()