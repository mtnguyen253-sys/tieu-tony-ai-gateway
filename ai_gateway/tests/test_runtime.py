import pytest
import os
from fastapi.testclient import TestClient
from ai_gateway.api.app import app, create_app
from ai_gateway.protocols.cap import AgentResponse

def test_app_import():
    assert app is not None
    assert app.title == "Tiểu Tony AI Gateway"

def test_create_app():
    new_app = create_app()
    assert new_app is not None

def test_default_runtime_no_provider():
    from ai_gateway.config.settings import Settings
    # Mặc định chưa có provider nào thì sẽ return 503
    empty_settings = Settings(env={}, load_dotenv_file=False)
    client = TestClient(create_app(app_settings=empty_settings))
    response = client.post(
        "/chat/completions",
        json={
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello"}]
        }
    )
    assert response.status_code == 503
    data = response.json()
    assert "error" in data
    assert data["error"]["type"] == "provider_unavailable"
    assert data["error"]["code"] == "no_provider_available"

def test_default_runtime_no_provider_ignores_shell_env(monkeypatch):
    from ai_gateway.config.settings import Settings
    monkeypatch.setenv("OPENROUTER_API_KEY", "fake-key")
    monkeypatch.setenv("OPENROUTER_MODEL", "fake-model")
    monkeypatch.setenv("AI_GATEWAY_PROVIDER_1_NAME", "fake")
    monkeypatch.setenv("AI_GATEWAY_PROVIDER_1_BASE_URL", "http://fake")
    monkeypatch.setenv("AI_GATEWAY_PROVIDER_1_API_KEY", "fake-key")
    monkeypatch.setenv("AI_GATEWAY_PROVIDER_1_MODEL", "fake-model")

    empty_settings = Settings(env={}, load_dotenv_file=False)
    client = TestClient(create_app(app_settings=empty_settings))

    response = client.post("/chat/completions", json={
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Hello"}],
    })

    assert response.status_code == 503

def test_legacy_openrouter_config(monkeypatch):
    from ai_gateway.config.settings import Settings
    from ai_gateway.api.app import create_app
    
    # Simulate legacy OpenRouter config
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-12345")
    monkeypatch.setenv("OPENROUTER_MODEL", "qwen/qwen-test")
    
    # Use load_dotenv_file=False to ensure only our monkeypatched env is used
    settings = Settings(env=os.environ, load_dotenv_file=False)
    client = TestClient(create_app(app_settings=settings))
    
    # 1. Health check counts
    resp_health = client.get("/v1/health")
    assert resp_health.status_code == 200
    data_health = resp_health.json()
    assert data_health["provider_configured"] is True
    assert data_health["provider_count"] >= 1
    
    # 2. Models list
    resp_models = client.get("/v1/models")
    assert resp_models.status_code == 200
    data_models = resp_models.json()
    model_ids = [m["id"] for m in data_models["data"]]
    assert "qwen/qwen-test" in model_ids

def test_mock_runtime_returns_200():
    class MockOrchestrator:
        def execute(self, req):
            return AgentResponse(response_id="123", content="mocked response", usage={})
    
    mock_app = create_app(orchestrator=MockOrchestrator())
    client = TestClient(mock_app)
    response = client.post(
        "/chat/completions",
        json={
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "Hello"}]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "choices" in data
    assert data["choices"][0]["message"]["content"] == "mocked response"

def test_models_returns_list():
    client = TestClient(app)
    response = client.get("/models")
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "list"
    assert isinstance(data["data"], list)

