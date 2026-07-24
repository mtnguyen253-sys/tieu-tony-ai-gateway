from ai_gateway.api import app as app_module
from ai_gateway.adapters.base import BaseProvider
from ai_gateway.config.settings import Settings
from ai_gateway.core.provider_statistics import get_global_statistics_updater
from ai_gateway.core.usage import UsageEvent
from ai_gateway.registry.capability import CapabilityRegistry, RoutingPolicy, TaskRequirement, TaskType


class MockProvider(BaseProvider):
    def __init__(self, name, coding, cost):
        self._name = name
        self._coding = coding
        self._cost = cost

    @property
    def name(self):
        return self._name

    @property
    def capabilities(self):
        return {
            "coding": self._coding,
            "reasoning": 5.0,
            "translation": 5.0,
            "context_window": 8000,
            "tool_call": True,
            "latency": 500.0,
            "cost": self._cost,
            "supports_prompt_cache": True,
        }

    def connect(self):
        return True

    def chat(self, request):
        return None

    def stream(self, request):
        yield None

    def tool_call(self, request):
        return None

    def health(self):
        return {"status": "ok"}

    def estimate_cost(self, req):
        return 0.0


def test_global_statistics_updater_uses_requested_window_size(monkeypatch):
    monkeypatch.setattr("ai_gateway.core.provider_statistics._global_statistics_updater", None)

    updater = get_global_statistics_updater(window_size=3)

    assert updater.window_size == 3


def test_create_app_injects_adaptive_settings_and_window_size(monkeypatch):
    captured = {}
    original_router = app_module.PolicyRouter

    class CapturingRouter(original_router):
        def __init__(self, *args, **kwargs):
            captured.update(kwargs)
            super().__init__(*args, **kwargs)
            captured["router"] = self

    settings = Settings(
        env={
            "AI_GATEWAY_ADAPTIVE_WINDOW_SIZE": "3",
            "AI_GATEWAY_ADAPTIVE_ROUTING_ENABLED": "false",
        },
        load_dotenv_file=False,
    )
    monkeypatch.setattr(app_module, "PolicyRouter", CapturingRouter)

    registry = CapabilityRegistry()
    registry.register("higher_base_score", MockProvider("higher_base_score", coding=20.0, cost=1.0))
    registry.register("better_history", MockProvider("better_history", coding=0.0, cost=1.0))

    app_module.create_app(app_settings=settings, registry=registry)

    assert captured["statistics_updater"].window_size == 3
    assert captured["adaptive_settings"] is settings
    for i in range(3):
        captured["statistics_updater"].update(UsageEvent(
            request_id=f"failure-{i}",
            timestamp=float(i),
            provider="higher_base_score",
            status="error",
            error_type="TimeoutException",
            latency_ms=5000.0,
        ))
        captured["statistics_updater"].update(UsageEvent(
            request_id=f"success-{i}",
            timestamp=float(i),
            provider="better_history",
            status="success",
            latency_ms=100.0,
            estimated_cost=0.01,
            cached_input_tokens=100,
        ))

    decision = captured["router"].route(
        TaskRequirement(task_type=TaskType.CODING),
        {},
        {},
        RoutingPolicy.BALANCED,
    )

    assert decision.provider_name == "higher_base_score"
