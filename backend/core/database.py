"""
Database connection and session management
"""
import asyncio
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import redis
import json
import logging
from .config import settings
from contextlib import contextmanager
from typing import Generator

logger = logging.getLogger(__name__)

# SQLAlchemy setup
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Redis setup
redis_client = redis.from_url(settings.REDIS_URL)

# Database Models
class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(String, unique=True, index=True)  # 会员id / id
    name = Column(String)  # Customer name
    email = Column(String)  # Customer email
    age = Column(Integer)  # existing + calculated from birthday
    gender = Column(String)  # 性别 / sex (existing)
    location = Column(String)  # 所在地
    total_spent = Column(Float, default=0.0)  # Total customer spending
    purchase_frequency = Column(Integer, default=0)  # Number of purchases
    last_purchase_date = Column(DateTime)  # Last purchase date
    birthday = Column(DateTime)  # 生日 / birthday
    registration_time = Column(DateTime)  # 注册时间 / reg_date
    membership_level = Column(String)  # 会员等级 (橙卡会员，金卡会员，钻卡会员)
    rating_id = Column(Integer)  # rwting_id
    expanding_type_name = Column(String)  # expanding_type_name
    expanding_channel_name = Column(String)  # expanding_channel_name
    segment_id = Column(String)  # Changed to String to match Segment.segment_id
    
    # Additional fields for mixed format
    member_name = Column(String)  # member_nme
    from_org_id = Column(String)  # from_org_id
    registration_project = Column(String)  # 注册项目
    birth_month = Column(Integer)  # 生日月
    birth_identity = Column(String)  # 出生身份
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Purchase(Base):
    __tablename__ = "purchases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(String, index=True)  # 会员id
    purchase_amount = Column(Float)  # 消费金额
    points_earned = Column(Integer)  # 消费获取积分
    business_type = Column(String)  # 消费业态
    store_name = Column(String)  # 消费店铺
    purchase_time = Column(DateTime)  # 消费时间 (from file data)
    purchase_date = Column(DateTime, default=datetime.utcnow)  # System record date
    created_at = Column(DateTime, default=datetime.utcnow)

class CameraData(Base):
    __tablename__ = "camera_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    visitor_count = Column(Integer)
    demographics = Column(Text)  # JSON string
    emotions = Column(Text)  # JSON string
    dwell_time = Column(Float)
    location_zone = Column(String)

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    campaign_type = Column(String)
    target_audience = Column(Text)  # JSON string
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    budget = Column(Float)
    predicted_roi = Column(Float)
    actual_roi = Column(Float)
    status = Column(String, default="draft")
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Segment(Base):
    __tablename__ = "segments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    segment_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    criteria = Column(Text)  # JSON string
    customer_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_type = Column(String)  # daily, weekly, monthly
    generated_at = Column(DateTime, default=datetime.utcnow)
    data = Column(Text)  # JSON string
    file_path = Column(String)
    status = Column(String, default="generated")

# Database functions

def get_db() -> Generator[Session, None, None]:
    """Get database session with proper context management"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

@contextmanager
def get_db_context():
    """Context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def init_database():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def check_database_connection():
    """Check if database is accessible"""
    try:
        with get_db_context() as db:
            db.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

# Cache functions
class CacheManager:
    def __init__(self):
        self.redis = redis_client
        self.default_ttl = 3600  # 1 hour
    
    def get(self, key: str):
        """Get value from cache"""
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: any, ttl: int = None):
        """Set value in cache"""
        try:
            ttl = ttl or self.default_ttl
            self.redis.setex(key, ttl, json.dumps(value, default=str))
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str):
        """Delete key from cache"""
        try:
            return self.redis.delete(key)
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

cache = CacheManager()