from typing import List, Dict, Optional, Any
from ai_gateway.config.settings import ProviderKeyProfile
from ai_gateway.core.quota import InMemoryQuotaTracker
from ai_gateway.core.cooldown import ProviderCooldownManager

class KeyPool:
    def __init__(
        self,
        provider_name: str,
        keys: List[ProviderKeyProfile],
        quota_tracker: InMemoryQuotaTracker,
        cooldown_manager: Optional[ProviderCooldownManager] = None,
    ):
        self.provider_name = provider_name
        self.keys = keys
        self.quota_tracker = quota_tracker
        self.cooldown_manager = cooldown_manager

    def select_key(self) -> Optional[ProviderKeyProfile]:
        # Filter enabled keys
        available_keys = [k for k in self.keys if k.enabled]
        if not available_keys:
            return None
        
        valid_keys = []
        for key in available_keys:
            # Check cooldown per key
            if self.cooldown_manager and self.cooldown_manager.is_cooldown(self.provider_name, key.name):
                continue
                
            usage = self.quota_tracker.get_usage(self.provider_name, key.name)
            
            # Check limits
            if key.daily_request_limit is not None and usage["request_count"] >= key.daily_request_limit:
                continue
            if key.daily_token_limit is not None and usage["total_tokens"] >= key.daily_token_limit:
                continue
            if key.daily_cost_limit is not None and usage["estimated_cost"] >= key.daily_cost_limit:
                continue
                
            # If everything is fine, it's valid
            valid_keys.append((key, usage))
            
        if not valid_keys:
            return None
            
        # Select key with lowest usage (request_count, estimated_cost)
        valid_keys.sort(key=lambda x: (x[1]["request_count"], x[1]["estimated_cost"], x[0].name))
        
        return valid_keys[0][0]
