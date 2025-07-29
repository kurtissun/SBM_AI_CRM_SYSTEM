"""
Intelligent Insights API Endpoints
AI-generated business insights and recommendations
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from ...core.database import get_db, Customer, Campaign, Purchase
from ...core.security import get_current_user
from ...ai_engine.insight_generator import IntelligentInsightGenerator

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/business-insights")
async def get_business_insights(
    time_range: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    insight_type: str = Query("comprehensive", regex="^(basic|comprehensive|strategic)$"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    🧠 **AI-Generated Business Insights**
    
    Get intelligent business insights and recommendations powered by AI.
    """
    try:
        # Calculate date range
        time_mapping = {
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
            "90d": timedelta(days=90),
            "1y": timedelta(days=365)
        }
        
        start_date = datetime.now() - time_mapping[time_range]
        
        # Gather data
        customers = db.query(Customer).filter(Customer.created_at >= start_date).all()
        campaigns = db.query(Campaign).filter(Campaign.created_at >= start_date).all()
        purchases = db.query(Purchase).join(Customer).filter(Customer.created_at >= start_date).all()
        
        # Initialize insight generator
        insight_generator = IntelligentInsightGenerator(db)
        
        # Generate comprehensive insights
        insights = {
            "insight_metadata": {
                "generated_at": datetime.now().isoformat(),
                "time_range": time_range,
                "insight_type": insight_type,
                "data_points_analyzed": len(customers) + len(campaigns) + len(purchases)
            },
            "key_insights": insight_generator.generate_key_insights({
                "customers": customers,
                "campaigns": campaigns,
                "purchases": purchases,
                "time_range": time_range
            }),
            "performance_insights": insight_generator.analyze_performance_patterns({
                "customers": len(customers),
                "campaigns": len(campaigns),
                "total_revenue": sum(p.purchase_amount for p in purchases),
                "avg_customer_value": sum(p.purchase_amount for p in purchases) / len(customers) if customers else 0
            }),
            "trend_analysis": insight_generator.detect_trends({
                "customer_growth": _calculate_growth_trend(customers),
                "campaign_performance": _analyze_campaign_trends(campaigns),
                "revenue_trends": _analyze_revenue_trends(purchases)
            }),
            "opportunity_identification": insight_generator.identify_opportunities({
                "customer_segments": _analyze_segment_opportunities(customers),
                "campaign_gaps": _identify_campaign_gaps(campaigns),
                "market_opportunities": _detect_market_opportunities(customers, purchases)
            })
        }
        
        if insight_type in ["comprehensive", "strategic"]:
            insights["predictive_insights"] = insight_generator.generate_predictive_insights({
                "customer_behavior": _predict_customer_behavior(customers),
                "market_trends": _predict_market_trends(purchases),
                "revenue_forecasts": _generate_revenue_forecasts(purchases, customers)
            })
            
            insights["strategic_recommendations"] = insight_generator.generate_strategic_recommendations({
                "business_metrics": {
                    "customer_count": len(customers),
                    "campaign_count": len(campaigns),
                    "revenue": sum(p.purchase_amount for p in purchases)
                },
                "performance_data": insights["performance_insights"]
            })
        
        if insight_type == "strategic":
            insights["executive_briefing"] = insight_generator.generate_executive_briefing({
                "key_metrics": insights["insight_metadata"],
                "critical_insights": insights["key_insights"],
                "strategic_priorities": insights["strategic_recommendations"]
            })
            
            insights["risk_assessment"] = insight_generator.assess_business_risks({
                "customer_data": customers,
                "campaign_data": campaigns,
                "financial_data": purchases
            })
        
        return insights
        
    except Exception as e:
        logger.error(f"Business insights generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Insights generation failed: {str(e)}")

@router.get("/customer-insights")
async def get_customer_insights(
    customer_id: Optional[str] = None,
    segment_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get AI insights for specific customers or segments"""
    try:
        insight_generator = IntelligentInsightGenerator(db)
        
        if customer_id:
            customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
            if not customer:
                raise HTTPException(status_code=404, detail="Customer not found")
            
            insights = insight_generator.generate_individual_customer_insights(customer)
            
        elif segment_id is not None:
            customers = db.query(Customer).filter(Customer.segment_id == segment_id).all()
            if not customers:
                raise HTTPException(status_code=404, detail="No customers found in segment")
            
            insights = insight_generator.generate_segment_insights(customers, segment_id)
            
        else:
            # General customer insights
            customers = db.query(Customer).all()
            insights = insight_generator.generate_general_customer_insights(customers)
        
        return {
            "insights_type": "customer_specific" if customer_id else "segment_specific" if segment_id else "general",
            "target_id": customer_id or segment_id or "all_customers",
            "insights": insights,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Customer insights generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Customer insights failed: {str(e)}")

@router.get("/campaign-insights/{campaign_id}")
async def get_campaign_insights(
    campaign_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get AI insights for specific campaign"""
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        insight_generator = IntelligentInsightGenerator(db)
        insights = insight_generator.generate_campaign_insights(campaign)
        
        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign.name,
            "insights": insights,
            "performance_analysis": _analyze_campaign_performance(campaign),
            "optimization_suggestions": _generate_campaign_optimizations(campaign),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Campaign insights generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Campaign insights failed: {str(e)}")

@router.get("/market-insights")
async def get_market_insights(
    analysis_depth: str = Query("standard", regex="^(standard|deep|competitive)$"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get AI-powered market insights and opportunities"""
    try:
        insight_generator = IntelligentInsightGenerator(db)
        
        # Gather comprehensive market data
        customers = db.query(Customer).all()
        campaigns = db.query(Campaign).all()
        purchases = db.query(Purchase).all()
        
        market_insights = {
            "market_overview": insight_generator.analyze_market_position({
                "customer_base": len(customers),
                "market_penetration": _calculate_market_penetration(customers),
                "competitive_position": _assess_competitive_position(campaigns, purchases)
            }),
            "customer_market_analysis": insight_generator.analyze_customer_market({
                "demographics": _analyze_market_demographics(customers),
                "behavior_patterns": _analyze_market_behavior(customers, purchases),
                "segment_dynamics": _analyze_segment_market_dynamics(customers)
            }),
            "growth_opportunities": insight_generator.identify_growth_opportunities({
                "untapped_segments": _identify_untapped_segments(customers),
                "market_gaps": _identify_market_gaps(customers, purchases),
                "expansion_potential": _calculate_expansion_potential(customers, campaigns)
            })
        }
        
        if analysis_depth in ["deep", "competitive"]:
            market_insights["deep_market_analysis"] = insight_generator.perform_deep_market_analysis({
                "customer_lifetime_patterns": _analyze_customer_lifetime_patterns(customers, purchases),
                "market_trend_analysis": _perform_trend_analysis(purchases),
                "seasonal_patterns": _detect_seasonal_patterns(purchases)
            })
        
        if analysis_depth == "competitive":
            market_insights["competitive_intelligence"] = insight_generator.generate_competitive_intelligence({
                "market_share_analysis": _estimate_market_share(customers, purchases),
                "competitive_positioning": _analyze_competitive_positioning(campaigns),
                "differentiation_opportunities": _identify_differentiation_opportunities(customers)
            })
        
        return {
            "analysis_depth": analysis_depth,
            "market_insights": market_insights,
            "strategic_implications": insight_generator.derive_strategic_implications(market_insights),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Market insights generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Market insights failed: {str(e)}")

@router.post("/generate-custom-insights")
async def generate_custom_insights(
    analysis_request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate custom AI insights based on specific business questions"""
    try:
        insight_generator = IntelligentInsightGenerator(db)
        
        # Validate request
        required_fields = ["business_question", "data_scope", "analysis_type"]
        for field in required_fields:
            if field not in analysis_request:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Gather relevant data based on scope
        data_scope = analysis_request["data_scope"]
        relevant_data = _gather_relevant_data(data_scope, db)
        
        # Generate custom insights
        custom_insights = insight_generator.generate_custom_insights({
            "business_question": analysis_request["business_question"],
            "analysis_type": analysis_request["analysis_type"],
            "data": relevant_data,
            "parameters": analysis_request.get("parameters", {})
        })
        
        return {
            "request_id": f"custom_{datetime.now().timestamp()}",
            "business_question": analysis_request["business_question"],
            "analysis_type": analysis_request["analysis_type"],
            "custom_insights": custom_insights,
            "methodology": insight_generator.explain_methodology(analysis_request["analysis_type"]),
            "confidence_score": custom_insights.get("confidence", 0.8),
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Custom insights generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Custom insights failed: {str(e)}")

# Helper functions for insight generation
def _calculate_growth_trend(customers):
    """Calculate customer growth trend"""
    if not customers:
        return {"trend": "no_data", "rate": 0}
    
    # Group by month and calculate growth
    monthly_counts = {}
    for customer in customers:
        month_key = customer.created_at.strftime("%Y-%m")
        monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
    
    if len(monthly_counts) < 2:
        return {"trend": "insufficient_data", "rate": 0}
    
    months = sorted(monthly_counts.keys())
    recent_growth = (monthly_counts[months[-1]] - monthly_counts[months[-2]]) / monthly_counts[months[-2]] * 100
    
    return {
        "trend": "growing" if recent_growth > 0 else "declining" if recent_growth < 0 else "stable",
        "rate": recent_growth,
        "monthly_data": monthly_counts
    }

def _analyze_campaign_trends(campaigns):
    """Analyze campaign performance trends"""
    if not campaigns:
        return {"message": "No campaigns to analyze"}
    
    # Calculate average ROI trend
    sorted_campaigns = sorted(campaigns, key=lambda x: x.created_at)
    rois = [c.predicted_roi for c in sorted_campaigns]
    
    if len(rois) > 1:
        trend = "improving" if rois[-1] > rois[0] else "declining"
        improvement_rate = ((rois[-1] - rois[0]) / rois[0]) * 100
    else:
        trend = "stable"
        improvement_rate = 0
    
    return {
        "performance_trend": trend,
        "improvement_rate": improvement_rate,
        "average_roi": sum(rois) / len(rois),
        "total_campaigns": len(campaigns)
    }

def _analyze_revenue_trends(purchases):
    """Analyze revenue trends from purchase data"""
    if not purchases:
        return {"message": "No purchase data available"}
    
    # Group by month
    monthly_revenue = {}
    for purchase in purchases:
        if purchase.purchase_date:
            month_key = purchase.purchase_date.strftime("%Y-%m")
            monthly_revenue[month_key] = monthly_revenue.get(month_key, 0) + purchase.purchase_amount
    
    months = sorted(monthly_revenue.keys())
    if len(months) < 2:
        return {"trend": "insufficient_data", "monthly_revenue": monthly_revenue}
    
    recent_change = ((monthly_revenue[months[-1]] - monthly_revenue[months[-2]]) / 
                    monthly_revenue[months[-2]]) * 100
    
    return {
        "trend": "growing" if recent_change > 0 else "declining",
        "growth_rate": recent_change,
        "monthly_revenue": monthly_revenue,
        "total_revenue": sum(monthly_revenue.values())
    }

def _analyze_segment_opportunities(customers):
    """Identify opportunities in customer segments"""
    if not customers:
        return []
    
    segment_sizes = {}
    for customer in customers:
        if customer.segment_id is not None:
            segment_sizes[customer.segment_id] = segment_sizes.get(customer.segment_id, 0) + 1
    
    opportunities = []
    total_customers = len(customers)
    
    for segment_id, size in segment_sizes.items():
        percentage = (size / total_customers) * 100
        
        if percentage < 10:  # Small segments
            opportunities.append({
                "segment_id": segment_id,
                "opportunity_type": "growth_potential",
                "current_size": size,
                "recommendation": f"Segment {segment_id} has growth potential with targeted campaigns"
            })
        elif percentage > 40:  # Large segments
            opportunities.append({
                "segment_id": segment_id,
                "opportunity_type": "subsegmentation",
                "current_size": size,
                "recommendation": f"Segment {segment_id} is large - consider sub-segmentation"
            })
    
    return opportunities

def _identify_campaign_gaps(campaigns):
    """Identify gaps in campaign coverage"""
    if not campaigns:
        return ["No campaigns running - major opportunity for customer engagement"]
    
    gaps = []
    
    # Check campaign types
    campaign_types = set(getattr(c, 'campaign_type', 'engagement') for c in campaigns)
    all_types = {'engagement', 'conversion', 'retention', 'acquisition'}
    missing_types = all_types - campaign_types
    
    for missing_type in missing_types:
        gaps.append(f"No {missing_type} campaigns detected - opportunity for {missing_type} focus")
    
    # Check for inactive periods
    active_campaigns = [c for c in campaigns if c.status == 'active']
    if len(active_campaigns) < len(campaigns) * 0.3:
        gaps.append("Low active campaign ratio - consider activating more campaigns")
    
    return gaps

def _detect_market_opportunities(customers, purchases):
    """Detect market opportunities from customer and purchase data"""
    opportunities = []
    
    if not customers or not purchases:
        return ["Insufficient data for market opportunity analysis"]
    
    # High-value customer opportunity
    high_value_customers = len([c for c in customers if c.rating_id >= 4])
    if high_value_customers > len(customers) * 0.4:
        opportunities.append("High satisfaction rate indicates opportunity for premium services")
    
    # Purchase pattern opportunities
    avg_purchase = sum(p.purchase_amount for p in purchases) / len(purchases)
    high_value_purchases = len([p for p in purchases if p.purchase_amount > avg_purchase * 2])
    
    if high_value_purchases > len(purchases) * 0.2:
        opportunities.append("Significant high-value purchases suggest luxury market opportunity")
    
    return opportunities

def _predict_customer_behavior(customers):
    """Predict future customer behavior patterns"""
    if not customers:
        return {"message": "No customer data for predictions"}
    
    # Simple predictive model based on ratings and age
    high_engagement_predicted = len([c for c in customers if c.rating_id >= 4 and c.age < 40])
    churn_risk_predicted = len([c for c in customers if c.rating_id <= 2])
    
    return {
        "high_engagement_potential": high_engagement_predicted,
        "churn_risk_customers": churn_risk_predicted,
        "predicted_growth_rate": 15.0,  # Would use ML model in production
        "confidence": 0.78
    }

def _predict_market_trends(purchases):
    """Predict market trends from purchase data"""
    if not purchases:
        return {"message": "No purchase data for trend prediction"}
    
    # Analyze spending patterns
    recent_purchases = [p for p in purchases if p.purchase_date and 
                      p.purchase_date >= datetime.now() - timedelta(days=30)]
    
    if recent_purchases:
        recent_avg = sum(p.purchase_amount for p in recent_purchases) / len(recent_purchases)
        total_avg = sum(p.purchase_amount for p in purchases) / len(purchases)
        trend_direction = "upward" if recent_avg > total_avg else "downward"
    else:
        trend_direction = "stable"
    
    return {
        "spending_trend": trend_direction,
        "predicted_next_month_growth": 8.5,
        "market_sentiment": "positive" if trend_direction == "upward" else "cautious",
        "confidence": 0.72
    }

def _generate_revenue_forecasts(purchases, customers):
    """Generate revenue forecasts"""
    if not purchases or not customers:
        return {"message": "Insufficient data for revenue forecasting"}
    
    # Simple forecasting based on current patterns
    monthly_revenue = sum(p.purchase_amount for p in purchases) / 12  # Simplified
    customer_growth_rate = 1.1  # 10% growth assumption
    
    return {
        "next_month_forecast": monthly_revenue * customer_growth_rate,
        "next_quarter_forecast": monthly_revenue * 3 * customer_growth_rate,
        "annual_forecast": monthly_revenue * 12 * customer_growth_rate,
        "growth_assumptions": {
            "customer_growth": "10%",
            "spending_per_customer": "stable"
        },
        "confidence": 0.75
    }

def _analyze_campaign_performance(campaign):
    """Analyze individual campaign performance"""
    roi = campaign.actual_roi or campaign.predicted_roi
    
    return {
        "roi_analysis": {
            "current_roi": roi,
            "performance_rating": "excellent" if roi > 2.5 else "good" if roi > 1.5 else "needs_improvement",
            "vs_benchmark": roi - 1.8  # Industry benchmark
        },
        "efficiency_metrics": {
            "cost_per_result": campaign.budget / max(roi, 0.1),
            "budget_utilization": "optimal" if 1.5 <= roi <= 3.0 else "review_needed"
        }
    }

def _generate_campaign_optimizations(campaign):
    """Generate campaign optimization suggestions"""
    roi = campaign.actual_roi or campaign.predicted_roi
    suggestions = []
    
    if roi < 1.5:
        suggestions.append("Consider revising targeting criteria to improve ROI")
        suggestions.append("Test different creative approaches")
    elif roi > 3.0:
        suggestions.append("Scale successful elements to similar campaigns")
        suggestions.append("Increase budget allocation for maximum impact")
    
    suggestions.append("Monitor performance metrics weekly for optimization opportunities")
    
    return suggestions

def _calculate_market_penetration(customers):
    """Calculate market penetration metrics"""
    # Simplified calculation - would use market research data in production
    estimated_total_market = len(customers) * 10  # Assumption
    penetration_rate = len(customers) / estimated_total_market * 100
    
    return {
        "penetration_rate": penetration_rate,
        "market_size_estimate": estimated_total_market,
        "growth_potential": max(0, 100 - penetration_rate)
    }

def _assess_competitive_position(campaigns, purchases):
    """Assess competitive market position"""
    # Simplified competitive analysis
    total_spend = sum(c.budget for c in campaigns)
    total_revenue = sum(p.purchase_amount for p in purchases)
    
    return {
        "market_share_estimate": "moderate",  # Would use real competitive data
        "competitive_strength": "strong" if total_revenue > total_spend * 2 else "moderate",
        "differentiation_score": 0.75
    }

def _gather_relevant_data(data_scope, db):
    """Gather data based on specified scope"""
    data = {}
    
    if "customers" in data_scope:
        data["customers"] = db.query(Customer).all()
    
    if "campaigns" in data_scope:
        data["campaigns"] = db.query(Campaign).all()
    
    if "purchases" in data_scope:
        data["purchases"] = db.query(Purchase).all()
    
    return data

def _analyze_market_demographics(customers):
    """Analyze market demographics"""
    if not customers:
        return {"message": "No demographic data"}
    
    ages = [c.age for c in customers if c.age]
    genders = [c.gender for c in customers if c.gender]
    
    return {
        "age_profile": {
            "average": sum(ages) / len(ages) if ages else 0,
            "distribution": "diverse" if len(set(ages)) > len(ages) * 0.1 else "concentrated"
        },
        "gender_balance": {
            "male": genders.count("M") if genders else 0,
            "female": genders.count("F") if genders else 0,
            "balance_score": 0.5  # Would calculate actual balance
        }
    }

def _analyze_market_behavior(customers, purchases):
    """Analyze market behavior patterns"""
    # Simplified behavior analysis
    high_value_customers = len([c for c in customers if c.rating_id >= 4])
    total_purchases = len(purchases)
    
    return {
        "engagement_level": "high" if high_value_customers > len(customers) * 0.4 else "moderate",
        "purchase_activity": "active" if total_purchases > len(customers) else "moderate",
        "loyalty_indicators": {
            "repeat_customers": total_purchases / len(customers) if customers else 0,
            "satisfaction_rate": high_value_customers / len(customers) * 100 if customers else 0
        }
    }

def _analyze_segment_market_dynamics(customers):
    """Analyze market dynamics by segments"""
    segment_counts = {}
    for customer in customers:
        if customer.segment_id is not None:
            segment_counts[customer.segment_id] = segment_counts.get(customer.segment_id, 0) + 1
    
    return {
        "segment_distribution": segment_counts,
        "dominant_segment": max(segment_counts.items(), key=lambda x: x[1])[0] if segment_counts else None,
        "market_concentration": len(segment_counts) / len(customers) if customers else 0
    }

def _identify_untapped_segments(customers):
    """Identify potentially untapped market segments"""
    # Simplified analysis - would use more sophisticated segmentation in production
    age_groups = {}
    for customer in customers:
        if customer.age:
            age_group = f"{(customer.age // 10) * 10}s"
            age_groups[age_group] = age_groups.get(age_group, 0) + 1
    
    # Identify underrepresented age groups
    avg_group_size = sum(age_groups.values()) / len(age_groups) if age_groups else 0
    untapped = [group for group, count in age_groups.items() if count < avg_group_size * 0.5]
    
    return untapped

def _identify_market_gaps(customers, purchases):
    """Identify gaps in market coverage"""
    gaps = []
    
    # Geographic gaps (simplified)
    if len(set(getattr(c, 'location', 'unknown') for c in customers)) < 3:
        gaps.append("Limited geographic coverage")
    
    # Demographic gaps
    age_range = max(c.age for c in customers if c.age) - min(c.age for c in customers if c.age)
    if age_range < 30:
        gaps.append("Narrow age demographic coverage")
    
    return gaps

def _calculate_expansion_potential(customers, campaigns):
    """Calculate market expansion potential"""
    customer_diversity = len(set((c.age, c.gender) for c in customers if c.age and c.gender))
    campaign_reach = len(campaigns)
    
    expansion_score = min(1.0, (customer_diversity / len(customers) if customers else 0) + 
                         (campaign_reach / 10))  # Normalized score
    
    return {
        "expansion_score": expansion_score,
        "potential_rating": "high" if expansion_score > 0.7 else "medium" if expansion_score > 0.4 else "low",
        "recommended_strategies": [
            "Demographic expansion",
            "Geographic expansion",
            "Campaign diversification"
        ]
    }

def _analyze_customer_lifetime_patterns(customers, purchases):
    """Analyze customer lifetime value patterns"""
    if not customers or not purchases:
        return {"message": "Insufficient data for lifetime analysis"}
    
    # Simple CLV calculation
    customer_values = {}
    for purchase in purchases:
        customer_values[purchase.customer_id] = customer_values.get(purchase.customer_id, 0) + purchase.purchase_amount
    
    avg_clv = sum(customer_values.values()) / len(customer_values) if customer_values else 0
    
    return {
        "average_clv": avg_clv,
        "clv_distribution": "varied",  # Would calculate actual distribution
        "lifetime_stages": {
            "new": len([c for c in customers if (datetime.now() - c.created_at).days < 30]),
            "established": len([c for c in customers if 30 <= (datetime.now() - c.created_at).days < 365]),
            "mature": len([c for c in customers if (datetime.now() - c.created_at).days >= 365])
        }
    }

def _perform_trend_analysis(purchases):
    """Perform comprehensive trend analysis"""
    if not purchases:
        return {"message": "No purchase data for trend analysis"}
    
    # Monthly trend analysis
    monthly_data = {}
    for purchase in purchases:
        if purchase.purchase_date:
            month = purchase.purchase_date.strftime("%Y-%m")
            monthly_data[month] = monthly_data.get(month, 0) + purchase.purchase_amount
    
    months = sorted(monthly_data.keys())
    if len(months) < 3:
        return {"trend": "insufficient_data", "monthly_data": monthly_data}
    
    # Calculate trend direction
    recent_avg = sum(monthly_data[m] for m in months[-3:]) / 3
    early_avg = sum(monthly_data[m] for m in months[:3]) / 3
    
    trend_direction = "growing" if recent_avg > early_avg else "declining"
    
    return {
        "trend_direction": trend_direction,
        "monthly_data": monthly_data,
        "growth_rate": ((recent_avg - early_avg) / early_avg * 100) if early_avg > 0 else 0
    }

def _detect_seasonal_patterns(purchases):
    """Detect seasonal patterns in purchase data"""
    if not purchases:
        return {"message": "No purchase data for seasonal analysis"}
    
    # Group by month
    seasonal_data = {}
    for purchase in purchases:
        if purchase.purchase_date:
            month = purchase.purchase_date.month
            seasonal_data[month] = seasonal_data.get(month, 0) + purchase.purchase_amount
    
    # Identify peak months
    if seasonal_data:
        peak_month = max(seasonal_data.items(), key=lambda x: x[1])[0]
        low_month = min(seasonal_data.items(), key=lambda x: x[1])[0]
    else:
        peak_month = low_month = None
    
    return {
        "seasonal_pattern": "detected" if len(seasonal_data) > 6 else "insufficient_data",
        "peak_month": peak_month,
        "low_month": low_month,
        "monthly_revenue": seasonal_data
    }

def _estimate_market_share(customers, purchases):
    """Estimate market share based on customer and purchase data"""
    # Simplified market share estimation
    total_revenue = sum(p.purchase_amount for p in purchases)
    estimated_market_size = total_revenue * 20  # Assumption: we have 5% market share
    
    return {
        "estimated_market_share": 5.0,  # Percentage
        "market_size_estimate": estimated_market_size,
        "revenue_position": "competitive"
    }

def _analyze_competitive_positioning(campaigns):
    """Analyze competitive positioning based on campaigns"""
    if not campaigns:
        return {"message": "No campaign data for competitive analysis"}
    
    total_budget = sum(c.budget for c in campaigns)
    avg_roi = sum(c.predicted_roi for c in campaigns) / len(campaigns)
    
    return {
        "investment_level": "moderate" if total_budget < 100000 else "high",
        "roi_competitiveness": "above_average" if avg_roi > 2.0 else "average",
        "campaign_sophistication": "advanced" if len(campaigns) > 5 else "basic"
    }

def _identify_differentiation_opportunities(customers):
    """Identify opportunities for market differentiation"""
    opportunities = []
    
    if not customers:
        return ["Insufficient customer data for differentiation analysis"]
    
    # Analyze customer satisfaction
    high_satisfaction = len([c for c in customers if c.rating_id >= 4])
    satisfaction_rate = high_satisfaction / len(customers) * 100
    
    if satisfaction_rate > 70:
        opportunities.append("High satisfaction indicates strong differentiation potential in service quality")
    
    # Analyze demographic concentration
    age_diversity = len(set(c.age for c in customers if c.age))
    if age_diversity > len(customers) * 0.1:
        opportunities.append("Diverse customer base suggests opportunity for targeted differentiation")
    
    opportunities.extend([
        "Personalization and customization services",
        "Premium customer experience programs",
        "Innovative loyalty and rewards systems"
    ])
    
    return opportunities