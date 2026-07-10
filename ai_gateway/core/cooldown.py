from typing import Dict, Optional
from pydantic import BaseModel
from ai_gateway.core.circuit_breaker import Clock
import logging

logger = logging.getLogger(__name__)

class CooldownState(BaseModel):
    lock_until: float
    reason: str = ""

class ProviderCooldownManager:
    """Manages cooldown state for providers when they hit rate limits or quotas."""
    
    def __init__(self, clock: Optional[Clock] = None):
        self._states: Dict[str, CooldownState] = {}
        self.clock = clock or Clock()

    def mark_cooldown(self, provider_name: str, duration: float = 60.0, model: Optional[str] = None, reason: str = ""):
        key = f"{provider_name}:{model}" if model else provider_name
        self._states[key] = CooldownState(lock_until=self.clock.now() + duration, reason=reason)
        logger.warning(f"Marked {key} for cooldown for {duration} seconds. Reason: {reason}")

    def is_cooldown(self, provider_name: str, model: Optional[str] = None) -> bool:
        keys_to_check = [provider_name]
        if model:
            keys_to_check.append(f"{provider_name}:{model}")
        
        now = self.clock.now()
        for key in keys_to_check:
            if key in self._states:
                if now < self._states[key].lock_until:
                    return True
                else:
                    # Auto expire
                    del self._states[key]
        return False

    def clear(self, provider_name: str, model: Optional[str] = None):
        key = f"{provider_name}:{model}" if model else provider_name
        if key in self._states:
            del self._states[key]
