import uuid
import httpx
from typing import Dict, Any, Optional

from ai_gateway.adapters.base import BaseProvider
from ai_gateway.protocols.cap import AgentRequest, AgentResponse
from ai_gateway.core.executor import (
    ProviderUnavailableException,
    AuthenticationException,
    RateLimitException,
    TimeoutException
)

class GenericOpenAICompatibleAdapter(BaseProvider):
    def __init__(
        self,
        name: str,
        base_url: str,
        model: str,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
        supports_streaming: bool = True,
        enabled: bool = True,
        cost_input_per_million: float = 0.0,
        cost_output_per_million: float = 0.0
    ):
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or ''
        self.default_model = model
        self.timeout = timeout
        self.custom_headers = headers or {}
        self.supports_streaming = supports_streaming
        self.enabled = enabled
        self.cost_input_per_million = cost_input_per_million
        self.cost_output_per_million = cost_output_per_million

    @property
    def capabilities(self) -> Dict[str, Any]:
        return {
            "codebase_reading": 8,
            "context_window": 8,
            "reasoning": 8,
            "routing": True,
            "cost": self.cost_input_per_million
        }

    def connect(self) -> bool:
        return self.enabled

    def _get_headers(self) -> Dict[str, str]:
        headers = self.custom_headers.copy()
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def chat(self, request: AgentRequest) -> AgentResponse:
        if not self.enabled:
            raise ProviderUnavailableException(f"Provider {self.name} is disabled")

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
        
        try:
            with httpx.Client() as client:
                resp = client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=self._get_headers(),
                    timeout=self.timeout
                )
                
                if resp.status_code in (401, 403):
                    raise AuthenticationException(f"{self.name} authentication/authorization error: {resp.status_code}")
                elif resp.status_code == 429:
                    retry_after = resp.headers.get("Retry-After")
                    try:
                        retry_after_val = float(retry_after) if retry_after else 60.0
                    except (ValueError, TypeError):
                        retry_after_val = 60.0
                    raise RateLimitException(f"{self.name} rate limit exceeded", retry_after=retry_after_val, model=self.default_model)
                elif resp.status_code >= 500:
                    raise ProviderUnavailableException(f"{self.name} returned {resp.status_code}")
                elif resp.status_code != 200:
                    raise ProviderUnavailableException(f"{self.name} returned error {resp.status_code}: {resp.text}")
                    
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                resolved_model = data.get("model") or self.default_model
                
                return AgentResponse(
                    response_id=f"gen_res_{uuid.uuid4().hex[:8]}",
                    content=content,
                    usage=usage,
                    model=resolved_model
                )
        except httpx.TimeoutException as e:
            raise TimeoutException(f"{self.name} request timed out: {e}")
        except httpx.RequestError as e:
            raise ProviderUnavailableException(f"Failed to connect to {self.name}: {e}")

    def stream(self, request: AgentRequest):
        import json
        if not self.enabled:
            raise ProviderUnavailableException(f"Provider {self.name} is disabled")
        if not self.supports_streaming:
            raise ProviderUnavailableException(f"{self.name} does not support streaming")

        or_messages = []
        for msg in request.messages:
            or_messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        payload = {
            "model": self.default_model,
            "messages": or_messages,
            "stream": True
        }
        
        try:
            client = httpx.Client()
            req = client.build_request(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            resp = client.send(req, stream=True)
            
            if resp.status_code in (401, 403):
                resp.read()
                resp.close()
                client.close()
                raise AuthenticationException(f"{self.name} authentication/authorization error: {resp.status_code}")
            elif resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After")
                try:
                    retry_after_val = float(retry_after) if retry_after else 60.0
                except (ValueError, TypeError):
                    retry_after_val = 60.0
                resp.read()
                resp.close()
                client.close()
                raise RateLimitException(f"{self.name} rate limit exceeded", retry_after=retry_after_val, model=self.default_model)
            elif resp.status_code >= 500:
                resp.read()
                resp.close()
                client.close()
                raise ProviderUnavailableException(f"{self.name} returned {resp.status_code}")
            elif resp.status_code != 200:
                err_text = resp.read().decode()
                resp.close()
                client.close()
                raise ProviderUnavailableException(f"{self.name} returned error {resp.status_code}: {err_text}")
                
            def _generator():
                try:
                    for line in resp.iter_lines():
                        if line:
                            line = line.strip()
                            if line.startswith("data: "):
                                data_str = line[6:]
                                if data_str == "[DONE]":
                                    break
                                try:
                                    chunk = json.loads(data_str)
                                    content = None
                                    finish_reason = None
                                    if chunk.get("choices") and len(chunk["choices"]) > 0:
                                        delta = chunk["choices"][0].get("delta", {})
                                        content = delta.get("content")
                                        finish_reason = chunk["choices"][0].get("finish_reason")
                                        
                                    usage = chunk.get("usage")
                                    model = chunk.get("model") or self.default_model
                                    
                                    yield {
                                        "content": content,
                                        "finish_reason": finish_reason,
                                        "usage": usage,
                                        "model": model,
                                        "raw": chunk
                                    }
                                except json.JSONDecodeError:
                                    pass
                finally:
                    resp.close()
                    client.close()
            
            return _generator()
        except httpx.TimeoutException as e:
            raise TimeoutException(f"{self.name} request timed out: {e}")
        except httpx.RequestError as e:
            raise ProviderUnavailableException(f"Failed to connect to {self.name}: {e}")

    def tool_call(self, request: AgentRequest) -> AgentResponse:
        raise NotImplementedError("Tool calls not supported yet")

    def health(self) -> Dict[str, Any]:
        return {"status": "ok" if self.enabled else "error", "provider": self.name}

    def estimate_cost(self, request: AgentRequest) -> float:
        return 0.0
