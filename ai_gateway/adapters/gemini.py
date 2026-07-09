import uuid
from typing import Generator, Dict, Any
from ai_gateway.adapters.base import BaseProvider
from ai_gateway.protocols.cap import AgentRequest, AgentResponse, ToolCall

class GeminiAdapter(BaseProvider):
    """
    Adapter for Google Gemini API (Mock Implementation for Phase 2).
    """

    @property
    def capabilities(self) -> Dict[str, Any]:
        return {
            "codebase_reading": 10,
            "context_window": 10,
            "reasoning": 9
        }

    def connect(self) -> bool:
        # Mock connection logic
        return True

    def chat(self, request: AgentRequest) -> AgentResponse:
        # 1. Translate CAP to Gemini payload (Mock)
        gemini_messages = []
        for msg in request.messages:
            gemini_messages.append({
                "role": "model" if msg.get("role") == "assistant" else "user",
                "parts": [{"text": msg.get("content", "")}]
            })
            
        # 2. Mock calling Gemini API
        mock_response_content = f"Mocked Gemini response for request {request.request_id}"
        
        # 3. Translate Gemini response back to CAP
        return AgentResponse(
            response_id=f"gemini_res_{uuid.uuid4().hex[:8]}",
            content=mock_response_content,
            usage={"prompt_tokens": 15, "completion_tokens": 20, "total_tokens": 35}
        )

    def stream(self, request: AgentRequest) -> Generator[AgentResponse, None, None]:
        # Mock streaming chunks
        for i in range(3):
            yield AgentResponse(
                response_id=f"gemini_stream_{uuid.uuid4().hex[:8]}",
                content=f"Chunk {i} ",
                usage={"prompt_tokens": 15, "completion_tokens": 5, "total_tokens": 20}
            )

    def tool_call(self, request: AgentRequest) -> AgentResponse:
        # Mock tool call response
        tc = ToolCall(
            id=f"call_{uuid.uuid4().hex[:8]}",
            name="mock_tool",
            arguments={"param": "value"}
        )
        return AgentResponse(
            response_id=f"gemini_tool_res_{uuid.uuid4().hex[:8]}",
            content=None,
            tool_calls=[tc],
            usage={"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30}
        )

    def health(self) -> Dict[str, Any]:
        return {"status": "ok", "provider": "gemini"}

    def estimate_cost(self, request: AgentRequest) -> float:
        # Mock cost estimation based on number of messages
        return 0.001 * len(request.messages)
