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


@patch("ai_gateway.adapters.openrouter.httpx.Client")
def test_openrouter_adapter_401(mock_client_class):
    adapter = OpenRouterAdapter(api_key="test-key")
    req = AgentRequest(request_id="req_or", messages=[{"role": "user", "content": "Hi OR!"}])
    
    mock_response = MagicMock()
    mock_response.status_code = 401
    
    mock_client = MagicMock()
    mock_client.post.return_value = mock_response
    mock_client_class.return_value.__enter__.return_value = mock_client
    
    from ai_gateway.core.executor import AuthenticationException
    with pytest.raises(AuthenticationException):
        adapter.chat(req)

@patch("ai_gateway.adapters.openrouter.httpx.Client")
def test_openrouter_adapter_429(mock_client_class):
    adapter = OpenRouterAdapter(api_key="test-key")
    req = AgentRequest(request_id="req_or", messages=[{"role": "user", "content": "Hi OR!"}])
    
    mock_response = MagicMock()
    mock_response.status_code = 429
    
    mock_client = MagicMock()
    mock_client.post.return_value = mock_response
    mock_client_class.return_value.__enter__.return_value = mock_client
    
    from ai_gateway.core.executor import RateLimitException
    with pytest.raises(RateLimitException):
        adapter.chat(req)

@patch("ai_gateway.adapters.openrouter.httpx.Client")
def test_openrouter_adapter_500(mock_client_class):
    adapter = OpenRouterAdapter(api_key="test-key")
    req = AgentRequest(request_id="req_or", messages=[{"role": "user", "content": "Hi OR!"}])
    
    mock_response = MagicMock()
    mock_response.status_code = 500
    
    mock_client = MagicMock()
    mock_client.post.return_value = mock_response
    mock_client_class.return_value.__enter__.return_value = mock_client
    
    from ai_gateway.core.executor import ProviderUnavailableException
    with pytest.raises(ProviderUnavailableException):
        adapter.chat(req)

@patch("ai_gateway.adapters.openrouter.httpx.Client")
def test_openrouter_adapter_timeout(mock_client_class):
    adapter = OpenRouterAdapter(api_key="test-key")
    req = AgentRequest(request_id="req_or", messages=[{"role": "user", "content": "Hi OR!"}])
    
    import httpx
    mock_client = MagicMock()
    mock_client.post.side_effect = httpx.TimeoutException("Timeout")
    mock_client_class.return_value.__enter__.return_value = mock_client
    
    from ai_gateway.core.executor import TimeoutException
    with pytest.raises(TimeoutException):
        adapter.chat(req)

@patch("ai_gateway.adapters.openrouter.httpx.Client")
def test_openrouter_adapter_model_normalization(mock_client_class):
    adapter = OpenRouterAdapter(api_key="test-key")
    req = AgentRequest(request_id="req_or", messages=[{"role": "user", "content": "Hi OR!"}])
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "ok"}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
        "model": "qwen/qwen-turbo"
    }
    
    mock_client = MagicMock()
    mock_client.post.return_value = mock_response
    mock_client_class.return_value.__enter__.return_value = mock_client
    
    resp = adapter.chat(req)
    assert resp.model == "qwen/qwen-turbo"


def test_openrouter_adapter_usage_extraction():
    from ai_gateway.adapters.openrouter import OpenRouterAdapter
    import httpx
    
    adapter = OpenRouterAdapter(api_key="test")
    
    class MockResponse:
        def __init__(self, json_data, status_code=200):
            self._json_data = json_data
            self.status_code = status_code
        def json(self):
            return self._json_data
            
    mock_data = {
        "id": "gen-123",
        "model": "openrouter/qwen-plus",
        "choices": [{"message": {"content": "hello"}}],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
            "prompt_tokens_details": {
                "cached_tokens": 5
            }
        }
    }
    
    import unittest.mock as mock
    with mock.patch("httpx.Client.post", return_value=MockResponse(mock_data)):
        req = AgentRequest(request_id="req1", messages=[])
        resp = adapter.chat(req)
        
        assert resp.model == "openrouter/qwen-plus"
        assert resp.usage["prompt_tokens"] == 10
        assert resp.usage["completion_tokens"] == 20
        assert resp.usage["total_tokens"] == 30
        assert resp.usage.get("prompt_tokens_details", {}).get("cached_tokens") == 5

