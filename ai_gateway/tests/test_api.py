import pytest
from fastapi.testclient import TestClient
from ai_gateway.api.app import create_app
from ai_gateway.protocols.cap import AgentResponse
from ai_gateway.core.router import NoProviderAvailableException

# We'll use a mocked orchestrator and registry for tests
class MockRegistry:
    def all(self):
        return {"mock-provider": {}}
    def get_provider(self, name):
        class MockProvider:
            default_model = "mock-model"
        return MockProvider()

class MockDuplicateRegistry:
    def all(self):
        return {"p1": {}, "p2": {}}
    def get_provider(self, name):
        class MockProvider:
            default_model = "shared-model"
        return MockProvider()

class MockEmptyRegistry:
    def all(self):
        return {}
    def get_provider(self, name):
        return None

class MockOrchestrator:
    def execute(self, req):
        return AgentResponse(
            response_id="test-123",
            content="Hello there!",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        )

class MockFailingOrchestrator:
    def execute(self, req):
        raise NoProviderAvailableException("All fallback providers exhausted.")

app = create_app(orchestrator=MockOrchestrator(), registry=MockRegistry())
client = TestClient(app)

duplicate_app = create_app(orchestrator=MockOrchestrator(), registry=MockDuplicateRegistry())
duplicate_client = TestClient(duplicate_app)

empty_app = create_app(orchestrator=MockFailingOrchestrator(), registry=MockEmptyRegistry())
empty_client = TestClient(empty_app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "ai_gateway"

def test_list_models():
    response = client.get("/models")
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp.get("object") == "list"
    assert "data" in json_resp
    assert isinstance(json_resp["data"], list)

def test_list_models_empty():
    response = empty_client.get("/models")
    assert response.status_code == 200
    json_resp = response.json()
    assert "data" in json_resp
    assert len(json_resp["data"]) == 0

def test_list_models_deduplication():
    response = duplicate_client.get("/models")
    assert response.status_code == 200
    json_resp = response.json()
    assert len(json_resp["data"]) == 1
    assert json_resp["data"][0]["id"] == "shared-model"

def test_chat_completions_missing_messages():
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": []
    }
    response = client.post("/chat/completions", json=payload)
    assert response.status_code == 422

def test_chat_completions_success():
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "Hi"}
        ]
    }
    response = client.post("/chat/completions", json=payload)
    assert response.status_code == 200
    
    json_resp = response.json()
    assert "choices" in json_resp
    assert len(json_resp["choices"]) > 0
    assert json_resp["choices"][0]["message"]["content"] == "Hello there!"
    assert json_resp["usage"]["total_tokens"] == 30
    assert json_resp["id"] == "test-123"

def test_chat_completions_no_provider():
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "Hi"}
        ]
    }
    response = empty_client.post("/chat/completions", json=payload)
    assert response.status_code == 503
    json_resp = response.json()
    assert "error" in json_resp
    assert json_resp["error"]["type"] == "provider_unavailable"
    assert json_resp["error"]["code"] == "no_provider_available"


def test_v1_health_check():
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_v1_list_models():
    response = client.get("/v1/models")
    assert response.status_code == 200
    assert response.json()["object"] == "list"

def test_v1_chat_completions_success():
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "Hi"}
        ]
    }
    response = client.post("/v1/chat/completions", json=payload)
    assert response.status_code == 200
    json_resp = response.json()
    assert "choices" in json_resp
    assert len(json_resp["choices"]) > 0
    assert json_resp["choices"][0]["message"]["content"] == "Hello there!"
