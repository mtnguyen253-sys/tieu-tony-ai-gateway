import os
import json
import httpx
import sys

def main():
    base_url = os.environ.get("AI_GATEWAY_BASE_URL", "http://127.0.0.1:8000")
    print(f"Connecting to Gateway at: {base_url}")

    payload = {
        "model": "qwen/qwen3.6-plus",
        "messages": [{"role": "user", "content": "Say hello in Vietnamese"}],
        "stream": True
    }

    try:
        with httpx.stream("POST", f"{base_url}/chat/completions", json=payload, timeout=30.0) as resp:
            if resp.status_code != 200:
                print(f"Error: {resp.status_code}")
                print(resp.read().decode())
                return

            print("Streaming started...\n")
            for line in resp.iter_lines():
                if line and line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        print("\n\n[DONE]")
                        break
                    
                    try:
                        chunk = json.loads(data_str)
                        choices = chunk.get("choices", [])
                        if choices:
                            delta = choices[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                sys.stdout.write(content)
                                sys.stdout.flush()
                        
                        usage = chunk.get("usage")
                        if usage:
                            print(f"\n[Usage: {usage}]")
                    except json.JSONDecodeError:
                        pass
    except httpx.RequestError as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    main()
