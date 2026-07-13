import pytest
from ai_gateway.core.cache_economics import estimate_effective_input_cost

def test_estimate_effective_input_cost_no_cache():
    # input_tokens=1000, ratio=0, input_cost=10, read_cost=5 (ignored)
    # uncached = 1000, cached = 0
    # cost = (1000 * 10) / 1,000,000 = 0.01
    cost = estimate_effective_input_cost(1000, 0.0, 10.0, 5.0)
    assert cost == 0.01

def test_estimate_effective_input_cost_with_cache():
    # input_tokens=1000, ratio=0.5, input_cost=10, read_cost=2
    # uncached = 500, cached = 500
    # cost = (500 * 10 + 500 * 2) / 1,000,000 = (5000 + 1000) / 1,000,000 = 6000 / 1,000,000 = 0.006
    cost = estimate_effective_input_cost(1000, 0.5, 10.0, 2.0)
    assert cost == 0.006

def test_estimate_effective_input_cost_no_read_cost():
    # input_tokens=1000, ratio=0.5, input_cost=10, read_cost=None
    # cost = (1000 * 10) / 1,000,000 = 0.01
    cost = estimate_effective_input_cost(1000, 0.5, 10.0, None)
    assert cost == 0.01
