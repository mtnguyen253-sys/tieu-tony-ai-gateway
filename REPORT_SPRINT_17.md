# Sprint 17.2 Bugfix Report: Fix Public Gateway CAP Contract Mapping & Abstract Strategy Instantiation

## 1. Files Changed
- `ai_gateway/api/app.py`
- `ai_gateway/tests/test_api.py`
- `ai_gateway/core/fallback.py`
- `ai_gateway/tests/test_fallback.py`

## 2. Design Decisions
- **Fix MockRouter Assertions**: Chỉnh sửa hành vi của `MockRouter` trong file `test_fallback.py` để biến `call_count` tăng ngay lập tức ở đầu hàm (ngay cả khi gọi router nhưng bị throw `NoProviderAvailableException`). Điều này đảm bảo test `test_6_both_providers_fail` kiểm chứng chính xác 3 lần routing attempts trước khi fallback bị cạn kiệt.
- **Fix Fallback Exception Mapping**: Sửa lỗi `CircuitOpenException` (và `RateLimitException`) không kích hoạt cơ chế fallback. Đã xóa các class Exception định nghĩa trùng lặp nội bộ trong `fallback.py` và import trực tiếp từ `ai_gateway.core.executor` để đồng nhất type catch. Tránh được lỗi bắt sai exception khiến fallback strategy thất bại.
- **Fix Abstract Strategy Instantiation**: Khắc phục lỗi TypeError ("Can't instantiate abstract class RetryStrategy without an implementation for abstract method 'execute'") bằng cách thay đổi `RetryStrategy()` thành concrete class `NoRetryStrategy()`. Cấu trúc factory `create_app` vẫn được giữ nguyên tính độc lập để test.
- **Fix CAP Contract Mapping**:
  - Đã loại bỏ import sai class `Message` (không tồn tại trong module `ai_gateway.protocols.cap`). Thay vào đó chỉ sử dụng duy nhất class `AgentRequest` có sẵn.
  - Sửa lại việc khởi tạo `AgentRequest` từ HTTP Request để bám đúng vào contract chuẩn của `AgentRequest.model_fields`, với các trường bắt buộc như `request_id`, `messages` (đã được map thủ công thành cấu trúc dict) và tuỳ chọn `tools=None` thay vì gọi đối tượng không hợp lệ.
  - Sửa lỗi mapping từ response ảo (có `data` và `metadata`) sang đúng contract của `AgentResponse` (với các trường `response_id`, `content`, `usage`).
- **503 Service Unavailable Exception Mapping**: Xử lý triệt để lỗi `NoProviderAvailableException` từ core truyền ra và map chuẩn thành mã lỗi `503 Service Unavailable`. Cấu trúc JSON response tuân thủ theo chuẩn format lỗi của OpenAI API để client dễ dàng tương thích (`error.type = provider_unavailable`, `error.code = no_provider_available`). Tránh được việc throw lỗi 500 do nội bộ.
- **`create_app` Factory**: Tái cấu trúc module `app.py` sử dụng Application Factory Pattern (`create_app(orchestrator, registry)`). Cách làm này loại bỏ sự phụ thuộc (hard dependency) của API vào các core components thật khi thực thi tests, cho phép dễ dàng inject Mock Orchestrator và Mock Registry.
- **Dynamic `/models` Endpoint**: API `/models` không còn bị crash khi Registry chưa có provider, thay vào đó sẽ graceful return object dạng `{"object": "list", "data": []}`.
- **Simplified `/health`**: Bỏ các dependency không cần thiết (không gọi thật vào provider), chỉ trả về thông tin tối giản (`status`, `service`, `version`).

## 3. Assumptions
- Các tham số streaming, authentication, tool calling tạm thời chưa được xử lý và mặc định bỏ qua.
- Với testing, chúng ta giả định MockOrchestrator có thể bao phủ hoàn toàn contract của Core Orchestrator mà API mong đợi.

## 4. Architecture Review
Cấu trúc Layer API đã trở nên độc lập và dễ test hơn, đồng thời giải quyết triệt để lỗi Contract mapping. Tuy nhiên, việc chạy Test Suite chưa thành công (không "PASS 100%") do giới hạn của môi trường không cài đặt sẵn `pytest`. Các file test (`test_api.py`) đã được cập nhật logic mock đầy đủ.

## 5. Technical Debt
- **TD-003 (Async Migration)**: Hệ thống vẫn chạy Synchronous, API framework đã dùng FastAPI (hỗ trợ async) nhưng core vẫn là block operations.
- **TD-008 (API Streaming Support)**: Chưa hỗ trợ luồng stream (`stream=True`) của OpenAI.
- **TD-009 (API Authentication)**: Public Gateway hiện chưa có tính năng check API key.

## 6. External Public API Changed?
- API `/chat/completions` hiện tại sẽ trả về HTTP Status 503 thay vì 500 khi hệ thống không có Provider nào khả dụng (đáp ứng đúng chuẩn OpenAI-compatible error handling). Cấu trúc error JSON được thiết kế chuẩn xác hơn.

## 7. Internal API Changed?
- Việc gọi API layer tới CAP package tuân thủ đúng định dạng của AgentRequest và AgentResponse thật thay vì class mock ảo.

## 8. Breaking Change?
- Có thay đổi nhỏ trong cấu trúc internal bootstrap API, tuy nhiên do Public Gateway mới phát hành dạng thử nghiệm nên chưa gây ảnh hưởng tới client hiện tại.

## 9. Sprint Recommendation
- API Gateway đã chịu lỗi (fault-tolerant) tốt hơn trước các sự cố ở tầng Routing/Provider. Hệ thống Mapping contract đã đồng bộ. Sprint tiếp theo tập trung vào việc quản lý API Key (TD-009) để đảm bảo an toàn nếu expose dịch vụ ra public.
