import pytest
import time
from ai_gateway.core.usage import UsageEvent
from ai_gateway.core.provider_statistics import StatisticsUpdater

def test_statistics_decay_sliding_window():
    # Set window size to 3 to easily test roll out/decay
    updater = StatisticsUpdater(window_size=3)
    updater.reset()
    
    # 1. Add 3 failure events
    for i in range(3):
        updater.update(UsageEvent(
            request_id=f"fail_{i}",
            timestamp=time.time(),
            provider="decay_provider",
            status="error",
            error_type="TimeoutException",
            latency_ms=5000.0
        ))
        
    stats = updater.get_stats("decay_provider")
    assert stats.failure_count == 3
    assert stats.success_count == 0
    assert stats.timeout_count == 3
    assert stats.average_latency == 5000.0
    
    # 2. Add 1 success event. The oldest failure event should drop out.
    updater.update(UsageEvent(
        request_id="success_1",
        timestamp=time.time(),
        provider="decay_provider",
        status="success",
        latency_ms=100.0
    ))
    
    stats = updater.get_stats("decay_provider")
    assert stats.failure_count == 2
    assert stats.success_count == 1
    assert stats.timeout_count == 2
    # New average latency: (5000 + 5000 + 100) / 3 = 3366.67
    assert abs(stats.average_latency - 3366.67) < 0.1
    
    # 3. Add 2 more success events. All failures should drop out completely!
    for i in range(2):
        updater.update(UsageEvent(
            request_id=f"success_{i+2}",
            timestamp=time.time(),
            provider="decay_provider",
            status="success",
            latency_ms=100.0
        ))
        
    stats = updater.get_stats("decay_provider")
    assert stats.failure_count == 0
    assert stats.success_count == 3
    assert stats.timeout_count == 0
    assert stats.average_latency == 100.0
