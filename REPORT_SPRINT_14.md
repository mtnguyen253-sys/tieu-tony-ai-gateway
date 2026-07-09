# Báo Cáo Cuối - Sprint 14 (Fallback Strategy)

## 1. Các file thay đổi
- `ai_gateway/core/fallback.py` (Tạo mới): Định nghĩa `FallbackStrategy`, `NoFallbackStrategy`, và `ProviderFallbackStrategy`.
- `ai_gateway/tests/test_fallback.py` (Tạo mới): Các kịch bản kiểm thử (test 1 đến test 7) đảm bảo cơ chế Fallback hoạt động đúng đắn.
- `ai_gateway/core/executor.py` (Sửa đổi): Bổ sung thêm `CircuitOpenException`, `ValidationException`, `AuthenticationException`. Chấp nhận tham số `provider` trong phương thức `execute` của `ExecutionEngine` để cho phép Fallback/Orchestrator truyền cụ thể provider thay vì tự gọi `Router` bên trong.
- `ai_gateway/core/orchestrator.py` (Sửa đổi): Bổ sung tiêm (inject) `FallbackStrategy` qua constructor. Điều chỉnh lại `execute` để kết nối chuỗi `FallbackStrategy` -> `RetryStrategy` -> `ExecutionEngine`.

## 2. Design Decisions
- **Strategy Pattern cho Fallback**: Phân tách hoàn toàn logic Fallback ra khỏi Orchestrator.
- **Dependency Injection**: `FallbackStrategy` nhận `PolicyRouter` và `ExecutionEngine` để làm việc. Orchestrator nhận `FallbackStrategy` qua constructor.
- **Không thay đổi Router Algorithm**: `FallbackStrategy` không tự chọn provider mà thay vào đó thêm danh sách `excluded_providers` vào `context` và gọi lại `PolicyRouter.route()`. Điều này đáp ứng nguyên tắc Open/Closed Principle cho Router.
- **Exception Whitelisting**: Chỉ kích hoạt Fallback khi gặp `ProviderUnavailableException`, `CircuitOpenException`, hoặc khi Router trả về `NoProviderAvailableException`. Các lỗi như `AuthenticationException` hoặc `ValidationException` sẽ re-raise ngay.
- **Chỉnh sửa ExecutionEngine**: Để bảo đảm `FallbackStrategy` có quyền quyết định chọn Provider mới, phương thức `ExecutionEngine.execute` được mở rộng thêm tuỳ chọn nhận `provider`. Điều này giúp `FallbackStrategy` "chỉ định" Provider cụ thể vào Engine (sau khi Fallback đã tương tác với Router). Không phá vỡ Public API cũ vì tham số này là Optional.

## 3. Assumptions
- Giao diện `FallbackStrategy` `execute(self, operation, **kwargs)` được sử dụng thay cho chữ ký gốc để truyền được `context` và `requirement` vào quá trình chọn lại provider bằng Router.
- Các Exception từ Circuit Breaker đã được định nghĩa tại mức Engine/Fallback để đảm bảo quá trình hoạt động không bị crash do thiếu class ngoại lệ.
- Request được sử dụng xuyên suốt không lưu trữ state ẩn nào, `context` (từ điển) được nhân bản hoặc làm mới (mutated) mỗi lần Retry/Fallback.

## 4. Architecture Review
- **SOLID**: 
  - *Single Responsibility Principle*: Hoàn toàn tuân thủ, `FallbackStrategy` chỉ tập trung vào việc quản lý vòng lặp đổi Provider, `Router` đảm nhiệm chọn, `ExecutionEngine` đảm nhiệm gọi API.
  - *Open/Closed Principle*: Các thành phần đều mở để thêm Strategy mới nhưng không cần phải sửa class Orchestrator gốc (đã được abstract hoá qua Interface).
- **Coupling**: Bằng cách bọc closures (`_operation`) và dependency injection, ta đã tách biệt hoàn toàn Fallback khỏi Retry mà không tạo Coupling.
- **Circular Dependency**: Không. `orchestrator.py` gọi `fallback.py`, `fallback.py` gọi interface, không có chiều ngược lại.
- **Public API**: Thêm tham số optional vào `ExecutionEngine.execute` là an toàn.

## 5. Technical Debt
- **Vấn đề (Issue)**: Phương thức `ExecutionEngine.execute` hiện tại vừa có khả năng gọi Router (nếu không được chỉ định provider) lại vừa thi hành (nếu được truyền). Trách nhiệm này đang bị lẫn lộn một chút.
- **Tác động (Impact)**: Nếu Orchestrator trong tương lai tiếp tục phức tạp lên, Engine có thể vô tình làm trái ý định của Fallback.
- **Giải pháp (Recommendation)**: Tách triệt để Router ra khỏi ExecutionEngine. ExecutionEngine CHỈ nên làm nhiệm vụ gọi mạng (HTTP client / Adapter). Logic Router nên chuyển hẳn sang Orchestrator hoặc một `RoutingOrchestrator` chuyên trách.
- **Sprint lên kế hoạch**: Sprint 15 hoặc Refactoring Phase.

## 6. Extension Points
- Có thể kết hợp `FallbackStrategy` với cơ chế tính phí (Budget Fallback): Nếu provider xịn hết budget, có thể tự fallback sang Google Free.
- Triển khai Exponential Backoff trong quá trình chờ Circuit Breaker đóng lại (Half-Open) thay vì chỉ chọn ngay provider khác.

## 7. Sprint 15 Recommendation
- Tiến hành thực thi **Async Refactoring** cho toàn bộ pipeline để hỗ trợ Concurrency và Streaming một cách chính thức, đồng thời dọn dẹp Technical Debt (tách Router ra khỏi Engine).
- Xem xét chuẩn hoá và tích hợp các công cụ Observability (Logging/Metrics).
