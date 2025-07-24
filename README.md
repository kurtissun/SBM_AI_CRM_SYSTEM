"""
SBM CRM System Management Scripts

This package contains various management scripts for the SBM CRM system:

- setup_database.py: Database initialization and setup
- train_models.py: ML model training and management
- run_etl.py: ETL pipeline execution and scheduling
- backup_system.py: System backup and recovery
- deploy.py: Production deployment automation

Usage:
    python scripts/setup_database.py
    python scripts/train_models.py --generate-synthetic
    python scripts/run_etl.py run
    python scripts/backup_system.py create
    python scripts/deploy.py deploy
"""

__version__ = "1.0.0"
__author__ = "SBM Tech Team"

# ===============================
# FILE: README.md
# LOCATION: README.md
# ACTION: Replace entire empty file
# ===============================

# 🏢 SBM AI CRM System

**Enterprise-grade Customer Relationship Management System powered by Artificial Intelligence**

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)

## 🌟 Overview

The SBM AI CRM System is a comprehensive customer intelligence platform designed for Super Brand Mall, featuring advanced AI-powered customer segmentation, campaign optimization, real-time analytics, and computer vision capabilities for customer behavior analysis.

## ✨ Key Features

### 🤖 AI-Powered Customer Intelligence
- **Adaptive Customer Segmentation**: Automatic clustering with business insights
- **Predictive Analytics**: Customer lifetime value, churn prediction, next purchase
- **Campaign Intelligence**: ROI prediction and optimization recommendations
- **Hyper-Personalization**: Individual customer profiling and targeting

### 📊 Advanced Analytics & Insights
- **Real-time Dashboard**: Live customer and traffic analytics
- **Automated Reporting**: Daily, weekly, monthly business intelligence reports
- **Performance Metrics**: Campaign ROI, customer engagement, conversion tracking
- **Predictive Forecasting**: Revenue and growth projections

### 📹 Computer Vision System
- **Biometric Analysis**: Age, gender, emotion recognition
- **Traffic Monitoring**: Real-time visitor tracking and crowd density
- **Face Recognition**: Customer identification and visit tracking
- **Behavior Analytics**: Dwell time, attention zones, activity patterns

### 🔧 Enterprise Infrastructure
- **Scalable Architecture**: Microservices with Docker deployment
- **Security & Compliance**: RBAC, data encryption, audit trails
- **ETL Pipeline**: Automated data processing and validation
- **API-First Design**: RESTful APIs with comprehensive documentation

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd sbm-ai-crm-system
```

2. **Set up environment**
```bash
# Copy environment template
cp .env.example .env

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

3. **Configure environment variables**
```bash
# Edit .env file with your settings
DATABASE_URL=postgresql://user:password@localhost:5432/sbm_crm
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-key  # Optional
```

4. **Initialize the system**
```bash
# Set up database
python scripts/setup_database.py

# Train initial models
python scripts/train_models.py --generate-synthetic

# Start services
docker-compose up -d
```

5. **Access the system**
- **API Documentation**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8501
- **Health Check**: http://localhost:8000/health

### Demo Credentials

| Role | Username | Password | Permissions |
|------|----------|----------|-------------|
| Admin | `admin` | `admin123` | Full access |
| Marketing Manager | `marketing_manager` | `marketing123` | Campaign management |
| Analyst | `analyst` | `analyst123` | Analytics & reports |
| Viewer | `viewer` | `viewer123` | Read-only access |

## 📁 Project Structure

```
sbm-ai-crm-system/
├── backend/                    # Core application
│   ├── ai_engine/             # AI/ML components
│   │   ├── adaptive_clustering.py
│   │   ├── campaign_intelligence.py
│   │   ├── conversational_ai.py
│   │   ├── economic_simulator.py
│   │   ├── hyper_personalization.py
│   │   └── insight_generator.py
│   ├── api/                   # FastAPI application
│   │   ├── endpoints/         # API endpoints
│   │   ├── auth.py           # Authentication
│   │   └── main.py           # Main application
│   ├── camera_system/         # Computer vision
│   │   ├── biometric_analyzer.py
│   │   ├── cv_models.py
│   │   ├── face_recognition.py
│   │   └── traffic_monitor.py
│   ├── core/                  # Core utilities
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # Database models
│   │   └── security.py       # Security utilities
│   └── data_pipeline/         # ETL pipeline
│       ├── data_cleaner.py
│       ├── data_validator.py
│       └── etl_processor.py
├── config/                    # Configuration files
├── data/                      # Data storage
├── frontend/                  # Frontend dashboard
├── models/                    # ML models
├── scripts/                   # Management scripts
├── tests/                     # Test suite
└── monitoring/               # Monitoring setup
```

## 🔧 API Usage

### Authentication

```python
import requests

# Login to get token
response = requests.post("http://localhost:8000/auth/login", json={
    "username": "admin",
    "password": "admin123"
})
token = response.json()["access_token"]

# Use token in requests
headers = {"Authorization": f"Bearer {token}"}
```

### Customer Segmentation

```python
# Upload customer data for segmentation
files = {"file": open("customer_data.csv", "rb")}
response = requests.post(
    "http://localhost:8000/api/customers/upload",
    files=files,
    headers=headers,
    params={"auto_segment": True}
)

segmentation_results = response.json()
```

### Campaign Optimization

```python
# Create AI-optimized campaign
campaign_data = {
    "name": "Summer Promotion",
    "target_segments": [0, 1, 2],
    "budget": 50000,
    "duration_days": 14,
    "campaign_type": "engagement"
}

response = requests.post(
    "http://localhost:8000/api/campaigns/create",
    json=campaign_data,
    headers=headers,
    params={"ai_optimize": True}
)

campaign_strategy = response.json()
```

### Real-time Analytics

```python
# Get real-time dashboard data
response = requests.get(
    "http://localhost:8000/api/analytics/dashboard/overview",
    headers=headers,
    params={"time_range": "7d"}
)

dashboard_data = response.json()
```

## 🛠️ Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend tests/

# Run specific test categories
pytest tests/test_ai_engine.py -v
pytest tests/test_camera_system.py -v
```

### Code Quality

```bash
# Format code
black backend/ scripts/ tests/

# Lint code
flake8 backend/ scripts/ tests/

# Type checking
mypy backend/
```

### Development Server

```bash
# Start development server with hot reload
uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 8000

# Start development environment
docker-compose -f docker-compose.dev.yml up
```

## 📊 Management Scripts

### Database Management

```bash
# Initialize database
python scripts/setup_database.py

# Check database status
python scripts/setup_database.py --verify
```

### Model Training

```bash
# Train all models with synthetic data
python scripts/train_models.py --generate-synthetic

# Train specific models
python scripts/train_models.py --models clustering campaign_roi

# Train with real data
python scripts/train_models.py --customer-data data/customers.csv
```

### ETL Pipeline

```bash
# Run all ETL pipelines
python scripts/run_etl.py run

# Schedule automated ETL
python scripts/run_etl.py schedule

# Check ETL status
python scripts/run_etl.py status
```

### Backup & Recovery

```bash
# Create full backup
python scripts/backup_system.py create

# List available backups
python scripts/backup_system.py list

# Restore from backup
python scripts/backup_system.py restore --backup-name backup_20241215_143022.tar.gz
```

### Production Deployment

```bash
# Full production deployment
python scripts/deploy.py deploy

# Run health checks
python scripts/deploy.py health-check

# Rollback deployment
python scripts/deploy.py rollback
```

## 🔍 Monitoring & Observability

### Health Monitoring

- **Health Check**: `GET /health`
- **System Status**: `GET /api/system/status`
- **Metrics**: Prometheus metrics at `/metrics`

### Logging

```bash
# View application logs
docker-compose logs -f sbm-api

# View all service logs
docker-compose logs -f
```

### Performance Monitoring

- **Grafana Dashboard**: http://localhost:3000
- **Prometheus Metrics**: http://localhost:9090

## 🔒 Security

### Authentication & Authorization

- **JWT-based authentication** with role-based access control
- **API rate limiting** to prevent abuse
- **Data encryption** for sensitive information
- **Audit logging** for compliance

### Data Privacy

- **GDPR compliance** with data anonymization
- **Right to deletion** for customer data
- **Encrypted backups** and secure storage

## 📈 Performance

### Scalability

- **Horizontal scaling** with load balancers
- **Database connection pooling** for efficiency
- **Redis caching** for improved response times
- **Background job processing** with Celery

### Optimization

- **Model inference caching** for faster predictions
- **Database indexing** for query optimization
- **CDN integration** for static assets
- **Compression** for API responses

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

### Code Standards

- Follow PEP 8 for Python code
- Add type hints for all functions
- Write comprehensive tests
- Update documentation

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation

- **API Documentation**: Available at `/docs` when running
- **Architecture Guide**: See `docs/architecture.md`
- **Deployment Guide**: See `docs/deployment.md`

### Getting Help

- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions
- **Email**: contact@sbm-tech.com

### Enterprise Support

For enterprise support, custom deployments, and consulting services, contact our team at enterprise@sbm-tech.com.

---

**Built with ❤️ by kurtissun**