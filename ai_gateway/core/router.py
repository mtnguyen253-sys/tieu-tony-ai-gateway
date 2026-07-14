from ai_gateway.core.health import InMemoryHealthTracker
from ai_gateway.core.budget import BudgetManager
import time
import logging
from typing import Any, Dict, Optional
from pydantic import BaseModel
from ai_gateway.registry.capability import (
    CapabilityRegistry,
    TaskRequirement,
    RoutingPolicy,
    ScoringEngine,
)
from ai_gateway.core.circuit_breaker import CircuitBreaker
from ai_gateway.core.cooldown import ProviderCooldownManager

logger = logging.getLogger(__name__)

class RoutingDecision(BaseModel):
    provider_name: str
    provider: Any
    score: float
    reason: str
    excluded_providers: Dict[str, str]
    policy_used: RoutingPolicy
    timestamp: float

class NoProviderAvailableException(Exception):
    """Raised when no provider meets the requirements or constraints."""
    pass

class PolicyRouter:
    """Routes tasks to the most suitable AI provider based on capabilities and policies."""
    
    def __init__(self, registry: CapabilityRegistry, circuit_breaker: Optional[CircuitBreaker] = None, cooldown_manager: Optional[ProviderCooldownManager] = None, budget_manager: Optional[BudgetManager] = None, health_tracker: Optional[InMemoryHealthTracker] = None):
        self.registry = registry
        self.circuit_breaker = circuit_breaker
        self.cooldown_manager = cooldown_manager
        self.budget_manager = budget_manager
        self.health_tracker = health_tracker

    def route(
        self,
        requirement: TaskRequirement,
        context: Dict[str, Any],
        quotas: Dict[str, float],
        policy: RoutingPolicy
    ) -> RoutingDecision:
        logger.info(f"Routing task: {requirement.task_type} with policy {policy.name}")
        
        candidates = self.registry.all()
        excluded_providers: Dict[str, str] = {}
        scored_providers = []

        logger.info(f"Candidate Providers: {list(candidates.keys())}")

        already_excluded = context.get("excluded_providers", [])
        for name, capability in candidates.items():
            if name in already_excluded:
                excluded_providers[name] = "Excluded by context/fallback"
                continue
            
            # Circuit breaker check
            if self.circuit_breaker and not self.circuit_breaker.is_available(name):
                excluded_providers[name] = "Circuit breaker OPEN"
                logger.info(f"Provider excluded: {name} - Reason: Circuit breaker OPEN")
                continue
                
            # Cooldown check
            requested_model = getattr(requirement, "model", None)
            if requested_model is None and isinstance(context, dict):
                requested_model = context.get("model") or context.get("model_id") or context.get("requested_model")

            if self.cooldown_manager and self.cooldown_manager.is_cooldown(name, requested_model):
                excluded_providers[name] = "Provider/Model in cooldown"
                logger.info(f"Provider excluded: {name} - Reason: Cooldown active")
                continue

            provider = self.registry.get_provider(name)
            if not provider:
                continue

            health_info = provider.health()
            is_healthy = health_info.get("status") == "ok"
            quota = quotas.get(name, 1.0)
            
            # Constraints Check
            if not ScoringEngine.constraints(capability, requirement, quota, is_healthy):
                if quota <= 0:
                    reason = "Out of quota"
                elif not is_healthy:
                    reason = "Provider unhealthy"
                elif capability.context_window < requirement.required_context:
                    reason = "Context window too small"
                elif requirement.required_tools and not capability.tool_call:
                    reason = "Tool calling not supported"
                elif capability.cost > requirement.budget:
                    reason = "Cost exceeds budget"
                elif capability.latency > requirement.latency_requirement:
                    reason = "Latency exceeds requirement"
                else:
                    reason = "Constraints not met"
                
                excluded_providers[name] = reason
                logger.info(f"Provider excluded: {name} - Reason: {reason}")
                continue
            
            # Budget & Penalty checks
            mode = "normal"
            prefer_cheaper = True
            penalty = 0.0
            
            if self.health_tracker:
                health_score = self.health_tracker.get_score(name)
                penalty += (1.0 - health_score) * 10.0

            if self.budget_manager:
                mode = self.budget_manager.policy.mode
                prefer_cheaper = self.budget_manager.policy.prefer_cheaper_models
                penalty += self.budget_manager.get_penalty(name)
                
                # We can do a rudimentary budget check if capability has a typical cost
                # For instance, if capability.cost > 0:
                if not self.budget_manager.check_budget_for_request(capability.cost):
                    excluded_providers[name] = "Budget limit exceeded"
                    logger.info(f"Provider excluded: {name} - Reason: Budget limit exceeded")
                    continue

            # Score Calculation
            task_policy = context.get("task_policy")
            score = ScoringEngine.score(capability, requirement, policy, quota, mode, prefer_cheaper, penalty, task_policy=task_policy)
            scored_providers.append((score, name, provider))
            logger.info(f"Score for {name}: {score:.4f} (penalty: {penalty:.2f})")

        if not scored_providers:
            logger.error("No provider available for routing.")
            raise NoProviderAvailableException("No provider met the constraints.")

        # Sort: Descending by score, Tie-break alphabetically by provider name
        scored_providers.sort(key=lambda x: (-x[0], x[1]))
        
        best_score, best_name, best_provider = scored_providers[0]
        logger.info(f"Selected Provider: {best_name} with score {best_score:.4f}")

        return RoutingDecision(
            provider_name=best_name,
            provider=best_provider,
            score=best_score,
            reason=f"Highest score ({best_score:.2f})",
            excluded_providers=excluded_providers,
            policy_used=policy,
            timestamp=time.time()
        )
