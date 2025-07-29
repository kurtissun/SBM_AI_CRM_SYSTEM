"""
Admin AI Chat API Endpoints
Real-time analytics and campaign insights with customizable AI responses
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from core.database import get_db
from core.security import get_current_user
from ai_engine.admin_chat_assistant import AdminChatAssistant, ChatStyle, ResponseLength

router = APIRouter(prefix="/api/admin/chat", tags=["Admin Chat"])

# Pydantic models for request/response
class ChatMessage(BaseModel):
    message: str = Field(..., description="User message to the AI assistant")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the query")

class ChatPreferences(BaseModel):
    style: Optional[ChatStyle] = Field(ChatStyle.FORMAL, description="Response style")
    length: Optional[ResponseLength] = Field(ResponseLength.DETAILED, description="Response length")
    include_percentages: Optional[bool] = Field(True, description="Include percentage calculations")
    include_recommendations: Optional[bool] = Field(True, description="Include actionable recommendations")
    custom_prompt_prefix: Optional[str] = Field("", description="Custom prompt prefix")
    focus_areas: Optional[List[str]] = Field(["analytics", "campaigns", "customers"], description="Areas of focus")

class ChatResponse(BaseModel):
    response: str
    data_insights: Dict[str, Any]
    conversation_id: int
    timestamp: str
    error: Optional[bool] = False

class DatabaseQuery(BaseModel):
    query_type: str = Field(..., description="Type of database query to execute")
    filters: Optional[Dict[str, Any]] = Field(None, description="Query filters")

# Global chat assistant instance (will be initialized per request)
def get_chat_assistant(db: Session = Depends(get_db)) -> AdminChatAssistant:
    """Get or create chat assistant instance"""
    return AdminChatAssistant(db)

@router.post("/message", response_model=ChatResponse)
async def send_chat_message(
    message: ChatMessage,
    chat_assistant: AdminChatAssistant = Depends(get_chat_assistant),
    current_user: dict = Depends(get_current_user)
):
    """
    Send a message to the AI chat assistant and get insights
    """
    try:
        # Process the chat message
        result = chat_assistant.chat(message.message, message.context)
        
        return ChatResponse(
            response=result["response"],
            data_insights=result["data_insights"],
            conversation_id=result["conversation_id"],
            timestamp=result["timestamp"],
            error=result.get("error", False)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@router.post("/preferences")
async def update_chat_preferences(
    preferences: ChatPreferences,
    chat_assistant: AdminChatAssistant = Depends(get_chat_assistant),
    current_user: dict = Depends(get_current_user)
):
    """
    Update AI chat assistant preferences and settings
    """
    try:
        # Convert Pydantic model to dict
        prefs_dict = preferences.dict(exclude_unset=True)
        
        # Update preferences
        result = chat_assistant.update_preferences(prefs_dict)
        
        return {
            "status": result["status"],
            "message": result["message"],
            "updated_preferences": prefs_dict,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update preferences: {str(e)}")

@router.get("/preferences")
async def get_chat_preferences(
    chat_assistant: AdminChatAssistant = Depends(get_chat_assistant),
    current_user: dict = Depends(get_current_user)
):
    """
    Get current AI chat assistant preferences
    """
    try:
        return {
            "preferences": chat_assistant.user_preferences,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get preferences: {str(e)}")

@router.post("/query-database")
async def query_database_directly(
    query: DatabaseQuery,
    chat_assistant: AdminChatAssistant = Depends(get_chat_assistant),
    current_user: dict = Depends(get_current_user)
):
    """
    Query database directly for specific insights
    """
    try:
        # Get database insights
        insights = chat_assistant.get_database_insights(query.query_type, query.filters)
        
        return {
            "query_type": query.query_type,
            "insights": insights,
            "timestamp": datetime.now().isoformat(),
            "filters_applied": query.filters or {}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

@router.get("/history")
async def get_chat_history(
    limit: int = 10,
    chat_assistant: AdminChatAssistant = Depends(get_chat_assistant),
    current_user: dict = Depends(get_current_user)
):
    """
    Get recent chat conversation history
    """
    try:
        history = chat_assistant.get_conversation_history(limit)
        
        return {
            "conversation_history": history,
            "total_conversations": len(chat_assistant.conversation_history),
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chat history: {str(e)}")

@router.delete("/history")
async def clear_chat_history(
    chat_assistant: AdminChatAssistant = Depends(get_chat_assistant),
    current_user: dict = Depends(get_current_user)
):
    """
    Clear chat conversation history
    """
    try:
        result = chat_assistant.clear_conversation_history()
        
        return {
            "status": result["status"],
            "message": result["message"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear history: {str(e)}")

@router.get("/available-queries")
async def get_available_queries(
    chat_assistant: AdminChatAssistant = Depends(get_chat_assistant),
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of available query types and examples
    """
    try:
        queries = chat_assistant.get_available_queries()
        
        return {
            "available_queries": queries,
            "total_query_types": len(queries),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available queries: {str(e)}")

@router.get("/styles-and-options")
async def get_style_options():
    """
    Get available chat styles and response options
    """
    return {
        "chat_styles": {
            "formal": "Professional business communication",
            "casual": "Conversational and friendly tone",
            "technical": "Technical analysis with detailed metrics",
            "executive": "Executive summary format",
            "pithy": "Brief and to-the-point responses"
        },
        "response_lengths": {
            "brief": "Short, concise responses",
            "detailed": "Comprehensive analysis",
            "comprehensive": "In-depth insights with context"
        },
        "customization_options": {
            "include_percentages": "Show percentage calculations and ratios",
            "include_recommendations": "Provide actionable recommendations",
            "custom_prompt_prefix": "Add custom prefix to all responses",
            "focus_areas": "Specify areas of interest for analysis"
        }
    }

@router.post("/quick-insights")
async def get_quick_insights(
    insight_type: str,
    chat_assistant: AdminChatAssistant = Depends(get_chat_assistant),
    current_user: dict = Depends(get_current_user)
):
    """
    Get quick insights without full chat processing
    """
    try:
        # Map insight types to queries
        insight_mapping = {
            "dashboard": "customer_overview",
            "campaigns": "campaign_performance", 
            "revenue": "revenue_analysis",
            "segments": "segment_analysis",
            "predictions": "predictive_analysis"
        }
        
        query_type = insight_mapping.get(insight_type, "customer_overview")
        insights = chat_assistant.get_database_insights(query_type)
        
        # Format as quick summary
        if query_type == "customer_overview":
            summary = f"Total Customers: {insights.get('total_customers', 0):,} | High-Value: {insights.get('high_value_percentage', 0)}%"
        elif query_type == "campaign_performance":
            summary = f"Campaigns: {insights.get('active_campaigns', 0)} active | Success Rate: {insights.get('success_rate_percentage', 0)}%"
        elif query_type == "revenue_analysis":
            summary = f"Total Revenue: ${insights.get('total_revenue', 0):,.2f} | Avg Customer Value: ${insights.get('average_customer_value', 0):,.2f}"
        else:
            summary = "Insights processed successfully"
        
        return {
            "insight_type": insight_type,
            "quick_summary": summary,
            "detailed_insights": insights,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get quick insights: {str(e)}")

@router.post("/analytics-deep-dive")
async def analytics_deep_dive(
    analysis_type: str,
    time_period_days: int = 30,
    chat_assistant: AdminChatAssistant = Depends(get_chat_assistant),
    current_user: dict = Depends(get_current_user)
):
    """
    Perform deep analytics dive with comprehensive insights
    """
    try:
        # Get comprehensive data
        filters = {"time_period_days": time_period_days}
        
        if analysis_type == "customer_analysis":
            insights = chat_assistant.get_database_insights("customer_overview", filters)
            revenue_insights = chat_assistant.get_database_insights("revenue_analysis", filters)
            segment_insights = chat_assistant.get_database_insights("segment_analysis", filters)
            
            # Combine insights
            combined_insights = {
                "customer_data": insights,
                "revenue_data": revenue_insights,
                "segment_data": segment_insights
            }
            
        elif analysis_type == "campaign_analysis":
            campaign_insights = chat_assistant.get_database_insights("campaign_performance", filters)
            predictive_insights = chat_assistant.get_database_insights("predictive_analysis", filters)
            
            combined_insights = {
                "campaign_data": campaign_insights,
                "predictive_data": predictive_insights
            }
            
        else:
            # Default comprehensive analysis
            combined_insights = {
                "customer_data": chat_assistant.get_database_insights("customer_overview", filters),
                "campaign_data": chat_assistant.get_database_insights("campaign_performance", filters),
                "revenue_data": chat_assistant.get_database_insights("revenue_analysis", filters)
            }
        
        # Generate AI-formatted response
        ai_response = chat_assistant.format_response_by_style(
            combined_insights, 
            f"Comprehensive {analysis_type} analysis"
        )
        
        return {
            "analysis_type": analysis_type,
            "time_period_days": time_period_days,
            "comprehensive_insights": combined_insights,
            "ai_formatted_response": ai_response,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deep dive analysis failed: {str(e)}")