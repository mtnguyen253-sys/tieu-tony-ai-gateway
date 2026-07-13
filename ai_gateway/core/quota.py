import time
from typing import Dict, Optional, Any
from dataclasses import dataclass, field

@dataclass
class QuotaState:
    request_count_today: int = 0
    input_tokens_today: int = 0
    output_tokens_today: int = 0
    total_tokens_today: int = 0
    estimated_cost_today: float = 0.0
    rate_limit_count_today: int = 0
    last_rate_limited_at: float = 0.0
    last_error: Optional[str] = None
    last_reset: float = field(default_factory=time.time)

class InMemoryQuotaTracker:
    def __init__(self):
        # provider_name -> key_name -> QuotaState
        self.state: Dict[str, Dict[str, QuotaState]] = {}
    
    def _get_state(self, provider: str, key: str) -> QuotaState:
        if provider not in self.state:
            self.state[provider] = {}
        if key not in self.state[provider]:
            self.state[provider][key] = QuotaState()
        
        # Simple reset logic based on time (e.g. naive 24h reset)
        st = self.state[provider][key]
        now = time.time()
        if now - st.last_reset > 86400: # 24 hours
            st.request_count_today = 0
            st.input_tokens_today = 0
            st.output_tokens_today = 0
            st.total_tokens_today = 0
            st.estimated_cost_today = 0.0
            st.rate_limit_count_today = 0
            st.last_reset = now
        return st

    def record_success(self, provider: str, key: str, input_tokens: int = 0, output_tokens: int = 0, cost: float = 0.0):
        st = self._get_state(provider, key)
        st.request_count_today += 1
        st.input_tokens_today += (input_tokens or 0)
        st.output_tokens_today += (output_tokens or 0)
        st.total_tokens_today += ((input_tokens or 0) + (output_tokens or 0))
        st.estimated_cost_today += (cost or 0.0)

    def record_rate_limit(self, provider: str, key: str):
        st = self._get_state(provider, key)
        st.rate_limit_count_today += 1
        st.last_rate_limited_at = time.time()

    def record_error(self, provider: str, key: str, error: str):
        st = self._get_state(provider, key)
        st.last_error = error

    def get_usage(self, provider: str, key: str) -> Dict[str, Any]:
        st = self._get_state(provider, key)
        return {
            "request_count": st.request_count_today,
            "input_tokens": st.input_tokens_today,
            "output_tokens": st.output_tokens_today,
            "total_tokens": st.total_tokens_today,
            "estimated_cost": st.estimated_cost_today,
            "rate_limit_count": st.rate_limit_count_today,
            "last_rate_limited_at": st.last_rate_limited_at,
            "last_error": st.last_error
        }
