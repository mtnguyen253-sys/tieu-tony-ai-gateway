# Sprint 18A Report: Runtime Wiring & Safety Test

## 1. Files Changed
- `ai_gateway/tests/test_runtime.py` (Created)
- `ai_gateway/api/app.py` (Verified)

## 2. Design Decisions
- **Runtime Testing**: Thêm file `test_runtime.py` để kiểm chứng việc import FastAPI application (`app`, `create_app`) hoàn toàn an toàn và không bị lỗi.
- **Dependency Injection for Testing**: Chèn `MockOrchestrator` thông qua `create_app(orchestrator=MockOrchestrator())` cho phép test mock runtime trả về HTTP 200 mà không cần sửa đổi production path.
- **Graceful Failure**: Default runtime sẽ ném lỗi 503 Service Unavailable (chuẩn format OpenAI) khi không có provider khả dụng, không để xảy ra lỗi nội bộ HTTP 500 do Unhandled Exception.

## 3. Assumptions
- Giả định rằng môi trường host FastAPI có đủ dependencies (`fastapi`, `uvicorn`, v.v.). API Key authentication và Streaming response được tạm hoãn lại và không thuộc scope của sprint này.

## 4. Architecture Review
Hệ thống sử dụng Application Factory Pattern rất hiệu quả cho phép thay thế (mock) các layer tuỳ ý (Orchestrator, Registry) trong quá trình testing. Các lớp Layered Architecture đang duy trì tốt tính lỏng lẻo (loose coupling) của mình.

## 5. Technical Debt
- **TD-003**: Migration sang async flow vẫn đang chờ.
- **TD-008**: Chưa có Streaming.
- **TD-009**: Chưa có Authentication.

## 6. External Public API Changed?
Không. Contract vẫn tuân thủ như Sprint 17.1 (trả về 503 khi Provider Unavailable).

## 7. Internal API Changed?
Không.

## 8. Breaking Change?
Không có Breaking Change.

## 9. Sprint Recommendation
Hệ thống hiện tại đã đủ an toàn (Safety Test passed) ở mức độ import và bootstrap. Sprint tiếp theo có thể cân nhắc tích hợp CLI starter (RUN_LOCAL) hoặc tiến tới xử lý Authentication (TD-009) để sẵn sàng cho môi trường public.
