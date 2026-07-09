# Báo Cáo Cuối - Sprint 13 (Retry Strategy)

## 1. Các file thay đổi
- `ai_gateway/core/retry.py` (Tạo mới)
- `ai_gateway/tests/test_retry.py` (Tạo mới)
- `ai_gateway/core/orchestrator.py` (Sửa đổi: Inject `RetryStrategy` và bọc `ExecutionEngine` bằng retry block)

## 2. Design Decisions
- Sử dụng **Strategy Pattern**: `RetryStrategy` định nghĩa interface chung cho nhiều chiến lược Retry. `FixedRetryStrategy` và `NoRetryStrategy` triển khai cụ thể, tách biệt hoàn toàn khỏi Orchestrator.
- **Dependency Injection**: Orchestrator nhận `retry_strategy` qua tham số khởi tạo thay vì tự thiết lập.
- **Exception Whitelisting**: `FixedRetryStrategy` chỉ retry khi gặp `TimeoutException`. Các exception khác (như `RateLimitException`, `ProviderUnavailableException`, `UnknownProviderException`, `AuthenticationException`) sẽ được re-raise ngay.
- `RetryStrategy` bọc toàn bộ khối `ExecutionEngine.execute()` thông qua một hàm `Callable` không có tham số (`_operation`).

## 3. Assumptions
- Giả định rằng `TimeoutException` là trường hợp có thể phục hồi nhanh chóng mà không cần Backoff hay Fallback.
- Các exception về RateLimit hay ProviderUnavailable đang được circuit breaker bắt nên không retry trực tiếp vào cùng provider đó ngay lập tức (phù hợp với Fallback ở chặng sau).
- Orchestrator mặc định dùng `NoRetryStrategy` nếu không có strategy nào được inject vào.

## 4. Technical Debt
- **Blocking Retry Loop**: Vòng lặp `while True:` hiện đang là đồng bộ (synchronous). Khi chuyển sang `async`, vòng lặp này cần phải refactor sử dụng `async/await` để tránh chặn event loop.
- **Hardcoded Retry Limit**: `FixedRetryStrategy` vẫn đang dùng magic number hoặc tham số mặc định (3 retries). Có thể sẽ cần đẩy các cấu hình này ra thành biến môi trường hoặc config file ở các Sprint sau.
- Cấu trúc `RetryStrategy` không cho phép truyền các context phụ (như request hay quotas) vào để đưa ra quyết định retry thông minh hơn (ví dụ: đổi Provider nếu hết quota).

## 5. Extension Points cho Sprint 14
- Trong `ExecutionOrchestrator`, thay vì chỉ bọc `engine.execute` bằng `retry_strategy`, ta có thể tạo `FallbackStrategy` hoạt động song song hoặc kết hợp (như gọi `Router` một lần nữa với provider bị loại để thử nghiệm provider dự phòng).
- Thêm cơ chế Exponential Backoff có `Jitter` (để tránh thundering herd) vào hệ sinh thái của `RetryStrategy`.

## 6. Sprint 14 Recommendation
- Đề xuất triển khai **Fallback Strategy** hoặc **Advanced Retry Policy** (Exponential Backoff, Jitter).
- Bổ sung khả năng để Retry/Fallback giao tiếp ngược với Router để lấy Provider dự phòng (thay vì chỉ đâm đầu vào một provider vừa chết).
