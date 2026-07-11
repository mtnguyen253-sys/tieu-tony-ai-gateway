import time
import uuid
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import json
import asyncio

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
from ai_gateway.core.cooldown import ProviderCooldownManager
from ai_gateway.core.fallback import ProviderFallbackStrategy
from ai_gateway.core.retry import NoRetryStrategy
from ai_gateway.config.settings import settings
from ai_gateway.core.executor import ExecutionEngine, AuthenticationException, RateLimitException, TimeoutException


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
        cooldown_manager = ProviderCooldownManager()
        circuit_breaker = CircuitBreaker()
        router = PolicyRouter(registry, circuit_breaker=circuit_breaker, cooldown_manager=cooldown_manager)
        retry_strategy = NoRetryStrategy()
        fallback_strategy = ProviderFallbackStrategy(router)
        executor = ExecutionEngine(circuit_breaker, cooldown_manager=cooldown_manager)

        orchestrator = ExecutionOrchestrator(
            engine=executor,
            router=router,
            retry_strategy=retry_strategy,
            fallback_strategy=fallback_strategy
        )
    @app.get("/health")
    @app.get("/v1/health")
    async def health_check():
        """Returns service health."""
        return {
            "status": "ok",
            "service": "ai_gateway",
            "version": "0.1.0",
            "provider_configured": bool(settings.openrouter_api_key),
            "budget_mode": settings.budget_mode
        }
    @app.get("/models")
    @app.get("/v1/models")
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
    @app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
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
            tools=None,
            stream=req.stream
        )
        
        try:
            if req.stream:
                stream_iter = orchestrator.execute_stream(agent_req)
                
                async def generate():
                    response_id = agent_req.request_id
                    created = int(time.time())
                    model = req.model
                    
                    try:
                        for chunk in stream_iter:
                            content = chunk.get("content")
                            finish_reason = chunk.get("finish_reason")
                            usage = chunk.get("usage")
                            if chunk.get("model"):
                                model = chunk.get("model")
                            
                            delta = {}
                            if content is not None:
                                delta["content"] = content
                            elif not finish_reason:
                                delta["role"] = "assistant"
                                
                            choice_dict = {
                                "index": 0,
                                "delta": delta,
                                "finish_reason": finish_reason
                            }
                            
                            chunk_data = {
                                "id": response_id,
                                "object": "chat.completion.chunk",
                                "created": created,
                                "model": model,
                                "choices": [choice_dict]
                            }
                            
                            if usage:
                                chunk_data["usage"] = usage
                                
                            yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
                            
                        yield "data: [DONE]\n\n"
                    except Exception as e:
                        # Yield a custom error if we fail mid-stream
                        err_data = {
                            "id": response_id,
                            "object": "chat.completion.chunk",
                            "created": created,
                            "model": model,
                            "choices": [{"index": 0, "delta": {}, "finish_reason": "error"}],
                            "error": str(e)
                        }
                        yield f"data: {json.dumps(err_data, ensure_ascii=False)}\n\n"
                        yield "data: [DONE]\n\n"
                        
                return StreamingResponse(generate(), media_type="text/event-stream")

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
                model=getattr(response, 'model', None) or req.model,
                choices=[choice],
                usage=ChatCompletionUsage(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens
                )
            )
        except AuthenticationException as e:
            return JSONResponse(
                status_code=401,
                content={
                    "error": {
                        "message": str(e),
                        "type": "authentication_error",
                        "code": "invalid_api_key"
                    }
                }
            )
        except RateLimitException as e:
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "message": str(e),
                        "type": "rate_limit",
                        "code": "provider_rate_limited"
                    }
                }
            )
        except TimeoutException as e:
            return JSONResponse(
                status_code=504,
                content={
                    "error": {
                        "message": str(e),
                        "type": "timeout",
                        "code": "provider_timeout"
                    }
                }
            )
        except (NoProviderAvailableException, Exception) as e:
            # For specific Gateway routing errors, we keep it as 503
            if isinstance(e, NoProviderAvailableException) or e.__class__.__name__ == 'ProviderUnavailableException':
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
            raise HTTPException(status_code=500, detail=str(e))

    return app

# Expose a default app instance for simple uvicorn running
app = create_app()
