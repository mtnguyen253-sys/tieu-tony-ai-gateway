# Sprint 28 Report

## Files Changed
- `ai_gateway/config/settings.py`: Added cache metadata fields to `ProviderProfile`.
- `ai_gateway/core/cache_economics.py`: New helper for effective cost estimation.
- `ai_gateway/core/router.py`: Routing logic updated to consider cache metadata.
- `ai_gateway/registry/capability.py`: Updated `ProviderCapability` and `ScoringEngine` with cache-aware scoring.
- `ai_gateway/tests/test_cache_economics.py`: Added tests for effective cost calculation.
- `ai_gateway/tests/test_cache_routing.py`: Added tests for cache-aware routing.
- `RUN_LOCAL.md`: Updated with cache-aware routing documentation.
- `/.env.example`: Updated with cache metadata examples.
- `/TECH_DEBT.md`: Added technical debt related to prompt caching.

## Cache-aware Routing Behavior
- Providers supporting `prompt_cache` receive a bonus score when `long_context` or `cache_preferred` hints are present in the task requirement.
- Providers not supporting `prompt_cache` receive a penalty when cache-aware hints are present, but are not strictly excluded.

## Effective Cost Formula
The formula estimates cost based on `input_cost` (uncached) and `cache_read_cost` (cached tokens).
`cost = (uncached_tokens * input_cost + cached_tokens * cache_read_cost) / 1,000,000`

## Routing Mode Behavior
- Existing modes (`normal`, `economy`, `emergency`, `quality_first`) are maintained.
- Cache-aware scoring is applied on top of existing scoring.

## Tests Run
- All 136 tests passed in `ai_gateway/tests/`.

## Technical Debt
- Chưa có dynamic learning từ historical cache ratio.
- Chưa có provider-specific prompt cache API.
- Chưa có persistent analytics DB.
- Chưa có tokenizer chính xác.
- Chưa có cache write/read separation đầy đủ cho từng provider.

## Breaking Change?
- No.

## External API Change?
- No.

## Sprint Recommendation
- Sprint 28 requirements met.
