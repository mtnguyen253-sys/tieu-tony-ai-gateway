# Integration Guide: Codex

This guide describes how to connect the **Codex** CLI or extension tool to **Tiểu Tony AI Gateway** as an OpenAI-compatible provider.

> [!NOTE]
> *Template configuration only. This integration has not been manually verified with every Codex version. Please check your specific tool's configuration files and documentation to align with your exact version.*

## Provider-backed boundary

This guide is configuration guidance for using Codex with the local OpenAI-compatible gateway. Provider-free checks are limited to the local health and models endpoints documented below and in `README.md`, `RUN_LOCAL.md`, and `docs/CLIENT_COMPATIBILITY.md`.

Live Codex chat, streaming, tool/function calling, usage-ledger writes, and end-to-end provider connectivity require separately approved provider configuration and live verification before they should be treated as verified.

## 1. Connection Configuration

- **Base URL**: `http://127.0.0.1:8000/v1`
- **API Key**: `dummy` (or any non-empty string)
- **Model**: Any model listed under `http://127.0.0.1:8000/v1/models` (e.g., `qwen/qwen3.6-plus`)

## 2. Configuration Example

Most Codex versions accept environment variables or custom JSON configurations.

### Option A: Environment Variables
If Codex reads from standard OpenAI environment variables, export them as follows:
```bash
export OPENAI_BASE_URL="http://127.0.0.1:8000/v1"
export OPENAI_API_KEY="dummy"
export CODEX_MODEL="qwen/qwen3.6-plus"
```

### Option B: Custom Configuration File (JSON/YAML)
For Codex client configuration files (e.g., in `~/.codex/config.json`), you can define:
```json
{
  "api_type": "open_ai",
  "api_base": "http://127.0.0.1:8000/v1",
  "api_key": "dummy",
  "model": "qwen/qwen3.6-plus"
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
