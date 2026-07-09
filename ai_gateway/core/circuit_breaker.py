import time
from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel

class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class Clock:
    """Abstraction for time to allow deterministic testing."""
    def now(self) -> float:
        return time.time()

class ProviderState(BaseModel):
    state: CircuitState = CircuitState.CLOSED
    lock_until: float = 0.0
    reason: str = ""
    probe_in_flight: bool = False

class CircuitBreaker:
    """Manages the availability state of AI providers."""
    
    def __init__(self, clock: Optional[Clock] = None):
        self._states: Dict[str, ProviderState] = {}
        self.clock = clock or Clock()

    def get_state(self, provider_name: str) -> CircuitState:
        """Returns the current state of the circuit breaker for a provider."""
        if provider_name not in self._states:
            return CircuitState.CLOSED
        
        provider_state = self._states[provider_name]
        
        # Auto-reset if lock_until has expired
        if provider_state.state == CircuitState.OPEN and self.clock.now() >= provider_state.lock_until:
            provider_state.state = CircuitState.HALF_OPEN
            provider_state.reason = "Lock expired, entering HALF_OPEN"
            provider_state.probe_in_flight = False
            
        return provider_state.state

    def is_available(self, provider_name: str) -> bool:
        """Checks if a provider is currently available to accept requests."""
        state = self.get_state(provider_name)
        if state == CircuitState.CLOSED:
            return True
        elif state == CircuitState.HALF_OPEN:
            provider_state = self._states[provider_name]
            if not provider_state.probe_in_flight:
                provider_state.probe_in_flight = True
                return True
            return False
        return False

    def record_success(self, provider_name: str) -> None:
        if provider_name in self._states:
            self._states[provider_name].state = CircuitState.CLOSED
            self._states[provider_name].probe_in_flight = False
            self._states[provider_name].lock_until = 0.0
            self._states[provider_name].reason = "Success"

    def record_failure(self, provider_name: str, duration: float = 30.0, reason: str = "") -> None:
        self.trip(provider_name, duration, reason)

    def trip(self, provider_name: str, duration: float = 30.0, reason: str = "") -> None:
        """Trips the circuit breaker, marking the provider as OPEN for a duration."""
        lock_until = self.clock.now() + duration
        if provider_name not in self._states:
            self._states[provider_name] = ProviderState(
                state=CircuitState.OPEN, 
                lock_until=lock_until, 
                reason=reason
            )
        else:
            self._states[provider_name].state = CircuitState.OPEN
            self._states[provider_name].lock_until = lock_until
            self._states[provider_name].reason = reason
            self._states[provider_name].probe_in_flight = False

    def reset(self, provider_name: str) -> None:
        """Manually resets the circuit breaker, marking the provider as CLOSED."""
        if provider_name in self._states:
            self._states[provider_name].state = CircuitState.CLOSED
            self._states[provider_name].lock_until = 0.0
            self._states[provider_name].reason = "Manual reset"
            self._states[provider_name].probe_in_flight = False
