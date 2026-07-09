# Technical Debt

## TD-001
- **Title**: Circuit Breaker HALF_OPEN implementation
- **Description**: Trạng thái `HALF_OPEN` đã được khai báo nhưng chưa có logic kiểm tra phục hồi tự động (probe requests).
- **Impact**: Provider có thể chuyển thẳng từ OPEN sang CLOSED khi hết thời gian chờ, dễ dẫn đến sập lại hệ thống.
- **Priority**: High
- **Status**: Resolved (Sprint 16)
- **Created**: Sprint 10
- **Recommendation**: Triển khai cơ chế giới hạn 1 request thử nghiệm (probe) khi ở trạng thái HALF_OPEN.

## TD-002
- **Title**: Scoring Engine dynamic normalization
- **Description**: Thuật toán tính điểm sử dụng trọng số cứng mà không chuẩn hoá (normalization) các thang đo khác biệt (ms vs USD).
- **Impact**: Trọng số có thể thiếu chính xác khi các giá trị input có thang đo quá chênh lệch.
- **Priority**: Medium
- **Status**: Open
- **Created**: Sprint 9
- **Recommendation**: Triển khai thuật toán Min-Max Scaling hoặc Softmax.

## TD-003
- **Title**: Synchronous execution pipeline
- **Description**: Toàn bộ luồng thực thi (Router, Engine, Strategy, Orchestrator) đang là thiết kế synchronous.
- **Impact**: Gây blocking thread khi kết nối tới API của provider (I/O bound). Ảnh hưởng nghiêm trọng đến Throughput thực tế.
- **Priority**: Critical
- **Status**: Open
- **Created**: Sprint 11
- **Recommendation**: Refactor toàn bộ core API sử dụng `async/await` và `asyncio`.

## TD-004
- **Title**: Real Provider Integration
- **Description**: Các Adapter (Gemini, OpenRouter) mới chỉ dừng ở mức API chuẩn (Mock objects). Chưa có kết nối mạng thực tế.
- **Impact**: Không thể gửi request AI thật sự trong production.
- **Priority**: High
- **Status**: Open
- **Created**: Phase 2
- **Recommendation**: Tích hợp các SDK chính thức hoặc triển khai HTTP client gọi REST API trực tiếp.

## TD-005
- **Title**: Observability (Telemetry & Metrics)
- **Description**: Hiện chỉ sử dụng Python `logging`. Thiếu các công cụ đo đếm metric như success rate, token usage, timeout count, request latency.
- **Impact**: Rất khó debug và thống kê chi phí, tối ưu hệ thống ở production.
- **Priority**: Medium
- **Status**: Open
- **Created**: Sprint 12.5
- **Recommendation**: Tích hợp metrics gateway như Prometheus hoặc OpenTelemetry.

## TD-006
- **Title**: ExecutionEngine mixed responsibilities
- **Description**: `ExecutionEngine.execute()` vừa hỗ trợ tự gọi Router lại vừa cho phép thực thi nếu provider được chỉ định (tiêm qua arguments).
- **Impact**: Gây lẫn lộn trách nhiệm, tiềm ẩn vi phạm SRP nếu logic routing phức tạp lên.
- **Priority**: High
- **Status**: Resolved (Sprint 15)
- **Created**: Sprint 14
- **Recommendation**: Tách dứt điểm logic gọi Router ra khỏi Engine. Engine chỉ tập trung gọi AI.

## TD-007
- **Title**: Hardcoded Retry Limits
- **Description**: Cấu hình của `FixedRetryStrategy` đang để tham số số lần retry cố định trong class.
- **Impact**: Thiếu linh hoạt với các Policy khác nhau hoặc yêu cầu cấu hình độc lập qua biến môi trường.
- **Priority**: Low
- **Status**: Open
- **Created**: Sprint 13
- **Recommendation**: Xây dựng object Config để tiêm (inject) các thông số timeout, retries vào strategy.

## TD-008
- **Title**: API Streaming Support
- **Description**: Public Gateway v1 mới chỉ hỗ trợ trả kết quả JSON 1 cục, chưa hỗ trợ chế độ Server-Sent Events (SSE) `stream=True` của OpenAI.
- **Impact**: UX kém đối với các tác vụ dài (long-running generation).
- **Priority**: High
- **Status**: Open
- **Created**: Sprint 17
- **Recommendation**: Triển khai `StreamingResponse` trong FastAPI kết hợp với Async I/O (TD-003).

## TD-009
- **Title**: API Authentication & Key Management
- **Description**: Các public endpoint hiện tại hoàn toàn mở (unauthenticated). Chưa có quản lý API keys của người dùng (Gateway users).
- **Impact**: Rủi ro bảo mật, không kiểm soát được lượng truy cập và lạm dụng (abuse) nếu expose ra ngoài.
- **Priority**: Critical
- **Status**: Open
- **Created**: Sprint 17
- **Recommendation**: Xây dựng module middleware/dependency để kiểm tra Bearer Token hợp lệ.
