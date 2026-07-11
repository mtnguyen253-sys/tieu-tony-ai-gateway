import logging
import os
from typing import Dict, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

def _get_float_env(key: str, default: Optional[float] = None) -> Optional[float]:
    val = os.getenv(key)
    if val is not None:
        try:
            return float(val)
        except ValueError:
            pass
    return default

class BudgetPolicy(BaseModel):
    daily_budget_usd: Optional[float] = Field(default_factory=lambda: _get_float_env("AI_GATEWAY_DAILY_BUDGET_USD"))
    monthly_budget_usd: Optional[float] = Field(default_factory=lambda: _get_float_env("AI_GATEWAY_MONTHLY_BUDGET_USD"))
    mode: str = Field(default_factory=lambda: os.getenv("AI_GATEWAY_BUDGET_MODE", "normal"))
    prefer_cheaper_models: bool = True
    max_estimated_cost_per_request: Optional[float] = Field(default_factory=lambda: _get_float_env("AI_GATEWAY_MAX_COST_PER_REQUEST"))

class BudgetManager:
    """
    Tracks budget and provider reliability metrics (error rates, rate limits)
    to inform routing decisions.
    """
    def __init__(self, policy: Optional[BudgetPolicy] = None):
        self.policy = policy or BudgetPolicy()
        self.current_daily_spend = 0.0
        self.current_monthly_spend = 0.0
        
        # Track metrics for penalties and stats
        self.provider_errors: Dict[str, int] = {}
        self.provider_rate_limits: Dict[str, int] = {}
        self.provider_successes: Dict[str, int] = {}
        self.provider_requests: Dict[str, int] = {}
        self.provider_cost: Dict[str, float] = {}
        self.provider_latency_sum: Dict[str, float] = {}
        self.provider_input_tokens_sum: Dict[str, int] = {}
        self.provider_output_tokens_sum: Dict[str, int] = {}
        
    def record_spend(self, provider_name: str, amount_usd: float) -> None:
        self.current_daily_spend += amount_usd
        self.current_monthly_spend += amount_usd
        self.provider_cost[provider_name] = self.provider_cost.get(provider_name, 0.0) + amount_usd
        
        if self.policy.daily_budget_usd and self.current_daily_spend > self.policy.daily_budget_usd * 0.8:
            logger.warning(f"[BUDGET WARNING] Daily spend {self.current_daily_spend:.4f} exceeds 80% of budget {self.policy.daily_budget_usd:.4f}")
            
        if self.policy.monthly_budget_usd and self.current_monthly_spend > self.policy.monthly_budget_usd * 0.8:
            logger.warning(f"[BUDGET WARNING] Monthly spend {self.current_monthly_spend:.4f} exceeds 80% of budget {self.policy.monthly_budget_usd:.4f}")
            
        total_cost = sum(self.provider_cost.values())
        if total_cost > 0 and self.provider_cost[provider_name] / total_cost > 0.7:
            logger.warning(f"[BUDGET WARNING] Provider {provider_name} accounts for >70% of total cost ({self.provider_cost[provider_name]:.4f}/{total_cost:.4f})")
        
    def record_error(self, provider_name: str) -> None:
        self.provider_requests[provider_name] = self.provider_requests.get(provider_name, 0) + 1
        self.provider_errors[provider_name] = self.provider_errors.get(provider_name, 0) + 1
        
    def record_rate_limit(self, provider_name: str) -> None:
        self.provider_requests[provider_name] = self.provider_requests.get(provider_name, 0) + 1
        self.provider_rate_limits[provider_name] = self.provider_rate_limits.get(provider_name, 0) + 1
        
        reqs = self.provider_requests[provider_name]
        rls = self.provider_rate_limits[provider_name]
        if reqs >= 5 and rls / reqs > 0.3:
            logger.warning(f"[BUDGET WARNING] Provider {provider_name} has high rate limit rate ({rls}/{reqs})")
        
    def record_success(self, provider_name: str, latency_ms: Optional[float] = None, input_tokens: Optional[int] = None, output_tokens: Optional[int] = None) -> None:
        self.provider_requests[provider_name] = self.provider_requests.get(provider_name, 0) + 1
        self.provider_successes[provider_name] = self.provider_successes.get(provider_name, 0) + 1
        
        if latency_ms is not None:
            self.provider_latency_sum[provider_name] = self.provider_latency_sum.get(provider_name, 0.0) + latency_ms
        if input_tokens is not None:
            self.provider_input_tokens_sum[provider_name] = self.provider_input_tokens_sum.get(provider_name, 0) + input_tokens
        if output_tokens is not None:
            self.provider_output_tokens_sum[provider_name] = self.provider_output_tokens_sum.get(provider_name, 0) + output_tokens
        
    def get_penalty(self, provider_name: str) -> float:
        """
        Calculate a score penalty based on error rates and rate limit history.
        Returns a value between 0.0 (no penalty) and e.g., 5.0 (high penalty).
        """
        errors = self.provider_errors.get(provider_name, 0)
        rate_limits = self.provider_rate_limits.get(provider_name, 0)
        successes = self.provider_successes.get(provider_name, 0)
        
        total = errors + rate_limits + successes
        if total < 3:
            # Not enough data for meaningful penalty
            return 0.0
            
        error_rate = errors / total
        rate_limit_rate = rate_limits / total
        
        # 10% error rate = 1.0 penalty, up to max 5.0
        error_penalty = min(5.0, error_rate * 10.0)
        
        # Rate limits penalize slightly less
        rate_limit_penalty = min(3.0, rate_limit_rate * 5.0)
        
        return error_penalty + rate_limit_penalty
        
    def check_budget_for_request(self, estimated_cost: float) -> bool:
        """
        Check if request exceeds max per-request limit or daily budget.
        Logs warning if exceeded.
        Returns True if ALLOWED, False if REJECTED.
        """
        # Check daily budget
        if self.policy.daily_budget_usd is not None:
            if self.current_daily_spend + estimated_cost > self.policy.daily_budget_usd:
                logger.warning(
                    f"[BUDGET WARNING] Estimated spend {self.current_daily_spend + estimated_cost:.4f} "
                    f"exceeds daily budget {self.policy.daily_budget_usd:.4f}"
                )
                if self.policy.mode in ("economy", "emergency"):
                    return False
                    
        # Check max cost per request
        if self.policy.max_estimated_cost_per_request is not None:
            if estimated_cost > self.policy.max_estimated_cost_per_request:
                logger.warning(
                    f"[BUDGET WARNING] Request estimated cost {estimated_cost:.4f} "
                    f"exceeds max per-request limit {self.policy.max_estimated_cost_per_request:.4f}"
                )
                return False
                
        return True
