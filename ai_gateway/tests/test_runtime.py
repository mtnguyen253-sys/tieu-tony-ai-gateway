import pytest
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
    # Mặc định chưa có provider nào thì sẽ return 503
    client = TestClient(app)
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

