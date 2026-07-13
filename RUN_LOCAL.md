# Hướng Dẫn Chạy Local (Tiểu Tony AI Gateway)

Hướng dẫn này giúp bạn thiết lập và chạy AI Gateway trên máy local (ưu tiên môi trường Windows/PowerShell).

## 1. Clone repo
```powershell
git clone <repository_url>
cd tieu-tony-ai-gateway
```

## 2. Tạo Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 3. Cài đặt Dependencies
```powershell
python -m pip install -r requirements-dev.txt
```

## 4. Cấu hình môi trường (.env)

Bạn có thể cấu hình provider theo 2 cách:

### Legacy OpenRouter config
```env
OPENROUTER_API_KEY=...
OPENROUTER_MODEL=qwen/qwen3.6-plus
```

### Generic provider config
```env
AI_GATEWAY_PROVIDER_1_NAME=cliproxy
AI_GATEWAY_PROVIDER_1_BASE_URL=http://127.0.0.1:8317/v1
AI_GATEWAY_PROVIDER_1_API_KEY=dummy
AI_GATEWAY_PROVIDER_1_MODEL=DeepSeek-V4-Pro
AI_GATEWAY_PROVIDER_1_ENABLED=true
AI_GATEWAY_PROVIDER_1_SUPPORTS_STREAMING=true

AI_GATEWAY_PROVIDER_2_NAME=together
AI_GATEWAY_PROVIDER_2_BASE_URL=https://api.together.xyz/v1
AI_GATEWAY_PROVIDER_2_API_KEY=your_together_key_here
AI_GATEWAY_PROVIDER_2_MODEL=deepseek-ai/DeepSeek-V4-Pro
AI_GATEWAY_PROVIDER_2_ENABLED=true
```

Copy file `.env.example` thành `.env` và điền API key thực tế nếu cần:
```powershell
copy .env.example .env
```

## 5. Chạy Gateway
Bạn có thể chạy bằng script có sẵn (sẽ tự động active venv và fallback `.env.example` nếu chưa tạo `.env`):
```powershell
.\scripts\run_local.ps1 -Reload
```
Hoặc chạy trực tiếp qua Uvicorn:
```powershell
python -m uvicorn ai_gateway.api.app:app --reload
```

## 6. Kiểm tra Health & Models
```powershell
curl http://127.0.0.1:8000/v1/health
curl http://127.0.0.1:8000/v1/models
```

## 7. Test Non-streaming Request
```powershell
@'
{
  "model": "qwen/qwen3.6-plus",
  "messages": [
    {"role": "user", "content": "Say hello in Vietnamese"}
  ]
}
'@ | Set-Content -Encoding UTF8 body.json

curl.exe -X POST http://127.0.0.1:8000/v1/chat/completions `
  -H "Content-Type: application/json" `
  --data-binary "@body.json"
```

## 8. Test Streaming Request
```powershell
@'
{
  "model": "qwen/qwen3.6-plus",
  "messages": [
    {"role": "user", "content": "Say hello in Vietnamese"}
  ],
  "stream": true
}
'@ | Set-Content -Encoding UTF8 stream_body.json

curl.exe -N -X POST http://127.0.0.1:8000/v1/chat/completions `
  -H "Content-Type: application/json" `
  --data-binary "@stream_body.json"
```

## 9. Test OpenAI SDK
Chạy script smoke test bằng Python (đảm bảo package `openai` đã được cài):
```powershell
python examples/smoke_openai_sdk.py
```
*(Hoặc script stream raw `python examples/smoke_streaming.py`)*

## 10. Chạy Unit Tests
Chạy toàn bộ bộ test để đảm bảo không bị regression:
```powershell
python -m pytest ai_gateway/tests -v
```

### Token Economics Report
Tiểu Tony automatically logs usage events (requests, tokens, latency, cost) to `logs/usage.jsonl`.
You can view a detailed token economics report to analyze your costs and performance.

Run the summary tool:
```bash
python -m ai_gateway.tools.usage_summary logs/usage.jsonl
```

For JSON output:
```bash
python -m ai_gateway.tools.usage_summary logs/usage.jsonl --json
```

**How to read the report:**
- **Cache Ratio**: High cache ratio (>70%) means your prompts are effectively reusing cached tokens (good for long-context workloads). If it is low, consider optimizing your prompts or enabling cache-aware routing.
- **Cost Breakdown**: Shows input, cached input, and output token costs separately (if supported by the provider configuration).
- **Insights & Warnings**: The tool automatically warns you if:
  - A single model accounts for >70% of total cost.
  - A provider has a high rate-limit frequency.
  - Your requests are unusually output-heavy.
  - Unknown pricing configurations are heavily utilized.
