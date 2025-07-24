from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime

from ...ai_engine.conversational_ai import crm_assistant
from ...core.security import get_current_user

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    user_context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    intent: Dict[str, Any]
    data_used: str
    suggested_actions: List[str]
    timestamp: str
    conversation_id: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_with_assistant(
    request: ChatRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Chat with the CRM AI assistant
    """
    try:
        # Add user info to context
        enhanced_context = request.user_context or {}
        enhanced_context.update({
            "user_id": current_user.get("user_id"),
            "username": current_user.get("username"),
            "timestamp": datetime.now().isoformat()
        })
        
        # Get AI response
        result = crm_assistant.chat(request.query, enhanced_context)
        
        return ChatResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@router.get("/chat/history")
async def get_chat_history(current_user: Dict = Depends(get_current_user)):
    """
    Get recent conversation history
    """
    try:
        history = crm_assistant.get_conversation_history()
        return {"history": history, "count": len(history)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")

@router.delete("/chat/history")
async def clear_chat_history(current_user: Dict = Depends(get_current_user)):
    """
    Clear conversation history
    """
    try:
        crm_assistant.clear_conversation()
        return {"message": "Conversation history cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear history: {str(e)}")

@router.post("/chat/quick-commands")
async def quick_commands(current_user: Dict = Depends(get_current_user)):
    """
    Get quick command suggestions
    """
    commands = [
        {
            "command": "Show me customers at risk of churning",
            "category": "Customer Analysis",
            "description": "Identifies customers with high churn probability"
        },
        {
            "command": "What's the performance of my active campaigns?",
            "category": "Campaign Management", 
            "description": "Shows ROI and metrics for current campaigns"
        },
        {
            "command": "How many visitors are in the mall right now?",
            "category": "Traffic Analytics",
            "description": "Real-time visitor count and zone distribution"
        },
        {
            "command": "Create a campaign for young professionals",
            "category": "Campaign Creation",
            "description": "AI-assisted campaign creation with recommendations"
        },
        {
            "command": "Show me my best customer segments",
            "category": "Customer Analysis",
            "description": "Displays top-performing customer segments"
        }
    ]
    
    return {"quick_commands": commands}