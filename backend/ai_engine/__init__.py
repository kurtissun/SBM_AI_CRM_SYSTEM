
"""AI Engine components for customer intelligence and campaign optimization."""

from .adaptive_clustering import AdaptiveClustering as AdaptiveClusteringEngine
from .campaign_intelligence import CampaignIntelligenceEngine
from .conversational_ai import crm_assistant
from .insight_generator import IntelligentInsightGenerator

__all__ = [
    "AdaptiveClusteringEngine",
    "CampaignIntelligenceEngine", 
    "crm_assistant",
    "IntelligentInsightGenerator"
]

