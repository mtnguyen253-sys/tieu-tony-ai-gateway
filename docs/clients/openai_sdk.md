# Integration Guide: OpenAI Python SDK

This guide describes how to connect the OpenAI Python SDK to **Tiểu Tony AI Gateway** as an OpenAI-compatible provider.

## 1. Connection Configuration

- **Base URL**: `http://127.0.0.1:8000/v1`
- **API Key**: `dummy` (or any non-empty string)
- **Model**: Any model listed under `http://127.0.0.1:8000/v1/models` (e.g., `qwen/qwen3.6-plus`)

## 2. Integration Example (Python)

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

## 3. Verification

Before integrating, you can verify that the gateway is running properly:

### Check Health
```bash
curl http://127.0.0.1:8000/v1/health
```

### Check Available Models
```bash
curl http://127.0.0.1:8000/v1/models
```

### Run Smoke Test
Run the unified client smoke script:
```bash
python examples/smoke_external_client.py
```
