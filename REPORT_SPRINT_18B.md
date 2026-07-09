# Sprint 18B Report: Smoke Script & RUN_LOCAL Documentation

## 1. Files Changed
- `examples/smoke_chat_completion.py` (Created)
- `RUN_LOCAL.md` (Created)
- `ai_gateway/api/dev.py` (Created)

## 2. Design Decisions
- **Smoke Script**: Tạo file `examples/smoke_chat_completion.py` sử dụng `httpx` để thực hiện HTTP request POST đến endpoint `/chat/completions`. Script tự động bắt exception nếu không kết nối được và in ra thông báo thân thiện (tránh in stack trace dài gây rối).
- **Dev/Mock Runtime**: Khởi tạo file `ai_gateway/api/dev.py` chứa endpoint dev/mock độc lập. Ứng dụng trong file này được cấu hình để inject một `MockOrchestrator` nhằm trả về 200 OK với simulated response, không làm ảnh hưởng (mix) vào production/default runtime. Default runtime vẫn trả về 503 khi chưa có provider.
- **RUN_LOCAL.md**: Đã viết tài liệu hướng dẫn nhanh các bước để lập trình viên tự setup local (venv, dependencies, chạy server ở cả mode default và dev/mock, cùng với cách gọi smoke script).

## 3. Assumptions
- Giả định thư viện `httpx` sẽ được cài chung khi lập trình viên thực hiện cài các dependencies. Không sử dụng thư viện `openai` SDK trong nhịp này.

## 4. Architecture Review
Cách thiết kế tách rời Application Factory (`create_app`) trong Sprint 17.2/18A đã cho thấy hiệu quả: file `ai_gateway/api/dev.py` rất ngắn gọn và dễ hiểu, thể hiện sức mạnh của dependency injection trong việc khởi tạo môi trường test/mock HTTP.

## 5. Technical Debt
- **TD-003**: Migration sang async flow vẫn đang chờ.
- **TD-008**: Chưa có Streaming.
- **TD-009**: Chưa có Authentication.

## 6. External Public API Changed?
Không.

## 7. Internal API Changed?
Không.

## 8. Breaking Change?
Không có Breaking Change. 

## 9. Sprint Recommendation
Hệ thống Gateway hiện tại đã có bộ khung vững vàng với đầy đủ Testing, Fallback, Mocking, và Documentation để onboarding nhanh. Trong các Sprint tiếp theo có thể tiến tới xử lý Authentication (API Keys) hoặc Streaming để hoàn thiện chuẩn API.
