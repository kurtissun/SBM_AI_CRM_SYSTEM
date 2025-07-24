
"""
ETL pipeline execution script
"""
import sys
import os
from pathlib import Path
import argparse
import schedule
import time
import logging
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.data_pipeline.etl_processor import ETLProcessor, ETLJob
from backend.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_customer_pipeline():
    """Run customer data ETL pipeline"""
    logger.info("🔄 Running customer data pipeline...")
    
    processor = ETLProcessor()
    
    # Create customer pipeline job
    job_config = ETLJob(
        job_id="customer_etl_pipeline",
        name="Customer Data ETL Pipeline",
        source_config={
            'type': 'csv',
            'file_path': 'data/raw/customer_data.csv'
        },
        transform_config={
            'apply_cleaning': True,
            'apply_validation': True,
            'custom_transforms': [
                {
                    'type': 'add_calculated_column',
                    'column_name': 'age_group',
                    'calculation': {'type': 'age_group'}
                }
            ]
        },
        destination_config={
            'type': 'customer_table'
        }
    )
    
    job_id = processor.create_etl_job(job_config)
    result = processor.execute_etl_job(job_id)
    
    if result['status'] == 'completed':
        logger.info("✅ Customer pipeline completed successfully")
    else:
        logger.error(f"❌ Customer pipeline failed: {result.get('errors', [])}")
    
    return result

def run_campaign_pipeline():
    """Run campaign data ETL pipeline"""
    logger.info("🔄 Running campaign data pipeline...")
    
    processor = ETLProcessor()
    
    # Create campaign pipeline job
    job_config = ETLJob(
        job_id="campaign_etl_pipeline",
        name="Campaign Data ETL Pipeline",
        source_config={
            'type': 'database',
            'query': 'SELECT * FROM campaigns WHERE updated_at >= NOW() - INTERVAL 1 DAY'
        },
        transform_config={
            'apply_cleaning': True,
            'apply_validation': False,
            'custom_transforms': [
                {
                    'type': 'add_calculated_column',
                    'column_name': 'roi_category',
                    'calculation': {'type': 'roi_category'}
                }
            ]
        },
        destination_config={
            'type': 'csv',
            'file_path': 'data/processed/daily_campaign_data.csv'
        }
    )
    
    job_id = processor.create_etl_job(job_config)
    result = processor.execute_etl_job(job_id)
    
    if result['status'] == 'completed':
        logger.info("✅ Campaign pipeline completed successfully")
    else:
        logger.error(f"❌ Campaign pipeline failed: {result.get('errors', [])}")
    
    return result

def run_analytics_pipeline():
    """Run analytics aggregation pipeline"""
    logger.info("🔄 Running analytics pipeline...")
    
    processor = ETLProcessor()
    
    # Create analytics pipeline job
    job_config = ETLJob(
        job_id="analytics_etl_pipeline",
        name="Analytics Aggregation Pipeline",
        source_config={
            'type': 'database',
            'query': '''
                SELECT 
                    c.segment_id,
                    c.age,
                    c.rating_id,
                    cam.name as campaign_name,
                    cam.actual_roi
                FROM customers c
                LEFT JOIN campaigns cam ON cam.target_segments LIKE '%' || c.segment_id || '%'
                WHERE c.segment_id IS NOT NULL
            '''
        },
        transform_config={
            'apply_cleaning': False,
            'apply_validation': False,
            'custom_transforms': [
                {
                    'type': 'aggregate',
                    'group_by': ['segment_id'],
                    'aggregations': {
                        'age': 'mean',
                        'rating_id': 'mean',
                        'actual_roi': 'mean'
                    }
                }
            ]
        },
        destination_config={
            'type': 'csv',
            'file_path': 'data/processed/segment_analytics.csv'
        }
    )
    
    job_id = processor.create_etl_job(job_config)
    result = processor.execute_etl_job(job_id)
    
    
    if result['status'] == 'completed':
        logger.info("✅ Analytics pipeline completed successfully")
    else:
        logger.error(f"❌ Analytics pipeline failed: {result.get('errors', [])}")
    
    return result

def run_all_pipelines():
    """Run all ETL pipelines"""
    logger.info("🚀 Running all ETL pipelines...")
    
    results = []
    
    # Run pipelines in sequence
    pipelines = [
        ("Customer Pipeline", run_customer_pipeline),
        ("Campaign Pipeline", run_campaign_pipeline),
        ("Analytics Pipeline", run_analytics_pipeline)
    ]
    
    for name, pipeline_func in pipelines:
        try:
            result = pipeline_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"❌ {name} failed with exception: {e}")
            results.append((name, {"status": "failed", "error": str(e)}))
    
    # Summary
    successful = sum(1 for _, result in results if result.get('status') == 'completed')
    total = len(results)
    
    logger.info(f"📊 Pipeline execution summary: {successful}/{total} successful")
    
    for name, result in results:
        status = "✅" if result.get('status') == 'completed' else "❌"
        logger.info(f"   {status} {name}: {result.get('status', 'unknown')}")
    
    return results

def schedule_pipelines():
    """Set up scheduled pipeline execution"""
    logger.info("⏰ Setting up scheduled ETL pipelines...")
    
    # Schedule customer pipeline daily at 2 AM
    schedule.every().day.at("02:00").do(run_customer_pipeline)
    
    # Schedule campaign pipeline every 4 hours
    schedule.every(4).hours.do(run_campaign_pipeline)
    
    # Schedule analytics pipeline daily at 3 AM
    schedule.every().day.at("03:00").do(run_analytics_pipeline)
    
    logger.info("✅ Scheduled jobs configured:")
    logger.info("   - Customer pipeline: Daily at 2:00 AM")
    logger.info("   - Campaign pipeline: Every 4 hours")
    logger.info("   - Analytics pipeline: Daily at 3:00 AM")
    
    # Keep the scheduler running
    logger.info("🔄 Scheduler started. Press Ctrl+C to stop...")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("⏹️ Scheduler stopped by user")

def show_pipeline_status():
    """Show status of ETL pipelines"""
    logger.info("📊 Checking ETL pipeline status...")
    
    processor = ETLProcessor()
    metrics = processor.get_etl_metrics()
    
    logger.info("ETL System Status:")
    logger.info(f"   Total jobs: {metrics['total_jobs']}")
    logger.info(f"   Enabled jobs: {metrics['enabled_jobs']}")
    logger.info(f"   Total runs: {metrics['total_runs']}")
    logger.info(f"   Success rate: {metrics['success_rate']:.1f}%")
    logger.info(f"   Avg duration: {metrics['average_duration_seconds']:.1f}s")
    logger.info(f"   Total rows processed: {metrics['total_rows_processed']}")
    logger.info(f"   Last 24h runs: {metrics['last_24h_runs']}")

def cleanup_old_data():
    """Clean up old processed data"""
    logger.info("🧹 Cleaning up old processed data...")
    
    try:
        import glob
        from datetime import timedelta
        
        # Clean up files older than 30 days
        cutoff_date = datetime.now() - timedelta(days=30)
        
        data_dirs = [
            "data/processed",
            "data/reports/daily_reports",
            "logs"
        ]
        
        total_deleted = 0
        
        for data_dir in data_dirs:
            if not Path(data_dir).exists():
                continue
                
            for file_path in Path(data_dir).glob("**/*"):
                if file_path.is_file():
                    file_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_modified < cutoff_date:
                        file_path.unlink()
                        total_deleted += 1
                        logger.debug(f"Deleted old file: {file_path}")
        
        logger.info(f"✅ Cleanup completed. Deleted {total_deleted} old files")
        
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")

def main():
    """Main ETL script function"""
    parser = argparse.ArgumentParser(description="ETL Pipeline Management")
    parser.add_argument("command", choices=[
        "run", "schedule", "status", "cleanup", 
        "customer", "campaign", "analytics"
    ], help="Command to execute")
    parser.add_argument("--force", action="store_true", help="Force execution even if recent run exists")
    
    args = parser.parse_args()
    
    logger.info(f"🚀 ETL Command: {args.command}")
    
    try:
        if args.command == "run":
            run_all_pipelines()
        elif args.command == "schedule":
            schedule_pipelines()
        elif args.command == "status":
            show_pipeline_status()
        elif args.command == "cleanup":
            cleanup_old_data()
        elif args.command == "customer":
            run_customer_pipeline()
        elif args.command == "campaign":
            run_campaign_pipeline()
        elif args.command == "analytics":
            run_analytics_pipeline()
        
        logger.info("🎉 ETL command completed successfully")
        
    except Exception as e:
        logger.error(f"❌ ETL command failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

