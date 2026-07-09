import re

with open("ai_gateway/api/app.py", "r") as f:
    content = f.read()

import_os = "import os\n"

old_init_block = """    # Initialize core components if not provided
    if registry is None:
        registry = CapabilityRegistry()
        
    if orchestrator is None:"""

new_init_block = """    import os
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
            
    if orchestrator is None:"""

if old_init_block in content:
    content = content.replace(old_init_block, new_init_block)
    with open("ai_gateway/api/app.py", "w") as f:
        f.write(content)
    print("Patched init block successfully")
else:
    print("Failed to find old block")
