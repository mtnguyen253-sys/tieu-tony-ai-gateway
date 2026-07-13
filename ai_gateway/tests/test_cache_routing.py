import pytest
from ai_gateway.registry.capability import (
    ProviderCapability,
    TaskRequirement,
    RoutingPolicy,
    ScoringEngine,
    TaskType
)

def test_cache_aware_scoring_bonus():
    # Cache provider
    cap_cache = ProviderCapability(
        coding=8.0, 
        supports_prompt_cache=True
    )
    # Non-cache provider
    cap_no_cache = ProviderCapability(
        coding=8.0, 
        supports_prompt_cache=False
    )
    
    req = TaskRequirement(task_type=TaskType.CODING, long_context=True)
    policy = RoutingPolicy.BALANCED
    
    # Mode normal
    score_cache = ScoringEngine.score(cap_cache, req, policy, 1.0)
    score_no_cache = ScoringEngine.score(cap_no_cache, req, policy, 1.0)
    
    assert score_cache > score_no_cache
    # Bonus is 2.0, penalty is -0.5, so diff should be 2.5
    assert (score_cache - score_no_cache) == pytest.approx(2.5)

def test_no_cache_hints_no_bonus():
    cap_cache = ProviderCapability(coding=8.0, supports_prompt_cache=True)
    cap_no_cache = ProviderCapability(coding=8.0, supports_prompt_cache=False)
    
    req = TaskRequirement(task_type=TaskType.CODING, long_context=False)
    policy = RoutingPolicy.BALANCED
    
    score_cache = ScoringEngine.score(cap_cache, req, policy, 1.0)
    score_no_cache = ScoringEngine.score(cap_no_cache, req, policy, 1.0)
    
    assert score_cache == score_no_cache
