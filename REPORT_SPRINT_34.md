# Sprint 34 Report - Adaptive Routing Configuration Correctness

## Files Changed
- `ai_gateway/api/app.py`
- `ai_gateway/core/provider_statistics.py`
- `ai_gateway/core/router.py`
- `ai_gateway/core/usage.py`
- `ai_gateway/tests/test_adaptive_configuration.py`

## Design Decisions
- `create_app()` creates one `StatisticsUpdater` with the injected `app_settings.adaptive_window_size` and injects it into both the runtime router and default usage ledger.
- `PolicyRouter` accepts optional injected adaptive settings and retains its global-settings fallback for existing direct callers.
- Usage ledgers accept an optional statistics updater while preserving their prior global-updater default.

## Assumptions
- A configured adaptive window size is valid because `Settings` continues to own configuration parsing.
- Existing callers that do not inject dependencies should retain Sprint 33 behavior.

## Architecture Review
The change uses dependency injection across app, ledger, and router boundaries. It avoids endpoint changes and does not alter adaptive scoring rules, persistence, or decay behavior.

## Technical Debt
- Adaptive statistics remain in-memory and count-window based; persistence and time-based decay remain out of scope.
- The test suite reports one existing `StarletteDeprecationWarning` for `TestClient`'s `httpx` usage.

## External Public API Changed?
No.

## Internal API Changed?
Yes, additively: optional `statistics_updater` parameters on usage ledgers, optional `adaptive_settings` on `PolicyRouter`, and optional `window_size` on the global updater getter.

## Breaking Change?
No.

## Validation
- Focused adaptive tests: 10 passed.
- Full suite: 159 passed, 1 existing deprecation warning.
- `git diff --check`: passed.

## Sprint Recommendation
Sprint 34 is complete. Do not broaden this work into persistence or time-decay redesign without a separate scoped sprint.
