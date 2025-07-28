"""
Enhanced Conversational AI with SBM Goals Integration
"""
import openai
from typing import Dict, List, Any, Optional
import json
import logging
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from core.database import get_db, Customer, Campaign, CameraData
from core.config import settings
from core.sbm_config import sbm_config
from .generative_analytics import generative_analytics

logger = logging.getLogger(__name__)

class EnhancedCRMAssistant:
    """Enhanced CRM Assistant with deep integration to analytics and SBM goals"""
    
    def __init__(self):
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.openai_available = True
        else:
            self.openai_available = False
            logger.warning("OpenAI API key not found - using enhanced fallback responses")
        
        self.conversation_history = []
        self.context_memory = {}
        self.sbm_context = sbm_config.get_ai_context()
        
    def chat(self, query: str, user_context: Dict = None, db: Session = None) -> Dict[str, Any]:
        """Enhanced chat interface with deep data integration"""
        try:
            # Update SBM context
            self.sbm_context = sbm_config.get_ai_context()
            
            # Parse user intent with enhanced understanding
            intent = self._parse_enhanced_intent(query)
            
            # Get relevant data based on intent with actual database queries
            relevant_data = self._get_enhanced_relevant_data(intent, query, db)
            
            # Generate response with SBM context
            if self.openai_available:
                response = self._generate_enhanced_ai_response(query, intent, relevant_data, user_context)
            else:
                response = self._generate_enhanced_fallback_response(intent, relevant_data)
            
            # Generate data-driven insights
            insights = self._generate_contextual_insights(intent, relevant_data)
            
            # Store conversation with context
            self._store_conversation(query, response, user_context, insights)
            
            return {
                "response": response,
                "intent": intent,
                "data_used": relevant_data.get("summary", ""),
                "insights": insights,
                "suggested_actions": self._get_enhanced_suggested_actions(intent, relevant_data),
                "visualizations": self._suggest_visualizations(intent, relevant_data),
                "timestamp": datetime.now().isoformat(),
                "sbm_alignment": self._check_goal_alignment(intent, relevant_data)
            }
            
        except Exception as e:
            logger.error(f"Enhanced chat error: {e}")
            return {
                "response": "I apologize for the error. Let me help you with your CRM needs. What would you like to know?",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _parse_enhanced_intent(self, query: str) -> Dict[str, Any]:
        """Enhanced intent parsing with more granular understanding"""
        query_lower = query.lower()
        
        # Campaign analysis intents
        if any(word in query_lower for word in ['campaign', 'marketing', 'promotion']):
            if any(word in query_lower for word in ['performance', 'roi', 'results', 'effective']):
                return {
                    "type": "campaign_analysis",
                    "subtype": "performance",
                    "metrics": ["roi", "conversion", "engagement"],
                    "time_sensitive": True
                }
            elif any(word in query_lower for word in ['create', 'new', 'launch', 'design']):
                return {
                    "type": "campaign_creation",
                    "subtype": "ai_assisted",
                    "needs_segmentation": True
                }
            elif any(word in query_lower for word in ['optimize', 'improve', 'better']):
                return {
                    "type": "campaign_optimization",
                    "subtype": "recommendations",
                    "focus": "improvement"
                }
            else:
                return {"type": "campaign_general", "subtype": "overview"}
        
        # Customer analytics intents
        elif any(word in query_lower for word in ['customer', 'segment', 'profile', 'behavior']):
            if 'churn' in query_lower or 'leaving' in query_lower or 'risk' in query_lower:
                return {
                    "type": "customer_analytics",
                    "subtype": "churn_prediction",
                    "urgency": "high"
                }
            elif any(word in query_lower for word in ['value', 'lifetime', 'clv', 'worth']):
                return {
                    "type": "customer_analytics",
                    "subtype": "lifetime_value",
                    "metrics": ["clv", "revenue_potential"]
                }
            elif 'segment' in query_lower:
                return {
                    "type": "customer_analytics",
                    "subtype": "segmentation",
                    "analysis_depth": "detailed"
                }
            else:
                return {"type": "customer_analytics", "subtype": "general"}
        
        # Business performance intents
        elif any(word in query_lower for word in ['revenue', 'sales', 'profit', 'growth']):
            return {
                "type": "business_performance",
                "subtype": "financial",
                "metrics": ["revenue", "growth_rate", "profitability"]
            }
        
        # Goal alignment intents
        elif any(word in query_lower for word in ['goal', 'target', 'objective', 'kpi']):
            return {
                "type": "goal_tracking",
                "subtype": "progress",
                "alignment_check": True
            }
        
        # Predictive analytics intents
        elif any(word in query_lower for word in ['predict', 'forecast', 'future', 'trend']):
            return {
                "type": "predictive_analytics",
                "subtype": "forecasting",
                "time_horizon": "medium"
            }
        
        # Real-time analytics
        elif any(word in query_lower for word in ['now', 'current', 'real-time', 'today']):
            return {
                "type": "real_time_analytics",
                "subtype": "current_state",
                "refresh_rate": "live"
            }
        
        else:
            return {"type": "general", "subtype": "help"}
    
    def _get_enhanced_relevant_data(self, intent: Dict, query: str, db: Session = None) -> Dict[str, Any]:
        """Get enhanced relevant data with actual database queries"""
        if not db:
            db = next(get_db())
        
        data = {"summary": "", "details": {}}
        
        try:
            # Parse date range from query if present
            date_range = self._extract_date_range(query)
            
            if intent["type"] == "campaign_analysis":
                data = self._get_campaign_performance_data(db, date_range)
                
            elif intent["type"] == "campaign_creation":
                data = self._get_campaign_creation_data(db)
                
            elif intent["type"] == "campaign_optimization":
                data = self._get_campaign_optimization_data(db, date_range)
                
            elif intent["type"] == "customer_analytics":
                if intent["subtype"] == "churn_prediction":
                    data = self._get_churn_analysis_data(db, date_range)
                elif intent["subtype"] == "lifetime_value":
                    data = self._get_clv_analysis_data(db, date_range)
                elif intent["subtype"] == "segmentation":
                    data = self._get_segmentation_data(db, date_range)
                else:
                    data = self._get_customer_overview_data(db, date_range)
                    
            elif intent["type"] == "business_performance":
                data = self._get_business_performance_data(db, date_range)
                
            elif intent["type"] == "goal_tracking":
                data = self._get_goal_progress_data(db)
                
            elif intent["type"] == "predictive_analytics":
                data = self._get_predictive_analytics_data(db)
                
            elif intent["type"] == "real_time_analytics":
                data = self._get_real_time_data(db)
            
        except Exception as e:
            logger.error(f"Data retrieval error: {e}")
            data = {"summary": "Data retrieval error occurred", "error": str(e)}
        
        return data
    
    def _extract_date_range(self, query: str) -> Dict[str, datetime]:
        """Extract date range from query text"""
        query_lower = query.lower()
        
        # Default to last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Check for specific time mentions
        if 'today' in query_lower:
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif 'yesterday' in query_lower:
            end_date = end_date - timedelta(days=1)
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif 'this week' in query_lower or 'current week' in query_lower:
            start_date = end_date - timedelta(days=end_date.weekday())
        elif 'last week' in query_lower:
            start_date = end_date - timedelta(days=end_date.weekday() + 7)
            end_date = start_date + timedelta(days=6)
        elif 'this month' in query_lower or 'current month' in query_lower:
            start_date = end_date.replace(day=1)
        elif 'last month' in query_lower:
            start_date = (end_date.replace(day=1) - timedelta(days=1)).replace(day=1)
            end_date = end_date.replace(day=1) - timedelta(days=1)
        elif 'last 7 days' in query_lower:
            start_date = end_date - timedelta(days=7)
        elif 'last 90 days' in query_lower:
            start_date = end_date - timedelta(days=90)
        elif 'this year' in query_lower:
            start_date = end_date.replace(month=1, day=1)
        
        return {"start_date": start_date, "end_date": end_date}
    
    def _get_campaign_performance_data(self, db: Session, date_range: Dict) -> Dict[str, Any]:
        """Get detailed campaign performance data"""
        campaigns = db.query(Campaign).filter(
            Campaign.created_at >= date_range["start_date"],
            Campaign.created_at <= date_range["end_date"]
        ).all()
        
        if not campaigns:
            return {"summary": "No campaigns found in the specified period"}
        
        # Calculate performance metrics
        total_budget = sum(c.budget for c in campaigns)
        active_campaigns = [c for c in campaigns if c.status == "active"]
        completed_campaigns = [c for c in campaigns if c.status == "completed"]
        
        # ROI calculations
        campaign_performance = []
        for campaign in campaigns:
            roi = campaign.actual_roi or campaign.predicted_roi or 0
            revenue = campaign.budget * roi
            campaign_performance.append({
                "id": str(campaign.id),
                "name": campaign.name,
                "status": campaign.status,
                "budget": campaign.budget,
                "roi": roi,
                "revenue": revenue,
                "profit": revenue - campaign.budget,
                "efficiency": roi / (campaign.budget / 10000) if campaign.budget > 0 else 0
            })
        
        # Sort by ROI
        campaign_performance.sort(key=lambda x: x["roi"], reverse=True)
        
        return {
            "summary": f"Analyzed {len(campaigns)} campaigns with ${total_budget:,.2f} total budget",
            "details": {
                "total_campaigns": len(campaigns),
                "active_campaigns": len(active_campaigns),
                "completed_campaigns": len(completed_campaigns),
                "total_budget": total_budget,
                "average_roi": sum(c["roi"] for c in campaign_performance) / len(campaign_performance) if campaign_performance else 0,
                "best_performer": campaign_performance[0] if campaign_performance else None,
                "worst_performer": campaign_performance[-1] if campaign_performance else None,
                "campaigns": campaign_performance[:10]  # Top 10
            },
            "date_range": {
                "start": date_range["start_date"].isoformat(),
                "end": date_range["end_date"].isoformat()
            }
        }
    
    def _get_campaign_creation_data(self, db: Session) -> Dict[str, Any]:
        """Get data for campaign creation assistance"""
        # Get customer segments
        customers = db.query(Customer).all()
        total_customers = len(customers)
        
        # Segment analysis
        segment_distribution = {}
        for customer in customers:
            seg_id = customer.segment_id or "Unassigned"
            segment_distribution[seg_id] = segment_distribution.get(seg_id, 0) + 1
        
        # Recent successful campaigns
        recent_campaigns = db.query(Campaign).filter(
            Campaign.actual_roi > 2.0
        ).order_by(Campaign.created_at.desc()).limit(5).all()
        
        return {
            "summary": "Campaign creation data ready",
            "details": {
                "total_customers": total_customers,
                "segment_distribution": segment_distribution,
                "recommended_segments": self._identify_opportunity_segments(segment_distribution),
                "successful_campaign_templates": [
                    {
                        "name": c.name,
                        "roi": c.actual_roi,
                        "budget": c.budget,
                        "duration": (c.end_date - c.start_date).days if c.end_date and c.start_date else None
                    } for c in recent_campaigns
                ],
                "seasonal_recommendations": self._get_seasonal_recommendations(),
                "budget_recommendations": self._calculate_budget_recommendations(total_customers)
            }
        }
    
    def _get_campaign_optimization_data(self, db: Session, date_range: Dict) -> Dict[str, Any]:
        """Get data for campaign optimization"""
        # Get underperforming campaigns
        campaigns = db.query(Campaign).filter(
            Campaign.status == "active"
        ).all()
        
        optimization_opportunities = []
        for campaign in campaigns:
            roi = campaign.actual_roi or campaign.predicted_roi or 0
            if roi < 1.5:  # Underperforming threshold
                optimization_opportunities.append({
                    "campaign_id": str(campaign.id),
                    "name": campaign.name,
                    "current_roi": roi,
                    "budget": campaign.budget,
                    "improvement_potential": "high" if roi < 1.0 else "medium",
                    "recommendations": self._generate_optimization_recommendations(campaign)
                })
        
        return {
            "summary": f"Found {len(optimization_opportunities)} campaigns with optimization potential",
            "details": {
                "total_active_campaigns": len(campaigns),
                "underperforming_count": len(optimization_opportunities),
                "optimization_opportunities": optimization_opportunities,
                "general_recommendations": [
                    "A/B test different messaging",
                    "Refine target audience",
                    "Adjust campaign timing",
                    "Optimize channel mix"
                ]
            }
        }
    
    def _get_churn_analysis_data(self, db: Session, date_range: Dict) -> Dict[str, Any]:
        """Get customer churn analysis data"""
        customers = db.query(Customer).all()
        
        # Simple churn risk calculation based on rating
        churn_risk_distribution = {
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        high_risk_customers = []
        for customer in customers:
            if customer.rating_id <= 2:
                churn_risk_distribution["high"] += 1
                high_risk_customers.append({
                    "customer_id": customer.customer_id,
                    "age": customer.age,
                    "rating": customer.rating_id,
                    "segment": customer.segment_id,
                    "risk_score": 0.8
                })
            elif customer.rating_id == 3:
                churn_risk_distribution["medium"] += 1
            else:
                churn_risk_distribution["low"] += 1
        
        return {
            "summary": f"{churn_risk_distribution['high']} customers at high churn risk",
            "details": {
                "total_customers": len(customers),
                "churn_risk_distribution": churn_risk_distribution,
                "high_risk_percentage": (churn_risk_distribution["high"] / len(customers) * 100) if customers else 0,
                "high_risk_customers": high_risk_customers[:20],  # Top 20
                "churn_factors": [
                    "Low satisfaction ratings",
                    "Decreased engagement",
                    "Competitive offers",
                    "Service issues"
                ],
                "retention_strategies": [
                    "Personalized retention offers",
                    "Proactive customer service",
                    "Loyalty program enrollment",
                    "Win-back campaigns"
                ]
            }
        }
    
    def _get_clv_analysis_data(self, db: Session, date_range: Dict) -> Dict[str, Any]:
        """Get customer lifetime value analysis"""
        customers = db.query(Customer).all()
        
        # Calculate CLV segments
        clv_segments = []
        for customer in customers:
            # Simplified CLV calculation
            clv = customer.rating_id * customer.age * 100  # Base calculation
            clv_segments.append({
                "customer_id": customer.customer_id,
                "clv": clv,
                "segment": customer.segment_id,
                "rating": customer.rating_id
            })
        
        clv_segments.sort(key=lambda x: x["clv"], reverse=True)
        
        # Calculate statistics
        clv_values = [c["clv"] for c in clv_segments]
        avg_clv = np.mean(clv_values) if clv_values else 0
        
        return {
            "summary": f"Average CLV: ${avg_clv:,.2f}",
            "details": {
                "total_customers": len(customers),
                "average_clv": avg_clv,
                "median_clv": np.median(clv_values) if clv_values else 0,
                "top_10_percent_threshold": np.percentile(clv_values, 90) if clv_values else 0,
                "high_value_customers": [c for c in clv_segments if c["clv"] > avg_clv * 2][:20],
                "clv_distribution": {
                    "high": len([c for c in clv_segments if c["clv"] > avg_clv * 1.5]),
                    "medium": len([c for c in clv_segments if avg_clv * 0.5 <= c["clv"] <= avg_clv * 1.5]),
                    "low": len([c for c in clv_segments if c["clv"] < avg_clv * 0.5])
                }
            }
        }
    
    def _get_segmentation_data(self, db: Session, date_range: Dict) -> Dict[str, Any]:
        """Get detailed segmentation data"""
        customers = db.query(Customer).filter(
            Customer.created_at >= date_range["start_date"],
            Customer.created_at <= date_range["end_date"]
        ).all()
        
        # Segment analysis
        segment_profiles = {}
        for customer in customers:
            seg_id = customer.segment_id or "Unassigned"
            if seg_id not in segment_profiles:
                segment_profiles[seg_id] = {
                    "count": 0,
                    "total_age": 0,
                    "ratings": [],
                    "gender_dist": {}
                }
            
            segment_profiles[seg_id]["count"] += 1
            segment_profiles[seg_id]["total_age"] += customer.age
            segment_profiles[seg_id]["ratings"].append(customer.rating_id)
            
            gender = customer.gender or "Unknown"
            segment_profiles[seg_id]["gender_dist"][gender] = \
                segment_profiles[seg_id]["gender_dist"].get(gender, 0) + 1
        
        # Calculate segment characteristics
        segment_analysis = []
        for seg_id, profile in segment_profiles.items():
            avg_age = profile["total_age"] / profile["count"] if profile["count"] > 0 else 0
            avg_rating = np.mean(profile["ratings"]) if profile["ratings"] else 0
            
            segment_analysis.append({
                "segment_id": seg_id,
                "size": profile["count"],
                "percentage": (profile["count"] / len(customers) * 100) if customers else 0,
                "avg_age": avg_age,
                "avg_rating": avg_rating,
                "gender_distribution": profile["gender_dist"],
                "segment_name": self._get_segment_name(seg_id),
                "characteristics": self._get_segment_characteristics(seg_id)
            })
        
        segment_analysis.sort(key=lambda x: x["size"], reverse=True)
        
        return {
            "summary": f"Analyzed {len(customers)} customers across {len(segment_analysis)} segments",
            "details": {
                "total_customers": len(customers),
                "segment_count": len(segment_analysis),
                "segments": segment_analysis,
                "largest_segment": segment_analysis[0] if segment_analysis else None,
                "smallest_segment": segment_analysis[-1] if segment_analysis else None,
                "segmentation_quality": self._assess_segmentation_quality(segment_analysis)
            }
        }
    
    def _get_customer_overview_data(self, db: Session, date_range: Dict) -> Dict[str, Any]:
        """Get general customer overview data"""
        customers = db.query(Customer).filter(
            Customer.created_at >= date_range["start_date"],
            Customer.created_at <= date_range["end_date"]
        ).all()
        
        new_customers = db.query(Customer).filter(
            Customer.created_at >= datetime.now() - timedelta(days=30)
        ).count()
        
        # Demographics analysis
        age_groups = {"<25": 0, "25-34": 0, "35-44": 0, "45-54": 0, "55+": 0}
        gender_dist = {}
        rating_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for customer in customers:
            # Age grouping
            if customer.age < 25:
                age_groups["<25"] += 1
            elif customer.age < 35:
                age_groups["25-34"] += 1
            elif customer.age < 45:
                age_groups["35-44"] += 1
            elif customer.age < 55:
                age_groups["45-54"] += 1
            else:
                age_groups["55+"] += 1
            
            # Gender
            gender = customer.gender or "Unknown"
            gender_dist[gender] = gender_dist.get(gender, 0) + 1
            
            # Rating
            if customer.rating_id in rating_dist:
                rating_dist[customer.rating_id] += 1
        
        return {
            "summary": f"Total {len(customers)} customers, {new_customers} new in last 30 days",
            "details": {
                "total_customers": len(customers),
                "new_customers_30d": new_customers,
                "growth_rate": (new_customers / len(customers) * 100) if customers else 0,
                "demographics": {
                    "age_groups": age_groups,
                    "gender_distribution": gender_dist,
                    "average_age": np.mean([c.age for c in customers]) if customers else 0
                },
                "satisfaction": {
                    "rating_distribution": rating_dist,
                    "average_rating": np.mean([c.rating_id for c in customers]) if customers else 0,
                    "satisfied_percentage": (sum(rating_dist.get(i, 0) for i in [4, 5]) / len(customers) * 100) if customers else 0
                }
            }
        }
    
    def _get_business_performance_data(self, db: Session, date_range: Dict) -> Dict[str, Any]:
        """Get business performance metrics"""
        # Get campaign performance
        campaigns = db.query(Campaign).filter(
            Campaign.created_at >= date_range["start_date"],
            Campaign.created_at <= date_range["end_date"]
        ).all()
        
        total_budget = sum(c.budget for c in campaigns)
        total_revenue = sum(c.budget * (c.actual_roi or c.predicted_roi or 0) for c in campaigns)
        
        # Customer metrics
        total_customers = db.query(Customer).count()
        new_customers = db.query(Customer).filter(
            Customer.created_at >= date_range["start_date"]
        ).count()
        
        # Goal progress
        goal_progress = sbm_config._calculate_performance_summary()
        
        return {
            "summary": f"Revenue: ${total_revenue:,.2f}, ROI: {(total_revenue/total_budget - 1)*100:.1f}%",
            "details": {
                "financial_metrics": {
                    "total_revenue": total_revenue,
                    "total_investment": total_budget,
                    "net_profit": total_revenue - total_budget,
                    "roi_percentage": ((total_revenue/total_budget - 1)*100) if total_budget > 0 else 0
                },
                "customer_metrics": {
                    "total_customers": total_customers,
                    "new_customers": new_customers,
                    "acquisition_rate": (new_customers / total_customers * 100) if total_customers > 0 else 0
                },
                "campaign_metrics": {
                    "total_campaigns": len(campaigns),
                    "average_campaign_roi": sum(c.actual_roi or c.predicted_roi or 0 for c in campaigns) / len(campaigns) if campaigns else 0
                },
                "goal_performance": goal_progress,
                "period": {
                    "start": date_range["start_date"].isoformat(),
                    "end": date_range["end_date"].isoformat(),
                    "days": (date_range["end_date"] - date_range["start_date"]).days
                }
            }
        }
    
    def _get_goal_progress_data(self, db: Session) -> Dict[str, Any]:
        """Get detailed goal progress data"""
        sbm_context = sbm_config.get_ai_context()
        goals = sbm_config.config.goals
        
        goal_details = []
        for goal in goals:
            progress = (goal.current_value / goal.target_value * 100) if goal.target_value else 0
            goal_details.append({
                "goal_id": goal.goal_id,
                "name": goal.name,
                "description": goal.description,
                "priority": goal.priority,
                "progress_percentage": progress,
                "current_value": goal.current_value,
                "target_value": goal.target_value,
                "status": "on_track" if progress >= 80 else "needs_attention" if progress >= 50 else "at_risk",
                "timeline": goal.timeline,
                "kpis": goal.kpis
            })
        
        return {
            "summary": f"{len([g for g in goal_details if g['status'] == 'on_track'])} of {len(goals)} goals on track",
            "details": {
                "total_goals": len(goals),
                "goals": goal_details,
                "high_priority_goals": [g for g in goal_details if g["priority"] == "high"],
                "at_risk_goals": [g for g in goal_details if g["status"] == "at_risk"],
                "overall_performance": sbm_context["performance_summary"]
            }
        }
    
    def _get_predictive_analytics_data(self, db: Session) -> Dict[str, Any]:
        """Get predictive analytics data"""
        customers = db.query(Customer).all()
        campaigns = db.query(Campaign).filter(Campaign.status == "active").all()
        
        # Revenue forecast (simplified)
        avg_customer_value = 500  # Base value
        growth_rate = 0.05  # 5% monthly growth
        
        monthly_forecast = []
        current_revenue = len(customers) * avg_customer_value
        for month in range(6):
            forecast_revenue = current_revenue * (1 + growth_rate) ** month
            monthly_forecast.append({
                "month": month + 1,
                "revenue": forecast_revenue,
                "customer_base": int(len(customers) * (1 + growth_rate * 0.5) ** month)
            })
        
        return {
            "summary": "6-month forecast generated with 5% growth projection",
            "details": {
                "revenue_forecast": monthly_forecast,
                "growth_assumptions": {
                    "monthly_growth_rate": growth_rate * 100,
                    "customer_acquisition_rate": growth_rate * 0.5 * 100,
                    "average_customer_value": avg_customer_value
                },
                "predicted_trends": [
                    "Increasing mobile engagement",
                    "Growing premium segment",
                    "Seasonal peak in Q4"
                ],
                "risk_factors": [
                    "Market competition",
                    "Economic conditions",
                    "Seasonal variations"
                ]
            }
        }
    
    def _get_real_time_data(self, db: Session) -> Dict[str, Any]:
        """Get real-time analytics data"""
        # Today's metrics
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        today_customers = db.query(Customer).filter(
            Customer.created_at >= today_start
        ).count()
        
        active_campaigns = db.query(Campaign).filter(
            Campaign.status == "active"
        ).count()
        
        # Simulated real-time traffic
        current_hour = datetime.now().hour
        estimated_traffic = self._estimate_hourly_traffic(current_hour)
        
        return {
            "summary": f"Real-time: {today_customers} new customers today, {estimated_traffic} current visitors",
            "details": {
                "current_metrics": {
                    "timestamp": datetime.now().isoformat(),
                    "new_customers_today": today_customers,
                    "active_campaigns": active_campaigns,
                    "estimated_visitors": estimated_traffic,
                    "peak_hour_prediction": "2:00 PM - 4:00 PM"
                },
                "hourly_trends": {
                    "current_hour": current_hour,
                    "traffic_level": "high" if estimated_traffic > 200 else "medium" if estimated_traffic > 100 else "low",
                    "compared_to_average": "+15%" if current_hour in [14, 15, 16] else "-5%"
                },
                "alerts": self._generate_real_time_alerts(today_customers, estimated_traffic)
            }
        }
    
    def _generate_enhanced_ai_response(self, query: str, intent: Dict, data: Dict, user_context: Dict) -> str:
        """Generate enhanced AI response with SBM context"""
        try:
            # Build comprehensive context
            sbm_goals = sbm_config.get_ai_context()
            
            context_prompt = f"""
You are an advanced AI assistant for {sbm_goals['business_name']}, helping the marketing team make data-driven decisions.

Company Context:
- Vision: {sbm_goals['vision']}
- Mission: {sbm_goals['mission']}
- High Priority Goals: {json.dumps(sbm_goals['high_priority_goals'], indent=2)}
- Current Performance: {json.dumps(sbm_goals['performance_summary'], indent=2)}

Query: "{query}"
Intent: {json.dumps(intent)}
Relevant Data: {json.dumps(data, indent=2)}

AI Preferences: {json.dumps(sbm_goals['ai_preferences'])}

Provide a response that:
1. Directly addresses the query with specific data points
2. Aligns insights with SBM's business goals
3. Offers actionable recommendations
4. Highlights opportunities and risks
5. Uses a {sbm_goals['ai_preferences']['response_style']} tone

Keep the response concise but comprehensive (3-5 sentences with key data points).
"""
            
            response = openai.ChatCompletion.create(
                model="gpt-4" if intent.get("subtype") == "ai_assisted" else "gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert CRM AI assistant for a premium shopping mall."},
                    {"role": "user", "content": context_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Enhanced AI response error: {e}")
            return self._generate_enhanced_fallback_response(intent, data)
    
    def _generate_enhanced_fallback_response(self, intent: Dict, data: Dict) -> str:
        """Generate enhanced fallback response when AI is unavailable"""
        
        if intent["type"] == "campaign_analysis":
            details = data.get("details", {})
            return f"I've analyzed {details.get('total_campaigns', 0)} campaigns with an average ROI of {details.get('average_roi', 0):.2f}x. " \
                   f"Your best performer is generating {details.get('best_performer', {}).get('roi', 0):.2f}x ROI. " \
                   f"Consider scaling successful campaigns and optimizing the {details.get('active_campaigns', 0)} currently active ones."
        
        elif intent["type"] == "customer_analytics":
            if intent["subtype"] == "churn_prediction":
                details = data.get("details", {})
                return f"Alert: {details.get('churn_risk_distribution', {}).get('high', 0)} customers are at high churn risk " \
                       f"({details.get('high_risk_percentage', 0):.1f}% of your base). " \
                       f"Immediate action recommended: launch targeted retention campaigns focusing on personalized offers and engagement."
            
            elif intent["subtype"] == "lifetime_value":
                details = data.get("details", {})
                return f"Your customer base has an average CLV of ${details.get('average_clv', 0):,.2f}. " \
                       f"{len(details.get('high_value_customers', []))} customers are high-value (2x+ average). " \
                       f"Focus on retaining and expanding these relationships through premium services."
        
        elif intent["type"] == "business_performance":
            details = data.get("details", {})
            financial = details.get("financial_metrics", {})
            return f"Performance Update: ${financial.get('total_revenue', 0):,.2f} revenue with " \
                   f"{financial.get('roi_percentage', 0):.1f}% ROI. " \
                   f"{details.get('goal_performance', {}).get('goals_on_track', 0)} of your business goals are on track. " \
                   f"Focus on optimizing campaigns to hit your targets."
        
        elif intent["type"] == "goal_tracking":
            details = data.get("details", {})
            at_risk = details.get("at_risk_goals", [])
            return f"Goal Status: {details.get('overall_performance', {}).get('goals_on_track', 0)} of " \
                   f"{details.get('total_goals', 0)} goals are on track. " \
                   f"{len(at_risk)} goals need immediate attention. " \
                   f"Priority focus should be on high-impact initiatives to accelerate progress."
        
        else:
            return "I'm here to help you optimize your CRM performance. I can analyze campaigns, predict customer behavior, " \
                   "track business goals, and provide AI-powered recommendations. What would you like to explore?"
    
    def _generate_contextual_insights(self, intent: Dict, data: Dict) -> List[Dict[str, Any]]:
        """Generate contextual insights based on data"""
        insights = []
        
        if intent["type"] == "campaign_analysis":
            details = data.get("details", {})
            if details.get("average_roi", 0) < 2.0:
                insights.append({
                    "type": "optimization_opportunity",
                    "title": "ROI Below Target",
                    "description": "Average campaign ROI is below the 2x target",
                    "recommendation": "Review targeting and messaging for underperforming campaigns"
                })
        
        elif intent["type"] == "customer_analytics":
            if intent["subtype"] == "churn_prediction":
                high_risk = data.get("details", {}).get("churn_risk_distribution", {}).get("high", 0)
                if high_risk > 100:
                    insights.append({
                        "type": "urgent_action",
                        "title": "High Churn Risk Alert",
                        "description": f"{high_risk} customers at immediate risk",
                        "recommendation": "Launch emergency retention campaign within 48 hours"
                    })
        
        # Goal alignment insights
        sbm_goals = sbm_config.get_goals_by_priority("high")
        for goal in sbm_goals:
            if goal.current_value < goal.target_value * 0.8:
                insights.append({
                    "type": "goal_risk",
                    "title": f"{goal.name} Behind Target",
                    "description": f"Currently at {(goal.current_value/goal.target_value*100):.1f}% of target",
                    "recommendation": f"Accelerate initiatives for {goal.name}"
                })
        
        return insights
    
    def _get_enhanced_suggested_actions(self, intent: Dict, data: Dict) -> List[Dict[str, str]]:
        """Get enhanced suggested actions with context"""
        actions = []
        
        if intent["type"] == "campaign_analysis":
            actions.extend([
                {"action": "Optimize Underperformers", "urgency": "high", "impact": "immediate"},
                {"action": "Scale Best Performers", "urgency": "medium", "impact": "high"},
                {"action": "A/B Test New Variants", "urgency": "low", "impact": "long-term"}
            ])
        
        elif intent["type"] == "customer_analytics":
            if intent["subtype"] == "churn_prediction":
                actions.extend([
                    {"action": "Launch Retention Campaign", "urgency": "immediate", "impact": "high"},
                    {"action": "Personal Outreach to High-Risk", "urgency": "high", "impact": "medium"},
                    {"action": "Analyze Churn Patterns", "urgency": "medium", "impact": "strategic"}
                ])
        
        return actions
    
    def _suggest_visualizations(self, intent: Dict, data: Dict) -> List[Dict[str, str]]:
        """Suggest relevant visualizations"""
        visualizations = []
        
        if intent["type"] == "campaign_analysis":
            visualizations.extend([
                {"type": "bar_chart", "title": "Campaign ROI Comparison", "data_key": "campaigns"},
                {"type": "line_chart", "title": "Performance Trend", "data_key": "performance_trend"},
                {"type": "pie_chart", "title": "Budget Distribution", "data_key": "budget_allocation"}
            ])
        
        elif intent["type"] == "customer_analytics":
            visualizations.extend([
                {"type": "heatmap", "title": "Segment Distribution", "data_key": "segments"},
                {"type": "scatter_plot", "title": "CLV vs Engagement", "data_key": "clv_analysis"},
                {"type": "funnel", "title": "Customer Journey", "data_key": "journey_stages"}
            ])
        
        return visualizations
    
    def _check_goal_alignment(self, intent: Dict, data: Dict) -> Dict[str, Any]:
        """Check how the current query/action aligns with SBM goals"""
        alignment = {
            "aligned_goals": [],
            "alignment_score": 0,
            "recommendations": []
        }
        
        sbm_goals = sbm_config.config.goals
        
        # Check alignment based on intent
        if intent["type"] in ["campaign_analysis", "campaign_optimization"]:
            revenue_goal = next((g for g in sbm_goals if g.goal_id == "revenue_growth"), None)
            if revenue_goal:
                alignment["aligned_goals"].append(revenue_goal.name)
                alignment["alignment_score"] = 0.8
        
        elif intent["type"] == "customer_analytics":
            satisfaction_goal = next((g for g in sbm_goals if g.goal_id == "customer_satisfaction"), None)
            if satisfaction_goal:
                alignment["aligned_goals"].append(satisfaction_goal.name)
                alignment["alignment_score"] = 0.9
        
        # Generate alignment recommendations
        if alignment["alignment_score"] < 0.7:
            alignment["recommendations"].append("Consider how this action supports your primary business goals")
        
        return alignment
    
    # Helper methods for data processing
    def _identify_opportunity_segments(self, distribution: Dict) -> List[Dict[str, Any]]:
        """Identify segments with growth opportunities"""
        opportunities = []
        total = sum(distribution.values())
        
        for seg_id, count in distribution.items():
            percentage = (count / total * 100) if total > 0 else 0
            if percentage < 20:  # Underrepresented segments
                opportunities.append({
                    "segment_id": seg_id,
                    "current_size": count,
                    "growth_potential": "high",
                    "recommended_action": "Targeted acquisition campaign"
                })
        
        return opportunities
    
    def _get_seasonal_recommendations(self) -> List[str]:
        """Get seasonal campaign recommendations"""
        month = datetime.now().month
        
        if month in [11, 12]:  # Holiday season
            return ["Holiday shopping campaigns", "Gift guide promotions", "Year-end loyalty rewards"]
        elif month in [6, 7, 8]:  # Summer
            return ["Summer sale events", "Tourist-focused campaigns", "Outdoor activity promotions"]
        elif month in [3, 4, 5]:  # Spring
            return ["Spring renewal campaigns", "New season collections", "Health & wellness focus"]
        else:  # Fall
            return ["Back-to-school promotions", "Fall fashion campaigns", "Harvest festival events"]
    
    def _calculate_budget_recommendations(self, total_customers: int) -> Dict[str, Any]:
        """Calculate recommended campaign budgets"""
        return {
            "small_campaign": total_customers * 5,  # $5 per customer
            "medium_campaign": total_customers * 10,
            "large_campaign": total_customers * 20,
            "recommendation": "Start with medium budget and scale based on performance"
        }
    
    def _generate_optimization_recommendations(self, campaign) -> List[str]:
        """Generate specific optimization recommendations for a campaign"""
        recommendations = []
        
        roi = campaign.actual_roi or campaign.predicted_roi or 0
        
        if roi < 1.0:
            recommendations.extend([
                "Review and refine target audience",
                "Test new creative messaging",
                "Consider pausing and restructuring"
            ])
        elif roi < 1.5:
            recommendations.extend([
                "A/B test different offers",
                "Expand to similar audiences",
                "Optimize delivery timing"
            ])
        else:
            recommendations.extend([
                "Increase budget allocation",
                "Expand to new channels",
                "Create lookalike audiences"
            ])
        
        return recommendations
    
    def _get_segment_name(self, segment_id) -> str:
        """Get friendly name for segment"""
        segment_names = {
            0: "Tech-Savvy Professionals",
            1: "Budget-Conscious Families",
            2: "International Tourists",
            3: "Event-Driven Visitors",
            4: "Premium Mature Shoppers",
            5: "Deal Seekers",
            "Unassigned": "Unsegmented Customers"
        }
        return segment_names.get(segment_id, f"Segment {segment_id}")
    
    def _get_segment_characteristics(self, segment_id) -> List[str]:
        """Get segment characteristics"""
        characteristics = {
            0: ["Digital-first", "Early adopters", "Convenience focused"],
            1: ["Value seekers", "Family oriented", "Practical"],
            2: ["Experience seekers", "High spending", "Short visit duration"],
            3: ["Social", "Event motivated", "Group shopping"],
            4: ["Quality focused", "Brand loyal", "Service oriented"],
            5: ["Price sensitive", "Promotion driven", "Comparison shoppers"]
        }
        return characteristics.get(segment_id, ["Diverse preferences"])
    
    def _assess_segmentation_quality(self, segments: List[Dict]) -> Dict[str, Any]:
        """Assess the quality of customer segmentation"""
        if not segments:
            return {"score": 0, "assessment": "No segmentation data"}
        
        # Calculate distribution balance
        sizes = [s["size"] for s in segments]
        avg_size = np.mean(sizes)
        std_size = np.std(sizes)
        balance_score = 1 - (std_size / avg_size) if avg_size > 0 else 0
        
        return {
            "score": balance_score,
            "assessment": "Well balanced" if balance_score > 0.7 else "Imbalanced",
            "recommendation": "Consider rebalancing segments" if balance_score < 0.7 else "Maintain current segmentation"
        }
    
    def _estimate_hourly_traffic(self, hour: int) -> int:
        """Estimate mall traffic for given hour"""
        # Typical mall traffic pattern
        traffic_pattern = {
            10: 50, 11: 100, 12: 200, 13: 250, 14: 300, 15: 350,
            16: 300, 17: 250, 18: 200, 19: 150, 20: 100, 21: 50
        }
        return traffic_pattern.get(hour, 25)
    
    def _generate_real_time_alerts(self, new_customers: int, traffic: int) -> List[Dict[str, str]]:
        """Generate real-time alerts"""
        alerts = []
        
        if traffic > 300:
            alerts.append({
                "type": "high_traffic",
                "message": "High traffic detected - ensure adequate staffing",
                "severity": "medium"
            })
        
        if new_customers > 50:
            alerts.append({
                "type": "high_acquisition",
                "message": f"{new_customers} new customers today - above average",
                "severity": "positive"
            })
        
        return alerts
    
    def _store_conversation(self, query: str, response: str, user_context: Dict, insights: List[Dict]):
        """Store conversation with enhanced context"""
        conversation_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response,
            "insights": insights,
            "user_context": user_context or {},
            "sbm_goals_version": self.sbm_context.get("updated_at", "")
        }
        
        self.conversation_history.append(conversation_entry)
        
        # Keep only last 20 conversations for richer context
        if len(self.conversation_history) > 20:
            self.conversation_history.pop(0)
    
    def get_conversation_history(self) -> List[Dict]:
        """Get recent conversation history"""
        return self.conversation_history[-10:]  # Last 10 conversations
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.context_memory = {}

# Create global instance
enhanced_crm_assistant = EnhancedCRMAssistant()