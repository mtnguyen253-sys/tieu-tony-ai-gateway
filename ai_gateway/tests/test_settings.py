import os
import pytest
from ai_gateway.config.settings import Settings

def test_settings_default():
    s = Settings()
    assert s.host == os.getenv("AI_GATEWAY_HOST", "127.0.0.1")
    assert isinstance(s.port, int)
    assert s.log_level == os.getenv("AI_GATEWAY_LOG_LEVEL", "info")
    assert s.budget_mode == os.getenv("AI_GATEWAY_BUDGET_MODE", "normal")
