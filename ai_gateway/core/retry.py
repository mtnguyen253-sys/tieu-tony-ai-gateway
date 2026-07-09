import logging
from abc import ABC, abstractmethod
from typing import Callable, Tuple, Type

from ai_gateway.protocols.cap import AgentResponse
from ai_gateway.core.executor import (
    TimeoutException,
    RateLimitException,
    ProviderUnavailableException,
    UnknownProviderException
)

logger = logging.getLogger(__name__)

class AuthenticationException(Exception):
    pass

class RetryStrategy(ABC):
    """Abstract base class for retry strategies."""
    
    @abstractmethod
    def execute(self, operation: Callable[[], AgentResponse]) -> AgentResponse:
        """Executes the operation according to the retry strategy."""
        pass

class NoRetryStrategy(RetryStrategy):
    """Executes the operation exactly once, without retries."""
    
    def execute(self, operation: Callable[[], AgentResponse]) -> AgentResponse:
        return operation()

class FixedRetryStrategy(RetryStrategy):
    """Retries the operation a fixed number of times for specific exceptions."""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.retryable_exceptions: Tuple[Type[Exception], ...] = (TimeoutException,)
        
    def execute(self, operation: Callable[[], AgentResponse]) -> AgentResponse:
        attempts = 0
        while True:
            try:
                return operation()
            except self.retryable_exceptions as e:
                attempts += 1
                if attempts > self.max_retries:
                    logger.error(f"Max retries ({self.max_retries}) reached. Failing.")
                    raise
                logger.warning(f"Operation failed with {type(e).__name__}. Retrying {attempts}/{self.max_retries}...")
            except Exception as e:
                logger.error(f"Operation failed with non-retryable exception {type(e).__name__}. Re-raising.")
                raise
