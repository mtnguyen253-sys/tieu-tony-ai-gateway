# REPORT_SPRINT_31

## 1. Files Changed
- `ai_gateway/core/health.py`: Tạo mới `ProviderHealthState` và `InMemoryHealthTracker`.
- `ai_gateway/core/executor.py`: Cập nhật `ExecutionEngine` để gửi event (success, error, timeout, rate_limit) về `health_tracker`.
- `ai_gateway/core/router.py`: Cập nhật `PolicyRouter` để trừ điểm `ScoringEngine` (penalty) dựa trên `health_score`.
- `ai_gateway/api/app.py`: Cập nhật instance wiring và `/health` endpoint để trả về health tracking metadata an toàn.
- `ai_gateway/config/settings.py`: Thêm cấu hình cờ `AI_GATEWAY_HEALTH_SCORING_ENABLED`.
- `ai_gateway/tools/usage_summary.py`: Bổ sung section Reliability (thống kê success rate, rate limit rate, latency by provider/model).
- `ai_gateway/tools/config_check.py`: Bổ sung trạng thái tính năng health scoring.
- `ai_gateway/tests/test_health.py`: Bổ sung các ca kiểm thử cho health score calculations, penalty, và executor integration.
- `ai_gateway/tests/test_router.py`: Bổ sung test kiểm thử penalty router.
- `RUN_LOCAL.md`: Cập nhật tài liệu HDSD.
- `TECH_DEBT.md`: Cập nhật nợ kỹ thuật.

## 2. Health Tracker Behavior & Scoring Formula
Health score khởi điểm là 1.0. Sau mỗi request:
- Success < 80%: phạt tỉ lệ (lên tới -0.3).
- Rate Limit rate > 10%: phạt điểm tỉ lệ.
- Timeout rate > 5%: phạt điểm.
- Server error rate > 5%: phạt điểm.
- High Latency > 5000ms: phạt điểm.
- Recent Auth Error (< 1h): phạt cực nặng (-0.5).
Điểm `health_score` nằm trong khoảng [0.0, 1.0]. 

## 3. Router Integration
Trong `PolicyRouter`, điểm penalty tính bằng `(1.0 - health_score) * 10.0`. Nếu provider bị điểm 0.0 (hoàn toàn hỏng), sẽ bị penalty lên tới 10 điểm, đẩy thẳng xuống độ ưu tiên cực thấp để nhường lượt cho provider khoẻ hơn (Dựa theo config). Trọng số Cache Sprint 28 và Tier Bonus Sprint 30 được giữ nguyên.

## 4. Usage Report Reliability Section
`usage_summary.py` giờ đây trích xuất tổng request success/error/rate_limit từ toàn bộ file `usage.jsonl`, gom nhóm theo Provider/Model và tính % Tỷ lệ thành công (Success Rate) cùng với Average Latency (độ trễ trung bình).

## 5. Tests Run
Tất cả 152 test trong pytest suite đều được xác nhận pass.
`test_health.py` xác minh logic trừ điểm khi timeout, lỗi authentication và rate limit.
`test_cache_routing.py` và `test_cooldown.py` được xác nhận giữ nguyên hành vi không phá vỡ.
`config_check` không print bí mật ra bên ngoài.

## 6. Technical Debt
Health Tracker được implement in-memory nên sẽ bị clear sau khi server khởi động lại và không sync cross-instance.

## 7. Breaking Change?
Không.

## 8. External Public API Changed?
`/health` trả về thêm 3 properties nhẹ nhàng: `health_tracking_enabled`, `unhealthy_provider_count`, `degraded_provider_count`. Không có thay đổi nào về `/v1/chat/completions`.

## 9. Sprint Recommendation
- PASS. Sẵn sàng cho các Sprint tiếp theo (Có thể triển khai Persistence Redis cho Health Tracking nếu cần).
