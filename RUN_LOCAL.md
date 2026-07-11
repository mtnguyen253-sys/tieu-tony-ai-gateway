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
Copy file `.env.example` thành `.env` và điền API key thực tế nếu cần:
```powershell
copy .env.example .env
```
Mở file `.env` và cập nhật `OPENROUTER_API_KEY`.

(Tuỳ chọn) Chạy script kiểm tra môi trường:
```powershell
.\scripts\check_env.ps1
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
