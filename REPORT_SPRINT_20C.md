# Báo cáo Sprint 20C - Usage Ledger + Cost Estimator + Savings Insight Foundation

## Files Changed
- `ai_gateway/core/usage.py` (New): Defined `UsageEvent`, `UsageLedger`, `InMemoryUsageLedger`, and `JsonlUsageLedger`.
- `ai_gateway/core/cost.py` (New): Defined `CostEstimator` with simple token calculation.
- `ai_gateway/config/model_prices.py` (New): Defined `MODEL_PRICES` configuration dictionary.
- `ai_gateway/core/executor.py`: Injected `usage_ledger` and `cost_estimator` into `ExecutionEngine` to record request statuses, tokens, and estimated cost.
- `ai_gateway/core/orchestrator.py`: Passed `fallback_count` and `policy` parameters down to the `ExecutionEngine`.
- `ai_gateway/adapters/openrouter.py`: Fixed `usage` property mapping in `AgentResponse` to retain full usage details (including `prompt_tokens_details`).
- `ai_gateway/tools/usage_summary.py` (New): Created utility to summarize `usage.jsonl` data.
- `ai_gateway/tests/test_usage.py` (New): Unit tests for usage features.
- `ai_gateway/tests/test_adapters.py`, `ai_gateway/tests/test_executor.py`, `ai_gateway/tests/test_orchestrator.py`: Updated mock engine parameters and added adapter usage extraction test.
- `.gitignore`: Added `logs/*.jsonl`, `usage.jsonl`, `*.usage.jsonl`.

## Design Decisions
- **ExecutionEngine as the Recorder**: Usage and error events are logged inside `ExecutionEngine.execute`. This is closest to the metal, allowing us to capture metrics per *provider attempt* (crucial for finding out which provider rate limits or timeouts often). 
- **JsonlUsageLedger**: For local persistence, JSONL files (one JSON object per line) provide an appending approach without pulling in a heavy DB initially.
- **CostEstimator Formula**: Calculates `non_cached_input = max(0, input_tokens - cached_input_tokens)`. Applies respective pricing. Unknown models default to `$0.0`.
- **Pass Context via kwargs**: `fallback_count` and `route_policy` are passed to the engine dynamically, not cluttering the core `AgentRequest` object, retaining backward compatibility.

## Usage Ledger behavior
- **Record**: After a request finishes (success or Exception), a `UsageEvent` is emitted.
- **Error Types**: Maps exception classes (e.g. `RateLimitException`) to the `error_type` field.
- **Local JSONL Output**: By default stores in `logs/usage.jsonl`.

## Cost Estimator behavior
- Expects a dictionary containing `input_per_million`, `cached_input_per_million`, and `output_per_million`.
- Safe fallbacks: Returns $0.0 for unknown models or requests without tokens.

## Summary/Insight behavior
- `python -m ai_gateway.tools.usage_summary logs/usage.jsonl`
- Summarizes tokens, success/error rates, estimated costs, and costs by provider/model.
- Provides static insights/warnings if error rate > 30%, or if cost is > $10.0.

## Assumptions
- The system only runs on a single node right now (JSONL file concurrent appends could interleave, though generally safe in Python but not scalable).
- Fallback tracking relies on the number of `excluded_providers`.

## Tests run
- `test_usage_event_serialization`, `test_in_memory_ledger`, `test_jsonl_ledger`.
- `test_cost_estimator_basic`, `test_cost_estimator_with_cached`, `test_cost_estimator_unknown_model`, `test_cost_estimator_none_tokens`.
- `test_openrouter_adapter_usage_extraction`.
- Full suite passed: 97 passed, 1 warning (deprecation).

## Technical Debt
- **Price Table Scalability**: `MODEL_PRICES` is a static dictionary and should be dynamically fetched or externalized in the future to keep up with model price changes.
- **Storage Backend**: `JsonlUsageLedger` will struggle under heavy concurrent load or in a multi-instance setup. Will need migration to SQLite, Postgres, or ClickHouse for production metrics.
- **Quality Score**: Optimization metrics currently lack a feedback loop from users to adjust routing policies intelligently.
- **Budget-aware Routing**: While data is available, the router does not currently use this to enforce cost limits actively.

## External Public API Changed?
No changes.

## Internal API Changed?
Added `**kwargs` to `ExecutionEngine.execute()` signature to accept tracking arguments. Passed `fallback_count` and `policy` from orchestrator.

## Breaking Change?
No.

## Sprint Recommendation
- Begin Sprint 21 to utilize this data (Budget-aware Routing), introducing limits and fallback based on total cost consumed. 
- Implement cost/budget caps per API key or tenant.
