# Sprint 36 Report - Configuration Loading Boundary Hardening

## Files Changed
- `ai_gateway/config/settings.py`
- `ai_gateway/api/runtime.py`
- `scripts/run_local.ps1`
- `RUN_LOCAL.md`
- `ai_gateway/tests/test_settings.py`
- `ai_gateway/tests/test_settings_profiles.py`
- `ai_gateway/tests/test_config_loading_boundary.py`

## Design Decisions
- Settings construction is import-safe by default and does not load `.env`.
- `load_settings_from_dotenv()` is the explicit factory for runtime configuration loading.
- `ai_gateway.api.runtime:app` is the documented local runtime entrypoint; it is the only added module that opts into dotenv loading.

## Assumptions
- Production/local runs that rely on `.env` use the documented runtime entrypoint or call the explicit settings factory.
- Environment variables supplied by the process remain supported without dotenv loading.

## Architecture Review
Configuration file loading is now isolated from application-library import. `create_app(app_settings=...)` remains the dependency-injection path for tests and embedding callers.

## Technical Debt
- The default `app` object remains for compatibility and uses only process environment values; operators must use the documented runtime module when `.env` loading is required.

## External Public API Changed?
No. Existing routes and response behavior are unchanged.

## Internal API Changed?
Yes, additively: `load_settings_from_dotenv()` and `ai_gateway.api.runtime:app` were added. The default `Settings()` behavior no longer loads `.env` implicitly.

## Breaking Change?
No endpoint breaking change. Runtime invocations that require `.env` must use the documented entrypoint.

## Sprint Recommendation
Run the focused configuration-boundary tests and full pytest suite. Do not expand into provider/runtime smoke validation in this sprint.
