"""
Generative Analytics Engine - LLM-powered insights for all analytics components
"""
import json
import logging
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests

logger = logging.getLogger(__name__)

class GenerativeAnalyticsEngine:
    """
    LLM-powered analytics engine that generates contextual insights,
    recommendations, and predictions for all CRM components
    """
    
    def __init__(self):
        self.ollama_available = self._check_ollama()
        self.model_name = "llama3.2:3b"
        self.enabled = self.ollama_available
        
        if not self.enabled:
            logger.warning("Local LLM not available for analytics. Using rule-based fallbacks.")
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _query_llm(self, prompt: str, temperature: float = 0.7) -> str:
        """Query local LLM"""
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': self.model_name,
                    'prompt': prompt,
                    'temperature': temperature,
                    'stream': False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')
            return ""
        except Exception as e:
            logger.error(f"LLM query failed: {e}")
            return ""
    
    def generate_dashboard_insights(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate intelligent dashboard insights using LLM"""
        
        if not self.enabled:
            return self._fallback_dashboard_insights(metrics)
        
        prompt = f"""
You are a Chinese retail analytics expert analyzing shopping mall performance data.

CURRENT METRICS:
{json.dumps(metrics, indent=2, ensure_ascii=False)}

BUSINESS CONTEXT:
- Chinese shopping mall with mixed retail, dining, and entertainment
- Customer base includes 橙卡会员, 金卡会员, 钻卡会员 tiers
- Focus on Chinese consumer behavior and market dynamics

Generate actionable insights and recommendations:

1. **Key Performance Insights** - What do the numbers tell us?
2. **Immediate Action Items** - What should be done this week?
3. **Strategic Opportunities** - Medium-term growth areas
4. **Risk Alerts** - Potential issues requiring attention
5. **Chinese Market Context** - Specific considerations for Chinese retail

Provide practical, actionable recommendations for mall management.

Respond in JSON format:
```json
{{
  "performance_insights": [...],
  "immediate_actions": [...],
  "strategic_opportunities": [...],
  "risk_alerts": [...],
  "chinese_market_factors": [...],
  "executive_summary": "...",
  "priority_level": "high/medium/low"
}}
```
"""
        
        response = self._query_llm(prompt, temperature=0.6)
        
        try:
            if '```json' in response:
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                json_text = response[json_start:json_end].strip()
            else:
                json_text = response.strip()
            
            return json.loads(json_text)
        except:
            return self._fallback_dashboard_insights(metrics)
    
    def generate_customer_insights(self, customer_data: pd.DataFrame, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Generate comprehensive customer insights using LLM"""
        
        if not self.enabled:
            return self._fallback_customer_insights(customer_data)
        
        # Analyze data patterns
        data_summary = self._summarize_customer_data(customer_data)
        
        prompt = f"""
You are an expert in Chinese customer analytics. Analyze this shopping mall customer data:

CUSTOMER DATA SUMMARY:
{json.dumps(data_summary, indent=2, ensure_ascii=False)}

ANALYSIS TYPE: {analysis_type}

CHINESE RETAIL CONTEXT:
- Shopping behaviors: Mobile payments, social commerce, group buying
- Demographics: Multi-generational shopping, family decision making
- Preferences: Experience-focused, brand conscious, value seeking
- Seasonal patterns: CNY, Golden Week, Singles Day impact

Provide insights for:

1. **Customer Behavior Patterns** - What behaviors do you observe?
2. **Demographic Insights** - Key demographic trends and segments
3. **Engagement Analysis** - Customer satisfaction and loyalty patterns
4. **Revenue Opportunities** - Ways to increase customer value
5. **Retention Strategies** - How to keep customers engaged
6. **Personalization Opportunities** - Customization possibilities
7. **Market Positioning** - Competitive advantages

Focus on actionable insights for Chinese shopping mall context.

Respond in JSON format:
```json
{{
  "behavior_patterns": [...],
  "demographic_insights": [...],
  "engagement_analysis": {{...}},
  "revenue_opportunities": [...],
  "retention_strategies": [...],
  "personalization_opportunities": [...],
  "market_positioning": [...],
  "key_findings": "...",
  "confidence_score": 0.85
}}
```
"""
        
        response = self._query_llm(prompt, temperature=0.7)
        
        try:
            if '```json' in response:
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                json_text = response[json_start:json_end].strip()
            else:
                json_text = response.strip()
            
            insights = json.loads(json_text)
            
            # Add traditional analytics as supplementary data
            insights['traditional_analytics'] = {
                'demographics': self._analyze_demographics(customer_data),
                'behavior_metrics': self._analyze_behavior_patterns(customer_data)
            }
            
            return insights
        except:
            return self._fallback_customer_insights(customer_data)
    
    def generate_campaign_recommendations(self, performance_data: Dict[str, Any], customer_segments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate intelligent campaign recommendations using LLM"""
        
        if not self.enabled:
            return self._fallback_campaign_recommendations(performance_data)
        
        prompt = f"""
You are a Chinese digital marketing expert specializing in shopping mall campaigns.

CAMPAIGN PERFORMANCE DATA:
{json.dumps(performance_data, indent=2, ensure_ascii=False)}

CUSTOMER SEGMENTS:
{json.dumps(customer_segments or {}, indent=2, ensure_ascii=False)}

CHINESE MARKETING LANDSCAPE:
- Platforms: WeChat, Douyin, Xiaohongshu, Weibo
- Shopping behaviors: Mobile-first, social commerce, live streaming
- Cultural factors: Face-saving, group dynamics, festival shopping
- Payment methods: Alipay, WeChat Pay, digital wallets

Generate campaign strategies:

1. **Platform-Specific Campaigns** - WeChat, Douyin, Xiaohongshu strategies
2. **Seasonal Campaigns** - CNY, Golden Week, Singles Day, 618
3. **Segment-Targeted Campaigns** - Campaigns for each customer segment
4. **Content Strategies** - What content resonates with Chinese consumers
5. **Influencer Collaborations** - KOL and KOC partnership opportunities
6. **Cross-selling Campaigns** - Between retail, dining, entertainment
7. **Retention Campaigns** - Membership and loyalty strategies

Focus on ROI optimization and Chinese consumer psychology.

Respond in JSON format:
```json
{{
  "platform_campaigns": {{...}},
  "seasonal_campaigns": [...],
  "segment_campaigns": {{...}},
  "content_strategies": [...],
  "influencer_opportunities": [...],
  "cross_selling_campaigns": [...],
  "retention_campaigns": [...],
  "budget_allocation": {{...}},
  "expected_roi": {{...}},
  "implementation_timeline": {{...}}
}}
```
"""
        
        response = self._query_llm(prompt, temperature=0.8)
        
        try:
            if '```json' in response:
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                json_text = response[json_start:json_end].strip()
            else:
                json_text = response.strip()
            
            return json.loads(json_text)
        except:
            return self._fallback_campaign_recommendations(performance_data)
    
    def generate_predictive_insights(self, historical_data: pd.DataFrame, prediction_horizon: int = 30) -> Dict[str, Any]:
        """Generate predictive insights using LLM analysis"""
        
        if not self.enabled:
            return self._fallback_predictive_insights(historical_data, prediction_horizon)
        
        # Analyze trends and patterns
        trends = self._analyze_trends(historical_data)
        
        prompt = f"""
You are a predictive analytics expert for Chinese retail markets.

HISTORICAL DATA TRENDS:
{json.dumps(trends, indent=2, ensure_ascii=False)}

PREDICTION HORIZON: {prediction_horizon} days

CHINESE MARKET FACTORS:
- Economic cycles and consumer spending patterns
- Seasonal shopping behaviors and festival impacts
- Digital transformation trends
- Competition from e-commerce platforms
- Demographic shifts and generational changes

Provide predictions for:

1. **Customer Behavior Trends** - How will customer behaviors evolve?
2. **Revenue Forecasts** - Expected revenue patterns and growth
3. **Churn Predictions** - Which customers are at risk?
4. **Market Opportunities** - Emerging trends and opportunities
5. **Competitive Landscape** - How competition might change
6. **Technology Impact** - How tech trends will affect business
7. **Risk Assessment** - Potential challenges and threats

Include confidence levels and specific recommendations.

Respond in JSON format:
```json
{{
  "behavior_predictions": [...],
  "revenue_forecasts": {{...}},
  "churn_predictions": {{...}},
  "market_opportunities": [...],
  "competitive_outlook": [...],
  "technology_trends": [...],
  "risk_assessment": [...],
  "confidence_levels": {{...}},
  "recommended_actions": [...],
  "prediction_accuracy": "high/medium/low"
}}
```
"""
        
        response = self._query_llm(prompt, temperature=0.6)
        
        try:
            if '```json' in response:
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                json_text = response[json_start:json_end].strip()
            else:
                json_text = response.strip()
            
            return json.loads(json_text)
        except:
            return self._fallback_predictive_insights(historical_data, prediction_horizon)
    
    def generate_traffic_insights(self, traffic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate real-time traffic insights using LLM"""
        
        if not self.enabled:
            return self._fallback_traffic_insights(traffic_data)
        
        prompt = f"""
You are a retail space optimization expert analyzing shopping mall traffic.

REAL-TIME TRAFFIC DATA:
{json.dumps(traffic_data, indent=2, ensure_ascii=False)}

CHINESE SHOPPING PATTERNS:
- Peak hours: Evenings, weekends, lunch breaks
- Group shopping behaviors and family visits
- Mobile device usage and digital interactions
- Food court and entertainment zone preferences
- Seasonal and weather impact on traffic

Analyze and provide:

1. **Traffic Optimization** - How to better manage crowd flow
2. **Zone Performance** - Which areas are performing well/poorly
3. **Capacity Management** - How to handle peak times
4. **Customer Experience** - Improvements for high-traffic periods
5. **Revenue Opportunities** - How to monetize traffic patterns
6. **Safety Considerations** - Crowd management and safety
7. **Technology Solutions** - Digital tools to improve flow

Focus on actionable operational improvements.

Respond in JSON format:
```json
{{
  "traffic_optimization": [...],
  "zone_analysis": {{...}},
  "capacity_recommendations": [...],
  "experience_improvements": [...],
  "revenue_opportunities": [...],
  "safety_measures": [...],
  "technology_solutions": [...],
  "immediate_actions": [...],
  "trend_analysis": "..."
}}
```
"""
        
        response = self._query_llm(prompt, temperature=0.7)
        
        try:
            if '```json' in response:
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                json_text = response[json_start:json_end].strip()
            else:
                json_text = response.strip()
            
            return json.loads(json_text)
        except:
            return self._fallback_traffic_insights(traffic_data)
    
    def generate_market_opportunities(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate market opportunity analysis using LLM"""
        
        if not self.enabled:
            return self._fallback_market_opportunities(business_data)
        
        prompt = f"""
You are a Chinese retail market strategist analyzing business opportunities.

CURRENT BUSINESS DATA:
{json.dumps(business_data, indent=2, ensure_ascii=False)}

CHINESE MARKET CONTEXT:
- Retail landscape: O2O integration, social commerce growth
- Consumer trends: Experience economy, sustainability focus
- Technology adoption: AI, AR/VR, IoT in retail
- Competition: Traditional malls vs e-commerce vs live commerce
- Regulations: Data privacy, consumer protection, business policies

Identify opportunities in:

1. **New Customer Segments** - Untapped demographic groups
2. **Service Expansion** - New services or experiences to offer
3. **Technology Integration** - Digital transformation opportunities
4. **Partnership Opportunities** - Strategic alliances and collaborations
5. **Revenue Diversification** - New revenue streams
6. **Market Expansion** - Geographic or demographic expansion
7. **Competitive Advantages** - Areas to differentiate from competitors

Provide specific, actionable recommendations with timelines.

Respond in JSON format:
```json
{{
  "new_segments": [...],
  "service_expansion": [...],
  "technology_integration": [...],
  "partnerships": [...],
  "revenue_streams": [...],
  "market_expansion": [...],
  "competitive_advantages": [...],
  "implementation_roadmap": {{...}},
  "investment_requirements": {{...}},
  "expected_returns": {{...}}
}}
```
"""
        
        response = self._query_llm(prompt, temperature=0.8)
        
        try:
            if '```json' in response:
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                json_text = response[json_start:json_end].strip()
            else:
                json_text = response.strip()
            
            return json.loads(json_text)
        except:
            return self._fallback_market_opportunities(business_data)
    
    # Helper methods for data analysis
    def _summarize_customer_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Summarize customer data for LLM analysis"""
        summary = {
            'total_customers': len(df),
            'demographics': {},
            'behavior_patterns': {},
            'engagement_metrics': {}
        }
        
        if 'age' in df.columns:
            summary['demographics']['age_stats'] = {
                'mean': float(df['age'].mean()),
                'std': float(df['age'].std()),
                'min': int(df['age'].min()),
                'max': int(df['age'].max())
            }
        
        if 'gender' in df.columns:
            summary['demographics']['gender_dist'] = df['gender'].value_counts().to_dict()
        
        if 'rating_id' in df.columns:
            summary['engagement_metrics']['avg_rating'] = float(df['rating_id'].mean())
            summary['engagement_metrics']['rating_dist'] = df['rating_id'].value_counts().to_dict()
        
        if 'segment_id' in df.columns:
            summary['behavior_patterns']['segment_dist'] = df['segment_id'].value_counts().to_dict()
        
        return summary
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze trends in historical data"""
        trends = {
            'customer_growth': {},
            'engagement_trends': {},
            'seasonal_patterns': {}
        }
        
        if 'created_at' in df.columns:
            df['month'] = pd.to_datetime(df['created_at']).dt.month
            monthly_counts = df.groupby('month').size().to_dict()
            trends['seasonal_patterns']['monthly_registration'] = monthly_counts
        
        if 'rating_id' in df.columns:
            trends['engagement_trends']['avg_rating_over_time'] = float(df['rating_id'].mean())
        
        return trends
    
    def _analyze_demographics(self, df: pd.DataFrame) -> Dict:
        """Traditional demographic analysis"""
        return {
            "age_distribution": {
                "mean": float(df['age'].mean()) if 'age' in df.columns else 0,
                "median": float(df['age'].median()) if 'age' in df.columns else 0,
                "std": float(df['age'].std()) if 'age' in df.columns else 0
            },
            "gender_distribution": df['gender'].value_counts().to_dict() if 'gender' in df.columns else {},
            "rating_distribution": df['rating_id'].value_counts().to_dict() if 'rating_id' in df.columns else {}
        }
    
    def _analyze_behavior_patterns(self, df: pd.DataFrame) -> Dict:
        """Traditional behavior analysis"""
        return {
            "engagement_levels": {
                "high_engagement": len(df[df['rating_id'] >= 4]) if 'rating_id' in df.columns else 0,
                "medium_engagement": len(df[df['rating_id'] == 3]) if 'rating_id' in df.columns else 0,
                "low_engagement": len(df[df['rating_id'] <= 2]) if 'rating_id' in df.columns else 0
            }
        }
    
    # Fallback methods when LLM is unavailable
    def _fallback_dashboard_insights(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback dashboard insights"""
        return {
            "performance_insights": [
                "Customer growth rate analysis needed",
                "Campaign performance monitoring recommended"
            ],
            "immediate_actions": [
                "Review customer acquisition strategies",
                "Optimize marketing spend allocation"
            ],
            "strategic_opportunities": [
                "Expand customer segmentation",
                "Implement loyalty programs"
            ],
            "executive_summary": "Basic performance metrics available, recommend LLM setup for advanced insights",
            "llm_available": False
        }
    
    def _fallback_customer_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Fallback customer insights"""
        return {
            "behavior_patterns": ["Standard demographic analysis available"],
            "revenue_opportunities": ["Upselling to high-value customers", "Retention campaign implementation"],
            "key_findings": "Basic customer analysis completed, enhanced insights require LLM",
            "traditional_analytics": {
                'demographics': self._analyze_demographics(df),
                'behavior_metrics': self._analyze_behavior_patterns(df)
            },
            "llm_available": False
        }
    
    def _fallback_campaign_recommendations(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback campaign recommendations"""
        return {
            "platform_campaigns": {"wechat": ["Basic social media engagement"], "douyin": ["Short video content"]},
            "seasonal_campaigns": ["Chinese New Year promotion", "Golden Week special offers"],
            "expected_roi": {"estimated_improvement": "10-15%"},
            "llm_available": False
        }
    
    def _fallback_predictive_insights(self, df: pd.DataFrame, horizon: int) -> Dict[str, Any]:
        """Fallback predictive insights"""
        return {
            "behavior_predictions": ["Customer engagement expected to remain stable"],
            "revenue_forecasts": {"growth_rate": "5-10% estimated"},
            "prediction_accuracy": "medium",
            "recommended_actions": ["Implement customer retention programs", "Monitor engagement metrics"],
            "llm_available": False
        }
    
    def _fallback_traffic_insights(self, traffic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback traffic insights"""
        return {
            "traffic_optimization": ["Monitor peak hours", "Optimize staff allocation"],
            "immediate_actions": ["Review crowd management procedures"],
            "trend_analysis": "Basic traffic patterns identified",
            "llm_available": False
        }
    
    def _fallback_market_opportunities(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback market opportunities"""
        return {
            "new_segments": ["Young professionals", "Family shoppers"],
            "technology_integration": ["Mobile app development", "Digital payment systems"],
            "expected_returns": {"timeline": "6-12 months", "roi": "15-25%"},
            "llm_available": False
        }

# Global instance for use across the application
generative_analytics = GenerativeAnalyticsEngine()