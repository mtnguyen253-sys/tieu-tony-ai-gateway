import pytest
from unittest.mock import patch, MagicMock
from ai_gateway.protocols.cap import AgentRequest, AgentResponse
from ai_gateway.adapters.base import BaseProvider
from ai_gateway.adapters.gemini import GeminiAdapter
from ai_gateway.adapters.openrouter import OpenRouterAdapter
from ai_gateway.adapters.google_free import GoogleFreeAdapter

def test_gemini_adapter_is_base_provider():
    adapter = GeminiAdapter()
    assert isinstance(adapter, BaseProvider)

def test_gemini_adapter_capabilities():
    adapter = GeminiAdapter()
    caps = adapter.capabilities
    assert caps["codebase_reading"] == 10
    assert caps["context_window"] == 10
    assert caps["reasoning"] == 9

def test_gemini_adapter_chat_integrity():
    adapter = GeminiAdapter()
    req = AgentRequest(
        request_id="req_123",
        messages=[{"role": "user", "content": "Hello Gemini!"}]
    )
    
    assert adapter.connect() is True
    
    response = adapter.chat(req)
    
    assert isinstance(response, AgentResponse)
    assert response.response_id.startswith("gemini_res_")
    assert "Mocked Gemini response" in response.content
    assert "req_123" in response.content
    assert response.usage["prompt_tokens"] == 15
    assert response.usage["completion_tokens"] == 20

def test_gemini_adapter_tool_call():
    adapter = GeminiAdapter()
    req = AgentRequest(
        request_id="req_tool",
        messages=[{"role": "user", "content": "Use a tool"}],
        tools=[{"name": "mock_tool", "description": "Mock"}]
    )
    
    response = adapter.tool_call(req)
    assert response.content is None
    assert response.tool_calls is not None
    assert len(response.tool_calls) == 1
    assert response.tool_calls[0].name == "mock_tool"

def test_openrouter_adapter_is_base_provider():
    adapter = OpenRouterAdapter(api_key="test-key")
    assert isinstance(adapter, BaseProvider)

@patch("ai_gateway.adapters.openrouter.httpx.Client")
def test_openrouter_adapter_chat_integrity(mock_client_class):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Mocked OpenRouter response"}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}
    }
    
    mock_client = MagicMock()
    mock_client.post.return_value = mock_response
    mock_client_class.return_value.__enter__.return_value = mock_client

    adapter = OpenRouterAdapter(api_key="test-key")
    req = AgentRequest(request_id="req_or", messages=[{"role": "user", "content": "Hi OR!"}])
    assert adapter.connect() is True
    
    response = adapter.chat(req)
    assert isinstance(response, AgentResponse)
    assert response.response_id.startswith("or_res_")
    assert "Mocked OpenRouter response" in response.content

def test_google_free_adapter_is_base_provider():
    adapter = GoogleFreeAdapter()
    assert isinstance(adapter, BaseProvider)

def test_google_free_adapter_chat_integrity():
    adapter = GoogleFreeAdapter()
    req = AgentRequest(request_id="req_gf", messages=[{"role": "user", "content": "Hi GF!"}])
    assert adapter.connect() is True
    response = adapter.chat(req)
    assert isinstance(response, AgentResponse)
    assert response.response_id.startswith("gf_res_")
    assert "Mocked Google Free response" in response.content
    assert adapter.estimate_cost(req) == 0.0

