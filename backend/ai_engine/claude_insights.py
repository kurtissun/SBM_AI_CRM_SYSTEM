"""
Claude LLM Integration for Generative Customer Insights
"""
import json
import logging
from typing import Dict, List, Any, Optional
import anthropic
from core.config import settings

logger = logging.getLogger(__name__)

class ClaudeInsightGenerator:
    """
    Integrates Claude LLM for generative customer insights and analysis
    """
    
    def __init__(self):
        self.client = None
        if hasattr(settings, 'CLAUDE_API_KEY') and settings.CLAUDE_API_KEY:
            self.client = anthropic.Anthropic(api_key=settings.CLAUDE_API_KEY)
            self.enabled = True
        else:
            self.enabled = False
            logger.warning("Claude API key not found. Generative insights disabled.")
    
    def generate_segment_insights(self, cluster_data: Dict, business_context: Dict = None) -> Dict:
        """
        Generate comprehensive, contextual insights using Claude LLM
        """
        if not self.enabled:
            return self._fallback_insights(cluster_data)
        
        try:
            prompt = self._build_analysis_prompt(cluster_data, business_context)
            
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4000,
                temperature=0.7,
                messages=[{
                    "role": "user", 
                    "content": prompt
                }]
            )
            
            # Parse Claude's response into structured insights
            insights = self._parse_claude_response(response.content[0].text)
            return insights
            
        except Exception as e:
            logger.error(f"Claude insight generation failed: {e}")
            return self._fallback_insights(cluster_data)
    
    def _build_analysis_prompt(self, cluster_data: Dict, business_context: Dict = None) -> str:
        """
        Build comprehensive prompt for Claude analysis
        """
        cluster_profiles = cluster_data.get('cluster_profiles', {})
        insights = cluster_data.get('insights', {})
        
        # Build context about the business
        context = business_context or {
            'business_type': 'Shopping Mall / Retail Complex',
            'location': 'China (Major Cities: Beijing, Shanghai, Guangzhou, Shenzhen, Chengdu)',
            'customer_base': 'Mixed demographics with Chinese shopping preferences'
        }
        
        prompt = f"""
You are an expert customer analytics consultant analyzing shopping mall customer data in China. 

BUSINESS CONTEXT:
- Type: {context.get('business_type', 'Retail Complex')}
- Location: {context.get('location', 'China')}
- Customer Base: {context.get('customer_base', 'Mixed demographics')}

CUSTOMER SEGMENTATION DATA:
{json.dumps(cluster_profiles, indent=2, ensure_ascii=False)}

CURRENT INSIGHTS:
{json.dumps(insights, indent=2, ensure_ascii=False)}

STORE LOCATIONS: Real Chinese shopping destinations including:
- 万达广场, 国贸商城, 三里屯 (Beijing)
- 外滩茶餐厅, 南京路步行街, 陆家嘴金融城 (Shanghai) 
- 正佳广场, 天河城, 珠江新城美食坊 (Guangzhou)
- 华强北商城, 海岸城, 世界之窗 (Shenzhen)
- 春熙路火锅城, 太古里, 宽窄巷子 (Chengdu)

Please provide a comprehensive analysis with the following structure:

1. **EXECUTIVE SUMMARY** (Chinese market context)
   - Key findings about customer segments
   - Strategic priorities for Chinese retail market
   - Revenue opportunities

2. **SEGMENT-SPECIFIC INSIGHTS** (for each cluster)
   - Demographic profile interpretation
   - Shopping behavior patterns typical in Chinese malls
   - Cultural preferences and motivations
   - Specific store location preferences
   - Membership level significance (橙卡会员, 金卡会员, 钻卡会员)

3. **MARKETING STRATEGIES** (China-specific)
   - WeChat/Alipay integration opportunities
   - Chinese social media campaigns (Xiaohongshu, Douyin)
   - Festival/holiday marketing (CNY, Golden Week, Singles Day)
   - Local partnership recommendations

4. **OPERATIONAL RECOMMENDATIONS**
   - Store layout optimization for each segment
   - Service customization for Chinese customer expectations
   - Technology integration (mobile payments, mini-programs)

5. **REVENUE OPTIMIZATION**
   - Cross-selling opportunities between business types (零售, 餐饮, 娱乐)
   - Premium service strategies for different membership tiers
   - Location-specific promotions

6. **RISK ASSESSMENT & MITIGATION**
   - Competition from online platforms (Tmall, JD.com)
   - Economic sensitivity analysis
   - Customer retention strategies

Provide actionable, culturally-aware insights that consider Chinese consumer behavior, shopping preferences, and market dynamics. Focus on practical implementation strategies.

Respond in JSON format with clear sections and actionable recommendations.
"""
        return prompt
    
    def _parse_claude_response(self, response_text: str) -> Dict:
        """
        Parse Claude's response into structured insights
        """
        try:
            # Try to extract JSON from Claude's response
            if '```json' in response_text:
                json_start = response_text.find('```json') + 7
                json_end = response_text.find('```', json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                # If no JSON markers, try to parse the whole response
                json_text = response_text.strip()
            
            parsed_insights = json.loads(json_text)
            return parsed_insights
            
        except json.JSONDecodeError:
            # If JSON parsing fails, create structured insights from text
            return self._structure_text_response(response_text)
    
    def _structure_text_response(self, text: str) -> Dict:
        """
        Convert text response to structured format
        """
        sections = text.split('\n\n')
        
        structured_insights = {
            'executive_summary': {
                'key_findings': [],
                'strategic_priorities': [],
                'revenue_opportunities': []
            },
            'segment_insights': {},
            'marketing_strategies': {
                'digital_integration': [],
                'social_media': [],
                'seasonal_campaigns': [],
                'partnerships': []
            },
            'operational_recommendations': {
                'store_optimization': [],
                'service_customization': [],
                'technology_integration': []
            },
            'revenue_optimization': {
                'cross_selling': [],
                'premium_services': [],
                'location_strategies': []
            },
            'risk_assessment': {
                'competitive_threats': [],
                'mitigation_strategies': []
            },
            'claude_raw_analysis': text  # Keep full text for reference
        }
        
        # Extract key points from text sections
        for section in sections:
            if any(keyword in section.lower() for keyword in ['summary', 'findings', 'priorities']):
                structured_insights['executive_summary']['key_findings'].append(section.strip())
            elif any(keyword in section.lower() for keyword in ['marketing', 'wechat', 'social']):
                structured_insights['marketing_strategies']['digital_integration'].append(section.strip())
            elif any(keyword in section.lower() for keyword in ['operational', 'store', 'service']):
                structured_insights['operational_recommendations']['store_optimization'].append(section.strip())
        
        return structured_insights
    
    def _fallback_insights(self, cluster_data: Dict) -> Dict:
        """
        Fallback insights when Claude is not available
        """
        return {
            'source': 'fallback_system',
            'note': 'Claude LLM not available. Using rule-based insights.',
            'basic_insights': cluster_data.get('insights', {}),
            'recommendations': [
                'Implement customer segmentation campaigns',
                'Focus on high-value customer retention',
                'Optimize marketing spend across segments'
            ]
        }
    
    def analyze_customer_journey(self, customer_data: Dict, segment_id: int) -> Dict:
        """
        Generate customer journey analysis using Claude
        """
        if not self.enabled:
            return {'error': 'Claude LLM not available'}
        
        prompt = f"""
Analyze the customer journey for this specific customer segment in a Chinese shopping mall context:

CUSTOMER SEGMENT DATA:
{json.dumps(customer_data, indent=2, ensure_ascii=False)}

SEGMENT ID: {segment_id}

Please provide:
1. **Customer Journey Mapping** - from awareness to purchase to loyalty
2. **Touchpoint Analysis** - key interaction points in Chinese retail
3. **Pain Points** - common frustrations for this segment
4. **Optimization Opportunities** - specific improvements
5. **Technology Integration** - WeChat, Alipay, mini-programs usage
6. **Cultural Considerations** - Chinese shopping behaviors and preferences

Provide practical, actionable insights for improving the customer experience.
"""
        
        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                temperature=0.6,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                'customer_journey_analysis': response.content[0].text,
                'segment_id': segment_id,
                'analysis_type': 'customer_journey'
            }
            
        except Exception as e:
            logger.error(f"Customer journey analysis failed: {e}")
            return {'error': f'Analysis failed: {str(e)}'}
    
    def generate_campaign_recommendations(self, segments_data: Dict, campaign_objectives: List[str]) -> Dict:
        """
        Generate specific campaign recommendations using Claude
        """
        if not self.enabled:
            return {'error': 'Claude LLM not available'}
        
        prompt = f"""
Create specific marketing campaign recommendations for Chinese shopping mall customer segments:

SEGMENT DATA:
{json.dumps(segments_data, indent=2, ensure_ascii=False)}

CAMPAIGN OBJECTIVES:
{', '.join(campaign_objectives)}

For each segment, provide:
1. **Campaign Theme** - culturally relevant themes for Chinese market
2. **Channel Strategy** - WeChat, Douyin, Xiaohongshu, offline
3. **Timing & Seasonality** - Chinese festivals, shopping seasons
4. **Creative Direction** - visual and messaging guidelines
5. **Budget Allocation** - recommended spend distribution
6. **Success Metrics** - KPIs specific to Chinese market
7. **Localization** - city-specific adaptations

Consider Chinese consumer behavior, mobile-first approach, and social commerce trends.
"""
        
        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=3000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                'campaign_recommendations': response.content[0].text,
                'objectives': campaign_objectives,
                'analysis_type': 'campaign_strategy'
            }
            
        except Exception as e:
            logger.error(f"Campaign recommendations failed: {e}")
            return {'error': f'Campaign generation failed: {str(e)}'}
    
    def predict_segment_trends(self, historical_data: Dict, forecast_period: str = "6_months") -> Dict:
        """
        Predict segment evolution and trends using Claude
        """
        if not self.enabled:
            return {'error': 'Claude LLM not available'}
        
        prompt = f"""
Analyze historical customer segment data and predict future trends for Chinese retail market:

HISTORICAL DATA:
{json.dumps(historical_data, indent=2, ensure_ascii=False)}

FORECAST PERIOD: {forecast_period}

Provide predictions for:
1. **Segment Growth Trends** - which segments will grow/decline
2. **Behavioral Evolution** - how customer preferences will change
3. **Market Dynamics** - impact of economic, social, technological changes
4. **New Segment Emergence** - potential new customer types
5. **Revenue Implications** - financial impact of trends
6. **Strategic Adaptations** - how to prepare for changes

Consider Chinese market dynamics:
- Digital transformation acceleration
- Generation Z shopping behaviors
- Post-pandemic retail trends
- Economic policy impacts
- Technology adoption patterns

Provide actionable strategic recommendations based on predictions.
"""
        
        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2500,
                temperature=0.6,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                'trend_predictions': response.content[0].text,
                'forecast_period': forecast_period,
                'analysis_type': 'trend_prediction'
            }
            
        except Exception as e:
            logger.error(f"Trend prediction failed: {e}")
            return {'error': f'Trend prediction failed: {str(e)}'}

# Integration point for existing insight generator
def enhance_insights_with_claude(insights: Dict, cluster_data: Dict, business_context: Dict = None) -> Dict:
    """
    Enhance existing insights with Claude-generated analysis
    """
    claude_generator = ClaudeInsightGenerator()
    
    if claude_generator.enabled:
        claude_insights = claude_generator.generate_segment_insights(cluster_data, business_context)
        
        # Merge Claude insights with existing insights
        enhanced_insights = insights.copy()
        enhanced_insights['claude_analysis'] = claude_insights
        enhanced_insights['analysis_enhanced'] = True
        
        return enhanced_insights
    else:
        insights['claude_analysis'] = {'status': 'unavailable', 'reason': 'API key not configured'}
        return insights