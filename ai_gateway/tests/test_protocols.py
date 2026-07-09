import json
from ai_gateway.protocols.cap import (
    ToolCall,
    ToolResult,
    AgentRequest,
    AgentResponse,
    ContextSnapshot,
)

def test_tool_call_serialization():
    tc = ToolCall(id="tc_1", name="get_weather", arguments={"location": "Hanoi"})
    assert tc.id == "tc_1"
    assert tc.name == "get_weather"
    assert tc.arguments == {"location": "Hanoi"}
    
    # Test JSON serialization/deserialization
    json_data = tc.model_dump_json()
    assert "tc_1" in json_data
    
    loaded_tc = ToolCall.model_validate_json(json_data)
    assert loaded_tc.id == tc.id
    assert loaded_tc.name == tc.name

def test_tool_result_serialization():
    tr = ToolResult(tool_call_id="tc_1", output="Sunny, 30°C")
    assert tr.tool_call_id == "tc_1"
    assert tr.output == "Sunny, 30°C"
    assert tr.is_error is False
    
    # Test error flag
    tr_error = ToolResult(tool_call_id="tc_2", output="Failed", is_error=True)
    assert tr_error.is_error is True
    
    json_data = tr.model_dump_json()
    loaded_tr = ToolResult.model_validate_json(json_data)
    assert loaded_tr.tool_call_id == tr.tool_call_id

def test_agent_request_serialization():
    req = AgentRequest(
        request_id="req_1",
        messages=[{"role": "user", "content": "Hello"}],
        tools=[{"name": "get_weather", "description": "Get weather"}]
    )
    assert req.request_id == "req_1"
    assert len(req.messages) == 1
    
    json_data = req.model_dump_json()
    loaded_req = AgentRequest.model_validate_json(json_data)
    assert loaded_req.request_id == req.request_id
    assert loaded_req.tools[0]["name"] == "get_weather"

def test_agent_response_serialization():
    tc = ToolCall(id="tc_1", name="get_weather", arguments={"location": "Hanoi"})
    res = AgentResponse(
        response_id="res_1",
        content="Here is the weather",
        tool_calls=[tc],
        usage={"prompt_tokens": 10, "completion_tokens": 5}
    )
    assert res.response_id == "res_1"
    assert len(res.tool_calls) == 1
    
    json_data = res.model_dump_json()
    loaded_res = AgentResponse.model_validate_json(json_data)
    assert loaded_res.response_id == res.response_id
    assert loaded_res.usage["prompt_tokens"] == 10

def test_context_snapshot_serialization():
    snap = ContextSnapshot(
        snapshot_id="snap_1",
        timestamp=1700000000.0,
        tokens_used=100,
        data={"key": "value"}
    )
    assert snap.snapshot_id == "snap_1"
    assert snap.tokens_used == 100
    
    json_data = snap.model_dump_json()
    loaded_snap = ContextSnapshot.model_validate_json(json_data)
    assert loaded_snap.snapshot_id == snap.snapshot_id
    assert loaded_snap.data["key"] == "value"
