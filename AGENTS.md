# Project Governance (AGENTS.md)

## Mission
Cung cấp một lớp trung gian (Gateway) thông minh, ổn định và linh hoạt để điều phối các yêu cầu tới đa dạng các nhà cung cấp AI.

## Working Rules
- Chỉ làm đúng phạm vi Sprint.
- Không tự refactor.
- Không thay đổi Public API nếu chưa được yêu cầu.
- Không thêm dependency ngoài yêu cầu.
- Không hardcode.
- Ưu tiên Composition hơn Inheritance.
- Ưu tiên Strategy / Adapter Pattern.
- Nếu phát hiện vấn đề kiến trúc thì ghi Technical Debt thay vì tự sửa.

## Sprint Rules
- Chỉ giải quyết một vấn đề.
- Không mở rộng ngoài phạm vi.
- Không thêm feature ngoài yêu cầu.

## Testing & Validation Rules
- Không được tuyên bố "PASS 100%" nếu chưa thực sự chạy được bộ test. Nếu môi trường không có pytest, phải ghi rõ đây là giới hạn của môi trường thay vì kết luận test đã thành công.

## Output Rules
Sau mỗi Sprint phải sinh báo cáo có các mục sau:
- Files Changed
- Design Decisions
- Assumptions
- Architecture Review
- Technical Debt
- External Public API Changed?
- Internal API Changed?
- Breaking Change?
- Sprint Recommendation

## Definition of Done
Sprint chỉ PASS khi:
- pytest PASS (nếu môi trường hỗ trợ)
- Không phá Public API
- Có Report

## Architecture First

Nếu phát hiện vấn đề trong quá trình triển khai:

1. Đánh giá xem đó là Bug, Technical Debt hay Feature Request.
2. Không tự refactor để "tiện tay sửa luôn".
3. Nếu không thuộc phạm vi Sprint:
   - Ghi vào TECH_DEBT.md hoặc báo cáo cuối Sprint.
   - Tiếp tục hoàn thành Sprint hiện tại.

Ưu tiên hoàn thành đúng phạm vi hơn là theo đuổi kiến trúc hoàn hảo.
