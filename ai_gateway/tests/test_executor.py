import pytest
import logging
from ai_gateway.core.executor import (
    ExecutionEngine, RateLimitException, ProviderUnavailableException, TimeoutException, UnknownProviderException, ValidationException
)
from ai_gateway.core.circuit_breaker import CircuitBreaker
from ai_gateway.protocols.cap import AgentRequest, AgentResponse

class MockProvider:
    def __init__(self, name: str, exception_to_raise=None, response_to_return=None):
        self.name = name
        self.exception_to_raise = exception_to_raise
        self.response_to_return = response_to_return
        
    def chat(self, request: AgentRequest) -> AgentResponse:
        if self.exception_to_raise:
            raise self.exception_to_raise
        return self.response_to_return


def test_1_provider_success():
    req = AgentRequest(request_id="req1", messages=[])
    resp = AgentResponse(response_id="res1", content="ok", usage={})
    
    provider = MockProvider("p1", response_to_return=resp)
    cb = CircuitBreaker()
    engine = ExecutionEngine(circuit_breaker=cb) # type: ignore
    result = engine.execute(req, provider=provider)
    assert result == resp

def test_2_provider_rate_limit_trips_cb():
    req = AgentRequest(request_id="req2", messages=[])
    provider = MockProvider("p1", exception_to_raise=RateLimitException("429"))
    cb = CircuitBreaker()
    engine = ExecutionEngine(circuit_breaker=cb) # type: ignore
    with pytest.raises(RateLimitException):
        engine.execute(req, provider=provider)
        
    assert cb.is_available("p1") is False

def test_3_provider_timeout_no_trip():
    req = AgentRequest(request_id="req3", messages=[])
    provider = MockProvider("p1", exception_to_raise=TimeoutException("timeout"))
    cb = CircuitBreaker()
    engine = ExecutionEngine(circuit_breaker=cb) # type: ignore
    with pytest.raises(TimeoutException):
        engine.execute(req, provider=provider)
        
    assert cb.is_available("p1") is True

def test_4_provider_none_raises_validation():
    req = AgentRequest(request_id="req4", messages=[])
    cb = CircuitBreaker()
    engine = ExecutionEngine(circuit_breaker=cb) # type: ignore
    with pytest.raises(ValidationException):
        engine.execute(req, provider=None)

def test_5_provider_returns_agent_response():
    req = AgentRequest(request_id="req5", messages=[])
    resp = AgentResponse(response_id="res5", content="data", usage={})
    provider = MockProvider("p1", response_to_return=resp)
    cb = CircuitBreaker()
    engine = ExecutionEngine(circuit_breaker=cb) # type: ignore
    result = engine.execute(req, provider=provider)
    assert isinstance(result, AgentResponse)
    assert result.content == "data"

def test_6_logger_called(caplog):
    req = AgentRequest(request_id="req6", messages=[])
    resp = AgentResponse(response_id="res6", content="data", usage={})
    provider = MockProvider("p1", response_to_return=resp)
    cb = CircuitBreaker()
    test_logger = logging.getLogger("test_logger")
    test_logger.setLevel(logging.INFO)
    engine = ExecutionEngine(circuit_breaker=cb, logger=test_logger) # type: ignore
    with caplog.at_level(logging.INFO, logger="test_logger"):
        engine.execute(req, provider=provider)
        
    assert "Executing request req6 with provider p1" in caplog.text
    assert "Request req6 succeeded" in caplog.text


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
