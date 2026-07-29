# Integration Guide: General OpenAI-Compatible Clients

This guide describes how to connect any standard, generic OpenAI-compatible clients (such as Lobe Chat, LibreChat, Chatbox, Cursor, VS Code Continue, etc.) to **Tiểu Tony AI Gateway**.

## Provider-backed boundary

This guide is configuration guidance for using generic OpenAI-compatible clients with the local gateway. Provider-free checks are limited to the local health and models endpoints documented below and in `README.md`, `RUN_LOCAL.md`, and `docs/CLIENT_COMPATIBILITY.md`.

Live client chat, streaming, tool/function calling, usage-ledger writes, and end-to-end provider connectivity require separately approved provider configuration and live verification before they should be treated as verified for a specific client.

## 1. Connection Configuration

Most standard OpenAI-compatible applications will ask for the following parameter fields:

- **Base URL / API Base**: `http://127.0.0.1:8000/v1`
- **API Key**: `dummy` (or any arbitrary non-empty string)
- **Model / Custom Model Name**: Any model ID exposed via `/v1/models` (e.g., `qwen/qwen3.6-plus`)

## 2. Configuration Patterns

### Example: Cursor or VS Code Extensions (e.g., Continue / Cline)
If configuring an IDE extension, define the custom model in your configuration JSON (e.g. `config.json` for Continue):

```json
{
  "models": [
    {
      "title": "Tiểu Tony Qwen",
      "provider": "openai",
      "model": "qwen/qwen3.6-plus",
      "apiBase": "http://127.0.0.1:8000/v1",
      "apiKey": "dummy"
    }
  ]
}
```

## 3. Provider-free verification

Before provider-backed integration, you can verify that the gateway process is reachable:

### Check Health
```bash
curl http://127.0.0.1:8000/v1/health
```

### Check Available Models
```bash
curl http://127.0.0.1:8000/v1/models
```
