from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

class TaskComplexity(str, Enum):
    NO_LLM = "no_llm"
    SIMPLE = "simple"
    STANDARD = "standard"
    COMPLEX = "complex"
    CRITICAL = "critical"
    LONG_CONTEXT = "long_context"

class ModelTier(str, Enum):
    NONE = "none"
    CHEAP = "cheap"
    BALANCED = "balanced"
    STRONG = "strong"
    LONG_CONTEXT = "long_context"

@dataclass
class TaskClassification:
    complexity: TaskComplexity
    reason: str
    estimated_input_tokens: int = 0
    needs_reasoning: bool = False
    needs_coding: bool = False
    needs_tool_calling: bool = False
    is_long_context: bool = False
    is_destructive: bool = False

class TaskClassifier:
    def __init__(self):
        pass

    def estimate_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """Extremely rough estimation: 4 chars ~ 1 token."""
        total_chars = 0
        for m in messages:
            content = m.get("content", "")
            if isinstance(content, str):
                total_chars += len(content)
            elif isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and "text" in part:
                        total_chars += len(part["text"])
        return total_chars // 4

    def classify(self, req) -> TaskClassification:
        messages = getattr(req, "messages", [])
        tools = getattr(req, "tools", None)
        
        estimated_tokens = self.estimate_tokens(messages)
        
        # Determine basic traits
        has_tools = bool(tools)
        is_long = estimated_tokens > 8000
        
        # Analyze content
        content_text = ""
        for m in messages:
            content = m.get("content", "")
            if isinstance(content, str):
                content_text += content.lower() + "\n"
            elif isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and "text" in part:
                        content_text += part["text"].lower() + "\n"

        is_coding = any(kw in content_text for kw in ["code", "function", "class", "refactor", "bug", "python", "javascript", "typescript", "debug"])
        needs_reasoning = any(kw in content_text for kw in ["analyze", "architect", "why", "explain complex", "reasoning", "think step by step"])
        is_destructive = any(kw in content_text for kw in ["delete", "drop table", "remove", "destroy", "rm -rf", "push to main"])
        is_security = any(kw in content_text for kw in ["secret", "password", "api_key", "auth", "token", "credentials"])
        
        # Determine complexity based on heuristics
        
        # 1. Critical tasks
        if is_destructive or is_security:
            return TaskClassification(
                complexity=TaskComplexity.CRITICAL,
                reason="Task involves destructive actions or security/secrets",
                estimated_input_tokens=estimated_tokens,
                needs_coding=is_coding,
                needs_reasoning=needs_reasoning,
                needs_tool_calling=has_tools,
                is_destructive=True
            )
            
        # 2. Long context tasks
        if is_long:
            return TaskClassification(
                complexity=TaskComplexity.LONG_CONTEXT,
                reason="Estimated input tokens exceed 8000",
                estimated_input_tokens=estimated_tokens,
                needs_coding=is_coding,
                needs_reasoning=needs_reasoning,
                needs_tool_calling=has_tools,
                is_long_context=True
            )
            
        # 3. Complex tasks
        if (is_coding and needs_reasoning) or ("architecture" in content_text) or ("refactor core" in content_text):
            return TaskClassification(
                complexity=TaskComplexity.COMPLEX,
                reason="Task requires architectural reasoning or complex refactoring",
                estimated_input_tokens=estimated_tokens,
                needs_coding=is_coding,
                needs_reasoning=True,
                needs_tool_calling=has_tools
            )
            
        # 4. Simple tasks
        simple_keywords = ["translate", "summarize short", "rewrite", "commit message", "fix typo", "markdown cleanup", "classify text"]
        if any(kw in content_text for kw in simple_keywords) and not has_tools and not is_coding:
            return TaskClassification(
                complexity=TaskComplexity.SIMPLE,
                reason="Task matches simple heuristics (translate, summarize short, etc.)",
                estimated_input_tokens=estimated_tokens,
                needs_coding=False,
                needs_reasoning=False,
                needs_tool_calling=False
            )
            
        # 5. Fallback to standard
        return TaskClassification(
            complexity=TaskComplexity.STANDARD,
            reason="Task does not match special complexity criteria",
            estimated_input_tokens=estimated_tokens,
            needs_coding=is_coding,
            needs_reasoning=needs_reasoning,
            needs_tool_calling=has_tools
        )
