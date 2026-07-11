import logging
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class RoutingPolicy(str, Enum):
    BALANCED = "BALANCED"
    QUALITY_FIRST = "QUALITY_FIRST"
    COST_FIRST = "COST_FIRST"
    LATENCY_FIRST = "LATENCY_FIRST"

class TaskType(str, Enum):
    CODING = "CODING"
    REASONING = "REASONING"
    TRANSLATION = "TRANSLATION"
    GENERAL = "GENERAL"

class ProviderCapability(BaseModel):
    coding: float = 0.0
    reasoning: float = 0.0
    translation: float = 0.0
    context_window: int = 0
    tool_call: bool = False
    latency: float = 0.0
    cost: float = 0.0
    quota_weight: float = 1.0

class TaskRequirement(BaseModel):
    task_type: TaskType = TaskType.GENERAL
    required_context: int = 0
    required_tools: bool = False
    priority: int = 1
    budget: float = 100.0
    latency_requirement: float = 10000.0

class CapabilityRegistry:
    def __init__(self):
        self._providers: Dict[str, Any] = {}
        self._capabilities: Dict[str, ProviderCapability] = {}

    def register(self, name: str, provider: Any) -> None:
        self._providers[name] = provider
        # Extract raw dict from provider capabilities property
        raw_caps = provider.capabilities
        self._capabilities[name] = ProviderCapability(
            coding=raw_caps.get("coding", raw_caps.get("codebase_reading", 0.0)),
            reasoning=raw_caps.get("reasoning", 0.0),
            translation=raw_caps.get("translation", 0.0),
            context_window=raw_caps.get("context_window", 0),
            tool_call=raw_caps.get("tool_call", False),
            latency=raw_caps.get("latency", 0.0),
            cost=raw_caps.get("cost", 0.0),
            quota_weight=raw_caps.get("quota_weight", 1.0)
        )

    def unregister(self, name: str) -> None:
        self._providers.pop(name, None)
        self._capabilities.pop(name, None)

    def refresh(self, name: str, provider: Any) -> None:
        self.register(name, provider)

    def get(self, name: str) -> Optional[ProviderCapability]:
        return self._capabilities.get(name)

    def get_provider(self, name: str) -> Optional[Any]:
        return self._providers.get(name)

    def all(self) -> Dict[str, ProviderCapability]:
        return self._capabilities.copy()

class ScoringEngine:
    @staticmethod
    def constraints(capability: ProviderCapability, requirement: TaskRequirement, quota: float, is_healthy: bool) -> bool:
        if quota <= 0:
            return False
        if not is_healthy:
            return False
        if capability.context_window < requirement.required_context:
            return False
        if requirement.required_tools and not capability.tool_call:
            return False
        if capability.cost > requirement.budget:
            return False
        if capability.latency > requirement.latency_requirement:
            return False
        return True

    @staticmethod
    def weight(policy: RoutingPolicy, mode: str = "normal", prefer_cheaper: bool = True) -> Dict[str, float]:
        if policy == RoutingPolicy.QUALITY_FIRST:
            weights = {"quality": 0.7, "cost": 0.1, "latency": 0.1, "quota": 0.1}
        elif policy == RoutingPolicy.COST_FIRST:
            weights = {"quality": 0.2, "cost": 0.6, "latency": 0.1, "quota": 0.1}
        elif policy == RoutingPolicy.LATENCY_FIRST:
            weights = {"quality": 0.2, "cost": 0.1, "latency": 0.6, "quota": 0.1}
        else:  # BALANCED
            weights = {"quality": 0.4, "cost": 0.3, "latency": 0.2, "quota": 0.1}
            
        if mode == "emergency":
            # Budget emergency: strongly prioritize cost, minimize quality/latency weight
            weights["cost"] = min(1.0, weights["cost"] + 0.6)
            weights["quality"] = max(0.0, weights["quality"] - 0.3)
            weights["latency"] = max(0.0, weights["latency"] - 0.3)
        elif mode == "economy" or (prefer_cheaper and policy != RoutingPolicy.QUALITY_FIRST):
            # Increase cost weight
            weights["cost"] = min(1.0, weights["cost"] + 0.3)
            weights["quality"] = max(0.0, weights["quality"] - 0.15)
            weights["latency"] = max(0.0, weights["latency"] - 0.15)
            
        return weights

    @staticmethod
    def score(capability: ProviderCapability, requirement: TaskRequirement, policy: RoutingPolicy, quota: float, mode: str = "normal", prefer_cheaper: bool = True, penalty: float = 0.0) -> float:
        weights = ScoringEngine.weight(policy, mode, prefer_cheaper)

        # Base quality score on task type
        quality_score = 0.0
        if requirement.task_type == TaskType.CODING:
            quality_score = capability.coding
        elif requirement.task_type == TaskType.REASONING:
            quality_score = capability.reasoning
        elif requirement.task_type == TaskType.TRANSLATION:
            quality_score = capability.translation
        else:
            quality_score = (capability.coding + capability.reasoning + capability.translation) / 3.0

        # Cost score (inverted, 0 means best/free, higher is worse)
        # Assumes cost is typically between 0 and 10.
        cost_score = max(0.0, 10.0 - capability.cost)

        # Latency score (inverted, lower is better)
        # Latency is often in ms, max 10,000 assumed for normalization
        latency_score = max(0.0, 10.0 - (capability.latency / 1000.0))

        # Quota score
        quota_score = min(10.0, quota * capability.quota_weight)

        final_score = (
            quality_score * weights["quality"] +
            cost_score * weights["cost"] +
            latency_score * weights["latency"] +
            quota_score * weights["quota"]
        )
        final_score = max(0.0, final_score - penalty)
        return final_score
