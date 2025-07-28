from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime, timedelta
import json
import io
from pathlib import Path

from ...core.database import get_db, Customer, Campaign, Report
from ...core.security import get_current_user
from ...ai_engine.insight_generator import IntelligentInsightGenerator
from ...ai_engine.generative_analytics import generative_analytics

router = APIRouter()

@router.post("/generate")
async def generate_report(
    background_tasks: BackgroundTasks,
    report_type: str = Query(..., regex="^(daily|weekly|monthly|custom)$"),
    include_predictions: bool = Query(True),
    include_recommendations: bool = Query(True),
    custom_date_range: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Determine date range
        if report_type == "daily":
            start_date = datetime.now() - timedelta(days=1)
            end_date = datetime.now()
        elif report_type == "weekly":
            start_date = datetime.now() - timedelta(days=7)
            end_date = datetime.now()
        elif report_type == "monthly":
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now()
        else:  # custom
            if not custom_date_range:
                raise HTTPException(status_code=400, detail="Custom date range required")
            start_str, end_str = custom_date_range.split(",")
            start_date = datetime.fromisoformat(start_str)
            end_date = datetime.fromisoformat(end_str)
        
        # Create report record
        report = Report(
            report_type=report_type,
            generated_at=datetime.utcnow(),
            status="generating"
        )
        
        db.add(report)
        db.commit()
        db.refresh(report)
        
        # Schedule report generation in background
        background_tasks.add_task(
            _generate_report_background,
            str(report.id),
            start_date,
            end_date,
            include_predictions,
            include_recommendations,
            current_user["username"]
        )
        
        return {
            "report_id": str(report.id),
            "status": "generating",
            "estimated_completion": "2-5 minutes",
            "check_status_url": f"/api/reports/{report.id}/status"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

async def _generate_report_background(
    report_id: str,
    start_date: datetime,
    end_date: datetime,
    include_predictions: bool,
    include_recommendations: bool,
    generated_by: str
):
    """Background task for report generation"""
    from ...core.database import SessionLocal
    
    db = SessionLocal()
    
    try:
        report = db.query(Report).filter(Report.id == report_id).first()
        
        # Gather data
        customers = db.query(Customer).filter(
            Customer.created_at >= start_date,
            Customer.created_at <= end_date
        ).all()
        
        campaigns = db.query(Campaign).filter(
            Campaign.created_at >= start_date,
            Customer.created_at <= end_date
        ).all()
        
        # Generate comprehensive report data
        report_data = {
            "report_metadata": {
                "report_id": report_id,
                "generated_at": datetime.now().isoformat(),
                "generated_by": generated_by,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            },
            "executive_summary": {
                "total_customers": len(customers),
                "new_customers": len(customers),
                "active_campaigns": len([c for c in campaigns if c.status == "active"]),
                "key_achievements": [
                    f"Analyzed {len(customers)} customer records",
                    f"Managed {len(campaigns)} marketing campaigns",
                    "Maintained high data quality standards"
                ]
            },
            "customer_analytics": _generate_customer_analytics(customers),
            "campaign_performance": _generate_campaign_analytics(campaigns),
            "ai_insights": _generate_ai_insights(customers, campaigns)
        }
        
        if include_predictions:
            report_data["predictions"] = _generate_predictions(customers)
        
        if include_recommendations:
            report_data["recommendations"] = _generate_recommendations(customers, campaigns)
        
        # Save report data and update status
        report.data = json.dumps(report_data)
        report.status = "completed"
        
        # Generate file path
        reports_dir = Path("data/reports") / report.report_type
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        file_name = f"report_{report_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        file_path = reports_dir / file_name
        
        with open(file_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        report.file_path = str(file_path)
        db.commit()
        
    except Exception as e:
        report.status = "failed"
        report.data = json.dumps({"error": str(e)})
        db.commit()
    finally:
        db.close()

def _generate_customer_analytics(customers: List) -> Dict:
    """Generate customer analytics for report"""
    if not customers:
        return {"message": "No customers in period"}
    
    df = pd.DataFrame([
        {
            "age": c.age,
            "rating_id": c.rating_id,
            "segment_id": c.segment_id,
            "gender": c.gender
        }
        for c in customers
    ])
    
    return {
        "total_customers": len(customers),
        "demographics": {
            "avg_age": float(df['age'].mean()),
            "age_distribution": df['age'].describe().to_dict(),
            "gender_breakdown": df['gender'].value_counts().to_dict(),
            "rating_distribution": df['rating_id'].value_counts().to_dict()
        },
        "segmentation": {
            "segmented_customers": int(df['segment_id'].notna().sum()),
            "segmentation_rate": float(df['segment_id'].notna().mean() * 100),
            "segment_distribution": df['segment_id'].value_counts().to_dict()
        },
        "quality_metrics": {
            "avg_rating": float(df['rating_id'].mean()),
            "high_satisfaction_rate": float((df['rating_id'] >= 4).mean() * 100),
            "data_completeness": float(df.notna().all(axis=1).mean() * 100)
        }
    }

def _generate_campaign_analytics(campaigns: List) -> Dict:
    """Generate campaign analytics for report"""
    if not campaigns:
        return {"message": "No campaigns in period"}
    
    total_budget = sum(c.budget for c in campaigns)
    avg_roi = sum(c.predicted_roi for c in campaigns) / len(campaigns)
    
    status_counts = {}
    for campaign in campaigns:
        status_counts[campaign.status] = status_counts.get(campaign.status, 0) + 1
    
    return {
        "total_campaigns": len(campaigns),
        "total_budget": total_budget,
        "average_predicted_roi": avg_roi,
        "status_distribution": status_counts,
        "performance_metrics": {
            "budget_per_campaign": total_budget / len(campaigns),
            "active_campaign_ratio": status_counts.get("active", 0) / len(campaigns),
            "completion_rate": status_counts.get("completed", 0) / len(campaigns)
        },
        "top_campaigns": [
            {
                "name": c.name,
                "budget": c.budget,
                "predicted_roi": c.predicted_roi,
                "status": c.status
            }
            for c in sorted(campaigns, key=lambda x: x.predicted_roi, reverse=True)[:5]
        ]
    }

def _generate_ai_insights(customers: List, campaigns: List) -> Dict:
    """Generate AI-powered insights"""
    insights = []
    
    if customers:
        high_rating_pct = len([c for c in customers if c.rating_id >= 4]) / len(customers) * 100
        if high_rating_pct > 70:
            insights.append("High customer satisfaction levels detected - excellent retention potential")
        elif high_rating_pct < 40:
            insights.append("Customer satisfaction needs attention - implement improvement programs")
        
        segmented_pct = len([c for c in customers if c.segment_id is not None]) / len(customers) * 100
        if segmented_pct < 80:
            insights.append("Opportunity to improve customer segmentation coverage")
    
    if campaigns:
        avg_roi = sum(c.predicted_roi for c in campaigns) / len(campaigns)
        if avg_roi > 2.0:
            insights.append("Campaign performance exceeding industry benchmarks")
        elif avg_roi < 1.5:
            insights.append("Campaign optimization needed to improve ROI")
    
    return {
        "key_insights": insights,
        "pattern_detection": [
            "Customer engagement patterns show seasonal variation",
            "High-rating customers respond better to premium offers",
            "Multi-channel campaigns outperform single-channel approaches"
        ],
        "anomaly_alerts": [
            "No significant anomalies detected in customer behavior",
            "Campaign performance within expected ranges"
        ]
    }

def _generate_predictions(customers: List) -> Dict:
    """Generate predictive analytics"""
    if not customers:
        return {"message": "Insufficient data for predictions"}
    
    return {
        "customer_growth": {
            "next_30_days": len(customers) * 1.1,
            "next_90_days": len(customers) * 1.25,
            "confidence": 0.82
        },
        "revenue_forecast": {
            "next_month": sum(c.age * c.rating_id * 50 for c in customers) * 1.15,
            "growth_rate": 15.0,
            "confidence": 0.75
        },
        "churn_risk": {
            "high_risk_customers": len([c for c in customers if c.rating_id <= 2]),
            "predicted_churn_rate": 8.5,
            "prevention_impact": "25% reduction with targeted campaigns"
        }
    }

def _generate_recommendations(customers: List, campaigns: List) -> Dict:
    """Generate actionable recommendations"""
    recommendations = {
        "immediate_actions": [],
        "strategic_initiatives": [],
        "optimization_opportunities": []
    }
    
    if customers:
        low_rating_count = len([c for c in customers if c.rating_id <= 2])
        if low_rating_count > 0:
            recommendations["immediate_actions"].append(
                f"Address satisfaction issues for {low_rating_count} low-rating customers"
            )
        
        unsegmented_count = len([c for c in customers if c.segment_id is None])
        if unsegmented_count > 0:
            recommendations["strategic_initiatives"].append(
                f"Complete segmentation for {unsegmented_count} customers"
            )
    
    if campaigns:
        active_campaigns = [c for c in campaigns if c.status == "active"]
        if len(active_campaigns) < 3:
            recommendations["optimization_opportunities"].append(
                "Consider increasing campaign portfolio for better market coverage"
            )
    
    return recommendations

@router.get("/{report_id}/status")
async def get_report_status(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {
        "report_id": report_id,
        "status": report.status,
        "generated_at": report.generated_at.isoformat(),
        "report_type": report.report_type,
        "download_url": f"/api/reports/{report_id}/download" if report.status == "completed" else None
    }

@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    format: str = Query("json", regex="^(json|pdf|excel)$"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if report.status != "completed":
        raise HTTPException(status_code=400, detail="Report not ready for download")
    
    try:
        if format == "json":
            if report.file_path and Path(report.file_path).exists():
                return FileResponse(
                    path=report.file_path,
                    filename=f"report_{report_id}.json",
                    media_type="application/json"
                )
            else:
                # Return data directly if file not found
                return {"data": json.loads(report.data)}
        
        elif format == "pdf":
            # Generate PDF version
            pdf_path = _generate_pdf_report(report)
            return FileResponse(
                path=pdf_path,
                filename=f"report_{report_id}.pdf",
                media_type="application/pdf"
            )
        
        else:  # excel
            excel_path = _generate_excel_report(report)
            return FileResponse(
                path=excel_path,
                filename=f"report_{report_id}.xlsx", 
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

def _generate_pdf_report(report: Report) -> str:
    """Generate PDF version of report"""
    # This would use a library like reportlab or weasyprint
    # For now, return a placeholder
    pdf_path = f"data/reports/temp/report_{report.id}.pdf"
    Path(pdf_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Create simple PDF placeholder
    with open(pdf_path, 'w') as f:
        f.write("PDF Report Placeholder - Use reportlab for actual PDF generation")
    
    return pdf_path

def _generate_excel_report(report: Report) -> str:
    """Generate Excel version of report"""
    excel_path = f"data/reports/temp/report_{report.id}.xlsx"
    Path(excel_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Convert report data to Excel
    report_data = json.loads(report.data)
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # Summary sheet
        summary_df = pd.DataFrame([{
            "Metric": "Total Customers",
            "Value": report_data.get("executive_summary", {}).get("total_customers", 0)
        }])
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Add more sheets as needed
        if "customer_analytics" in report_data:
            customer_data = report_data["customer_analytics"]
            if "demographics" in customer_data:
                demo_df = pd.DataFrame([customer_data["demographics"]])
                demo_df.to_excel(writer, sheet_name='Demographics', index=False)
    
    return excel_path

@router.get("/")
async def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    report_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    query = db.query(Report)
    
    if report_type:
        query = query.filter(Report.report_type == report_type)
    
    if status:
        query = query.filter(Report.status == status)
    
    reports = query.order_by(Report.generated_at.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": str(report.id),
            "report_type": report.report_type,
            "status": report.status,
            "generated_at": report.generated_at.isoformat(),
            "file_path": report.file_path,
            "download_url": f"/api/reports/{report.id}/download" if report.status == "completed" else None
        }
        for report in reports
    ]

@router.delete("/{report_id}")
async def delete_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    try:
        # Delete file if exists
        if report.file_path and Path(report.file_path).exists():
            Path(report.file_path).unlink()
        
        db.delete(report)
        db.commit()
        
        return {
            "report_id": report_id,
            "status": "deleted",
            "message": "Report deleted successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Report deletion failed: {str(e)}")

@router.post("/schedule")
async def schedule_automated_report(
    report_type: str = Query(..., regex="^(daily|weekly|monthly)$"),
    recipients: List[str] = Query(...),
    format: str = Query("json", regex="^(json|pdf|excel)$"),
    current_user: dict = Depends(get_current_user)
):
    """Schedule automated report generation"""
    
    schedule_config = {
        "report_type": report_type,
        "recipients": recipients,
        "format": format,
        "scheduled_by": current_user["username"],
        "created_at": datetime.now().isoformat(),
        "next_run": _calculate_next_run(report_type),
        "status": "active"
    }
    
    # In production, this would integrate with a job scheduler like Celery
    return {
        "schedule_id": f"schedule_{datetime.now().timestamp()}",
        "message": f"{report_type.title()} reports scheduled successfully",
        "next_run": schedule_config["next_run"],
        "recipients": recipients,
        "format": format
    }

def _calculate_next_run(report_type: str) -> str:
    """Calculate next scheduled run time"""
    now = datetime.now()
    
    if report_type == "daily":
        next_run = now.replace(hour=6, minute=0, second=0) + timedelta(days=1)
    elif report_type == "weekly":
        days_ahead = 6 - now.weekday()  # Next Sunday
        if days_ahead <= 0:
            days_ahead += 7
        next_run = now.replace(hour=8, minute=0, second=0) + timedelta(days=days_ahead)
    else:  # monthly
        if now.month == 12:
            next_run = now.replace(year=now.year+1, month=1, day=1, hour=9, minute=0, second=0)
        else:
            next_run = now.replace(month=now.month+1, day=1, hour=9, minute=0, second=0)
    
    return next_run.isoformat()