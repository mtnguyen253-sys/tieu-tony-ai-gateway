import os
import uuid
import httpx
from typing import Generator, Dict, Any
from ai_gateway.adapters.base import BaseProvider
from ai_gateway.protocols.cap import AgentRequest, AgentResponse, ToolCall
from ai_gateway.core.executor import ProviderUnavailableException, AuthenticationException, RateLimitException, TimeoutException

class OpenRouterAdapter(BaseProvider):
    """
    Adapter for OpenRouter API.
    """
    def __init__(self, api_key: str, default_model: str = "openai/gpt-3.5-turbo"):
        self.api_key = api_key
        self.default_model = default_model
        self.name = "openrouter"

    @property
    def capabilities(self) -> Dict[str, Any]:
        return {
            "codebase_reading": 8,
            "context_window": 8,
            "reasoning": 8,
            "routing": True
        }

    def connect(self) -> bool:
        return True

    def chat(self, request: AgentRequest) -> AgentResponse:
        or_messages = []
        for msg in request.messages:
            or_messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
            
        payload = {
            "model": self.default_model,
            "messages": or_messages
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "Tieu Tony AI Gateway"
        }
        
        try:
            with httpx.Client() as client:
                resp = client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                if resp.status_code in (401, 403):
                    raise AuthenticationException(f"OpenRouter authentication/authorization error: {resp.status_code}")
                elif resp.status_code == 429:
                    retry_after = resp.headers.get("Retry-After")
                    try:
                        retry_after_val = float(retry_after) if retry_after else 60.0
                    except (ValueError, TypeError):
                        retry_after_val = 60.0
                    raise RateLimitException(f"OpenRouter rate limit exceeded", retry_after=retry_after_val, model=self.default_model)
                elif resp.status_code >= 500:
                    raise ProviderUnavailableException(f"OpenRouter returned {resp.status_code}")
                elif resp.status_code != 200:
                    raise ProviderUnavailableException(f"OpenRouter returned error {resp.status_code}: {resp.text}")
                    
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                resolved_model = data.get("model") or self.default_model
                
                return AgentResponse(
                    response_id=f"or_res_{uuid.uuid4().hex[:8]}",
                    content=content,
                    usage=usage,
                    model=resolved_model
                )
        except httpx.TimeoutException as e:
            raise TimeoutException(f"OpenRouter request timed out: {e}")
        except httpx.RequestError as e:
            raise ProviderUnavailableException(f"Failed to connect to OpenRouter: {e}")

    def stream(self, request: AgentRequest) -> Generator[AgentResponse, None, None]:
        raise NotImplementedError("Streaming not supported yet")

    def tool_call(self, request: AgentRequest) -> AgentResponse:
        raise NotImplementedError("Tool calls not supported yet")

    def health(self) -> Dict[str, Any]:
        return {"status": "ok", "provider": "openrouter"}

    def estimate_cost(self, request: AgentRequest) -> float:
        return 0.0
