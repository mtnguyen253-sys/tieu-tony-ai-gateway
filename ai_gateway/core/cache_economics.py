from typing import Optional

def estimate_effective_input_cost(
    input_tokens: int,
    expected_cache_ratio: float,
    input_cost_per_million: float,
    cache_read_cost_per_million: Optional[float] = None,
    cache_write_cost_per_million: Optional[float] = None,
) -> float:
    """
    Estimates the effective input cost for a given request, considering cache hits.
    
    Formula:
    - cached_tokens = input_tokens * expected_cache_ratio
    - uncached_tokens = input_tokens - cached_tokens
    
    If cache_read_cost is provided:
        cost = (uncached_tokens * input_cost + cached_tokens * cache_read_cost) / 1,000,000
    Else:
        cost = (input_tokens * input_cost) / 1,000,000
    """
    
    if cache_read_cost_per_million is None:
        return (input_tokens * input_cost_per_million) / 1_000_000
    
    cached_tokens = input_tokens * expected_cache_ratio
    uncached_tokens = input_tokens - cached_tokens
    
    total_cost_million = (uncached_tokens * input_cost_per_million) + (cached_tokens * cache_read_cost_per_million)
    
    return total_cost_million / 1_000_000
