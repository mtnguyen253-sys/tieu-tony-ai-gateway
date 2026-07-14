import pytest
from unittest.mock import MagicMock
from ai_gateway.core.router import PolicyRouter
from ai_gateway.registry.capability import CapabilityRegistry, TaskRequirement, RoutingPolicy, TaskType
from ai_gateway.core.provider_statistics import StatisticsUpdater, get_global_statistics_updater
from ai_gateway.core.usage import UsageEvent
from ai_gateway.adapters.base import BaseProvider

class SimpleMockProvider(BaseProvider):
    def __init__(self, name, coding=8.0, cost=1.0):
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
            "supports_prompt_cache": True
        }

    def connect(self) -> bool: return True
    def chat(self, request): return MagicMock()
    def stream(self, request): yield MagicMock()
    def tool_call(self, request): return MagicMock()
    def health(self): return {"status": "ok"}
    def estimate_cost(self, req): return 0.0

def test_adaptive_router_bonuses_and_penalties():
    registry = CapabilityRegistry()
    prov_a = SimpleMockProvider("prov_a", coding=9.0, cost=2.0)  # Normally higher score
    prov_b = SimpleMockProvider("prov_b", coding=8.0, cost=1.0)  # Normally lower score
    registry.register("prov_a", prov_a)
    registry.register("prov_b", prov_b)

    # Use a local statistics updater to isolate tests
    updater = StatisticsUpdater(window_size=10)
    updater.reset()

    # Create poor history for prov_a (high timeouts)
    for i in range(10):
        updater.update(UsageEvent(
            request_id=f"a_{i}",
            timestamp=123.0,
            provider="prov_a",
            status="error",
            error_type="TimeoutException",
            latency_ms=5000.0
        ))

    # Create excellent history for prov_b (high success, low latency, cache hits)
    for i in range(10):
        updater.update(UsageEvent(
            request_id=f"b_{i}",
            timestamp=123.0,
            provider="prov_b",
            status="success",
            latency_ms=200.0,
            estimated_cost=0.01,
            cached_input_tokens=100  # cache hit!
        ))

    router = PolicyRouter(registry, statistics_updater=updater)
    requirement = TaskRequirement(task_type=TaskType.CODING)
    
    # Check stats
    stats_a = updater.get_stats("prov_a")
    stats_b = updater.get_stats("prov_b")
    
    # prov_a success rate is 0.0%, timeout rate is 100%
    # prov_b success rate is 100%, latency low, cache hit 100%
    
    decision = router.route(requirement, {}, {}, RoutingPolicy.BALANCED)
    
    # Normally prov_a would win due to higher coding capability (9.0 vs 8.0)
    # But because prov_a is penalized (timeout > 10% penalty) and prov_b gets bonuses (success rate >= 98% bonus, cache bonus, etc.)
    # prov_b should win!
    assert decision.provider_name == "prov_b"
