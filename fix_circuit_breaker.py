import re
with open("ai_gateway/core/circuit_breaker.py", "r") as f:
    content = f.read()

content = content.replace("probe_in_flight: bool = False\n", "")
content = re.sub(
    r"class ProviderState\(BaseModel\):\n\s*state: CircuitState = CircuitState.CLOSED\n\s*lock_until: float = 0.0\n\s*reason: str = \"\"\n",
    "class ProviderState(BaseModel):\n    state: CircuitState = CircuitState.CLOSED\n    lock_until: float = 0.0\n    reason: str = \"\"\n    probe_in_flight: bool = False\n",
    content
)

content = re.sub(
    r"        if provider_state.state == CircuitState.OPEN and self.clock.now\(\) >= provider_state.lock_until:\n\s*provider_state.state = CircuitState.CLOSED\n\s*provider_state.reason = \"Lock expired\"\n",
    "        if provider_state.state == CircuitState.OPEN and self.clock.now() >= provider_state.lock_until:\n            provider_state.state = CircuitState.HALF_OPEN\n            provider_state.reason = \"Lock expired, entering HALF_OPEN\"\n            provider_state.probe_in_flight = False\n",
    content
)

content = re.sub(
    r"    def is_available\(self, provider_name: str\) -> bool:\n\s*\"\"\"Checks if a provider is currently available to accept requests.\"\"\"\n\s*return self.get_state\(provider_name\) == CircuitState.CLOSED\n",
    "    def is_available(self, provider_name: str) -> bool:\n        \"\"\"Checks if a provider is currently available to accept requests.\"\"\"\n        state = self.get_state(provider_name)\n        if state == CircuitState.CLOSED:\n            return True\n        elif state == CircuitState.HALF_OPEN:\n            provider_state = self._states[provider_name]\n            if not provider_state.probe_in_flight:\n                provider_state.probe_in_flight = True\n                return True\n            return False\n        return False\n",
    content
)

content = re.sub(
    r"    def trip\(self, provider_name: str, duration: float = 30.0, reason: str = \"\"\) -> None:\n",
    "    def record_success(self, provider_name: str) -> None:\n        if provider_name in self._states:\n            self._states[provider_name].state = CircuitState.CLOSED\n            self._states[provider_name].probe_in_flight = False\n            self._states[provider_name].lock_until = 0.0\n\n    def record_failure(self, provider_name: str, duration: float = 30.0, reason: str = \"\") -> None:\n        self.trip(provider_name, duration, reason)\n\n    def trip(self, provider_name: str, duration: float = 30.0, reason: str = \"\") -> None:\n",
    content
)

content = re.sub(
    r"            self._states\[provider_name\].state = CircuitState.OPEN\n\s*self._states\[provider_name\].lock_until = lock_until\n\s*self._states\[provider_name\].reason = reason\n",
    "            self._states[provider_name].state = CircuitState.OPEN\n            self._states[provider_name].lock_until = lock_until\n            self._states[provider_name].reason = reason\n            self._states[provider_name].probe_in_flight = False\n",
    content
)

content = re.sub(
    r"            self._states\[provider_name\].state = CircuitState.CLOSED\n\s*self._states\[provider_name\].lock_until = 0.0\n\s*self._states\[provider_name\].reason = \"Manual reset\"\n",
    "            self._states[provider_name].state = CircuitState.CLOSED\n            self._states[provider_name].lock_until = 0.0\n            self._states[provider_name].reason = \"Manual reset\"\n            self._states[provider_name].probe_in_flight = False\n",
    content
)

with open("ai_gateway/core/circuit_breaker.py", "w") as f:
    f.write(content)
