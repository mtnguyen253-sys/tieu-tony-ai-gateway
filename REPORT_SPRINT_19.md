# Sprint 19 Report: Real Provider Runtime Wiring

## 1. Files Changed
- `ai_gateway/adapters/openrouter.py` (Modified)
- `ai_gateway/api/app.py` (Modified)
- `examples/smoke_real_provider.py` (Created)
- `RUN_LOCAL.md` (Modified)

## 2. Design Decisions
- **Real Provider Integration**: Đã nâng cấp `OpenRouterAdapter` từ mock object lên real implementation sử dụng thư viện `httpx` (mô phỏng gọi API synchronous theo kiến trúc hiện tại). Bổ sung error handling logic, đảm bảo các lỗi Auth hoặc Server được bắt và map về CAP exceptions.
- **Environment Variables Wiring**: Cập nhật `create_app` trong `app.py` để đọc biến `OPENROUTER_API_KEY`. Nếu có API key hợp lệ, `OpenRouterAdapter` sẽ tự động đăng ký vào registry cho default runtime.
- **Dynamic Endpoint `/models`**: Endpoint trả về danh sách model giờ sẽ dựa trên `OPENROUTER_MODEL` nếu OpenRouter được cấu hình. Nếu không có provider (không có API Key), endpoint vẫn trả về list data rỗng `[]`.
- **Smoke Script bổ sung**: Viết thêm script `smoke_real_provider.py` để test riêng cho real endpoint mà không đụng tới mock/dev path.

## 3. Assumptions
- Giao tiếp vẫn là synchronous vì cốt lõi orchestrator của hệ thống đang ở synchronous (TD-003). Để duy trì Definition of Done, ta không migrate qua asynchronous trong vòng này. 

## 4. Architecture Review
Runtime Wiring đã thành công mà không break các test hiện tại. Registry Pattern và Application Factory phối hợp tốt để tách biệt môi trường Dev (Mocked Orchestrator) và Prod (Real Adapter with Key). Default runtime hiện tại đạt được tính chất an toàn cao: Không có Provider = 503 HTTP Code, không throw HTTP 500 Unhandled Exception.

## 5. Technical Debt
- **TD-003**: Migration sang async flow (đặc biệt bây giờ khi httpx được sử dụng ở sync mode).
- **TD-008**: Chưa có Streaming.
- **TD-009**: Chưa có Gateway Authentication (mặc dù đã tích hợp downstream provider Authentication).

## 6. External Public API Changed?
- API `/models` hiện trả về object linh hoạt theo đăng ký của Registry thay vì fixed mock list.

## 7. Internal API Changed?
- Thay đổi chữ ký constructor của `OpenRouterAdapter` (thêm `api_key` và `default_model`). Tuy nhiên phần này chỉ nội bộ gọi tại bootstrap layer của `app.py`.

## 8. Breaking Change?
Không có Breaking Change.

## 9. Sprint Recommendation
Gateway đã chạy thực tế với provider (OpenRouter). Các bước tiếp theo: Có thể bắt đầu triển khai Authentication Key (TD-009) cho API public, hoặc tiến tới nâng cấp sang kiến trúc Asynchronous (TD-003) cùng Streaming (TD-008) để đáp ứng chuẩn AI Endpoint đầy đủ.
