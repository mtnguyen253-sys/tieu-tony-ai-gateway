import os
from typing import List, Dict, Optional
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from dataclasses import dataclass, field

@dataclass
class ProviderKeyProfile:
    name: str
    api_key: str
    enabled: bool = True
    daily_request_limit: Optional[int] = None
    daily_token_limit: Optional[int] = None
    daily_cost_limit: Optional[float] = None

@dataclass
class ProviderProfile:
    name: str
    base_url: str
    model: str
    api_key: Optional[str] = None
    enabled: bool = True
    supports_streaming: bool = True
    cost_input_per_million: Optional[float] = None
    cost_cached_input_per_million: Optional[float] = None
    cost_output_per_million: Optional[float] = None
    keys: List[ProviderKeyProfile] = field(default_factory=list)


def _parse_bool(val: str, default: bool) -> bool:
    if not val:
        return default
    val = val.lower().strip()
    if val in ("true", "1", "yes", "on"):
        return True
    if val in ("false", "0", "no", "off"):
        return False
    return default

def _parse_int(val: str, default: Optional[int] = None) -> Optional[int]:
    if not val:
        return default
    try:
        return int(val)
    except ValueError:
        return default

def _parse_float(val: str, default: Optional[float] = None) -> Optional[float]:
    if not val:
        return default
    try:
        return float(val)
    except ValueError:
        return default

class Settings:
    def __init__(self):
        self.host = os.getenv("AI_GATEWAY_HOST", "127.0.0.1")
        self.port = int(os.getenv("AI_GATEWAY_PORT", "8000"))
        self.log_level = os.getenv("AI_GATEWAY_LOG_LEVEL", "info")
        self.budget_mode = os.getenv("AI_GATEWAY_BUDGET_MODE", "normal")
        
        # Provider config
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.openrouter_model = os.getenv("OPENROUTER_MODEL", "qwen/qwen3.6-plus")
        
        self.providers: List[ProviderProfile] = self._parse_providers()

    def _parse_providers(self) -> List[ProviderProfile]:
        providers = []
        
        env_vars = os.environ
        
        # Group by provider ID
        provider_data = {}
        for k, v in env_vars.items():
            if k.startswith("AI_GATEWAY_PROVIDER_"):
                parts = k.split("_")
                if len(parts) >= 5:
                    # AI_GATEWAY_PROVIDER_{ID}_{FIELD} or AI_GATEWAY_PROVIDER_{ID}_KEY_{KID}_{FIELD}
                    provider_id = parts[3]
                    if provider_id not in provider_data:
                        provider_data[provider_id] = {"keys": {}}
                    
                    if len(parts) >= 7 and parts[4] == "KEY":
                        key_id = parts[5]
                        field = "_".join(parts[6:]).lower()
                        if key_id not in provider_data[provider_id]["keys"]:
                            provider_data[provider_id]["keys"][key_id] = {}
                        provider_data[provider_id]["keys"][key_id][field] = v
                    else:
                        field = "_".join(parts[4:]).lower()
                        provider_data[provider_id][field] = v
        
        for pid, data in provider_data.items():
            name = data.get("name")
            base_url = data.get("base_url")
            model = data.get("model")
            
            if not name or not base_url or not model:
                continue
            
            api_key = data.get("api_key")
            enabled = _parse_bool(data.get("enabled", ""), True)
            supports_streaming = _parse_bool(data.get("supports_streaming", ""), True)
            
            cost_input = _parse_float(data.get("cost_input_per_million", ""))
            cost_cached_input = _parse_float(data.get("cost_cached_input_per_million", ""))
            cost_output = _parse_float(data.get("cost_output_per_million", ""))
            
            keys = []
            for kid, kdata in data.get("keys", {}).items():
                kname = kdata.get("name")
                kapi_key = kdata.get("api_key")
                if not kname or not kapi_key:
                    continue
                kenabled = _parse_bool(kdata.get("enabled", ""), True)
                req_limit = _parse_int(kdata.get("daily_request_limit", ""), None)
                tok_limit = _parse_int(kdata.get("daily_token_limit", ""), None)
                cost_limit = _parse_float(kdata.get("daily_cost_limit", ""), None)
                
                keys.append(ProviderKeyProfile(
                    name=kname,
                    api_key=kapi_key,
                    enabled=kenabled,
                    daily_request_limit=req_limit,
                    daily_token_limit=tok_limit,
                    daily_cost_limit=cost_limit
                ))
            
            providers.append(ProviderProfile(
                name=name,
                base_url=base_url,
                api_key=api_key,
                model=model,
                enabled=enabled,
                supports_streaming=supports_streaming,
                cost_input_per_million=cost_input,
                cost_cached_input_per_million=cost_cached_input,
                cost_output_per_million=cost_output,
                keys=keys
            ))
            
        return providers

settings = Settings()
