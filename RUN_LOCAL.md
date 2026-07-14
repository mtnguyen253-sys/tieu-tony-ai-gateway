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

## 6. Kiểm tra Cấu hình (Sprint 29)
Kiểm tra cấu hình hiện tại trước khi chạy:
```powershell
python -m ai_gateway.tools.config_check
```

## 7. Chạy Smoke Test (Sprint 29)
Chạy smoke test để xác thực runtime provider selection:
```powershell
python examples/smoke_runtime_selection.py
```

## 8. Kiểm tra Health & Models
```powershell
curl http://127.0.0.1:8000/v1/health
curl http://127.0.0.1:8000/v1/models
```

## 9. Test Non-streaming Request
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

## 10. Test Streaming Request
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

## 11. Test OpenAI SDK
Chạy script smoke test bằng Python (đảm bảo package `openai` đã được cài):
```powershell
python examples/smoke_openai_sdk.py
```
*(Hoặc script stream raw `python examples/smoke_streaming.py`)*

## 12. Chạy Unit Tests
Chạy toàn bộ bộ test để đảm bảo không bị regression:
```powershell
python -m pytest ai_gateway/tests -v
```

## 13. Usage Economics & Cache-aware Routing
Xem báo cáo Usage Economics:
```bash
python -m ai_gateway.tools.usage_summary logs/usage.jsonl
```
Nếu Cache Ratio thấp, cân nhắc chọn các provider có `supports_prompt_cache=true`.

## 14. Task Classification & Routing (Sprint 30)
Gateway tự động phân loại mức độ phức tạp của từng yêu cầu (SIMPLE, STANDARD, COMPLEX, LONG_CONTEXT, CRITICAL) và chọn model tier phù hợp (CHEAP, BALANCED, STRONG, LONG_CONTEXT) nhằm tiết kiệm chi phí mà vẫn đảm bảo hiệu suất. Bạn có thể định cấu hình `model_tier` và `max_context_tokens` cho từng provider trong `.env`:

```env
AI_GATEWAY_PROVIDER_1_NAME=cheap_provider
AI_GATEWAY_PROVIDER_1_MODEL_TIER=cheap
AI_GATEWAY_PROVIDER_1_MAX_CONTEXT_TOKENS=8192

AI_GATEWAY_PROVIDER_2_NAME=long_context_provider
AI_GATEWAY_PROVIDER_2_MODEL_TIER=long_context
AI_GATEWAY_PROVIDER_2_MAX_CONTEXT_TOKENS=128000
```
