import pytest
from ai_gateway.core.fallback import ProviderFallbackStrategy, NoFallbackStrategy
from ai_gateway.core.router import PolicyRouter, RoutingDecision, NoProviderAvailableException
from ai_gateway.core.executor import (
    ProviderUnavailableException,
    CircuitOpenException,
    AuthenticationException,
    UnknownProviderException,
    ExecutionEngine
)
from ai_gateway.protocols.cap import AgentResponse

class MockProvider:
    def __init__(self, name):
        self.name = name

class MockRouter:
    def __init__(self, sequence):
        self.sequence = sequence
        self.call_count = 0
        self.last_context = None

    def route(self, requirement, context, quotas, policy):
        from ai_gateway.registry.capability import RoutingPolicy
        self.last_context = context
        index = self.call_count
        self.call_count += 1
        if index >= len(self.sequence):
            raise NoProviderAvailableException("No more providers")
        
        provider_name = self.sequence[index]
        
        if not provider_name:
            raise NoProviderAvailableException("No provider")
            
        return RoutingDecision(
            provider_name=provider_name,
            provider=MockProvider(provider_name),
            score=10.0,
            reason="test",
            excluded_providers={},
            policy_used=policy or RoutingPolicy.BALANCED,
            timestamp=0.0
        )

def test_1_first_provider_success():
    router = MockRouter(["p1", "p2"])
    fallback = ProviderFallbackStrategy(router=router) # type: ignore
    
    def op(provider):
        return AgentResponse(response_id="1", content=f"ok_{provider.name}", usage={})
        
    res = fallback.execute(op, context={})
    assert res.content == "ok_p1"
    assert router.call_count == 1

def test_2_first_provider_unavailable_fallback_to_second():
    router = MockRouter(["p1", "p2"])
    fallback = ProviderFallbackStrategy(router=router) # type: ignore
    
    def op(provider):
        if provider.name == "p1":
            raise ProviderUnavailableException("p1 down")
        return AgentResponse(response_id="2", content=f"ok_{provider.name}", usage={})
        
    res = fallback.execute(op, context={})
    assert res.content == "ok_p2"
    assert router.call_count == 2
    assert "p1" in router.last_context["excluded_providers"]

def test_3_first_provider_circuit_open_fallback():
    router = MockRouter(["p1", "p2"])
    fallback = ProviderFallbackStrategy(router=router) # type: ignore
    
    def op(provider):
        if provider.name == "p1":
            raise CircuitOpenException("p1 open")
        return AgentResponse(response_id="3", content=f"ok_{provider.name}", usage={})
        
    res = fallback.execute(op, context={})
    assert res.content == "ok_p2"
    assert router.call_count == 2
    assert "p1" in router.last_context["excluded_providers"]

def test_4_first_provider_auth_exception_no_fallback():
    router = MockRouter(["p1", "p2"])
    fallback = ProviderFallbackStrategy(router=router) # type: ignore
    
    def op(provider):
        if provider.name == "p1":
            raise AuthenticationException("p1 auth failed")
        return AgentResponse(response_id="4", content="ok", usage={})
        
    with pytest.raises(AuthenticationException):
        fallback.execute(op, context={})
        
    assert router.call_count == 1

def test_5_no_provider_available():
    router = MockRouter([])
    fallback = ProviderFallbackStrategy(router=router) # type: ignore
    
    def op(provider):
        pass
        
    with pytest.raises(NoProviderAvailableException):
        fallback.execute(op, context={})

def test_6_both_providers_fail():
    router = MockRouter(["p1", "p2"])
    fallback = ProviderFallbackStrategy(router=router) # type: ignore
    
    def op(provider):
        if provider.name == "p1":
            raise ProviderUnavailableException("p1 down")
        if provider.name == "p2":
            raise CircuitOpenException("p2 open")
            
    with pytest.raises(NoProviderAvailableException):
        fallback.execute(op, context={})
        
    assert router.call_count == 3  # Try p1, try p2, then empty

def test_7_router_does_not_pick_failed_provider():
    # Because we check the excluded_providers is updated correctly.
    router = MockRouter(["p1", "p2"])
    fallback = ProviderFallbackStrategy(router=router) # type: ignore
    
    def op(provider):
        if provider.name == "p1":
            raise ProviderUnavailableException("p1 down")
        return AgentResponse(response_id="7", content="ok", usage={})
        
    fallback.execute(op, context={"excluded_providers": []})
    
    assert "p1" in router.last_context["excluded_providers"]
