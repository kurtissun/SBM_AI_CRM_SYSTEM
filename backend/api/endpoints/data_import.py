"""
Data Import Endpoint
Handles CSV/XLSX import for customer data and other entities
"""

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import pandas as pd
import io
import logging
import uuid
from dateutil import parser

from core.database import get_db, Customer, Purchase, Campaign, Segment
from core.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

class ImportResponse(BaseModel):
    status: str
    message: str
    imported_count: int
    errors: List[str] = []
    timestamp: datetime

class ImportStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    message: str
    imported_count: int
    total_count: int
    errors: List[str] = []

# In-memory job status tracking (in production, use Redis)
import_jobs = {}

def process_customer_data(df: pd.DataFrame, db: Session) -> Dict[str, Any]:
    """Process customer data from DataFrame"""
    imported_count = 0
    errors = []
    
    try:
        for index, row in df.iterrows():
            try:
                # Generate customer_id if not provided
                customer_id = str(row.get('customer_id', str(uuid.uuid4())))
                
                # Parse dates safely
                last_purchase_date = None
                if pd.notna(row.get('last_purchase_date')):
                    try:
                        last_purchase_date = parser.parse(str(row['last_purchase_date']))
                    except:
                        pass
                
                birthday = None
                if pd.notna(row.get('birthday')):
                    try:
                        birthday = parser.parse(str(row['birthday']))
                    except:
                        pass
                
                registration_time = None
                if pd.notna(row.get('registration_time')):
                    try:
                        registration_time = parser.parse(str(row['registration_time']))
                    except:
                        registration_time = datetime.utcnow()
                else:
                    registration_time = datetime.utcnow()
                
                # Check if customer already exists
                existing_customer = db.query(Customer).filter(
                    Customer.customer_id == customer_id
                ).first()
                
                if existing_customer:
                    # Update existing customer
                    customer = existing_customer
                else:
                    # Create new customer
                    customer = Customer(customer_id=customer_id)
                    db.add(customer)
                
                # Update customer fields
                customer.name = str(row.get('name', '')) if pd.notna(row.get('name')) else None
                customer.email = str(row.get('email', '')) if pd.notna(row.get('email')) else None
                customer.age = int(row['age']) if pd.notna(row.get('age')) else None
                customer.gender = str(row.get('gender', '')) if pd.notna(row.get('gender')) else None
                customer.location = str(row.get('location', '')) if pd.notna(row.get('location')) else None
                customer.total_spent = float(row.get('total_spent', 0)) if pd.notna(row.get('total_spent')) else 0.0
                customer.purchase_frequency = int(row.get('purchase_frequency', 0)) if pd.notna(row.get('purchase_frequency')) else 0
                customer.last_purchase_date = last_purchase_date
                customer.birthday = birthday
                customer.registration_time = registration_time
                customer.membership_level = str(row.get('membership_level', '')) if pd.notna(row.get('membership_level')) else None
                customer.rating_id = int(row['rating_id']) if pd.notna(row.get('rating_id')) else None
                customer.expanding_type_name = str(row.get('expanding_type_name', '')) if pd.notna(row.get('expanding_type_name')) else None
                customer.expanding_channel_name = str(row.get('expanding_channel_name', '')) if pd.notna(row.get('expanding_channel_name')) else None
                customer.segment_id = str(row.get('segment_id', '')) if pd.notna(row.get('segment_id')) else None
                customer.member_name = str(row.get('member_name', '')) if pd.notna(row.get('member_name')) else None
                customer.from_org_id = str(row.get('from_org_id', '')) if pd.notna(row.get('from_org_id')) else None
                customer.registration_project = str(row.get('registration_project', '')) if pd.notna(row.get('registration_project')) else None
                customer.birth_month = int(row['birth_month']) if pd.notna(row.get('birth_month')) else None
                customer.birth_identity = str(row.get('birth_identity', '')) if pd.notna(row.get('birth_identity')) else None
                customer.updated_at = datetime.utcnow()
                
                imported_count += 1
                
            except Exception as e:
                error_msg = f"Row {index + 1}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"Error processing row {index + 1}: {e}")
                continue
        
        db.commit()
        return {
            "imported_count": imported_count,
            "errors": errors
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing customer data: {e}")
        raise e

def process_purchase_data(df: pd.DataFrame, db: Session) -> Dict[str, Any]:
    """Process purchase data from DataFrame"""
    imported_count = 0
    errors = []
    
    try:
        for index, row in df.iterrows():
            try:
                customer_id = str(row.get('customer_id', ''))
                if not customer_id:
                    errors.append(f"Row {index + 1}: customer_id is required")
                    continue
                
                # Parse purchase time
                purchase_time = None
                if pd.notna(row.get('purchase_time')):
                    try:
                        purchase_time = parser.parse(str(row['purchase_time']))
                    except:
                        purchase_time = datetime.utcnow()
                else:
                    purchase_time = datetime.utcnow()
                
                purchase = Purchase(
                    customer_id=customer_id,
                    purchase_amount=float(row.get('purchase_amount', 0)) if pd.notna(row.get('purchase_amount')) else 0.0,
                    points_earned=int(row.get('points_earned', 0)) if pd.notna(row.get('points_earned')) else 0,
                    business_type=str(row.get('business_type', '')) if pd.notna(row.get('business_type')) else None,
                    store_name=str(row.get('store_name', '')) if pd.notna(row.get('store_name')) else None,
                    purchase_time=purchase_time
                )
                
                db.add(purchase)
                imported_count += 1
                
            except Exception as e:
                error_msg = f"Row {index + 1}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"Error processing purchase row {index + 1}: {e}")
                continue
        
        db.commit()
        return {
            "imported_count": imported_count,
            "errors": errors
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing purchase data: {e}")
        raise e

async def process_import_job(job_id: str, file_content: bytes, file_type: str, data_type: str, db: Session):
    """Background task to process import job"""
    try:
        import_jobs[job_id]["status"] = "processing"
        import_jobs[job_id]["message"] = "Reading file..."
        
        # Read file
        if file_type in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel']:
            df = pd.read_excel(io.BytesIO(file_content))
        else:  # CSV
            df = pd.read_csv(io.StringIO(file_content.decode('utf-8')))
        
        import_jobs[job_id]["total_count"] = len(df)
        import_jobs[job_id]["message"] = f"Processing {len(df)} records..."
        
        # Process data based on type
        if data_type == "customers":
            result = process_customer_data(df, db)
        elif data_type == "purchases":
            result = process_purchase_data(df, db)
        else:
            raise ValueError(f"Unsupported data type: {data_type}")
        
        # Update job status
        import_jobs[job_id].update({
            "status": "completed",
            "progress": 100,
            "message": f"Import completed successfully. Imported {result['imported_count']} records.",
            "imported_count": result['imported_count'],
            "errors": result['errors']
        })
        
    except Exception as e:
        import_jobs[job_id].update({
            "status": "failed",
            "message": f"Import failed: {str(e)}",
            "errors": [str(e)]
        })
        logger.error(f"Import job {job_id} failed: {e}")

@router.post("/upload", tags=["Data Import"])
async def upload_data_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    data_type: str = "customers",  # customers, purchases, campaigns
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload CSV or XLSX file for data import"""
    try:
        # Validate file type
        allowed_types = [
            'text/csv',
            'application/csv',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel'
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed types: CSV, XLSX"
            )
        
        # Validate data type
        if data_type not in ["customers", "purchases", "campaigns"]:
            raise HTTPException(
                status_code=400,
                detail="data_type must be one of: customers, purchases, campaigns"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Create job ID and track status
        job_id = str(uuid.uuid4())
        import_jobs[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "progress": 0,
            "message": "Import job queued",
            "imported_count": 0,
            "total_count": 0,
            "errors": [],
            "created_at": datetime.utcnow(),
            "created_by": current_user.get("username")
        }
        
        # Start background processing
        background_tasks.add_task(
            process_import_job,
            job_id,
            file_content,
            file.content_type,
            data_type,
            db
        )
        
        return JSONResponse(content={
            "job_id": job_id,
            "status": "queued",
            "message": f"Import job started for {data_type} data",
            "filename": file.filename,
            "data_type": data_type
        })
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{job_id}", response_model=ImportStatusResponse, tags=["Data Import"])
async def get_import_status(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get status of import job"""
    if job_id not in import_jobs:
        raise HTTPException(status_code=404, detail="Import job not found")
    
    job = import_jobs[job_id]
    return ImportStatusResponse(**job)

@router.get("/jobs", tags=["Data Import"])
async def list_import_jobs(
    current_user: dict = Depends(get_current_user)
):
    """List all import jobs for current user"""
    user_jobs = {
        job_id: job for job_id, job in import_jobs.items()
        if job.get("created_by") == current_user.get("username")
    }
    
    return {
        "jobs": user_jobs,
        "total": len(user_jobs)
    }

@router.post("/sample", tags=["Data Import"])
async def generate_sample_file(
    data_type: str = "customers",
    format: str = "csv",  # csv or xlsx
    current_user: dict = Depends(get_current_user)
):
    """Generate sample file template for import"""
    try:
        if data_type == "customers":
            sample_data = {
                'customer_id': ['CUST001', 'CUST002', 'CUST003'],
                'name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
                'email': ['john@example.com', 'jane@example.com', 'bob@example.com'],
                'age': [25, 30, 35],
                'gender': ['Male', 'Female', 'Male'],
                'location': ['New York', 'Los Angeles', 'Chicago'],
                'total_spent': [1500.50, 2300.75, 800.25],
                'purchase_frequency': [5, 8, 3],
                'membership_level': ['Gold', 'Platinum', 'Silver'],
                'segment_id': ['SEG001', 'SEG002', 'SEG001']
            }
        elif data_type == "purchases":
            sample_data = {
                'customer_id': ['CUST001', 'CUST002', 'CUST003'],
                'purchase_amount': [150.50, 230.75, 80.25],
                'points_earned': [15, 23, 8],
                'business_type': ['Retail', 'Food', 'Electronics'],
                'store_name': ['Store A', 'Restaurant B', 'Tech Store C'],
                'purchase_time': ['2024-01-15 10:30:00', '2024-01-16 14:20:00', '2024-01-17 16:45:00']
            }
        else:
            raise HTTPException(status_code=400, detail="Unsupported data type")
        
        df = pd.DataFrame(sample_data)
        
        if format == "xlsx":
            output = io.BytesIO()
            df.to_excel(output, index=False)
            output.seek(0)
            content = output.getvalue()
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"sample_{data_type}.xlsx"
        else:  # csv
            output = io.StringIO()
            df.to_csv(output, index=False)
            content = output.getvalue().encode('utf-8')
            media_type = "text/csv"
            filename = f"sample_{data_type}.csv"
        
        from fastapi.responses import Response
        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error generating sample file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/job/{job_id}", tags=["Data Import"])
async def delete_import_job(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete import job from tracking"""
    if job_id not in import_jobs:
        raise HTTPException(status_code=404, detail="Import job not found")
    
    job = import_jobs[job_id]
    if job.get("created_by") != current_user.get("username"):
        raise HTTPException(status_code=403, detail="Not authorized to delete this job")
    
    del import_jobs[job_id]
    
    return JSONResponse(content={
        "message": "Import job deleted successfully",
        "job_id": job_id
    })