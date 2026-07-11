from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import os
import json
from ai_gateway.core.budget import BudgetPolicy, BudgetManager
from ai_gateway.core.router import PolicyRouter
from ai_gateway.registry.capability import CapabilityRegistry, RoutingPolicy, TaskRequirement

class MockProvider:
    def __init__(self, name, caps):
        self._name = name
        self._capabilities = caps
        self.provider_id = name
        
    @property
    def capabilities(self):
        return self._capabilities

    def health(self):
        return {"status": "ok"}

def run_smoke():
    registry = CapabilityRegistry()
    
    registry.register("expensive_model", MockProvider("expensive_model", {
        "provider": "mock",
        "model": "expensive-model",
        "codebase_reading": 10,
        "context_window": 10,
        "reasoning": 10,
        "cost": 5.0,
        "latency": 100
    }))
    
    registry.register("cheap_model", MockProvider("cheap_model", {
        "provider": "mock",
        "model": "cheap-model",
        "codebase_reading": 8,
        "context_window": 8,
        "reasoning": 8,
        "cost": 0.05,
        "latency": 200
    }))

    mode = os.getenv("AI_GATEWAY_BUDGET_MODE", "normal")
    daily_budget = os.getenv("AI_GATEWAY_DAILY_BUDGET_USD", "None")
    max_cost = os.getenv("AI_GATEWAY_MAX_COST_PER_REQUEST", "None")
    
    print(f"Budget mode: {mode}")
    print(f"Daily budget: {daily_budget}")
    print(f"Max cost per request: {max_cost}")

    policy = BudgetPolicy()
    manager = BudgetManager(policy=policy)
    
    router = PolicyRouter(registry, budget_manager=manager)

    req = TaskRequirement()

    try:
        decision = router.route(
            requirement=req,
            context={},
            quotas={},
            policy=RoutingPolicy.BALANCED
        )
        print(f"Selected provider/model: {decision.provider_name}/{decision.provider.capabilities['model']}")
        if decision.provider.capabilities['model'] == "cheap-model":
            print("Reason: cheaper model preferred")
        else:
            print("Reason: higher capability/balanced preferred")
    except Exception as e:
        print(f"Routing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_smoke()
