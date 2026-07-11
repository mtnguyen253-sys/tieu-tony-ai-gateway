import pytest
from fastapi.testclient import TestClient
from ai_gateway.api.app import create_app
from ai_gateway.protocols.cap import AgentRequest
from ai_gateway.core.orchestrator import ExecutionOrchestrator
from ai_gateway.core.executor import ExecutionEngine, RateLimitException
from ai_gateway.registry.capability import CapabilityRegistry
from ai_gateway.adapters.base import BaseProvider
from ai_gateway.core.circuit_breaker import CircuitBreaker
from ai_gateway.core.router import PolicyRouter, RoutingDecision
from ai_gateway.core.fallback import NoFallbackStrategy
import time

class MockStreamProvider(BaseProvider):
    def __init__(self, name="mock_stream", fail_before=False):
        self.name = name
        self.default_model = "mock/model"
        self.fail_before = fail_before

    @property
    def capabilities(self):
        return {"routing": True}

    def connect(self):
        return True

    def chat(self, request):
        pass

    def stream(self, request):
        if self.fail_before:
            raise RateLimitException("Stream rate limited", retry_after=10.0, model=self.default_model)
        
        def _gen():
            yield {"content": "Xin", "finish_reason": None, "usage": None, "model": self.default_model}
            yield {"content": " chào", "finish_reason": None, "usage": None, "model": self.default_model}
            yield {"content": None, "finish_reason": "stop", "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}, "model": self.default_model}
        return _gen()

    def tool_call(self, request): pass
    def health(self): return {}
    def estimate_cost(self, request): return 0.0

class MockRouter(PolicyRouter):
    def __init__(self, registry, circuit_breaker):
        super().__init__(registry, circuit_breaker)
        self.registry = registry

    def route(self, requirement, context, quotas, policy):
        return RoutingDecision(
            provider_name="mock_stream",
            provider=self.registry.get_provider("mock_stream"),
            score=100.0,
            reason="mock",
            excluded_providers={},
            policy_used="BALANCED",
            timestamp=time.time()
        )

def test_streaming_endpoint_success():
    registry = CapabilityRegistry()
    registry.register("mock_stream", MockStreamProvider())
    
    cb = CircuitBreaker()
    router = MockRouter(registry, circuit_breaker=cb)
    engine = ExecutionEngine(circuit_breaker=cb)
    orchestrator = ExecutionOrchestrator(engine=engine, router=router, fallback_strategy=NoFallbackStrategy())
    
    app = create_app(orchestrator=orchestrator, registry=registry)
    client = TestClient(app)
    
    response = client.post(
        "/chat/completions",
        json={
            "model": "mock/model",
            "messages": [{"role": "user", "content": "hi"}],
            "stream": True
        }
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
    
    text = response.text
    assert "data: " in text
    assert "Xin" in text
    assert " chào" in text
    assert "data: [DONE]" in text
    assert "prompt_tokens" in text

def test_streaming_endpoint_rate_limit_before():
    registry = CapabilityRegistry()
    registry.register("mock_stream", MockStreamProvider(fail_before=True))
    
    cb = CircuitBreaker()
    router = MockRouter(registry, circuit_breaker=cb)
    engine = ExecutionEngine(circuit_breaker=cb)
    orchestrator = ExecutionOrchestrator(engine=engine, router=router, fallback_strategy=NoFallbackStrategy())
    
    app = create_app(orchestrator=orchestrator, registry=registry)
    client = TestClient(app)
    
    response = client.post(
        "/chat/completions",
        json={
            "model": "mock/model",
            "messages": [{"role": "user", "content": "hi"}],
            "stream": True
        }
    )
    
    assert response.status_code == 429
    assert response.json()["error"]["type"] == "rate_limit"

