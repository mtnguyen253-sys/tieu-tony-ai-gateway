# Hướng dẫn chạy Local (Tiểu Tony AI Gateway)

Tài liệu này hướng dẫn cách chạy và test AI Gateway ở môi trường local.

## 1. Môi trường (Virtual Environment)

Tạo virtual environment:
```powershell
python -m venv venv
```

Activate venv (trên Windows PowerShell):
```powershell
.\venv\Scripts\Activate.ps1
```

## 2. Cài đặt Dependencies

Cài đặt các gói cần thiết:
```powershell
pip install fastapi uvicorn pydantic httpx pytest
```

## 3. Cấu hình Environment Variables (Provider thật)

Gateway hỗ trợ OpenRouter làm provider đầu tiên. Để cấu hình, bạn có thể tạo file `.env` ở thư mục gốc hoặc set trực tiếp trong PowerShell.

Set biến môi trường qua PowerShell:
```powershell
$env:OPENROUTER_API_KEY="sk-or-v1-..."
$env:OPENROUTER_MODEL="openai/gpt-3.5-turbo"
```

## 4. Chạy Test Suite

Để đảm bảo hệ thống an toàn và code không bị break, chạy full test suite:
```powershell
python -m pytest ai_gateway/tests -v
```

## 5. Chạy Server

### 5.1. Production / Default Runtime
Chạy với cấu hình mặc định (sẽ sử dụng provider thật nếu có API Key, nếu không sẽ trả 503):
```powershell
python -m uvicorn ai_gateway.api.app:app --reload
```

### 5.2. Dev / Mock Runtime
Chạy với cấu hình mock orchestrator (luôn trả về 200 cho mục đích test integration, không cần API Key):
```powershell
python -m uvicorn ai_gateway.api.dev:app --reload
```

## 6. Chạy Smoke Script

Khi server đang chạy, mở một terminal khác và gọi smoke script tương ứng:

### 6.1. Test Mock Runtime
(Yêu cầu server chạy qua `ai_gateway.api.dev:app`)
```powershell
python examples/smoke_chat_completion.py
```
**Kỳ vọng:**
- Status Code: 200
- Assistant Response: "Hello from Mock Orchestrator! This is a simulated response."

### 6.2. Test Default Runtime (Chưa cấu hình API Key)
(Yêu cầu server chạy qua `ai_gateway.api.app:app` và không set OPENROUTER_API_KEY)
```powershell
python examples/smoke_real_provider.py
```
**Kỳ vọng:**
- Status Code: 503
- Báo lỗi Provider Unavailable.

### 6.3. Test Default Runtime (Có cấu hình API Key)
(Yêu cầu server chạy qua `ai_gateway.api.app:app` và đã set OPENROUTER_API_KEY)
```powershell
python examples/smoke_real_provider.py
```
**Kỳ vọng:**
- Status Code: 200
- Assistant Response: Câu trả lời thực tế từ mô hình AI (OpenRouter).

## 7. Dừng Server
Tại terminal đang chạy Uvicorn, nhấn `Ctrl + C` để dừng server.
