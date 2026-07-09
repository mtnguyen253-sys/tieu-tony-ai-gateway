# Sprint 16 Report: Circuit Breaker HALF_OPEN + Probe Recovery

## 1. Files Changed
- `ai_gateway/core/circuit_breaker.py`
- `ai_gateway/core/executor.py`
- `ai_gateway/tests/test_circuit_breaker.py`
- `ai_gateway/tests/test_executor.py`
- `TECH_DEBT.md`
- `ROADMAP.md`
- `AGENTS.md`
- `src/data.ts` (sync)

## 2. Design Decisions
- **HALF_OPEN State Machine**: Triển khai cơ chế kiểm soát `HALF_OPEN` thông qua thuộc tính `probe_in_flight` trong `ProviderState`.
- **Probe Logic**: Khi provider đang ở trạng thái `HALF_OPEN`, chỉ duy nhất 1 request đầu tiên được cấp quyền thăm dò (probe) và gán `probe_in_flight = True`. Các request sau sẽ bị từ chối (`is_available` trả về False) cho tới khi probe hoàn thành và cập nhật trạng thái mới (`CLOSED` hoặc `OPEN`).
- **ExecutionEngine Integration**: Bổ sung cơ chế gọi `record_success` (đưa Circuit về `CLOSED`) hoặc `record_failure` (đưa Circuit về lại `OPEN`) ngay trong block `try-except` khi thực thi provider.
- **Timeout Exception Handling**: Bổ sung xử lý riêng rẽ `TimeoutException`: Lỗi timeout sẽ chỉ kích hoạt circuit trip (đưa về `OPEN`) nếu system đang thử nghiệm (probe) ở mode `HALF_OPEN`.

### State Transition Table
| Current State | Event/Condition | Action | New State | `probe_in_flight` | `lock_until` |
| --- | --- | --- | --- | --- | --- |
| `CLOSED` | Provider Failed (Rate Limit/Unavailable) | `record_failure()` -> `trip()` | `OPEN` | `False` | `now() + duration` |
| `OPEN` | `now() >= lock_until` | Check `get_state()` | `HALF_OPEN` | `False` | Unchanged |
| `HALF_OPEN` | `is_available()` called (first time) | Allow request | `HALF_OPEN` | `True` | Unchanged |
| `HALF_OPEN` | `is_available()` called (subsequent) | Deny request | `HALF_OPEN` | `True` | Unchanged |
| `HALF_OPEN` | Provider Success | `record_success()` | `CLOSED` | `False` | `0.0` |
| `HALF_OPEN` | Provider Failed (incl. Timeout) | `record_failure()` -> `trip()` | `OPEN` | `False` | `now() + duration` |

## 3. Assumptions
- Các `ProviderUnavailableException`, `RateLimitException` mặc định đều luôn bị coi là critical network failures (Trip ngay lập tức).
- Timeout là lỗi có thể ngẫu nhiên hoặc thoáng qua, nên không trigger trip circuit breaker (khi đang `CLOSED`), nhưng đặc biệt nguy hiểm nếu đang ở trạng thái `HALF_OPEN`, do đó sẽ fallback thẳng về `OPEN`.
- Quản lý `probe_in_flight` thông qua boolean (không sử dụng Atomic Integer hay Locks phức tạp), vì môi trường Python hiện tại giả định single process hoặc GIL lock là đủ trong kiến trúc thiết kế mock hiện thời. Đảm bảo chỉ 1 request trở thành probe.

## 4. Architecture Review
Hệ thống xử lý đúng đắn cơ chế phục hồi Circuit Breaker. Tuy nhiên, việc chạy Test Suite chưa thành công hoàn toàn (không PASS 100%) do giới hạn của môi trường không cài đặt sẵn `pytest`.

## 5. Technical Debt
- **TD-001 (Circuit Breaker HALF_OPEN implementation)** is formally **RESOLVED** via this Sprint.
- Hệ thống vẫn đang chạy Synchronous (TD-003) và chưa có Async I/O, đây là bottle-neck hiệu năng thực tế.

## 6. External Public API Changed?
- Không.

## 7. Internal API Changed?
- Có bổ sung thêm `record_success(provider_name)` và `record_failure(provider_name, ...)` vào `CircuitBreaker`.

## 8. Breaking Change?
- Không. Interface hiện tại vẫn giữ nguyên (tương thích lùi), chỉ bổ sung API.

## 9. Sprint Recommendation
- Lõi hệ thống (Core Engine, CircuitBreaker, Routing) đã gần như hoàn thiện. Đề xuất chuẩn bị cho **Milestone 2 - Public Gateway** (Sprint 17), tập trung vào các API REST tương thích OpenAI.
