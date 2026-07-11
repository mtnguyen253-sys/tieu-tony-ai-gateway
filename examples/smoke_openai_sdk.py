import os
import sys

try:
    from openai import OpenAI
except ImportError:
    print("Please install openai: python -m pip install openai")
    sys.exit(1)

def main():
    base_url = os.environ.get("AI_GATEWAY_BASE_URL", "http://127.0.0.1:8000/v1")
    api_key = os.environ.get("AI_GATEWAY_API_KEY", "dummy")
    model = os.environ.get("AI_GATEWAY_MODEL", "qwen/qwen3.6-plus")
    
    print(f"Connecting to {base_url} with model {model}...")
    
    client = OpenAI(
        base_url=base_url,
        api_key=api_key
    )
    
    print("\n--- Testing /models ---")
    models = client.models.list()
    for m in models.data:
        print(f"Model: {m.id} (owned by {m.owned_by})")
        
    print("\n--- Testing non-streaming ---")
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "Say hello in Vietnamese"}
            ]
        )
        print("Response:", resp.choices[0].message.content)
        if hasattr(resp, 'usage') and resp.usage:
            print("Usage:", resp.usage)
    except Exception as e:
        print("Non-streaming error:", e)
        
    print("\n--- Testing streaming ---")
    try:
        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "Say hello in Vietnamese"}
            ],
            stream=True
        )
        print("Streaming response: ", end="")
        for chunk in stream:
            if chunk.choices and len(chunk.choices) > 0:
                content = chunk.choices[0].delta.content
                if content:
                    sys.stdout.write(content)
                    sys.stdout.flush()
        print("\nStream completed.")
    except Exception as e:
        print("Streaming error:", e)

if __name__ == "__main__":
    main()
