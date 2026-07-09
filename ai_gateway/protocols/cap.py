from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: Dict[str, Any]


class ToolResult(BaseModel):
    tool_call_id: str
    output: str
    is_error: bool = False


class AgentRequest(BaseModel):
    request_id: str
    messages: List[Dict[str, Any]]
    tools: Optional[List[Dict[str, Any]]] = None


class AgentResponse(BaseModel):
    response_id: str
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    usage: Dict[str, Any]


class ContextSnapshot(BaseModel):
    snapshot_id: str
    timestamp: float
    tokens_used: int
    data: Dict[str, Any]
