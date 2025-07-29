"""
Financial Analytics API Endpoints
Revenue and profitability analysis
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import logging

from ...core.database import get_db, Customer, Campaign, Purchase
from ...core.security import get_current_user
from ...analytics.financial_engine import FinancialAnalyticsEngine

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/revenue-analysis")
async def get_revenue_analysis(
    time_range: str = Query("90d", regex="^(30d|90d|180d|1y|2y)$"),
    analysis_type: str = Query("comprehensive", regex="^(basic|comprehensive|advanced)$"),
    segment_breakdown: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    💰 **Revenue Analysis**
    
    Comprehensive revenue analysis with segmentation and forecasting.
    """
    try:
        # Calculate time range
        time_mapping = {
            "30d": timedelta(days=30),
            "90d": timedelta(days=90),
            "180d": timedelta(days=180),
            "1y": timedelta(days=365),
            "2y": timedelta(days=730)
        }
        
        start_date = datetime.now() - time_mapping[time_range]
        
        # Get financial data
        customers = db.query(Customer).filter(Customer.created_at >= start_date).all()
        purchases = db.query(Purchase).join(Customer).filter(
            Customer.created_at >= start_date
        ).all()
        campaigns = db.query(Campaign).filter(Campaign.created_at >= start_date).all()
        
        if not purchases:
            return {"message": "No purchase data available for revenue analysis"}
        
        # Initialize financial analytics engine
        financial_engine = FinancialAnalyticsEngine(db)
        
        revenue_analysis = {
            "analysis_metadata": {
                "time_range": time_range,
                "analysis_type": analysis_type,
                "start_date": start_date.isoformat(),
                "end_date": datetime.now().isoformat(),
                "data_points": len(purchases),
                "customers_analyzed": len(customers),
                "generated_at": datetime.now().isoformat()
            },
            "revenue_overview": financial_engine.calculate_revenue_overview(
                purchases, start_date
            ),
            "revenue_trends": financial_engine.analyze_revenue_trends(
                purchases, time_range
            ),
            "revenue_metrics": financial_engine.calculate_revenue_metrics(
                purchases, customers, campaigns
            )
        }
        
        if segment_breakdown:
            revenue_analysis["segment_revenue"] = financial_engine.analyze_segment_revenue(
                purchases, customers
            )
        
        if analysis_type in ["comprehensive", "advanced"]:
            revenue_analysis["profitability_analysis"] = financial_engine.analyze_profitability(
                purchases, campaigns
            )
            revenue_analysis["customer_value_analysis"] = financial_engine.analyze_customer_value(
                purchases, customers
            )
            revenue_analysis["revenue_forecasting"] = financial_engine.forecast_revenue(
                purchases, customers, time_range
            )
        
        if analysis_type == "advanced":
            revenue_analysis["advanced_metrics"] = financial_engine.calculate_advanced_metrics(
                purchases, customers, campaigns
            )
            revenue_analysis["cohort_analysis"] = financial_engine.perform_cohort_analysis(
                customers, purchases
            )
            revenue_analysis["attribution_analysis"] = financial_engine.analyze_revenue_attribution(
                purchases, campaigns, customers
            )
        
        return revenue_analysis
        
    except Exception as e:
        logger.error(f"Revenue analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Revenue analysis failed: {str(e)}")

@router.get("/profitability-analysis")
async def get_profitability_analysis(
    analysis_scope: str = Query("overall", regex="^(overall|customer|campaign|segment|product)$"),
    target_id: Optional[str] = None,
    include_costs: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    📊 **Profitability Analysis**
    
    Detailed profitability analysis across different business dimensions.
    """
    try:
        financial_engine = FinancialAnalyticsEngine(db)
        
        # Get relevant data based on analysis scope
        customers = db.query(Customer).all()
        purchases = db.query(Purchase).all()
        campaigns = db.query(Campaign).all()
        
        if not purchases:
            return {"message": "No purchase data available for profitability analysis"}
        
        profitability_analysis = {
            "analysis_metadata": {
                "analysis_scope": analysis_scope,
                "target_id": target_id,
                "include_costs": include_costs,
                "total_revenue": sum(p.purchase_amount for p in purchases),
                "analysis_date": datetime.now().isoformat()
            }
        }
        
        if analysis_scope == "overall":
            profitability_analysis["overall_profitability"] = financial_engine.calculate_overall_profitability(
                purchases, campaigns, include_costs
            )
            profitability_analysis["profit_trends"] = financial_engine.analyze_profit_trends(
                purchases, campaigns
            )
            profitability_analysis["margin_analysis"] = financial_engine.analyze_profit_margins(
                purchases, campaigns
            )
            
        elif analysis_scope == "customer":
            if target_id:
                profitability_analysis["customer_profitability"] = financial_engine.analyze_customer_profitability(
                    target_id, purchases, campaigns, customers
                )
            else:
                profitability_analysis["customer_profitability_ranking"] = financial_engine.rank_customer_profitability(
                    purchases, customers, campaigns
                )
                
        elif analysis_scope == "campaign":
            if target_id:
                profitability_analysis["campaign_profitability"] = financial_engine.analyze_campaign_profitability(
                    target_id, campaigns, purchases
                )
            else:
                profitability_analysis["campaign_profitability_ranking"] = financial_engine.rank_campaign_profitability(
                    campaigns, purchases
                )
                
        elif analysis_scope == "segment":
            profitability_analysis["segment_profitability"] = financial_engine.analyze_segment_profitability(
                customers, purchases, campaigns, target_id
            )
            
        elif analysis_scope == "product":
            profitability_analysis["product_profitability"] = financial_engine.analyze_product_profitability(
                purchases, target_id
            )
        
        # Common analysis for all scopes
        profitability_analysis["profitability_insights"] = financial_engine.generate_profitability_insights(
            profitability_analysis, analysis_scope
        )
        profitability_analysis["optimization_recommendations"] = financial_engine.generate_profitability_recommendations(
            profitability_analysis, customers, campaigns, purchases
        )
        
        return profitability_analysis
        
    except Exception as e:
        logger.error(f"Profitability analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Profitability analysis failed: {str(e)}")

@router.get("/customer-lifetime-value")
async def get_customer_lifetime_value(
    calculation_method: str = Query("predictive", regex="^(historical|predictive|hybrid)$"),
    time_horizon: int = Query(365, ge=30, le=1095),
    segment_id: Optional[int] = None,
    include_predictions: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    👑 **Customer Lifetime Value Analysis**
    
    Calculate and analyze Customer Lifetime Value using various methodologies.
    """
    try:
        financial_engine = FinancialAnalyticsEngine(db)
        
        # Get relevant data
        query = db.query(Customer)
        if segment_id is not None:
            query = query.filter(Customer.segment_id == segment_id)
        
        customers = query.all()
        purchases = db.query(Purchase).filter(
            Purchase.customer_id.in_([c.customer_id for c in customers])
        ).all()
        
        if not customers or not purchases:
            return {"message": "Insufficient data for CLV analysis"}
        
        clv_analysis = {
            "analysis_metadata": {
                "calculation_method": calculation_method,
                "time_horizon_days": time_horizon,
                "segment_id": segment_id,
                "customers_analyzed": len(customers),
                "include_predictions": include_predictions,
                "generated_at": datetime.now().isoformat()
            },
            "clv_overview": financial_engine.calculate_clv_overview(
                customers, purchases, calculation_method, time_horizon
            ),
            "clv_distribution": financial_engine.analyze_clv_distribution(
                customers, purchases, calculation_method
            ),
            "clv_segments": financial_engine.segment_customers_by_clv(
                customers, purchases, calculation_method
            )
        }
        
        if include_predictions:
            clv_analysis["predictive_clv"] = financial_engine.predict_future_clv(
                customers, purchases, time_horizon
            )
            clv_analysis["clv_scenarios"] = financial_engine.generate_clv_scenarios(
                customers, purchases, time_horizon
            )
            clv_analysis["retention_impact"] = financial_engine.analyze_retention_impact_on_clv(
                customers, purchases
            )
        
        # Individual customer CLV analysis for top customers
        clv_analysis["top_value_customers"] = financial_engine.identify_top_value_customers(
            customers, purchases, calculation_method, limit=20
        )
        
        # CLV optimization recommendations
        clv_analysis["clv_optimization"] = financial_engine.generate_clv_optimization_strategies(
            customers, purchases, clv_analysis
        )
        
        return clv_analysis
        
    except Exception as e:
        logger.error(f"CLV analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"CLV analysis failed: {str(e)}")

@router.get("/financial-forecasting")
async def get_financial_forecasting(
    forecast_period: str = Query("quarterly", regex="^(monthly|quarterly|annual)$"),
    forecast_horizon: int = Query(12, ge=1, le=36),
    include_scenarios: bool = Query(True),
    confidence_intervals: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    🔮 **Financial Forecasting**
    
    Advanced financial forecasting with scenario analysis and confidence intervals.
    """
    try:
        financial_engine = FinancialAnalyticsEngine(db)
        
        # Get historical financial data
        customers = db.query(Customer).all()
        purchases = db.query(Purchase).all()
        campaigns = db.query(Campaign).all()
        
        if not purchases:
            return {"message": "Insufficient historical data for forecasting"}
        
        forecasting_analysis = {
            "forecast_metadata": {
                "forecast_period": forecast_period,
                "forecast_horizon": forecast_horizon,
                "include_scenarios": include_scenarios,
                "confidence_intervals": confidence_intervals,
                "historical_data_points": len(purchases),
                "forecast_generated_at": datetime.now().isoformat()
            },
            "revenue_forecast": financial_engine.forecast_revenue_advanced(
                purchases, customers, forecast_period, forecast_horizon
            ),
            "customer_acquisition_forecast": financial_engine.forecast_customer_acquisition(
                customers, forecast_period, forecast_horizon
            ),
            "profitability_forecast": financial_engine.forecast_profitability(
                purchases, campaigns, forecast_period, forecast_horizon
            )
        }
        
        if include_scenarios:
            forecasting_analysis["scenario_analysis"] = financial_engine.generate_forecast_scenarios(
                purchases, customers, campaigns, forecast_period, forecast_horizon
            )
            forecasting_analysis["sensitivity_analysis"] = financial_engine.perform_sensitivity_analysis(
                purchases, customers, forecast_period
            )
        
        if confidence_intervals:
            forecasting_analysis["confidence_intervals"] = financial_engine.calculate_forecast_confidence(
                forecasting_analysis, purchases, customers
            )
            forecasting_analysis["forecast_reliability"] = financial_engine.assess_forecast_reliability(
                purchases, customers, forecast_period
            )
        
        # Business implications and recommendations
        forecasting_analysis["business_implications"] = financial_engine.interpret_forecast_results(
            forecasting_analysis, customers, campaigns
        )
        forecasting_analysis["strategic_recommendations"] = financial_engine.generate_strategic_recommendations(
            forecasting_analysis, purchases, customers, campaigns
        )
        
        return forecasting_analysis
        
    except Exception as e:
        logger.error(f"Financial forecasting failed: {e}")
        raise HTTPException(status_code=500, detail=f"Financial forecasting failed: {str(e)}")

@router.get("/cost-analysis")
async def get_cost_analysis(
    cost_category: str = Query("all", regex="^(all|marketing|operational|customer_acquisition|retention)$"),
    allocation_method: str = Query("proportional", regex="^(proportional|activity_based|direct)$"),
    time_range: str = Query("90d", regex="^(30d|90d|180d|1y)$"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    💸 **Cost Analysis**
    
    Comprehensive cost analysis and allocation across business activities.
    """
    try:
        # Calculate time range
        time_mapping = {
            "30d": timedelta(days=30),
            "90d": timedelta(days=90),
            "180d": timedelta(days=180),
            "1y": timedelta(days=365)
        }
        
        start_date = datetime.now() - time_mapping[time_range]
        
        financial_engine = FinancialAnalyticsEngine(db)
        
        # Get relevant data
        campaigns = db.query(Campaign).filter(Campaign.created_at >= start_date).all()
        customers = db.query(Customer).filter(Customer.created_at >= start_date).all()
        purchases = db.query(Purchase).join(Customer).filter(
            Customer.created_at >= start_date
        ).all()
        
        cost_analysis = {
            "analysis_metadata": {
                "cost_category": cost_category,
                "allocation_method": allocation_method,
                "time_range": time_range,
                "start_date": start_date.isoformat(),
                "end_date": datetime.now().isoformat(),
                "generated_at": datetime.now().isoformat()
            },
            "cost_overview": financial_engine.calculate_cost_overview(
                campaigns, customers, cost_category, allocation_method
            ),
            "cost_breakdown": financial_engine.analyze_cost_breakdown(
                campaigns, customers, purchases, cost_category
            ),
            "cost_efficiency": financial_engine.analyze_cost_efficiency(
                campaigns, customers, purchases, allocation_method
            )
        }
        
        if cost_category in ["all", "marketing"]:
            cost_analysis["marketing_costs"] = financial_engine.analyze_marketing_costs(
                campaigns, customers, allocation_method
            )
            cost_analysis["customer_acquisition_cost"] = financial_engine.calculate_customer_acquisition_cost(
                campaigns, customers, time_range
            )
        
        if cost_category in ["all", "retention"]:
            cost_analysis["retention_costs"] = financial_engine.analyze_retention_costs(
                customers, campaigns, purchases
            )
        
        # Cost optimization recommendations
        cost_analysis["cost_optimization"] = financial_engine.generate_cost_optimization_recommendations(
            cost_analysis, campaigns, customers
        )
        
        return cost_analysis
        
    except Exception as e:
        logger.error(f"Cost analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cost analysis failed: {str(e)}")

@router.get("/roi-analysis")
async def get_roi_analysis(
    roi_scope: str = Query("campaigns", regex="^(campaigns|customers|segments|overall)$"),
    calculation_period: str = Query("90d", regex="^(30d|90d|180d|1y)$"),
    include_projected_roi: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    📈 **ROI Analysis**
    
    Return on Investment analysis across different business dimensions.
    """
    try:
        # Calculate time range
        time_mapping = {
            "30d": timedelta(days=30),
            "90d": timedelta(days=90),
            "180d": timedelta(days=180),
            "1y": timedelta(days=365)
        }
        
        start_date = datetime.now() - time_mapping[calculation_period]
        
        financial_engine = FinancialAnalyticsEngine(db)
        
        # Get relevant data
        campaigns = db.query(Campaign).filter(Campaign.created_at >= start_date).all()
        customers = db.query(Customer).filter(Customer.created_at >= start_date).all()
        purchases = db.query(Purchase).join(Customer).filter(
            Customer.created_at >= start_date
        ).all()
        
        roi_analysis = {
            "analysis_metadata": {
                "roi_scope": roi_scope,
                "calculation_period": calculation_period,
                "start_date": start_date.isoformat(),
                "end_date": datetime.now().isoformat(),
                "include_projected_roi": include_projected_roi,
                "generated_at": datetime.now().isoformat()
            }
        }
        
        if roi_scope == "campaigns":
            roi_analysis["campaign_roi"] = financial_engine.analyze_campaign_roi(
                campaigns, purchases, customers
            )
            roi_analysis["campaign_roi_ranking"] = financial_engine.rank_campaigns_by_roi(
                campaigns, purchases
            )
            
        elif roi_scope == "customers":
            roi_analysis["customer_roi"] = financial_engine.analyze_customer_roi(
                customers, purchases, campaigns
            )
            roi_analysis["customer_roi_segments"] = financial_engine.segment_customers_by_roi(
                customers, purchases, campaigns
            )
            
        elif roi_scope == "segments":
            roi_analysis["segment_roi"] = financial_engine.analyze_segment_roi(
                customers, purchases, campaigns
            )
            
        elif roi_scope == "overall":
            roi_analysis["overall_roi"] = financial_engine.calculate_overall_roi(
                campaigns, purchases, customers
            )
            roi_analysis["roi_trends"] = financial_engine.analyze_roi_trends(
                campaigns, purchases, calculation_period
            )
        
        if include_projected_roi:
            roi_analysis["projected_roi"] = financial_engine.project_future_roi(
                campaigns, customers, purchases, roi_scope
            )
            roi_analysis["roi_scenarios"] = financial_engine.generate_roi_scenarios(
                campaigns, customers, purchases
            )
        
        # ROI optimization insights
        roi_analysis["roi_insights"] = financial_engine.generate_roi_insights(
            roi_analysis, campaigns, customers, purchases
        )
        roi_analysis["roi_optimization"] = financial_engine.recommend_roi_optimizations(
            roi_analysis, campaigns, customers
        )
        
        return roi_analysis
        
    except Exception as e:
        logger.error(f"ROI analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"ROI analysis failed: {str(e)}")

@router.get("/financial-dashboard")
async def get_financial_dashboard(
    dashboard_type: str = Query("executive", regex="^(executive|operational|detailed)$"),
    time_range: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    real_time_updates: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    📊 **Financial Dashboard**
    
    Comprehensive financial dashboard with key metrics and KPIs.
    """
    try:
        # Calculate time range
        time_mapping = {
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
            "90d": timedelta(days=90),
            "1y": timedelta(days=365)
        }
        
        start_date = datetime.now() - time_mapping[time_range]
        
        financial_engine = FinancialAnalyticsEngine(db)
        
        # Get comprehensive financial data
        customers = db.query(Customer).filter(Customer.created_at >= start_date).all()
        purchases = db.query(Purchase).join(Customer).filter(
            Customer.created_at >= start_date
        ).all()
        campaigns = db.query(Campaign).filter(Campaign.created_at >= start_date).all()
        
        dashboard_data = {
            "dashboard_metadata": {
                "dashboard_type": dashboard_type,
                "time_range": time_range,
                "real_time_updates": real_time_updates,
                "data_freshness": datetime.now().isoformat(),
                "total_data_points": len(customers) + len(purchases) + len(campaigns)
            },
            "key_metrics": financial_engine.calculate_key_financial_metrics(
                customers, purchases, campaigns, dashboard_type
            ),
            "performance_indicators": financial_engine.calculate_financial_kpis(
                customers, purchases, campaigns, time_range
            ),
            "trend_analysis": financial_engine.analyze_financial_trends(
                purchases, campaigns, time_range
            )
        }
        
        if dashboard_type in ["operational", "detailed"]:
            dashboard_data["detailed_metrics"] = financial_engine.calculate_detailed_metrics(
                customers, purchases, campaigns
            )
            dashboard_data["segment_performance"] = financial_engine.analyze_segment_financial_performance(
                customers, purchases, campaigns
            )
        
        if dashboard_type == "detailed":
            dashboard_data["advanced_analytics"] = financial_engine.generate_advanced_financial_analytics(
                customers, purchases, campaigns
            )
            dashboard_data["predictive_metrics"] = financial_engine.calculate_predictive_financial_metrics(
                customers, purchases, campaigns
            )
        
        # Alerts and recommendations
        dashboard_data["financial_alerts"] = financial_engine.generate_financial_alerts(
            dashboard_data, customers, purchases, campaigns
        )
        dashboard_data["optimization_opportunities"] = financial_engine.identify_financial_optimization_opportunities(
            dashboard_data, customers, purchases, campaigns
        )
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Financial dashboard failed: {e}")
        raise HTTPException(status_code=500, detail=f"Financial dashboard failed: {str(e)}")

@router.post("/custom-financial-analysis")
async def run_custom_financial_analysis(
    analysis_request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    🔬 **Custom Financial Analysis**
    
    Run custom financial analysis based on specific business questions.
    """
    try:
        financial_engine = FinancialAnalyticsEngine(db)
        
        # Validate analysis request
        required_fields = ["analysis_question", "data_scope", "metrics_of_interest"]
        for field in required_fields:
            if field not in analysis_request:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Get relevant data based on scope
        data_scope = analysis_request["data_scope"]
        customers = db.query(Customer).all() if "customers" in data_scope else []
        purchases = db.query(Purchase).all() if "purchases" in data_scope else []
        campaigns = db.query(Campaign).all() if "campaigns" in data_scope else []
        
        # Run custom analysis
        custom_analysis = financial_engine.run_custom_financial_analysis(
            analysis_request, customers, purchases, campaigns
        )
        
        return {
            "analysis_metadata": {
                "analysis_id": f"custom_{datetime.now().timestamp()}",
                "analysis_question": analysis_request["analysis_question"],
                "data_scope": data_scope,
                "metrics_of_interest": analysis_request["metrics_of_interest"],
                "generated_at": datetime.now().isoformat()
            },
            "custom_analysis": custom_analysis,
            "methodology": financial_engine.explain_analysis_methodology(
                analysis_request
            ),
            "insights": financial_engine.interpret_custom_analysis_results(
                custom_analysis, analysis_request
            ),
            "recommendations": financial_engine.generate_custom_recommendations(
                custom_analysis, customers, purchases, campaigns
            )
        }
        
    except Exception as e:
        logger.error(f"Custom financial analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Custom financial analysis failed: {str(e)}")