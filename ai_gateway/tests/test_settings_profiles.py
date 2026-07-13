import pytest
import os
from unittest.mock import patch
from ai_gateway.config.settings import Settings

def test_settings_parse_providers():
    env_vars = {
        "AI_GATEWAY_PROVIDER_1_NAME": "my_provider",
        "AI_GATEWAY_PROVIDER_1_BASE_URL": "http://127.0.0.1:8000/v1",
        "AI_GATEWAY_PROVIDER_1_API_KEY": "dummy",
        "AI_GATEWAY_PROVIDER_1_MODEL": "test-model",
        "AI_GATEWAY_PROVIDER_1_ENABLED": "true",
        "AI_GATEWAY_PROVIDER_1_COST_INPUT_PER_MILLION": "1.5",
        "AI_GATEWAY_PROVIDER_1_COST_OUTPUT_PER_MILLION": "2.0",
        
        "AI_GATEWAY_PROVIDER_2_NAME": "other_provider",
        "AI_GATEWAY_PROVIDER_2_BASE_URL": "http://other",
        "AI_GATEWAY_PROVIDER_2_MODEL": "other-model",
        "AI_GATEWAY_PROVIDER_2_ENABLED": "false"
    }
    with patch.dict(os.environ, env_vars, clear=True):
        settings = Settings()
        assert len(settings.providers) == 2
        
        # Sort by name for reliable assertion
        providers = sorted(settings.providers, key=lambda x: x.name)
        
        p1 = providers[0]
        assert p1.name == "my_provider"
        assert p1.base_url == "http://127.0.0.1:8000/v1"
        assert p1.api_key == "dummy"
        assert p1.model == "test-model"
        assert p1.enabled is True
        assert p1.cost_input_per_million == 1.5
        assert p1.cost_output_per_million == 2.0
        assert p1.supports_streaming is True
        
        p2 = providers[1]
        assert p2.name == "other_provider"
        assert p2.enabled is False
        assert p2.cost_input_per_million is None

def test_settings_invalid_provider_ignored():
    env_vars = {
        "AI_GATEWAY_PROVIDER_1_NAME": "my_provider",
        "AI_GATEWAY_PROVIDER_1_API_KEY": "dummy",
        # Missing base_url and model
    }
    with patch.dict(os.environ, env_vars, clear=True):
        settings = Settings()
        assert len(settings.providers) == 0

