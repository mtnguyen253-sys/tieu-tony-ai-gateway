import httpx
import sys
import os

def main():
    url = "http://127.0.0.1:8000/chat/completions"
    payload = {
        "model": "openrouter",
        "messages": [
            {"role": "user", "content": "Hello! Please reply with a short greeting."}
        ]
    }
    
    print(f"Sending request to {url}...")
    try:
        response = httpx.post(url, json=payload, timeout=30.0)
    except httpx.ConnectError:
        print("Error: Could not connect to the server. Is it running on http://127.0.0.1:8000?")
        sys.exit(1)
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")
        sys.exit(1)
        
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print("Response JSON:")
        import json
        print(json.dumps(data, indent=2))
        
        if response.status_code == 200:
            if "choices" in data and len(data["choices"]) > 0:
                print("\nAssistant Response:")
                print(data["choices"][0]["message"]["content"])
    except Exception as e:
        print(f"Error parsing JSON response: {e}")
        print(f"Raw response: {response.text}")

if __name__ == "__main__":
    main()
