import pytest
import time
from datetime import datetime, timedelta
from ai_gateway.core.health import InMemoryHealthTracker, ProviderHealthState
from ai_gateway.core.executor import ExecutionEngine, RateLimitException, TimeoutException
from ai_gateway.core.circuit_breaker import CircuitBreaker
from unittest.mock import MagicMock

def test_health_tracker_success():
    tracker = InMemoryHealthTracker()
    tracker.record_success("prov1", latency_ms=150.0)
    
    state = tracker.get_health("prov1")
    assert state is not None
    assert state.success_count == 1
    assert state.total_requests == 1
    assert state.health_score == 1.0

def test_health_tracker_rate_limit_penalty():
    tracker = InMemoryHealthTracker()
    for _ in range(8):
        tracker.record_success("prov1", latency_ms=100.0)
    for _ in range(2):
        tracker.record_rate_limit("prov1", latency_ms=50.0)
        
    score = tracker.get_score("prov1")
    assert score < 1.0
    
def test_health_tracker_timeout_penalty():
    tracker = InMemoryHealthTracker()
    for _ in range(9):
        tracker.record_success("prov1", latency_ms=100.0)
    tracker.record_timeout("prov1", latency_ms=5000.0)
        
    score = tracker.get_score("prov1")
    assert score < 1.0

def test_health_tracker_auth_error_heavy_penalty():
    tracker = InMemoryHealthTracker()
    tracker.record_success("prov1", latency_ms=100.0)
    tracker.record_error("prov1", error_type="auth", latency_ms=50.0)
        
    score = tracker.get_score("prov1")
    assert score <= 0.5  # Heavy penalty for recent auth error

def test_health_tracker_latency_penalty():
    tracker = InMemoryHealthTracker()
    tracker.record_success("prov1", latency_ms=8000.0)  # > 5000ms
        
    score = tracker.get_score("prov1")
    assert score < 1.0

def test_health_tracker_unseen_provider():
    tracker = InMemoryHealthTracker()
    assert tracker.get_score("prov_unseen") == 1.0

def test_executor_records_success_health():
    cb = CircuitBreaker()
    tracker = InMemoryHealthTracker()
    engine = ExecutionEngine(circuit_breaker=cb, health_tracker=tracker)
    
    mock_provider = MagicMock()
    mock_provider.name = "mock_prov"
    mock_response = MagicMock()
    mock_response.usage = {}
    mock_response.metadata = {}
    mock_provider.chat.return_value = mock_response
    
    mock_request = MagicMock()
    mock_request.request_id = "1"
    mock_request.model = "test-model"
    
    engine.execute(mock_request, mock_provider, key_name="key1")
    assert tracker.get_health("mock_prov").success_count == 1

def test_executor_records_rate_limit_health():
    cb = CircuitBreaker()
    tracker = InMemoryHealthTracker()
    engine = ExecutionEngine(circuit_breaker=cb, health_tracker=tracker)
    
    mock_provider = MagicMock()
    mock_provider.name = "mock_prov"
    
    mock_request = MagicMock()
    mock_request.request_id = "1"
    mock_request.model = "test-model"
    
    mock_provider.chat.side_effect = RateLimitException("rate limited")
    try:
        engine.execute(mock_request, mock_provider, key_name="key1")
    except RateLimitException:
        pass
    assert tracker.get_health("mock_prov").rate_limit_count == 1

def test_executor_records_timeout_health():
    cb = CircuitBreaker()
    tracker = InMemoryHealthTracker()
    engine = ExecutionEngine(circuit_breaker=cb, health_tracker=tracker)
    
    mock_provider = MagicMock()
    mock_provider.name = "mock_prov"
    
    mock_request = MagicMock()
    mock_request.request_id = "1"
    mock_request.model = "test-model"
    
    mock_provider.chat.side_effect = TimeoutException("timeout")
    try:
        engine.execute(mock_request, mock_provider, key_name="key1")
    except TimeoutException:
        pass
    assert tracker.get_health("mock_prov").timeout_count == 1

