"""
API endpoints for hyper-personalization features
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
import logging
from datetime import datetime
from ...core.security import get_current_user
from ...ai_engine.hyper_personalization import hyper_personalization_engine
from ...core.database import get_db, Customer

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/customers/{customer_id}/profile")
async def create_personalized_profile(
    customer_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create comprehensive personalized profile for customer"""
    
    # Get customer data from database
    customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Convert to dict for processing
    customer_data = {
        'customer_id': customer.customer_id,
        'age': customer.age,
        'sex': customer.gender,
        'rating_id': customer.rating_id,
        'avg_spending': getattr(customer, 'avg_spending', 1200),  # Would come from transaction data
        'visit_frequency': getattr(customer, 'visit_frequency', 2.5)  # Would be calculated
    }
    
    # Generate personalized profile
    profile = hyper_personalization_engine.create_individual_profile(customer_id, customer_data)
    
    return {
        "status": "success",
        "customer_id": customer_id,
        "profile": profile,
        "personalization_ready": True
    }

@router.get("/customers/{customer_id}/personalized-offers")
async def get_personalized_offers(
    customer_id: str,
    limit: int = 5,
    current_user: dict = Depends(get_current_user)
):
    """Get highly personalized offers for specific customer"""
    
    offers = hyper_personalization_engine.generate_personalized_offers(customer_id)
    
    if not offers:
        # Create profile first if it doesn't exist
        await create_personalized_profile(customer_id, current_user)
        offers = hyper_personalization_engine.generate_personalized_offers(customer_id)
    
    return {
        "customer_id": customer_id,
        "personalized_offers": offers[:limit],
        "total_offers": len(offers),
        "personalization_level": "hyper_personalized",
        "generated_at": datetime.now().isoformat()
    }

@router.get("/customers/{customer_id}/communication-timing")
async def get_optimal_communication_timing(
    customer_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get optimal communication timing for specific customer"""
    
    timing = hyper_personalization_engine.personalized_communication_timing(customer_id)
    
    return {
        "customer_id": customer_id,
        "optimal_timing": timing,
        "confidence_score": 0.85,
        "recommendations": [
            f"Best contact day: {timing['optimal_day']}",
            f"Optimal time: {timing['optimal_time']}",
            f"Preferred frequency: {timing['communication_frequency']}"
        ]
    }

@router.get("/customers/{customer_id}/personalized-journey")
async def get_personalized_journey(
    customer_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get complete personalized customer journey"""
    
    journey = hyper_personalization_engine.generate_individual_journey(customer_id)
    
    return {
        "customer_id": customer_id,
        "personalized_journey": journey,
        "journey_stage": journey["current_stage"],
        "next_actions": journey["next_best_actions"],
        "customizations": journey["experience_customizations"]
    }

@router.post("/segments/{segment_id}/bulk-personalization")
async def create_bulk_personalized_offers(
    segment_id: int,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create personalized offers for all customers in a segment"""
    
    # Get all customers in segment
    customers = db.query(Customer).filter(Customer.segment_id == segment_id).all()
    
    personalized_results = []
    
    for customer in customers:
        try:
            # Create profile if needed
            profile = hyper_personalization_engine.create_individual_profile(
                customer.customer_id, 
                {
                    'age': customer.age,
                    'sex': customer.gender,
                    'rating_id': customer.rating_id,
                    'avg_spending': 1200,  # Would be calculated from transactions
                    'visit_frequency': 2.5
                }
            )
            
            # Generate personalized offers
            offers = hyper_personalization_engine.generate_personalized_offers(customer.customer_id)
            
            personalized_results.append({
                "customer_id": customer.customer_id,
                "offers_count": len(offers),
                "top_offer": offers[0] if offers else None,
                "personalization_score": offers[0]["final_effectiveness_score"] if offers else 0
            })
            
        except Exception as e:
            logger.error(f"Failed to personalize for customer {customer.customer_id}: {e}")
    
    return {
        "segment_id": segment_id,
        "customers_processed": len(personalized_results),
        "avg_personalization_score": sum(r["personalization_score"] for r in personalized_results) / len(personalized_results),
        "results": personalized_results
    }
