import os
import httpx
import json
import sys

# Example smoke test script
# Reads:
# AI_GATEWAY_BASE_URL
# AI_GATEWAY_API_KEY
# AI_GATEWAY_MODEL

BASE_URL = os.getenv("AI_GATEWAY_BASE_URL", "http://127.0.0.1:8000/v1")
API_KEY = os.getenv("AI_GATEWAY_API_KEY", "dummy")
MODEL = os.getenv("AI_GATEWAY_MODEL", "qwen/qwen3.6-plus")

def test_smoke():
    print(f"Testing {BASE_URL} with model {MODEL}...")
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    with httpx.Client(base_url=BASE_URL, headers=headers, timeout=30.0) as client:
        # 1. Health
        try:
            resp = client.get("/health")
            print(f"Health: {resp.status_code}")
            if resp.status_code != 200:
                print(f"Health check failed: {resp.text}")
                return
        except Exception as e:
            print(f"Health check error: {e}")
            return
            
        # 2. Models
        try:
            resp = client.get("/models")
            print(f"Models: {resp.status_code}")
            models = resp.json().get("data", [])
            print(f"Available models: {[m['id'] for m in models]}")
        except Exception as e:
            print(f"Models check error: {e}")
            
        # 3. Chat Completion
        body = {
            "model": MODEL,
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": False
        }
        try:
            resp = client.post("/chat/completions", json=body)
            print(f"Chat Completion (no stream): {resp.status_code}")
            if resp.status_code == 200:
                print(f"Response: {resp.json().get('choices', [{}])[0].get('message', {}).get('content')[:50]}...")
            else:
                print(f"Chat Completion failed: {resp.text}")
        except Exception as e:
            print(f"Chat Completion error: {e}")

if __name__ == "__main__":
    test_smoke()
