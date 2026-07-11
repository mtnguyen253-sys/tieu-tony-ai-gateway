from ai_gateway.core.budget import BudgetManager
import time
import logging
from typing import Dict, Any, Optional
from ai_gateway.core.usage import UsageEvent, UsageLedger
from ai_gateway.core.cost import CostEstimator

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
        usage_ledger: Optional[UsageLedger] = None,
        cost_estimator: Optional[CostEstimator] = None,
        budget_manager: Optional[BudgetManager] = None,
        logger: Optional[logging.Logger] = None
    ):
        self.circuit_breaker = circuit_breaker
        self.cooldown_manager = cooldown_manager
        self.usage_ledger = usage_ledger
        self.cost_estimator = cost_estimator
        self.budget_manager = budget_manager
        self.logger = logger or logging.getLogger(__name__)

    def execute(
        self,
        request: AgentRequest,
        provider: Any,
        **kwargs
    ) -> AgentResponse:
        if not provider:
            raise ValidationException("Provider cannot be None.")
        provider_name = getattr(provider, 'name', 'unknown')
        
        fallback_count = kwargs.get("fallback_count", 0)
        retry_count = kwargs.get("retry_count", 0)
        route_policy = kwargs.get("policy", None)

        if not self.circuit_breaker.is_available(provider_name):
            if self.usage_ledger:
                self.usage_ledger.record(UsageEvent(
                    request_id=request.request_id,
                    timestamp=time.time(),
                    provider=provider_name,
                    status="error",
                    error_type="CircuitOpenException",
                    error_code="circuit_open",
                    fallback_count=fallback_count,
                    retry_count=retry_count,
                    route_policy=route_policy
                ))
            raise CircuitOpenException(f"Circuit breaker is OPEN for {provider_name}")

        self.logger.info(f"Executing request {request.request_id} with provider {provider_name}")
        start_time = time.time()
        
        def _record_usage(status, error_type=None, error_code=None, cooldown_triggered=False, response=None, latency_ms=None):
            input_tokens = None
            cached_input_tokens = None
            output_tokens = None
            total_tokens = None
            model = getattr(provider, 'default_model', None)
            resolved_model = model
            estimated_cost = None

            if response and response.usage:
                usage = response.usage
                input_tokens = usage.get("prompt_tokens")
                output_tokens = usage.get("completion_tokens")
                total_tokens = usage.get("total_tokens")
                prompt_details = usage.get("prompt_tokens_details", {})
                cached_input_tokens = prompt_details.get("cached_tokens")
                
                if response.model:
                    resolved_model = response.model
                    
                if self.cost_estimator:
                    estimated_cost = self.cost_estimator.estimate(
                        provider=provider_name,
                        model=resolved_model,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        cached_input_tokens=cached_input_tokens
                    )

            if self.budget_manager:
                if status == "success":
                    self.budget_manager.record_success(
                        provider_name, 
                        latency_ms=latency_ms,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens
                    )
                    if estimated_cost is not None:
                        self.budget_manager.record_spend(provider_name, estimated_cost)
                elif error_type == "RateLimitException":
                    self.budget_manager.record_rate_limit(provider_name)
                else:
                    self.budget_manager.record_error(provider_name)

            if not self.usage_ledger:
                return
            
            input_tokens = None
            cached_input_tokens = None
            output_tokens = None
            total_tokens = None
            model = getattr(provider, 'default_model', None)
            resolved_model = model
            estimated_cost = None

            if response and response.usage:
                usage = response.usage
                input_tokens = usage.get("prompt_tokens")
                output_tokens = usage.get("completion_tokens")
                total_tokens = usage.get("total_tokens")
                # OpenAI standard for cached tokens: prompt_tokens_details -> cached_tokens
                prompt_details = usage.get("prompt_tokens_details", {})
                cached_input_tokens = prompt_details.get("cached_tokens")
                
                if response.model:
                    resolved_model = response.model
                
                if self.cost_estimator:
                    estimated_cost = self.cost_estimator.estimate(
                        provider=provider_name,
                        model=resolved_model,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        cached_input_tokens=cached_input_tokens
                    )
            
            event = UsageEvent(
                request_id=request.request_id,
                timestamp=time.time(),
                provider=provider_name,
                model=model,
                resolved_model=resolved_model,
                input_tokens=input_tokens,
                cached_input_tokens=cached_input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                estimated_cost=estimated_cost,
                latency_ms=latency_ms,
                status=status,
                error_type=error_type,
                error_code=error_code,
                fallback_count=fallback_count,
                retry_count=retry_count,
                cooldown_triggered=cooldown_triggered,
                route_policy=route_policy
            )
            self.usage_ledger.record(event)

        try:
            response = provider.chat(request)
            execution_time = time.time() - start_time
            latency_ms = execution_time * 1000
            self.logger.info(f"Request {request.request_id} succeeded in {execution_time:.4f}s")
            self.circuit_breaker.record_success(provider_name)
            
            _record_usage(status="success", response=response, latency_ms=latency_ms)
            
            return response
        except RateLimitException as e:
            execution_time = time.time() - start_time
            latency_ms = execution_time * 1000
            self.logger.error(f"Request {request.request_id} failed with {type(e).__name__} in {execution_time:.4f}s. Reason: {e}")
            cooldown_triggered = False
            if self.cooldown_manager:
                self.cooldown_manager.mark_cooldown(provider_name, duration=getattr(e, 'retry_after', 60.0), model=getattr(e, 'model', None), reason=str(e))
                cooldown_triggered = True
            self.circuit_breaker.record_failure(provider_name, reason=str(e))
            
            _record_usage(status="error", error_type="RateLimitException", error_code="provider_rate_limited", cooldown_triggered=cooldown_triggered, latency_ms=latency_ms)
            raise
        except ProviderUnavailableException as e:
            execution_time = time.time() - start_time
            latency_ms = execution_time * 1000
            self.logger.error(f"Request {request.request_id} failed with {type(e).__name__} in {execution_time:.4f}s. Reason: {e}")
            self.circuit_breaker.record_failure(provider_name, reason=str(e))
            _record_usage(status="error", error_type="ProviderUnavailableException", latency_ms=latency_ms)
            raise
        except TimeoutException as e:
            execution_time = time.time() - start_time
            latency_ms = execution_time * 1000
            self.logger.error(f"Request {request.request_id} failed with TimeoutException in {execution_time:.4f}s. Reason: {e}")
            from ai_gateway.core.circuit_breaker import CircuitState
            if self.circuit_breaker.get_state(provider_name) == CircuitState.HALF_OPEN:
                self.circuit_breaker.record_failure(provider_name, reason=str(e))
            _record_usage(status="error", error_type="TimeoutException", latency_ms=latency_ms)
            raise
        except Exception as e:
            execution_time = time.time() - start_time
            latency_ms = execution_time * 1000
            self.logger.error(f"Request {request.request_id} failed with {type(e).__name__} in {execution_time:.4f}s. Reason: {e}")
            _record_usage(status="error", error_type=type(e).__name__, latency_ms=latency_ms)
            raise


    def execute_stream(
        self,
        request: AgentRequest,
        provider: Any,
        **kwargs
    ):
        if not provider:
            raise ValidationException("Provider cannot be None.")
        provider_name = getattr(provider, 'name', 'unknown')
        
        fallback_count = kwargs.get("fallback_count", 0)
        retry_count = kwargs.get("retry_count", 0)
        route_policy = kwargs.get("policy", None)

        if not self.circuit_breaker.is_available(provider_name):
            if self.usage_ledger:
                self.usage_ledger.record(UsageEvent(
                    request_id=request.request_id,
                    timestamp=time.time(),
                    provider=provider_name,
                    status="error",
                    error_type="CircuitOpenException",
                    error_code="circuit_open",
                    fallback_count=fallback_count,
                    retry_count=retry_count,
                    route_policy=route_policy,
                    stream=True
                ))
            raise CircuitOpenException(f"Circuit breaker is OPEN for {provider_name}")

        self.logger.info(f"Executing stream request {request.request_id} with provider {provider_name}")
        start_time = time.time()
        
        def _record_usage(status, error_type=None, error_code=None, cooldown_triggered=False, latency_ms=None, input_tokens=None, output_tokens=None, total_tokens=None, model=None, estimated_cost=None):
            if self.budget_manager:
                if status == "success":
                    self.budget_manager.record_success(
                        provider_name, 
                        latency_ms=latency_ms,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens
                    )
                    if estimated_cost is not None:
                        self.budget_manager.record_spend(provider_name, estimated_cost)
                elif error_type == "RateLimitException":
                    self.budget_manager.record_rate_limit(provider_name)
                else:
                    self.budget_manager.record_error(provider_name)

            if not self.usage_ledger:
                return
            
            resolved_model = model or getattr(provider, 'default_model', None)
            
            event = UsageEvent(
                request_id=request.request_id,
                timestamp=time.time(),
                provider=provider_name,
                model=getattr(provider, 'default_model', None),
                resolved_model=resolved_model,
                input_tokens=input_tokens,
                cached_input_tokens=None,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                estimated_cost=estimated_cost,
                latency_ms=latency_ms,
                status=status,
                error_type=error_type,
                error_code=error_code,
                fallback_count=fallback_count,
                retry_count=retry_count,
                cooldown_triggered=cooldown_triggered,
                route_policy=route_policy,
                stream=True
            )
            self.usage_ledger.record(event)

        try:
            stream_iter = provider.stream(request)
            # return a generator that wraps the stream
            def _generator():
                last_usage = None
                model = None
                try:
                    for chunk in stream_iter:
                        if isinstance(chunk, dict) and chunk.get("usage"):
                            last_usage = chunk.get("usage")
                        if isinstance(chunk, dict) and chunk.get("model"):
                            model = chunk.get("model")
                        yield chunk
                    
                    execution_time = time.time() - start_time
                    latency_ms = execution_time * 1000
                    self.circuit_breaker.record_success(provider_name)
                    
                    input_tokens = None
                    output_tokens = None
                    total_tokens = None
                    estimated_cost = None
                    if last_usage:
                        input_tokens = last_usage.get("prompt_tokens")
                        output_tokens = last_usage.get("completion_tokens")
                        total_tokens = last_usage.get("total_tokens")
                        if self.cost_estimator:
                            estimated_cost = self.cost_estimator.estimate(
                                provider=provider_name,
                                model=model or getattr(provider, 'default_model', None),
                                input_tokens=input_tokens,
                                output_tokens=output_tokens
                            )
                    _record_usage(status="success", latency_ms=latency_ms, input_tokens=input_tokens, output_tokens=output_tokens, total_tokens=total_tokens, model=model, estimated_cost=estimated_cost)
                except Exception as e:
                    execution_time = time.time() - start_time
                    latency_ms = execution_time * 1000
                    self.logger.error(f"Stream interrupted: {e}")
                    # We might not be able to fallback mid-stream, so just record error
                    _record_usage(status="error", error_type=type(e).__name__, latency_ms=latency_ms)
                    raise
            
            return _generator()

        except RateLimitException as e:
            execution_time = time.time() - start_time
            latency_ms = execution_time * 1000
            self.logger.error(f"Stream request {request.request_id} failed with {type(e).__name__} in {execution_time:.4f}s. Reason: {e}")
            cooldown_triggered = False
            if self.cooldown_manager:
                self.cooldown_manager.mark_cooldown(provider_name, duration=getattr(e, 'retry_after', 60.0), model=getattr(e, 'model', None), reason=str(e))
                cooldown_triggered = True
            self.circuit_breaker.record_failure(provider_name, reason=str(e))
            
            _record_usage(status="error", error_type="RateLimitException", error_code="provider_rate_limited", cooldown_triggered=cooldown_triggered, latency_ms=latency_ms)
            raise
        except ProviderUnavailableException as e:
            execution_time = time.time() - start_time
            latency_ms = execution_time * 1000
            self.logger.error(f"Stream request {request.request_id} failed with {type(e).__name__} in {execution_time:.4f}s. Reason: {e}")
            self.circuit_breaker.record_failure(provider_name, reason=str(e))
            _record_usage(status="error", error_type="ProviderUnavailableException", latency_ms=latency_ms)
            raise
        except TimeoutException as e:
            execution_time = time.time() - start_time
            latency_ms = execution_time * 1000
            self.logger.error(f"Stream request {request.request_id} failed with TimeoutException in {execution_time:.4f}s. Reason: {e}")
            from ai_gateway.core.circuit_breaker import CircuitState
            if self.circuit_breaker.get_state(provider_name) == CircuitState.HALF_OPEN:
                self.circuit_breaker.record_failure(provider_name, reason=str(e))
            _record_usage(status="error", error_type="TimeoutException", latency_ms=latency_ms)
            raise
        except Exception as e:
            execution_time = time.time() - start_time
            latency_ms = execution_time * 1000
            self.logger.error(f"Stream request {request.request_id} failed with {type(e).__name__} in {execution_time:.4f}s. Reason: {e}")
            _record_usage(status="error", error_type=type(e).__name__, latency_ms=latency_ms)
            raise

