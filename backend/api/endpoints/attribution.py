"""
Revenue Attribution API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.security import get_current_user, require_permission
from ...revenue.attribution_engine import (
    RevenueAttributionEngine, 
    AttributionModel, 
    ConversionType,
    TouchpointType
)

router = APIRouter()

class ConversionRequest(BaseModel):
    customer_id: str
    conversion_data: Dict[str, Any]
    attribution_model: Optional[str] = AttributionModel.LINEAR
    attribution_window_days: Optional[int] = 30

class CustomModelRequest(BaseModel):
    name: str
    model_type: str = AttributionModel.CUSTOM
    description: Optional[str] = ""
    config: Dict[str, Any] = {}
    attribution_window_days: int = 30
    lookback_window_days: int = 90
    touchpoint_weights: Dict[str, float] = {}
    position_weights: Dict[str, float] = {}
    time_decay_rate: float = 0.5

class AttributionResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

@router.post("/analyze-conversion", response_model=AttributionResponse)
async def analyze_conversion_attribution(
    request: ConversionRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze revenue attribution for a conversion"""
    try:
        attribution_engine = RevenueAttributionEngine(db)
        
        result = attribution_engine.analyze_conversion_attribution(
            customer_id=request.customer_id,
            conversion_data=request.conversion_data,
            attribution_model=request.attribution_model,
            attribution_window_days=request.attribution_window_days
        )
        
        return AttributionResponse(
            success=True,
            message="Attribution analysis completed successfully",
            data={
                "conversion_id": result.conversion_id,
                "customer_id": result.customer_id,
                "total_revenue": result.total_revenue,
                "attribution_model": result.attribution_model,
                "model_confidence": result.model_confidence,
                "touchpoint_attributions": result.touchpoint_attributions,
                "journey_summary": result.journey_summary
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Attribution analysis failed: {str(e)}")

@router.get("/campaign/{campaign_id}/report")
async def get_campaign_attribution_report(
    campaign_id: str,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: dict = Depends(require_permission("view_analytics")),
    db: Session = Depends(get_db)
):
    """Get comprehensive attribution report for a campaign"""
    try:
        attribution_engine = RevenueAttributionEngine(db)
        
        report = attribution_engine.get_campaign_attribution_report(
            campaign_id=campaign_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate campaign report: {str(e)}")

@router.get("/channel-performance")
async def get_channel_performance_analysis(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: dict = Depends(require_permission("view_analytics")),
    db: Session = Depends(get_db)
):
    """Analyze performance across all marketing channels"""
    try:
        attribution_engine = RevenueAttributionEngine(db)
        
        channel_performance = attribution_engine.get_channel_performance_analysis(
            start_date=start_date,
            end_date=end_date
        )
        
        # Convert to dict format for JSON response
        channel_data = []
        for channel in channel_performance:
            channel_data.append({
                "channel": channel.channel,
                "total_revenue": channel.total_revenue,
                "attributed_conversions": channel.attributed_conversions,
                "avg_attribution_percentage": channel.avg_attribution_percentage,
                "first_touch_revenue": channel.first_touch_revenue,
                "last_touch_revenue": channel.last_touch_revenue,
                "assisted_revenue": channel.assisted_revenue
            })
        
        return {
            "analysis_period": {
                "start_date": start_date.isoformat() if start_date else (datetime.now() - timedelta(days=30)).isoformat(),
                "end_date": end_date.isoformat() if end_date else datetime.now().isoformat()
            },
            "channel_performance": channel_data,
            "summary": {
                "total_channels": len(channel_data),
                "total_revenue": sum(c["total_revenue"] for c in channel_data),
                "total_conversions": sum(c["attributed_conversions"] for c in channel_data),
                "top_performing_channel": max(channel_data, key=lambda x: x["total_revenue"])["channel"] if channel_data else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Channel analysis failed: {str(e)}")

@router.post("/custom-model", response_model=AttributionResponse)
async def create_custom_attribution_model(
    request: CustomModelRequest,
    current_user: dict = Depends(require_permission("manage_attribution")),
    db: Session = Depends(get_db)
):
    """Create a custom attribution model"""
    try:
        attribution_engine = RevenueAttributionEngine(db)
        
        model_config = {
            "name": request.name,
            "type": request.model_type,
            "description": request.description,
            "config": request.config,
            "attribution_window_days": request.attribution_window_days,
            "lookback_window_days": request.lookback_window_days,
            "touchpoint_weights": request.touchpoint_weights,
            "position_weights": request.position_weights,
            "time_decay_rate": request.time_decay_rate
        }
        
        model_id = attribution_engine.create_custom_attribution_model(model_config)
        
        return AttributionResponse(
            success=True,
            message=f"Custom attribution model '{request.name}' created successfully",
            data={"model_id": model_id}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create custom model: {str(e)}")

@router.get("/insights")
async def get_attribution_insights(
    timeframe_days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(require_permission("view_analytics")),
    db: Session = Depends(get_db)
):
    """Get comprehensive attribution insights and recommendations"""
    try:
        attribution_engine = RevenueAttributionEngine(db)
        
        insights = attribution_engine.get_attribution_insights(timeframe_days)
        
        return insights
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get attribution insights: {str(e)}")

@router.get("/models")
async def list_attribution_models(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all available attribution models"""
    try:
        from ...revenue.attribution_engine import AttributionModel as ModelDB
        
        # Get custom models from database
        custom_models = db.query(ModelDB).filter(ModelDB.is_active == True).all()
        
        # Standard models
        standard_models = [
            {
                "id": "first_touch",
                "name": "First Touch",
                "type": "standard",
                "description": "100% credit to the first touchpoint",
                "attribution_window_days": 30,
                "is_active": True
            },
            {
                "id": "last_touch", 
                "name": "Last Touch",
                "type": "standard",
                "description": "100% credit to the last touchpoint",
                "attribution_window_days": 30,
                "is_active": True
            },
            {
                "id": "linear",
                "name": "Linear",
                "type": "standard", 
                "description": "Equal credit to all touchpoints",
                "attribution_window_days": 30,
                "is_active": True
            },
            {
                "id": "time_decay",
                "name": "Time Decay",
                "type": "standard",
                "description": "More credit to touchpoints closer to conversion",
                "attribution_window_days": 30,
                "is_active": True
            },
            {
                "id": "position_based",
                "name": "Position Based",
                "type": "standard",
                "description": "40% first, 40% last, 20% middle touchpoints",
                "attribution_window_days": 30,
                "is_active": True
            }
        ]
        
        # Convert custom models
        custom_model_data = []
        for model in custom_models:
            custom_model_data.append({
                "id": model.id,
                "name": model.name,
                "type": "custom",
                "description": model.description,
                "attribution_window_days": model.attribution_window_days,
                "lookback_window_days": model.lookback_window_days,
                "model_config": model.model_config,
                "touchpoint_weights": model.touchpoint_weights,
                "position_weights": model.position_weights,
                "time_decay_rate": model.time_decay_rate,
                "accuracy_score": model.accuracy_score,
                "last_trained": model.last_trained.isoformat() if model.last_trained else None,
                "is_active": model.is_active,
                "created_at": model.created_at.isoformat()
            })
        
        return {
            "standard_models": standard_models,
            "custom_models": custom_model_data,
            "total_models": len(standard_models) + len(custom_model_data),
            "recommended_model": "linear"  # Default recommendation
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list attribution models: {str(e)}")

@router.get("/dashboard")
async def get_attribution_dashboard(
    time_range: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_user: dict = Depends(require_permission("view_analytics")),
    db: Session = Depends(get_db)
):
    """Get attribution dashboard overview"""
    try:
        from ...revenue.attribution_engine import RevenueAttribution, AttributionTouchpoint
        
        # Calculate time range
        time_mapping = {
            "7d": timedelta(days=7),
            "30d": timedelta(days=30), 
            "90d": timedelta(days=90),
            "1y": timedelta(days=365)
        }
        
        end_date = datetime.now()
        start_date = end_date - time_mapping[time_range]
        
        # Get attribution data
        attributions = db.query(RevenueAttribution).filter(
            RevenueAttribution.conversion_date.between(start_date, end_date)
        ).all()
        
        if not attributions:
            return {
                "message": "No attribution data found for the specified time range",
                "time_range": time_range,
                "summary_metrics": {
                    "total_conversions": 0,
                    "total_revenue": 0,
                    "avg_conversion_value": 0,
                    "unique_customers": 0
                }
            }
        
        # Summary metrics
        total_conversions = len(attributions)
        total_revenue = sum(a.conversion_value for a in attributions)
        avg_conversion_value = total_revenue / total_conversions
        unique_customers = len(set(a.customer_id for a in attributions))
        
        # Model usage breakdown
        model_usage = defaultdict(int)
        for attribution in attributions:
            model_usage[attribution.attribution_model] += 1
        
        # Revenue by attribution model
        model_revenue = defaultdict(float)
        for attribution in attributions:
            model_revenue[attribution.attribution_model] += attribution.conversion_value
        
        # Top performing touchpoints
        touchpoints = db.query(AttributionTouchpoint).join(
            RevenueAttribution, AttributionTouchpoint.attribution_id == RevenueAttribution.id
        ).filter(
            RevenueAttribution.conversion_date.between(start_date, end_date)
        ).all()
        
        touchpoint_performance = defaultdict(lambda: {"revenue": 0, "count": 0})
        for tp in touchpoints:
            touchpoint_performance[tp.touchpoint_type]["revenue"] += tp.attributed_revenue
            touchpoint_performance[tp.touchpoint_type]["count"] += 1
        
        top_touchpoints = sorted(
            [{"type": k, "revenue": v["revenue"], "count": v["count"]} 
             for k, v in touchpoint_performance.items()],
            key=lambda x: x["revenue"],
            reverse=True
        )[:10]
        
        # Conversion trends (daily)
        daily_conversions = defaultdict(lambda: {"count": 0, "revenue": 0})
        for attribution in attributions:
            day = attribution.conversion_date.date().isoformat()
            daily_conversions[day]["count"] += 1
            daily_conversions[day]["revenue"] += attribution.conversion_value
        
        return {
            "time_range": time_range,
            "analysis_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary_metrics": {
                "total_conversions": total_conversions,
                "total_revenue": total_revenue,
                "avg_conversion_value": avg_conversion_value,
                "unique_customers": unique_customers,
                "attribution_coverage": (total_conversions / max(1, unique_customers)) * 100
            },
            "model_performance": {
                "model_usage": dict(model_usage),
                "model_revenue": dict(model_revenue),
                "most_used_model": max(model_usage.items(), key=lambda x: x[1])[0] if model_usage else None,
                "highest_revenue_model": max(model_revenue.items(), key=lambda x: x[1])[0] if model_revenue else None
            },
            "touchpoint_analysis": {
                "top_performing_touchpoints": top_touchpoints,
                "total_touchpoints_analyzed": len(touchpoints),
                "avg_touchpoints_per_conversion": len(touchpoints) / max(1, total_conversions)
            },
            "conversion_trends": {
                "daily_data": dict(daily_conversions),
                "peak_day": max(daily_conversions.items(), key=lambda x: x[1]["revenue"])[0] if daily_conversions else None,
                "trend_direction": _calculate_trend_direction(dict(daily_conversions))
            },
            "recommendations": _generate_dashboard_recommendations(
                attributions, touchpoints, model_usage, model_revenue
            )
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get attribution dashboard: {str(e)}")

@router.get("/conversion/{conversion_id}")
async def get_conversion_attribution_details(
    conversion_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed attribution breakdown for a specific conversion"""
    try:
        from ...revenue.attribution_engine import RevenueAttribution, AttributionTouchpoint
        
        # Get attribution record
        attribution = db.query(RevenueAttribution).filter(
            RevenueAttribution.conversion_id == conversion_id
        ).first()
        
        if not attribution:
            raise HTTPException(status_code=404, detail="Conversion attribution not found")
        
        # Get touchpoints
        touchpoints = db.query(AttributionTouchpoint).filter(
            AttributionTouchpoint.attribution_id == attribution.id
        ).order_by(AttributionTouchpoint.position_in_journey).all()
        
        # Format touchpoint data
        touchpoint_data = []
        for tp in touchpoints:
            touchpoint_data.append({
                "id": tp.id,
                "type": tp.touchpoint_type,
                "channel": tp.channel,
                "campaign_id": tp.campaign_id,
                "campaign_name": tp.campaign_name,
                "source": tp.source,
                "medium": tp.medium,
                "attributed_revenue": tp.attributed_revenue,
                "attribution_percentage": tp.attribution_percentage,
                "attribution_weight": tp.attribution_weight,
                "position_in_journey": tp.position_in_journey,
                "days_before_conversion": tp.days_before_conversion,
                "timestamp": tp.touchpoint_timestamp.isoformat(),
                "touchpoint_data": tp.touchpoint_data
            })
        
        return {
            "conversion_id": conversion_id,
            "attribution_id": attribution.id,
            "customer_id": attribution.customer_id,
            "conversion_details": {
                "type": attribution.conversion_type,
                "value": attribution.conversion_value,
                "date": attribution.conversion_date.isoformat()
            },
            "attribution_analysis": {
                "model_used": attribution.attribution_model,
                "touchpoints_analyzed": attribution.touchpoints_analyzed,
                "attribution_window_days": attribution.attribution_window_days,
                "attribution_data": attribution.attribution_data,
                "revenue_breakdown": attribution.revenue_breakdown,
                "primary_attribution": attribution.primary_attribution
            },
            "customer_journey": {
                "touchpoints": touchpoint_data,
                "journey_length_days": max([tp["days_before_conversion"] for tp in touchpoint_data]) if touchpoint_data else 0,
                "total_touchpoints": len(touchpoint_data),
                "unique_channels": len(set(tp["channel"] for tp in touchpoint_data if tp["channel"])),
                "journey_summary": _summarize_customer_journey(touchpoint_data)
            },
            "timestamps": {
                "created_at": attribution.created_at.isoformat(),
                "updated_at": attribution.updated_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversion details: {str(e)}")

@router.get("/models/comparison")
async def compare_attribution_models(
    campaign_id: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: dict = Depends(require_permission("view_analytics")),
    db: Session = Depends(get_db)
):
    """Compare performance of different attribution models"""
    try:
        from ...revenue.attribution_engine import RevenueAttribution, AttributionTouchpoint
        
        # Set default date range
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        # Build query
        query = db.query(RevenueAttribution).filter(
            RevenueAttribution.conversion_date.between(start_date, end_date)
        )
        
        # Filter by campaign if specified
        if campaign_id:
            # Get attributions that have touchpoints from the specified campaign
            campaign_attribution_ids = db.query(AttributionTouchpoint.attribution_id).filter(
                AttributionTouchpoint.campaign_id == campaign_id
            ).distinct().subquery()
            
            query = query.filter(RevenueAttribution.id.in_(campaign_attribution_ids))
        
        attributions = query.all()
        
        if not attributions:
            return {
                "message": "No attribution data found for comparison",
                "filters": {
                    "campaign_id": campaign_id,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }
        
        # Group by attribution model
        model_comparison = defaultdict(lambda: {
            "conversions": 0,
            "total_revenue": 0,
            "avg_revenue_per_conversion": 0,
            "unique_customers": set(),
            "avg_touchpoints": 0,
            "total_touchpoints": 0
        })
        
        for attribution in attributions:
            model = attribution.attribution_model
            model_data = model_comparison[model]
            
            model_data["conversions"] += 1
            model_data["total_revenue"] += attribution.conversion_value
            model_data["unique_customers"].add(attribution.customer_id)
            model_data["total_touchpoints"] += attribution.touchpoints_analyzed
        
        # Calculate derived metrics
        comparison_results = {}
        for model, data in model_comparison.items():
            comparison_results[model] = {
                "conversions": data["conversions"],
                "total_revenue": data["total_revenue"],
                "avg_revenue_per_conversion": data["total_revenue"] / max(1, data["conversions"]),
                "unique_customers": len(data["unique_customers"]),
                "avg_touchpoints_per_conversion": data["total_touchpoints"] / max(1, data["conversions"]),
                "revenue_share": (data["total_revenue"] / sum(d["total_revenue"] for d in model_comparison.values())) * 100
            }
        
        # Determine best performing model
        best_revenue_model = max(comparison_results.items(), key=lambda x: x[1]["total_revenue"])[0]
        best_avg_model = max(comparison_results.items(), key=lambda x: x[1]["avg_revenue_per_conversion"])[0]
        
        return {
            "comparison_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "campaign_filter": campaign_id
            },
            "model_comparison": comparison_results,
            "summary": {
                "total_models_compared": len(comparison_results),
                "best_total_revenue_model": best_revenue_model,
                "best_avg_revenue_model": best_avg_model,
                "total_conversions": sum(data["conversions"] for data in comparison_results.values()),
                "total_revenue": sum(data["total_revenue"] for data in comparison_results.values())
            },
            "recommendations": _generate_model_comparison_recommendations(comparison_results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model comparison failed: {str(e)}")

# Helper functions
def _calculate_trend_direction(daily_data: Dict[str, Dict[str, float]]) -> str:
    """Calculate trend direction from daily data"""
    try:
        if len(daily_data) < 2:
            return "insufficient_data"
        
        dates = sorted(daily_data.keys())
        first_half = dates[:len(dates)//2]
        second_half = dates[len(dates)//2:]
        
        first_half_revenue = sum(daily_data[date]["revenue"] for date in first_half)
        second_half_revenue = sum(daily_data[date]["revenue"] for date in second_half)
        
        if second_half_revenue > first_half_revenue * 1.1:
            return "increasing"
        elif second_half_revenue < first_half_revenue * 0.9:
            return "decreasing"
        else:
            return "stable"
            
    except Exception:
        return "unknown"

def _generate_dashboard_recommendations(attributions, touchpoints, model_usage, model_revenue) -> List[str]:
    """Generate recommendations for attribution dashboard"""
    recommendations = []
    
    try:
        if not attributions:
            recommendations.append("Start tracking conversions to build attribution insights")
            return recommendations
        
        # Model recommendations
        most_used_model = max(model_usage.items(), key=lambda x: x[1])[0] if model_usage else None
        highest_revenue_model = max(model_revenue.items(), key=lambda x: x[1])[0] if model_revenue else None
        
        if most_used_model != highest_revenue_model:
            recommendations.append(f"Consider using {highest_revenue_model} model more frequently for higher revenue attribution")
        
        # Journey complexity
        avg_touchpoints = len(touchpoints) / len(attributions) if attributions else 0
        if avg_touchpoints > 5:
            recommendations.append("Complex customer journeys detected - consider position-based or custom attribution models")
        elif avg_touchpoints < 2:
            recommendations.append("Simple customer journeys - single-touch models may be sufficient")
        
        # Revenue patterns
        revenue_values = [a.conversion_value for a in attributions]
        if revenue_values:
            revenue_variance = np.var(revenue_values)
            if revenue_variance > 100000:
                recommendations.append("High revenue variance - consider customer segment-specific attribution analysis")
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating dashboard recommendations: {e}")
        return ["Unable to generate recommendations"]

def _summarize_customer_journey(touchpoints: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Summarize customer journey from touchpoint data"""
    try:
        if not touchpoints:
            return {"summary": "No touchpoints in journey"}
        
        # Channel sequence
        channels = [tp.get("channel") or tp.get("type") for tp in touchpoints]
        unique_channels = list(set(filter(None, channels)))
        
        # Time analysis
        if len(touchpoints) > 1:
            time_gaps = []
            for i in range(1, len(touchpoints)):
                gap = abs(touchpoints[i]["days_before_conversion"] - touchpoints[i-1]["days_before_conversion"])
                time_gaps.append(gap)
            avg_gap = sum(time_gaps) / len(time_gaps) if time_gaps else 0
        else:
            avg_gap = 0
        
        return {
            "channel_sequence": channels,
            "unique_channels": unique_channels,
            "channel_diversity": len(unique_channels),
            "avg_time_between_touchpoints": avg_gap,
            "journey_complexity": "simple" if len(touchpoints) <= 2 else "moderate" if len(touchpoints) <= 5 else "complex",
            "dominant_channel": max(set(channels), key=channels.count) if channels else None
        }
        
    except Exception as e:
        logger.error(f"Error summarizing customer journey: {e}")
        return {"error": str(e)}

def _generate_model_comparison_recommendations(comparison_results: Dict[str, Dict[str, Any]]) -> List[str]:
    """Generate recommendations from model comparison"""
    recommendations = []
    
    try:
        if not comparison_results:
            return ["No model data available for recommendations"]
        
        # Find best performing models
        best_revenue = max(comparison_results.items(), key=lambda x: x[1]["total_revenue"])
        best_avg = max(comparison_results.items(), key=lambda x: x[1]["avg_revenue_per_conversion"])
        
        if best_revenue[0] == best_avg[0]:
            recommendations.append(f"'{best_revenue[0]}' model performs best in both total and average revenue")
        else:
            recommendations.append(f"Use '{best_revenue[0]}' for volume, '{best_avg[0]}' for high-value conversions")
        
        # Check for significant differences
        revenue_values = [data["avg_revenue_per_conversion"] for data in comparison_results.values()]
        if max(revenue_values) > min(revenue_values) * 2:
            recommendations.append("Significant differences between models - model choice significantly impacts attribution")
        
        # Model-specific recommendations
        for model, data in comparison_results.items():
            if data["avg_touchpoints_per_conversion"] > 5 and model in ["first_touch", "last_touch"]:
                recommendations.append(f"Complex journeys may not be well-suited for {model} attribution")
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating model comparison recommendations: {e}")
        return ["Unable to generate model recommendations"]