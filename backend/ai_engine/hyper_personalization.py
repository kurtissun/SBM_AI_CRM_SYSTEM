"""
Advanced hyper-personalization engine for individual customer targeting
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import json
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
import logging

logger = logging.getLogger(__name__)

class HyperPersonalizationEngine:
    """
    Creates unique, individualized experiences for each customer
    """
    
    def __init__(self):
        self.customer_profiles = {}
        self.similarity_model = NearestNeighbors(n_neighbors=10, metric='cosine')
        self.preference_weights = {
            'recency': 0.3,
            'frequency': 0.25, 
            'monetary': 0.25,
            'category_affinity': 0.2
        }
        
    def create_individual_profile(self, customer_id: str, customer_data: Dict) -> Dict[str, Any]:
        """
        Creates a comprehensive individual profile for hyper-personalization
        """
        profile = {
            'customer_id': customer_id,
            'created_at': datetime.now().isoformat(),
            'demographic_profile': self._extract_demographics(customer_data),
            'behavioral_profile': self._analyze_behavior_patterns(customer_data),
            'preference_profile': self._infer_preferences(customer_data),
            'engagement_profile': self._analyze_engagement_patterns(customer_data),
            'lifecycle_stage': self._determine_lifecycle_stage(customer_data),
            'personalization_opportunities': []
        }
        
        # Generate personalization opportunities
        profile['personalization_opportunities'] = self._identify_opportunities(profile)
        
        self.customer_profiles[customer_id] = profile
        return profile
    
    def generate_personalized_offers(self, customer_id: str) -> List[Dict[str, Any]]:
        """
        Generates highly specific, personalized offers for individual customer
        """
        if customer_id not in self.customer_profiles:
            logger.warning(f"Customer {customer_id} profile not found")
            return []
        
        profile = self.customer_profiles[customer_id]
        offers = []
        
        # 1. Category-based personalized offers
        category_offers = self._generate_category_offers(profile)
        offers.extend(category_offers)
        
        # 2. Timing-based personalized offers
        timing_offers = self._generate_timing_offers(profile)
        offers.extend(timing_offers)
        
        # 3. Social proof personalized offers
        social_offers = self._generate_social_proof_offers(profile)
        offers.extend(social_offers)
        
        # 4. Lifecycle-based offers
        lifecycle_offers = self._generate_lifecycle_offers(profile)
        offers.extend(lifecycle_offers)
        
        # Rank offers by predicted effectiveness
        ranked_offers = self._rank_offers_by_effectiveness(offers, profile)
        
        return ranked_offers[:5]  # Return top 5 offers
    
    def personalized_communication_timing(self, customer_id: str) -> Dict[str, Any]:
        """
        Determines optimal communication timing for each individual customer
        """
        profile = self.customer_profiles.get(customer_id, {})
        engagement_data = profile.get('engagement_profile', {})
        
        timing_strategy = {
            'optimal_day': self._predict_optimal_day(engagement_data),
            'optimal_time': self._predict_optimal_time(engagement_data),
            'communication_frequency': self._determine_frequency(profile),
            'preferred_channels': self._rank_communication_channels(profile),
            'message_tone': self._determine_message_tone(profile),
            'content_preferences': self._determine_content_preferences(profile)
        }
        
        return timing_strategy
    
    def generate_individual_journey(self, customer_id: str) -> Dict[str, Any]:
        """
        Creates a personalized customer journey map for the individual
        """
        profile = self.customer_profiles.get(customer_id, {})
        
        journey = {
            'current_stage': profile.get('lifecycle_stage', 'unknown'),
            'next_best_actions': self._predict_next_actions(profile),
            'personalized_touchpoints': self._design_touchpoints(profile),
            'content_recommendations': self._recommend_content(profile),
            'experience_customizations': self._customize_experience(profile)
        }
        
        return journey
    
    def _extract_demographics(self, customer_data: Dict) -> Dict:
        """Extract and enhance demographic information"""
        demographics = {
            'age': customer_data.get('age', 0),
            'gender': customer_data.get('sex', 'unknown'),
            'age_group': self._categorize_age(customer_data.get('age', 0)),
            'life_stage': self._infer_life_stage(customer_data),
            'economic_segment': self._infer_economic_segment(customer_data)
        }
        return demographics
    
    def _analyze_behavior_patterns(self, customer_data: Dict) -> Dict:
        """Analyze individual behavioral patterns"""
        return {
            'visit_frequency': customer_data.get('visit_frequency', 0),
            'avg_spending': customer_data.get('avg_spending', 0),
            'seasonal_patterns': self._detect_seasonal_patterns(customer_data),
            'time_preferences': self._analyze_time_preferences(customer_data),
            'category_affinity': self._calculate_category_affinity(customer_data),
            'brand_loyalty_score': self._calculate_brand_loyalty(customer_data)
        }
    
    def _infer_preferences(self, customer_data: Dict) -> Dict:
        """Infer deep preferences from behavior"""
        return {
            'price_sensitivity': self._calculate_price_sensitivity(customer_data),
            'quality_preference': self._infer_quality_preference(customer_data),
            'convenience_importance': self._measure_convenience_preference(customer_data),
            'social_influence_susceptibility': self._measure_social_influence(customer_data),
            'innovation_adoption': self._classify_innovation_adoption(customer_data)
        }
    
    def _generate_category_offers(self, profile: Dict) -> List[Dict]:
        """Generate offers based on category preferences"""
        offers = []
        category_affinity = profile['behavioral_profile'].get('category_affinity', {})
        
        for category, affinity_score in category_affinity.items():
            if affinity_score > 0.7:  # High affinity
                offer = {
                    'type': 'category_personalized',
                    'category': category,
                    'offer_text': f"Exclusive {category} collection just for you - 25% off your favorite brands",
                    'discount_percentage': self._calculate_optimal_discount(profile, category),
                    'predicted_effectiveness': affinity_score * 0.8,
                    'personalization_level': 'high'
                }
                offers.append(offer)
        
        return offers
    
    def _generate_timing_offers(self, profile: Dict) -> List[Dict]:
        """Generate time-sensitive personalized offers"""
        offers = []
        time_prefs = profile['behavioral_profile'].get('time_preferences', {})
        
        if time_prefs.get('preferred_shopping_time') == 'evening':
            offer = {
                'type': 'timing_personalized',
                'offer_text': "Evening shopper special - Extra 15% off after 6PM, just for you!",
                'timing_restriction': 'after_6pm',
                'predicted_effectiveness': 0.75,
                'personalization_level': 'medium'
            }
            offers.append(offer)
        
        return offers
    
    def _generate_social_proof_offers(self, profile: Dict) -> List[Dict]:
        """Generate offers with personalized social proof"""
        offers = []
        social_susceptibility = profile['preference_profile'].get('social_influence_susceptibility', 0)
        
        if social_susceptibility > 0.6:
            similar_customers = self._find_similar_customers(profile)
            popular_items = self._get_popular_items_among_similar(similar_customers)
            
            offer = {
                'type': 'social_proof_personalized',
                'offer_text': f"Customers like you are loving {popular_items[0]} - Special price just for you!",
                'social_proof': f"95% of customers with similar taste rated this 5 stars",
                'predicted_effectiveness': social_susceptibility * 0.7,
                'personalization_level': 'high'
            }
            offers.append(offer)
        
        return offers
    
    def _generate_lifecycle_offers(self, profile: Dict) -> List[Dict]:
        """Generate offers based on customer lifecycle stage"""
        offers = []
        lifecycle_stage = profile.get('lifecycle_stage', 'unknown')
        
        lifecycle_offers = {
            'new_customer': {
                'offer_text': "Welcome! Get 30% off your second visit this month",
                'focus': 'retention',
                'effectiveness': 0.8
            },
            'regular_customer': {
                'offer_text': "Thank you for your loyalty - Exclusive VIP preview access",
                'focus': 'engagement',
                'effectiveness': 0.7
            },
            'at_risk': {
                'offer_text': "We miss you! Come back with 40% off your favorite categories",
                'focus': 'win_back',
                'effectiveness': 0.9
            },
            'champion': {
                'offer_text': "Our top customer deserves the best - Personal shopping service included",
                'focus': 'advocacy',
                'effectiveness': 0.85
            }
        }
        
        if lifecycle_stage in lifecycle_offers:
            offer = lifecycle_offers[lifecycle_stage].copy()
            offer['type'] = 'lifecycle_personalized'
            offer['predicted_effectiveness'] = offer['effectiveness']
            offer['personalization_level'] = 'high'
            offers.append(offer)
        
        return offers
    
    def _predict_optimal_day(self, engagement_data: Dict) -> str:
        """Predict best day to contact customer"""
        day_patterns = engagement_data.get('day_patterns', {})
        if day_patterns:
            return max(day_patterns.items(), key=lambda x: x[1])[0]
        return 'tuesday'  # Default safe choice
    
    def _predict_optimal_time(self, engagement_data: Dict) -> str:
        """Predict best time to contact customer"""
        time_patterns = engagement_data.get('time_patterns', {})
        if time_patterns:
            return max(time_patterns.items(), key=lambda x: x[1])[0]
        return '14:00'  # Default afternoon
    
    def _rank_offers_by_effectiveness(self, offers: List[Dict], profile: Dict) -> List[Dict]:
        """Rank offers by predicted effectiveness for this specific customer"""
        for offer in offers:
            # Adjust effectiveness based on customer characteristics
            base_effectiveness = offer.get('predicted_effectiveness', 0.5)
            
            # Adjust for price sensitivity
            price_sensitivity = profile['preference_profile'].get('price_sensitivity', 0.5)
            if 'discount' in offer.get('offer_text', '').lower():
                base_effectiveness *= (1 + price_sensitivity * 0.3)
            
            # Adjust for personalization level
            personalization_bonus = {
                'high': 0.2,
                'medium': 0.1,
                'low': 0.0
            }
            base_effectiveness += personalization_bonus.get(offer.get('personalization_level', 'low'), 0)
            
            offer['final_effectiveness_score'] = min(base_effectiveness, 1.0)
        
        return sorted(offers, key=lambda x: x['final_effectiveness_score'], reverse=True)
    
    # Helper methods for advanced personalization
    def _categorize_age(self, age: int) -> str:
        if age < 25: return 'young_adult'
        elif age < 35: return 'adult' 
        elif age < 50: return 'middle_aged'
        elif age < 65: return 'mature'
        else: return 'senior'
    
    def _infer_life_stage(self, customer_data: Dict) -> str:
        age = customer_data.get('age', 0)
        spending = customer_data.get('avg_spending', 0)
        
        if age < 30 and spending < 1000:
            return 'student'
        elif 25 <= age <= 35 and spending > 2000:
            return 'young_professional'
        elif 30 <= age <= 50 and spending > 3000:
            return 'established_family'
        elif age > 50 and spending > 2500:
            return 'mature_affluent'
        else:
            return 'general'
    
    def _calculate_price_sensitivity(self, customer_data: Dict) -> float:
        # Higher rating with lower spending = price sensitive
        rating = customer_data.get('rating_id', 3)
        spending = customer_data.get('avg_spending', 1000)
        
        if rating >= 4 and spending < 1500:
            return 0.8  # High price sensitivity
        elif rating >= 3 and spending < 2000:
            return 0.6  # Medium price sensitivity
        else:
            return 0.3  # Low price sensitivity
    
    def _find_similar_customers(self, profile: Dict) -> List[str]:
        # Simplified - would use actual similarity calculation
        return ['similar_customer_1', 'similar_customer_2', 'similar_customer_3']
    
    def _get_popular_items_among_similar(self, similar_customers: List[str]) -> List[str]:
        # Would query actual popular items
        return ['Premium Skincare Set', 'Designer Handbag', 'Gourmet Food Selection']

# Global instance
hyper_personalization_engine = HyperPersonalizationEngine()
