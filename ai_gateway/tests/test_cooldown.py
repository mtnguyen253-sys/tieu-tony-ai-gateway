import pytest
from unittest.mock import MagicMock
from ai_gateway.core.cooldown import ProviderCooldownManager
from ai_gateway.core.circuit_breaker import Clock
from ai_gateway.core.router import PolicyRouter, RoutingDecision
from ai_gateway.registry.capability import CapabilityRegistry, TaskRequirement, RoutingPolicy
from ai_gateway.core.executor import ExecutionEngine, RateLimitException, ProviderUnavailableException
from ai_gateway.protocols.cap import AgentRequest, AgentResponse
from ai_gateway.adapters.base import BaseProvider
from ai_gateway.core.fallback import ProviderFallbackStrategy
from ai_gateway.core.retry import FixedRetryStrategy

class FakeClock(Clock):
    def __init__(self, current_time: float = 0.0):
        self.current_time = current_time
    def now(self) -> float:
        return self.current_time
    def advance(self, seconds: float):
        self.current_time += seconds

class MockProvider(BaseProvider):
    def __init__(self, name, model="test-model"):
        self.name = name
        self.default_model = model
        
    @property
    def capabilities(self):
        return {"codebase_reading": 8, "context_window": 8, "reasoning": 8, "routing": True}
        
    def connect(self) -> bool: return True
    def chat(self, request): return MagicMock()
    def stream(self, request): yield MagicMock()
    def tool_call(self, request): return MagicMock()
    def health(self): return {"status": "ok"}
    def estimate_cost(self, req): return 0.0

def test_cooldown_manager_basic():
    clock = FakeClock()
    manager = ProviderCooldownManager(clock=clock)
    
    manager.mark_cooldown("openrouter", duration=60.0, model="qwen/qwen-turbo")
    
    # Should be in cooldown
    assert manager.is_cooldown("openrouter", "qwen/qwen-turbo") == True
    
    # Other model on same provider should NOT be in cooldown unless the provider itself is marked
    # Wait, our is_cooldown checks `provider_name` as well. Let's see:
    # keys_to_check = [provider_name, f"{provider_name}:{model}"]
    # Yes, if we marked `openrouter:qwen/qwen-turbo`, then `openrouter` is NOT in cooldown.
    assert manager.is_cooldown("openrouter", "other-model") == False
    
    # Advance time
    clock.advance(61.0)
    assert manager.is_cooldown("openrouter", "qwen/qwen-turbo") == False

def test_cooldown_manager_provider_level():
    clock = FakeClock()
    manager = ProviderCooldownManager(clock=clock)
    
    # Mark whole provider
    manager.mark_cooldown("openrouter", duration=60.0)
    
    assert manager.is_cooldown("openrouter", "any-model") == True
    assert manager.is_cooldown("openrouter") == True

def test_router_excludes_cooldown():
    registry = MagicMock()
    provider_mock = MockProvider("openrouter")
    registry.all.return_value = {"openrouter": MagicMock(context_window=1000, cost=0.01, latency=100, tool_call=True, coding=8, reasoning=8, translation=8, quota_weight=1.0)}
    registry.get_provider.return_value = provider_mock
    
    clock = FakeClock()
    cooldown_manager = ProviderCooldownManager(clock=clock)
    router = PolicyRouter(registry=registry, cooldown_manager=cooldown_manager)
    
    # Mark cooldown
    cooldown_manager.mark_cooldown("openrouter")
    
    # Route should fail
    from ai_gateway.core.router import NoProviderAvailableException
    with pytest.raises(NoProviderAvailableException):
        router.route(TaskRequirement(), {}, {"openrouter": 1.0}, RoutingPolicy.BALANCED)
        
    # Advance time
    clock.advance(61.0)
    
    # Route should succeed
    decision = router.route(TaskRequirement(), {}, {"openrouter": 1.0}, RoutingPolicy.BALANCED)
    assert decision.provider_name == "openrouter"

def test_execution_engine_triggers_cooldown():
    clock = FakeClock()
    cooldown_manager = ProviderCooldownManager(clock=clock)
    breaker = MagicMock()
    breaker.is_available.return_value = True
    
    engine = ExecutionEngine(circuit_breaker=breaker, cooldown_manager=cooldown_manager)
    
    provider = MockProvider("openrouter")
    provider.chat = MagicMock(side_effect=RateLimitException("429", retry_after=30.0, model="test"))
    
    with pytest.raises(RateLimitException):
        engine.execute(AgentRequest(request_id="1", messages=[]), provider)
        
    assert cooldown_manager.is_cooldown("openrouter", "test") == True

def test_retry_strategy_no_dumb_retry():
    strategy = FixedRetryStrategy(max_retries=2)
    
    calls = 0
    def operation():
        nonlocal calls
        calls += 1
        raise RateLimitException("429", retry_after=30.0, model="test")
        
    with pytest.raises(RateLimitException):
        strategy.execute(operation)
        
    # Should only call once, no retries
    assert calls == 1

def test_fallback_behavior():
    registry = MagicMock()
    
    prov1 = MockProvider("prov1")
    prov2 = MockProvider("prov2")
    
    # Mock route to return prov1 first, then prov2
    router = MagicMock()
    router.route.side_effect = [
        RoutingDecision(provider_name="prov1", provider=prov1, score=1.0, reason="", excluded_providers={}, policy_used=RoutingPolicy.BALANCED, timestamp=0.0),
        RoutingDecision(provider_name="prov2", provider=prov2, score=0.9, reason="", excluded_providers={}, policy_used=RoutingPolicy.BALANCED, timestamp=0.0)
    ]
    
    fallback = ProviderFallbackStrategy(router)
    
    calls = []
    def operation(provider):
        calls.append(provider.name)
        if provider.name == "prov1":
            raise RateLimitException("429")
        return AgentResponse(response_id="ok", usage={})
        
    resp = fallback.execute(operation)
    assert resp.response_id == "ok"
    assert calls == ["prov1", "prov2"]
