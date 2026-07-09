import pytest
from ai_gateway.core.state import StateManager, StateSnapshot

def test_state_manager_initialization():
    manager = StateManager("/tmp/workdir")
    assert manager.working_directory == "/tmp/workdir"
    assert manager.variables == {}
    assert "git_diff" in manager.current_state
    assert "files" in manager.current_state
    assert "conversation_summary" in manager.current_state

def test_update_variable():
    manager = StateManager()
    manager.update_variable("api_key", "secret123")
    assert manager.variables["api_key"] == "secret123"
    
    manager.update_variable("api_key", "new_secret")
    assert manager.variables["api_key"] == "new_secret"

def test_save_and_load_snapshot():
    manager = StateManager("/app")
    manager.update_variable("theme", "dark")
    manager.current_state["files"] = ["main.py"]
    manager.current_state["git_diff"] = "+ print('hello')"
    
    # Save the snapshot
    snapshot = manager.save_snapshot()
    assert isinstance(snapshot, StateSnapshot)
    assert snapshot.variables["theme"] == "dark"
    assert "main.py" in snapshot.current_state["files"]
    
    # Modify state after snapshot
    manager.update_variable("theme", "light")
    manager.current_state["files"] = ["main.py", "utils.py"]
    manager.current_state["git_diff"] = ""
    
    # Verify modification applied
    assert manager.variables["theme"] == "light"
    assert len(manager.current_state["files"]) == 2
    
    # Load snapshot to restore state
    manager.load_snapshot(snapshot.snapshot_id)
    
    assert manager.working_directory == "/app"
    assert manager.variables["theme"] == "dark"
    assert manager.current_state["files"] == ["main.py"]
    assert manager.current_state["git_diff"] == "+ print('hello')"

def test_load_invalid_snapshot():
    manager = StateManager()
    with pytest.raises(ValueError, match="not found"):
        manager.load_snapshot("invalid_snapshot_id")
