#!/usr/bin/env python3
"""
Test script for AI-powered Marketing Campaign Advisor
Demonstrates the new campaign guidance functionality
"""
import requests
import json

def test_campaign_advisor():
    base_url = "http://localhost:8080"
    
    print("🎯 Testing AI-Powered Marketing Campaign Advisor")
    print("=" * 60)
    
    # Step 1: Login
    print("1️⃣ Authenticating...")
    login_response = requests.post(
        f"{base_url}/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    auth_data = login_response.json()
    token = auth_data["access_token"]
    print(f"✅ Authenticated as {auth_data['user_info']['username']}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Test Health Check
    print("\n2️⃣ Checking Campaign Advisor Health...")
    health_response = requests.get(f"{base_url}/api/campaign-advisor/health", headers=headers)
    if health_response.status_code == 200:
        health = health_response.json()
        print(f"✅ Campaign Advisor Status: {health['status']}")
        print(f"🛠️ Features: {len(health.get('features', []))} available")
    else:
        print(f"❌ Health check failed: {health_response.status_code}")
    
    # Step 3: Get Customer Insights
    print("\n3️⃣ Getting Live Customer Database Insights...")
    insights_response = requests.get(f"{base_url}/api/campaign-advisor/customer-insights", headers=headers)
    if insights_response.status_code == 200:
        insights = insights_response.json()
        customer_data = insights["customer_insights"]["customer_demographics"]
        print(f"📊 Total Customers: {customer_data.get('total_customers', 0)}")
        print(f"👥 Average Age: {customer_data.get('average_age', 'N/A')}")
        print(f"🏙️ Cities Covered: {customer_data.get('cities_covered', 0)}")
        
        spending_data = insights["customer_insights"]["spending_patterns"]
        print(f"💰 Average Spending: ¥{spending_data.get('average_spending', 0)}")
        
        top_stores = insights["customer_insights"]["top_stores"][:3]
        if top_stores:
            print("🏪 Top Stores:")
            for store in top_stores:
                print(f"   • {store['name']}: {store['visits']} visits")
    else:
        print(f"❌ Customer insights failed: {insights_response.status_code}")
    
    # Step 4: Get Mall Context
    print("\n4️⃣ Getting Super Brand Mall Shanghai Context...")
    mall_response = requests.get(f"{base_url}/api/campaign-advisor/mall-context", headers=headers)
    if mall_response.status_code == 200:
        mall_data = mall_response.json()["mall_context"]
        print(f"🏢 Location: {mall_data['location']}")
        print(f"🎯 Positioning: {mall_data['positioning']}")
        
        tenant_categories = mall_data["tenant_categories"]
        print("🛍️ Key Tenant Categories:")
        for category, brands in tenant_categories.items():
            print(f"   • {category.replace('_', ' ').title()}: {', '.join(brands[:3])}...")
    else:
        print(f"❌ Mall context failed: {mall_response.status_code}")
    
    # Step 5: Test Campaign Templates
    print("\n5️⃣ Getting Pre-built Campaign Templates...")
    templates_response = requests.get(f"{base_url}/api/campaign-advisor/templates", headers=headers)
    if templates_response.status_code == 200:
        templates = templates_response.json()["templates"]
        print(f"📋 Available Templates: {len(templates)}")
        for template_name, template_data in templates.items():
            print(f"   • {template_data['name']}")
            print(f"     Budget: {template_data['recommended_budget']}")
            print(f"     Duration: {template_data['duration']}")
    else:
        print(f"❌ Templates failed: {templates_response.status_code}")
    
    # Step 6: Test Quick Guidance
    print("\n6️⃣ Testing Quick Campaign Guidance...")
    quick_request = {
        "campaign_goal": "提高年轻消费者对茶饮品牌的参与度",
        "target_audience": "18-35岁都市白领",
        "budget": "20万人民币"
    }
    
    quick_response = requests.post(
        f"{base_url}/api/campaign-advisor/quick-guidance", 
        json=quick_request, 
        headers=headers
    )
    
    if quick_response.status_code == 200:
        quick_data = quick_response.json()
        print("⚡ Quick Guidance Generated:")
        guidance = quick_data.get("quick_guidance", {})
        if "campaign_overview" in guidance:
            overview = guidance["campaign_overview"]
            print(f"   📊 Campaign Name: {overview.get('name', 'N/A')}")
            print(f"   🎯 Theme: {overview.get('theme', 'N/A')}")
        if "recommended_partnerships" in guidance:
            partnerships = guidance["recommended_partnerships"][:3]
            print(f"   🤝 Key Partnerships: {', '.join(partnerships)}")
    else:
        print(f"❌ Quick guidance failed: {quick_response.status_code}")
    
    # Step 7: Test Full AI Campaign Analysis
    print("\n7️⃣ Testing Full AI Campaign Analysis...")
    campaign_request = {
        "prompt": "我想为超级品牌购物中心创建一个针对年轻消费者的营销活动，重点是茶饮和娱乐体验。活动应该结合线上线下，创造社交媒体话题，提高品牌知名度。预算大约30万人民币，持续2个月。希望与喜茶、KTV等店铺合作。",
        "target_segment": "trendy_lifestyle_advocates",
        "campaign_type": "experiential_marketing",
        "budget_range": "250k-350k RMB"
    }
    
    analysis_response = requests.post(
        f"{base_url}/api/campaign-advisor/analyze", 
        json=campaign_request, 
        headers=headers
    )
    
    print(f"📡 Analysis Status: {analysis_response.status_code}")
    
    if analysis_response.status_code == 200:
        analysis = analysis_response.json()
        print("🤖 AI Campaign Analysis Generated!")
        
        analysis_data = analysis.get("analysis", {})
        if "campaign_analysis" in analysis_data:
            campaign_info = analysis_data["campaign_analysis"]
            
            if "campaign_overview" in campaign_info:
                overview = campaign_info["campaign_overview"]
                print(f"\n📊 Campaign Overview:")
                print(f"   • Name: {overview.get('name', 'N/A')}")
                print(f"   • Theme: {overview.get('theme', 'N/A')}")
                objectives = overview.get('objectives', [])
                if objectives:
                    print(f"   • Objectives: {', '.join(objectives[:3])}")
            
            if "audience_targeting" in campaign_info:
                targeting = campaign_info["audience_targeting"]
                print(f"\n🎯 Target Audience:")
                segments = targeting.get('primary_segments', [])
                if segments:
                    print(f"   • Primary Segments: {', '.join(segments[:3])}")
                print(f"   • Demographics: {targeting.get('demographics', 'N/A')}")
            
            if "recommended_partnerships" in campaign_info:
                partnerships = campaign_info["recommended_partnerships"]
                print(f"\n🤝 Recommended Partnerships:")
                for partnership in partnerships[:4]:
                    print(f"   • {partnership}")
            
            if "campaign_tactics" in campaign_info:
                tactics = campaign_info["campaign_tactics"]
                print(f"\n📋 Campaign Tactics:")
                for tactic in tactics[:4]:
                    print(f"   • {tactic}")
            
            if "implementation_steps" in campaign_info:
                steps = campaign_info["implementation_steps"]
                print(f"\n✅ Implementation Steps:")
                for i, step in enumerate(steps[:4], 1):
                    print(f"   {i}. {step}")
        
        # Show customer insights used
        customer_insights = analysis_data.get("customer_insights", {})
        if customer_insights and "customer_demographics" in customer_insights:
            demographics = customer_insights["customer_demographics"]
            print(f"\n📈 Analysis Based On:")
            print(f"   • {demographics.get('total_customers', 0)} customers in database")
            print(f"   • Average age: {demographics.get('average_age', 'N/A')}")
            print(f"   • {demographics.get('cities_covered', 0)} cities covered")
        
        print(f"\n🎉 Full AI Campaign Analysis Completed Successfully!")
        print(f"💡 Analysis generated by: {analysis.get('user', 'Unknown')}")
        
    else:
        error_data = analysis_response.json() if analysis_response.headers.get('content-type', '').startswith('application/json') else {"error": analysis_response.text}
        print(f"❌ AI analysis failed: {error_data}")
    
    print(f"\n🏁 Campaign Advisor Testing Complete!")
    print("=" * 60)
    print("Available Endpoints:")
    print("• POST /api/campaign-advisor/analyze - Full AI campaign analysis")
    print("• POST /api/campaign-advisor/quick-guidance - Rapid recommendations")
    print("• GET /api/campaign-advisor/customer-insights - Live database insights")
    print("• GET /api/campaign-advisor/mall-context - Mall tenant information")
    print("• GET /api/campaign-advisor/templates - Pre-built templates")
    print("• GET /api/campaign-advisor/health - Health check")

if __name__ == "__main__":
    test_campaign_advisor()