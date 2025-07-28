#!/usr/bin/env python3
"""
Simple test server to check connectivity
"""
import sys
import uvicorn
from fastapi import FastAPI

app = FastAPI(title="Test Server")

@app.get("/")
async def root():
    return {"message": "✅ Server is working!", "status": "ok"}

@app.get("/test")  
async def test():
    return {"test": "successful", "server": "running"}

if __name__ == "__main__":
    print("🚀 Starting simple test server...")
    print("📍 Will be available at: http://localhost:8080")
    print("🔗 Test endpoints: / and /test")
    print("=" * 50)
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8080,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Server failed: {e}")
        sys.exit(1)