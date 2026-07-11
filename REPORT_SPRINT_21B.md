# Báo cáo Sprint 21B - Budget-aware Routing Validation + Runtime Smoke

## Files Changed
- `RUN_LOCAL.md`: Thêm tài liệu hướng dẫn cấu hình `AI_GATEWAY_BUDGET_MODE`, `AI_GATEWAY_DAILY_BUDGET_USD`, `AI_GATEWAY_MONTHLY_BUDGET_USD`, và `AI_GATEWAY_MAX_COST_PER_REQUEST`. Sửa cấu trúc heading và thêm lệnh test runtime với real provider.
- `examples/smoke_budget_modes.py` (New): Script smoke test kiểm tra hoạt động của router dưới các điều kiện budget khác nhau mà không cần API key thực tế.
- `ai_gateway/tools/usage_summary.py`: Thêm logic đọc `AI_GATEWAY_DAILY_BUDGET_USD` từ ENV và cảnh báo khi tổng chi phí vượt 80% ngân sách ngày, hoặc khi một provider/model chiếm hơn 70% tổng chi phí.
- `ai_gateway/tests/test_smoke.py` (New): Chạy script smoke qua subprocess cho cả 3 mode (normal, economy, emergency) để đảm bảo script chạy thành công mà không crash.
- `ai_gateway/tests/test_usage_summary_warnings.py` (New): Viết Unit test đảm bảo `usage_summary.py` in ra đúng các cảnh báo theo yêu cầu (vượt budget, provider chiếm tỉ trọng cao, rate limit cao).
- `ai_gateway/tests/test_budget.py`: Thêm unit test kiểm tra khả năng load BudgetPolicy từ biến môi trường đúng đắn.
- `TECH_DEBT.md`: Cập nhật nợ kĩ thuật.

## Runtime Validation Behavior
- `BudgetPolicy` sẽ đọc các giá trị USD và mode trực tiếp từ OS environment variables. 
- Validation đảm bảo rằng nếu biến môi trường bị sai format (không parse ra số), ứng dụng sẽ không crash mà dùng giá trị mặc định là vô hiệu (None).

## Budget Mode Smoke Behavior
Smoke script thiết lập sẵn 2 model: một model giá rẻ (cost = 0.05, capability vừa đủ) và một model đắt (cost = 5.0, capability cao). 
- Khi truyền `AI_GATEWAY_BUDGET_MODE="economy"` hoặc `emergency`, router ưu tiên đẩy trọng số cost lên để lựa chọn model giá rẻ ("cheaper model preferred").

## Usage Summary Warnings
Tool đọc log JSONL và in ra:
- Tổng token (input/output), cost, và độ trễ.
- Tổng hợp cost và số lỗi theo từng model.
- Warning nếu một model chiếm trên 70% tổng số tiền đã chi trả.
- Warning nếu chạm mốc 80% daily budget.
- Warning nếu tỉ lệ lỗi hoặc rate limit cao bất thường.

## Tests run
Toàn bộ Test suite đều chạy ổn định và Pass. Do môi trường giới hạn không sử dụng `pytest` mặc định nên dùng python unittest để đảm bảo logic:
- `test_smoke.py`: Kiểm tra Smoke script hoạt động.
- `test_usage_summary_warnings.py`: Đảm bảo output text của summary chứa warning hợp lệ.
- Các bài test của `test_budget.py` (penalty computation, limit testing, env loading).

## Technical Debt
- **Budget Validation**: Hiện chủ yếu test bằng smoke script và file test, chưa có dashboard trực quan cho quản trị viên.
- **Budget State**: `BudgetManager` đang lưu trạng thái ở dạng In-memory, sẽ sai số khi scale-out multi-instance, cần Redis.
- **Quality Score**: Chưa có thông tin đo lường chất lượng thực (user feedback) tác động vào budget routing.
- **Price Refresh**: Chưa có cơ chế auto-fetch giá API hiện thời, phải hardcode struct.

## External Public API Changed?
Không.

## Internal API Changed?
Không.

## Breaking Change?
Không.

## Sprint Recommendation
Mở rộng chức năng Dashboard Admin UI để hiển thị các insights từ usage summary và real-time budget spending một cách trực quan, đồng thời triển khai Redis để lưu global budget state.
