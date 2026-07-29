# Integration Guide: OpenAI Python SDK

This guide describes how to connect the OpenAI Python SDK to **Tiểu Tony AI Gateway** as an OpenAI-compatible provider.

## Provider-backed boundary

This guide is configuration guidance for using the OpenAI Python SDK with the local gateway. Provider-free checks are limited to the local health and models endpoints documented below and in `README.md`, `RUN_LOCAL.md`, and `docs/CLIENT_COMPATIBILITY.md`.

Live SDK chat completions, streaming, tool/function calling, usage-ledger writes, smoke scripts, and end-to-end provider connectivity require separately approved provider configuration and live verification before they should be treated as verified.

## 1. Connection Configuration

- **Base URL**: `http://127.0.0.1:8000/v1`
- **API Key**: `dummy` (or any non-empty string)
- **Model**: Any model listed under `http://127.0.0.1:8000/v1/models` (e.g., `qwen/qwen3.6-plus`)

## 2. Integration Example (Python)

The following example exercises a provider-backed chat completion path. Do not treat it as provider-free verification.

```python
from openai import OpenAI

# Initialize client pointing to the local AI Gateway
client = OpenAI(
    base_url="http://127.0.0.1:8000/v1",
    api_key="dummy" # Any non-empty string works as long as auth is not enforced
)

# Call the chat completions endpoint
response = client.chat.completions.create(
    model="qwen/qwen3.6-plus",
    messages=[
        {"role": "user", "content": "Tell me a joke."}
    ],
    stream=False
)

print(response.choices[0].message.content)
```

## 3. Provider-free verification

Before provider-backed integration, you can verify that the gateway process is reachable:

### Check Health
```bash
curl http://127.0.0.1:8000/v1/health
```

### Check Available Models
```bash
curl http://127.0.0.1:8000/v1/models
```

### Provider-backed smoke test
Run the unified client smoke script only when provider-backed live verification is separately approved:
```bash
python examples/smoke_external_client.py
```
