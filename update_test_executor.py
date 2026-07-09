import re
with open("ai_gateway/tests/test_executor.py", "r") as f:
    content = f.read()

# Remove MockRouter
content = re.sub(r"class MockRouter:.*?def route.*?return RoutingDecision.*?timestamp=0\.0\n\s*\)\n", "", content, flags=re.DOTALL)

# Add half-open timeout test
test_half_open = """
def test_7_provider_timeout_in_half_open_trips_cb():
    from ai_gateway.core.circuit_breaker import CircuitState, Clock
    
    class FakeClock(Clock):
        def __init__(self):
            self.current_time = 0.0
        def now(self) -> float:
            return self.current_time
        def advance(self, seconds: float):
            self.current_time += seconds
            
    clock = FakeClock()
    req = AgentRequest(request_id="req7", messages=[])
    provider = MockProvider("p1", exception_to_raise=TimeoutException("timeout"))
    cb = CircuitBreaker(clock=clock)
    
    cb.trip("p1", duration=30.0)
    clock.advance(31.0)
    
    # State is now HALF_OPEN
    assert cb.get_state("p1") == CircuitState.HALF_OPEN
    
    engine = ExecutionEngine(circuit_breaker=cb) # type: ignore
    with pytest.raises(TimeoutException):
        engine.execute(req, provider=provider)
        
    # Should be back to OPEN
    assert cb.get_state("p1") == CircuitState.OPEN

def test_8_provider_success_records_success():
    from ai_gateway.core.circuit_breaker import CircuitState, Clock
    
    class FakeClock(Clock):
        def __init__(self):
            self.current_time = 0.0
        def now(self) -> float:
            return self.current_time
        def advance(self, seconds: float):
            self.current_time += seconds
            
    clock = FakeClock()
    req = AgentRequest(request_id="req8", messages=[])
    resp = AgentResponse(response_id="res8", content="data", usage={})
    provider = MockProvider("p1", response_to_return=resp)
    cb = CircuitBreaker(clock=clock)
    
    cb.trip("p1", duration=30.0)
    clock.advance(31.0)
    
    assert cb.get_state("p1") == CircuitState.HALF_OPEN
    
    engine = ExecutionEngine(circuit_breaker=cb) # type: ignore
    engine.execute(req, provider=provider)
        
    # Should be CLOSED now
    assert cb.get_state("p1") == CircuitState.CLOSED
"""

content += test_half_open

with open("ai_gateway/tests/test_executor.py", "w") as f:
    f.write(content)
