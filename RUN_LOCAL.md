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

## 11. Cache-aware Routing
AI Gateway hỗ trợ định tuyến thông minh dựa trên khả năng cache prompt (prompt caching) của provider. Nếu workload của bạn yêu cầu nhiều context (long-context) hoặc bạn ưu tiên sử dụng cache, router sẽ ưu tiên các provider có metadata cache-capable.

### Cấu hình Provider hỗ trợ Cache:
Trong file `.env`, bạn có thể thêm các field sau cho một provider:
```env
AI_GATEWAY_PROVIDER_1_SUPPORTS_PROMPT_CACHE=true
AI_GATEWAY_PROVIDER_1_CACHE_READ_COST_PER_MILLION=0.1
AI_GATEWAY_PROVIDER_1_CACHE_WRITE_COST_PER_MILLION=0.5
AI_GATEWAY_PROVIDER_1_CACHE_PRIORITY=1.2
```

### Cách sử dụng:
Khi gửi request, bạn có thể truyền hints trong context để kích hoạt routing cache-aware:
- `cache_preferred=true`
- `long_context=true`

### Xem báo cáo Cache Ratio:
Xem báo cáo Usage Economics để theo dõi Cache Ratio của các provider:
```bash
python -m ai_gateway.tools.usage_summary logs/usage.jsonl
```
Nếu Cache Ratio thấp, cân nhắc chọn các provider có `supports_prompt_cache=true`.
