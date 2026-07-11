import pytest
from ai_gateway.core.budget import BudgetPolicy, BudgetManager

def test_budget_manager_penalties():
    mgr = BudgetManager()
    
    # Not enough data
    assert mgr.get_penalty("prov1") == 0.0
    
    # Successes don't add penalty, but provide data volume
    mgr.record_success("prov1")
    mgr.record_success("prov1")
    mgr.record_success("prov1")
    
    assert mgr.get_penalty("prov1") == 0.0
    
    # 1 error out of 4 (25% error rate) -> 2.5 penalty
    mgr.record_error("prov1")
    penalty = mgr.get_penalty("prov1")
    assert penalty == 2.5
    
    # Rate limit -> rate limit penalty
    mgr.record_rate_limit("prov1")
    # Now 1 error, 1 rate limit, 3 success = 5 total
    # Error rate: 1/5 = 20% -> 2.0 penalty
    # Rate limit rate: 1/5 = 20% -> 1.0 penalty
    # Total = 3.0
    penalty = mgr.get_penalty("prov1")
    assert penalty == 3.0

def test_budget_manager_budget_checks():
    policy = BudgetPolicy(
        daily_budget_usd=1.0,
        max_estimated_cost_per_request=0.5,
        mode="economy"
    )
    mgr = BudgetManager(policy)
    
    assert mgr.check_budget_for_request(0.1) == True
    
    # Exceeds max per request
    assert mgr.check_budget_for_request(0.6) == False
    
    mgr.record_spend("prov1", 0.9)
    # Exceeds daily budget (economy mode rejects)
    assert mgr.check_budget_for_request(0.2) == False
    
    # In normal mode, it should just warn but allow (returns True)
    policy.mode = "normal"
    assert mgr.check_budget_for_request(0.2) == True
    
    # In emergency mode, max_estimated_cost_per_request still applies
    policy.mode = "emergency"
    assert mgr.check_budget_for_request(10.0) == False

def test_budget_policy_env_loading(monkeypatch):
    monkeypatch.setenv("AI_GATEWAY_BUDGET_MODE", "economy")
    monkeypatch.setenv("AI_GATEWAY_DAILY_BUDGET_USD", "2.5")
    monkeypatch.setenv("AI_GATEWAY_MONTHLY_BUDGET_USD", "30")
    monkeypatch.setenv("AI_GATEWAY_MAX_COST_PER_REQUEST", "0.1")
    
    policy = BudgetPolicy()
    assert policy.mode == "economy"
    assert policy.daily_budget_usd == 2.5
    assert policy.monthly_budget_usd == 30.0
    assert policy.max_estimated_cost_per_request == 0.1

def test_budget_policy_invalid_env(monkeypatch):
    monkeypatch.setenv("AI_GATEWAY_DAILY_BUDGET_USD", "invalid_number")
    # Should not crash, should just default to None
    policy = BudgetPolicy()
    assert policy.daily_budget_usd is None
