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
from .config import settings

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
    customer_id = Column(String, unique=True, index=True)
    age = Column(Integer)
    gender = Column(String)
    rating_id = Column(Integer)
    expanding_type_name = Column(String)
    expanding_channel_name = Column(String)
    segment_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    name = Column(String, index=True)
    description = Column(Text)
    target_segments = Column(Text)  # JSON string
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    budget = Column(Float)
    predicted_roi = Column(Float)
    actual_roi = Column(Float)
    status = Column(String, default="draft")
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_type = Column(String)  # daily, weekly, monthly
    generated_at = Column(DateTime, default=datetime.utcnow)
    data = Column(Text)  # JSON string
    file_path = Column(String)
    status = Column(String, default="generated")

# Database functions
def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def init_database():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

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