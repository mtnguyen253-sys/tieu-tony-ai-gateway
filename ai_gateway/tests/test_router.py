import pytest
from ai_gateway.registry.capability import (
    CapabilityRegistry, ProviderCapability, TaskRequirement, RoutingPolicy, TaskType
)
from ai_gateway.core.router import PolicyRouter, NoProviderAvailableException, RoutingDecision
from ai_gateway.adapters.base import BaseProvider
from typing import Dict, Any, Generator
from ai_gateway.protocols.cap import AgentRequest, AgentResponse

class MockProvider(BaseProvider):
    def __init__(self, name: str, caps: Dict[str, Any], healthy: bool = True):
        self.name = name
        self._caps = caps
        self._healthy = healthy
        
    @property
    def capabilities(self) -> Dict[str, Any]:
        return self._caps

    def connect(self) -> bool: return True
    def chat(self, request: AgentRequest) -> AgentResponse: pass # type: ignore
    def stream(self, request: AgentRequest) -> Generator[AgentResponse, None, None]: pass # type: ignore
    def tool_call(self, request: AgentRequest) -> AgentResponse: pass # type: ignore
    def health(self) -> Dict[str, Any]: return {"status": "ok" if self._healthy else "error"}
    def estimate_cost(self, request: AgentRequest) -> float: return 0.0

@pytest.fixture
def registry() -> CapabilityRegistry:
    reg = CapabilityRegistry()
    # Gemini
    reg.register("gemini", MockProvider("gemini", {
        "coding": 10.0, "reasoning": 9.0, "translation": 8.0,
        "context_window": 1000000, "tool_call": True, "latency": 500.0, "cost": 5.0
    }))
    # OpenRouter
    reg.register("openrouter", MockProvider("openrouter", {
        "coding": 8.0, "reasoning": 8.0, "translation": 8.0,
        "context_window": 128000, "tool_call": True, "latency": 800.0, "cost": 2.0
    }))
    # Google Free
    reg.register("google_free", MockProvider("google_free", {
        "coding": 5.0, "reasoning": 5.0, "translation": 9.0,
        "context_window": 32000, "tool_call": False, "latency": 300.0, "cost": 0.0
    }))
    return reg

def test_1_refactor_codebase(registry: CapabilityRegistry):
    # Task: Refactor toàn bộ codebase -> coding cao, context lớn -> Expected: gemini
    req = TaskRequirement(task_type=TaskType.CODING, required_context=200000)
    router = PolicyRouter(registry)
    quotas = {"gemini": 10.0, "openrouter": 10.0, "google_free": 10.0}
    
    decision = router.route(req, {}, quotas, RoutingPolicy.QUALITY_FIRST)
    
    assert decision.provider_name == "gemini"
    assert "openrouter" in decision.excluded_providers
    assert decision.excluded_providers["openrouter"] == "Context window too small"
    assert "google_free" in decision.excluded_providers

def test_2_translate_low_cost(registry: CapabilityRegistry):
    # Task: Dịch tài liệu, chi phí thấp -> Expected: google_free
    req = TaskRequirement(task_type=TaskType.TRANSLATION)
    router = PolicyRouter(registry)
    quotas = {"gemini": 10.0, "openrouter": 10.0, "google_free": 10.0}
    
    decision = router.route(req, {}, quotas, RoutingPolicy.COST_FIRST)
    
    assert decision.provider_name == "google_free"

def test_3_gemini_out_of_quota(registry: CapabilityRegistry):
    req = TaskRequirement(task_type=TaskType.CODING)
    router = PolicyRouter(registry)
    quotas = {"gemini": 0.0, "openrouter": 10.0, "google_free": 10.0}
    
    decision = router.route(req, {}, quotas, RoutingPolicy.QUALITY_FIRST)
    
    assert decision.provider_name == "openrouter"
    assert "gemini" in decision.excluded_providers
    assert decision.excluded_providers["gemini"] == "Out of quota"

def test_4_quality_first_gemini_wins(registry: CapabilityRegistry):
    req = TaskRequirement(task_type=TaskType.REASONING)
    router = PolicyRouter(registry)
    quotas = {"gemini": 10.0, "openrouter": 10.0, "google_free": 10.0}
    
    decision = router.route(req, {}, quotas, RoutingPolicy.QUALITY_FIRST)
    
    assert decision.provider_name == "gemini"

def test_5_cost_first_google_free_wins(registry: CapabilityRegistry):
    req = TaskRequirement(task_type=TaskType.GENERAL)
    router = PolicyRouter(registry)
    quotas = {"gemini": 10.0, "openrouter": 10.0, "google_free": 10.0}
    
    decision = router.route(req, {}, quotas, RoutingPolicy.COST_FIRST)
    
    assert decision.provider_name == "google_free"

def test_6_context_exceeds_gemini_excluded(registry: CapabilityRegistry):
    # Context vượt giới hạn -> Gemini bị loại -> Expect NoProviderAvailableException
    req = TaskRequirement(task_type=TaskType.CODING, required_context=2000000)
    router = PolicyRouter(registry)
    quotas = {"gemini": 10.0, "openrouter": 10.0, "google_free": 10.0}
    
    with pytest.raises(NoProviderAvailableException):
        router.route(req, {}, quotas, RoutingPolicy.BALANCED)

def test_7_tool_calling_required(registry: CapabilityRegistry):
    # Tool Calling Required -> Google Free bị loại
    req = TaskRequirement(task_type=TaskType.GENERAL, required_tools=True)
    router = PolicyRouter(registry)
    quotas = {"gemini": 10.0, "openrouter": 10.0, "google_free": 10.0}
    
    decision = router.route(req, {}, quotas, RoutingPolicy.BALANCED)
    
    assert "google_free" in decision.excluded_providers
    assert decision.excluded_providers["google_free"] == "Tool calling not supported"

def test_8_no_provider_available(registry: CapabilityRegistry):
    # Không còn Provider (e.g., budget is extremely low, no one meets it)
    req = TaskRequirement(task_type=TaskType.GENERAL, budget=-1.0)
    router = PolicyRouter(registry)
    quotas = {"gemini": 10.0, "openrouter": 10.0, "google_free": 10.0}
    
    with pytest.raises(NoProviderAvailableException):
        router.route(req, {}, quotas, RoutingPolicy.BALANCED)

def test_9_tie_break():
    # Hai Provider cùng điểm -> Kiểm tra Tie Break (tên alphabet)
    reg = CapabilityRegistry()
    reg.register("beta_provider", MockProvider("beta", {"coding": 5, "cost": 5, "latency": 500}))
    reg.register("alpha_provider", MockProvider("alpha", {"coding": 5, "cost": 5, "latency": 500}))
    
    router = PolicyRouter(reg)
    req = TaskRequirement(task_type=TaskType.CODING)
    quotas = {"beta_provider": 10.0, "alpha_provider": 10.0}
    
    decision = router.route(req, {}, quotas, RoutingPolicy.BALANCED)
    
    assert decision.provider_name == "alpha_provider"

def test_10_registry_refresh(registry: CapabilityRegistry):
    # Registry refresh -> Provider mới được Router nhìn thấy
    req = TaskRequirement(task_type=TaskType.GENERAL)
    router = PolicyRouter(registry)
    quotas = {"gemini": 10.0, "openrouter": 10.0, "google_free": 10.0, "super_provider": 10.0}
    
    # First, gemini should win
    decision = router.route(req, {}, quotas, RoutingPolicy.QUALITY_FIRST)
    assert decision.provider_name == "gemini"
    
    # Introduce new provider and refresh
    registry.refresh("super_provider", MockProvider("super", {
        "coding": 100.0, "reasoning": 100.0, "translation": 100.0, 
        "cost": 0.0, "latency": 1.0, "context_window": 10000000, "tool_call": True
    }))
    
    decision2 = router.route(req, {}, quotas, RoutingPolicy.QUALITY_FIRST)
    assert decision2.provider_name == "super_provider"
