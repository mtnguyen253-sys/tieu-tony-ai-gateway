import time
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from ai_gateway.core.usage import UsageEvent

logger = logging.getLogger(__name__)

class ProviderStats(BaseModel):
    success_count: int = 0
    failure_count: int = 0
    rate_limit_count: int = 0
    timeout_count: int = 0
    auth_error_count: int = 0
    average_latency: float = 0.0
    average_cost: float = 0.0
    average_prompt_tokens: float = 0.0
    average_completion_tokens: float = 0.0
    cache_hit_ratio: float = 0.0
    rolling_score: float = 0.0
    last_update: float = 0.0

class StatisticsUpdater:
    def __init__(self, window_size: int = 50):
        self.window_size = window_size
        self._provider_history: Dict[str, List[UsageEvent]] = {}
        self._provider_stats: Dict[str, ProviderStats] = {}

    def get_stats(self, provider: str) -> ProviderStats:
        if provider not in self._provider_stats:
            self._provider_stats[provider] = ProviderStats()
        return self._provider_stats[provider]

    def reset(self) -> None:
        self._provider_history.clear()
        self._provider_stats.clear()

    def update(self, event: UsageEvent) -> None:
        provider = event.provider
        if not provider:
            return

        if provider not in self._provider_history:
            self._provider_history[provider] = []

        # Decaying/Rolling behavior: append new event and maintain the window
        self._provider_history[provider].append(event)
        if len(self._provider_history[provider]) > self.window_size:
            self._provider_history[provider].pop(0)

        history = self._provider_history[provider]
        total_count = len(history)

        success_count = sum(1 for e in history if e.status == "success")
        failure_count = sum(1 for e in history if e.status == "error")
        rate_limit_count = sum(1 for e in history if e.status == "error" and e.error_type == "RateLimitException")
        timeout_count = sum(1 for e in history if e.status == "error" and e.error_type == "TimeoutException")
        auth_error_count = sum(1 for e in history if e.status == "error" and e.error_type == "AuthenticationException")

        latencies = [e.latency_ms for e in history if e.latency_ms is not None]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0

        costs = [e.estimated_cost for e in history if e.estimated_cost is not None]
        avg_cost = sum(costs) / len(costs) if costs else 0.0

        prompt_tokens = [e.input_tokens for e in history if e.input_tokens is not None]
        avg_prompt_tokens = sum(prompt_tokens) / len(prompt_tokens) if prompt_tokens else 0.0

        completion_tokens = [e.output_tokens for e in history if e.output_tokens is not None]
        avg_completion_tokens = sum(completion_tokens) / len(completion_tokens) if completion_tokens else 0.0

        cache_hits = sum(1 for e in history if e.cached_input_tokens is not None and e.cached_input_tokens > 0)
        cache_hit_ratio = cache_hits / total_count if total_count > 0 else 0.0

        stats = self.get_stats(provider)
        stats.success_count = success_count
        stats.failure_count = failure_count
        stats.rate_limit_count = rate_limit_count
        stats.timeout_count = timeout_count
        stats.auth_error_count = auth_error_count
        stats.average_latency = avg_latency
        stats.average_cost = avg_cost
        stats.average_prompt_tokens = avg_prompt_tokens
        stats.average_completion_tokens = avg_completion_tokens
        stats.cache_hit_ratio = cache_hit_ratio
        stats.last_update = time.time()

        # Calculate in-memory rolling_score
        stats.rolling_score = self.calculate_rolling_score(stats)

    def calculate_rolling_score(self, stats: ProviderStats) -> float:
        score = 0.0
        total = stats.success_count + stats.failure_count
        if total == 0:
            return 0.0

        success_rate = stats.success_count / total
        timeout_rate = stats.timeout_count / total
        rate_limit_rate = stats.rate_limit_count / total

        # Load config dynamically if possible, else default
        try:
            from ai_gateway.config.settings import settings
            cfg = settings
        except Exception:
            cfg = None

        success_bonus = getattr(cfg, "historical_success_bonus", 2.0)
        failure_penalty = getattr(cfg, "historical_failure_penalty", -3.0)
        rate_limit_penalty = getattr(cfg, "historical_rate_limit_penalty", -2.0)
        cache_bonus = getattr(cfg, "historical_cache_bonus", 2.0)
        latency_bonus = getattr(cfg, "historical_latency_bonus", 1.0)
        cost_bonus = getattr(cfg, "historical_cost_bonus", 1.0)

        if success_rate >= 0.98:
            score += success_bonus
        if timeout_rate > 0.10:
            score += failure_penalty
        if rate_limit_rate > 0.10 or stats.rate_limit_count > 2:
            score += rate_limit_penalty
        if stats.cache_hit_ratio > 0.30:
            score += cache_bonus
        if stats.average_latency > 0 and stats.average_latency < 1500:
            score += latency_bonus
        if stats.average_cost > 0 and stats.average_cost < 0.5:
            score += cost_bonus

        return score

_global_statistics_updater = None

def get_global_statistics_updater() -> StatisticsUpdater:
    global _global_statistics_updater
    if _global_statistics_updater is None:
        _global_statistics_updater = StatisticsUpdater()
    return _global_statistics_updater
