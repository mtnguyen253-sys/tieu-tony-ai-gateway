# Báo Cáo Sprint 22: Basic Streaming / OpenAI-compatible stream=True

## Files Changed
- `ai_gateway/api/schemas.py`: Thêm `stream: Optional[bool] = False` vào `ChatCompletionRequest`.
- `ai_gateway/protocols/cap.py`: Thêm `stream: bool = False` vào `AgentRequest`.
- `ai_gateway/core/executor.py`: Bổ sung phương thức `execute_stream()` để xử lý luồng streaming, gọi `provider.stream()` và bọc logic ghi nhận UsageLedger/Budget.
- `ai_gateway/core/orchestrator.py`: Bổ sung `execute_stream()` để route và thực thi stream an toàn.
- `ai_gateway/adapters/base.py`: Thêm interface `stream(self, request: AgentRequest)` cho provider.
- `ai_gateway/adapters/openrouter.py`: Triển khai phương thức `stream()`, sử dụng `httpx` SSE parser để stream từng chunk từ OpenRouter. Handle các lỗi HTTP ban đầu.
- `ai_gateway/api/app.py`: Cập nhật endpoint `/chat/completions` để hỗ trợ trả về `StreamingResponse` với chuẩn `text/event-stream` nếu `req.stream = True`.
- `ai_gateway/core/usage.py`: Thêm `stream: bool = False` vào `UsageEvent`.
- `ai_gateway/tests/test_stream.py`: Thêm các unit test dành riêng cho streaming (success, rate limit trước stream).
- `examples/smoke_streaming.py`: Thêm script để manual test streaming.
- `RUN_LOCAL.md`: Cập nhật hướng dẫn chạy test streaming.
- `TECH_DEBT.md`: Cập nhật các tech debt liên quan đến streaming.

## Design Decisions
- **Executor Stream Wrapper**: Sử dụng generator để bọc (wrap) chunk iterator của provider. Giúp `ExecutionEngine` vẫn có thể tính latency, đếm token và log errors mà không phá vỡ pipeline.
- **Error Behavior**: Nếu lỗi xảy ra *trước* khi stream bắt đầu (VD: Auth, Rate Limit), exception sẽ được ném lên bình thường, kích hoạt Fallback/Retry và trả JSON 401/429. Nếu lỗi xảy ra *sau* khi bắt đầu stream, generator sẽ tự động yield chunk error (`finish_reason: "error"`) và ngắt stream thay vì HTTP 500 (vì HTTP headers đã trả 200 trước đó).
- **Usage Ledger trong Streaming**: Usage được trích xuất từ chunk cuối cùng (nếu provider có trả). Nếu không có, Ledger vẫn ghi nhận sự kiện thành công với tokens là `None`. 
- **OpenRouter `ensure_ascii`**: Sử dụng `json.dumps(chunk, ensure_ascii=False)` để đảm bảo UTF-8/Unicode được truyền đúng chuẩn OpenAI.

## Assumptions
- Hầu hết các client hỗ trợ OpenAI SDK đều đọc format chunk SSE chuẩn (`"data: {...}\n\n"`).
- Việc xử lý `mid-stream fallback` (chuyển sang provider khác giữa lúc stream đang chạy và chắp nối câu văn) là không bắt buộc trong MVP và đã được log lại vào Tech Debt.
- `tools` (function calling) chưa được ưu tiên hỗ trợ trong streaming ở sprint này.

## Architecture Review
- Việc bổ sung `execute_stream` vào Orchestrator và Executor giữ cho hệ thống tương thích tốt với luồng non-streaming hiện hữu.
- Bằng cách chuẩn hoá output của `provider.stream()` thành dạng từ điển (dictionary), API layer không bị trói buộc với bất kỳ một cấu trúc SSE lỏng lẻo nào của backend, giữ code clean và dễ bảo trì.

## Technical Debt
Xem chi tiết trong `TECH_DEBT.md`. Nổi bật:
- Chưa xử lý fallback giữa stream.
- Chưa hỗ trợ stream event tuỳ biến cho tool calling.

## API Changes
- **External Public API Changed?**: Có, endpoint `/chat/completions` giờ đã hỗ trợ `stream: true` và trả về `StreamingResponse`. Cấu trúc JSON khi `stream: false` giữ nguyên 100% độ tương thích.
- **Internal API Changed?**: Có, bổ sung phương thức `execute_stream` ở Executor và Orchestrator, thêm `stream()` ở Provider.
- **Breaking Change?**: Không. Những API hiện hữu không bị ảnh hưởng.

## Sprint Recommendation
- PASS.
- Sẵn sàng chuyển giao Sprint 23 với các tính năng bổ trợ hoặc test tương thích (VD: Tool Calling) hoặc Auth.
