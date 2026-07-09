import re
with open("ai_gateway/core/executor.py", "r") as f:
    content = f.read()

# Fix indentation and logic around provider none check
content = re.sub(
    r"        if not provider:\n\s*raise ValidationException\(\"Provider cannot be None.\"\)\n\s*# We assume provider object has a name attribute or we can derive it.\n\s*# In our mock/tests, it has `.name`.\n\s*provider_name = getattr\(provider, 'name', 'unknown'\)\n\s*if not provider:\n\s*raise UnknownProviderException\(f\"Provider \{provider_name\} is unknown or None.\"\)\n",
    "        if not provider:\n            raise ValidationException(\"Provider cannot be None.\")\n\n        provider_name = getattr(provider, 'name', 'unknown')\n",
    content
)

# Update the try-except block
content = re.sub(
    r"        try:\n\s*response = provider.chat\(request\)\n\s*execution_time = time.time\(\) - start_time\n\s*self.logger.info\(f\"Request \{request.request_id\} succeeded in \{execution_time:.4f\}s\"\)\n\s*return response\n\s*except \(RateLimitException, ProviderUnavailableException\) as e:\n\s*execution_time = time.time\(\) - start_time\n\s*self.logger.error\(f\"Request \{request.request_id\} failed with \{type\(e\).__name__\} in \{execution_time:.4f\}s. Reason: \{e\}\"\)\n\s*self.circuit_breaker.trip\(provider_name, reason=str\(e\)\)\n\s*raise\n\s*except Exception as e:\n\s*execution_time = time.time\(\) - start_time\n\s*self.logger.error\(f\"Request \{request.request_id\} failed with \{type\(e\).__name__\} in \{execution_time:.4f\}s. Reason: \{e\}\"\)\n\s*raise\n",
    "        try:\n            response = provider.chat(request)\n            execution_time = time.time() - start_time\n            self.logger.info(f\"Request {request.request_id} succeeded in {execution_time:.4f}s\")\n            self.circuit_breaker.record_success(provider_name)\n            return response\n        except (RateLimitException, ProviderUnavailableException) as e:\n            execution_time = time.time() - start_time\n            self.logger.error(f\"Request {request.request_id} failed with {type(e).__name__} in {execution_time:.4f}s. Reason: {e}\")\n            self.circuit_breaker.record_failure(provider_name, reason=str(e))\n            raise\n        except TimeoutException as e:\n            execution_time = time.time() - start_time\n            self.logger.error(f\"Request {request.request_id} failed with TimeoutException in {execution_time:.4f}s. Reason: {e}\")\n            from ai_gateway.core.circuit_breaker import CircuitState\n            if self.circuit_breaker.get_state(provider_name) == CircuitState.HALF_OPEN:\n                self.circuit_breaker.record_failure(provider_name, reason=str(e))\n            raise\n        except Exception as e:\n            execution_time = time.time() - start_time\n            self.logger.error(f\"Request {request.request_id} failed with {type(e).__name__} in {execution_time:.4f}s. Reason: {e}\")\n            raise\n",
    content
)

with open("ai_gateway/core/executor.py", "w") as f:
    f.write(content)
