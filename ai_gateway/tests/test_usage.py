import os
import json
import tempfile
from ai_gateway.core.usage import UsageEvent, InMemoryUsageLedger, JsonlUsageLedger
from ai_gateway.core.cost import CostEstimator

def test_usage_event_serialization():
    event = UsageEvent(
        request_id="req1",
        timestamp=123.4,
        status="success",
        input_tokens=10,
        output_tokens=20
    )
    d = event.model_dump()
    assert d["request_id"] == "req1"
    assert d["input_tokens"] == 10
    
    event2 = UsageEvent.model_validate(d)
    assert event2.output_tokens == 20

def test_in_memory_ledger():
    ledger = InMemoryUsageLedger()
    event = UsageEvent(request_id="req1", timestamp=1.0, status="success")
    ledger.record(event)
    assert len(ledger.events) == 1
    assert ledger.events[0].request_id == "req1"

def test_jsonl_ledger():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        path = f.name
    
    try:
        ledger = JsonlUsageLedger(file_path=path)
        event = UsageEvent(request_id="req2", timestamp=2.0, status="error")
        ledger.record(event)
        
        with open(path, "r") as f:
            lines = f.readlines()
            assert len(lines) == 1
            data = json.loads(lines[0])
            assert data["request_id"] == "req2"
            assert data["status"] == "error"
    finally:
        os.remove(path)

def test_cost_estimator_basic():
    prices = {
        "prov:model": {
            "input_per_million": 1.0,
            "cached_input_per_million": 0.5,
            "output_per_million": 2.0
        }
    }
    estimator = CostEstimator(prices=prices)
    cost = estimator.estimate("prov", "model", input_tokens=1000000, output_tokens=1000000)
    assert cost == 3.0

def test_cost_estimator_with_cached():
    prices = {
        "prov:model": {
            "input_per_million": 1.0,
            "cached_input_per_million": 0.5,
            "output_per_million": 2.0
        }
    }
    estimator = CostEstimator(prices=prices)
    # 1M input (500k cached, 500k non-cached), 1M output
    cost = estimator.estimate("prov", "model", input_tokens=1000000, output_tokens=1000000, cached_input_tokens=500000)
    # non-cached input: 500k * 1.0 = 0.5
    # cached input: 500k * 0.5 = 0.25
    # output: 1M * 2.0 = 2.0
    # total = 2.75
    assert cost == 2.75

def test_cost_estimator_unknown_model():
    estimator = CostEstimator(prices={})
    cost = estimator.estimate("prov", "unknown", input_tokens=100, output_tokens=100)
    assert cost == 0.0

def test_cost_estimator_none_tokens():
    estimator = CostEstimator(prices={})
    cost = estimator.estimate("prov", "model", input_tokens=None, output_tokens=None)
    assert cost == 0.0
