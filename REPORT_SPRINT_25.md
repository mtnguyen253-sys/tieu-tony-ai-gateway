# Sprint 25 Report: Generic OpenAI-compatible Provider Profiles

## Files Changed
- `ai_gateway/adapters/openai_compatible.py`: Added `GenericOpenAICompatibleAdapter`.
- `ai_gateway/config/settings.py`: Added `ProviderProfile` class and updated `Settings` to parse multiple provider profiles from environment variables (`AI_GATEWAY_PROVIDER_*`).
- `ai_gateway/api/app.py`: Updated `create_app` to instantiate and register `GenericOpenAICompatibleAdapter` instances based on settings. Updated `MODEL_PRICES` runtime registration.
- `RUN_LOCAL.md`: Added documentation for configuring multiple generic providers via environment variables.
- `examples/smoke_generic_provider.py`: Added a smoke test script to test generic providers configuration.
- `ai_gateway/tests/test_openai_compatible.py`: Added unit tests for the generic adapter.
- `ai_gateway/tests/test_settings_profiles.py`: Added unit tests for profile config parsing.
- `ai_gateway/tests/test_router_generic.py`: Added budget-aware routing tests for generic providers.
- `TECH_DEBT.md`: Logged new technical debt from Sprint 25.

## Generic Provider Behavior
- Implemented `GenericOpenAICompatibleAdapter` which acts as a passthrough to any OpenAI-compatible upstream endpoint.
- Handles standard JSON requests for chat completions.
- Automatically normalizes models, extracts usage from the upstream response, and performs standard error mapping (401, 403, 429, 5xx) to internal gateway exceptions for fallback triggering.
- Extracts `Retry-After` if available.

## Config Behavior
- Configuration supports dynamic loading of any number of provider profiles by looking for environment variables starting with `AI_GATEWAY_PROVIDER_{ID}_...`
- Required variables: `NAME`, `BASE_URL`, `MODEL`. Optional: `API_KEY`, `ENABLED`, `SUPPORTS_STREAMING`, `COST_INPUT_PER_MILLION`, `COST_OUTPUT_PER_MILLION`.
- Gracefully skips incomplete configurations without crashing the app.
- Backwards compatible with legacy `OPENROUTER_API_KEY` configuration.

## Routing Behavior
- Budget-aware routing dynamically uses the cost parameters configured in the provider profile.
- Tested under "normal", "economy", and "emergency" modes. Economy and emergency modes successfully prioritize cheaper generic providers.
- If a provider is disabled via configuration, its health check returns "error" and it is successfully excluded from routing.
- Cooldown exclusion respects generic providers properly.

## Streaming Behavior
- Added support for SSE event streaming to upstream OpenAI-compatible servers.
- If a provider is explicitly configured with `SUPPORTS_STREAMING=false` and a request sets `stream=true`, the adapter throws `ProviderUnavailableException` preventing a 500 error and allowing potential fallback to a streaming-capable provider.

## Tests Run
- Successfully passed all 123 tests including non-stream, stream unsupported checks, rate limit extraction, disabled behaviors, config parsing, and budget routing matrix.
- `python -m pytest ai_gateway/tests -v` returned `123 passed`.

## Technical Debt
- Multi-key pool missing for generic provider profiles.
- Quota is tracked per provider, not per API key.
- Provider dashboard is lacking for inspecting dynamically configured providers.
- No auto-model discovery for upstream generic providers (e.g., calling their `/v1/models`).
- Cache-aware routing logic not yet implemented for probabilistic routing.
- Quality score remains a default value (8.0) and isn't populated dynamically based on the model.

## External Public API Changed?
No. The `/v1/chat/completions`, `/v1/health`, and `/v1/models` endpoints remain OpenAI-compatible. The `/v1/models` endpoint now dynamically exposes models registered via generic provider configs.

## Internal API Changed?
Yes. Added `cost_input_per_million` and `cost_output_per_million` properties logic to initialize runtime `MODEL_PRICES`. 

## Breaking Change?
No. Legacy OpenRouter configuration via `OPENROUTER_API_KEY` still works as expected.

## Sprint Recommendation
- Move to Sprint 26 to implement Auto Model Discovery (fetching `/v1/models` from upstream generic providers instead of hardcoding `MODEL`).
- Consider implementing Multi-key Pools to rotate through multiple `API_KEY`s for the same generic provider `BASE_URL`.
