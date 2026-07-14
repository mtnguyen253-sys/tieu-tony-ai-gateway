import os
from ai_gateway.config.settings import settings

def check_config():
    print("--- Config Validation Report ---")
    
    providers = settings.providers
    enabled_providers = [p for p in providers if p.enabled]
    
    key_count = sum(len(p.keys) for p in providers)
    enabled_key_count = sum(sum(1 for k in p.keys if k.enabled) for p in providers)
    
    print(f"Provider count: {len(providers)}")
    print(f"Enabled provider count: {len(enabled_providers)}")
    print(f"Model count: {len(set(p.model for p in providers))}")
    print(f"Key count: {key_count}")
    print(f"Enabled key count: {enabled_key_count}")
    print(f"Budget mode: {settings.budget_mode}")
    
    print("\nEnabled Providers:")
    for p in enabled_providers:
        print(f"- {p.name} (Model: {p.model}, Tier: {getattr(p, 'model_tier', 'balanced')}, Streaming: {p.supports_streaming}, Cache: {p.supports_prompt_cache})")
        if getattr(p, 'max_context_tokens', None):
            print(f"  Max Context: {p.max_context_tokens}")
        if getattr(p, 'quality_score', None):
            print(f"  Quality Score: {p.quality_score}")
        
    # Validation checks
    for p in providers:
        if not p.base_url:
            print(f"[WARNING] Provider {p.name} missing base_url")
        if not p.api_key and not p.keys:
             print(f"[WARNING] Provider {p.name} missing API key/keys")
    
    print("\nConfig validation complete.")

if __name__ == "__main__":
    check_config()
