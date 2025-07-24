"""
Configuration management for SBM AI CRM System
"""
import os
from typing import Optional
from pydantic import BaseSettings
import yaml

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/sbm_crm"
    REDIS_URL: str = "redis://localhost:6379"
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI/ML
    MODEL_PATH: str = "./models"
    BATCH_SIZE: int = 32
    MAX_CLUSTERS: int = 20
    MIN_CLUSTER_SIZE: int = 50
    
    # Camera System
    CAMERA_ENDPOINTS: list = [
        "rtsp://camera1.sbm.local/stream",
        "rtsp://camera2.sbm.local/stream"
    ]
    FRAME_RATE: int = 30
    DETECTION_CONFIDENCE: float = 0.7
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/sbm_crm.log"
    
    # External APIs
    OPENAI_API_KEY: Optional[str] = None
    WEATHER_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"

def load_config(config_file: str = None) -> Settings:
    """Load configuration from file or environment"""
    if config_file:
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        return Settings(**config_data)
    return Settings()

# Global settings instance
settings = load_config()