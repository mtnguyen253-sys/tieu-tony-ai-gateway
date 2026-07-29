from fastapi.testclient import TestClient

from ai_gateway.api.app import create_app
from ai_gateway.config.settings import Settings


def _provider_free_client() -> TestClient:
    settings = Settings(env={}, load_dotenv_file=False)
    return TestClient(create_app(app_settings=settings))


def test_v1_health_provider_free_contract():
    client = _provider_free_client()

    response = client.get("/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "ai_gateway"
    assert data["version"] == "0.1.0"
    assert data["provider_configured"] is False
    assert data["provider_count"] == 0
    assert data["enabled_provider_count"] == 0
    assert data["key_count"] == 0
    assert data["enabled_key_count"] == 0
    assert data["budget_mode"] == "normal"
    assert isinstance(data["health_tracking_enabled"], bool)


def test_v1_models_provider_free_contract_allows_empty_data():
    client = _provider_free_client()

    response = client.get("/v1/models")

    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "list"
    assert data["data"] == []
