import pytest
import time
from ai_gateway.core.usage import UsageEvent
from ai_gateway.core.provider_statistics import StatisticsUpdater, ProviderStats

def test_provider_statistics_basic_success():
    updater = StatisticsUpdater(window_size=10)
    updater.reset()
    
    # 1. First event: success
    event1 = UsageEvent(
        request_id="req1",
        timestamp=time.time(),
        provider="provider_test",
        status="success",
        latency_ms=120.0,
        estimated_cost=0.01,
        input_tokens=100,
        output_tokens=200,
        cached_input_tokens=0
    )
    updater.update(event1)
    
    stats = updater.get_stats("provider_test")
    assert stats.success_count == 1
    assert stats.failure_count == 0
    assert stats.average_latency == 120.0
    assert stats.average_cost == 0.01
    assert stats.average_prompt_tokens == 100.0
    assert stats.average_completion_tokens == 200.0
    assert stats.cache_hit_ratio == 0.0

def test_provider_statistics_multiple_events():
    updater = StatisticsUpdater(window_size=10)
    updater.reset()
    
    # Success event with prompt cache
    event1 = UsageEvent(
        request_id="req1",
        timestamp=time.time(),
        provider="provider_test",
        status="success",
        latency_ms=100.0,
        estimated_cost=0.01,
        input_tokens=100,
        output_tokens=200,
        cached_input_tokens=50 # Cache hit!
    )
    
    # Timeout error event
    event2 = UsageEvent(
        request_id="req2",
        timestamp=time.time(),
        provider="provider_test",
        status="error",
        error_type="TimeoutException",
        latency_ms=5000.0,
        estimated_cost=0.0
    )
    
    # Rate limit error event
    event3 = UsageEvent(
        request_id="req3",
        timestamp=time.time(),
        provider="provider_test",
        status="error",
        error_type="RateLimitException",
        latency_ms=10.0,
        estimated_cost=0.0
    )
    
    updater.update(event1)
    updater.update(event2)
    updater.update(event3)
    
    stats = updater.get_stats("provider_test")
    assert stats.success_count == 1
    assert stats.failure_count == 2
    assert stats.timeout_count == 1
    assert stats.rate_limit_count == 1
    
    # Combined latency average: (100.0 + 5000.0 + 10.0) / 3 = 1703.333
    assert abs(stats.average_latency - 1703.33) < 0.1
    # Cache hit ratio: 1/3 = 0.3333
    assert abs(stats.cache_hit_ratio - 0.333) < 0.01

def test_statistics_reset():
    updater = StatisticsUpdater(window_size=5)
    event = UsageEvent(
        request_id="req1",
        timestamp=time.time(),
        provider="prov_reset",
        status="success"
    )
    updater.update(event)
    assert updater.get_stats("prov_reset").success_count == 1
    
    updater.reset()
    assert updater.get_stats("prov_reset").success_count == 0
