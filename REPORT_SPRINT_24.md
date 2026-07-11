# Báo Cáo Sprint 24: Packaging / Deployment / Config Profiles

## Files Changed
- `requirements.txt`: Khai báo các dependency cơ bản cho runtime.
- `requirements-dev.txt`: Thêm `pytest` và `openai` hỗ trợ dev và testing.
- `.env.example`: File mẫu chứa các biến cấu hình chuẩn cho app và provider.
- `ai_gateway/config/settings.py`: Khởi tạo lớp `Settings` load biến môi trường thông qua `python-dotenv`.
- `ai_gateway/api/app.py`: Tích hợp config loader, cập nhật endpoint `/health` và `/v1/health` để phản ánh trạng thái an toàn (`provider_configured`, `budget_mode`).
- `scripts/run_local.ps1`: Script PowerShell hỗ trợ khởi động uvicorn tự động load venv và copy `.env` nếu thiếu.
- `scripts/check_env.ps1`: Script PowerShell kiểm tra nhanh python, venv, requirement imports và cấu hình `OPENROUTER_API_KEY`.
- `RUN_LOCAL.md`: Viết lại toàn bộ hướng dẫn theo chuẩn flow cài đặt và sử dụng script mới.
- `pyproject.toml`: Khai báo metadata cơ bản cho project, cho phép dev cài project dưới dạng package.
- `TECH_DEBT.md`: Cập nhật thiếu sót về Docker, Redis, Auth, Logging.

## Packaging Behavior
- App giờ đây có đầy đủ metadata từ `pyproject.toml` và các file `requirements.txt`, làm việc clone và cài đặt trên máy local chuẩn và dễ dàng hơn.

## Config/profile Behavior
- Cấu hình được gom lại tại `settings.py` bằng `os.getenv` cùng dotenv fallback, không gây crash nếu không dùng `.env`.
- `OPENROUTER_API_KEY` được tách bạch, cho phép user kiểm tra trạng thái thông qua check script và endpoint health (mà không lộ secret).

## Scripts Added
- `scripts/run_local.ps1`: Chạy project an toàn.
- `scripts/check_env.ps1`: Tự chẩn đoán lỗi môi trường (environment diagnosis).

## RUN_LOCAL Changes
- Workflow rút gọn thành 10 bước rõ ràng, cung cấp command snippet cho PowerShell và curl.

## Tests Run
- Bổ sung `ai_gateway/tests/test_settings.py` để verify default config behaviour.
- Đã chạy 111 tests. Tỷ lệ PASS 100%. Không bị hồi quy.

## Technical Debt
Xem chi tiết trong `TECH_DEBT.md`:
- Chưa có Dockerfile.
- Chưa có systemd/service.
- Chưa validate Auth API Key nội bộ.
- Chưa có structured logging cho production.
- Trạng thái in-memory giới hạn scaling đa tiến trình (Redis needed).

## API Changes
- **External Public API Changed?**: `/health` và `/v1/health` trả về thêm 2 field `provider_configured` và `budget_mode` (an toàn).
- **Internal API Changed?**: Không (chỉ thêm module config).
- **Breaking Change?**: Không.

## Sprint Recommendation
- PASS.
- Sẵn sàng chuyển giao Sprint 25 để tập trung Authentication, Dockerization hoặc Persistence/Redis.
