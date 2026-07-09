import pytest
from ai_gateway.core.circuit_breaker import CircuitBreaker, CircuitState, Clock
from ai_gateway.core.router import PolicyRouter, NoProviderAvailableException
from ai_gateway.registry.capability import CapabilityRegistry, TaskRequirement, RoutingPolicy, TaskType
from ai_gateway.adapters.base import BaseProvider
from ai_gateway.protocols.cap import AgentRequest, AgentResponse
from typing import Dict, Any, Generator

class FakeClock(Clock):
    def __init__(self, initial_time: float = 0.0):
        self.current_time = initial_time

    def now(self) -> float:
        return self.current_time

    def advance(self, seconds: float):
        self.current_time += seconds

def test_1_default_available():
    cb = CircuitBreaker()
    assert cb.is_available("gemini") is True
    assert cb.get_state("gemini") == CircuitState.CLOSED

def test_2_trip_unavailable():
    cb = CircuitBreaker()
    cb.trip("gemini", reason="429 Too Many Requests")
    assert cb.is_available("gemini") is False
    assert cb.get_state("gemini") == CircuitState.OPEN

def test_3_fake_clock_advance():
    clock = FakeClock()
    cb = CircuitBreaker(clock=clock)
    
    cb.trip("gemini", duration=30.0)
    assert cb.is_available("gemini") is False
    assert cb.get_state("gemini") == CircuitState.OPEN
    
    # Hết lock_until -> HALF_OPEN -> probe được phép
    clock.advance(31.0)
    # get_state triggers the transition
    assert cb.get_state("gemini") == CircuitState.HALF_OPEN
    
    # HALF_OPEN chỉ cho 1 probe
    assert cb.is_available("gemini") is True # First probe allowed
    assert cb.is_available("gemini") is False # Second probe denied
    assert cb.get_state("gemini") == CircuitState.HALF_OPEN

def test_half_open_success():
    clock = FakeClock()
    cb = CircuitBreaker(clock=clock)
    cb.trip("gemini", duration=30.0)
    clock.advance(31.0)
    
    assert cb.is_available("gemini") is True # Probe
    
    # record_success -> CLOSED
    cb.record_success("gemini")
    assert cb.get_state("gemini") == CircuitState.CLOSED
    assert cb.is_available("gemini") is True

def test_half_open_failure():
    clock = FakeClock()
    cb = CircuitBreaker(clock=clock)
    cb.trip("gemini", duration=30.0)
    clock.advance(31.0)
    
    assert cb.is_available("gemini") is True # Probe
    
    # record_failure -> OPEN
    cb.record_failure("gemini", duration=30.0)
    assert cb.get_state("gemini") == CircuitState.OPEN
    assert cb.is_available("gemini") is False

def test_4_reset():
    cb = CircuitBreaker()
    cb.trip("gemini")
    assert cb.is_available("gemini") is False
    
    cb.reset("gemini")
    assert cb.is_available("gemini") is True
    assert cb.get_state("gemini") == CircuitState.CLOSED

def test_5_unknown_provider_no_crash():
    cb = CircuitBreaker()
    cb.reset("unknown_provider")
    assert cb.is_available("unknown_provider") is True

class MockProvider(BaseProvider):
    def __init__(self, name: str, caps: Dict[str, Any], healthy: bool = True):
        self.name = name
        self._caps = caps
        self._healthy = healthy
        
    @property
    def capabilities(self) -> Dict[str, Any]:
        return self._caps

    def connect(self) -> bool: return True
    def chat(self, request: AgentRequest) -> AgentResponse: pass # type: ignore
    def stream(self, request: AgentRequest) -> Generator[AgentResponse, None, None]: pass # type: ignore
    def tool_call(self, request: AgentRequest) -> AgentResponse: pass # type: ignore
    def health(self) -> Dict[str, Any]: return {"status": "ok" if self._healthy else "error"}
    def estimate_cost(self, request: AgentRequest) -> float: return 0.0

@pytest.fixture
def registry_with_providers() -> CapabilityRegistry:
    reg = CapabilityRegistry()
    reg.register("p1", MockProvider("p1", {"coding": 10}))
    reg.register("p2", MockProvider("p2", {"coding": 10}))
    reg.register("p3", MockProvider("p3", {"coding": 10}))
    return reg

def test_6_router_excludes_open_provider(registry_with_providers: CapabilityRegistry):
    cb = CircuitBreaker()
    router = PolicyRouter(registry_with_providers, circuit_breaker=cb)
    
    cb.trip("p1") # Trip p1
    
    req = TaskRequirement(task_type=TaskType.CODING)
    decision = router.route(req, {}, {"p1": 10.0, "p2": 10.0, "p3": 10.0}, RoutingPolicy.BALANCED)
    
    assert "p1" in decision.excluded_providers
    assert decision.excluded_providers["p1"] == "Circuit breaker OPEN"
    assert decision.provider_name in ["p2", "p3"]

def test_7_two_open_router_chooses_remaining(registry_with_providers: CapabilityRegistry):
    cb = CircuitBreaker()
    router = PolicyRouter(registry_with_providers, circuit_breaker=cb)
    
    cb.trip("p1")
    cb.trip("p2")
    
    req = TaskRequirement(task_type=TaskType.CODING)
    decision = router.route(req, {}, {"p1": 10.0, "p2": 10.0, "p3": 10.0}, RoutingPolicy.BALANCED)
    
    assert "p1" in decision.excluded_providers
    assert "p2" in decision.excluded_providers
    assert decision.provider_name == "p3"

def test_8_all_open_no_provider(registry_with_providers: CapabilityRegistry):
    cb = CircuitBreaker()
    router = PolicyRouter(registry_with_providers, circuit_breaker=cb)
    
    cb.trip("p1")
    cb.trip("p2")
    cb.trip("p3")
    
    req = TaskRequirement(task_type=TaskType.CODING)
    
    with pytest.raises(NoProviderAvailableException):
        router.route(req, {}, {"p1": 10.0, "p2": 10.0, "p3": 10.0}, RoutingPolicy.BALANCED)
