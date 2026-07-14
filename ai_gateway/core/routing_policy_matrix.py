from dataclasses import dataclass
from typing import Optional
from ai_gateway.core.task_classifier import TaskComplexity, ModelTier, TaskClassification

@dataclass
class TaskRoutingPolicy:
    recommended_tier: ModelTier
    max_tier: Optional[ModelTier] = None
    min_tier: Optional[ModelTier] = None
    prefer_cost: bool = False
    prefer_quality: bool = False
    prefer_latency: bool = False
    prefer_cache: bool = False
    allow_higher_cost: bool = False
    require_safe_mode: bool = False
    should_call_llm: bool = True
    
    allow_escalation: bool = False
    escalation_tier: Optional[ModelTier] = None
    escalation_reason: Optional[str] = None

class RoutingPolicyMatrix:
    def __init__(self):
        self.matrix = {
            TaskComplexity.NO_LLM: TaskRoutingPolicy(
                recommended_tier=ModelTier.NONE,
                should_call_llm=False
            ),
            TaskComplexity.SIMPLE: TaskRoutingPolicy(
                recommended_tier=ModelTier.CHEAP,
                max_tier=ModelTier.BALANCED,
                prefer_cost=True,
                prefer_latency=True
            ),
            TaskComplexity.STANDARD: TaskRoutingPolicy(
                recommended_tier=ModelTier.BALANCED,
                max_tier=ModelTier.STRONG
            ),
            TaskComplexity.COMPLEX: TaskRoutingPolicy(
                recommended_tier=ModelTier.STRONG,
                min_tier=ModelTier.BALANCED,
                prefer_quality=True,
                allow_higher_cost=True,
                allow_escalation=True,
                escalation_tier=ModelTier.STRONG,
                escalation_reason="Complex task requires strong model on retry"
            ),
            TaskComplexity.CRITICAL: TaskRoutingPolicy(
                recommended_tier=ModelTier.STRONG,
                min_tier=ModelTier.STRONG,
                require_safe_mode=True,
                prefer_quality=True
            ),
            TaskComplexity.LONG_CONTEXT: TaskRoutingPolicy(
                recommended_tier=ModelTier.LONG_CONTEXT,
                prefer_cache=True,
                prefer_cost=True # prefer low effective input cost
            )
        }
        
    def get_policy(self, classification: TaskClassification) -> TaskRoutingPolicy:
        return self.matrix.get(classification.complexity, self.matrix[TaskComplexity.STANDARD])
