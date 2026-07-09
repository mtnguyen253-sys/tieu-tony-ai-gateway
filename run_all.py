import sys
from unittest.mock import MagicMock
sys.modules['pytest'] = MagicMock()
class Raiser:
    def __init__(self, exc):
        self.exc = exc
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_type:
            raise AssertionError(f"Expected exception {self.exc} not raised")
        if not issubclass(exc_type, self.exc):
            raise AssertionError(f"Expected {self.exc}, got {exc_type}")
        return True
sys.modules['pytest'].raises = Raiser

from ai_gateway.tests.test_fallback import *
from ai_gateway.tests.test_orchestrator import *
from ai_gateway.tests.test_retry import *

# test_fallback
test_1_first_provider_success()
test_2_first_provider_unavailable_fallback_to_second()
test_3_first_provider_circuit_open_fallback()
test_4_first_provider_auth_exception_no_fallback()
test_5_no_provider_available()
test_6_both_providers_fail()
test_7_router_does_not_pick_failed_provider()

# test_orchestrator
test_1_execution_success()
test_2_execution_exception_raised()
test_4_agent_response_unchanged()

# test_retry
test_1_no_retry_success()
test_2_fixed_retry_timeout_success()
test_3_fixed_retry_timeout_fails()
test_4_rate_limit_no_retry()
test_5_provider_unavailable_no_retry()
test_6_unknown_provider_no_retry()
test_7_orchestrator_uses_retry_strategy()

print("ALL MANUAL TESTS PASSED")
