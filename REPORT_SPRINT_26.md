# Sprint 26 Report: Usage Economics Report

## Files Changed
- `ai_gateway/core/usage.py`: Extended `UsageEvent` model to include `input_cost`, `cached_input_cost`, and `output_cost` for fine-grained token economics.
- `ai_gateway/core/cost.py`: Upgraded `CostEstimator` to provide `estimate_detailed` returning a dictionary with a full breakdown of input, cached, output, and total costs.
- `ai_gateway/core/executor.py`: Updated `ExecutionEngine` to utilize `estimate_detailed` and record the cost breakdown into the `UsageEvent` ledger.
- `ai_gateway/tools/usage_summary.py`: Completely rewritten to generate a comprehensive Token Economics report. Supports caching insights, detailed cost breakdowns, top expensive models, output-heavy requests tracking, and smart warnings (rate-limit, cost concentration, context cache). Added JSON output flag `--json`.
- `ai_gateway/tests/test_usage_summary_warnings.py`: Updated to test the new summary features, cost breakdowns, token counts, and the JSON output generation.
- `RUN_LOCAL.md`: Added documentation for running the new Token Economics report and interpreting insights (like cache ratio).
- `TECH_DEBT.md`: Logged new technical debt items identified in Sprint 26 (no web dashboard, lack of persistent DB, no automated cache-aware routing).

## Design Decisions
- **Cost Breakdown Addition:** Instead of recalculating cost inside the summary tool (which lacks runtime pricing knowledge), we modified the core `CostEstimator` and `UsageEvent` to record the cost breakdown *at execution time*.
- **Summary Independence:** The `usage_summary.py` script remains a standalone tool parsing `.jsonl`. It handles the absence of breakdown fields gracefully for backwards compatibility.
- **Rules-based Insights:** The insights (e.g., "Model accounts for >70% of total cost") are computed on the fly by the summary script based on aggregated log data, keeping the core gateway lightweight.

## Assumptions
- We assume `cost_cached_input_per_million` is provided in provider pricing configs. If missing, it defaults to the standard input price (no discount).
- The summary script parses logs sequentially. Extremely large JSONL files (gigabytes) might be slow to process in-memory, hence the tech debt note for a persistent DB.

## Architecture Review
- The Token Economics reporting correctly adheres to the separation of concerns. `ExecutionEngine` creates raw structured usage records, and `usage_summary.py` handles the data aggregation and recommendation generation.

## Technical Debt
- **Persistent DB:** Relying on `.jsonl` will not scale indefinitely for historical analytics.
- **Cache-Aware Routing:** We are reporting the cache efficiency, but the routing policy isn't leveraging it yet.
- **Dashboard:** No graphical web dashboard exists.
- **Key Pools / Auth:** Multi-key pools and user authentication are still missing.

## External Public API Changed?
No. Endpoints remain strictly OpenAI-compatible.

## Internal API Changed?
Yes. 
- `UsageEvent` now includes `input_cost`, `cached_input_cost`, `output_cost`.
- `CostEstimator` has a new method `estimate_detailed()`.

## Breaking Change?
No. Previous `.jsonl` log lines without the detailed cost fields will gracefully default to 0.0 for those fields and will report "Partial breakdown unavailable".

## Sprint Recommendation
- Move to Sprint 27 to implement a **Persistent DB** for analytics (e.g., PostgreSQL or SQLite) or **Automated Cache-Aware Routing** logic based on these economic insights.
