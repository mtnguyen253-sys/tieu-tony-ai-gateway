import uuid
import time
from typing import Any, Dict
from pydantic import BaseModel

class StateSnapshot(BaseModel):
    """Pydantic model representing a snapshot of the agent's state."""
    snapshot_id: str
    timestamp: float
    working_directory: str
    variables: Dict[str, Any]
    current_state: Dict[str, Any]

class StateManager:
    """Manages the internal state of the Agent in the local environment."""
    
    def __init__(self, working_directory: str = "/"):
        self.working_directory = working_directory
        self.variables: Dict[str, Any] = {}
        self.current_state: Dict[str, Any] = {
            "git_diff": "",
            "files": [],
            "conversation_summary": ""
        }
        # In-memory storage for snapshots mapped by snapshot_id
        self._snapshots: Dict[str, StateSnapshot] = {}

    def update_variable(self, key: str, value: Any) -> None:
        """Update a variable in the agent's environment."""
        self.variables[key] = value

    def save_snapshot(self) -> StateSnapshot:
        """Package the entire current state into a snapshot object."""
        snapshot_id = str(uuid.uuid4())
        snapshot = StateSnapshot(
            snapshot_id=snapshot_id,
            timestamp=time.time(),
            working_directory=self.working_directory,
            variables=self.variables.copy(),
            current_state=self.current_state.copy()
        )
        self._snapshots[snapshot_id] = snapshot
        return snapshot

    def load_snapshot(self, snapshot_id: str) -> None:
        """Restore the state from a previously saved snapshot."""
        if snapshot_id not in self._snapshots:
            raise ValueError(f"Snapshot with ID '{snapshot_id}' not found.")
        
        snapshot = self._snapshots[snapshot_id]
        self.working_directory = snapshot.working_directory
        self.variables = snapshot.variables.copy()
        self.current_state = snapshot.current_state.copy()
