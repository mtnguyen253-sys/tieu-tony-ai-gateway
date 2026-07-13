import pytest
from unittest.mock import patch, MagicMock
from ai_gateway.adapters.openai_compatible import GenericOpenAICompatibleAdapter
from ai_gateway.protocols.cap import AgentRequest
from ai_gateway.core.executor import ProviderUnavailableException, AuthenticationException, RateLimitException

def test_generic_adapter_non_stream_success():
    adapter = GenericOpenAICompatibleAdapter(
        name="test_provider",
        base_url="http://test",
        api_key="test_key",
        model="test-model"
    )
    assert adapter.capabilities["cost"] == 0.0
    
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "Hello"}}],
        "usage": {"total_tokens": 10},
        "model": "test-model-resolved"
    }
    
    with patch("httpx.Client.post", return_value=mock_resp):
        req = AgentRequest(request_id="1", messages=[{"role": "user", "content": "hi"}], tools=None, stream=False)
        resp = adapter.chat(req)
        assert resp.content == "Hello"
        assert resp.usage["total_tokens"] == 10
        assert resp.model == "test-model-resolved"

def test_generic_adapter_stream_not_supported():
    adapter = GenericOpenAICompatibleAdapter(
        name="test_provider",
        base_url="http://test",
        api_key="test_key",
        model="test-model",
        supports_streaming=False
    )
    req = AgentRequest(request_id="1", messages=[{"role": "user", "content": "hi"}], tools=None, stream=True)
    with pytest.raises(ProviderUnavailableException) as exc:
        adapter.stream(req)
    assert "does not support streaming" in str(exc.value)

def test_generic_adapter_auth_error():
    adapter = GenericOpenAICompatibleAdapter(
        name="test_provider",
        base_url="http://test",
        api_key="test_key",
        model="test-model"
    )
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    with patch("httpx.Client.post", return_value=mock_resp):
        req = AgentRequest(request_id="1", messages=[], tools=None, stream=False)
        with pytest.raises(AuthenticationException):
            adapter.chat(req)

def test_generic_adapter_rate_limit():
    adapter = GenericOpenAICompatibleAdapter(
        name="test_provider",
        base_url="http://test",
        api_key="test_key",
        model="test-model"
    )
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_resp.headers = {"Retry-After": "10"}
    with patch("httpx.Client.post", return_value=mock_resp):
        req = AgentRequest(request_id="1", messages=[], tools=None, stream=False)
        with pytest.raises(RateLimitException) as exc:
            adapter.chat(req)
        assert exc.value.retry_after == 10.0

def test_generic_adapter_disabled():
    adapter = GenericOpenAICompatibleAdapter(
        name="test_provider",
        base_url="http://test",
        api_key="test_key",
        model="test-model",
        enabled=False
    )
    req = AgentRequest(request_id="1", messages=[], tools=None, stream=False)
    with pytest.raises(ProviderUnavailableException) as exc:
        adapter.chat(req)
    assert "is disabled" in str(exc.value)

