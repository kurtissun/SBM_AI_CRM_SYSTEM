import openai
from typing import Dict, List, Any
import json
import logging
from datetime import datetime, timedelta
import pandas as pd
from core.database import get_db, Customer, Campaign
from core.config import settings

logger = logging.getLogger(__name__)

class ConversationalCRMAssistant:
    def __init__(self):
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.openai_available = True
        else:
            self.openai_available = False
            logger.warning("OpenAI API key not found - using fallback responses")
        
        self.conversation_history = []
        self.context_memory = {}
    
    def chat(self, query: str, user_context: Dict = None) -> Dict[str, Any]:
        """Main chat interface for CRM assistant"""
        try:
            # Parse user intent
            intent = self._parse_intent(query)
            
            # Get relevant data based on intent
            relevant_data = self._get_relevant_data(intent, query)
            
            # Generate response
            if self.openai_available:
                response = self._generate_ai_response(query, intent, relevant_data, user_context)
            else:
                response = self._generate_fallback_response(intent, relevant_data)
            
            # Store conversation
            self._store_conversation(query, response, user_context)
            
            return {
                "response": response,
                "intent": intent,
                "data_used": relevant_data.get("summary", ""),
                "suggested_actions": self._get_suggested_actions(intent),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {
                "response": "I apologize, but I encountered an error processing your request. Please try again.",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _parse_intent(self, query: str) -> Dict[str, Any]:
        """Parse user intent from query"""
        query_lower = query.lower()
        
        # Customer-related intents
        if any(word in query_lower for word in ['customer', 'segment', 'profile', 'churn']):
            if 'churn' in query_lower:
                return {"type": "customer_analysis", "subtype": "churn_analysis"}
            elif 'segment' in query_lower:
                return {"type": "customer_analysis", "subtype": "segmentation"}
            else:
                return {"type": "customer_analysis", "subtype": "general"}
        
        # Campaign-related intents
        elif any(word in query_lower for word in ['campaign', 'marketing', 'promotion', 'roi']):
            if 'create' in query_lower or 'new' in query_lower:
                return {"type": "campaign_management", "subtype": "create"}
            elif 'performance' in query_lower or 'roi' in query_lower:
                return {"type": "campaign_management", "subtype": "performance"}
            else:
                return {"type": "campaign_management", "subtype": "general"}
        
        # Analytics intents
        elif any(word in query_lower for word in ['analytics', 'report', 'insights', 'data']):
            return {"type": "analytics", "subtype": "insights"}
        
        # Traffic/visitor intents
        elif any(word in query_lower for word in ['traffic', 'visitor', 'crowd', 'footfall']):
            return {"type": "traffic_analysis", "subtype": "current"}
        
        else:
            return {"type": "general", "subtype": "help"}
    
    def _get_relevant_data(self, intent: Dict, query: str) -> Dict[str, Any]:
        """Retrieve relevant data based on intent"""
        db = get_db()
        data = {"summary": ""}
        
        try:
            if intent["type"] == "customer_analysis":
                # Get customer statistics
                total_customers = db.query(Customer).count()
                
                if intent["subtype"] == "churn_analysis":
                    # Simulate churn analysis
                    high_risk_customers = total_customers * 0.15  # 15% at risk
                    data = {
                        "total_customers": total_customers,
                        "high_risk_churn": int(high_risk_customers),
                        "churn_rate": "15%",
                        "top_risk_factors": ["Low engagement", "Decreased visit frequency", "Rating decline"],
                        "summary": f"Found {int(high_risk_customers)} customers at high churn risk"
                    }
                
                elif intent["subtype"] == "segmentation":
                    # Get segment distribution (simulated)
                    segments = [
                        {"name": "Tech Professionals", "size": int(total_customers * 0.23), "percentage": 23},
                        {"name": "Family Shoppers", "size": int(total_customers * 0.19), "percentage": 19},
                        {"name": "Premium Customers", "size": int(total_customers * 0.18), "percentage": 18},
                        {"name": "Tourists", "size": int(total_customers * 0.15), "percentage": 15},
                        {"name": "Budget Conscious", "size": int(total_customers * 0.25), "percentage": 25}
                    ]
                    data = {
                        "total_customers": total_customers,
                        "segments": segments,
                        "largest_segment": max(segments, key=lambda x: x["size"]),
                        "summary": f"Customer base divided into {len(segments)} segments"
                    }
            
            elif intent["type"] == "campaign_management":
                # Get campaign data
                total_campaigns = db.query(Campaign).count()
                active_campaigns = db.query(Campaign).filter(Campaign.status == "active").count()
                
                if intent["subtype"] == "performance":
                    # Simulated performance data
                    data = {
                        "total_campaigns": total_campaigns,
                        "active_campaigns": active_campaigns,
                        "avg_roi": 2.34,
                        "best_performing": "Spring Festival Promotion",
                        "total_budget": 500000,
                        "summary": f"{active_campaigns} active campaigns with 2.34x average ROI"
                    }
                
                else:
                    data = {
                        "total_campaigns": total_campaigns,
                        "active_campaigns": active_campaigns,
                        "summary": f"{total_campaigns} total campaigns, {active_campaigns} currently active"
                    }
            
            elif intent["type"] == "traffic_analysis":
                # Simulated traffic data
                current_visitors = 234
                data = {
                    "current_visitors": current_visitors,
                    "peak_hour": "2:00 PM",
                    "busiest_zone": "Main Hall",
                    "crowd_level": "Medium",
                    "summary": f"{current_visitors} visitors currently in mall"
                }
            
        except Exception as e:
            logger.error(f"Data retrieval error: {e}")
            data = {"summary": "Unable to retrieve data", "error": str(e)}
        
        finally:
            db.close()
        
        return data
    
    def _generate_ai_response(self, query: str, intent: Dict, data: Dict, user_context: Dict) -> str:
        """Generate AI response using OpenAI"""
        try:
            # Build context prompt
            context_prompt = f"""
You are an AI assistant for Super Brand Mall's CRM system. You help marketing teams analyze customers, optimize campaigns, and make data-driven decisions.

Current data context: {json.dumps(data, indent=2)}

User query: "{query}"
Intent: {intent["type"]} - {intent["subtype"]}

Provide a helpful, actionable response that:
1. Directly answers the user's question
2. Highlights key insights from the data
3. Suggests specific actions they can take
4. Uses a professional but friendly tone

Keep responses concise but informative (2-4 sentences).
"""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful CRM assistant for Super Brand Mall."},
                    {"role": "user", "content": context_prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._generate_fallback_response(intent, data)
    
    def _generate_fallback_response(self, intent: Dict, data: Dict) -> str:
        """Generate fallback response when OpenAI is unavailable"""
        
        if intent["type"] == "customer_analysis":
            if intent["subtype"] == "churn_analysis":
                return f"I found {data.get('high_risk_churn', 0)} customers at high churn risk ({data.get('churn_rate', 'N/A')}). Consider launching retention campaigns focusing on engagement and personalized offers."
            
            elif intent["subtype"] == "segmentation":
                largest = data.get("largest_segment", {})
                return f"Your customer base has {len(data.get('segments', []))} segments. The largest is '{largest.get('name', 'Unknown')}' with {largest.get('size', 0)} customers ({largest.get('percentage', 0)}%). Consider targeted campaigns for each segment."
        
        elif intent["type"] == "campaign_management":
            if intent["subtype"] == "performance":
                return f"You have {data.get('active_campaigns', 0)} active campaigns with an average ROI of {data.get('avg_roi', 0)}x. Your best performer is '{data.get('best_performing', 'N/A')}'. Consider scaling successful campaigns."
            
            elif intent["subtype"] == "create":
                return "I can help you create a new campaign! Consider your target segment, budget, and objectives. Would you like me to suggest optimal segments based on your current customer data?"
        
        elif intent["type"] == "traffic_analysis":
            return f"Current mall traffic: {data.get('current_visitors', 0)} visitors. Peak hour is {data.get('peak_hour', 'N/A')} with highest activity in {data.get('busiest_zone', 'N/A')}. Consider adjusting staffing and promotions accordingly."
        
        else:
            return "I'm here to help with customer analysis, campaign management, and traffic insights. What would you like to know about your CRM data?"
    
    def _get_suggested_actions(self, intent: Dict) -> List[str]:
        """Get suggested follow-up actions"""
        
        if intent["type"] == "customer_analysis":
            return [
                "Create targeted retention campaign",
                "Analyze segment preferences",
                "Export customer list for outreach"
            ]
        
        elif intent["type"] == "campaign_management":
            return [
                "Create new campaign",
                "Analyze campaign performance",
                "Optimize budget allocation"
            ]
        
        elif intent["type"] == "traffic_analysis":
            return [
                "View real-time heatmap",
                "Set up traffic alerts",
                "Analyze visitor patterns"
            ]
        
        else:
            return [
                "Analyze customer segments",
                "Review campaign performance",
                "Check traffic analytics"
            ]
    
    def _store_conversation(self, query: str, response: str, user_context: Dict):
        """Store conversation for context memory"""
        conversation_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response,
            "user_context": user_context or {}
        }
        
        self.conversation_history.append(conversation_entry)
        
        # Keep only last 10 conversations
        if len(self.conversation_history) > 10:
            self.conversation_history.pop(0)
    
    def get_conversation_history(self) -> List[Dict]:
        """Get recent conversation history"""
        return self.conversation_history[-5:]  # Last 5 conversations
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.context_memory = {}

# Global instance
crm_assistant = ConversationalCRMAssistant()
