# REPORT_SPRINT_30

## 1. Files Changed
- `ai_gateway/core/task_classifier.py` (New): Implemented task complexity classification using heuristic keyword mapping and prompt length estimation.
- `ai_gateway/core/routing_policy_matrix.py` (New): Implemented mapping between TaskComplexity and ModelTier routing policies.
- `ai_gateway/config/settings.py` (Updated): Added `model_tier`, `max_context_tokens`, and `quality_score` to ProviderProfile schemas. Parses environment configs securely.
- `ai_gateway/registry/capability.py` (Updated): Augmented `ProviderCapability` with tier definitions. Updated `ScoringEngine.score()` to grant heavy bonuses to tier-matching policies and apply penalties to misaligned assignments (e.g. using a STRONG model for a SIMPLE task).
- `ai_gateway/adapters/openai_compatible.py` (Updated): Passed new metadata fields down to generic adapter capabilities.
- `ai_gateway/api/app.py` (Updated): Instantiated GenericOpenAIAdapter with the new metadata fields.
- `ai_gateway/core/orchestrator.py` (Updated): Instantiated the `TaskClassifier` and `RoutingPolicyMatrix`. Added execution logic to classify requests up front and inject `task_policy` into the router context.
- `ai_gateway/core/router.py` (Updated): Modified `PolicyRouter.route()` to extract `task_policy` from context and provide it to the scoring engine.
- `ai_gateway/tools/config_check.py` (Updated): Updated the CLI output to render `model_tier`, `max_context_tokens`, and `quality_score`.
- `ai_gateway/tests/test_classifier.py` (New): Added tests for basic classification scenarios.
- `ai_gateway/tests/test_router_tier.py` (New): Added end-to-end routing validation for tier-aware policy selection.
- `TECH_DEBT.md` (Updated): Added Sprint 30 technical debts related to heuristic limitations and lack of tokenizer.
- `RUN_LOCAL.md` (Updated): Added instructions for configuring `model_tier`.

## 2. Design Decisions
- **Heuristic Classifier Over NLP Model**: Implemented a lightweight, fast, local heuristic-based `TaskClassifier` in Python over using heavy ML dependencies to keep the Gateway's execution latency as close to 0ms as possible.
- **Strict Scoring Penalties**: Designed the tier matching in `ScoringEngine` with severe asymmetric penalties (e.g., -10.0 for using STRONG models on SIMPLE tasks) to enforce cost-effective routing forcefully while allowing fallback if needed.
- **Context Size Estimation**: Used a simple fallback estimation (string length / 4) for token counting to detect long-context tasks efficiently without requiring a heavy `tiktoken` dependency in the core router path.
- **Upstream No-LLM**: Did not implement `NO_LLM` execution logic or "Local Skills" in Tiểu Tony, adhering strictly to the architecture constraint that this gateway assumes LLM resolution is required by the time a task reaches it.

## 3. Assumptions
- The task classifier assumes English-centric or generic keywords for heuristics (e.g., "translate", "refactor"). It may not classify accurately for highly abstract or non-English prompts, defaulting to `STANDARD`.
- We assume `ProviderCapability.cost` ranges functionally between 0.0 and 10.0 per million tokens for scoring normalization.
- Provider tier configuration is trusted; if a user incorrectly tags an expensive model as `CHEAP`, the system will route simple requests to it.

## 4. Architecture Review
The `ExecutionOrchestrator` now assumes a more proactive role, intercepting the `AgentRequest` before the `PolicyRouter` evaluates candidate models. By decoupling the `TaskClassifier` and `RoutingPolicyMatrix` from the router's internal loop, we preserve the purity of `PolicyRouter` as a generic capability matcher, making it highly modular. This adheres well to our Strategy pattern.

## 5. Technical Debt
- Classification is simplistic. In the future, a fast embedding classifier or lightweight ML approach could replace the naive keyword matching.
- Token counting is approximate. We should evaluate integrating `tiktoken` or a similar tokenizer for more robust context bounds checking.

## 6. External Public API Changed?
- No. The OpenAI-compatible endpoints (`/v1/chat/completions`, `/v1/models`) are completely unchanged in structure.

## 7. Internal API Changed?
- Yes. `ScoringEngine.score()` now accepts an optional `task_policy` kwarg.
- `GenericOpenAICompatibleAdapter.__init__` gained new metadata kwargs.

## 8. Breaking Change?
- No. All existing tests pass (using mock capability registries). Legacy configurations missing `model_tier` default safely to `balanced`, preserving identical scoring behavior for standard tasks.

## 9. Sprint Recommendation
- PASS. Ready to proceed to Sprint 31.
