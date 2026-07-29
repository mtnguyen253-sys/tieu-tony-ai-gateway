# Tieu Tony AI Gateway

Tieu Tony is a lightweight OpenAI-compatible gateway for routing requests across AI providers.

## Provider-Free Local Runtime

The documented local runtime entrypoint is:

```powershell
python -m uvicorn ai_gateway.api.runtime:app --host 127.0.0.1 --port 8000
```

The provider-free runtime surface verified by recent reports is:

```powershell
curl http://127.0.0.1:8000/v1/health
curl http://127.0.0.1:8000/v1/models
```

These checks do not require provider API keys, network calls, live provider verification, or Lao Tony integration. `/v1/models` may return an empty `data` list when no provider is configured or enabled.

## Provider-Backed Runtime

Chat completions, streaming, external client smoke scripts, usage ledgers, provider statistics, and provider-backed model enumeration require separately configured providers and should be treated as a separate verification scope.

Do not treat provider-free health/models verification as proof that live provider chat, streaming, external clients, or provider connectivity have passed.

## Local Docs

- `RUN_LOCAL.md` - local runtime and verification commands
- `docs/CLIENT_COMPATIBILITY.md` - OpenAI-compatible client configuration boundaries
- `docs/clients/` - client-specific configuration templates
- `REPORT_SPRINT_37.md` - explicit runtime `/v1/health` verification
- `REPORT_SPRINT_38.md` - provider-free `/v1/models` verification
