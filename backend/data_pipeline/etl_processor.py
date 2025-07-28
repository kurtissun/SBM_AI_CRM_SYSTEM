import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Callable, Union
import logging
from datetime import datetime, timedelta
import json
import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import threading
from dataclasses import dataclass
from abc import ABC, abstractmethod

from .data_cleaner import AdvancedDataCleaner
from .data_validator import DataValidator
from core.database import get_db, Customer, CameraData
from core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class ETLJob:
    job_id: str
    name: str
    source_config: Dict[str, Any]
    transform_config: Dict[str, Any]
    destination_config: Dict[str, Any]
    schedule: Optional[str] = None
    enabled: bool = True

class DataSource(ABC):
    
    @abstractmethod
    def extract(self, config: Dict[str, Any]) -> pd.DataFrame:
        pass

class CSVDataSource(DataSource):
    
    def extract(self, config: Dict[str, Any]) -> pd.DataFrame:
        file_path = config['file_path']
        return pd.read_csv(file_path, **config.get('pandas_kwargs', {}))

class ExcelDataSource(DataSource):
    
    def extract(self, config: Dict[str, Any]) -> pd.DataFrame:
        file_path = config['file_path']
        return pd.read_excel(file_path, **config.get('pandas_kwargs', {}))

class DatabaseDataSource(DataSource):
    
    def extract(self, config: Dict[str, Any]) -> pd.DataFrame:
        query = config['query']
        db = get_db()
        return pd.read_sql(query, db.bind)

class APIDataSource(DataSource):
    
    def extract(self, config: Dict[str, Any]) -> pd.DataFrame:
        import requests
        
        url = config['url']
        headers = config.get('headers', {})
        params = config.get('params', {})
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        return pd.DataFrame(data)

class ETLProcessor:
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.data_cleaner = AdvancedDataCleaner()
        self.data_validator = DataValidator()
        
        self.data_sources = {
            'csv': CSVDataSource(),
            'excel': ExcelDataSource(),
            'database': DatabaseDataSource(),
            'api': APIDataSource()
        }
        
        self.active_jobs = {}
        self.job_history = []
        
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.job_lock = threading.Lock()
    
    def register_data_source(self, name: str, source: DataSource):
        self.data_sources[name] = source
        logger.info(f"Registered data source: {name}")
    
    def create_etl_job(self, job_config: ETLJob) -> str:
        with self.job_lock:
            self.active_jobs[job_config.job_id] = job_config
        
        logger.info(f"Created ETL job: {job_config.name} ({job_config.job_id})")
        return job_config.job_id
    
    def execute_etl_job(self, job_id: str) -> Dict[str, Any]:
        if job_id not in self.active_jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job = self.active_jobs[job_id]
        
        if not job.enabled:
            logger.warning(f"Job {job_id} is disabled")
            return {'status': 'skipped', 'reason': 'job_disabled'}
        
        logger.info(f"Starting ETL job: {job.name}")
        
        execution_report = {
            'job_id': job_id,
            'job_name': job.name,
            'start_time': datetime.now().isoformat(),
            'status': 'running',
            'stages': {},
            'metrics': {},
            'errors': []
        }
        
        try:
            logger.info(f"Extracting data for job {job.name}")
            extract_result = self._extract_data(job.source_config)
            execution_report['stages']['extract'] = {
                'status': 'completed',
                'rows_extracted': len(extract_result['data']),
                'duration_seconds': extract_result.get('duration', 0)
            }
            
            logger.info(f"Transforming data for job {job.name}")
            transform_result = self._transform_data(
                extract_result['data'], 
                job.transform_config
            )
            execution_report['stages']['transform'] = {
                'status': 'completed',
                'rows_processed': len(transform_result['data']),
                'transformations_applied': len(transform_result.get('transformations', [])),
                'duration_seconds': transform_result.get('duration', 0)
            }
            
            logger.info(f"Loading data for job {job.name}")
            load_result = self._load_data(
                transform_result['data'],
                job.destination_config
            )
            execution_report['stages']['load'] = {
                'status': 'completed',
                'rows_loaded': load_result.get('rows_loaded', 0),
                'duration_seconds': load_result.get('duration', 0)
            }
            
            execution_report['status'] = 'completed'
            execution_report['end_time'] = datetime.now().isoformat()
            
            total_duration = (
                datetime.fromisoformat(execution_report['end_time']) - 
                datetime.fromisoformat(execution_report['start_time'])
            ).total_seconds()
            
            execution_report['metrics'] = {
                'total_duration_seconds': total_duration,
                'rows_per_second': execution_report['stages']['load']['rows_loaded'] / total_duration if total_duration > 0 else 0,
                'data_quality_score': transform_result.get('data_quality_score', 0)
            }
            
        except Exception as e:
            logger.error(f"ETL job {job.name} failed: {str(e)}")
            execution_report['status'] = 'failed'
            execution_report['end_time'] = datetime.now().isoformat()
            execution_report['errors'].append({
                'error_type': type(e).__name__,
                'error_message': str(e),
                'timestamp': datetime.now().isoformat()
            })
        
        self.job_history.append(execution_report)
        
        logger.info(f"ETL job {job.name} completed with status: {execution_report['status']}")
        return execution_report
    
    def _extract_data(self, source_config: Dict[str, Any]) -> Dict[str, Any]:
        start_time = datetime.now()
        
        source_type = source_config.get('type')
        if source_type not in self.data_sources:
            raise ValueError(f"Unknown data source type: {source_type}")
        
        source = self.data_sources[source_type]
        data = source.extract(source_config)
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            'data': data,
            'duration': duration,
            'source_type': source_type,
            'rows_extracted': len(data)
        }
    
    def _transform_data(self, data: pd.DataFrame, 
                       transform_config: Dict[str, Any]) -> Dict[str, Any]:
        start_time = datetime.now()
        
        transformed_data = data.copy()
        transformations_applied = []
        
        if transform_config.get('apply_cleaning', True):
            cleaning_result = self.data_cleaner.clean_customer_data(transformed_data)
            transformed_data = cleaning_result['cleaned_data']
            transformations_applied.extend(cleaning_result['transformations'])
        
        data_quality_score = 0
        if transform_config.get('apply_validation', True):
            validation_result = self.data_validator.validate_dataset(transformed_data)
            data_quality_score = validation_result['data_quality_score']
        
        custom_transforms = transform_config.get('custom_transforms', [])
        for transform in custom_transforms:
            try:
                transformed_data = self._apply_custom_transform(transformed_data, transform)
                transformations_applied.append(transform['name'])
            except Exception as e:
                logger.error(f"Custom transform {transform.get('name', 'unknown')} failed: {str(e)}")
        
        if 'output_columns' in transform_config:
            output_columns = transform_config['output_columns']
            available_columns = [col for col in output_columns if col in transformed_data.columns]
            transformed_data = transformed_data[available_columns]
            transformations_applied.append(f"filtered_to_{len(available_columns)}_columns")
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            'data': transformed_data,
            'duration': duration,
            'transformations': transformations_applied,
            'data_quality_score': data_quality_score
        }
    
    def _apply_custom_transform(self, data: pd.DataFrame, 
                              transform_config: Dict[str, Any]) -> pd.DataFrame:
        transform_type = transform_config.get('type')
        
        if transform_type == 'column_rename':
            mapping = transform_config.get('mapping', {})
            return data.rename(columns=mapping)
        
        elif transform_type == 'column_drop':
            columns_to_drop = transform_config.get('columns', [])
            return data.drop(columns=[col for col in columns_to_drop if col in data.columns])
        
        elif transform_type == 'filter_rows':
            condition = transform_config.get('condition')
            if condition:
                column = condition.get('column')
                operator = condition.get('operator')
                value = condition.get('value')
                
                if column in data.columns:
                    if operator == 'equals':
                        return data[data[column] == value]
                    elif operator == 'not_equals':
                        return data[data[column] != value]
                    elif operator == 'greater_than':
                        return data[data[column] > value]
                    elif operator == 'less_than':
                        return data[data[column] < value]
                    elif operator == 'in':
                        return data[data[column].isin(value)]
            
            return data
        
        elif transform_type == 'add_calculated_column':
            column_name = transform_config.get('column_name')
            calculation = transform_config.get('calculation')
            
            if calculation.get('type') == 'age_group':
                data[column_name] = pd.cut(
                    data['age'],
                    bins=[0, 18, 25, 35, 50, 65, 100],
                    labels=['minor', 'young_adult', 'adult', 'middle_aged', 'mature', 'senior']
                )
            elif calculation.get('type') == 'days_since':
                date_column = calculation.get('date_column')
                if date_column in data.columns:
                    data[column_name] = (datetime.now() - pd.to_datetime(data[date_column])).dt.days
            
            return data
        
        elif transform_type == 'aggregate':
            group_by = transform_config.get('group_by', [])
            aggregations = transform_config.get('aggregations', {})
            
            if group_by and aggregations:
                return data.groupby(group_by).agg(aggregations).reset_index()
            
            return data
        
        else:
            logger.warning(f"Unknown transform type: {transform_type}")
            return data
    
    def _load_data(self, data: pd.DataFrame, 
                  destination_config: Dict[str, Any]) -> Dict[str, Any]:
        start_time = datetime.now()
        
        destination_type = destination_config.get('type')
        rows_loaded = 0
        
        try:
            if destination_type == 'csv':
                file_path = destination_config['file_path']
                data.to_csv(file_path, index=False, **destination_config.get('pandas_kwargs', {}))
                rows_loaded = len(data)
            
            elif destination_type == 'excel':
                file_path = destination_config['file_path']
                data.to_excel(file_path, index=False, **destination_config.get('pandas_kwargs', {}))
                rows_loaded = len(data)
            
            elif destination_type == 'database':
                table_name = destination_config['table_name']
                if_exists = destination_config.get('if_exists', 'append')
                
                db = get_db()
                data.to_sql(table_name, db.bind, if_exists=if_exists, index=False)
                rows_loaded = len(data)
            
            elif destination_type == 'customer_table':
                rows_loaded = self._load_to_customer_table(data, destination_config)
            
            else:
                raise ValueError(f"Unknown destination type: {destination_type}")
            
        except Exception as e:
            logger.error(f"Failed to load data: {str(e)}")
            raise
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            'rows_loaded': rows_loaded,
            'duration': duration,
            'destination_type': destination_type
        }
    
    def _load_to_customer_table(self, data: pd.DataFrame, 
                               config: Dict[str, Any]) -> int:
        db = get_db()
        
        column_mapping = config.get('column_mapping', {
            'customer_id': 'customer_id',
            'age': 'age',
            'sex': 'gender',
            'rating_id': 'rating_id',
            'expanding_type_name': 'expanding_type_name',
            'expanding_channel_name': 'expanding_channel_name'
        })
        
        rows_loaded = 0
        
        try:
            for _, row in data.iterrows():
                customer_data = {}
                for source_col, target_col in column_mapping.items():
                    if source_col in row:
                        customer_data[target_col] = row[source_col]
                
                customer = Customer(**customer_data)
                
                existing = db.query(Customer).filter(
                    Customer.customer_id == customer_data.get('customer_id')
                ).first()
                
                if existing:
                    for key, value in customer_data.items():
                        setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                else:
                    db.add(customer)
                
                rows_loaded += 1
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            raise
        finally:
            db.close()
        
        return rows_loaded
    
    async def execute_etl_job_async(self, job_id: str) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.execute_etl_job, job_id)
    
    def schedule_etl_jobs(self):
        scheduled_jobs = [job for job in self.active_jobs.values() if job.schedule]
        
        for job in scheduled_jobs:
            if self._should_job_run(job):
                logger.info(f"Running scheduled job: {job.name}")
                self.execute_etl_job(job.job_id)
    
    def _should_job_run(self, job: ETLJob) -> bool:
        if not job.schedule:
            return False
        
        last_run = self._get_last_job_run(job.job_id)
        
        if job.schedule == 'daily':
            if not last_run:
                return True
            return (datetime.now() - last_run).days >= 1
        
        elif job.schedule == 'hourly':
            if not last_run:
                return True
            return (datetime.now() - last_run).seconds >= 3600
        
        return False
    
    def _get_last_job_run(self, job_id: str) -> Optional[datetime]:
        job_runs = [run for run in self.job_history if run['job_id'] == job_id]
        
        if job_runs:
            last_run = max(job_runs, key=lambda x: x['start_time'])
            return datetime.fromisoformat(last_run['start_time'])
        
        return None
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        if job_id not in self.active_jobs:
            return {'error': 'Job not found'}
        
        job = self.active_jobs[job_id]
        last_run = self._get_last_job_run(job_id)
        
        job_runs = [run for run in self.job_history if run['job_id'] == job_id]
        
        return {
            'job_id': job_id,
            'name': job.name,
            'enabled': job.enabled,
            'schedule': job.schedule,
            'last_run': last_run.isoformat() if last_run else None,
            'total_runs': len(job_runs),
            'success_rate': len([r for r in job_runs if r['status'] == 'completed']) / len(job_runs) * 100 if job_runs else 0,
            'last_status': job_runs[-1]['status'] if job_runs else 'never_run'
        }
    
    def get_etl_metrics(self) -> Dict[str, Any]:
        total_jobs = len(self.active_jobs)
        enabled_jobs = len([job for job in self.active_jobs.values() if job.enabled])
        total_runs = len(self.job_history)
        successful_runs = len([run for run in self.job_history if run['status'] == 'completed'])
        
        completed_runs = [run for run in self.job_history if run['status'] == 'completed']
        avg_duration = 0
        if completed_runs:
            durations = []
            for run in completed_runs:
                if 'metrics' in run and 'total_duration_seconds' in run['metrics']:
                    durations.append(run['metrics']['total_duration_seconds'])
            avg_duration = np.mean(durations) if durations else 0
        
        total_rows_processed = sum(
            run['stages'].get('load', {}).get('rows_loaded', 0)
            for run in self.job_history
            if run['status'] == 'completed'
        )
        
        return {
            'total_jobs': total_jobs,
            'enabled_jobs': enabled_jobs,
            'total_runs': total_runs,
            'successful_runs': successful_runs,
            'success_rate': successful_runs / total_runs * 100 if total_runs > 0 else 0,
            'average_duration_seconds': avg_duration,
            'total_rows_processed': total_rows_processed,
            'last_24h_runs': len([
                run for run in self.job_history
                if datetime.now() - datetime.fromisoformat(run['start_time']) <= timedelta(days=1)
            ])
        }
    
    def create_customer_data_pipeline(self) -> str:
        job_config = ETLJob(
            job_id="customer_data_pipeline",
            name="Customer Data Processing Pipeline",
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
                    },
                    {
                        'type': 'filter_rows',
                        'condition': {
                            'column': 'age',
                            'operator': 'greater_than',
                            'value': 0
                        }
                    }
                ],
                'output_columns': [
                    'customer_id', 'age', 'sex', 'rating_id', 
                    'expanding_type_name', 'expanding_channel_name', 'age_group'
                ]
            },
            destination_config={
                'type': 'customer_table',
                'column_mapping': {
                    'customer_id': 'customer_id',
                    'age': 'age',
                    'sex': 'gender',
                    'rating_id': 'rating_id',
                    'expanding_type_name': 'expanding_type_name',
                    'expanding_channel_name': 'expanding_channel_name'
                }
            },
            schedule='daily',
            enabled=True
        )
        
        return self.create_etl_job(job_config)
    
    def create_camera_data_pipeline(self) -> str:
        job_config = ETLJob(
            job_id="camera_data_pipeline",
            name="Camera Data Processing Pipeline",
            source_config={
                'type': 'api',
                'url': 'http://camera-system/api/daily-summary',
                'headers': {'Authorization': 'Bearer token'}
            },
            transform_config={
                'apply_cleaning': True,
                'apply_validation': False,
                'custom_transforms': [
                    {
                        'type': 'add_calculated_column',
                        'column_name': 'days_since_collection',
                        'calculation': {
                            'type': 'days_since',
                            'date_column': 'timestamp'
                        }
                    }
                ]
            },
            destination_config={
                'type': 'database',
                'table_name': 'camera_data',
                'if_exists': 'append'
            },
            schedule='hourly',
            enabled=True
        )
        
        return self.create_etl_job(job_config)
    
    def export_job_config(self, job_id: str, filepath: str):
        if job_id not in self.active_jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job = self.active_jobs[job_id]
        
        config = {
            'job_id': job.job_id,
            'name': job.name,
            'source_config': job.source_config,
            'transform_config': job.transform_config,
            'destination_config': job.destination_config,
            'schedule': job.schedule,
            'enabled': job.enabled
        }
        
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Job configuration exported to {filepath}")
    
    def import_job_config(self, filepath: str) -> str:
        with open(filepath, 'r') as f:
            config = json.load(f)
        
        job = ETLJob(
            job_id=config['job_id'],
            name=config['name'],
            source_config=config['source_config'],
            transform_config=config['transform_config'],
            destination_config=config['destination_config'],
            schedule=config.get('schedule'),
            enabled=config.get('enabled', True)
        )
        
        return self.create_etl_job(job)

def process_customer_csv(input_file: str, output_table: str = 'customers') -> Dict[str, Any]:
    processor = ETLProcessor()
    
    job_config = ETLJob(
        job_id=f"temp_customer_csv_{datetime.now().timestamp()}",
        name="Temporary Customer CSV Processing",
        source_config={
            'type': 'csv',
            'file_path': input_file
        },
        transform_config={
            'apply_cleaning': True,
            'apply_validation': True
        },
        destination_config={
            'type': 'customer_table' if output_table == 'customers' else 'database',
            'table_name': output_table
        }
    )
    
    job_id = processor.create_etl_job(job_config)
    return processor.execute_etl_job(job_id)

def setup_default_etl_pipelines() -> List[str]:
    processor = ETLProcessor()
    
    job_ids = []
    
    customer_job_id = processor.create_customer_data_pipeline()
    job_ids.append(customer_job_id)
    
    camera_job_id = processor.create_camera_data_pipeline()
    job_ids.append(camera_job_id)
    
    logger.info(f"Set up {len(job_ids)} default ETL pipelines")
    return job_ids