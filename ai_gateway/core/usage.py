import os
import json
import logging
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class UsageEvent(BaseModel):
    request_id: str
    timestamp: float
    provider: Optional[str] = None
    model: Optional[str] = None
    resolved_model: Optional[str] = None
    input_tokens: Optional[int] = None
    cached_input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    estimated_cost: Optional[float] = None
    input_cost: Optional[float] = None
    cached_input_cost: Optional[float] = None
    output_cost: Optional[float] = None
    latency_ms: Optional[float] = None
    status: str
    error_type: Optional[str] = None
    error_code: Optional[str] = None
    fallback_count: int = 0
    retry_count: int = 0
    cooldown_triggered: bool = False
    route_policy: Optional[str] = None
    stream: bool = False

class UsageLedger(ABC):
    @abstractmethod
    def record(self, event: UsageEvent) -> None:
        pass

class InMemoryUsageLedger(UsageLedger):
    def __init__(self, statistics_updater: Optional[Any] = None):
        self.events: List[UsageEvent] = []
        if statistics_updater is None:
            from ai_gateway.core.provider_statistics import get_global_statistics_updater
            statistics_updater = get_global_statistics_updater()
        self.statistics_updater = statistics_updater

    def record(self, event: UsageEvent) -> None:
        self.events.append(event)
        try:
            self.statistics_updater.update(event)
        except Exception as e:
            logger.error(f"Failed to update statistics: {e}")

class JsonlUsageLedger(UsageLedger):
    def __init__(self, file_path: str = "logs/usage.jsonl", statistics_updater: Optional[Any] = None):
        self.file_path = file_path
        if statistics_updater is None:
            from ai_gateway.core.provider_statistics import get_global_statistics_updater
            statistics_updater = get_global_statistics_updater()
        self.statistics_updater = statistics_updater
        os.makedirs(os.path.dirname(os.path.abspath(self.file_path)), exist_ok=True)

    def record(self, event: UsageEvent) -> None:
        try:
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(event.model_dump_json() + "\n")
            try:
                self.statistics_updater.update(event)
            except Exception as e:
                logger.error(f"Failed to update statistics: {e}")
        except Exception as e:
            logger.error(f"Failed to record usage event: {e}")
