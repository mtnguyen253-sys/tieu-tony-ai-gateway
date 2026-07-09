from fastapi import FastAPI
from ai_gateway.api.app import create_app
from ai_gateway.protocols.cap import AgentResponse

class MockOrchestrator:
    def execute(self, req):
        return AgentResponse(
            response_id="mock-123", 
            content="Hello from Mock Orchestrator! This is a simulated response.", 
            usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}
        )

app = create_app(orchestrator=MockOrchestrator())
