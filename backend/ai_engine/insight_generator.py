"""
Advanced AI-powered insight generation system
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
import json
import logging
from datetime import datetime, timedelta
import openai
from core.config import settings
import joblib
from sklearn.mixture import GaussianMixture
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score

logger = logging.getLogger(__name__)

class IntelligentInsightGenerator:
    """
    Advanced system for generating business insights and recommendations
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # Initialize OpenAI if available
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.use_openai = True
        else:
            self.use_openai = False
        
        # Predefined segment characteristics for fallback
        self.segment_profiles = {
            0: {
                'name': 'Tech-Savvy Young Professionals',
                'characteristics': ['high_digital_engagement', 'convenience_focused', 'brand_conscious'],
                'preferred_channels': ['mobile_app', 'social_media', 'digital_ads'],
                'spending_patterns': 'impulse_and_planned',
                'value_drivers': ['innovation', 'convenience', 'social_status']
            },
            1: {
                'name': 'Budget-Conscious Families',
                'characteristics': ['value_seeking', 'family_oriented', 'bulk_buying'],
                'preferred_channels': ['email', 'in_store', 'loyalty_programs'],
                'spending_patterns': 'planned_purchases',
                'value_drivers': ['value_for_money', 'family_benefits', 'savings']
            },
            2: {
                'name': 'International Tourists',
                'characteristics': ['experience_seeking', 'brand_hunting', 'time_constrained'],
                'preferred_channels': ['concierge', 'digital_maps', 'multilingual_support'],
                'spending_patterns': 'high_value_concentrated',
                'value_drivers': ['exclusivity', 'authentic_experiences', 'convenience']
            },
            3: {
                'name': 'Event-Driven Visitors',
                'characteristics': ['occasion_motivated', 'social_activity', 'experience_focused'],
                'preferred_channels': ['event_marketing', 'social_media', 'word_of_mouth'],
                'spending_patterns': 'event_triggered',
                'value_drivers': ['entertainment', 'social_experiences', 'memories']
            },
            4: {
                'name': 'Mature Premium Shoppers',
                'characteristics': ['quality_focused', 'service_oriented', 'brand_loyal'],
                'preferred_channels': ['personal_service', 'traditional_media', 'loyalty_programs'],
                'spending_patterns': 'considered_purchases',
                'value_drivers': ['quality', 'service', 'trust']
            },
            5: {
                'name': 'Deal-Seeking Opportunists',
                'characteristics': ['price_sensitive', 'promotion_driven', 'comparison_shopping'],
                'preferred_channels': ['flash_sales', 'deal_alerts', 'price_comparison'],
                'spending_patterns': 'promotion_triggered',
                'value_drivers': ['best_deals', 'limited_offers', 'savings']
            }
        }
    
    def generate_comprehensive_insights(self, cluster_data: Dict, 
                                      business_context: Dict = None) -> Dict:
        """
        Generate comprehensive business insights for customer segments
        """
        insights = {
            'executive_summary': self._generate_executive_summary(cluster_data),
            'segment_insights': self._analyze_segments(cluster_data),
            'business_opportunities': self._identify_opportunities(cluster_data, business_context),
            'campaign_recommendations': self._generate_campaign_recommendations(cluster_data),
            'seasonal_strategies': self._generate_seasonal_strategies(cluster_data),
            'competitive_analysis': self._analyze_competitive_positioning(cluster_data),
            'risk_assessment': self._assess_risks(cluster_data),
            'action_plan': self._create_action_plan(cluster_data)
        }
        
        # Enhance with AI if available
        if self.use_openai:
            try:
                insights = self._enhance_insights_with_ai(insights, cluster_data)
            except AttributeError as e:
                logger.warning(f"AI enhancement method not available: {e}")
            except Exception as e:
                logger.warning(f"AI enhancement failed: {e}")
        
        return insights
    
    def _generate_executive_summary(self, cluster_data: Dict) -> Dict:
        """
        Generate executive-level summary
        """
        cluster_profiles = cluster_data.get('cluster_profiles', {})
        insights = cluster_data.get('insights', {})
        
        total_customers = sum(profile.get('size', 0) for profile in cluster_profiles.values())
        n_clusters = len(cluster_profiles)
        
        # Identify largest and most valuable segments
        largest_segment = max(cluster_profiles.items(), 
                            key=lambda x: x[1].get('size', 0)) if cluster_profiles else (0, {})
        
        high_value_segments = [
            cluster_id for cluster_id, insight in insights.items()
            if insight.get('predicted_value') == 'high'
        ]
        
        summary = {
            'total_customers_analyzed': total_customers,
            'segments_identified': n_clusters,
            'largest_segment': {
                'id': largest_segment[0],
                'size': largest_segment[1].get('size', 0),
                'percentage': largest_segment[1].get('percentage', 0)
            },
            'high_value_segments': len(high_value_segments),
            'key_findings': [
                f"Identified {n_clusters} distinct customer segments",
                f"Largest segment represents {largest_segment[1].get('percentage', 0):.1f}% of customers",
                f"{len(high_value_segments)} segments show high value potential",
                "Diverse customer base requires targeted marketing approaches"
            ],
            'recommended_focus': high_value_segments[:3] if high_value_segments else [largest_segment[0]],
            'overall_strategy': self._determine_overall_strategy(cluster_profiles, insights)
        }
        
        return summary
    
    def _determine_overall_strategy(self, cluster_profiles: Dict, insights: Dict) -> str:
        """
        Determine overall marketing strategy based on segment composition
        """
        if not cluster_profiles:
            return "data_collection_focus"
        
        # Analyze segment distribution
        total_size = sum(profile.get('size', 0) for profile in cluster_profiles.values())
        
        # Calculate diversity index
        diversity_score = 0
        for profile in cluster_profiles.values():
            proportion = profile.get('size', 0) / total_size if total_size > 0 else 0
            if proportion > 0:
                diversity_score -= proportion * np.log(proportion)
        
        # Determine strategy based on diversity and value distribution
        high_value_count = sum(1 for insight in insights.values() 
                              if insight.get('predicted_value') == 'high')
        
        if diversity_score > 1.5:  # High diversity
            if high_value_count >= 2:
                return "multi_segment_premium_focus"
            else:
                return "diversified_engagement"
        else:  # Lower diversity, more concentrated
            if high_value_count >= 1:
                return "premium_concentration"
            else:
                return "volume_based_growth"
    
    def _analyze_segments(self, cluster_data: Dict) -> Dict:
        """
        Deep analysis of each customer segment
        """
        cluster_profiles = cluster_data.get('cluster_profiles', {})
        insights = cluster_data.get('insights', {})
        
        segment_analysis = {}
        
        for cluster_id, profile in cluster_profiles.items():
            insight = insights.get(cluster_id, {})
            
            # Get segment characteristics from predefined profiles
            segment_profile = self.segment_profiles.get(cluster_id, {})
            
            analysis = {
                'profile_overview': {
                    'size': profile.get('size', 0),
                    'percentage': profile.get('percentage', 0),
                    'name': segment_profile.get('name', f'Segment {cluster_id}'),
                    'description': insight.get('description', 'Diverse customer group')
                },
                'demographics': profile.get('demographics', {}),
                'behavioral_patterns': {
                    'characteristics': segment_profile.get('characteristics', []),
                    'spending_pattern': segment_profile.get('spending_patterns', 'mixed'),
                    'preferred_channels': segment_profile.get('preferred_channels', []),
                    'value_drivers': segment_profile.get('value_drivers', [])
                },
                'business_value': {
                    'predicted_value': insight.get('predicted_value', 'medium'),
                    'revenue_potential': self._calculate_revenue_potential(profile, insight),
                    'growth_opportunity': self._assess_growth_opportunity(profile, cluster_id),
                    'retention_risk': self._assess_retention_risk(profile, cluster_id)
                },
                'engagement_strategy': {
                    'primary_approach': insight.get('marketing_strategy', 'balanced_approach'),
                    'recommended_campaigns': insight.get('target_campaigns', []),
                    'engagement_frequency': self._recommend_engagement_frequency(cluster_id),
                    'personalization_level': self._recommend_personalization_level(cluster_id)
                },
                'success_metrics': self._define_success_metrics(cluster_id, insight),
                'competitive_vulnerability': self._assess_competitive_vulnerability(profile, cluster_id)
            }
            
            segment_analysis[cluster_id] = analysis
        
        return segment_analysis
    
    def _calculate_revenue_potential(self, profile: Dict, insight: Dict) -> str:
        """
        Calculate revenue potential for segment
        """
        size = profile.get('size', 0)
        predicted_value = insight.get('predicted_value', 'medium')
        
        # Simple scoring system
        if predicted_value == 'high' and size > 100:
            return 'very_high'
        elif predicted_value == 'high' or size > 200:
            return 'high'
        elif predicted_value == 'medium' and size > 100:
            return 'medium'
        else:
            return 'low'
    
    def _assess_growth_opportunity(self, profile: Dict, cluster_id: int) -> str:
        """
        Assess growth opportunity for segment
        """
        size = profile.get('size', 0)
        avg_age = profile.get('demographics', {}).get('avg_age', 0)
        
        # Young segments have higher growth potential
        if avg_age < 30 and size < 300:
            return 'high'
        elif avg_age < 45 and size < 200:
            return 'medium'
        elif size < 150:
            return 'medium'
        else:
            return 'low'
    
    def _assess_retention_risk(self, profile: Dict, cluster_id: int) -> str:
        """
        Assess retention risk for segment
        """
        avg_rating = profile.get('characteristics', {}).get('avg_rating_id', 3)
        
        if avg_rating >= 4:
            return 'low'
        elif avg_rating >= 3:
            return 'medium'
        else:
            return 'high'
    
    def _recommend_engagement_frequency(self, cluster_id: int) -> str:
        """
        Recommend engagement frequency based on segment
        """
        frequency_mapping = {
            0: 'high_frequency',  # Tech-savvy: daily/every other day
            1: 'medium_frequency',  # Families: 2-3 times per week
            2: 'targeted_frequency',  # Tourists: during visit periods
            3: 'event_driven',  # Event visitors: around events
            4: 'low_frequency',  # Mature: weekly/bi-weekly
            5: 'promotion_driven'  # Deal seekers: when deals available
        }
        return frequency_mapping.get(cluster_id, 'medium_frequency')
    
    def _recommend_personalization_level(self, cluster_id: int) -> str:
        """
        Recommend personalization level
        """
        personalization_mapping = {
            0: 'high',  # Tech-savvy appreciate personalization
            1: 'medium',  # Families want relevant but not intrusive
            2: 'high',  # Tourists need contextual personalization
            3: 'medium',  # Event visitors want event-relevant content
            4: 'high',  # Mature shoppers value personal service
            5: 'low'  # Deal seekers care more about price than personalization
        }
        return personalization_mapping.get(cluster_id, 'medium')
    
    def _define_success_metrics(self, cluster_id: int, insight: Dict) -> List[str]:
        """
        Define key success metrics for each segment
        """
        base_metrics = ['engagement_rate', 'conversion_rate', 'customer_satisfaction']
        
        segment_specific_metrics = {
            0: ['app_usage', 'social_media_engagement', 'tech_adoption_rate'],
            1: ['family_package_uptake', 'loyalty_program_participation', 'referral_rate'],
            2: ['visit_duration', 'spending_per_visit', 'experience_rating'],
            3: ['event_attendance', 'social_sharing', 'repeat_event_participation'],
            4: ['service_satisfaction', 'premium_product_uptake', 'brand_loyalty_score'],
            5: ['promotion_response_rate', 'deal_conversion_rate', 'price_sensitivity_index']
        }
        
        return base_metrics + segment_specific_metrics.get(cluster_id, [])
    
    def _assess_competitive_vulnerability(self, profile: Dict, cluster_id: int) -> str:
        """
        Assess how vulnerable segment is to competitive threats
        """
        vulnerability_mapping = {
            0: 'high',  # Tech-savvy easily switch for better features
            1: 'low',  # Families tend to stick with convenient options
            2: 'medium',  # Tourists may be influenced by reviews/recommendations
            3: 'medium',  # Event visitors may go where events are
            4: 'low',  # Mature shoppers tend to be brand loyal
            5: 'high'  # Deal seekers will follow better deals
        }
        return vulnerability_mapping.get(cluster_id, 'medium')
    
    def _identify_opportunities(self, cluster_data: Dict, business_context: Dict = None) -> Dict:
        """
        Identify specific business opportunities
        """
        cluster_profiles = cluster_data.get('cluster_profiles', {})
        insights = cluster_data.get('insights', {})
        
        opportunities = {
            'revenue_growth': [],
            'market_expansion': [],
            'customer_experience': [],
            'operational_efficiency': [],
            'strategic_partnerships': []
        }
        
        # Analyze each segment for opportunities
        for cluster_id, profile in cluster_profiles.items():
            insight = insights.get(cluster_id, {})
            size = profile.get('size', 0)
            percentage = profile.get('percentage', 0)
            
            # Revenue growth opportunities
            if insight.get('predicted_value') == 'high' and size > 100:
                opportunities['revenue_growth'].append({
                    'segment': cluster_id,
                    'opportunity': f'Premium upselling to {self.segment_profiles.get(cluster_id, {}).get("name", f"Segment {cluster_id}")}',
                    'potential_impact': 'high',
                    'implementation_difficulty': 'medium'
                })
            
            # Market expansion opportunities
            if size < 150 and insight.get('predicted_value') in ['high', 'medium']:
                opportunities['market_expansion'].append({
                    'segment': cluster_id,
                    'opportunity': f'Grow {self.segment_profiles.get(cluster_id, {}).get("name", f"Segment {cluster_id}")} segment through targeted acquisition',
                    'potential_impact': 'medium',
                    'implementation_difficulty': 'medium'
                })
            
            # Customer experience opportunities
            if cluster_id in [2, 4]:  # Tourists and mature shoppers value experience
                opportunities['customer_experience'].append({
                    'segment': cluster_id,
                    'opportunity': f'Enhanced service experience for {self.segment_profiles.get(cluster_id, {}).get("name", f"Segment {cluster_id}")}',
                    'potential_impact': 'high',
                    'implementation_difficulty': 'low'
                })
        
        # Cross-segment opportunities
        if len(cluster_profiles) >= 4:
            opportunities['operational_efficiency'].append({
                'segment': 'all',
                'opportunity': 'Unified customer platform for cross-segment insights',
                'potential_impact': 'high',
                'implementation_difficulty': 'high'
            })
        
        return opportunities
    
    def _generate_campaign_recommendations(self, cluster_data: Dict) -> Dict:
        """
        Generate specific campaign recommendations
        """
        cluster_profiles = cluster_data.get('cluster_profiles', {})
        insights = cluster_data.get('insights', {})
        
        campaigns = {
            'immediate_campaigns': [],
            'seasonal_campaigns': [],
            'long_term_initiatives': [],
            'cross_segment_campaigns': []
        }
        
        for cluster_id, profile in cluster_profiles.items():
            insight = insights.get(cluster_id, {})
            segment_name = self.segment_profiles.get(cluster_id, {}).get('name', f'Segment {cluster_id}')
            
            # Immediate campaigns
            if profile.get('percentage', 0) > 15:  # Large segments get priority
                campaigns['immediate_campaigns'].append({
                    'name': f'{segment_name} Engagement Boost',
                    'target_segment': cluster_id,
                    'objective': 'increase_engagement',
                    'duration': '2_weeks',
                    'channels': self.segment_profiles.get(cluster_id, {}).get('preferred_channels', []),
                    'budget_allocation': 'medium',
                    'expected_roi': '150-200%'
                })
            
            # Seasonal campaigns
            if cluster_id in [1, 3]:  # Family and event segments are seasonal
                campaigns['seasonal_campaigns'].append({
                    'name': f'{segment_name} Holiday Special',
                    'target_segment': cluster_id,
                    'timing': 'holiday_seasons',
                    'objective': 'drive_sales',
                    'special_offers': True
                })
        
        # Cross-segment campaigns
        if len(cluster_profiles) >= 3:
            campaigns['cross_segment_campaigns'].append({
                'name': 'Mall-Wide Experience Festival',
                'target_segments': list(cluster_profiles.keys()),
                'objective': 'brand_awareness',
                'duration': '1_month',
                'budget_allocation': 'high'
            })
        
        return campaigns
    
    def _generate_seasonal_strategies(self, cluster_data: Dict) -> Dict:
        """
        Generate seasonal marketing strategies
        """
        strategies = {
            'spring': self._create_seasonal_strategy('spring', cluster_data),
            'summer': self._create_seasonal_strategy('summer', cluster_data),
            'fall': self._create_seasonal_strategy('fall', cluster_data),
            'winter': self._create_seasonal_strategy('winter', cluster_data)
        }
        
        return strategies
    
    def _create_seasonal_strategy(self, season: str, cluster_data: Dict) -> Dict:
        """
        Create strategy for specific season
        """
        cluster_profiles = cluster_data.get('cluster_profiles', {})
        
        seasonal_themes = {
            'spring': {
                'themes': ['renewal', 'fresh_starts', 'outdoor_activities'],
                'high_activity_segments': [0, 1, 3],  # Young professionals, families, event visitors
                'campaign_focus': 'lifestyle_and_wellness'
            },
            'summer': {
                'themes': ['vacation', 'leisure', 'family_time'],
                'high_activity_segments': [1, 2, 3],  # Families, tourists, event visitors
                'campaign_focus': 'experiences_and_entertainment'
            },
            'fall': {
                'themes': ['back_to_routine', 'preparation', 'cozy_comfort'],
                'high_activity_segments': [0, 1, 4],  # Professionals, families, mature shoppers
                'campaign_focus': 'practical_and_premium'
            },
            'winter': {
                'themes': ['holidays', 'gifts', 'celebrations'],
                'high_activity_segments': [1, 2, 4],  # Families, tourists, mature shoppers
                'campaign_focus': 'gifts_and_celebrations'
            }
        }
        
        season_info = seasonal_themes[season]
        active_segments = [seg for seg in season_info['high_activity_segments'] 
                          if seg in cluster_profiles]
        
        return {
            'primary_themes': season_info['themes'],
            'focus_segments': active_segments,
            'campaign_focus': season_info['campaign_focus'],
            'recommended_budget_allocation': {
                seg: 'high' if seg in active_segments else 'low' 
                for seg in cluster_profiles.keys()
            },
            'key_initiatives': self._generate_seasonal_initiatives(season, active_segments)
        }
    
    def _generate_seasonal_initiatives(self, season: str, active_segments: List[int]) -> List[str]:
        """
        Generate specific initiatives for season
        """
        initiative_mapping = {
            'spring': [
                'Spring wellness festival',
                'Outdoor activity promotions',
                'Fresh fashion showcase',
                'Health and fitness campaigns'
            ],
            'summer': [
                'Summer entertainment series',
                'Family activity zones',
                'Tourist welcome programs',
                'Cooling station promotions'
            ],
            'fall': [
                'Back-to-work campaigns',
                'Autumn comfort foods',
                'Professional wardrobe updates',
                'Cozy home décor showcases'
            ],
            'winter': [
                'Holiday shopping festivals',
                'Gift recommendation services',
                'Celebration dining packages',
                'Year-end loyalty rewards'
            ]
        }
        
        return initiative_mapping.get(season, [])
    
    def _analyze_competitive_positioning(self, cluster_data: Dict) -> Dict:
        """
        Analyze competitive positioning opportunities
        """
        cluster_profiles = cluster_data.get('cluster_profiles', {})
        
        competitive_analysis = {
            'market_position': self._assess_market_position(cluster_profiles),
            'differentiation_opportunities': self._identify_differentiation_opportunities(cluster_profiles),
            'competitive_threats': self._assess_competitive_threats(cluster_profiles),
            'defensive_strategies': self._recommend_defensive_strategies(cluster_profiles),
            'offensive_strategies': self._recommend_offensive_strategies(cluster_profiles)
        }
        
        return competitive_analysis
    
    def _assess_market_position(self, cluster_profiles: Dict) -> str:
        """
        Assess overall market position
        """
        total_customers = sum(profile.get('size', 0) for profile in cluster_profiles.values())
        diversity_score = len(cluster_profiles)
        
        if total_customers > 1000 and diversity_score >= 5:
            return 'market_leader'
        elif total_customers > 500 and diversity_score >= 4:
            return 'strong_competitor'
        elif total_customers > 200:
            return 'niche_player'
        else:
            return 'emerging_player'
    
    def _identify_differentiation_opportunities(self, cluster_profiles: Dict) -> List[str]:
        """
        Identify ways to differentiate from competitors
        """
        opportunities = []
        
        # Analyze segment composition for unique angles
        if 0 in cluster_profiles:  # Tech-savvy segment
            opportunities.append('Technology-first shopping experience')
        
        if 2 in cluster_profiles:  # Tourist segment
            opportunities.append('International visitor specialization')
        
        if 4 in cluster_profiles:  # Mature premium segment
            opportunities.append('Premium service excellence')
        
        if len(cluster_profiles) >= 5:
            opportunities.append('Comprehensive multi-demographic appeal')
        
        return opportunities
    
    def _assess_competitive_threats(self, cluster_profiles: Dict) -> List[Dict]:
        """
        Assess competitive threats for each segment
        """
        threats = []
        
        for cluster_id, profile in cluster_profiles.items():
            vulnerability = self._assess_competitive_vulnerability(profile, cluster_id)
            segment_name = self.segment_profiles.get(cluster_id, {}).get('name', f'Segment {cluster_id}')
            
            if vulnerability == 'high':
                threats.append({
                    'segment': cluster_id,
                    'segment_name': segment_name,
                    'threat_level': 'high',
                    'threat_type': 'price_competition' if cluster_id == 5 else 'feature_competition',
                    'mitigation_priority': 'immediate'
                })
        
        return threats
    
    def _recommend_defensive_strategies(self, cluster_profiles: Dict) -> List[str]:
        """
        Recommend defensive strategies against competition
        """
        strategies = [
            'Strengthen customer loyalty programs',
            'Improve customer service quality',
            'Enhance unique value propositions'
        ]
        
        # Segment-specific defensive strategies
        if 1 in cluster_profiles:  # Families
            strategies.append('Family-friendly facility improvements')
        
        if 4 in cluster_profiles:  # Mature premium
            strategies.append('Premium service tier development')
        
        return strategies
    
    def _recommend_offensive_strategies(self, cluster_profiles: Dict) -> List[str]:
        """
        Recommend offensive strategies for market expansion
        """
        strategies = [
            'Targeted competitor customer acquisition',
            'Market penetration in underserved segments',
            'Strategic partnership development'
        ]
        
        return strategies
    
    def _assess_risks(self, cluster_data: Dict) -> Dict:
        """
        Assess potential risks and challenges
        """
        cluster_profiles = cluster_data.get('cluster_profiles', {})
        
        risks = {
            'customer_concentration_risk': self._assess_concentration_risk(cluster_profiles),
            'market_dependency_risk': self._assess_market_dependency_risk(cluster_profiles),
            'competitive_risk': self._assess_overall_competitive_risk(cluster_profiles),
            'operational_risks': self._identify_operational_risks(cluster_profiles),
            'mitigation_strategies': self._recommend_risk_mitigation(cluster_profiles)
        }
        
        return risks
    
    def _assess_concentration_risk(self, cluster_profiles: Dict) -> Dict:
        """
        Assess customer concentration risk
        """
        if not cluster_profiles:
            return {'level': 'unknown', 'description': 'Insufficient data'}
        
        total_customers = sum(profile.get('size', 0) for profile in cluster_profiles.values())
        largest_segment_size = max(profile.get('size', 0) for profile in cluster_profiles.values())
        concentration_ratio = largest_segment_size / total_customers if total_customers > 0 else 0
        
        if concentration_ratio > 0.6:
            risk_level = 'high'
            description = 'Over-dependence on single customer segment'
        elif concentration_ratio > 0.4:
            risk_level = 'medium'
            description = 'Moderate concentration in primary segment'
        else:
            risk_level = 'low'
            description = 'Well-diversified customer base'
        
        return {
            'level': risk_level,
            'concentration_ratio': concentration_ratio,
            'description': description
        }
    
    def _assess_market_dependency_risk(self, cluster_profiles: Dict) -> str:
        """
        Assess dependency on specific market conditions
        """
        tourist_segment_size = cluster_profiles.get(2, {}).get('size', 0)
        total_customers = sum(profile.get('size', 0) for profile in cluster_profiles.values())
        
        if total_customers > 0 and tourist_segment_size / total_customers > 0.3:
            return 'high_tourism_dependency'
        
        return 'low_external_dependency'
    
    def _assess_overall_competitive_risk(self, cluster_profiles: Dict) -> str:
        """
        Assess overall competitive risk level
        """
        high_vulnerability_segments = sum(
            1 for cluster_id in cluster_profiles.keys()
            if self._assess_competitive_vulnerability(cluster_profiles[cluster_id], cluster_id) == 'high'
        )
        
        total_segments = len(cluster_profiles)
        
        if high_vulnerability_segments / total_segments > 0.5:
            return 'high'
        elif high_vulnerability_segments / total_segments > 0.3:
            return 'medium'
        else:
            return 'low'
    
    def _identify_operational_risks(self, cluster_profiles: Dict) -> List[str]:
        """
        Identify operational risks
        """
        risks = []
        
        total_customers = sum(profile.get('size', 0) for profile in cluster_profiles.values())
        
        if total_customers > 2000:
            risks.append('Capacity management challenges')
        
        if 2 in cluster_profiles:  # Tourist segment
            risks.append('Seasonal demand fluctuations')
        
        if len(cluster_profiles) >= 6:
            risks.append('Marketing complexity and resource allocation challenges')
        
        return risks
    
    def _recommend_risk_mitigation(self, cluster_profiles: Dict) -> List[str]:
        """
        Recommend risk mitigation strategies
        """
        strategies = [
            'Diversify customer acquisition channels',
            'Develop flexible operational capacity',
            'Create robust customer retention programs',
            'Implement advanced analytics for early warning systems',
            'Build strategic partnerships for market resilience'
        ]
        
        return strategies
    
    def _create_action_plan(self, cluster_data: Dict) -> Dict:
        """
        Create prioritized action plan
        """
        cluster_profiles = cluster_data.get('cluster_profiles', {})
        insights = cluster_data.get('insights', {})
        
        action_plan = {
            'immediate_actions': self._identify_immediate_actions(cluster_profiles, insights),
            'short_term_initiatives': self._identify_short_term_initiatives(cluster_profiles, insights),
            'long_term_strategies': self._identify_long_term_strategies(cluster_profiles, insights),
            'resource_requirements': self._estimate_resource_requirements(cluster_profiles),
            'success_metrics': self._define_overall_success_metrics(cluster_profiles),
            'timeline': self._create_implementation_timeline(cluster_profiles)
        }
        
        return action_plan
    
    def _identify_immediate_actions(self, cluster_profiles: Dict, insights: Dict) -> List[Dict]:
        """
        Identify actions that should be taken immediately (next 2 weeks)
        """
        actions = []
        
        # High-value, large segments get immediate attention
        for cluster_id, profile in cluster_profiles.items():
            insight = insights.get(cluster_id, {})
            if (insight.get('predicted_value') == 'high' and 
                profile.get('percentage', 0) > 10):
                
                actions.append({
                    'action': f'Launch targeted campaign for {self.segment_profiles.get(cluster_id, {}).get("name", f"Segment {cluster_id}")}',
                    'priority': 'high',
                    'expected_completion': '2_weeks',
                    'responsible_team': 'marketing',
                    'success_metric': 'engagement_rate_increase'
                })
        
        # Always include data collection improvement
        actions.append({
            'action': 'Implement enhanced customer data collection',
            'priority': 'high',
            'expected_completion': '1_week',
            'responsible_team': 'analytics',
            'success_metric': 'data_quality_score'
        })
        
        return actions[:5]  # Limit to top 5 immediate actions
    
    def _identify_short_term_initiatives(self, cluster_profiles: Dict, insights: Dict) -> List[Dict]:
        """
        Identify initiatives for next 1-3 months
        """
        initiatives = [
            {
                'initiative': 'Comprehensive segmentation review and optimization',
                'timeline': '1_month',
                'priority': 'high',
                'expected_impact': 'improved_targeting_accuracy'
            },
            {
                'initiative': 'Cross-segment campaign testing program',
                'timeline': '6_weeks',
                'priority': 'medium',
                'expected_impact': 'optimized_campaign_performance'
            },
            {
                'initiative': 'Customer experience enhancement for top segments',
                'timeline': '2_months',
                'priority': 'high',
                'expected_impact': 'increased_customer_satisfaction'
            }
        ]
        
        return initiatives
    
    def _identify_long_term_strategies(self, cluster_profiles: Dict, insights: Dict) -> List[Dict]:
        """
        Identify long-term strategic initiatives (3+ months)
        """
        strategies = [
            {
                'strategy': 'Predictive customer lifecycle management system',
                'timeline': '6_months',
                'investment_level': 'high',
                'expected_roi': '300%'
            },
            {
                'strategy': 'Advanced personalization engine deployment',
                'timeline': '4_months',
                'investment_level': 'medium',
                'expected_roi': '200%'
            },
            {
                'strategy': 'Competitive intelligence and market expansion program',
                'timeline': '12_months',
                'investment_level': 'high',
                'expected_roi': '250%'
            }
        ]
        
        return strategies
    
    def _estimate_resource_requirements(self, cluster_profiles: Dict) -> Dict:
        """
        Estimate resource requirements for implementation
        """
        n_segments = len(cluster_profiles)
        total_customers = sum(profile.get('size', 0) for profile in cluster_profiles.values())
        
        return {
            'marketing_team_size': max(3, n_segments // 2),
            'analytics_specialists': 2,
            'budget_allocation': {
                'immediate_campaigns': 'medium',
                'technology_infrastructure': 'high',
                'staff_training': 'low',
                'external_consultants': 'medium'
            },
            'technology_requirements': [
                'Advanced analytics platform',
                'Campaign management system',
                'Customer data platform',
                'A/B testing infrastructure'
            ]
        }
    
    def _define_overall_success_metrics(self, cluster_profiles: Dict) -> List[str]:
        """
        Define overall success metrics for the segmentation program
        """
        return [
            'customer_lifetime_value_increase',
            'marketing_roi_improvement',
            'customer_satisfaction_score',
            'segment_engagement_rates',
            'cross_sell_success_rate',
            'customer_retention_rate',
            'market_share_growth',
            'campaign_conversion_rates'
        ]
    
    def _create_implementation_timeline(self, cluster_profiles: Dict) -> Dict:
        return {
            'week_1_2': [
                'Launch immediate high-priority campaigns',
                'Implement enhanced data collection',
                'Set up success metrics tracking'
            ],
            'month_1': [
                'Complete segmentation optimization',
                'Launch cross-segment testing',
                'Begin customer experience enhancements'
            ],
            'quarter_1': [
                'Evaluate initial results',
                'Scale successful clusters'
            ]
        }

        
    
    def _select_best_clusters(self, results: Dict) -> int:
        """
        Select best cluster number based on composite scoring
        """
        scores = {}
        
        for n_clusters, metrics in results.items():
            # Normalize metrics (higher is better for silhouette and calinski_harabasz)
            # Lower is better for davies_bouldin
            silhouette_norm = metrics['silhouette']
            calinski_norm = metrics['calinski_harabasz'] / 10000  # Scale down
            davies_norm = 1 / (1 + metrics['davies_bouldin'])  # Invert so higher is better
            
            # Composite score with weights
            composite_score = (0.4 * silhouette_norm + 
                             0.3 * calinski_norm + 
                             0.3 * davies_norm)
            scores[n_clusters] = composite_score
        
        return max(scores.keys(), key=lambda k: scores[k])
    
    def advanced_clustering(self, X: np.ndarray) -> Dict:
        """
        Try multiple clustering algorithms and select the best
        """
        algorithms = {
            'kmeans': self._cluster_kmeans,
            'gaussian_mixture': self._cluster_gaussian_mixture,
            'agglomerative': self._cluster_agglomerative
        }
        
        best_result = None
        best_score = -1
        
        for name, algo_func in algorithms.items():
            try:
                result = algo_func(X)
                if result['silhouette'] > best_score:
                    best_score = result['silhouette']
                    best_result = result
                    best_result['algorithm'] = name
            except Exception as e:
                logger.warning(f"Algorithm {name} failed: {e}")
                continue
        
        return best_result
    
    def _cluster_kmeans(self, X: np.ndarray) -> Dict:
        """KMeans clustering with optimal cluster detection"""
        return self.find_optimal_clusters(X)
    
    def _cluster_gaussian_mixture(self, X: np.ndarray) -> Dict:
        """Gaussian Mixture Model clustering"""
        best_score = -1
        best_result = None
        
        cluster_range = range(2, min(self.max_clusters + 1, len(X) // self.min_cluster_size + 1))
        
        for n_clusters in cluster_range:
            gmm = GaussianMixture(n_components=n_clusters, random_state=self.random_state)
            labels = gmm.fit_predict(X)
            
            silhouette = silhouette_score(X, labels)
            
            if silhouette > best_score:
                best_score = silhouette
                best_result = {
                    'silhouette': silhouette,
                    'model': gmm,
                    'labels': labels,
                    'n_clusters': n_clusters
                }
        
        return best_result
    
    def _cluster_agglomerative(self, X: np.ndarray) -> Dict:
        """Agglomerative clustering"""
        best_score = -1
        best_result = None
        
        cluster_range = range(2, min(self.max_clusters + 1, len(X) // self.min_cluster_size + 1))
        
        for n_clusters in cluster_range:
            agg = AgglomerativeClustering(n_clusters=n_clusters)
            labels = agg.fit_predict(X)
            
            silhouette = silhouette_score(X, labels)
            
            if silhouette > best_score:
                best_score = silhouette
                best_result = {
                    'silhouette': silhouette,
                    'model': agg,
                    'labels': labels,
                    'n_clusters': n_clusters
                }
        
        return best_result
    
    def create_cluster_profiles(self, df: pd.DataFrame, labels: np.ndarray, 
                              feature_names: List[str]) -> Dict:
        """
        Create detailed profiles for each cluster
        """
        df_with_clusters = df.copy()
        df_with_clusters['cluster'] = labels
        
        profiles = {}
        
        for cluster_id in np.unique(labels):
            cluster_data = df_with_clusters[df_with_clusters['cluster'] == cluster_id]
            
            profile = {
                'size': len(cluster_data),
                'percentage': len(cluster_data) / len(df) * 100,
                'demographics': {},
                'characteristics': {},
                'key_features': []
            }
            
            # Demographics
            if 'age' in df.columns:
                profile['demographics']['avg_age'] = float(cluster_data['age'].mean())
                profile['demographics']['age_std'] = float(cluster_data['age'].std())
                profile['demographics']['age_range'] = [
                    float(cluster_data['age'].min()), 
                    float(cluster_data['age'].max())
                ]
            
            if 'sex' in df.columns:
                profile['demographics']['gender_distribution'] = \
                    cluster_data['sex'].value_counts().to_dict()
            
            # Characteristics
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if col in cluster_data.columns:
                    profile['characteristics'][f'avg_{col}'] = float(cluster_data[col].mean())
            
            # Key distinguishing features
            cluster_means = cluster_data[numeric_cols].mean()
            overall_means = df[numeric_cols].mean()
            
            differences = (cluster_means - overall_means).abs().sort_values(ascending=False)
            profile['key_features'] = differences.head(3).index.tolist()
            
            profiles[cluster_id] = profile
        
        return profiles
    
    def generate_cluster_insights(self, profiles: Dict) -> Dict:
        """
        Generate business insights for each cluster
        """
        insights = {}
        
        for cluster_id, profile in profiles.items():
            insight = {
                'cluster_id': cluster_id,
                'size': profile['size'],
                'percentage': profile['percentage'],
                'description': '',
                'marketing_strategy': '',
                'target_campaigns': [],
                'predicted_value': 'medium'
            }
            
            # Generate description based on characteristics
            age_avg = profile['demographics'].get('avg_age', 0)
            
            if age_avg < 25:
                insight['description'] = "Young, tech-savvy customers"
                insight['marketing_strategy'] = "Digital-first, social media campaigns"
                insight['target_campaigns'] = ['social_media', 'mobile_app', 'gaming']
            elif age_avg < 35:
                insight['description'] = "Young professionals and early career"
                insight['marketing_strategy'] = "Convenience and lifestyle focused"
                insight['target_campaigns'] = ['convenience', 'professional', 'lifestyle']
            elif age_avg < 50:
                insight['description'] = "Established professionals and families"
                insight['marketing_strategy'] = "Family-oriented and premium experiences"
                insight['target_campaigns'] = ['family', 'premium', 'experiences']
            else:
                insight['description'] = "Mature customers with established preferences"
                insight['marketing_strategy'] = "Traditional channels and loyalty programs"
                insight['target_campaigns'] = ['loyalty', 'traditional', 'premium']
            
            # Predict customer value based on characteristics
            rating_avg = profile['characteristics'].get('avg_rating_id', 0)
            if rating_avg >= 4:
                insight['predicted_value'] = 'high'
            elif rating_avg >= 3:
                insight['predicted_value'] = 'medium'
            else:
                insight['predicted_value'] = 'low'
            
            insights[cluster_id] = insight
        
        return insights
    
    def fit_transform(self, df: pd.DataFrame, seasonal_weights: Dict = None) -> Dict:
        """
        Main method to perform adaptive clustering
        """
        logger.info("Starting adaptive clustering process")
        
        # Prepare features
        X, feature_names = self.prepare_features(df, seasonal_weights)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Apply PCA for dimensionality reduction
        X_reduced = self.pca.fit_transform(X_scaled)
        
        logger.info(f"Features reduced from {X.shape[1]} to {X_reduced.shape[1]} dimensions")
        
        # Find best clustering
        clustering_result = self.advanced_clustering(X_reduced)
        
        if clustering_result is None:
            raise ValueError("All clustering algorithms failed")
        
        self.best_model = clustering_result['model']
        labels = clustering_result['labels']
        
        # Create cluster profiles
        self.cluster_profiles = self.create_cluster_profiles(df, labels, feature_names)
        
        # Generate insights
        insights = self.generate_cluster_insights(self.cluster_profiles)
        
        result = {
            'labels': labels,
            'n_clusters': len(np.unique(labels)),
            'silhouette_score': clustering_result['silhouette'],
            'algorithm_used': clustering_result.get('algorithm', 'kmeans'),
            'cluster_profiles': self.cluster_profiles,
            'insights': insights,
            'feature_names': feature_names,
            'model_performance': {
                'explained_variance_ratio': self.pca.explained_variance_ratio_.tolist(),
                'n_components_used': self.pca.n_components_
            }
        }
        
        logger.info(f"Clustering completed: {result['n_clusters']} clusters, "
                   f"silhouette score: {result['silhouette_score']:.3f}")
        
        return result
    
    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """
        Predict cluster labels for new data
        """
        if self.best_model is None:
            raise ValueError("Model not fitted. Call fit_transform first.")
        
        X, _ = self.prepare_features(df)
        X_scaled = self.scaler.transform(X)
        X_reduced = self.pca.transform(X_scaled)
        
        return self.best_model.predict(X_reduced)
    
    def save_model(self, filepath: str):
        """Save the trained model and preprocessors"""
        model_data = {
            'scaler': self.scaler,
            'pca': self.pca,
            'model': self.best_model,
            'cluster_profiles': self.cluster_profiles,
            'config': self.config
        }
        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a trained model and preprocessors"""
        model_data = joblib.load(filepath)
        self.scaler = model_data['scaler']
        self.pca = model_data['pca']
        self.best_model = model_data['model']
        self.cluster_profiles = model_data['cluster_profiles']
        self.config = model_data.get('config', {})
        logger.info(f"Model loaded from {filepath}")

class SeasonalClusteringManager:
    """
    Manages seasonal adaptations in clustering
    """
    
    def __init__(self):
        self.seasonal_weights = {
            'spring': {'age': 1.0, 'rating_id': 1.2, 'expanding_type_name': 1.1},
            'summer': {'age': 0.9, 'rating_id': 1.3, 'expanding_type_name': 1.0},
            'fall': {'age': 1.1, 'rating_id': 1.1, 'expanding_type_name': 1.2},
            'winter': {'age': 1.2, 'rating_id': 0.9, 'expanding_type_name': 1.3}
        }
    
    def get_seasonal_weights(self, season: str = None) -> Dict:
        """Get seasonal weights based on current season or specified season"""
        if season is None:
            season = self._detect_current_season()
        return self.seasonal_weights.get(season, self.seasonal_weights['spring'])
    
    def _detect_current_season(self) -> str:
        """Detect current season based on date"""
        month = datetime.now().month
        if month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        elif month in [9, 10, 11]:
            return 'fall'
        else:
            return 'winter'
    
    def _enhance_insights_with_ai(self, insights: Dict, cluster_data: Dict) -> Dict:
        """
        Enhance insights with AI-powered recommendations (Claude LLM integration)
        """
        try:
            # Try Claude LLM first
            from .claude_insights import enhance_insights_with_claude
            
            business_context = {
                'business_type': 'Chinese Shopping Mall / Retail Complex',
                'location': 'China (Beijing, Shanghai, Guangzhou, Shenzhen, Chengdu)',
                'customer_base': 'Mixed demographics with Chinese shopping preferences',
                'store_types': ['零售 (Retail)', '餐饮 (F&B)', '娱乐 (Entertainment)'],
                'membership_tiers': ['橙卡会员', '金卡会员', '钻卡会员']
            }
            
            enhanced_insights = enhance_insights_with_claude(insights, cluster_data, business_context)
            
            # Add traditional AI suggestions as backup
            for section_name, section_data in enhanced_insights.items():
                if isinstance(section_data, dict) and 'ai_suggestions' not in section_data:
                    enhanced_insights[section_name]['ai_suggestions'] = self._generate_ai_suggestions(section_name, section_data)
            
            return enhanced_insights
            
        except Exception as e:
            logger.warning(f"AI enhancement failed: {e}")
            # Fallback to basic enhancement
            enhanced_insights = insights.copy()
            for section_name, section_data in enhanced_insights.items():
                if isinstance(section_data, dict) and 'recommendations' not in section_data:
                    enhanced_insights[section_name]['ai_suggestions'] = self._generate_ai_suggestions(section_name, section_data)
            return enhanced_insights
    
    def _generate_ai_suggestions(self, section_name: str, section_data: Dict) -> List[str]:
        """Generate AI-powered suggestions for each section"""
        suggestions = []
        
        if section_name == 'segment_insights':
            suggestions = [
                "Consider implementing dynamic pricing based on segment value",
                "Develop segment-specific loyalty programs",
                "Create personalized communication strategies"
            ]
        elif section_name == 'business_opportunities':
            suggestions = [
                "Explore cross-segment product bundling opportunities",
                "Investigate emerging market trends for expansion",
                "Consider strategic partnerships for market penetration"
            ]
        elif section_name == 'campaign_recommendations':
            suggestions = [
                "Implement A/B testing for campaign optimization",
                "Use predictive analytics for timing optimization",
                "Consider omnichannel campaign strategies"
            ]
        else:
            suggestions = [
                "Monitor performance metrics continuously",
                "Adapt strategies based on market feedback",
                "Consider seasonal variations in implementation"
            ]
        
        return suggestions
