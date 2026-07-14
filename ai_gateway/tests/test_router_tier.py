import pytest
from ai_gateway.core.router import PolicyRouter, RoutingDecision
from ai_gateway.registry.capability import CapabilityRegistry, TaskRequirement, ProviderCapability, RoutingPolicy
from ai_gateway.core.task_classifier import TaskClassification, TaskComplexity, ModelTier
from ai_gateway.core.routing_policy_matrix import RoutingPolicyMatrix

@pytest.fixture
def registry():
    reg = CapabilityRegistry()
    
    class MockProvider:
        def __init__(self, caps):
            self.capabilities = caps
        def health(self):
            return {"status": "ok"}
            
    # Add a strong provider
    reg.register("strong_prov", MockProvider({
        "coding": 9.5,
        "reasoning": 9.5,
        "cost": 8.0,
        "model_tier": "strong"
    }))
    
    # Add a balanced provider
    reg.register("balanced_prov", MockProvider({
        "coding": 8.0,
        "reasoning": 8.0,
        "cost": 2.0,
        "model_tier": "balanced"
    }))
    
    # Add a cheap provider
    reg.register("cheap_prov", MockProvider({
        "coding": 6.0,
        "reasoning": 6.0,
        "cost": 0.1,
        "model_tier": "cheap"
    }))
    
    # Add a long context provider
    reg.register("long_ctx_prov", MockProvider({
        "coding": 8.0,
        "cost": 5.0,
        "model_tier": "long_context",
        "max_context_tokens": 128000,
        "supports_prompt_cache": True
    }))
    
    return reg

@pytest.fixture
def router(registry):
    return PolicyRouter(registry)

def test_router_picks_cheap_for_simple(router):
    req = TaskRequirement(task_type="TRANSLATION")
    
    policy_matrix = RoutingPolicyMatrix()
    task_class = TaskClassification(complexity=TaskComplexity.SIMPLE, reason="test")
    task_policy = policy_matrix.get_policy(task_class)
    
    context = {"task_policy": task_policy}
    
    decision = router.route(req, context, {}, RoutingPolicy.BALANCED)
    assert decision.provider_name == "cheap_prov"

def test_router_picks_strong_for_complex(router):
    req = TaskRequirement(task_type="CODING")
    
    policy_matrix = RoutingPolicyMatrix()
    task_class = TaskClassification(complexity=TaskComplexity.COMPLEX, reason="test")
    task_policy = policy_matrix.get_policy(task_class)
    
    context = {"task_policy": task_policy}
    
    decision = router.route(req, context, {}, RoutingPolicy.BALANCED)
    assert decision.provider_name == "strong_prov"

def test_router_picks_long_context(router):
    req = TaskRequirement(task_type="GENERAL")
    
    policy_matrix = RoutingPolicyMatrix()
    task_class = TaskClassification(complexity=TaskComplexity.LONG_CONTEXT, reason="test", is_long_context=True)
    task_policy = policy_matrix.get_policy(task_class)
    
    context = {"task_policy": task_policy}
    
    decision = router.route(req, context, {}, RoutingPolicy.BALANCED)
    assert decision.provider_name == "long_ctx_prov"

def test_missing_model_tier_does_not_crash(router, registry):
    class MockProvider:
        def __init__(self, caps):
            self.capabilities = caps
        def health(self):
            return {"status": "ok"}
            
    registry.register("missing_tier_prov", MockProvider({
        "coding": 9.9,
        "reasoning": 9.9,
        "cost": 1.0,
        # missing model_tier, should default to "balanced"
    }))
    
    req = TaskRequirement()
    task_class = TaskClassification(complexity=TaskComplexity.STANDARD, reason="test")
    task_policy = RoutingPolicyMatrix().get_policy(task_class)
    context = {"task_policy": task_policy}
    
    # "missing_tier_prov" has amazing stats and very low cost, defaults to balanced. 
    # For STANDARD tasks, balanced is favored. It should win.
    decision = router.route(req, context, {}, RoutingPolicy.BALANCED)
    assert decision.provider_name == "missing_tier_prov"
