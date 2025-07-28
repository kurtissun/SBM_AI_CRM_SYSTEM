#!/usr/bin/env python3
"""
Test script to upload Super Brand Mall data and test generative segmentation
"""
import requests
import json

def test_upload():
    base_url = "http://localhost:8080"
    
    print("🧪 Testing Super Brand Mall Data Upload")
    print("=" * 50)
    
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
    
    # Step 2: Upload file
    print("\n2️⃣ Uploading Super Brand Mall data...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    with open("sample_dataset_2.csv", "rb") as f:
        files = {"file": ("sample_dataset_2.csv", f, "text/csv")}
        data = {"auto_segment": "true"}
        
        upload_response = requests.post(
            f"{base_url}/api/customers/upload/chinese",
            headers=headers,
            files=files,
            data=data
        )
    
    print(f"📡 Upload Status: {upload_response.status_code}")
    
    if upload_response.status_code == 200:
        result = upload_response.json()
        
        print("✅ Upload Successful!")
        print("\n📊 Upload Summary:")
        
        if "upload_summary" in result:
            summary = result["upload_summary"]
            print(f"   • Format: {summary.get('data_format_detected', 'N/A')}")
            print(f"   • Customers saved: {summary.get('customers_saved', 0)}")
            print(f"   • Purchases saved: {summary.get('purchases_saved', 0)}")
            print(f"   • Duplicates skipped: {summary.get('duplicates_skipped', 0)}")
            print(f"   • Data quality: {summary.get('data_quality_score', 0):.1f}%")
        
        if "segmentation_results" in result:
            seg = result["segmentation_results"]
            method = seg.get("segmentation_method", "unknown")
            llm_enabled = seg.get("llm_enabled", False)
            
            print(f"\n🤖 Segmentation Results:")
            print(f"   • Method: {method}")
            print(f"   • LLM Enabled: {llm_enabled}")
            print(f"   • Clusters: {seg.get('n_clusters', 0)}")
            print(f"   • Algorithm: {seg.get('algorithm_used', 'N/A')}")
            print(f"   • Quality Score: {seg.get('silhouette_score', 0):.3f}")
            
            if llm_enabled and "llm_segments" in seg:
                print("\n✨ Generated Segments:")
                for segment_id, segment_info in seg["llm_segments"].items():
                    name = segment_info.get("name", segment_id)
                    chinese_name = segment_info.get("chinese_name", "")
                    print(f"   • {segment_id}: {name} ({chinese_name})")
            
            if "customer_assignments" in seg:
                print(f"\n👥 Customer Assignments:")
                for segment_id, customers in seg["customer_assignments"].items():
                    print(f"   • {segment_id}: {len(customers)} customers")
            
            if "executive_summary" in seg:
                summary = seg["executive_summary"]
                print(f"\n📋 Executive Summary:")
                for finding in summary.get("key_findings", []):
                    print(f"   • {finding}")
        
        print(f"\n🎉 Test Completed Successfully!")
        
        # Step 3: Test analytics endpoint
        print("\n3️⃣ Testing Analytics Endpoint...")
        analytics_response = requests.get(
            f"{base_url}/analytics/dashboard/overview",
            headers=headers
        )
        
        if analytics_response.status_code == 200:
            analytics = analytics_response.json()
            
            if "ai_insights" in analytics:
                ai_insights = analytics["ai_insights"]
                print("🧠 AI Insights Available:")
                
                if "performance_insights" in ai_insights:
                    print(f"   • Performance insights: {len(ai_insights['performance_insights'])}")
                if "immediate_actions" in ai_insights:
                    print(f"   • Immediate actions: {len(ai_insights['immediate_actions'])}")
                if "executive_summary" in ai_insights:
                    summary = ai_insights["executive_summary"][:100] + "..." if len(ai_insights["executive_summary"]) > 100 else ai_insights["executive_summary"]
                    print(f"   • Summary: {summary}")
            else:
                print("🔄 Using traditional analytics (LLM not available)")
        
    else:
        error_data = upload_response.json() if upload_response.headers.get('content-type', '').startswith('application/json') else {"error": upload_response.text}
        print(f"❌ Upload failed: {error_data}")
        
        if "error" in error_data:
            error = error_data["error"]
            print(f"   • Code: {error.get('code', 'Unknown')}")
            print(f"   • Message: {error.get('message', 'Unknown error')}")

if __name__ == "__main__":
    test_upload()