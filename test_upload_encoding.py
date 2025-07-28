#!/usr/bin/env python3
"""
Test script to verify UTF-8 upload handling
"""
import requests
import json
import io

def test_upload_with_chinese_filename():
    base_url = "http://localhost:8080"
    
    print("🧪 Testing Upload with UTF-8 Encoding")
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
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Create test CSV with Chinese content
    print("2️⃣ Creating test CSV with Chinese content...")
    csv_content = """会员id,所在地,性别,生日,注册时间,消费时间,会员等级,消费金额,消费获取积分,消费业态,消费店铺
1001,上海,女,1990-05-15,2023-01-10,2023-12-01,VIP,1500.50,150,餐饮,喜茶
1002,北京,男,1985-10-22,2023-02-15,2023-12-02,普通,850.25,85,服装,优衣库
1003,广州,女,1988-08-30,2023-03-20,2023-12-03,金卡,2200.75,220,美妆,丝芙兰"""
    
    # Step 3: Test upload with Chinese filename
    print("3️⃣ Testing upload with Chinese filename...")
    chinese_filename = "客户数据_测试.csv"
    
    files = {
        'file': (chinese_filename, csv_content.encode('utf-8'), 'text/csv; charset=utf-8')
    }
    
    try:
        upload_response = requests.post(
            f"{base_url}/api/customers/upload/chinese",
            headers=headers,
            files=files,
            params={"auto_segment": True}
        )
        
        print(f"📡 Upload Status: {upload_response.status_code}")
        
        if upload_response.status_code == 200:
            result = upload_response.json()
            print("✅ Upload successful!")
            print(f"📊 Processed: {result.get('records_processed', 0)} records")
            print(f"🎯 Segments: {result.get('segments_created', 0)} created")
        else:
            print(f"❌ Upload failed: {upload_response.text}")
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
    
    print("\n🏁 Encoding test complete!")

if __name__ == "__main__":
    test_upload_with_chinese_filename()