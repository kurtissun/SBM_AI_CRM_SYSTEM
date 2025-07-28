#!/usr/bin/env python3
"""
Test script to demonstrate generative analytics capabilities
"""
import pandas as pd
import json
from backend.ai_engine.generative_analytics import GenerativeAnalyticsEngine

def test_generative_analytics():
    """Test the generative analytics engine"""
    
    print("🧪 Testing Generative Analytics Engine")
    print("=" * 50)
    
    # Initialize engine
    engine = GenerativeAnalyticsEngine()
    
    # Test data
    sample_data = pd.DataFrame({
        'customer_id': ['001', '002', '003', '004', '005'],
        'age': [25, 34, 45, 28, 52],
        'gender': ['男', '女', '男', '女', '男'],
        'rating_id': [4, 5, 3, 4, 2],
        'segment_id': [1, 1, 2, 1, 3],
        'location': ['北京', '上海', '广州', '深圳', '成都'],
        'membership_level': ['金卡会员', '钻卡会员', '橙卡会员', '金卡会员', '橙卡会员']
    })
    
    print(f"📊 Sample Data: {len(sample_data)} customers")
    print(f"🤖 LLM Available: {engine.enabled}")
    print()
    
    # Test 1: Customer Insights
    print("1️⃣ Testing Customer Insights Generation")
    print("-" * 40)
    
    customer_insights = engine.generate_customer_insights(sample_data, "comprehensive")
    
    if engine.enabled:
        print("✨ Generated LLM Insights:")
        print(f"   • Behavior Patterns: {len(customer_insights.get('behavior_patterns', []))} insights")
        print(f"   • Revenue Opportunities: {len(customer_insights.get('revenue_opportunities', []))} ideas")
        print(f"   • Key Findings: {customer_insights.get('key_findings', 'N/A')[:80]}...")
        
        if customer_insights.get('demographic_insights'):
            print(f"   • Demographic Analysis: Available")
    else:
        print("🔄 Using Fallback Analytics:")
        print(f"   • Traditional Analysis: {customer_insights.get('llm_available', 'Unknown')}")
    
    print()
    
    # Test 2: Dashboard Insights
    print("2️⃣ Testing Dashboard Insights Generation")
    print("-" * 40)
    
    dashboard_metrics = {
        "customer_metrics": {
            "total_customers": 150,
            "new_customers": 25,
            "high_value_customers": 45,
            "segmentation_rate": 85.3
        },
        "campaign_metrics": {
            "total_campaigns": 8,
            "active_campaigns": 3,
            "average_roi": 2.4,
            "total_budget": 50000
        }
    }
    
    dashboard_insights = engine.generate_dashboard_insights(dashboard_metrics)
    
    if engine.enabled:
        print("✨ Generated Dashboard Insights:")
        print(f"   • Performance Insights: {len(dashboard_insights.get('performance_insights', []))} items")
        print(f"   • Immediate Actions: {len(dashboard_insights.get('immediate_actions', []))} items")
        print(f"   • Strategic Opportunities: {len(dashboard_insights.get('strategic_opportunities', []))} items")
        print(f"   • Executive Summary: {dashboard_insights.get('executive_summary', 'N/A')[:80]}...")
    else:
        print("🔄 Using Fallback Dashboard:")
        print(f"   • Basic Insights Available")
    
    print()
    
    # Test 3: Campaign Recommendations
    print("3️⃣ Testing Campaign Recommendations")
    print("-" * 40)
    
    campaign_data = {
        "performance_summary": {
            "total_campaigns": 5,
            "average_roi": 2.1,
            "total_budget": 30000
        }
    }
    
    campaign_recs = engine.generate_campaign_recommendations(campaign_data)
    
    if engine.enabled:
        print("✨ Generated Campaign Recommendations:")
        if 'platform_campaigns' in campaign_recs:
            platforms = list(campaign_recs['platform_campaigns'].keys())
            print(f"   • Platform Strategies: {platforms}")
        if 'seasonal_campaigns' in campaign_recs:
            print(f"   • Seasonal Campaigns: {len(campaign_recs['seasonal_campaigns'])} ideas")
        if 'expected_roi' in campaign_recs:
            print(f"   • ROI Expectations: Available")
    else:
        print("🔄 Using Fallback Campaigns:")
        print(f"   • Basic Recommendations Available")
    
    print()
    
    # Test 4: Market Opportunities
    print("4️⃣ Testing Market Opportunity Analysis")
    print("-" * 40)
    
    business_data = {
        "customer_data": sample_data.to_dict('records'),
        "business_metrics": {"total_customers": len(sample_data)}
    }
    
    market_ops = engine.generate_market_opportunities(business_data)
    
    if engine.enabled:
        print("✨ Generated Market Opportunities:")
        print(f"   • New Segments: {len(market_ops.get('new_segments', []))} identified")
        print(f"   • Technology Integration: {len(market_ops.get('technology_integration', []))} opportunities")
        print(f"   • Revenue Streams: {len(market_ops.get('revenue_streams', []))} ideas")
    else:
        print("🔄 Using Fallback Market Analysis:")
        print(f"   • Basic Opportunities Available")
    
    print()
    
    # Summary
    print("📋 Test Summary")
    print("=" * 50)
    
    if engine.enabled:
        print("✅ Generative Analytics: ENABLED")
        print("🤖 LLM Model: " + engine.model_name)
        print("💡 Intelligence Level: HIGH (Context-aware, Chinese market insights)")
        print("🎯 Recommendations: Specific, actionable, culturally relevant")
        print("📊 Analysis Depth: Comprehensive with business context")
        print()
        print("🚀 Your system now provides:")
        print("   • Intelligent customer segmentation")
        print("   • Context-aware business insights")
        print("   • Chinese market-specific recommendations")
        print("   • Adaptive campaign strategies")
        print("   • Predictive market analysis")
    else:
        print("⚠️  Generative Analytics: DISABLED")
        print("🔄 Fallback Mode: Rule-based analytics")
        print("💡 Intelligence Level: BASIC (Statistical patterns only)")
        print("📊 Analysis Depth: Traditional clustering and metrics")
        print()
        print("🛠️ To enable full capabilities:")
        print("   1. Run: ./setup_local_llm.sh")
        print("   2. Or manually: ollama pull llama3.2:3b")
        print("   3. Restart the system")
    
    print()
    print("🎉 Test Completed!")

if __name__ == "__main__":
    test_generative_analytics()