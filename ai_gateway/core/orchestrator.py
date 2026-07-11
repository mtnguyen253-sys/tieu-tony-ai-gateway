import time
import logging
from typing import Optional, Dict, Any

from ai_gateway.protocols.cap import AgentRequest, AgentResponse
from ai_gateway.core.executor import ExecutionEngine
from ai_gateway.core.router import PolicyRouter
from ai_gateway.registry.capability import TaskRequirement, RoutingPolicy
from ai_gateway.core.retry import RetryStrategy, NoRetryStrategy
from ai_gateway.core.fallback import FallbackStrategy, NoFallbackStrategy
from ai_gateway.adapters.base import BaseProvider

class ExecutionOrchestrator:
    """Orchestrates the lifecycle of a request."""
    
    def __init__(
        self,
        engine: ExecutionEngine,
        router: PolicyRouter,
        retry_strategy: Optional[RetryStrategy] = None,
        fallback_strategy: Optional[FallbackStrategy] = None,
        logger: Optional[logging.Logger] = None
    ):
        self.engine = engine
        self.router = router
        self.retry_strategy = retry_strategy or NoRetryStrategy()
        self.fallback_strategy = fallback_strategy or NoFallbackStrategy()
        self.logger = logger or logging.getLogger(__name__)

    def execute(
        self,
        request: AgentRequest,
        requirement: Optional[TaskRequirement] = None,
        context: Optional[Dict[str, Any]] = None,
        quotas: Optional[Dict[str, float]] = None,
        policy: Optional[RoutingPolicy] = None
    ) -> AgentResponse:
        self.logger.info(f"Orchestrator started for request {request.request_id}")
        start_time = time.time()
        
        requirement = requirement or TaskRequirement()
        context = context or {}
        quotas = quotas or {}
        policy = policy or RoutingPolicy.BALANCED

        def _operation(provider: BaseProvider) -> AgentResponse:
            def _inner():
                return self.engine.execute(
                    request=request,
                    provider=provider,
                    fallback_count=len(context.get("excluded_providers", [])),
                    policy=policy.name if policy else None
                )
            return self.retry_strategy.execute(_inner)
            
        try:
            if isinstance(self.fallback_strategy, NoFallbackStrategy):
                decision = self.router.route(requirement, context, quotas, policy)
                response = _operation(decision.provider)
            else:
                response = self.fallback_strategy.execute(
                    _operation,
                    requirement=requirement,
                    context=context,
                    quotas=quotas,
                    policy=policy
                )
            execution_time = time.time() - start_time
            self.logger.info(f"Orchestrator success for request {request.request_id} in {execution_time:.4f}s")
            return response
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Orchestrator failure for request {request.request_id} in {execution_time:.4f}s. Reason: {e}")
            raise


    def execute_stream(
        self,
        request: AgentRequest,
        requirement: Optional[TaskRequirement] = None,
        context: Optional[Dict[str, Any]] = None,
        quotas: Optional[Dict[str, float]] = None,
        policy: Optional[RoutingPolicy] = None
    ):
        self.logger.info(f"Orchestrator started stream for request {request.request_id}")
        start_time = time.time()
        
        requirement = requirement or TaskRequirement()
        context = context or {}
        quotas = quotas or {}
        policy = policy or RoutingPolicy.BALANCED

        def _operation(provider: BaseProvider):
            def _inner():
                return self.engine.execute_stream(
                    request=request,
                    provider=provider,
                    fallback_count=len(context.get("excluded_providers", [])),
                    policy=policy.name if policy else None
                )
            return self.retry_strategy.execute(_inner)
            
        try:
            if isinstance(self.fallback_strategy, NoFallbackStrategy):
                decision = self.router.route(requirement, context, quotas, policy)
                return _operation(decision.provider)
            else:
                return self.fallback_strategy.execute(
                    _operation,
                    requirement=requirement,
                    context=context,
                    quotas=quotas,
                    policy=policy
                )
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Orchestrator failure for stream request {request.request_id} in {execution_time:.4f}s. Reason: {e}")
            raise
