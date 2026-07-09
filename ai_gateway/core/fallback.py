import logging
from abc import ABC, abstractmethod
from typing import Callable, Dict, Any, List

from ai_gateway.protocols.cap import AgentResponse
from ai_gateway.adapters.base import BaseProvider
from ai_gateway.core.router import PolicyRouter, NoProviderAvailableException
from ai_gateway.core.executor import (
    ProviderUnavailableException,
    UnknownProviderException,
    CircuitOpenException,
    ValidationException,
    AuthenticationException,
    RateLimitException,
)

logger = logging.getLogger(__name__)

class FallbackStrategy(ABC):
    @abstractmethod
    def execute(
        self,
        operation: Callable[[BaseProvider], AgentResponse],
        # Adding kwargs to pass request context without violating the core signature requirement
        **kwargs
    ) -> AgentResponse:
        ...

class NoFallbackStrategy(FallbackStrategy):
    def execute(self, operation: Callable[[BaseProvider], AgentResponse], **kwargs) -> AgentResponse:
        # Without routing, we just pass None and let ExecutionEngine do it if modified to handle None,
        # OR we can assume operation doesn't strictly need a BaseProvider if it routes internally.
        # But to respect the signature:
        return operation(None) # type: ignore

class ProviderFallbackStrategy(FallbackStrategy):
    def __init__(self, router: PolicyRouter):
        self.router = router

    def execute(self, operation: Callable[[BaseProvider], AgentResponse], **kwargs) -> AgentResponse:
        requirement = kwargs.get("requirement")
        context = kwargs.get("context", {})
        quotas = kwargs.get("quotas")
        
        from ai_gateway.registry.capability import RoutingPolicy
        policy = kwargs.get("policy") or RoutingPolicy.BALANCED

        failed_providers: List[str] = context.get("excluded_providers", [])
        
        while True:
            context["excluded_providers"] = failed_providers
            
            try:
                decision = self.router.route(requirement, context, quotas, policy)
            except NoProviderAvailableException as e:
                logger.error(f"Fallback exhausted. No providers available: {e}")
                raise
                
            provider = decision.provider
            if not provider:
                raise UnknownProviderException(f"Provider {decision.provider_name} not found")

            try:
                return operation(provider)
            except (ProviderUnavailableException, CircuitOpenException, NoProviderAvailableException, RateLimitException) as e:
                logger.warning(f"Provider {decision.provider_name} failed with {type(e).__name__}. Triggering fallback.")
                failed_providers.append(decision.provider_name)
            except Exception as e:
                logger.error(f"Provider {decision.provider_name} failed with non-fallback exception {type(e).__name__}.")
                raise
