# Sprint 19 Bugfix Report: Fix Local Test Regression After OpenRouter Runtime Wiring

## 1. Files Changed
- `ai_gateway/tests/test_adapters.py` (Modified)
- `ai_gateway/tests/test_api.py` (Modified)

## 2. Design Decisions
- **Fix `OpenRouterAdapter` Unit Tests**: 
  - Khắc phục lỗi `TypeError` do thiếu tham số `api_key` bằng cách truyền dummy `api_key="test-key"` vào các bài test khởi tạo `OpenRouterAdapter`.
  - Không gọi trực tiếp network (OpenRouter API) thật trong unit test (`test_openrouter_adapter_chat_integrity`). Sử dụng `@patch("ai_gateway.adapters.openrouter.httpx.Client")` để mock toàn bộ phản hồi từ HTTP client, giả lập chính xác format response JSON của OpenRouter. Đảm bảo test chạy an toàn, tách biệt hoàn toàn với môi trường bên ngoài mà không cần cấu hình API Key.
- **Fix `test_list_models`**: Sửa test `/models` để không yêu cầu mảng `data` phải chứa dữ liệu (`len > 0`) trong default mock runtime. Vì ở Sprint 18 & 19, default runtime không có cấu hình API Key sẽ trả về mảng rỗng `[]` để tránh lộ mô hình ảo. Code test đã được update để chỉ assert:
  - `status_code == 200`
  - `object == "list"`
  - `data` là mảng hợp lệ (`isinstance(list)`).

## 3. Assumptions
- Các chỉnh sửa mock trong bài test cover đúng JSON API Schema của OpenRouter. Code logic cốt lõi không bị thay đổi. 

## 4. Architecture Review
Unit test đã hoạt động hoàn toàn offline, tránh hiện tượng flaky test hay phụ thuộc API Key như mong đợi. Không có thay đổi về kiến trúc hệ thống.

## 5. Technical Debt
- **TD-003**: Migration sang async flow.
- **TD-008**: Chưa có Streaming.
- **TD-009**: Chưa có Gateway Authentication.

## 6. External Public API Changed?
Không.

## 7. Internal API Changed?
Không. Test scope modified only.

## 8. Breaking Change?
Không.

## 9. Sprint Recommendation
Test suite đã lấy lại trạng thái PASS 100% (Local Environment). Gateway an toàn để tiếp tục phát triển. Sprint tiếp theo có thể ưu tiên tập trung xử lý Authentication (TD-009) để public gateway an toàn.
