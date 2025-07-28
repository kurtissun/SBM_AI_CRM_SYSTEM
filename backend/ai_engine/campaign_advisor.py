#!/usr/bin/env python3
"""
AI-Powered Marketing Campaign Advisor
Analyzes customer database to provide intelligent campaign guidance
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import text

from core.database import get_db
from ai_engine.local_llm_segmentation import LocalLLMSegmentation

logger = logging.getLogger(__name__)

class CampaignAdvisor:
    """
    AI-powered marketing campaign advisor that analyzes customer data 
    to provide intelligent recommendations for Super Brand Mall Shanghai
    """
    
    def __init__(self):
        self.llm_engine = LocalLLMSegmentation()
        self.super_brand_mall_tenants = [
            # Luxury & Fashion
            "Hermès", "Louis Vuitton", "Chanel", "Dior", "Gucci", "Prada", "Cartier", 
            "Tiffany & Co", "Van Cleef & Arpels", "Bulgari", "Rolex", "Patek Philippe",
            
            # Mid-tier Fashion
            "Coach", "Michael Kors", "Kate Spade", "Tommy Hilfiger", "Hugo Boss",
            "Burberry", "Ralph Lauren", "CK Calvin Klein",
            
            # Fast Fashion & Casual
            "ZARA", "H&M", "Uniqlo", "MUJI", "Pull & Bear", "Massimo Dutti",
            
            # Chinese Traditional Jewelry
            "老凤祥", "周大福", "周生生", "六福珠宝", "潮宏基", "周六福",
            
            # Food & Beverage - Tea Culture
            "喜茶", "奈雪的茶", "蜜雪冰城", "茶百道", "书亦烧仙草", "一点点",
            
            # Food & Beverage - Dining
            "海底捞", "呷哺呷哺", "小龙坎", "大龙燚", "谭鸭血", "Din Tai Fung",
            "Starbucks", "KFC", "McDonald's", "Pizza Hut", "Burger King",
            
            # Entertainment
            "剧本杀", "密室逃脱", "KTV", "电玩城", "网咖", "桌游吧", "轰趴馆",
            "真人CS", "VR体验馆", "保龄球", "电影院", "溜冰场",
            
            # Department Stores & Supermarkets
            "Ole' 精品超市", "City Shop", "BHG", "太平洋百货", "第六百货",
            
            # Beauty & Cosmetics
            "Sephora", "丝芙兰", "屈臣氏", "万宁", "娇韵诗", "兰蔻", "雅诗兰黛"
        ]
    
    def analyze_campaign_opportunity(self, 
                                   prompt: str, 
                                   target_segment: Optional[str] = None,
                                   campaign_type: Optional[str] = None,
                                   budget_range: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze campaign opportunities based on customer database and user prompt
        """
        logger.info(f"🎯 Analyzing campaign opportunity: {prompt[:100]}...")
        
        try:
            # Get customer data insights
            customer_insights = self._analyze_customer_database()
            
            # Get segment-specific analysis if requested
            segment_analysis = None
            if target_segment:
                segment_analysis = self._analyze_segment_behavior(target_segment)
            
            # Generate LLM-powered recommendations regardless of database errors
            recommendations = self._generate_campaign_recommendations(
                prompt, customer_insights, segment_analysis, campaign_type, budget_range
            )
            
            return {
                'campaign_analysis': recommendations,
                'customer_insights': customer_insights,
                'segment_analysis': segment_analysis,
                'super_brand_mall_context': self._get_mall_context(),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Campaign analysis failed: {e}")
            return {
                'error': str(e),
                'fallback_recommendations': self._generate_fallback_recommendations(prompt)
            }
    
    def _analyze_customer_database(self) -> Dict[str, Any]:
        """Analyze current customer database for insights"""
        try:
            db = next(get_db())
            # Get customer demographics
            customer_stats = db.execute(text("""
                SELECT 
                    COUNT(*) as total_customers,
                    AVG(CASE WHEN birthday IS NOT NULL 
                        THEN (julianday('now') - julianday(birthday)) / 365.25 
                        ELSE NULL END) as avg_age,
                    COUNT(CASE WHEN gender = '男' THEN 1 END) as male_count,
                    COUNT(CASE WHEN gender = '女' THEN 1 END) as female_count,
                    COUNT(DISTINCT location) as cities_covered
                FROM customers 
                WHERE created_at > datetime('now', '-30 days')
            """)).fetchone()
            
            # Get spending patterns
            spending_stats = db.execute(text("""
                SELECT 
                    AVG(purchase_amount) as avg_spending,
                    MAX(purchase_amount) as max_spending,
                    MIN(purchase_amount) as min_spending,
                    COUNT(DISTINCT business_type) as business_types,
                    COUNT(DISTINCT store_name) as unique_stores
                FROM customer_purchases cp
                JOIN customers c ON cp.customer_id = c.id
                WHERE cp.purchase_date > datetime('now', '-30 days')
            """)).fetchone()
            
            # Get top stores and business types
            top_stores = db.execute(text("""
                SELECT store_name, COUNT(*) as visit_count
                FROM customer_purchases 
                WHERE purchase_date > datetime('now', '-30 days')
                GROUP BY store_name 
                ORDER BY visit_count DESC 
                LIMIT 10
            """)).fetchall()
            
            top_business_types = db.execute(text("""
                SELECT business_type, COUNT(*) as transaction_count,
                       AVG(purchase_amount) as avg_amount
                FROM customer_purchases 
                WHERE purchase_date > datetime('now', '-30 days')
                GROUP BY business_type 
                ORDER BY transaction_count DESC
            """)).fetchall()
            
            # Get membership distribution
            membership_stats = db.execute(text("""
                SELECT membership_level, COUNT(*) as count
                FROM customers 
                WHERE created_at > datetime('now', '-30 days')
                GROUP BY membership_level 
                ORDER BY count DESC
            """)).fetchall()
            
            return {
                'customer_demographics': {
                    'total_customers': customer_stats.total_customers if customer_stats else 0,
                    'average_age': round(customer_stats.avg_age, 1) if customer_stats and customer_stats.avg_age else 30,
                    'male_count': customer_stats.male_count if customer_stats else 0,
                    'female_count': customer_stats.female_count if customer_stats else 0,
                    'cities_covered': customer_stats.cities_covered if customer_stats else 0
                },
                'spending_patterns': {
                    'average_spending': round(spending_stats.avg_spending, 2) if spending_stats and spending_stats.avg_spending else 0,
                    'max_spending': spending_stats.max_spending if spending_stats else 0,
                    'min_spending': spending_stats.min_spending if spending_stats else 0,
                    'business_types_count': spending_stats.business_types if spending_stats else 0,
                    'unique_stores': spending_stats.unique_stores if spending_stats else 0
                },
                'top_stores': [{'name': store.store_name, 'visits': store.visit_count} 
                             for store in top_stores] if top_stores else [],
                'business_type_performance': [
                    {
                        'type': bt.business_type, 
                        'transactions': bt.transaction_count,
                        'avg_amount': round(bt.avg_amount, 2)
                    } for bt in top_business_types
                ] if top_business_types else [],
                'membership_distribution': [
                    {'level': ms.membership_level, 'count': ms.count} 
                    for ms in membership_stats
                ] if membership_stats else []
            }
            
        except Exception as e:
            logger.error(f"Database analysis failed: {e}")
            return {'error': str(e), 'analysis_date': datetime.now().isoformat()}
    
    def _analyze_segment_behavior(self, segment_name: str) -> Dict[str, Any]:
        """Analyze specific customer segment behavior"""
        try:
            db = next(get_db())
            # Get segment customers
            segment_customers = db.execute(text("""
                SELECT c.*, s.name as segment_name
                FROM customers c
            JOIN customer_segments cs ON c.id = cs.customer_id
                JOIN segments s ON cs.segment_id = s.id
                WHERE s.name LIKE :segment_name OR s.id = :segment_id
            """), {'segment_name': f'%{segment_name}%', 'segment_id': segment_name}).fetchall()
            
            if not segment_customers:
                return {'error': 'Segment not found or no customers in segment'}
            
            # Analyze segment spending patterns
            customer_ids = [str(c.id) for c in segment_customers]
            
            segment_purchases = db.execute(text(f"""
                SELECT 
                    AVG(purchase_amount) as avg_spending,
                    COUNT(*) as total_purchases,
                    COUNT(DISTINCT store_name) as unique_stores_visited,
                    COUNT(DISTINCT business_type) as business_types_engaged,
                    business_type,
                    store_name
                FROM customer_purchases 
                WHERE customer_id IN ({','.join(customer_ids)})
                AND purchase_date > datetime('now', '-30 days')
                GROUP BY business_type, store_name
                ORDER BY COUNT(*) DESC
            """)).fetchall()
            
            return {
                'segment_size': len(segment_customers),
                'avg_age': sum([self._calculate_age(c.birthday) for c in segment_customers if c.birthday]) / len(segment_customers),
                'gender_split': {
                    'male': len([c for c in segment_customers if c.gender == '男']),
                    'female': len([c for c in segment_customers if c.gender == '女'])
                },
                'preferred_stores': [
                    {'store': p.store_name, 'business_type': p.business_type}
                    for p in segment_purchases[:10]
                ] if segment_purchases else [],
                'spending_behavior': {
                    'avg_amount': round(segment_purchases[0].avg_spending, 2) if segment_purchases and segment_purchases[0].avg_spending else 0,
                    'total_purchases': sum([p.total_purchases for p in segment_purchases]) if segment_purchases else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Segment analysis failed: {e}")
            return {'error': str(e)}
    
    def _calculate_age(self, birthday_str: str) -> int:
        """Calculate age from birthday string"""
        try:
            from datetime import datetime
            birthday = datetime.strptime(birthday_str, '%Y-%m-%d')
            return int((datetime.now() - birthday).days / 365.25)
        except:
            return 30  # Default age
    
    def _generate_campaign_recommendations(self, 
                                         prompt: str,
                                         customer_insights: Dict[str, Any],
                                         segment_analysis: Optional[Dict[str, Any]],
                                         campaign_type: Optional[str],
                                         budget_range: Optional[str]) -> Dict[str, Any]:
        """Generate LLM-powered campaign recommendations"""
        
        # Prepare context for LLM
        context_data = {
            'user_prompt': prompt,
            'customer_insights': customer_insights,
            'segment_analysis': segment_analysis,
            'campaign_type': campaign_type,
            'budget_range': budget_range,
            'mall_tenants': self.super_brand_mall_tenants[:20]  # Sample tenants
        }
        
        llm_prompt = f"""
You are an expert marketing strategist for Super Brand Mall Shanghai, one of China's premier luxury shopping destinations. 

CAMPAIGN REQUEST:
{prompt}

CURRENT CUSTOMER DATABASE INSIGHTS:
{json.dumps(customer_insights, indent=2, ensure_ascii=False)}

SEGMENT ANALYSIS:
{json.dumps(segment_analysis, indent=2, ensure_ascii=False) if segment_analysis else "No specific segment analysis"}

CAMPAIGN TYPE: {campaign_type or "Not specified"}
BUDGET RANGE: {budget_range or "Not specified"}

SUPER BRAND MALL SHANGHAI CONTEXT:
- Location: Premium shopping district in Shanghai
- Target: Affluent Chinese consumers and international visitors
- Tenants: {', '.join(self.super_brand_mall_tenants[:15])}...

Based on this data, provide a comprehensive marketing campaign strategy with:

1. **Campaign Overview**
   - Campaign name and theme
   - Target audience definition
   - Key objectives

2. **Audience Targeting**
   - Primary target segments (based on data)
   - Secondary audiences
   - Demographic insights

3. **Store & Business Partnerships**
   - Which Super Brand Mall tenants to partner with
   - Why these partnerships make sense
   - Collaboration opportunities

4. **Campaign Tactics**
   - Specific marketing activities
   - Channel mix (online/offline)
   - Timeline recommendations

5. **Budget Allocation**
   - Recommended spend distribution
   - ROI expectations
   - Performance metrics to track

6. **Implementation Guidance**
   - Step-by-step action items
   - Resource requirements
   - Success indicators

Focus on actionable, data-driven recommendations that leverage the customer insights and Super Brand Mall's unique positioning.

Respond in valid JSON format with clear sections and bullet points.
"""
        
        try:
            llm_response = self.llm_engine._query_local_llm(llm_prompt, temperature=0.7)
            
            # Parse LLM response
            if llm_response and '```json' in llm_response:
                json_start = llm_response.find('```json') + 7
                json_end = llm_response.find('```', json_start)
                json_text = llm_response[json_start:json_end].strip()
                return json.loads(json_text)
            else:
                # Fallback parsing
                return self._parse_llm_response_fallback(llm_response)
                
        except Exception as e:
            logger.error(f"LLM campaign generation failed: {e}")
            return self._generate_fallback_recommendations(prompt)
    
    def _parse_llm_response_fallback(self, response: str) -> Dict[str, Any]:
        """Parse LLM response when JSON format fails"""
        return {
            'campaign_overview': {
                'name': 'Data-Driven Customer Engagement Campaign',
                'theme': 'Personalized luxury shopping experience',
                'objectives': ['Increase customer engagement', 'Drive premium purchases', 'Build brand loyalty']
            },
            'audience_targeting': {
                'primary_segments': ['High-value customers', 'Luxury shoppers', 'Experience seekers'],
                'demographics': 'Affluent professionals aged 25-45 in major Chinese cities'
            },
            'recommended_partnerships': [
                'Hermès - Ultra-luxury positioning',
                'Chanel - Premium beauty and fashion',
                '喜茶 - Trendy lifestyle experiences',
                'KTV - Entertainment and social experiences'
            ],
            'campaign_tactics': [
                'VIP exclusive events',
                'Social media influencer partnerships',
                'Cross-brand loyalty programs',
                'Experiential marketing activations'
            ],
            'budget_allocation': {
                'digital_marketing': '40%',
                'events_experiences': '35%',
                'partnerships': '25%'
            },
            'implementation_steps': [
                'Analyze customer segment preferences',
                'Partner with top-performing stores',
                'Create exclusive offers and experiences',
                'Launch integrated marketing campaign',
                'Track performance and optimize'
            ],
            'raw_response': response[:500] + '...' if response and len(response) > 500 else response
        }
    
    def _generate_fallback_recommendations(self, prompt: str) -> Dict[str, Any]:
        """Generate basic recommendations when LLM fails"""
        return {
            'campaign_overview': {
                'name': f'Targeted Campaign: {prompt[:50]}...',
                'theme': 'Customer-centric marketing approach',
                'objectives': [
                    'Increase customer engagement based on data insights',
                    'Drive targeted traffic to underperforming stores',
                    'Enhance customer lifetime value'
                ]
            },
            'audience_targeting': {
                'primary_segments': ['High-spending customers', 'Frequent visitors', 'Brand loyalists'],
                'targeting_rationale': 'Based on customer database analysis'
            },
            'recommended_partnerships': [
                'Top-performing stores from data analysis',
                'Complementary business types',
                'Emerging brands with growth potential'
            ],
            'campaign_tactics': [
                'Personalized offers based on purchase history',
                'Cross-store promotions',
                'Membership tier benefits',
                'Social media engagement campaigns'
            ],
            'success_metrics': [
                'Increase in average transaction value',
                'Customer retention rate improvement',
                'Cross-store visit frequency',
                'Campaign ROI measurement'
            ],
            'note': 'Fallback recommendations - LLM analysis unavailable'
        }
    
    def _get_mall_context(self) -> Dict[str, Any]:
        """Get Super Brand Mall Shanghai context"""
        return {
            'location': 'Super Brand Mall Shanghai',
            'positioning': 'Premium luxury shopping destination',
            'key_features': [
                'Located in Pudong Lujiazui financial district',
                'Over 13 floors of premium retail space',
                'Mix of international luxury and local premium brands',
                'High-end dining and entertainment options',
                'Attracts affluent local and international shoppers'
            ],
            'tenant_categories': {
                'luxury_fashion': ['Hermès', 'Louis Vuitton', 'Chanel', 'Dior'],
                'jewelry_watches': ['Cartier', 'Tiffany & Co', 'Rolex', '老凤祥'],
                'lifestyle_dining': ['喜茶', '海底捞', 'Din Tai Fung', 'Starbucks'],
                'entertainment': ['KTV', '剧本杀', '电影院', 'VR体验馆'],
                'beauty_cosmetics': ['Sephora', '丝芙兰', 'SK-II', '兰蔻']
            },
            'target_demographics': [
                'Affluent professionals aged 25-50',
                'International expatriates in Shanghai',
                'Luxury-conscious Chinese consumers',
                'Experience-seeking millennials and Gen Z'
            ]
        }

    def get_campaign_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get pre-built campaign templates for common scenarios"""
        return {
            'luxury_brand_launch': {
                'name': 'Premium Brand Launch Campaign',
                'description': 'Launch campaign for new luxury brand entering Super Brand Mall',
                'target_segments': ['luxury_collectors', 'brand_enthusiasts'],
                'recommended_budget': '500,000 - 1,000,000 RMB',
                'duration': '3 months',
                'key_tactics': [
                    'VIP preview events',
                    'Influencer partnerships',
                    'Exclusive member benefits',
                    'Cross-brand collaborations'
                ]
            },
            'seasonal_promotion': {
                'name': 'Chinese New Year Shopping Festival',
                'description': 'Traditional holiday shopping campaign',
                'target_segments': ['family_oriented', 'gift_purchasers'],
                'recommended_budget': '200,000 - 500,000 RMB',
                'duration': '6 weeks',
                'key_tactics': [
                    'Lucky draw promotions',
                    'Family package deals',
                    'Traditional cultural experiences',
                    'Gift wrapping services'
                ]
            },
            'youth_engagement': {
                'name': 'Gen Z Experience Campaign',
                'description': 'Engage younger demographics with experiential marketing',
                'target_segments': ['young_tech_savvy', 'social_media_active'],
                'recommended_budget': '100,000 - 300,000 RMB',
                'duration': '2 months',
                'key_tactics': [
                    'Social media challenges',
                    'Pop-up experiences',
                    'Gaming partnerships',
                    'Live streaming events'
                ]
            }
        }