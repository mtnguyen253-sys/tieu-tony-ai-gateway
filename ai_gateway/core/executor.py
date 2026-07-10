import time
import logging
from typing import Dict, Any, Optional

from ai_gateway.protocols.cap import AgentRequest, AgentResponse
from ai_gateway.core.circuit_breaker import CircuitBreaker
from ai_gateway.core.cooldown import ProviderCooldownManager

class RateLimitException(Exception):
    def __init__(self, message: str, retry_after: Optional[float] = 60.0, provider: Optional[str] = None, model: Optional[str] = None, **kwargs):
        super().__init__(message)
        self.retry_after = retry_after
        self.provider = provider
        self.model = model

class ProviderUnavailableException(Exception):
    pass

class TimeoutException(Exception):
    pass

class UnknownProviderException(Exception):
    pass

class CircuitOpenException(Exception):
    pass

class ValidationException(Exception):
    pass

class AuthenticationException(Exception):
    pass


class ExecutionEngine:
    """Executes requests using the appropriate provider determined by the router."""

    def __init__(
        self, 
        circuit_breaker: CircuitBreaker,
        cooldown_manager: Optional[ProviderCooldownManager] = None,
        logger: Optional[logging.Logger] = None
    ):
        self.circuit_breaker = circuit_breaker
        self.cooldown_manager = cooldown_manager
        self.logger = logger or logging.getLogger(__name__)

    def execute(
        self, 
        request: AgentRequest,
        provider: Any
    ) -> AgentResponse:
        if not provider:
            raise ValidationException("Provider cannot be None.")

        provider_name = getattr(provider, 'name', 'unknown')

        # If a provider is injected directly, check circuit breaker just in case,
        # but usually the router checks it. If it's open, throw CircuitOpenException.
        if not self.circuit_breaker.is_available(provider_name):
            raise CircuitOpenException(f"Circuit breaker is OPEN for {provider_name}")

        self.logger.info(f"Executing request {request.request_id} with provider {provider_name}")
        start_time = time.time()
        
        try:
            response = provider.chat(request)
            execution_time = time.time() - start_time
            self.logger.info(f"Request {request.request_id} succeeded in {execution_time:.4f}s")
            self.circuit_breaker.record_success(provider_name)
            return response
        except RateLimitException as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Request {request.request_id} failed with {type(e).__name__} in {execution_time:.4f}s. Reason: {e}")
            # Mark cooldown
            if self.cooldown_manager:
                self.cooldown_manager.mark_cooldown(provider_name, duration=getattr(e, 'retry_after', 60.0), model=getattr(e, 'model', None), reason=str(e))
            self.circuit_breaker.record_failure(provider_name, reason=str(e))
            raise
        except ProviderUnavailableException as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Request {request.request_id} failed with {type(e).__name__} in {execution_time:.4f}s. Reason: {e}")
            self.circuit_breaker.record_failure(provider_name, reason=str(e))
            raise
        except TimeoutException as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Request {request.request_id} failed with TimeoutException in {execution_time:.4f}s. Reason: {e}")
            from ai_gateway.core.circuit_breaker import CircuitState
            if self.circuit_breaker.get_state(provider_name) == CircuitState.HALF_OPEN:
                self.circuit_breaker.record_failure(provider_name, reason=str(e))
            raise
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Request {request.request_id} failed with {type(e).__name__} in {execution_time:.4f}s. Reason: {e}")
            raise
