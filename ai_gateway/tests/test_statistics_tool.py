import os
import pytest
from unittest.mock import patch
from ai_gateway.core.usage import UsageEvent
from ai_gateway.tools.provider_statistics import load_events_from_jsonl, get_recommendation, generate_report
from ai_gateway.core.provider_statistics import ProviderStats

def test_load_events_from_jsonl(tmp_path):
    temp_file = tmp_path / "test_usage.jsonl"
    
    event1 = UsageEvent(
        request_id="req1",
        timestamp=12345.67,
        provider="tool_provider",
        status="success",
        latency_ms=150.0
    )
    event2 = UsageEvent(
        request_id="req2",
        timestamp=12345.68,
        provider="tool_provider",
        status="error",
        error_type="TimeoutException"
    )
    
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(event1.model_dump_json() + "\n")
        f.write(event2.model_dump_json() + "\n")
        
    events = load_events_from_jsonl(str(temp_file))
    assert len(events) == 2
    assert events[0].provider == "tool_provider"
    assert events[0].status == "success"
    assert events[1].status == "error"

def test_get_recommendation():
    # 1. No history
    stats = ProviderStats()
    assert get_recommendation(stats, 0) == "No History"
    
    # 2. Perfect history (success rate 100%)
    stats_perf = ProviderStats(
        success_count=10,
        failure_count=0,
        cache_hit_ratio=0.4,
        average_cost=0.01
    )
    assert get_recommendation(stats_perf, 10) == "Preferred"
    
    # 3. High success rate without perfect cache / cost flags
    stats_good = ProviderStats(
        success_count=10,
        failure_count=0,
        cache_hit_ratio=0.0,
        average_cost=1.0
    )
    assert get_recommendation(stats_good, 10) == "GOOD"
    
    # 4. Low success rate / high timeout
    stats_bad = ProviderStats(
        success_count=5,
        failure_count=5,
        timeout_count=5
    )
    assert get_recommendation(stats_bad, 10) == "Avoid temporarily"

def test_generate_report_runs_cleanly(tmp_path):
    temp_file = tmp_path / "test_report_usage.jsonl"
    
    event = UsageEvent(
        request_id="req1",
        timestamp=12345.67,
        provider="dummy_p",
        status="success",
        latency_ms=100.0,
        estimated_cost=0.02
    )
    
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(event.model_dump_json() + "\n")
        
    # Simply call and assert no exception
    try:
        generate_report(str(temp_file))
    except Exception as e:
        pytest.fail(f"generate_report failed with: {e}")
