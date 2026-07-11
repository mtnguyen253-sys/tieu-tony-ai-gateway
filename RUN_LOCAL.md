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


## 4. Cấu hình Budget-aware Routing
AI Gateway hỗ trợ kiểm soát ngân sách thông qua các biến môi trường:

```powershell
$env:AI_GATEWAY_BUDGET_MODE="normal"
$env:AI_GATEWAY_DAILY_BUDGET_USD="1.0"
$env:AI_GATEWAY_MONTHLY_BUDGET_USD="30.0"
$env:AI_GATEWAY_MAX_COST_PER_REQUEST="0.05"
```

**Giải thích các Budget Mode:**
- **`normal`**: Cân bằng giữa cost, latency và quality.
- **`economy`**: Ưu tiên tiết kiệm chi phí, ưu tiên chọn provider/model rẻ hơn.
- **`emergency`**: Siết chi phí mạnh nhất. Đây là chế độ cạn kiệt ngân sách (cost-saving emergency), không phải là performance mode. Emergency mode sẽ ưu tiên tối đa model rẻ/free và **không được bypass budget limit** để tránh chọn model đắt tiền chỉ vì quality cao.

## 5. Chạy Test Suite

Để đảm bảo hệ thống an toàn và code không bị break, chạy full test suite:
```powershell
python -m pytest ai_gateway/tests -v
```

## 6. Chạy Server

### 6.1. Production / Default Runtime
Chạy với cấu hình mặc định (sẽ sử dụng provider thật nếu có API Key, nếu không sẽ trả 503):
```powershell
python -m uvicorn ai_gateway.api.app:app --reload
```

### 6.2. Dev / Mock Runtime
Chạy với cấu hình mock orchestrator (luôn trả về 200 cho mục đích test integration, không cần API Key):
```powershell
python -m uvicorn ai_gateway.api.dev:app --reload
```

## 7. Chạy Smoke Script

Khi server đang chạy, mở một terminal khác và gọi smoke script tương ứng:

### 7.1. Test Mock Runtime
(Yêu cầu server chạy qua `ai_gateway.api.dev:app`)
```powershell
python examples/smoke_chat_completion.py
```
**Kỳ vọng:**
- Status Code: 200
- Assistant Response: "Hello from Mock Orchestrator! This is a simulated response."

### 7.2. Test Default Runtime (Chưa cấu hình API Key)
(Yêu cầu server chạy qua `ai_gateway.api.app:app` và không set OPENROUTER_API_KEY)
```powershell
python examples/smoke_real_provider.py
```
**Kỳ vọng:**
- Status Code: 503
- Báo lỗi Provider Unavailable.

### 7.3. Test Default Runtime (Có cấu hình API Key)
(Yêu cầu server chạy qua `ai_gateway.api.app:app` và đã set OPENROUTER_API_KEY)
```powershell
python examples/smoke_real_provider.py
```
**Kỳ vọng:**
- Status Code: 200
- Assistant Response: Câu trả lời thực tế từ mô hình AI (OpenRouter).


### 7.4. Test Runtime với Real Provider (Budget Mode)
Terminal 1:
```powershell
$env:OPENROUTER_API_KEY="..."
$env:OPENROUTER_MODEL="qwen/qwen-plus"
$env:AI_GATEWAY_BUDGET_MODE="economy"
python -m uvicorn ai_gateway.api.app:app --reload
```
Terminal 2:
```powershell
python examples/smoke_real_provider.py
python -m ai_gateway.tools.usage_summary logs\\usage.jsonl
```
## 8. Dừng Server
Tại terminal đang chạy Uvicorn, nhấn `Ctrl + C` để dừng server.
