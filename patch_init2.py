import os
with open("ai_gateway/api/app.py", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "if registry is None:" in line:
        lines.insert(i+2, """        # Load provider from environment if available
        import os
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if openrouter_api_key:
            from ai_gateway.adapters.openrouter import OpenRouterAdapter
            openrouter_model = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
            provider = OpenRouterAdapter(api_key=openrouter_api_key, default_model=openrouter_model)
            registry.register("openrouter", provider)
""")
        break

with open("ai_gateway/api/app.py", "w") as f:
    f.writelines(lines)
