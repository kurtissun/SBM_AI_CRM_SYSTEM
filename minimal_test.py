#!/usr/bin/env python3
"""
Minimal FastAPI server to test basic connectivity
"""
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    print("🧪 Starting minimal test server on 127.0.0.1:8082")
    uvicorn.run(app, host="127.0.0.1", port=8082)