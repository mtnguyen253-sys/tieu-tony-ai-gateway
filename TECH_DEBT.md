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

## TD-010
- **Title**: Provider Error Schema Standardization
- **Description**: Error mapping đang implement trực tiếp trong app.py cho từng HTTP Status. Khi thêm nhiều Provider, có thể cần một Error mapper riêng để giữ code DRY.
- **Impact**: Code trong app.py có thể trở nên rối khi có quá nhiều logic handle lỗi đặc thù.
- **Priority**: Low
- **Status**: Open
- **Created**: Sprint 20A
- **Recommendation**: Xây dựng ErrorMapper utility hoặc Middleware để gom nhóm xử lý lỗi thành chuẩn OpenAI chung.

## TD-011
- **Title**: In-memory Cooldown State
- **Description**: `ProviderCooldownManager` hiện tại đang lưu trạng thái cooldown in-memory bằng dictionary. Khi triển khai multi-process hoặc multi-instance (VD: Gunicorn/Uvicorn workers, K8s pods), trạng thái này sẽ không được đồng bộ, dẫn đến việc rate limit vẫn có thể bị chạm (dumb retry trên các instance khác).
- **Impact**: Không hoạt động đúng trong môi trường distributed.
- **Priority**: Medium
- **Status**: Open
- **Created**: Sprint 20B
- **Recommendation**: Triển khai shared store (như Redis) để quản lý cooldown state cho toàn bộ Gateway cluster.

### Sprint 20C - Usage & Cost Ledger
- **Static Pricing Table**: Currently, model prices are hardcoded in `ai_gateway/config/model_prices.py`. This table needs to be auto-refreshed or managed via external configuration in the future.
- **Single-instance Ledger**: `JsonlUsageLedger` writes to local files, which is not suitable for multi-instance deployments. Needs an upgrade to SQLite, Postgres, ClickHouse, or an external metrics backend.
- **Lack of Quality Metric**: We record usage and error, but lack a quality score (e.g., user feedback) to optimize routing based on response quality.
- **Missing Budget-aware Router**: Usage is recorded but not yet used by the Router to enforce budget caps dynamically.

### Sprint 21A
- **Persistent Storage for Budgets**: `BudgetManager` relies on in-memory counters. A multi-worker environment will have split-brain budget tracking. Need Redis.
- **Exact Pre-computation**: Router checks budget against a static `capability.cost` rather than calculating exact predicted tokens for the prompt, which is hard to do synchronously before model choice.

### Sprint 21B
- **Budget Validation**: Hiện chủ yếu bằng smoke script, chưa có dashboard trực quan cho người dùng.
- **Budget State**: Chưa có persistent multi-instance budget state (cần Redis).
- **Quality Score**: Chưa có quality score/user feedback cho budget routing.
- **Price Refresh**: Chưa có automatic price refresh cho các model.

### Sprint 22 - Basic Streaming Support
- **Mid-stream Fallback Chưa Hỗ Trợ**: Nếu provider bị lỗi trong quá trình đang stream (đã gửi chunk đầu tiên), API chỉ trả về một chunk error (`finish_reason: error`) và kết thúc stream, thay vì transparently fallback qua provider khác. Fallback giữa chừng với LLM là rất khó do context và partial content.
- **Thiếu Usage Trong Streaming**: Một số provider khi streaming không trả về metadata usage (token counts). UsageLedger đang được handle an toàn (record `None`) nhưng điều này làm giảm độ chính xác của cost tracking nếu provider không hỗ trợ tuỳ chọn "include_usage".
- **Streaming Retry Chỉ Áp Dụng Trước Khi Bắt Đầu**: `RetryStrategy` và `FallbackStrategy` chỉ catch được lỗi kết nối ban đầu, không áp dụng cho lỗi bị đứt gãy giữa chừng.
- **Streaming Tool Calls Chưa Hoàn Thiện**: Streaming hiện tại chỉ parse chunk text cơ bản, chưa hỗ trợ đầy đủ các delta của function/tool calls nếu có.
- **SSE Client Compatibility**: Cần test thêm với các client chuẩn (OpenAI SDK, Codex, OpenClaw) để đảm bảo không có vấn thích tương thích về timing hoặc format chunk.

### Sprint 23 - OpenAI SDK Compatibility
- **Chưa có auth/API key validation nội bộ**: Các request được gửi từ OpenAI SDK vẫn chưa được auth (API key validation ở phía Gateway) mà chỉ bypass.
- **OpenAI SDK compatibility mới test với Python SDK**: Chưa test với Node SDK.
- **Tool calls streaming compatibility chưa hoàn thiện**: Nếu hỗ trợ tool calling/functions, cần thêm logic map format cho SDK.
- **Mid-stream fallback chưa hỗ trợ**: Nhắc lại tech debt cũ, vẫn chưa fallback giữa dòng.
- **Một số SDK có thể yêu cầu header/response edge cases khác**: Cần test kỹ hơn cho production cases (VD prompt caching header).

### Sprint 24 - Packaging / Deployment / Config Profiles
- **Chưa có Dockerfile**: Để thuận tiện deploy production, cần có `Dockerfile` và `docker-compose.yml`.
- **Chưa có systemd/service install**: Cho việc deploy native trên VPS.
- **Chưa có auth/API key middleware**: `/chat/completions` vẫn không validate client API key.
- **Chưa có production logging/observability chuẩn**: Log level đang được parse ở config nhưng chưa đưa vào root logger chuẩn (như Loguru hay structlog).
- **Chưa có Redis/shared state**: Rate limiting, cooldown, budget mode hiện tại hoàn toàn in-memory, không chạy đa tiến trình được an toàn.

### Sprint 28
- Chưa có dynamic learning từ historical cache ratio.
- Chưa có provider-specific prompt cache API.
- Chưa có persistent analytics DB.
- Chưa có tokenizer chính xác.
- Chưa có cache write/read separation đầy đủ cho từng provider.

### Sprint 29
- **Dashboard**: Chưa có dashboard runtime config.
- **Quota**: Chưa có persistent quota state.
- **Health**: Chưa có provider health probe định kỳ.
- **Security**: Chưa có encrypted secret store.
- **Routing**: Chưa có dynamic routing learning từ production usage.

### Sprint 30
- **Dynamic Task Classification**: The `TaskClassifier` currently relies on heuristic keyword matching and simple length checks. It should ideally use a fast, local ML model or semantic embedding classifier for greater accuracy.
- **Task Classification Overhead**: Classification adds a small processing overhead before routing.
- **Heuristics Limitation**: Keyword-based classification might incorrectly categorize tasks if user intent is complex but uses simple keywords.
- **Missing Tokenizer**: The length check uses a naive `len(char) / 4` approximation. We should integrate a real fast tokenizer like `tiktoken`.

### Sprint 31
- **In-Memory Health State**: `InMemoryHealthTracker` hiện chỉ lưu trong bộ nhớ (in-memory), sẽ mất dữ liệu khi restart service.
- **Lack of Multi-Process State**: Chưa có Redis/SQLite persistence cho health tracking, chạy gunicorn nhiều worker sẽ không đồng nhất.
- **No Active Health Probe**: Chưa có cơ chế ping/health check định kỳ độc lập với traffic thực tế (active probe).
- **Time Decay**: Thuật toán trừ điểm chưa có cơ chế phục hồi điểm theo thời gian chuẩn mực (decay function) hoàn chỉnh, ngoại trừ auth error.
- **Dashboard**: Chưa có giao diện dashboard theo dõi provider health.
- **Quality Signal**: Chưa có user feedback signal thực sự để chấm điểm model quality ngoài network layer.

### Sprint 32 - Connect Codex / Hermes / OpenClaw through Tiểu Tony
- **Client Authentication Bypass**: Local gateway intentionally bypasses strict client API key validation (accepts dummy keys like `dummy`). For multi-user staging/production, we need a secure API Key Validation Middleware.
- **Manual Verification Dependency**: Verifying compatibility for specific tools relies on running manual smoke scripts or checking logs manually. We need an automated integration test suite that spins up a mock client for each supported tool.
- **Lack of Granular Client Tagging**: Usage events in `logs/usage.jsonl` record provider/model metadata, but lack explicit tracking of which external client (e.g., Codex vs. Hermes vs. OpenClaw) initiated the request.
- **Unified Stream-Ledger Synchronization**: Streamed requests have basic recording, but exact token counts are approximated or omitted if backend providers do not stream usage blocks, affecting the precision of cost ledger tracking.
