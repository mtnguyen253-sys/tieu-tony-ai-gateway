# Sprint 33 Report – Adaptive Routing

## Overview
Sprint 33 introduces an adaptive, history-aware, non-AI statistical routing system. The routing mechanism learns directly from the real-time operational performance of each provider in-memory without relying on external databases or complex machine learning models.

---

## Files Changed
- `ai_gateway/core/provider_statistics.py`: Created to define `ProviderStats` data structure, sliding-window management, score calculators, and global updater instance.
- `ai_gateway/core/usage.py`: Integrated `get_global_statistics_updater` to trigger rolling statistic updates automatically upon recording any `UsageEvent`.
- `ai_gateway/core/router.py`: Integrated adaptive routing bonuses and penalties into `PolicyRouter.route()`.
- `ai_gateway/config/settings.py`: Added configuration variables and default scoring modifiers.
- `ai_gateway/tools/provider_statistics.py`: Created the CLI report tool that aggregates `usage.jsonl` data and outputs detailed stats and recommendations.
- `.env.example`: Documented new environment variables.
- `RUN_LOCAL.md`: Added section for Adaptive Routing configuration and CLI reporting.
- `TECH_DEBT.md`: Documented key technical debt items.
- `ai_gateway/tests/test_provider_statistics.py`: Created unit tests for the StatisticsUpdater.
- `ai_gateway/tests/test_adaptive_router.py`: Created unit tests for PolicyRouter integration.
- `ai_gateway/tests/test_statistics_decay.py`: Created unit tests for the sliding-window decay mechanism.
- `ai_gateway/tests/test_statistics_tool.py`: Created unit tests for the CLI reporting tool.

---

## Design Decisions
1. **No AI/ML Statistical Engine**: Implemented routing adaptations using deterministic statistics computed on a sliding-window of historical usage events (`window_size=50`).
2. **In-Memory Tracking**: Recorded events sequentially and updated averages (latency, cost, prompt/completion tokens) and ratios (success rate, timeout rate, rate limit rate, cache hit ratio) in-memory, completely bypassing database read/write bottlenecks.
3. **Decoupled Usage Observer Pattern**: Hooked the `StatisticsUpdater` directly into the existing `UsageLedger.record` implementation. This automatically tracks both synchronous and streaming requests without touching endpoint definitions.
4. **Additive Score Adjustments**: Kept the existing multi-criteria routing logic intact, introducing historical performance as custom bonuses and penalties that are added directly to the calculated score.
5. **Human-readable CLI Report**: Built a neat table report with standard formatting that computes historical stats directly from standard JSONL files, allowing operators to run reports anytime without impacting performance.

---

## Assumptions
- Latency threshold under `1500ms` is considered highly optimal and earns a bonus.
- Average cost under `0.5 USD` per request is considered cheap and earns a bonus.
- Cache hit ratio above `30%` is considered high and earns a bonus.
- Any failure rate above `15%` or timeout rate above `15%` triggers an `Avoid temporarily` recommendation.

---

## Architecture Review
The introduction of `ProviderStats` integrates seamlessly with the existing `CapabilityRegistry`, `PolicyRouter`, and `UsageLedger`. The system adheres fully to the Single Responsibility Principle, keeping statistics, routing, configuration, and reporting strictly modular.

---

## Technical Debt
- **In-Memory Statistics Loss**: Statistics are not currently persisted between gateway restarts.
- **Queue Storage Overhead**: Storing full `UsageEvent` objects in history can have small memory overheads.
- **Clock Time Decay**: Statistics do not naturally decay over inactive clock time, but are rather count-based.

---

## External Public API Changed?
- **No**. The FastAPI application and all OpenAI-compatible completions endpoints remain fully compatible.

## Internal API Changed?
- **Yes (Additive)**: `PolicyRouter.__init__` now supports an optional `statistics_updater` argument.

## Breaking Change?
- **No**. All 171 existing and new test cases pass successfully.

---

## Sprint Recommendation
It is recommended to deploy the Adaptive Routing system with `AI_GATEWAY_ADAPTIVE_ROUTING_ENABLED=true` in production to automatically handle transient provider failures, latency spikes, and optimize usage across providers.
