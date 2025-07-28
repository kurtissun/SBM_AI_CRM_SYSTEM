from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any, Optional
import pandas as pd
import io
import json
import numpy as np
import logging
from datetime import datetime, timedelta

from ...core.database import get_db, Customer, Purchase
from ...core.security import get_current_user
from ...ai_engine.adaptive_clustering import AdaptiveClustering as AdaptiveClusteringEngine
from ...ai_engine.insight_generator import IntelligentInsightGenerator
from ...data_pipeline.data_cleaner import AdvancedDataCleaner
from ...data_pipeline.data_validator import DataValidator

router = APIRouter()
logger = logging.getLogger(__name__)

def convert_numpy_types(obj):
    """Convert numpy types to JSON serializable Python types"""
    if isinstance(obj, dict):
        # Convert both keys and values
        converted_dict = {}
        for k, v in obj.items():
            # Convert key
            if isinstance(k, np.integer):
                key = int(k)
            elif isinstance(k, np.floating):
                key = float(k)
            else:
                key = k
            # Convert value
            converted_dict[key] = convert_numpy_types(v)
        return converted_dict
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif pd.isna(obj):
        return None
    else:
        return obj

@router.get("/", response_model=List[Dict])
async def get_customers(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    segment_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(Customer)
    
    if segment_id is not None:
        query = query.filter(Customer.segment_id == segment_id)
    
    customers = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": str(customer.id),
            "customer_id": customer.customer_id,
            "age": customer.age,
            "gender": customer.gender,
            "rating_id": customer.rating_id,
            "segment_id": customer.segment_id,
            "created_at": customer.created_at.isoformat()
        }
        for customer in customers
    ]

@router.get("/{customer_id}")
async def get_customer(
    customer_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return {
        "id": str(customer.id),
        "customer_id": customer.customer_id,
        "age": customer.age,
        "gender": customer.gender,
        "rating_id": customer.rating_id,
        "expanding_type_name": customer.expanding_type_name,
        "expanding_channel_name": customer.expanding_channel_name,
        "segment_id": customer.segment_id,
        "created_at": customer.created_at.isoformat(),
        "updated_at": customer.updated_at.isoformat()
    }

@router.post("/upload/chinese")
async def upload_chinese_customer_data(
    request: Request,
    file: UploadFile = File(...),
    auto_segment: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Upload Chinese format customer data: 会员id, 所在地, 性别, 生日, 注册时间, 消费时间, 会员等级, 消费金额, 消费获取积分, 消费业态, 消费店铺"""
    # Log the request for debugging encoding issues
    logger.info(f"📤 Chinese upload request from {current_user.get('username')}")
    logger.info(f"📁 Filename: {file.filename}")
    logger.info(f"📋 Content-Type: {file.content_type}")
    
    return await _process_upload(file, "chinese", auto_segment, db)

@router.post("/upload/mixed")
async def upload_mixed_customer_data(
    file: UploadFile = File(...),
    auto_segment: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Upload mixed format customer data: id, member_nme, sex, birthday, rwting_id, from_org_id, reg_date, expanding_type_name, expanding_channel_name, 注册项目, 年龄, 生日月, 出生身份"""
    return await _process_upload(file, "mixed", auto_segment, db)

@router.post("/upload")
async def upload_customer_data(
    file: UploadFile = File(...),
    auto_segment: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Auto-detect format and upload customer data"""
    return await _process_upload(file, "auto", auto_segment, db)

async def _process_upload(
    file: UploadFile,
    expected_format: str,
    auto_segment: bool,
    db: Session
):
    # Handle filename encoding issues
    filename = file.filename or "unknown_file"
    try:
        # Ensure filename is properly encoded
        filename = filename.encode('utf-8', errors='replace').decode('utf-8')
    except Exception:
        filename = "uploaded_file"
    
    # Check file extension with safe filename
    if not filename.lower().endswith(('.csv', '.xlsx')):
        raise HTTPException(status_code=400, detail="File must be CSV or Excel format")
    
    try:
        content = await file.read()
        
        if filename.lower().endswith('.csv'):
            # Try multiple encodings for Chinese text
            try:
                df = pd.read_csv(io.StringIO(content.decode('utf-8')))
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(io.StringIO(content.decode('gbk')))
                    print("📝 Used GBK encoding for Chinese text")
                except UnicodeDecodeError:
                    try:
                        df = pd.read_csv(io.StringIO(content.decode('gb2312')))
                        print("📝 Used GB2312 encoding for Chinese text")
                    except UnicodeDecodeError:
                        df = pd.read_csv(io.StringIO(content.decode('utf-8', errors='ignore')))
                        print("⚠️ Used UTF-8 with error ignoring")
        else:
            df = pd.read_excel(io.BytesIO(content))
        
        # Handle multiple data formats
        original_columns = df.columns.tolist()
        print(f"📋 Detected columns: {original_columns}")
        
        # Clean and normalize Chinese text
        def normalize_chinese_text(text):
            if pd.isna(text) or text is None:
                return text
            text = str(text).strip()
            # Convert traditional Chinese to simplified if needed
            # Replace common encoding issues
            replacements = {
                'Â': '', 'â': '', 'ã': '', 'Ã': '',
                'é': 'e', 'è': 'e', 'ê': 'e',
                'ç': 'c', 'ñ': 'n'
            }
            for old, new in replacements.items():
                text = text.replace(old, new)
            return text
        
        # Apply text normalization to all string columns
        for col in df.columns:
            if df[col].dtype == 'object':  # String columns
                df[col] = df[col].apply(normalize_chinese_text)
        
        # Format 1: Chinese format (complete mapping)
        chinese_mapping = {
            '会员id': 'customer_id',
            '所在地': 'location', 
            '性别': 'gender',
            '生日': 'birthday',
            '注册时间': 'registration_time',
            '消费时间': 'purchase_time',  # Added missing consumption time
            '会员等级': 'membership_level',
            '消费金额': 'purchase_amount',
            '消费获取积分': 'points_earned',
            '消费业态': 'business_type',
            '消费店铺': 'store_name'
        }
        
        # Format 2: Mixed format (corrected column names)
        mixed_mapping = {
            'id': 'customer_id',
            'member_name': 'member_name',  # Corrected from member_nme
            'sex': 'gender',
            'birthday': 'birthday',
            'rating_id': 'rating_id',  # Corrected from rwting_id
            'from_org_id': 'from_org_id',
            'reg_date': 'registration_time',
            'expanding_type_name': 'expanding_type_name',
            'expanding_channel_name': 'expanding_channel_name',
            '注册项目': 'registration_project',
            '年龄': 'age',
            '生日月': 'birth_month',
            '出生身份': 'birth_identity'
        }
        
        # Apply format-specific logic based on expected_format or auto-detect
        if expected_format == "chinese" or (expected_format == "auto" and '会员id' in df.columns):
            print("🎯 Processing: Chinese format")
            df = df.rename(columns=chinese_mapping)
            data_format = "chinese"
            
        elif expected_format == "mixed" or (expected_format == "auto" and ('member_name' in df.columns or 'rating_id' in df.columns)):
            print("🎯 Processing: Mixed format")
            df = df.rename(columns=mixed_mapping)
            data_format = "mixed"
            
            # Filter out privacy records for mixed format
            if 'gender' in df.columns:
                initial_count = len(df)
                df = df[df['gender'] != 'privacy']
                filtered_count = len(df)
                print(f"🔒 Filtered out {initial_count - filtered_count} privacy records")
                
        else:
            if expected_format != "auto":
                raise HTTPException(
                    status_code=400, 
                    detail=f"File format doesn't match expected format: {expected_format}"
                )
            print("🎯 Processing: Standard format")
            data_format = "standard"
        
        # Calculate age from birthday if provided
        if 'birthday' in df.columns and 'age' not in df.columns:
            df['birthday'] = pd.to_datetime(df['birthday'])
            df['age'] = ((datetime.now() - df['birthday']).dt.days / 365.25).astype(int)
        
        # Convert datetime columns
        datetime_columns = ['birthday', 'registration_time', 'purchase_time']
        for col in datetime_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        cleaner = AdvancedDataCleaner()
        cleaning_result = cleaner.clean_customer_data(df)
        cleaned_df = cleaning_result['cleaned_data']
        
        validator = DataValidator()
        validation_result = validator.validate_dataset(cleaned_df)

        # Save to database with duplicate detection
        customers_saved = 0
        purchases_saved = 0
        duplicates_skipped = 0
        processed_customer_ids = set()  # Track customers processed in this batch
        
        for _, row in cleaned_df.iterrows():
            customer_id = str(row.get('customer_id'))  # Ensure string format
            if not customer_id or customer_id == 'nan':
                continue
                
            # Check if customer exists in database OR already processed in this batch
            existing_customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
            already_processed_in_batch = customer_id in processed_customer_ids
            
            if not existing_customer and not already_processed_in_batch:
                # Create new customer with all possible fields
                customer = Customer(
                    customer_id=customer_id,
                    age=int(row.get('age')) if pd.notna(row.get('age')) else None,
                    gender=str(row.get('gender')) if pd.notna(row.get('gender')) else None,
                    location=str(row.get('location')) if pd.notna(row.get('location')) else None,
                    birthday=row.get('birthday') if pd.notna(row.get('birthday')) else None,
                    registration_time=row.get('registration_time') if pd.notna(row.get('registration_time')) else None,
                    membership_level=str(row.get('membership_level')) if pd.notna(row.get('membership_level')) else None,
                    rating_id=int(row.get('rating_id', 3)) if pd.notna(row.get('rating_id')) else 3,
                    
                    # Additional fields for mixed format
                    member_name=str(row.get('member_name')) if pd.notna(row.get('member_name')) else None,
                    from_org_id=str(row.get('from_org_id')) if pd.notna(row.get('from_org_id')) else None,
                    registration_project=str(row.get('registration_project')) if pd.notna(row.get('registration_project')) else None,
                    birth_month=int(row.get('birth_month')) if pd.notna(row.get('birth_month')) else None,
                    birth_identity=str(row.get('birth_identity')) if pd.notna(row.get('birth_identity')) else None,
                    
                    # Standard fields
                    expanding_type_name=str(row.get('expanding_type_name')) if pd.notna(row.get('expanding_type_name')) else None,
                    expanding_channel_name=str(row.get('expanding_channel_name')) if pd.notna(row.get('expanding_channel_name')) else None
                )
                db.add(customer)
                db.flush()  # Flush to get the ID without committing
                processed_customer_ids.add(customer_id)
                customers_saved += 1
                
            elif existing_customer and not already_processed_in_batch:
                # Update existing customer with new info
                update_fields = [
                    'location', 'membership_level', 'member_name', 'from_org_id',
                    'registration_project', 'birth_month', 'birth_identity',
                    'expanding_type_name', 'expanding_channel_name'
                ]
                
                for field in update_fields:
                    value = row.get(field)
                    if pd.notna(value) and value is not None:
                        setattr(existing_customer, field, str(value) if isinstance(value, str) else value)
                
                existing_customer.updated_at = datetime.utcnow()
                processed_customer_ids.add(customer_id)
                
            else:
                # Skip duplicate within same file
                duplicates_skipped += 1
                print(f"⚠️ Skipping duplicate customer_id in same file: {customer_id}")
            
            # Handle purchase data if present
            if 'purchase_amount' in row and pd.notna(row['purchase_amount']):
                purchase_amount = float(row['purchase_amount'])
                store_name = row.get('store_name', '')
                
                # Check for duplicate purchase (same customer, amount, store)
                existing_purchase = db.query(Purchase).filter(
                    Purchase.customer_id == customer_id,
                    Purchase.purchase_amount == purchase_amount,
                    Purchase.store_name == store_name
                ).first()
                
                if not existing_purchase:
                    purchase = Purchase(
                        customer_id=customer_id,
                        purchase_amount=purchase_amount,
                        points_earned=int(row.get('points_earned', 0)) if pd.notna(row.get('points_earned')) else 0,
                        business_type=str(row.get('business_type', '')) if pd.notna(row.get('business_type')) else '',
                        store_name=store_name,
                        purchase_time=row.get('purchase_time') if pd.notna(row.get('purchase_time')) else None
                    )
                    db.add(purchase)
                    purchases_saved += 1
                else:
                    duplicates_skipped += 1
        
        db.commit()

        response_data = {
            "upload_summary": {
                "original_rows": len(df),
                "cleaned_rows": len(cleaned_df),
                "customers_saved": customers_saved,
                "purchases_saved": purchases_saved,
                "duplicates_skipped": duplicates_skipped,
                "retention_rate": len(cleaned_df) / len(df) * 100,
                "data_quality_score": validation_result['data_quality_score'],
                "data_format_detected": data_format,
                "original_columns": original_columns
            },
            "cleaning_report": cleaning_result['cleaning_report'],
            "validation_report": {
                "total_rules": validation_result['summary']['total_rules'],
                "passed": validation_result['summary']['passed'],
                "failed": validation_result['summary']['failed'],
                "recommendations": validation_result['recommendations']
            }
        }
        
        if auto_segment and len(cleaned_df) >= 10:
            try:
                # Try generative LLM segmentation first
                from ...ai_engine.local_llm_segmentation import run_generative_segmentation
                
                logger.info("🤖 Attempting generative LLM segmentation...")
                
                clustering_result = run_generative_segmentation(cleaned_df)
                
                logger.info(f"🔍 LLM segmentation result: llm_enabled={clustering_result.get('llm_enabled', False)}, has_assignments={'customer_assignments' in clustering_result}")
                
                # If LLM segmentation successful and has custom segments
                if clustering_result.get('llm_enabled', False) and 'customer_assignments' in clustering_result:
                    logger.info("✨ LLM segmentation successful - applying intelligent segments")
                    
                    # Apply LLM-generated segment assignments
                    logger.info(f"🔧 Applying segments: {list(clustering_result['customer_assignments'].keys())}")
                    for segment_id, customer_ids in clustering_result['customer_assignments'].items():
                        logger.info(f"🔧 Processing segment {segment_id} with {len(customer_ids)} customers")
                        segment_numeric_id = hash(segment_id) % 1000  # Convert segment name to numeric ID
                        for customer_id in customer_ids:
                            logger.info(f"🔧 Updating customer {customer_id} to segment {segment_numeric_id}")
                            db.query(Customer).filter(Customer.customer_id == customer_id).update({
                                'segment_id': segment_numeric_id
                            })
                    
                    # Generate enhanced insights using both engines
                    logger.info("🧠 Generating enhanced insights...")
                    try:
                        insight_generator = IntelligentInsightGenerator()
                        enhanced_insights = insight_generator.generate_comprehensive_insights(clustering_result)
                        logger.info("✅ Enhanced insights generated successfully")
                    except Exception as insights_error:
                        logger.error(f"❌ Enhanced insights failed: {insights_error}")
                        enhanced_insights = {'segment_insights': {}}
                    
                    response_data["segmentation_results"] = convert_numpy_types({
                        "segmentation_method": "generative_llm",
                        "llm_enabled": True,
                        "n_clusters": clustering_result['n_clusters'],
                        "silhouette_score": clustering_result['silhouette_score'],
                        "algorithm_used": clustering_result['algorithm_used'],
                        "cluster_profiles": clustering_result['cluster_profiles'],
                        "customer_assignments": clustering_result.get('customer_assignments', {}),
                        "executive_summary": clustering_result.get('executive_summary', {}),
                        "insights": enhanced_insights.get('segment_insights', {}),
                        "llm_segments": clustering_result.get('cluster_profiles', {})
                    })
                    
                else:
                    # Fallback to traditional clustering
                    logger.info("🔄 Falling back to adaptive clustering...")
                    clustering_engine = AdaptiveClusteringEngine()
                    clustering_result = clustering_engine.fit_transform(cleaned_df)
                    
                    # Store traditional cluster labels
                    for idx, label in enumerate(clustering_result['labels']):
                        customer_id = cleaned_df.iloc[idx]['customer_id']
                        db.query(Customer).filter(Customer.customer_id == customer_id).update({'segment_id': int(label)})
                    
                    insight_generator = IntelligentInsightGenerator()
                    insights = insight_generator.generate_comprehensive_insights(clustering_result)
                    
                    response_data["segmentation_results"] = convert_numpy_types({
                        "segmentation_method": "traditional_clustering",
                        "llm_enabled": False,
                        "n_clusters": clustering_result['n_clusters'],
                        "silhouette_score": clustering_result['silhouette_score'],
                        "algorithm_used": clustering_result['algorithm_used'],
                        "cluster_profiles": clustering_result['cluster_profiles'],
                        "insights": insights['segment_insights']
                    })
                    
            except Exception as clustering_error:
                logger.error(f"❌ All segmentation methods failed: {clustering_error}")
                response_data["segmentation_results"] = {
                    "error": "Segmentation failed",
                    "details": str(clustering_error),
                    "fallback_applied": True
                }
        
        return JSONResponse(content=convert_numpy_types(response_data))
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@router.post("/segment")
async def segment_customers(
    customer_ids: List[str] = None,
    force_retrain: bool = False,
    algorithm: str = "adaptive_kmeans",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        query = db.query(Customer)
        if customer_ids:
            query = query.filter(Customer.customer_id.in_(customer_ids))
        
        customers = query.all()
        
        if len(customers) < 10:
            raise HTTPException(status_code=400, detail="Minimum 10 customers required for segmentation")
        
        # Enhanced segmentation data with purchase history and membership
        segmentation_data = []
        
        for customer in customers:
            # Calculate purchase metrics
            purchases = db.query(Purchase).filter(Purchase.customer_id == customer.customer_id).all()
            
            total_spent = sum(p.purchase_amount for p in purchases)
            avg_purchase = total_spent / len(purchases) if purchases else 0
            purchase_frequency = len(purchases)
            total_points = sum(p.points_earned for p in purchases)
            
            # Membership level encoding
            membership_score = {
                '橙卡会员': 1, '金卡会员': 2, '钻卡会员': 3
            }.get(customer.membership_level, 0)
            
            # Recent purchase activity (last 90 days)
            recent_date = datetime.now() - timedelta(days=90)
            recent_purchases = [p for p in purchases if p.purchase_date >= recent_date]
            recent_spending = sum(p.purchase_amount for p in recent_purchases)
            
            # Calculate customer lifetime value indicator
            days_since_registration = (datetime.now() - customer.registration_time).days if customer.registration_time else 365
            clv_indicator = total_spent / max(days_since_registration / 365, 0.1)
            
            segmentation_data.append({
                "customer_id": customer.customer_id,
                "age": customer.age or 30,
                "gender_encoded": 1 if customer.gender == "M" else 0,
                "membership_score": membership_score,
                "total_spent": total_spent,
                "avg_purchase_amount": avg_purchase,
                "purchase_frequency": purchase_frequency,
                "total_points": total_points,
                "recent_spending": recent_spending,
                "clv_indicator": clv_indicator,
                "rating_id": customer.rating_id or 3
            })
        
        df = pd.DataFrame(segmentation_data)
        
        # Enhanced clustering with purchase behavior
        clustering_engine = AdaptiveClusteringEngine({"algorithm": algorithm})
        clustering_result = clustering_engine.fit_transform(df)
        
        # Update customers with new segments
        for i, customer in enumerate(customers):
            customer.segment_id = int(clustering_result['labels'][i])
            customer.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Enhanced insights generation
        insight_generator = IntelligentInsightGenerator()
        insights = insight_generator.generate_comprehensive_insights(clustering_result)
        
        # Add purchase-based segment analysis
        segment_purchase_analysis = {}
        for segment_id in range(clustering_result['n_clusters']):
            segment_customers = [customers[i] for i, label in enumerate(clustering_result['labels']) if label == segment_id]
            segment_data = [segmentation_data[i] for i, label in enumerate(clustering_result['labels']) if label == segment_id]
            
            if segment_data:
                segment_purchase_analysis[segment_id] = {
                    "avg_total_spent": np.mean([d['total_spent'] for d in segment_data]),
                    "avg_purchase_frequency": np.mean([d['purchase_frequency'] for d in segment_data]),
                    "dominant_membership": max(set([c.membership_level for c in segment_customers if c.membership_level]), 
                                             key=[c.membership_level for c in segment_customers if c.membership_level].count) if any(c.membership_level for c in segment_customers) else "未分级",
                    "avg_clv_indicator": np.mean([d['clv_indicator'] for d in segment_data]),
                    "segment_value": "high" if np.mean([d['total_spent'] for d in segment_data]) > np.mean([d['total_spent'] for d in segmentation_data]) else "low"
                }
        
        return {
            "segmentation_completed": True,
            "customers_segmented": len(customers),
            "n_clusters": clustering_result['n_clusters'],
            "silhouette_score": clustering_result['silhouette_score'],
            "algorithm_used": clustering_result['algorithm_used'],
            "cluster_profiles": clustering_result['cluster_profiles'],
            "purchase_based_analysis": segment_purchase_analysis,
            "business_insights": insights,
            "segmentation_features": [
                "age", "gender", "membership_level", "total_spent", 
                "purchase_frequency", "recent_spending", "clv_indicator"
            ]
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Segmentation failed: {str(e)}")

@router.get("/segments/analytics")
async def get_segment_analytics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    customers = db.query(Customer).all()
    
    if not customers:
        return {"message": "No customers found"}
    
    # Enhanced segment analytics with purchase data
    segment_analytics = {}
    segmented_customers = [c for c in customers if c.segment_id is not None]
    
    if not segmented_customers:
        return {"message": "No segmented customers found"}
    
    total_segmented = len(segmented_customers)
    
    for segment_id in set(c.segment_id for c in segmented_customers):
        segment_customers = [c for c in segmented_customers if c.segment_id == segment_id]
        
        # Calculate purchase metrics for this segment
        segment_purchase_data = []
        total_segment_revenue = 0
        total_segment_purchases = 0
        membership_counts = {'橙卡会员': 0, '金卡会员': 0, '钻卡会员': 0, '未分级': 0}
        
        for customer in segment_customers:
            purchases = db.query(Purchase).filter(Purchase.customer_id == customer.customer_id).all()
            customer_total = sum(p.purchase_amount for p in purchases)
            customer_frequency = len(purchases)
            
            total_segment_revenue += customer_total
            total_segment_purchases += customer_frequency
            
            # Count membership levels
            membership_level = customer.membership_level or '未分级'
            if membership_level in membership_counts:
                membership_counts[membership_level] += 1
            else:
                membership_counts['未分级'] += 1
            
            segment_purchase_data.append({
                "customer_id": customer.customer_id,
                "total_spent": customer_total,
                "purchase_count": customer_frequency,
                "avg_purchase": customer_total / customer_frequency if customer_frequency > 0 else 0
            })
        
        # Calculate segment metrics
        avg_segment_revenue = total_segment_revenue / len(segment_customers)
        avg_segment_frequency = total_segment_purchases / len(segment_customers)
        
        # Demographics
        ages = [c.age for c in segment_customers if c.age]
        ratings = [c.rating_id for c in segment_customers if c.rating_id]
        genders = [c.gender for c in segment_customers if c.gender]
        
        analytics = {
            "segment_id": int(segment_id),
            "size": len(segment_customers),
            "percentage": len(segment_customers) / total_segmented * 100,
            "demographics": {
                "avg_age": float(np.mean(ages)) if ages else 0,
                "age_std": float(np.std(ages)) if ages else 0,
                "gender_distribution": {gender: genders.count(gender) for gender in set(genders)} if genders else {},
                "avg_rating": float(np.mean(ratings)) if ratings else 0
            },
            "purchase_analytics": {
                "total_revenue": float(total_segment_revenue),
                "avg_revenue_per_customer": float(avg_segment_revenue),
                "avg_purchase_frequency": float(avg_segment_frequency),
                "revenue_share": float(total_segment_revenue / sum(sum(db.query(func.sum(Purchase.purchase_amount)).filter(Purchase.customer_id == c.customer_id).scalar() or 0 for c in segmented_customers) for _ in [1]) * 100) if sum(sum(db.query(func.sum(Purchase.purchase_amount)).filter(Purchase.customer_id == c.customer_id).scalar() or 0 for c in segmented_customers) for _ in [1]) > 0 else 0
            },
            "membership_distribution": membership_counts,
            "business_insights": {
                "value_tier": "high" if avg_segment_revenue > 1000 else "medium" if avg_segment_revenue > 500 else "low",
                "engagement_level": "high" if avg_segment_frequency > 5 else "medium" if avg_segment_frequency > 2 else "low",
                "dominant_membership": max(membership_counts, key=membership_counts.get),
                "growth_potential": "high" if membership_counts.get('橙卡会员', 0) > membership_counts.get('钻卡会员', 0) else "medium",
                "retention_priority": "high" if avg_segment_revenue > 800 and avg_segment_frequency < 3 else "medium"
            },
            "recommendations": []
        }
        
        # Generate segment-specific recommendations
        if analytics["business_insights"]["value_tier"] == "high":
            analytics["recommendations"].append("Focus on VIP experiences and premium services")
        if analytics["business_insights"]["engagement_level"] == "low":
            analytics["recommendations"].append("Implement engagement campaigns to increase purchase frequency")
        if membership_counts['未分级'] > len(segment_customers) * 0.5:
            analytics["recommendations"].append("Prioritize membership enrollment for this segment")
        if analytics["purchase_analytics"]["avg_purchase_frequency"] > 3:
            analytics["recommendations"].append("This segment shows loyalty - consider referral programs")
        
        segment_analytics[segment_id] = analytics
    
    # Overall metrics with purchase data
    all_purchases = db.query(Purchase).join(Customer, Purchase.customer_id == Customer.customer_id).filter(Customer.segment_id.isnot(None)).all()
    total_revenue_all = sum(p.purchase_amount for p in all_purchases)
    
    return {
        "total_segmented_customers": total_segmented,
        "n_segments": len(segment_analytics),
        "segment_analytics": segment_analytics,
        "overall_metrics": {
            "avg_age": float(np.mean([c.age for c in segmented_customers if c.age])) if any(c.age for c in segmented_customers) else 0,
            "avg_rating": float(np.mean([c.rating_id for c in segmented_customers if c.rating_id])) if any(c.rating_id for c in segmented_customers) else 0,
            "total_revenue": float(total_revenue_all),
            "avg_revenue_per_customer": float(total_revenue_all / total_segmented) if total_segmented > 0 else 0,
            "membership_summary": {
                level: sum(1 for c in segmented_customers if c.membership_level == level)
                for level in ['橙卡会员', '金卡会员', '钻卡会员']
            }
        },
        "segment_comparison": {
            "highest_value_segment": max(segment_analytics.keys(), key=lambda x: segment_analytics[x]["purchase_analytics"]["avg_revenue_per_customer"]) if segment_analytics else None,
            "most_engaged_segment": max(segment_analytics.keys(), key=lambda x: segment_analytics[x]["purchase_analytics"]["avg_purchase_frequency"]) if segment_analytics else None,
            "largest_segment": max(segment_analytics.keys(), key=lambda x: segment_analytics[x]["size"]) if segment_analytics else None
        }
    }

@router.post("/{customer_id}/predict")
async def predict_customer_behavior(
    customer_id: str,
    prediction_type: str = Query(..., regex="^(clv|churn|next_purchase)$"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    try:
        # Get purchase history for enhanced predictions
        purchases = db.query(Purchase).filter(Purchase.customer_id == customer_id).all()
        
        # Calculate enhanced customer metrics
        total_spent = sum(p.purchase_amount for p in purchases)
        avg_purchase = total_spent / len(purchases) if purchases else 0
        purchase_frequency = len(purchases)
        total_points = sum(p.points_earned for p in purchases)
        
        # Recent activity (last 90 days)
        recent_date = datetime.now() - timedelta(days=90)
        recent_purchases = [p for p in purchases if p.purchase_date >= recent_date]
        recent_spending = sum(p.purchase_amount for p in recent_purchases)
        days_since_last_purchase = (datetime.now() - max([p.purchase_date for p in purchases])).days if purchases else 365
        
        # Membership score
        membership_score = {'橙卡会员': 1, '金卡会员': 2, '钻卡会员': 3}.get(customer.membership_level, 0)
        
        # Days since registration
        days_since_registration = (datetime.now() - customer.registration_time).days if customer.registration_time else 365
        
        customer_features = {
            "age": customer.age or 30,
            "rating_id": customer.rating_id or 3,
            "segment_id": customer.segment_id or 0,
            "total_spent": total_spent,
            "avg_purchase": avg_purchase,
            "purchase_frequency": purchase_frequency,
            "recent_spending": recent_spending,
            "days_since_last_purchase": days_since_last_purchase,
            "membership_score": membership_score,
            "days_since_registration": days_since_registration
        }
        
        if prediction_type == "clv":
            # Enhanced CLV prediction based on purchase history and membership
            base_clv = total_spent
            frequency_multiplier = min(purchase_frequency / 10, 2.0)  # Cap at 2x
            membership_multiplier = 1 + (membership_score * 0.3)  # 30% boost per tier
            recency_factor = max(0.5, 1 - (days_since_last_purchase / 365))  # Decay over time
            
            predicted_clv = base_clv * frequency_multiplier * membership_multiplier * recency_factor
            
            # Future value estimation
            monthly_avg = total_spent / max(days_since_registration / 30, 1)
            future_12m_value = monthly_avg * 12 * recency_factor
            
            prediction = {
                "customer_lifetime_value": float(predicted_clv + future_12m_value),
                "current_value": float(total_spent),
                "predicted_future_value": float(future_12m_value),
                "confidence": min(0.95, 0.6 + (purchase_frequency / 50)),
                "factors": ["purchase_history", "membership_level", "recency", "frequency"],
                "prediction_horizon": "12_months",
                "membership_impact": f"{membership_multiplier:.1f}x multiplier",
                "risk_assessment": "low" if recency_factor > 0.7 else "medium" if recency_factor > 0.4 else "high"
            }
            
        elif prediction_type == "churn":
            # Enhanced churn prediction
            base_churn = max(0.1, min(0.9, (5 - customer.rating_id) / 4))
            
            # Adjust based on purchase behavior
            recency_factor = min(days_since_last_purchase / 90, 1.0)  # Higher = more likely to churn
            frequency_factor = max(0, 1 - purchase_frequency / 20)  # Lower frequency = higher churn
            spending_factor = max(0, 1 - recent_spending / (total_spent / max(days_since_registration / 90, 1)))
            membership_factor = max(0, 1 - membership_score * 0.2)
            
            churn_probability = (base_churn + recency_factor + frequency_factor + spending_factor + membership_factor) / 5
            churn_probability = max(0.05, min(0.95, churn_probability))
            
            # Risk factors identification
            risk_factors = []
            if days_since_last_purchase > 60:
                risk_factors.append("long_time_since_last_purchase")
            if purchase_frequency < 3:
                risk_factors.append("low_purchase_frequency")
            if recent_spending < avg_purchase:
                risk_factors.append("declining_spending")
            if membership_score == 0:
                risk_factors.append("no_membership_tier")
            
            prediction = {
                "churn_probability": float(churn_probability),
                "risk_level": "high" if churn_probability > 0.7 else "medium" if churn_probability > 0.4 else "low",
                "key_factors": risk_factors,
                "days_since_last_purchase": days_since_last_purchase,
                "purchase_frequency": purchase_frequency,
                "membership_protection": f"{(1-membership_factor)*100:.1f}% protection from membership",
                "recommended_actions": _get_retention_actions(churn_probability, risk_factors, membership_score)
            }
            
        else:  # next_purchase
            # Enhanced next purchase prediction
            if purchases:
                # Calculate average days between purchases
                purchase_dates = sorted([p.purchase_date for p in purchases])
                if len(purchase_dates) > 1:
                    intervals = [(purchase_dates[i+1] - purchase_dates[i]).days for i in range(len(purchase_dates)-1)]
                    avg_interval = np.mean(intervals)
                else:
                    avg_interval = 30  # Default
            else:
                avg_interval = 60  # Default for new customers
            
            # Adjust based on membership and recent activity
            membership_acceleration = 1 - (membership_score * 0.1)  # Higher tier = shorter intervals
            recent_activity_factor = 0.8 if recent_spending > avg_purchase else 1.2
            
            predicted_days = int(avg_interval * membership_acceleration * recent_activity_factor)
            predicted_days = max(1, min(predicted_days, 180))  # Between 1-180 days
            
            # Purchase probability based on historical patterns
            purchase_probability = min(0.95, 0.3 + (purchase_frequency / 20) + (membership_score * 0.1))
            
            # Recommended products based on purchase history
            if purchases:
                business_types = [p.business_type for p in purchases if p.business_type]
                recommended_products = list(set(business_types))[:3] if business_types else ["general_retail"]
            else:
                recommended_products = ["general_retail", "fashion", "electronics"]
            
            prediction = {
                "days_to_next_purchase": predicted_days,
                "purchase_probability": float(purchase_probability),
                "recommended_products": recommended_products,
                "optimal_contact_time": _get_optimal_contact_time(customer, purchases),
                "predicted_amount": float(avg_purchase * 1.1),  # Slight increase prediction
                "confidence": min(0.9, 0.5 + (purchase_frequency / 30)),
                "based_on_pattern": f"avg {avg_interval:.0f} days between purchases"
            }
        
        return {
            "customer_id": customer_id,
            "prediction_type": prediction_type,
            "prediction": prediction,
            "customer_metrics": customer_features,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

def _get_retention_actions(churn_prob: float, risk_factors: List[str], membership_score: int) -> List[str]:
    """Generate targeted retention actions based on churn risk"""
    actions = []
    
    if churn_prob > 0.7:
        actions.extend(["immediate_personal_contact", "exclusive_discount", "loyalty_bonus"])
    elif churn_prob > 0.4:
        actions.extend(["targeted_email_campaign", "personalized_offers", "membership_upgrade_incentive"])
    else:
        actions.extend(["regular_engagement", "seasonal_promotions"])
    
    if "long_time_since_last_purchase" in risk_factors:
        actions.append("win_back_campaign")
    if "low_purchase_frequency" in risk_factors:
        actions.append("engagement_program")
    if "no_membership_tier" in risk_factors:
        actions.append("membership_enrollment_offer")
        
    return list(set(actions))

def _get_optimal_contact_time(customer: Customer, purchases: List[Purchase]) -> str:
    """Determine optimal contact time based on purchase patterns"""
    if not purchases:
        return "afternoon"
    
    # Simple heuristic based on membership level and age
    if customer.membership_level in ['金卡会员', '钻卡会员']:
        return "morning"  # Premium customers prefer morning
    elif customer.age and customer.age < 35:
        return "evening"  # Younger customers prefer evening
    else:
        return "afternoon"  # Default

@router.get("/insights/real-time")
async def get_real_time_insights(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Basic customer metrics
        total_customers = db.query(Customer).count()
        recent_customers = db.query(Customer).filter(
            Customer.created_at >= datetime.now() - timedelta(days=7)
        ).count()
        
        # Purchase analytics
        total_purchases = db.query(Purchase).count()
        recent_purchases = db.query(Purchase).filter(
            Purchase.purchase_date >= datetime.now() - timedelta(days=7)
        ).count()
        
        total_revenue = db.query(func.sum(Purchase.purchase_amount)).scalar() or 0
        recent_revenue = db.query(func.sum(Purchase.purchase_amount)).filter(
            Purchase.purchase_date >= datetime.now() - timedelta(days=7)
        ).scalar() or 0
        
        avg_purchase_amount = db.query(func.avg(Purchase.purchase_amount)).scalar() or 0
        
        # Membership analytics
        membership_distribution = {}
        for level in ['橙卡会员', '金卡会员', '钻卡会员']:
            count = db.query(Customer).filter(Customer.membership_level == level).count()
            membership_distribution[level] = count
        
        # High-value customer identification
        high_spenders = db.query(Customer.customer_id, func.sum(Purchase.purchase_amount).label('total_spent')).join(
            Purchase, Customer.customer_id == Purchase.customer_id
        ).group_by(Customer.customer_id).having(
            func.sum(Purchase.purchase_amount) > avg_purchase_amount * 3
        ).count()
        
        # Churn risk analysis
        inactive_threshold = datetime.now() - timedelta(days=90)
        customers_with_purchases = db.query(Customer.customer_id, func.max(Purchase.purchase_date).label('last_purchase')).join(
            Purchase, Customer.customer_id == Purchase.customer_id
        ).group_by(Customer.customer_id).subquery()
        
        at_risk_customers = db.query(customers_with_purchases).filter(
            customers_with_purchases.c.last_purchase < inactive_threshold
        ).count()
        
        # Trending analysis
        segments_with_revenue = db.query(
            Customer.segment_id,
            func.count(Customer.id).label('customer_count'),
            func.sum(Purchase.purchase_amount).label('total_revenue')
        ).join(Purchase, Customer.customer_id == Purchase.customer_id).filter(
            Customer.segment_id.isnot(None)
        ).group_by(Customer.segment_id).all()
        
        # Generate AI alerts
        alerts = []
        
        if recent_revenue > 0 and total_revenue > 0:
            weekly_growth = (recent_revenue / (total_revenue - recent_revenue)) * 100 if total_revenue > recent_revenue else 0
            if weekly_growth > 20:
                alerts.append({
                    "type": "opportunity",
                    "message": f"Revenue growth of {weekly_growth:.1f}% this week - consider scaling successful campaigns",
                    "priority": "high",
                    "action": "scale_campaigns"
                })
        
        if at_risk_customers > total_customers * 0.15:
            alerts.append({
                "type": "warning",
                "message": f"{at_risk_customers} customers haven't purchased in 90+ days - immediate retention needed",
                "priority": "high",
                "action": "launch_retention_campaign"
            })
        
        if membership_distribution.get('钻卡会员', 0) > membership_distribution.get('橙卡会员', 0):
            alerts.append({
                "type": "insight",
                "message": "Premium membership adoption is strong - consider expanding premium offerings",
                "priority": "medium",
                "action": "expand_premium_services"
            })
        
        # Smart recommendations
        recommendations = []
        
        if high_spenders > 0:
            recommendations.append(f"Target {high_spenders} high-value customers with VIP experiences")
        
        if at_risk_customers > 0:
            recommendations.append(f"Implement win-back campaigns for {at_risk_customers} inactive customers")
        
        if total_purchases > 0 and recent_purchases / total_purchases < 0.1:
            recommendations.append("Purchase activity is low - consider promotional campaigns")
        
        best_performing_segment = max(segments_with_revenue, key=lambda x: x.total_revenue) if segments_with_revenue else None
        if best_performing_segment:
            recommendations.append(f"Segment {best_performing_segment.segment_id} is highest revenue - analyze and replicate success patterns")
        
        insights = {
            "timestamp": datetime.now().isoformat(),
            "key_metrics": {
                "total_customers": total_customers,
                "new_customers_7d": recent_customers,
                "total_purchases": total_purchases,
                "recent_purchases_7d": recent_purchases,
                "total_revenue": float(total_revenue),
                "recent_revenue_7d": float(recent_revenue),
                "avg_purchase_amount": float(avg_purchase_amount),
                "high_value_customers": high_spenders,
                "at_risk_customers": at_risk_customers,
                "growth_rate_7d": (recent_customers / max(1, total_customers - recent_customers)) * 100
            },
            "membership_analytics": {
                "distribution": membership_distribution,
                "total_members": sum(membership_distribution.values()),
                "premium_ratio": (membership_distribution.get('金卡会员', 0) + membership_distribution.get('钻卡会员', 0)) / max(1, total_customers) * 100
            },
            "purchase_insights": {
                "purchase_velocity": recent_purchases / 7 if recent_purchases > 0 else 0,
                "revenue_per_customer": float(total_revenue / max(1, total_customers)),
                "avg_weekly_revenue": float(recent_revenue),
                "purchase_frequency": float(total_purchases / max(1, total_customers))
            },
            "ai_alerts": alerts,
            "trending_segments": [
                {
                    "segment_id": seg.segment_id,
                    "customer_count": seg.customer_count,
                    "total_revenue": float(seg.total_revenue),
                    "avg_revenue_per_customer": float(seg.total_revenue / seg.customer_count)
                }
                for seg in segments_with_revenue
            ],
            "recommendations": recommendations
        }
        
        return insights
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")

@router.post("/export")
async def export_customer_data(
    format: str = Query("csv", regex="^(csv|excel|json)$"),
    segment_ids: List[int] = Query(None),
    include_predictions: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        query = db.query(Customer)
        
        if segment_ids:
            query = query.filter(Customer.segment_id.in_(segment_ids))
        
        customers = query.all()
        
        export_data = []
        for customer in customers:
            customer_data = {
                "customer_id": customer.customer_id,
                "age": customer.age,
                "gender": customer.gender,
                "rating_id": customer.rating_id,
                "segment_id": customer.segment_id,
                "created_at": customer.created_at.isoformat()
            }
            
            if include_predictions:
                customer_data.update({
                    "predicted_clv": customer.age * customer.rating_id * 100 + 500,
                    "churn_risk": "low" if customer.rating_id >= 4 else "medium"
                })
            
            export_data.append(customer_data)
        
        if format == "csv":
            df = pd.DataFrame(export_data)
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            
            return JSONResponse(
                content={"data": csv_buffer.getvalue(), "format": "csv"},
                headers={"Content-Disposition": "attachment; filename=customers.csv"}
            )
        
        elif format == "json":
            return JSONResponse(content={"data": export_data, "format": "json"})
        
        else:  # excel
            df = pd.DataFrame(export_data)
            excel_buffer = io.BytesIO()
            df.to_excel(excel_buffer, index=False)
            
            return JSONResponse(
                content={"data": excel_buffer.getvalue().hex(), "format": "excel"},
                headers={"Content-Disposition": "attachment; filename=customers.xlsx"}
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")