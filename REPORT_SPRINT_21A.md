# Báo cáo Sprint 21A - Budget Policy + Cost-aware Routing

## Files Changed
- `ai_gateway/core/budget.py` (New): Defined `BudgetPolicy` and `BudgetManager` to track spend, error rates, and rate limit occurrences. It implements budget limits (daily, per-request) and calculates scoring penalties based on provider reliability.
- `ai_gateway/registry/capability.py`: Modified `ScoringEngine.weight` and `ScoringEngine.score` to accept `mode`, `prefer_cheaper`, and `penalty`. It adjusts weights (prioritizing cost in economy mode, and heavily prioritizing cost in emergency mode) and subtracts computed penalties from final scores.
- `ai_gateway/core/router.py`: Injected `BudgetManager` into `PolicyRouter`. Modified `route()` method to extract budget context and calculate penalties before scoring, rejecting candidates if they exceed max limits in restricted modes.
- `ai_gateway/core/executor.py`: Injected `BudgetManager` into `ExecutionEngine`. Modified `_record_usage()` to invoke `record_spend()`, `record_success()`, `record_error()`, and `record_rate_limit()` on the `BudgetManager`, closing the feedback loop.
- `ai_gateway/tests/test_budget.py` (New): Unit tests verifying budget limit rejections and penalty logic calculations based on error/rate limit rates.

## Design Decisions
- **Decoupled Budget Management**: `BudgetManager` sits as a separate component tracking live stats in-memory, rather than tightly coupling this logic inside `ScoringEngine`. 
- **Graceful Degradation**: If `BudgetManager` is omitted, the router defaults to normal behavior with zero penalties and default weights, preserving full backward compatibility.
- **Penalty Formula**: We track recent total requests. If there is enough data (e.g. `total >= 3`), error rate directly reduces the score. A 10% error rate roughly correlates to a 1.0 drop in score (max drop 5.0), rapidly pushing unstable providers down the queue. Rate limit rates also reduce score but slightly less aggressively.
- **Modes (Normal, Economy, Emergency)**:
  - `normal`: Follows standard RoutingPolicy weights, checks budget and warns if exceeded.
  - `economy`: Modifies weights to heavily favor cheap models and strictly enforces budget limits (drops candidates that push estimated spend over budget).
  - `emergency`: Chế độ cạn kiệt ngân sách (cost-saving emergency). Ưu tiên tối đa các model giá rẻ/free, tăng mạnh trọng số cost và giảm trọng số quality/latency. Vẫn kiểm soát chặt chẽ ngân sách (không bỏ qua budget limit) để tránh chọn model đắt tiền chỉ vì quality cao.

## Assumptions
- Currently, `BudgetManager` stores data in memory. Restarting the process resets daily spend and error rate metrics. A future sprint would tie this to a persistent ledger or Redis.
- `capability.cost` is treated as a static proxy to represent the general expense of a model to allow the router to pre-filter before execution. Exact costs are still only recorded post-execution by `CostEstimator`.

## Architecture Review
- The routing loop now correctly assimilates four pillars: Capabilities, Quotas, Policies, and (now) Budgets/Reliability metrics.
- The feedback loop is complete: `ExecutionEngine` captures errors/costs -> feeds to `BudgetManager` -> `PolicyRouter` scores candidates using penalities -> `ScoringEngine` computes final score.

## Technical Debt
- **Persistent Storage**: Like the `UsageLedger`, `BudgetManager` data is ephemeral. In a multi-worker environment, budget tracking will be inconsistent without a centralized backend (e.g., Redis).
- **Exact Pre-computation**: The router checks budget against a static `capability.cost` rather than calculating exact predicted tokens for the prompt, which is hard to do synchronously before model choice.

## External Public API Changed?
No.

## Internal API Changed?
- `PolicyRouter.__init__` now accepts `budget_manager: Optional[BudgetManager] = None`.
- `ExecutionEngine.__init__` now accepts `budget_manager: Optional[BudgetManager] = None`.
- `ScoringEngine.weight` and `score` accept extra arguments `mode`, `prefer_cheaper`, and `penalty`.

## Breaking Change?
No. Optional arguments ensure existing initializations continue to function.

## Sprint Recommendation
- Begin next sprint to implement a persistent tracking backend for the budget manager (e.g. Redis), or move towards advanced budget tiers per API key/tenant.
