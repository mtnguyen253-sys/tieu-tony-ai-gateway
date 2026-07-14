import os
import sys

try:
    from openai import OpenAI
except ImportError:
    print("Please install openai: python -m pip install openai")
    sys.exit(1)


def build_client_config() -> dict:
    """Builds the client configuration dictionary from environment variables."""
    base_url = os.environ.get("AI_GATEWAY_BASE_URL", "http://127.0.0.1:8000/v1")
    api_key = os.environ.get("AI_GATEWAY_API_KEY", "dummy")
    model = os.environ.get("AI_GATEWAY_MODEL", "qwen/qwen3.6-plus")
    stream_str = os.environ.get("AI_GATEWAY_STREAM", "true").lower()
    stream = stream_str in ("true", "1", "yes")
    return {
        "base_url": base_url,
        "api_key": api_key,
        "model": model,
        "stream": stream,
    }


def redact_config(config: dict) -> dict:
    """Returns a redacted copy of the configuration safe for printing."""
    redacted = config.copy()
    key = redacted.get("api_key", "dummy")
    if key and key != "dummy":
        redacted["api_key"] = key[:3] + "..." if len(key) > 6 else "***"
    else:
        redacted["api_key"] = "dummy"
    return redacted


def parse_models_response(models_data) -> list:
    """Parses model listing response to extract model IDs."""
    model_ids = []
    if hasattr(models_data, "data"):
        for m in models_data.data:
            model_ids.append(m.id)
    elif isinstance(models_data, dict) and "data" in models_data:
        for m in models_data["data"]:
            if isinstance(m, dict) and "id" in m:
                model_ids.append(m["id"])
    return model_ids


def main():
    config = build_client_config()
    safe_config = redact_config(config)

    print("========================================")
    print("  TIỂU TONY EXTERNAL CLIENT SMOKE TEST  ")
    print("========================================")
    print(f"Base URL:         {safe_config['base_url']}")
    print(f"API Key:          {safe_config['api_key']}")
    print(f"Configured Model: {safe_config['model']}")
    print(f"Enable Stream:    {safe_config['stream']}")
    print("----------------------------------------")

    client = OpenAI(
        base_url=config["base_url"],
        api_key=config["api_key"]
    )

    # 1. Fetch Models
    print("\n[1] Fetching available models...")
    try:
        models = client.models.list()
        model_ids = parse_models_response(models)
        print(f"Models Count:     {len(model_ids)}")
        if not model_ids:
            print("WARNING: /v1/models is EMPTY! Please check your provider setup in .env.")
        else:
            print("Available models:")
            for m_id in model_ids:
                print(f"  - {m_id}")
            if config["model"] not in model_ids:
                print(f"WARNING: Selected model '{config['model']}' is not in the available models list.")
    except Exception as e:
        print(f"Error listing models: {e}")
        model_ids = []

    # 2. Testing Non-Streaming completion
    print("\n[2] Testing non-streaming completion...")
    try:
        resp = client.chat.completions.create(
            model=config["model"],
            messages=[
                {"role": "user", "content": "Reply exactly: OK"}
            ],
            stream=False,
            max_tokens=10,
            temperature=0.0
        )
        print("Non-stream Status: SUCCESS")
        print(f"Response Preview: {resp.choices[0].message.content}")
        if hasattr(resp, 'usage') and resp.usage:
            print(f"Usage Info:       Prompt={resp.usage.prompt_tokens}, Completion={resp.usage.completion_tokens}, Total={resp.usage.total_tokens}")
    except Exception as e:
        print(f"Non-stream Status: FAILED ({type(e).__name__})")
        print(f"Error Details:     {e}")

    # 3. Testing Streaming completion (if enabled)
    if config["stream"]:
        print("\n[3] Testing streaming completion...")
        try:
            stream = client.chat.completions.create(
                model=config["model"],
                messages=[
                    {"role": "user", "content": "Count from 1 to 3. Keep it short."}
                ],
                stream=True,
                max_tokens=15,
                temperature=0.0
            )
            print("Stream Status:     SUCCESS")
            print("Stream Response:  ", end="")
            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    content = chunk.choices[0].delta.content
                    if content:
                        sys.stdout.write(content)
                        sys.stdout.flush()
            print("\nStream completed successfully.")
        except Exception as e:
            print(f"Stream Status:     FAILED ({type(e).__name__})")
            print(f"Error Details:     {e}")
    else:
        print("\n[3] Streaming test skipped (AI_GATEWAY_STREAM=false).")

    print("\n========================================")
    print("             SMOKE TEST END             ")
    print("========================================")


if __name__ == "__main__":
    main()
