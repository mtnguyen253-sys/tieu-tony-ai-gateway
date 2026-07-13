import pytest
from ai_gateway.core.router import PolicyRouter, NoProviderAvailableException
from ai_gateway.registry.capability import CapabilityRegistry, TaskRequirement, RoutingPolicy, TaskType
from ai_gateway.adapters.openai_compatible import GenericOpenAICompatibleAdapter
from ai_gateway.core.circuit_breaker import CircuitBreaker
from ai_gateway.core.cooldown import ProviderCooldownManager

def setup_registry():
    registry = CapabilityRegistry()
    p1 = GenericOpenAICompatibleAdapter(name="premium", base_url="http://p1", api_key="1", model="m1")
    p2 = GenericOpenAICompatibleAdapter(name="cheap", base_url="http://p2", api_key="2", model="m2")
    registry.register("premium", p1)
    registry.register("cheap", p2)
    return registry

def test_router_normal_mode():
    # To make premium win in 'economy/normal' (prefer_cheaper=True defaults when no budget manager):
    registry = setup_registry()
    registry.get("premium").coding = 10.0
    registry.get("premium").cost = 1.0
    registry.get("cheap").coding = 2.0
    registry.get("cheap").cost = 0.0
    
    router = PolicyRouter(registry, CircuitBreaker(), ProviderCooldownManager())
    req = TaskRequirement(task_type=TaskType.CODING)
    decision = router.route(req, {"budget_mode": "normal"}, {}, RoutingPolicy.BALANCED)
    assert decision.provider_name == "premium"

def test_router_economy_mode():
    registry = setup_registry()
    registry.get("premium").coding = 10.0
    registry.get("premium").cost = 8.0  # high cost
    registry.get("cheap").coding = 4.0
    registry.get("cheap").cost = 0.0
    
    router = PolicyRouter(registry, CircuitBreaker(), ProviderCooldownManager())
    req = TaskRequirement(task_type=TaskType.CODING)
    decision = router.route(req, {"budget_mode": "economy"}, {}, RoutingPolicy.BALANCED)
    assert decision.provider_name == "cheap"

def test_router_emergency_mode():
    registry = setup_registry()
    registry.get("premium").coding = 10.0
    registry.get("premium").cost = 5.0
    registry.get("cheap").coding = 2.0
    registry.get("cheap").cost = 0.0
    
    router = PolicyRouter(registry, CircuitBreaker(), ProviderCooldownManager())
    req = TaskRequirement(task_type=TaskType.CODING)
    decision = router.route(req, {"budget_mode": "emergency"}, {}, RoutingPolicy.BALANCED)
    assert decision.provider_name == "cheap"

def test_router_cooldown_excludes_provider():
    registry = setup_registry()
    registry.get("premium").coding = 10.0
    registry.get("premium").cost = 1.0
    registry.get("cheap").coding = 2.0
    registry.get("cheap").cost = 0.0
    
    cooldown = ProviderCooldownManager()
    cooldown.mark_cooldown("premium", 60.0)
    
    router = PolicyRouter(registry, CircuitBreaker(), cooldown)
    req = TaskRequirement(task_type=TaskType.CODING)
    decision = router.route(req, {"budget_mode": "normal"}, {}, RoutingPolicy.BALANCED)
    assert decision.provider_name == "cheap"

def test_router_disabled_provider_not_picked():
    registry = CapabilityRegistry()
    p3 = GenericOpenAICompatibleAdapter(name="disabled_prov", base_url="http://p3", api_key="3", model="m3", enabled=False)
    registry.register("disabled_prov", p3)
    
    router = PolicyRouter(registry, CircuitBreaker(), ProviderCooldownManager())
    req = TaskRequirement(task_type=TaskType.CODING)
    with pytest.raises(NoProviderAvailableException):
        router.route(req, {"budget_mode": "normal"}, {}, RoutingPolicy.BALANCED)
