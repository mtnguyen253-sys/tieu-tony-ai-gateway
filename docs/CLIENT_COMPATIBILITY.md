# Client Compatibility & Configuration Checklist

This document provides a comprehensive checklist and compatibility guide for integrating external OpenAI-compatible clients and tools (such as `Codex CLI`, `Hermes`, `OpenClaw`, `OpenAI Python/Node SDKs`, etc.) with **Tiá»ƒu Tony** AI Gateway.

---

## 1. Gateway Connection Parameters

When configuring any external client to route requests through the gateway, use the following configuration schema:

| Parameter | Required Value | Notes |
| :--- | :--- | :--- |
| **Base URL** | `http://127.0.0.1:8000/v1` | Explicitly include the `/v1` suffix (e.g. standard for OpenAI client routing). |
| **API Key** | Any string (e.g. `dummy`) | The gateway bypasses key validation checks for local client setups. |
| **Model** | Any supported model (e.g. `qwen/qwen3.6-plus`) | You can request specific models configured on your backends, or the default configured model. |

---

## 2. Compatibility Matrix

The gateway supports the core OpenAI Chat Completions API specification:

### ðŸŸ¢ `base_url` Customization
- **Requirement**: Client must support pointing to custom third-party endpoints.
- **Implementation**: The gateway binds to `http://127.0.0.1:8000` (by default) and exposes endpoints starting with `/v1`.

### ðŸŸ¢ `api_key` Policy
- **Requirement**: The gateway accepts any standard authorization header format (e.g., `Bearer dummy` or `Bearer <client-api-key>`).
- **Implementation**: API keys passed by external clients are accepted silently as local gateway auth bypass is enabled.

### ðŸŸ¢ Model Override
- **Requirement**: Clients often request specific models.
- **Implementation**: The gateway checks the requested model parameter and maps it to configured providers. If no mapping exists, it gracefully routes to the default provider's model (e.g., `qwen/qwen3.6-plus` via OpenRouter).

### ðŸŸ¢ Chat Streaming (`stream: true`)
- **Requirement**: Interactive assistants (e.g., terminal code helpers) require real-time streaming chunks.
- **Implementation**: Fully supported! The gateway proxies chunks from backend providers using server-sent events (`text/event-stream`), retaining compatibility with the OpenAI SDK streaming parser.

### ðŸŸ¢ Models List (`/v1/models`)
- **Requirement**: Client applications query `/v1/models` to discover which LLMs are available.
- **Implementation**: Returns a list of all currently configured and active provider models within the pool.

### ðŸŸ¢ Tool & Function Calling (`tools` & `tool_choice`)
- **Requirement**: Advanced agents pass schema-defined JSON tools for execution.
- **Implementation**: Passes-through standard OpenAI-format `tools` schemas to backend providers. Returns standard `tool_calls` structure inside JSON/streaming response blocks.

---

## 3. Client Troubleshooting Guide

### Issue: "Invalid Base URL" or "404 Not Found"
- **Check**: Ensure your client is targeting the correct port and ends with `/v1` (e.g., `http://127.0.0.1:8000/v1`, not `http://127.0.0.1:8000`).

### Issue: Connection Refused / Cannot Connect
- **Check**: Verify the gateway is running. Check your local firewall/port rules on port `8000`.

### Issue: API Key Missing or Unauthorized
- **Check**: Ensure you pass some value as the API key. Even if the gateway doesn't strictly validate the secret key, many client SDKs will fail on initialization if the `api_key` parameter is completely empty.

---

## 4. Usage Ledger Verification

To verify that requests made by external clients are being recorded properly:
1. Trigger a chat completion request using any configured client.
2. Verify that a new entry appears in `logs/usage.jsonl`.
3. Run the usage summary utility to view analytics:
   ```bash
   python -m ai_gateway.tools.usage_summary logs/usage.jsonl
   ```
