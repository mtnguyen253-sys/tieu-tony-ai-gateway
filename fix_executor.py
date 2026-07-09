import os
import re

# 1. ai_gateway/core/executor.py
with open("ai_gateway/core/executor.py", "r") as f:
    content = f.read()
content = content.replace("from ai_gateway.core.router import PolicyRouter\n", "")
content = content.replace("from ai_gateway.registry.capability import TaskRequirement, RoutingPolicy\n", "")
content = re.sub(
    r"def __init__\(\s*self,\s*router:\s*PolicyRouter,\s*circuit_breaker:\s*CircuitBreaker,\s*logger:\s*Optional\[logging\.Logger\]\s*=\s*None\s*\):",
    "def __init__(\n        self, \n        circuit_breaker: CircuitBreaker,\n        logger: Optional[logging.Logger] = None\n    ):",
    content
)
content = content.replace("        self.router = router\n", "")
content = re.sub(
    r"def execute\(\s*self,\s*request:\s*AgentRequest,\s*requirement:\s*Optional\[TaskRequirement\]\s*=\s*None,\s*context:\s*Optional\[Dict\[str,\s*Any\]\]\s*=\s*None,\s*quotas:\s*Optional\[Dict\[str,\s*float\]\]\s*=\s*None,\s*policy:\s*Optional\[RoutingPolicy\]\s*=\s*None,\s*provider:\s*Optional\[Any\]\s*=\s*None\s*\)\s*->\s*AgentResponse:",
    "def execute(\n        self, \n        request: AgentRequest,\n        provider: Any\n    ) -> AgentResponse:",
    content
)
content = re.sub(
    r"        requirement\s*=\s*requirement\s*or\s*TaskRequirement\(\)\n\s*context\s*=\s*context\s*or\s*\{\}\n\s*quotas\s*=\s*quotas\s*or\s*\{\}\n\s*policy\s*=\s*policy\s*or\s*RoutingPolicy.BALANCED\n\s*if not provider:\n\s*decision\s*=\s*self.router.route\(requirement, context, quotas, policy\)\n\s*provider_name\s*=\s*decision.provider_name\n\s*provider\s*=\s*decision.provider\n\s*else:\n",
    "        if not provider:\n            raise ValidationException(\"Provider cannot be None.\")\n\n",
    content
)
with open("ai_gateway/core/executor.py", "w") as f:
    f.write(content)

# 2. ai_gateway/core/orchestrator.py
with open("ai_gateway/core/orchestrator.py", "r") as f:
    content = f.read()

content = content.replace("from ai_gateway.core.executor import ExecutionEngine\n", "from ai_gateway.core.executor import ExecutionEngine\nfrom ai_gateway.core.router import PolicyRouter\n")

content = re.sub(
    r"def __init__\(\s*self,\s*engine:\s*ExecutionEngine,\s*retry_strategy:\s*Optional\[RetryStrategy\]\s*=\s*None,\s*fallback_strategy:\s*Optional\[FallbackStrategy\]\s*=\s*None,\s*logger:\s*Optional\[logging\.Logger\]\s*=\s*None\s*\):",
    "def __init__(\n        self,\n        engine: ExecutionEngine,\n        router: PolicyRouter,\n        retry_strategy: Optional[RetryStrategy] = None,\n        fallback_strategy: Optional[FallbackStrategy] = None,\n        logger: Optional[logging.Logger] = None\n    ):",
    content
)
content = content.replace("        self.engine = engine\n", "        self.engine = engine\n        self.router = router\n")
content = re.sub(
    r"return self\.engine\.execute\(\n\s*request=request,\n\s*requirement=requirement,\n\s*context=context,\n\s*quotas=quotas,\n\s*policy=policy,\n\s*provider=provider\n\s*\)",
    "return self.engine.execute(\n                    request=request,\n                    provider=provider\n                )",
    content
)
content = re.sub(
    r"            response = self\.fallback_strategy\.execute\(\n\s*_operation,\n\s*requirement=requirement,\n\s*context=context,\n\s*quotas=quotas,\n\s*policy=policy\n\s*\)",
    "            if isinstance(self.fallback_strategy, NoFallbackStrategy):\n                decision = self.router.route(requirement, context, quotas, policy)\n                response = _operation(decision.provider)\n            else:\n                response = self.fallback_strategy.execute(\n                    _operation,\n                    requirement=requirement,\n                    context=context,\n                    quotas=quotas,\n                    policy=policy\n                )",
    content
)
with open("ai_gateway/core/orchestrator.py", "w") as f:
    f.write(content)

# 3. ai_gateway/core/fallback.py
with open("ai_gateway/core/fallback.py", "r") as f:
    content = f.read()

content = content.replace("    ExecutionEngine,\n", "")
content = content.replace("class ProviderFallbackStrategy(FallbackStrategy):\n    def __init__(self, router: PolicyRouter, engine: ExecutionEngine):\n        self.router = router\n        self.engine = engine", "class ProviderFallbackStrategy(FallbackStrategy):\n    def __init__(self, router: PolicyRouter):\n        self.router = router")

with open("ai_gateway/core/fallback.py", "w") as f:
    f.write(content)

# 4. ai_gateway/tests/test_executor.py
with open("ai_gateway/tests/test_executor.py", "r") as f:
    content = f.read()
content = content.replace("from ai_gateway.core.router import NoProviderAvailableException, RoutingDecision\n", "")
content = content.replace("from ai_gateway.registry.capability import RoutingPolicy\n", "")
content = content.replace("from ai_gateway.core.executor import (\n    ExecutionEngine, RateLimitException, ProviderUnavailableException, TimeoutException, UnknownProviderException\n)", "from ai_gateway.core.executor import (\n    ExecutionEngine, RateLimitException, ProviderUnavailableException, TimeoutException, UnknownProviderException, ValidationException\n)")

# Remove MockRouter completely from test_executor.py since we don't route anymore.
content = re.sub(r"class MockRouter:\n.*?def route\(.*?\):.*?timestamp=0\.0\n\s*\)\n", "", content, flags=re.DOTALL)

# Refactor test cases
content = re.sub(
    r"    router = MockRouter\(provider_name=\"p1\", provider=provider\)\n    cb = CircuitBreaker\(\)\n    engine = ExecutionEngine\(router=router, circuit_breaker=cb\) # type: ignore\n\s*result = engine.execute\(req\)",
    "    cb = CircuitBreaker()\n    engine = ExecutionEngine(circuit_breaker=cb) # type: ignore\n    result = engine.execute(req, provider=provider)",
    content
)
content = re.sub(
    r"    router = MockRouter\(provider_name=\"p1\", provider=provider\)\n    cb = CircuitBreaker\(\)\n    engine = ExecutionEngine\(router=router, circuit_breaker=cb\) # type: ignore\n\s*with pytest.raises\(RateLimitException\):\n\s*engine.execute\(req\)",
    "    cb = CircuitBreaker()\n    engine = ExecutionEngine(circuit_breaker=cb) # type: ignore\n    with pytest.raises(RateLimitException):\n        engine.execute(req, provider=provider)",
    content
)
content = re.sub(
    r"    router = MockRouter\(provider_name=\"p1\", provider=provider\)\n    cb = CircuitBreaker\(\)\n    engine = ExecutionEngine\(router=router, circuit_breaker=cb\) # type: ignore\n\s*with pytest.raises\(TimeoutException\):\n\s*engine.execute\(req\)",
    "    cb = CircuitBreaker()\n    engine = ExecutionEngine(circuit_breaker=cb) # type: ignore\n    with pytest.raises(TimeoutException):\n        engine.execute(req, provider=provider)",
    content
)
# test 4 was about router failing. Let's change it to test provider being None.
content = re.sub(
    r"def test_4_router_no_provider\(\):\n\s*req = AgentRequest\(request_id=\"req4\", messages=\[\]\)\n\s*router = MockRouter\(should_raise=True\)\n\s*cb = CircuitBreaker\(\)\n\s*engine = ExecutionEngine\(router=router, circuit_breaker=cb\) # type: ignore\n\s*with pytest.raises\(NoProviderAvailableException\):\n\s*engine.execute\(req\)",
    "def test_4_provider_none_raises_validation():\n    req = AgentRequest(request_id=\"req4\", messages=[])\n    cb = CircuitBreaker()\n    engine = ExecutionEngine(circuit_breaker=cb) # type: ignore\n    with pytest.raises(ValidationException):\n        engine.execute(req, provider=None)",
    content
)
content = re.sub(
    r"    router = MockRouter\(provider_name=\"p1\", provider=provider\)\n    cb = CircuitBreaker\(\)\n    engine = ExecutionEngine\(router=router, circuit_breaker=cb\) # type: ignore\n\s*result = engine.execute\(req\)",
    "    cb = CircuitBreaker()\n    engine = ExecutionEngine(circuit_breaker=cb) # type: ignore\n    result = engine.execute(req, provider=provider)",
    content
)
content = re.sub(
    r"    router = MockRouter\(provider_name=\"p1\", provider=provider\)\n    cb = CircuitBreaker\(\)\n    test_logger = logging.getLogger\(\"test_logger\"\)\n    test_logger.setLevel\(logging.INFO\)\n    engine = ExecutionEngine\(router=router, circuit_breaker=cb, logger=test_logger\) # type: ignore\n\s*with caplog.at_level\(logging.INFO, logger=\"test_logger\"\):\n\s*engine.execute\(req\)",
    "    cb = CircuitBreaker()\n    test_logger = logging.getLogger(\"test_logger\")\n    test_logger.setLevel(logging.INFO)\n    engine = ExecutionEngine(circuit_breaker=cb, logger=test_logger) # type: ignore\n    with caplog.at_level(logging.INFO, logger=\"test_logger\"):\n        engine.execute(req, provider=provider)",
    content
)
# test 7 was about provider none raises unknown. Wait, executionEngine now raises ValidationException if None. Let's just remove it.
content = re.sub(
    r"def test_7_provider_none_raises_unknown\(\):.*",
    "",
    content, flags=re.DOTALL
)
with open("ai_gateway/tests/test_executor.py", "w") as f:
    f.write(content)

# 5. ai_gateway/tests/test_orchestrator.py
with open("ai_gateway/tests/test_orchestrator.py", "r") as f:
    content = f.read()

# Add a mock router to orchestrator tests
content = content.replace("from ai_gateway.protocols.cap import AgentRequest, AgentResponse\n", "from ai_gateway.protocols.cap import AgentRequest, AgentResponse\nfrom ai_gateway.core.router import RoutingDecision\n")

mock_router_code = """
class MockRouter:
    def route(self, requirement, context, quotas, policy):
        return RoutingDecision(provider_name="p1", provider="mock_prov", score=1.0, reason="", excluded_providers={}, policy_used=None, timestamp=0.0)
"""
content = content.replace("class MockExecutionEngine:", mock_router_code + "\nclass MockExecutionEngine:")
content = content.replace("    def execute(self, request, requirement=None, context=None, quotas=None, policy=None):", "    def execute(self, request, provider=None):")
content = content.replace("    orchestrator = ExecutionOrchestrator(engine=engine) # type: ignore", "    router = MockRouter()\n    orchestrator = ExecutionOrchestrator(engine=engine, router=router) # type: ignore")
content = content.replace("    orchestrator = ExecutionOrchestrator(engine=engine, logger=test_logger) # type: ignore", "    router = MockRouter()\n    orchestrator = ExecutionOrchestrator(engine=engine, router=router, logger=test_logger) # type: ignore")

with open("ai_gateway/tests/test_orchestrator.py", "w") as f:
    f.write(content)

# 6. ai_gateway/tests/test_fallback.py
with open("ai_gateway/tests/test_fallback.py", "r") as f:
    content = f.read()

content = content.replace("    ExecutionEngine)\n", ")\n")
content = content.replace(", engine=None", "")
with open("ai_gateway/tests/test_fallback.py", "w") as f:
    f.write(content)

