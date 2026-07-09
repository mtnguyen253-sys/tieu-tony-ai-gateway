# Sprint 15 Report: Execution Refactor (SRP Restoration)

## 1. Files Changed
- `ai_gateway/core/executor.py`
- `ai_gateway/core/orchestrator.py`
- `ai_gateway/core/fallback.py`
- `ai_gateway/tests/test_executor.py`
- `ai_gateway/tests/test_orchestrator.py`
- `ai_gateway/tests/test_fallback.py`
- `src/data.ts` (sync)

## 2. Design Decisions
- **SRP Restoration**: Removed `PolicyRouter` dependency entirely from `ExecutionEngine`. `ExecutionEngine` now receives an already routed `provider` instance and focuses purely on execution, catching exceptions, measuring time, logging, and updating the `CircuitBreaker`.
- **Validation Check**: If `provider` is `None`, `ExecutionEngine` immediately raises `ValidationException`.
- **Orchestrator Routing**: `ExecutionOrchestrator` is now the sole component invoking `PolicyRouter.route` for the initial attempt (via manual routing if no fallback strategy is used, or passing control to the fallback strategy).
- **Fallback Routing Control**: `ProviderFallbackStrategy` no longer holds a reference to `ExecutionEngine`. It handles iterative routing loops natively calling `PolicyRouter.route`, passing the newly chosen provider to the injected `operation` block.

## 3. Assumptions
- Tests are mock-based and do not require external HTTP connections.
- The `ProviderFallbackStrategy` retains the state of `excluded_providers` and iteratively queries `PolicyRouter` until a provider succeeds or all providers are exhausted.
- Unit test assertions verify exact behavior, but I removed irrelevant test stubs in `test_executor` that previously mocked `PolicyRouter` natively inside the engine.

## 4. Architecture Review
**PASS**. The architecture is now cleaner and adheres tightly to SRP. The `ExecutionEngine` is decoupled from routing. Dependencies now follow a cleaner one-way tree:
`ExecutionOrchestrator` -> `PolicyRouter` & `ExecutionEngine`
`ProviderFallbackStrategy` -> `PolicyRouter`
`ExecutionEngine` (No longer depends on `PolicyRouter`)

## 5. Technical Debt
- **TD-006 (ExecutionEngine mixed responsibilities)** is formally **RESOLVED** and closed via this Sprint.
- The project retains other outstanding Technical Debt (e.g., HALF_OPEN recovery, Dynamic Normalization, Synchronous pipeline), which are planned for future sprints.

## 6. Sprint Recommendation
- Since core request lifecycle modules are now isolated functionally (Routing vs Executing vs Retrying vs Fallback), the architecture is robust enough for advanced strategies. 
- Recommend moving to **HALF_OPEN Recovery** (TD-001) in Sprint 16 to solidify the `CircuitBreaker` resilience.
