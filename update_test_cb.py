import re
with open("ai_gateway/tests/test_circuit_breaker.py", "r") as f:
    content = f.read()

# Replace test_3_fake_clock_advance
content = re.sub(
    r"def test_3_fake_clock_advance\(\):.*?(?=def test_4)",
    """def test_3_fake_clock_advance():
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

""", content, flags=re.DOTALL
)

with open("ai_gateway/tests/test_circuit_breaker.py", "w") as f:
    f.write(content)
