with open("REPORT_SPRINT_17.md", "r") as f:
    content = f.read()

old = """# Sprint 17.1 Bugfix Report: Fix Public Gateway CAP Contract Mapping & Abstract Strategy Instantiation

## 1. Files Changed
- `ai_gateway/api/app.py`
- `ai_gateway/tests/test_api.py`

## 2. Design Decisions
- **Fix Fallback Exception Mapping"""

new = """# Sprint 17.2 Bugfix Report: Fix Public Gateway CAP Contract Mapping & Abstract Strategy Instantiation

## 1. Files Changed
- `ai_gateway/api/app.py`
- `ai_gateway/tests/test_api.py`
- `ai_gateway/core/fallback.py`
- `ai_gateway/tests/test_fallback.py`

## 2. Design Decisions
- **Fix MockRouter Assertions**: Chỉnh sửa hành vi của `MockRouter` trong file `test_fallback.py` để biến `call_count` tăng ngay lập tức ở đầu hàm (ngay cả khi gọi router nhưng bị throw `NoProviderAvailableException`). Điều này đảm bảo test `test_6_both_providers_fail` kiểm chứng chính xác 3 lần routing attempts trước khi fallback bị cạn kiệt.
- **Fix Fallback Exception Mapping"""

if old in content:
    content = content.replace(old, new)
    with open("REPORT_SPRINT_17.md", "w") as f:
        f.write(content)
    print("Patched successfully")
else:
    print("Pattern not found")
