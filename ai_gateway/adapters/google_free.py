import uuid
from typing import Generator, Dict, Any
from ai_gateway.adapters.base import BaseProvider
from ai_gateway.protocols.cap import AgentRequest, AgentResponse, ToolCall

class GoogleFreeAdapter(BaseProvider):
    """
    Adapter for Google Free API (Mock Implementation for Phase 2).
    """

    @property
    def capabilities(self) -> Dict[str, Any]:
        return {
            "codebase_reading": 5,
            "context_window": 5,
            "reasoning": 5,
            "free_tier": True
        }

    def connect(self) -> bool:
        # Mock connection logic
        return True

    def chat(self, request: AgentRequest) -> AgentResponse:
        # 1. Translate CAP to Google Free payload (Mock)
        gf_messages = []
        for msg in request.messages:
            gf_messages.append({
                "role": "model" if msg.get("role") == "assistant" else "user",
                "parts": [{"text": msg.get("content", "")}]
            })
            
        # 2. Mock calling Google Free API
        mock_response_content = f"Mocked Google Free response for request {request.request_id}"
        
        # 3. Translate response back to CAP
        return AgentResponse(
            response_id=f"gf_res_{uuid.uuid4().hex[:8]}",
            content=mock_response_content,
            usage={"prompt_tokens": 8, "completion_tokens": 12, "total_tokens": 20}
        )

    def stream(self, request: AgentRequest) -> Generator[AgentResponse, None, None]:
        # Mock streaming chunks
        for i in range(3):
            yield AgentResponse(
                response_id=f"gf_stream_{uuid.uuid4().hex[:8]}",
                content=f"GF_Chunk {i} ",
                usage={"prompt_tokens": 8, "completion_tokens": 4, "total_tokens": 12}
            )

    def tool_call(self, request: AgentRequest) -> AgentResponse:
        # Mock tool call response
        tc = ToolCall(
            id=f"gf_call_{uuid.uuid4().hex[:8]}",
            name="mock_tool_gf",
            arguments={"param": "value_gf"}
        )
        return AgentResponse(
            response_id=f"gf_tool_res_{uuid.uuid4().hex[:8]}",
            content=None,
            tool_calls=[tc],
            usage={"prompt_tokens": 12, "completion_tokens": 8, "total_tokens": 20}
        )

    def health(self) -> Dict[str, Any]:
        return {"status": "ok", "provider": "google_free"}

    def estimate_cost(self, request: AgentRequest) -> float:
        # Google free tier has no cost
        return 0.0
