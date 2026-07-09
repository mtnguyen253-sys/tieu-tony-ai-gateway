with open("ai_gateway/api/app.py", "r") as f:
    content = f.read()

old_init = """    # Initialize core components if not provided
    if registry is None:
        registry = CapabilityRegistry()
        
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
        )"""

new_init = """    import os
    # Initialize core components if not provided
    if registry is None:
        registry = CapabilityRegistry()
        
        # Load provider from environment if available
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
        )"""

old_models = """        # Just returning a few hardcoded models for now as mocked.
        # In a real scenario, this would map capabilities to models.
        data = [
            {
                "id": "gpt-3.5-turbo",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "openai"
            },
            {
                "id": "gemini-pro",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "google"
            }
        ]"""

new_models = """        data = []
        if "openrouter" in providers:
            # If OpenRouter is registered, expose models
            openrouter_model = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
            data.append({
                "id": openrouter_model,
                "object": "model",
                "created": int(time.time()),
                "owned_by": "openrouter"
            })"""

if old_init in content:
    content = content.replace(old_init, new_init)
if old_models in content:
    content = content.replace(old_models, new_models)
    
with open("ai_gateway/api/app.py", "w") as f:
    f.write(content)
print("Patched app.py successfully")
