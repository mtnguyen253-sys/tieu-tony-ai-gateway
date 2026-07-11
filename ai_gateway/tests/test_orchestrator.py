import pytest
import logging
from ai_gateway.core.orchestrator import ExecutionOrchestrator
from ai_gateway.protocols.cap import AgentRequest, AgentResponse
from ai_gateway.core.router import RoutingDecision


class MockRouter:
    def route(self, requirement, context, quotas, policy):
        from ai_gateway.registry.capability import RoutingPolicy
        return RoutingDecision(provider_name="p1", provider="mock_prov", score=1.0, reason="", excluded_providers={}, policy_used=policy or RoutingPolicy.BALANCED, timestamp=0.0)

class MockExecutionEngine:
    def __init__(self, response=None, exception=None):
        self.response = response
        self.exception = exception

    def execute(self, request, provider=None, **kwargs):
        if self.exception:
            raise self.exception
        return self.response

def test_1_execution_success():
    req = AgentRequest(request_id="req1", messages=[])
    resp = AgentResponse(response_id="res1", content="ok", usage={})
    engine = MockExecutionEngine(response=resp)
    router = MockRouter()
    orchestrator = ExecutionOrchestrator(engine=engine, router=router) # type: ignore
    
    result = orchestrator.execute(req)
    assert result == resp

def test_2_execution_exception_raised():
    req = AgentRequest(request_id="req2", messages=[])
    engine = MockExecutionEngine(exception=ValueError("engine failed"))
    router = MockRouter()
    orchestrator = ExecutionOrchestrator(engine=engine, router=router) # type: ignore
    
    with pytest.raises(ValueError):
        orchestrator.execute(req)

def test_3_logger_called(caplog):
    req = AgentRequest(request_id="req3", messages=[])
    resp = AgentResponse(response_id="res3", content="ok", usage={})
    engine = MockExecutionEngine(response=resp)
    test_logger = logging.getLogger("orch_test_logger")
    test_logger.setLevel(logging.INFO)
    router = MockRouter()
    orchestrator = ExecutionOrchestrator(engine=engine, router=router, logger=test_logger) # type: ignore
    
    with caplog.at_level(logging.INFO, logger="orch_test_logger"):
        orchestrator.execute(req)
        
    assert "Orchestrator started for request req3" in caplog.text
    assert "Orchestrator success for request req3" in caplog.text

def test_4_agent_response_unchanged():
    req = AgentRequest(request_id="req4", messages=[])
    resp = AgentResponse(response_id="res4", content="data", usage={"tokens": 10})
    engine = MockExecutionEngine(response=resp)
    router = MockRouter()
    orchestrator = ExecutionOrchestrator(engine=engine, router=router) # type: ignore
    
    result = orchestrator.execute(req)
    assert result.content == "data"
    assert result.usage["tokens"] == 10
