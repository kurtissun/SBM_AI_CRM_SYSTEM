"""
SBM Business Goals and Focus Configuration
"""
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class SBMGoal(BaseModel):
    """Individual business goal"""
    goal_id: str
    name: str
    description: str
    priority: str  # high, medium, low
    category: str  # revenue, customer_satisfaction, market_expansion, operational_efficiency
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    timeline: Optional[str] = None
    kpis: List[str] = []
    
class SBMFocus(BaseModel):
    """Business focus area"""
    focus_id: str
    name: str
    description: str
    related_goals: List[str] = []
    target_segments: List[int] = []
    key_initiatives: List[str] = []
    
class SBMConfiguration(BaseModel):
    """Overall SBM configuration"""
    business_name: str = "Super Brand Mall"
    vision: str = "To be the premier shopping and lifestyle destination"
    mission: str = "Delivering exceptional experiences through innovation and customer focus"
    core_values: List[str] = ["Customer First", "Innovation", "Excellence", "Sustainability"]
    goals: List[SBMGoal] = []
    focus_areas: List[SBMFocus] = []
    ai_preferences: Dict[str, Any] = {}
    updated_at: datetime = datetime.now()

class SBMConfigManager:
    """Manages SBM business configuration"""
    
    def __init__(self, config_file: str = "sbm_config.json"):
        self.config_file = config_file
        self.config = self._load_default_config()
        
    def _load_default_config(self) -> SBMConfiguration:
        """Load default SBM configuration"""
        default_goals = [
            SBMGoal(
                goal_id="revenue_growth",
                name="Revenue Growth",
                description="Increase annual revenue by 20%",
                priority="high",
                category="revenue",
                target_value=20.0,
                current_value=12.5,
                timeline="12 months",
                kpis=["monthly_revenue", "average_transaction_value", "conversion_rate"]
            ),
            SBMGoal(
                goal_id="customer_satisfaction",
                name="Customer Satisfaction Excellence",
                description="Achieve 90% customer satisfaction rating",
                priority="high",
                category="customer_satisfaction",
                target_value=90.0,
                current_value=85.0,
                timeline="6 months",
                kpis=["nps_score", "customer_ratings", "complaint_resolution_time"]
            ),
            SBMGoal(
                goal_id="market_expansion",
                name="Market Share Growth",
                description="Expand market share in premium segment",
                priority="medium",
                category="market_expansion",
                target_value=15.0,
                current_value=10.0,
                timeline="18 months",
                kpis=["new_customer_acquisition", "premium_segment_size", "brand_awareness"]
            ),
            SBMGoal(
                goal_id="digital_transformation",
                name="Digital Experience Enhancement",
                description="Modernize customer digital touchpoints",
                priority="high",
                category="operational_efficiency",
                target_value=100.0,
                current_value=60.0,
                timeline="9 months",
                kpis=["app_adoption_rate", "digital_engagement", "omnichannel_integration"]
            )
        ]
        
        default_focus_areas = [
            SBMFocus(
                focus_id="premium_customers",
                name="Premium Customer Experience",
                description="Enhance services for high-value customers",
                related_goals=["revenue_growth", "customer_satisfaction"],
                target_segments=[4],  # Mature Premium Shoppers
                key_initiatives=["VIP lounges", "Personal shopping", "Exclusive events"]
            ),
            SBMFocus(
                focus_id="family_engagement",
                name="Family-Friendly Destination",
                description="Create best-in-class family shopping experience",
                related_goals=["customer_satisfaction", "market_expansion"],
                target_segments=[1],  # Budget-Conscious Families
                key_initiatives=["Kids zones", "Family events", "Educational programs"]
            ),
            SBMFocus(
                focus_id="tech_innovation",
                name="Technology-First Shopping",
                description="Lead in retail technology adoption",
                related_goals=["digital_transformation", "revenue_growth"],
                target_segments=[0],  # Tech-Savvy Young Professionals
                key_initiatives=["AR shopping", "Mobile payments", "Smart recommendations"]
            )
        ]
        
        ai_preferences = {
            "response_style": "professional_friendly",
            "data_focus": ["customer_insights", "campaign_optimization", "revenue_growth"],
            "proactive_suggestions": True,
            "risk_tolerance": "moderate",
            "innovation_level": "high",
            "cultural_context": "chinese_market"
        }
        
        return SBMConfiguration(
            goals=default_goals,
            focus_areas=default_focus_areas,
            ai_preferences=ai_preferences
        )
    
    def get_config(self) -> SBMConfiguration:
        """Get current configuration"""
        return self.config
    
    def update_goals(self, goals: List[SBMGoal]):
        """Update business goals"""
        self.config.goals = goals
        self.config.updated_at = datetime.now()
        self._save_config()
        
    def update_focus_areas(self, focus_areas: List[SBMFocus]):
        """Update focus areas"""
        self.config.focus_areas = focus_areas
        self.config.updated_at = datetime.now()
        self._save_config()
        
    def update_ai_preferences(self, preferences: Dict[str, Any]):
        """Update AI preferences"""
        self.config.ai_preferences.update(preferences)
        self.config.updated_at = datetime.now()
        self._save_config()
        
    def get_goals_by_priority(self, priority: str) -> List[SBMGoal]:
        """Get goals filtered by priority"""
        return [g for g in self.config.goals if g.priority == priority]
    
    def get_goals_by_category(self, category: str) -> List[SBMGoal]:
        """Get goals filtered by category"""
        return [g for g in self.config.goals if g.category == category]
    
    def get_focus_areas_for_segment(self, segment_id: int) -> List[SBMFocus]:
        """Get focus areas relevant to a specific customer segment"""
        return [f for f in self.config.focus_areas if segment_id in f.target_segments]
    
    def get_ai_context(self) -> Dict[str, Any]:
        """Get AI context including goals and preferences"""
        return {
            "business_name": self.config.business_name,
            "vision": self.config.vision,
            "mission": self.config.mission,
            "core_values": self.config.core_values,
            "high_priority_goals": [g.dict() for g in self.get_goals_by_priority("high")],
            "current_focus_areas": [f.dict() for f in self.config.focus_areas],
            "ai_preferences": self.config.ai_preferences,
            "performance_summary": self._calculate_performance_summary()
        }
    
    def _calculate_performance_summary(self) -> Dict[str, Any]:
        """Calculate overall performance against goals"""
        total_goals = len(self.config.goals)
        if total_goals == 0:
            return {"overall_progress": 0, "goals_on_track": 0}
        
        goals_on_track = 0
        total_progress = 0
        
        for goal in self.config.goals:
            if goal.target_value and goal.current_value:
                progress = (goal.current_value / goal.target_value) * 100
                total_progress += progress
                if progress >= 80:  # Consider 80% as on track
                    goals_on_track += 1
        
        return {
            "overall_progress": total_progress / total_goals if total_goals > 0 else 0,
            "goals_on_track": goals_on_track,
            "total_goals": total_goals,
            "achievement_rate": (goals_on_track / total_goals * 100) if total_goals > 0 else 0
        }
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config.dict(), f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def load_config(self):
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                self.config = SBMConfiguration(**data)
        except FileNotFoundError:
            logger.info("Config file not found, using defaults")
            self.config = self._load_default_config()
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            self.config = self._load_default_config()

# Global instance
sbm_config = SBMConfigManager()