"""
Admin-AI Chat Assistant for Analytics and Campaign Insights
Real-time database integration with customizable AI responses
"""
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import pandas as pd
import numpy as np
from enum import Enum

# Import database models
from core.database import Customer, Campaign, Segment
from core.config import settings

# Import AI engines for data analysis
from analytics.predictive_engine import PredictiveAnalyticsEngine
from analytics.journey_engine import JourneyAnalyticsEngine
from analytics.financial_engine import FinancialAnalyticsEngine
from ai_engine.campaign_intelligence import CampaignIntelligenceEngine

logger = logging.getLogger(__name__)

class ChatStyle(str, Enum):
    FORMAL = "formal"
    CASUAL = "casual"
    TECHNICAL = "technical"
    EXECUTIVE = "executive"
    PITHY = "pithy"

class ResponseLength(str, Enum):
    BRIEF = "brief"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"

class AdminChatAssistant:
    """
    AI Chat Assistant for Admin Analytics and Campaign Insights
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.conversation_history = []
        self.user_preferences = {
            "style": ChatStyle.FORMAL,
            "length": ResponseLength.DETAILED,
            "include_percentages": True,
            "include_recommendations": True,
            "custom_prompt_prefix": "",
            "focus_areas": ["analytics", "campaigns", "customers"]
        }
        
        # Initialize AI engines
        try:
            self.predictive_engine = PredictiveAnalyticsEngine(db_session)
            self.journey_engine = JourneyAnalyticsEngine(db_session)
            self.financial_engine = FinancialAnalyticsEngine(db_session)
            self.campaign_intel = CampaignIntelligenceEngine()
            logger.info("✅ Chat assistant engines initialized")
        except Exception as e:
            logger.warning(f"⚠️ Some engines unavailable: {e}")
            self.predictive_engine = None
            self.journey_engine = None
            self.financial_engine = None
            self.campaign_intel = None
    
    def update_preferences(self, preferences: Dict[str, Any]) -> Dict[str, str]:
        """Update chat assistant preferences"""
        try:
            if "style" in preferences:
                self.user_preferences["style"] = ChatStyle(preferences["style"])
            if "length" in preferences:
                self.user_preferences["length"] = ResponseLength(preferences["length"])
            if "include_percentages" in preferences:
                self.user_preferences["include_percentages"] = preferences["include_percentages"]
            if "include_recommendations" in preferences:
                self.user_preferences["include_recommendations"] = preferences["include_recommendations"]
            if "custom_prompt_prefix" in preferences:
                self.user_preferences["custom_prompt_prefix"] = preferences["custom_prompt_prefix"]
            if "focus_areas" in preferences:
                self.user_preferences["focus_areas"] = preferences["focus_areas"]
            
            return {"status": "success", "message": "Preferences updated successfully"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to update preferences: {e}"}
    
    def get_database_insights(self, query_type: str, filters: Dict = None) -> Dict[str, Any]:
        """Get real-time insights from database"""
        try:
            insights = {}
            
            if query_type == "customer_overview":
                insights = self._get_customer_insights(filters)
            elif query_type == "campaign_performance":
                insights = self._get_campaign_insights(filters)
            elif query_type == "revenue_analysis":
                insights = self._get_revenue_insights(filters)
            elif query_type == "segment_analysis":
                insights = self._get_segment_insights(filters)
            elif query_type == "predictive_analysis":
                insights = self._get_predictive_insights(filters)
            
            return insights
        except Exception as e:
            logger.error(f"Database insights error: {e}")
            return {"error": str(e)}
    
    def _get_customer_insights(self, filters: Dict = None) -> Dict[str, Any]:
        """Get comprehensive customer analytics"""
        try:
            # Basic customer metrics
            total_customers = self.db.query(Customer).count()
            
            # Customer value distribution
            high_value_customers = self.db.query(Customer).filter(
                Customer.total_spent > 5000
            ).count()
            
            # Age demographics
            age_stats = self.db.query(
                func.min(Customer.age).label('min_age'),
                func.max(Customer.age).label('max_age'),
                func.avg(Customer.age).label('avg_age')
            ).first()
            
            # Gender distribution
            gender_dist = self.db.query(
                Customer.gender,
                func.count(Customer.id).label('count')
            ).group_by(Customer.gender).all()
            
            # Location analysis
            top_locations = self.db.query(
                Customer.location,
                func.count(Customer.id).label('count')
            ).group_by(Customer.location).order_by(func.count(Customer.id).desc()).limit(5).all()
            
            # Calculate success percentages
            high_value_percentage = (high_value_customers / total_customers * 100) if total_customers > 0 else 0
            
            return {
                "total_customers": total_customers,
                "high_value_customers": high_value_customers,
                "high_value_percentage": round(high_value_percentage, 2),
                "age_stats": {
                    "min": age_stats.min_age if age_stats else 0,
                    "max": age_stats.max_age if age_stats else 0,
                    "average": round(age_stats.avg_age, 1) if age_stats and age_stats.avg_age else 0
                },
                "gender_distribution": [{"gender": g.gender, "count": g.count} for g in gender_dist] if gender_dist else [],
                "top_locations": [{"location": l.location, "count": l.count} for l in top_locations] if top_locations else []
            }
        except Exception as e:
            logger.error(f"Customer insights error: {e}")
            return {"error": str(e)}
    
    def _get_campaign_insights(self, filters: Dict = None) -> Dict[str, Any]:
        """Get campaign performance analytics"""
        try:
            # Campaign status distribution
            campaign_stats = self.db.query(
                Campaign.status,
                func.count(Campaign.campaign_id).label('count')
            ).group_by(Campaign.status).all()
            
            total_campaigns = self.db.query(Campaign).count()
            active_campaigns = self.db.query(Campaign).filter(Campaign.status == 'active').count()
            
            # Budget analysis
            budget_stats = self.db.query(
                func.sum(Campaign.budget).label('total_budget'),
                func.avg(Campaign.budget).label('avg_budget'),
                func.max(Campaign.budget).label('max_budget')
            ).first()
            
            # Campaign type distribution
            type_dist = self.db.query(
                Campaign.campaign_type,
                func.count(Campaign.campaign_id).label('count')
            ).group_by(Campaign.campaign_type).all()
            
            # Success rate calculation (active campaigns as success metric)
            success_rate = (active_campaigns / total_campaigns * 100) if total_campaigns > 0 else 0
            
            return {
                "total_campaigns": total_campaigns,
                "active_campaigns": active_campaigns,
                "success_rate_percentage": round(success_rate, 2),
                "campaign_status_dist": [{"status": s.status, "count": s.count} for s in campaign_stats] if campaign_stats else [],
                "budget_analysis": {
                    "total_budget": float(budget_stats.total_budget) if budget_stats and budget_stats.total_budget else 0,
                    "average_budget": float(budget_stats.avg_budget) if budget_stats and budget_stats.avg_budget else 0,
                    "max_budget": float(budget_stats.max_budget) if budget_stats and budget_stats.max_budget else 0
                },
                "campaign_types": [{"type": t.campaign_type, "count": t.count} for t in type_dist] if type_dist else []
            }
        except Exception as e:
            logger.error(f"Campaign insights error: {e}")
            return {"error": str(e)}
    
    def _get_revenue_insights(self, filters: Dict = None) -> Dict[str, Any]:
        """Get revenue and financial analytics"""
        try:
            # Customer spending analysis
            revenue_stats = self.db.query(
                func.sum(Customer.total_spent).label('total_revenue'),
                func.avg(Customer.total_spent).label('avg_customer_value'),
                func.max(Customer.total_spent).label('highest_spender')
            ).first()
            
            # Purchase frequency analysis
            freq_stats = self.db.query(
                func.avg(Customer.purchase_frequency).label('avg_frequency'),
                func.max(Customer.purchase_frequency).label('max_frequency')
            ).first()
            
            # Top spenders
            top_spenders = self.db.query(Customer).order_by(Customer.total_spent.desc()).limit(5).all()
            
            # Revenue growth potential (customers with low frequency but high spend)
            growth_potential = self.db.query(Customer).filter(
                and_(Customer.total_spent > 1000, Customer.purchase_frequency < 3)
            ).count()
            
            total_customers = self.db.query(Customer).count()
            growth_percentage = (growth_potential / total_customers * 100) if total_customers > 0 else 0
            
            return {
                "total_revenue": float(revenue_stats.total_revenue) if revenue_stats and revenue_stats.total_revenue else 0,
                "average_customer_value": float(revenue_stats.avg_customer_value) if revenue_stats and revenue_stats.avg_customer_value else 0,
                "highest_single_spender": float(revenue_stats.highest_spender) if revenue_stats and revenue_stats.highest_spender else 0,
                "average_purchase_frequency": round(freq_stats.avg_frequency, 2) if freq_stats and freq_stats.avg_frequency else 0,
                "growth_potential_customers": growth_potential,
                "growth_potential_percentage": round(growth_percentage, 2),
                "top_spenders": [
                    {
                        "name": customer.name,
                        "total_spent": customer.total_spent,
                        "purchase_frequency": customer.purchase_frequency
                    } for customer in top_spenders
                ]
            }
        except Exception as e:
            logger.error(f"Revenue insights error: {e}")
            return {"error": str(e)}
    
    def _get_segment_insights(self, filters: Dict = None) -> Dict[str, Any]:
        """Get customer segmentation analytics"""
        try:
            # Segment distribution
            segment_stats = self.db.query(
                Customer.segment_id,
                func.count(Customer.id).label('count')
            ).group_by(Customer.segment_id).all()
            
            # Segment value analysis
            segment_value = self.db.query(
                Customer.segment_id,
                func.sum(Customer.total_spent).label('total_value'),
                func.avg(Customer.total_spent).label('avg_value')
            ).group_by(Customer.segment_id).all()
            
            total_customers = self.db.query(Customer).count()
            
            segments_data = []
            for stat in segment_stats:
                value_data = next((v for v in segment_value if v.segment_id == stat.segment_id), None)
                percentage = (stat.count / total_customers * 100) if total_customers > 0 else 0
                
                segments_data.append({
                    "segment_id": stat.segment_id,
                    "customer_count": stat.count,
                    "percentage": round(percentage, 2),
                    "total_value": float(value_data.total_value) if value_data and value_data.total_value else 0,
                    "average_value": float(value_data.avg_value) if value_data and value_data.avg_value else 0
                })
            
            return {
                "total_segments": len(segment_stats),
                "segment_details": segments_data
            }
        except Exception as e:
            logger.error(f"Segment insights error: {e}")
            return {"error": str(e)}
    
    def _get_predictive_insights(self, filters: Dict = None) -> Dict[str, Any]:
        """Get predictive analytics insights"""
        try:
            insights = {}
            
            if self.predictive_engine:
                # Get churn predictions
                try:
                    churn_predictions = self.predictive_engine.bulk_predict_customers(
                        prediction_type=self.predictive_engine.PredictionType.CHURN_PROBABILITY,
                        limit=100
                    )
                    high_churn_risk = len([p for p in churn_predictions if p.get('prediction', 0) > 0.7])
                    insights["churn_analysis"] = {
                        "high_risk_customers": high_churn_risk,
                        "high_risk_percentage": round((high_churn_risk / len(churn_predictions) * 100), 2) if churn_predictions else 0
                    }
                except:
                    insights["churn_analysis"] = {"error": "Churn model not available"}
                
                # Get CLV predictions
                try:
                    clv_predictions = self.predictive_engine.bulk_predict_customers(
                        prediction_type=self.predictive_engine.PredictionType.CUSTOMER_LIFETIME_VALUE,
                        limit=100
                    )
                    high_value_predicted = len([p for p in clv_predictions if p.get('prediction', 0) > 10000])
                    insights["clv_analysis"] = {
                        "high_value_potential": high_value_predicted,
                        "high_value_percentage": round((high_value_predicted / len(clv_predictions) * 100), 2) if clv_predictions else 0
                    }
                except:
                    insights["clv_analysis"] = {"error": "CLV model not available"}
            
            return insights
        except Exception as e:
            logger.error(f"Predictive insights error: {e}")
            return {"error": str(e)}
    
    def format_response_by_style(self, data: Dict[str, Any], query: str) -> str:
        """Format AI response based on user style preferences"""
        style = self.user_preferences["style"]
        length = self.user_preferences["length"]
        include_percentages = self.user_preferences["include_percentages"]
        include_recommendations = self.user_preferences["include_recommendations"]
        custom_prefix = self.user_preferences["custom_prompt_prefix"]
        
        # Start with custom prefix if provided
        response = f"{custom_prefix}\n\n" if custom_prefix else ""
        
        if style == ChatStyle.EXECUTIVE:
            response += self._format_executive_style(data, query, length, include_percentages)
        elif style == ChatStyle.TECHNICAL:
            response += self._format_technical_style(data, query, length, include_percentages)
        elif style == ChatStyle.CASUAL:
            response += self._format_casual_style(data, query, length, include_percentages)
        elif style == ChatStyle.PITHY:
            response += self._format_pithy_style(data, query, include_percentages)
        else:  # FORMAL
            response += self._format_formal_style(data, query, length, include_percentages)
        
        # Add recommendations if enabled
        if include_recommendations:
            response += "\n\n" + self._generate_recommendations(data, query)
        
        return response
    
    def _format_executive_style(self, data: Dict, query: str, length: ResponseLength, include_percentages: bool) -> str:
        """Executive summary style formatting"""
        if "customer_overview" in str(data):
            total = data.get("total_customers", 0)
            high_value = data.get("high_value_customers", 0)
            percentage = data.get("high_value_percentage", 0)
            
            response = f"**Customer Portfolio Summary**\n"
            response += f"• Total Customer Base: {total:,}\n"
            if include_percentages:
                response += f"• High-Value Customers: {high_value:,} ({percentage}%)\n"
            else:
                response += f"• High-Value Customers: {high_value:,}\n"
            
            if length != ResponseLength.BRIEF:
                age_stats = data.get("age_stats", {})
                response += f"• Average Customer Age: {age_stats.get('average', 0)} years\n"
                response += f"• Geographic Spread: {len(data.get('top_locations', []))} primary markets\n"
        
        elif "campaign_performance" in str(data):
            total = data.get("total_campaigns", 0)
            active = data.get("active_campaigns", 0)
            success_rate = data.get("success_rate_percentage", 0)
            
            response = f"**Campaign Performance Overview**\n"
            response += f"• Total Campaigns: {total}\n"
            response += f"• Active Campaigns: {active}\n"
            if include_percentages:
                response += f"• Success Rate: {success_rate}%\n"
        
        return response
    
    def _format_technical_style(self, data: Dict, query: str, length: ResponseLength, include_percentages: bool) -> str:
        """Technical analysis style formatting"""
        response = f"**Technical Analysis Results**\n\n"
        
        for key, value in data.items():
            if isinstance(value, dict):
                response += f"**{key.replace('_', ' ').title()}:**\n"
                for sub_key, sub_value in value.items():
                    response += f"  - {sub_key}: {sub_value}\n"
            elif isinstance(value, list):
                response += f"**{key.replace('_', ' ').title()}:** {len(value)} items\n"
            else:
                response += f"**{key.replace('_', ' ').title()}:** {value}\n"
        
        return response
    
    def _format_casual_style(self, data: Dict, query: str, length: ResponseLength, include_percentages: bool) -> str:
        """Casual conversational style formatting"""
        if "total_customers" in data:
            total = data.get("total_customers", 0)
            response = f"Hey! So looking at your customer data, you've got {total:,} customers in total. "
            
            if include_percentages and "high_value_percentage" in data:
                percentage = data.get("high_value_percentage", 0)
                response += f"About {percentage}% of them are high-value customers, which is pretty solid! "
        
        elif "total_campaigns" in data:
            total = data.get("total_campaigns", 0)
            active = data.get("active_campaigns", 0)
            response = f"Looking at your campaigns, you're running {active} active ones out of {total} total. "
            
            if include_percentages:
                success_rate = data.get("success_rate_percentage", 0)
                response += f"That's a {success_rate}% success rate - not bad at all! "
        
        return response
    
    def _format_pithy_style(self, data: Dict, query: str, include_percentages: bool) -> str:
        """Brief, to-the-point style formatting"""
        if "total_customers" in data:
            total = data.get("total_customers", 0)
            high_value = data.get("high_value_customers", 0)
            if include_percentages:
                percentage = data.get("high_value_percentage", 0)
                return f"{total:,} customers. {percentage}% high-value."
            else:
                return f"{total:,} customers. {high_value:,} high-value."
        
        elif "total_campaigns" in data:
            active = data.get("active_campaigns", 0)
            success_rate = data.get("success_rate_percentage", 0)
            if include_percentages:
                return f"{active} active campaigns. {success_rate}% success rate."
            else:
                return f"{active} active campaigns."
        
        return "Data processed."
    
    def _format_formal_style(self, data: Dict, query: str, length: ResponseLength, include_percentages: bool) -> str:
        """Formal business style formatting"""
        response = "Based on the current database analysis, here are the key findings:\n\n"
        
        if "total_customers" in data:
            total = data.get("total_customers", 0)
            high_value = data.get("high_value_customers", 0)
            
            response += f"Customer Analysis:\n"
            response += f"- Total customer base: {total:,}\n"
            response += f"- High-value customers: {high_value:,}\n"
            
            if include_percentages:
                percentage = data.get("high_value_percentage", 0)
                response += f"- High-value customer ratio: {percentage}%\n"
            
            if length != ResponseLength.BRIEF:
                age_stats = data.get("age_stats", {})
                if age_stats.get("average"):
                    response += f"- Average customer age: {age_stats.get('average')} years\n"
        
        elif "total_campaigns" in data:
            total = data.get("total_campaigns", 0)
            active = data.get("active_campaigns", 0)
            budget = data.get("budget_analysis", {})
            
            response += f"Campaign Performance Analysis:\n"
            response += f"- Total campaigns: {total}\n"
            response += f"- Currently active: {active}\n"
            
            if include_percentages:
                success_rate = data.get("success_rate_percentage", 0)
                response += f"- Success rate: {success_rate}%\n"
            
            if budget.get("total_budget"):
                response += f"- Total budget allocation: ${budget.get('total_budget'):,.2f}\n"
        
        return response
    
    def _generate_recommendations(self, data: Dict, query: str) -> str:
        """Generate actionable recommendations based on data"""
        recommendations = ["**Recommendations:**"]
        
        if "high_value_percentage" in data:
            percentage = data.get("high_value_percentage", 0)
            if percentage < 20:
                recommendations.append("• Consider implementing loyalty programs to increase high-value customer ratio")
                recommendations.append("• Analyze purchasing patterns of existing high-value customers for targeting")
            elif percentage > 40:
                recommendations.append("• Excellent high-value customer ratio - focus on retention strategies")
        
        if "success_rate_percentage" in data:
            success_rate = data.get("success_rate_percentage", 0)
            if success_rate < 50:
                recommendations.append("• Review campaign targeting and messaging strategies")
                recommendations.append("• Consider A/B testing different campaign approaches")
            elif success_rate > 80:
                recommendations.append("• Strong campaign performance - consider scaling successful campaigns")
        
        if "growth_potential_percentage" in data:
            growth_potential = data.get("growth_potential_percentage", 0)
            if growth_potential > 15:
                recommendations.append("• Significant growth potential identified - implement re-engagement campaigns")
        
        return "\n".join(recommendations) if len(recommendations) > 1 else ""
    
    def chat(self, message: str, context: Dict = None) -> Dict[str, Any]:
        """Main chat interface for admin queries"""
        try:
            # Analyze the message to determine intent
            intent = self._analyze_message_intent(message)
            
            # Get relevant data from database
            data = self.get_database_insights(intent["query_type"], intent.get("filters"))
            
            # Format response based on user preferences
            ai_response = self.format_response_by_style(data, message)
            
            # Store conversation
            conversation_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_message": message,
                "ai_response": ai_response,
                "intent": intent,
                "data_used": list(data.keys()) if isinstance(data, dict) else []
            }
            
            self.conversation_history.append(conversation_entry)
            
            # Keep only last 50 conversations
            if len(self.conversation_history) > 50:
                self.conversation_history = self.conversation_history[-50:]
            
            return {
                "response": ai_response,
                "data_insights": data,
                "conversation_id": len(self.conversation_history),
                "timestamp": conversation_entry["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {
                "response": f"I apologize, but I encountered an error processing your request: {str(e)}",
                "error": True,
                "timestamp": datetime.now().isoformat()
            }
    
    def _analyze_message_intent(self, message: str) -> Dict[str, Any]:
        """Analyze user message to determine what data to fetch"""
        message_lower = message.lower()
        
        # Customer-related queries
        if any(word in message_lower for word in ["customer", "user", "client", "buyer", "demographic"]):
            return {"query_type": "customer_overview", "confidence": 0.9}
        
        # Campaign-related queries
        elif any(word in message_lower for word in ["campaign", "marketing", "promotion", "ads", "advertising"]):
            return {"query_type": "campaign_performance", "confidence": 0.9}
        
        # Revenue/financial queries
        elif any(word in message_lower for word in ["revenue", "sales", "money", "profit", "financial", "income"]):
            return {"query_type": "revenue_analysis", "confidence": 0.9}
        
        # Segmentation queries
        elif any(word in message_lower for word in ["segment", "group", "category", "cluster"]):
            return {"query_type": "segment_analysis", "confidence": 0.8}
        
        # Predictive analytics queries
        elif any(word in message_lower for word in ["predict", "forecast", "future", "churn", "clv", "lifetime"]):
            return {"query_type": "predictive_analysis", "confidence": 0.8}
        
        # Default to customer overview
        else:
            return {"query_type": "customer_overview", "confidence": 0.5}
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict]:
        """Get recent chat history"""
        return self.conversation_history[-limit:] if self.conversation_history else []
    
    def clear_conversation_history(self) -> Dict[str, str]:
        """Clear chat history"""
        self.conversation_history = []
        return {"status": "success", "message": "Conversation history cleared"}
    
    def get_available_queries(self) -> List[Dict[str, str]]:
        """Get list of available query types with examples"""
        return [
            {
                "type": "customer_overview",
                "description": "Customer demographics and behavior analysis",
                "examples": ["Tell me about our customers", "What's our customer demographics?", "Customer analysis"]
            },
            {
                "type": "campaign_performance", 
                "description": "Campaign effectiveness and ROI analysis",
                "examples": ["How are our campaigns performing?", "Campaign success rates", "Marketing ROI"]
            },
            {
                "type": "revenue_analysis",
                "description": "Financial performance and revenue insights",
                "examples": ["Show me revenue data", "Financial performance", "Top spending customers"]
            },
            {
                "type": "segment_analysis",
                "description": "Customer segmentation and group analysis", 
                "examples": ["Customer segments breakdown", "Segment performance", "Group analysis"]
            },
            {
                "type": "predictive_analysis",
                "description": "Predictive analytics and forecasting",
                "examples": ["Predict customer churn", "Future value forecasts", "CLV predictions"]
            }
        ]