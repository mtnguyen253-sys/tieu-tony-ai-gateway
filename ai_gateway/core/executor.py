import logging
from typing import Optional, Dict, Any
from ai_gateway.protocols.cap import AgentRequest, AgentResponse
from ai_gateway.adapters.base import BaseProvider
from ai_gateway.core.quota import InMemoryQuotaTracker
from ai_gateway.core.circuit_breaker import CircuitBreaker, CircuitState
from ai_gateway.core.usage import UsageLedger
from ai_gateway.core.budget import BudgetManager
from ai_gateway.core.cost import CostEstimator
from ai_gateway.core.cooldown import ProviderCooldownManager

class RateLimitException(Exception):
    def __init__(self, message, **kwargs):
        super().__init__(message)
        self.retry_after = kwargs.get("retry_after")
        self.model = kwargs.get("model")
        self.key_name = kwargs.get("key_name")

class TimeoutException(Exception):
    def __init__(self, message, **kwargs):
        super().__init__(message)
        self.key_name = kwargs.get("key_name")

class ProviderUnavailableException(Exception):
    def __init__(self, message, **kwargs):
        super().__init__(message)
        self.key_name = kwargs.get("key_name")

class UnknownProviderException(Exception): pass
class AuthenticationException(Exception):
    def __init__(self, message, **kwargs):
        super().__init__(message)
        self.key_name = kwargs.get("key_name")

class CircuitOpenException(Exception): pass
class ValidationException(Exception): pass

class ExecutionEngine:
    def __init__(
        self, 
        circuit_breaker: CircuitBreaker, 
        usage_ledger: Optional[UsageLedger] = None, 
        budget_manager: Optional[BudgetManager] = None, 
        cost_estimator: Optional[CostEstimator] = None, 
        cooldown_manager: Optional[ProviderCooldownManager] = None, 
        quota_tracker: Optional[InMemoryQuotaTracker] = None,
        logger: Optional[logging.Logger] = None
    ):
        self.circuit_breaker = circuit_breaker
        self.usage_ledger = usage_ledger
        self.budget_manager = budget_manager
        self.cost_estimator = cost_estimator
        self.cooldown_manager = cooldown_manager
        self.quota_tracker = quota_tracker
        self.logger = logger or logging.getLogger(__name__)

    def _record_usage(self, provider_name: str, status: str, error_type=None, key_name=None, cost=0.0, input_tokens=0, output_tokens=0):
        if self.quota_tracker and key_name:
            if status == "success":
                self.quota_tracker.record_success(provider_name, key_name, input_tokens, output_tokens, cost)
            elif error_type == "RateLimitException":
                self.quota_tracker.record_rate_limit(provider_name, key_name)
            else:
                self.quota_tracker.record_error(provider_name, key_name, str(error_type))

    def execute(self, request: AgentRequest, provider: Optional[BaseProvider], **kwargs) -> AgentResponse:
        if provider is None:
            raise ValidationException("Provider cannot be None.")

        self.logger.info(f"Executing request {request.request_id} with provider {provider.name}")
        
        if not self.circuit_breaker.is_available(provider.name):
            raise CircuitOpenException(f"Circuit breaker is OPEN for {provider.name}")

        key_name = kwargs.get("key_name")
        
        try:
            response = provider.chat(request)
            
            # Record success
            self.circuit_breaker.record_success(provider.name)
            usage = getattr(response, "usage", {})
            self._record_usage(
                provider.name,
                "success", 
                key_name=key_name or response.metadata.get("key_name") if getattr(response, "metadata", None) else None,
                input_tokens=usage.get("input_tokens", 0),
                output_tokens=usage.get("output_tokens", 0),
                cost=0.0 
            )
            self.logger.info(f"Request {request.request_id} succeeded")
            return response
            
        except RateLimitException as e:
            if self.cooldown_manager:
                self.cooldown_manager.mark_cooldown(provider.name, duration=e.retry_after or 60.0, model=e.model, reason="RateLimit")
            self.circuit_breaker.record_failure(provider.name)
            self._record_usage(provider.name, "error", error_type="RateLimitException", key_name=e.key_name)
            raise
        except TimeoutException as e:
            # If we are in HALF_OPEN, a timeout is a failure that should trip the breaker again.
            if self.circuit_breaker.get_state(provider.name) == CircuitState.HALF_OPEN:
                self.circuit_breaker.record_failure(provider.name)
            self._record_usage(provider.name, "error", error_type="TimeoutException", key_name=e.key_name)
            raise
        except Exception as e:
            self.circuit_breaker.record_failure(provider.name)
            self._record_usage(provider.name, "error", error_type=type(e).__name__, key_name=key_name)
            raise

    def execute_stream(self, request: AgentRequest, provider: BaseProvider, **kwargs):
        self.logger.info(f"Executing stream request {request.request_id} with provider {provider.name}")
        return provider.stream(request)
