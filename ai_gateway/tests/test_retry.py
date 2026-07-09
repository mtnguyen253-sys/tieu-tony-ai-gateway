import pytest
from ai_gateway.core.retry import (
    NoRetryStrategy, 
    FixedRetryStrategy,
    AuthenticationException
)
from ai_gateway.core.executor import (
    TimeoutException,
    RateLimitException,
    ProviderUnavailableException,
    UnknownProviderException
)
from ai_gateway.protocols.cap import AgentResponse

def test_1_no_retry_success():
    strategy = NoRetryStrategy()
    calls = 0
    def op():
        nonlocal calls
        calls += 1
        return AgentResponse(response_id="1", content="ok", usage={})
        
    res = strategy.execute(op)
    assert res.content == "ok"
    assert calls == 1

def test_2_fixed_retry_timeout_success():
    strategy = FixedRetryStrategy()
    calls = 0
    def op():
        nonlocal calls
        calls += 1
        if calls < 3:
            raise TimeoutException("timeout")
        return AgentResponse(response_id="2", content="ok", usage={})
        
    res = strategy.execute(op)
    assert res.content == "ok"
    assert calls == 3

def test_3_fixed_retry_timeout_fails():
    strategy = FixedRetryStrategy(max_retries=3)
    calls = 0
    def op():
        nonlocal calls
        calls += 1
        raise TimeoutException("timeout")
        
    with pytest.raises(TimeoutException):
        strategy.execute(op)
        
    assert calls == 4  # Initial call + 3 retries

def test_4_rate_limit_no_retry():
    strategy = FixedRetryStrategy()
    calls = 0
    def op():
        nonlocal calls
        calls += 1
        raise RateLimitException("rate limit")
        
    with pytest.raises(RateLimitException):
        strategy.execute(op)
        
    assert calls == 1

def test_5_provider_unavailable_no_retry():
    strategy = FixedRetryStrategy()
    calls = 0
    def op():
        nonlocal calls
        calls += 1
        raise ProviderUnavailableException("unavailable")
        
    with pytest.raises(ProviderUnavailableException):
        strategy.execute(op)
        
    assert calls == 1

def test_6_unknown_provider_no_retry():
    strategy = FixedRetryStrategy()
    calls = 0
    def op():
        nonlocal calls
        calls += 1
        raise UnknownProviderException("unknown")
        
    with pytest.raises(UnknownProviderException):
        strategy.execute(op)
        
    assert calls == 1
    
def test_7_orchestrator_uses_retry_strategy():
    from ai_gateway.core.orchestrator import ExecutionOrchestrator
    from ai_gateway.protocols.cap import AgentRequest
    from ai_gateway.core.executor import ExecutionEngine
    
    class MockEngine:
        def execute(self, *args, **kwargs):
            return AgentResponse(response_id="123", content="engine_result", usage={})
            
    class MockRouter:
        def route(self, *args, **kwargs):
            from ai_gateway.core.router import RoutingDecision
            from ai_gateway.registry.capability import RoutingPolicy
            return RoutingDecision(
                provider_name="p1", 
                provider=None, 
                score=1.0, 
                reason="", 
                excluded_providers={}, 
                policy_used=RoutingPolicy.BALANCED, 
                timestamp=0.0
            )
            
    class MockStrategy(NoRetryStrategy):
        def __init__(self):
            self.called = False
            
        def execute(self, op):
            self.called = True
            return op()
            
    strategy = MockStrategy()
    orch = ExecutionOrchestrator(engine=MockEngine(), router=MockRouter(), retry_strategy=strategy) # type: ignore
    req = AgentRequest(request_id="test", messages=[])
    
    res = orch.execute(req)
    assert strategy.called is True
    assert res.content == "engine_result"
