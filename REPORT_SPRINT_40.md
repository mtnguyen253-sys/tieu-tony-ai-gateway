# Sprint 40 Report - OpenAI-Compatible Endpoint Contract Review

## Goal

Review the documented OpenAI-compatible endpoint contract for Tieu Tony and identify the next safe provider-free improvement.

## Files reviewed

- `AGENTS.md`
- `README.md`
- `RUN_LOCAL.md`
- `docs/CLIENT_COMPATIBILITY.md`
- `docs/clients/codex.md`
- `docs/clients/hermes.md`
- `docs/clients/openai_compatible_clients.md`
- `docs/clients/openai_sdk.md`
- `docs/clients/openclaw.md`
- `REPORT_SPRINT_37.md`
- `REPORT_SPRINT_38.md`
- `REPORT_SPRINT_39.md`
- `ROADMAP.md`
- `TECH_DEBT.md`
- `pyproject.toml`
- `ai_gateway/api/app.py`
- `ai_gateway/api/runtime.py`
- test file names under `ai_gateway/tests/`

## Precondition check result

- Target repo path confirmed: `E:\Tony_tonghop\AI\tiểu-tony-ai-gateway`
- Branch: `main`
- Initial `git status --short`: clean
- Initial `git diff --check`: OK

## Endpoint contract inventory

Source evidence from `ai_gateway/api/app.py`:

- `GET /health`
- `GET /v1/health`
- `GET /models`
- `GET /v1/models`
- `POST /chat/completions`
- `POST /v1/chat/completions`

Documented owner-facing OpenAI-compatible endpoints:

- `/v1/health`
- `/v1/models`
- `/v1/chat/completions`

## Provider-free verified endpoints

- `GET /v1/health`: verified in Sprint 37 with the explicit runtime entrypoint `ai_gateway.api.runtime:app`.
- `GET /v1/models`: verified in Sprint 38 with the explicit runtime entrypoint. Empty `data` is valid when no provider is configured or enabled.

## Provider-backed endpoints

- `POST /v1/chat/completions`: implemented and documented, but requires provider-backed verification for real responses.
- `POST /v1/chat/completions` with `stream=true`: implemented and documented, but requires provider-backed streaming verification.
- Tool/function calling behavior: documented as OpenAI-compatible guidance, but requires separate provider-backed or targeted contract verification.
- Usage ledger behavior from live client traffic: provider/client traffic scope, not provider-free.
- External client end-to-end flows: client-specific provider-backed scope.

## Compatibility claims reviewed

- `README.md` and the Sprint 39 boundary are consistent: only `/v1/health` and `/v1/models` are provider-free verified.
- `RUN_LOCAL.md` already has Sprint 39 notes that separate smoke, chat, streaming, and SDK usage as provider-backed. It still contains older strong compatibility wording in the external-client section; this is classified as follow-up technical debt rather than rewritten in this sprint because the line is embedded in mojibake-prone Vietnamese text.
- `docs/CLIENT_COMPATIBILITY.md` had over-broad wording for "core OpenAI Chat Completions", streaming, tool/function calling, and usage-ledger verification. It now separates implemented/provider-backed behavior from provider-free verification.
- Client-specific guides are mostly template configuration guides. Codex, Hermes, and OpenClaw already say they are not manually verified for every version. OpenAI SDK and general-client guides still present runnable provider-backed examples and should be refreshed in a later focused docs sprint if the owner wants every client guide to carry the same boundary language.

## Docs consistency findings

- `/v1/health` and `/v1/models` are described consistently across README, RUN_LOCAL, and central client compatibility docs as provider-free verified.
- `/v1/chat/completions` is separated from provider-free verification in README, RUN_LOCAL, and central client compatibility docs.
- Client guides remain useful as setup templates but should not be read as proof of live provider-backed verification.

## Changes made

- Updated `docs/CLIENT_COMPATIBILITY.md` to qualify chat, streaming, tool/function calling, and usage-ledger behavior as provider-backed scopes.
- Added `REPORT_SPRINT_40.md`.

## What is verified

- Explicit runtime entrypoint is documented as `ai_gateway.api.runtime:app`.
- `/v1/health` provider-free verification is documented by Sprint 37.
- `/v1/models` provider-free verification is documented by Sprint 38.
- Source inventory confirms the implemented route surface listed above.

## What is not verified

- Live provider connectivity.
- Chat completion success against a real provider.
- Streaming success against a real provider.
- Tool/function calling against a real provider.
- Specific external client behavior for Codex, Hermes, OpenClaw, OpenAI SDK, or general clients.
- Usage ledger writes from live client traffic.
- Lao Tony/Tieu Tony runtime integration.

## Risks / blockers

- Existing Vietnamese text renders as mojibake in some local command output; this sprint avoided broad text rewrites.
- `RUN_LOCAL.md` still has an older strong compatibility sentence in section 15, but nearby Sprint 39 provider-backed boundaries and this report classify it as not provider-free evidence.
- Client-specific docs still vary in how strongly they state provider-backed boundaries.
- No tests were run because this was a docs/report-only sprint with no code or test changes.

## Recommended next manual actions

1. Review the Sprint 40 docs/report diff.
2. Decide whether to commit with `Add OpenAI-compatible endpoint contract review`.
3. Open a separate client-guide boundary cleanup sprint if owner wants consistent notes in every `docs/clients/*.md` file.

## Decision

CLOSED

Endpoint contract is reviewed, compatibility claims are classified, provider-free boundaries remain clear, no provider/network/secrets were used, and final checks passed.

## Safety confirmation

- No provider/API/network/LLM calls were run.
- No `.env`, `.env.*`, secrets, keys, credentials, tokens, or private config values were read.
- No Tieu Tony live integration was run.
- No Lao Tony source files were changed.
- No memory/JSONL/persistence writes were made.
- No bridge/write-mode/agent launcher was created.
- No commit or push was performed.

## Files Changed

- `docs/CLIENT_COMPATIBILITY.md`
- `REPORT_SPRINT_40.md`

## Design Decisions

- Keep the runtime implementation untouched.
- Treat implemented routes and provider-free verified routes as separate facts.
- Centralize compatibility caveats in `docs/CLIENT_COMPATIBILITY.md` and the sprint report without broad multilingual rewrites.

## Assumptions

- Sprint 37 and Sprint 38 reports remain the source of truth for provider-free endpoint verification.
- Source route decorators are acceptable read-only contract evidence.

## Architecture Review

No runtime behavior or architecture changed. The route surface remains unchanged and the docs now better separate provider-free and provider-backed contract claims.

## Technical Debt

- Add uniform provider-backed boundary notes to every client-specific guide in a later docs-only sprint.
- Reconcile older technical debt entries that still describe streaming as open even though basic streaming route support exists.
- Clean up or rewrite mojibake-prone Vietnamese docs text in a separate docs-language sprint before editing those lines directly.

## External Public API Changed?

No.

## Internal API Changed?

No.

## Breaking Change?

No.

## Sprint Recommendation

Review and commit the docs/report changes if acceptable.
