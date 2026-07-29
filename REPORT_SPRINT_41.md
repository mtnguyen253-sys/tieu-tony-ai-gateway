# Sprint 41 Report - Client-Specific Provider-Backed Boundary Notes

## Goal

Make all client-specific docs in `docs/clients/` clearly state the provider-backed verification boundary so configuration guidance is not mistaken for live provider/client verification evidence.

## Files reviewed

- `AGENTS.md`
- `E:\Tony_tonghop\AI\lao-tony\PHASE_V2A_OPERATING_CONTRACT.md`
- `E:\Tony_tonghop\AI\lao-tony\PHASE_V2A_SKILL_RECIPES.md`
- `E:\Tony_tonghop\AI\lao-tony\PROJECT_SAFE_CHECK_RUNNER.md`
- `README.md`
- `RUN_LOCAL.md`
- `docs/CLIENT_COMPATIBILITY.md`
- `docs/clients/codex.md`
- `docs/clients/hermes.md`
- `docs/clients/openai_compatible_clients.md`
- `docs/clients/openai_sdk.md`
- `docs/clients/openclaw.md`
- `REPORT_SPRINT_39.md`
- `REPORT_SPRINT_40.md`

## Precondition check result

- Target repo path confirmed: `E:\Tony_tonghop\AI\tiểu-tony-ai-gateway`
- Branch: `main`
- Initial `git status --short`: clean
- Initial `git diff --check`: OK

## Client docs inventory

- `docs/clients/codex.md`
- `docs/clients/hermes.md`
- `docs/clients/openai_compatible_clients.md`
- `docs/clients/openai_sdk.md`
- `docs/clients/openclaw.md`

## Boundary consistency findings

- `docs/CLIENT_COMPATIBILITY.md` states that only `/v1/health` and `/v1/models` are provider-free verified.
- Sprint 40 states that chat completions, streaming, tool/function calling, usage-ledger behavior, and external-client behavior remain provider-backed verification scopes.
- The client-specific guides were useful configuration templates, but their verification sections did not consistently say that health/models checks are provider-free while live client behavior requires separate provider-backed verification.
- The OpenAI SDK guide included a runnable chat completion example and smoke script reference without a nearby provider-backed caveat.

## Changes made

- Added provider-backed boundary notes to each `docs/clients/*.md` guide.
- Renamed each client guide verification section to `Provider-free verification`.
- Reworded verification introductions so the listed curl checks verify only that the gateway process is reachable through provider-free health/models endpoints.
- Marked the OpenAI SDK chat example and smoke script as provider-backed verification scopes.
- Added this Sprint 41 report.

## What is verified

- Client-specific docs now say they are configuration guidance, not evidence of live provider-backed client verification.
- Client-specific docs now separate provider-free health/models checks from provider-backed live chat, streaming, tool/function calling, usage-ledger writes, smoke scripts, and end-to-end provider connectivity.
- The docs remain consistent with `README.md`, `RUN_LOCAL.md`, `docs/CLIENT_COMPATIBILITY.md`, and Sprint 40.

## What is not verified

- Live provider connectivity.
- Live client chat completions.
- Streaming.
- Tool/function calling.
- Usage-ledger writes from live traffic.
- External client end-to-end behavior for Codex, Hermes, OpenClaw, OpenAI SDK, or generic OpenAI-compatible clients.
- Tiểu Tony live integration.

## Non-goals

- No runtime code changes.
- No test changes.
- No provider/API/network/LLM calls.
- No `.env`, `.env.*`, secret, key, credential, token, or private config value reads.
- No Lao Tony source changes.
- No bridge, write-mode, or agent launcher.
- No memory, JSONL, or persistence writes.
- No commit or push.

## Risks / blockers

- Git displayed line-ending normalization warnings for edited Markdown files during diff review. `git diff --check` is the final whitespace validation source for this docs-only sprint.
- Older mojibake-prone Vietnamese text remains outside the edited client guides and is not addressed in this sprint.

## Recommended next manual actions

1. Review the Sprint 41 docs/report diff.
2. Decide whether to commit with `Clarify client provider-backed boundaries`.
3. Schedule a separate live client verification sprint only if provider-backed behavior needs to be claimed.

## Decision

CLOSED

Client-specific docs consistently state the provider-backed boundary, no provider/network/secrets were used, no code/tests changed, and final checks passed.

## Safety confirmation

- No provider/API/network/LLM calls were run.
- No `.env`, `.env.*`, secrets, keys, credentials, tokens, or private config values were read.
- No Tiểu Tony live integration was run.
- No runtime code changes were made.
- No tests were changed.
- No Lao Tony source files were changed.
- No memory/JSONL/persistence writes were made.
- No bridge/write-mode/agent launcher was created.
- No commit or push was performed.

## Files Changed

- `docs/clients/codex.md`
- `docs/clients/hermes.md`
- `docs/clients/openai_compatible_clients.md`
- `docs/clients/openai_sdk.md`
- `docs/clients/openclaw.md`
- `REPORT_SPRINT_41.md`

## Design Decisions

- Keep each note short and client-specific enough to remain readable.
- Preserve existing configuration examples while marking provider-backed behavior near the relevant examples.
- Keep provider-free verification limited to documented health/models endpoints.

## Assumptions

- Sprint 37, Sprint 38, Sprint 39, and Sprint 40 remain the current local evidence baseline.
- Docs-only edits do not require pytest under the Sprint 41 testing policy.

## Architecture Review

No runtime behavior, architecture, route surface, or API contract changed. The sprint only clarifies documentation boundaries for client-specific setup guides.

## Technical Debt

- Older multilingual/mojibake-prone documentation remains a separate docs-language cleanup item.
- Live provider-backed client compatibility still needs a separately approved verification sprint before any specific client can be claimed as end-to-end verified.

## External Public API Changed?

No.

## Internal API Changed?

No.

## Breaking Change?

No.

## Sprint Recommendation

Review and commit the docs/report changes if acceptable.
