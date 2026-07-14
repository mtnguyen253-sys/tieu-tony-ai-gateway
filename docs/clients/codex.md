# Integration Guide: Codex

This guide describes how to connect the **Codex** CLI or extension tool to **Tiểu Tony AI Gateway** as an OpenAI-compatible provider.

> [!NOTE]
> *Template configuration only. This integration has not been manually verified with every Codex version. Please check your specific tool's configuration files and documentation to align with your exact version.*

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

## 3. Verification

Before integrating, you can verify that the gateway is running properly:

### Check Health
```bash
curl http://127.0.0.1:8000/v1/health
```

### Check Available Models
```bash
curl http://127.0.0.1:8000/v1/models
```
