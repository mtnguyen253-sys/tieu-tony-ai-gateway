import pytest
from ai_gateway.core.quota import InMemoryQuotaTracker

def test_quota_update_success():
    tracker = InMemoryQuotaTracker()
    tracker.record_success("provider1", "key1", input_tokens=10, output_tokens=5, cost=0.01)
    usage = tracker.get_usage("provider1", "key1")
    assert usage["request_count"] == 1
    assert usage["input_tokens"] == 10
    assert usage["output_tokens"] == 5
    assert usage["total_tokens"] == 15
    assert usage["estimated_cost"] == 0.01

def test_quota_update_rate_limit():
    tracker = InMemoryQuotaTracker()
    tracker.record_rate_limit("provider1", "key1")
    usage = tracker.get_usage("provider1", "key1")
    assert usage["rate_limit_count"] == 1
    assert usage["last_rate_limited_at"] > 0
