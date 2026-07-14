from dataclasses import dataclass
from typing import Optional, Dict, List
from datetime import datetime, timezone

@dataclass
class ProviderHealthState:
    provider_name: str
    model: Optional[str] = None
    key_name: Optional[str] = None
    total_requests: int = 0
    success_count: int = 0
    error_count: int = 0
    rate_limit_count: int = 0
    timeout_count: int = 0
    auth_error_count: int = 0
    server_error_count: int = 0
    total_latency_ms: float = 0.0
    last_success_at: Optional[datetime] = None
    last_error_at: Optional[datetime] = None
    last_error_type: Optional[str] = None
    health_score: float = 1.0

class InMemoryHealthTracker:
    def __init__(self):
        # provider_name -> ProviderHealthState
        self._states: Dict[str, ProviderHealthState] = {}

    def _get_or_create(self, provider_name: str, model: Optional[str] = None, key_name: Optional[str] = None) -> ProviderHealthState:
        if provider_name not in self._states:
            self._states[provider_name] = ProviderHealthState(
                provider_name=provider_name,
                model=model,
                key_name=key_name
            )
        return self._states[provider_name]

    def _recalculate_score(self, state: ProviderHealthState):
        if state.total_requests == 0:
            state.health_score = 1.0
            return

        base_score = 1.0
        
        # Penalize low success rate
        success_rate = state.success_count / state.total_requests
        if success_rate < 0.8:
            base_score -= 0.3 * (0.8 - success_rate) / 0.8 # up to -0.3
            
        # Penalize rate limits
        rate_limit_rate = state.rate_limit_count / state.total_requests
        if rate_limit_rate > 0.1:
            base_score -= min(0.3, rate_limit_rate)
            
        # Penalize timeouts
        timeout_rate = state.timeout_count / state.total_requests
        if timeout_rate > 0.05:
            base_score -= min(0.3, timeout_rate * 2)
            
        # Penalize high average latency (>5000ms)
        if state.success_count > 0:
            avg_latency = state.total_latency_ms / state.success_count
            if avg_latency > 5000:
                base_score -= min(0.2, (avg_latency - 5000) / 10000.0)
                
        # Heavy penalty for recent auth error (e.g. within last hour)
        if state.last_error_type == "auth" and state.last_error_at:
            if (datetime.now(timezone.utc).replace(tzinfo=None) - state.last_error_at).total_seconds() < 3600:
                base_score -= 0.5
                
        # Penalize server errors
        server_error_rate = state.server_error_count / state.total_requests
        if server_error_rate > 0.05:
            base_score -= min(0.3, server_error_rate)

        state.health_score = max(0.0, min(1.0, base_score))

    def record_success(self, provider_name: str, model: Optional[str] = None, key_name: Optional[str] = None, latency_ms: float = 0.0):
        state = self._get_or_create(provider_name, model, key_name)
        state.total_requests += 1
        state.success_count += 1
        state.total_latency_ms += latency_ms
        state.last_success_at = datetime.now(timezone.utc).replace(tzinfo=None)
        self._recalculate_score(state)

    def record_error(self, provider_name: str, model: Optional[str] = None, key_name: Optional[str] = None, error_type: str = "unknown", latency_ms: float = 0.0):
        state = self._get_or_create(provider_name, model, key_name)
        state.total_requests += 1
        state.error_count += 1
        state.total_latency_ms += latency_ms
        state.last_error_at = datetime.now(timezone.utc).replace(tzinfo=None)
        state.last_error_type = error_type
        
        if error_type == "auth":
            state.auth_error_count += 1
        elif error_type == "server":
            state.server_error_count += 1
            
        self._recalculate_score(state)

    def record_rate_limit(self, provider_name: str, model: Optional[str] = None, key_name: Optional[str] = None, latency_ms: float = 0.0):
        state = self._get_or_create(provider_name, model, key_name)
        state.total_requests += 1
        state.rate_limit_count += 1
        state.total_latency_ms += latency_ms
        state.last_error_at = datetime.now(timezone.utc).replace(tzinfo=None)
        state.last_error_type = "rate_limit"
        self._recalculate_score(state)

    def record_timeout(self, provider_name: str, model: Optional[str] = None, key_name: Optional[str] = None, latency_ms: float = 0.0):
        state = self._get_or_create(provider_name, model, key_name)
        state.total_requests += 1
        state.timeout_count += 1
        state.total_latency_ms += latency_ms
        state.last_error_at = datetime.now(timezone.utc).replace(tzinfo=None)
        state.last_error_type = "timeout"
        self._recalculate_score(state)

    def get_health(self, provider_name: str, model: Optional[str] = None, key_name: Optional[str] = None) -> Optional[ProviderHealthState]:
        return self._states.get(provider_name)

    def get_score(self, provider_name: str, model: Optional[str] = None, key_name: Optional[str] = None) -> float:
        state = self._states.get(provider_name)
        if state:
            return state.health_score
        return 1.0

    def snapshot(self) -> Dict[str, ProviderHealthState]:
        return dict(self._states)
