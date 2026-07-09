import time
import uuid
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from .schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionChoice,
    Message as APIMessage,
    ChatCompletionUsage
)

from ai_gateway.protocols.cap import AgentRequest, AgentResponse
from ai_gateway.core.orchestrator import ExecutionOrchestrator
from ai_gateway.registry.capability import CapabilityRegistry
from ai_gateway.core.router import PolicyRouter, NoProviderAvailableException
from ai_gateway.core.circuit_breaker import CircuitBreaker
from ai_gateway.core.fallback import ProviderFallbackStrategy
from ai_gateway.core.retry import NoRetryStrategy
from ai_gateway.core.executor import ExecutionEngine


def create_app(orchestrator: Optional[ExecutionOrchestrator] = None, registry: Optional[CapabilityRegistry] = None) -> FastAPI:
    app = FastAPI(title="Tiểu Tony AI Gateway", version="0.1.0")

    # Initialize core components if not provided
    if registry is None:
        registry = CapabilityRegistry()
        # Load provider from environment if available
        import os
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_api_key:
            from ai_gateway.adapters.openrouter import OpenRouterAdapter
            openrouter_model = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
            provider = OpenRouterAdapter(api_key=openrouter_api_key, default_model=openrouter_model)
            registry.register("openrouter", provider)
    
    if orchestrator is None:
        router = PolicyRouter(registry)
        circuit_breaker = CircuitBreaker()
        retry_strategy = NoRetryStrategy()
        fallback_strategy = ProviderFallbackStrategy(router)
        executor = ExecutionEngine(circuit_breaker)

        orchestrator = ExecutionOrchestrator(
            engine=executor,
            router=router,
            retry_strategy=retry_strategy,
            fallback_strategy=fallback_strategy
        )

    @app.get("/health")
    async def health_check():
        """Returns service health."""
        return {
            "status": "ok",
            "service": "ai_gateway",
            "version": "0.1.0"
        }

    @app.get("/models")
    async def list_models():
        """Returns available models in OpenAI-compatible format."""
        providers = list(registry.all().keys()) if hasattr(registry, 'all') else []
        
        if not providers:
            return {
                "object": "list",
                "data": []
            }
            
        data = []
        if "openrouter" in providers:
            # If OpenRouter is registered, expose models
            openrouter_model = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
            data.append({
                "id": openrouter_model,
                "object": "model",
                "created": int(time.time()),
                "owned_by": "openrouter"
            })
        
        return {
            "object": "list",
            "data": data
        }

    @app.post("/chat/completions", response_model=ChatCompletionResponse)
    async def chat_completions(req: ChatCompletionRequest):
        """OpenAI-compatible chat completions endpoint."""
        
        if not req.messages:
            raise HTTPException(status_code=422, detail="Request must contain at least one message.")
            
        # Map to CAP AgentRequest
        cap_messages = [
            {"role": m.role, "content": m.content} for m in req.messages
        ]
        
        agent_req = AgentRequest(
            request_id=f"chatcmpl-{uuid.uuid4().hex}",
            messages=cap_messages,
            tools=None
        )
        
        try:
            response = orchestrator.execute(agent_req)
            
            # Map back to OpenAI Response
            content = "Success"
            prompt_tokens = 0
            completion_tokens = 0
            total_tokens = 0
            
            if response.content is not None:
                content = response.content
            if hasattr(response, 'usage') and response.usage:
                prompt_tokens = response.usage.get("prompt_tokens", 0)
                completion_tokens = response.usage.get("completion_tokens", 0)
                total_tokens = response.usage.get("total_tokens", 0)
                
            choice = ChatCompletionChoice(
                index=0,
                message=APIMessage(
                    role="assistant",
                    content=content
                ),
                finish_reason="stop"
            )
            
            return ChatCompletionResponse(
                id=response.response_id,
                created=int(time.time()),
                model=req.model,
                choices=[choice],
                usage=ChatCompletionUsage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens
                )
            )
        except NoProviderAvailableException as e:
            return JSONResponse(
                status_code=503,
                content={
                    "error": {
                        "message": str(e) or "No provider available",
                        "type": "provider_unavailable",
                        "code": "no_provider_available"
                    }
                }
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app

# Expose a default app instance for simple uvicorn running
app = create_app()
