import abc
from typing import Generator, Dict, Any
from ai_gateway.protocols.cap import AgentRequest, AgentResponse

class BaseProvider(abc.ABC):
    """
    Abstract Base Class defining the standard interface for all AI providers.
    """
    
    @property
    @abc.abstractmethod
    def capabilities(self) -> Dict[str, Any]:
        """Returns the capabilities of the provider."""
        pass

    @abc.abstractmethod
    def connect(self) -> bool:
        """Establishes connection or authenticates with the provider."""
        pass

    @abc.abstractmethod
    def chat(self, request: AgentRequest) -> AgentResponse:
        """Processes a chat completion request."""
        pass

    @abc.abstractmethod
    def stream(self, request: AgentRequest) -> Generator[AgentResponse, None, None]:
        """Processes a streaming chat completion request."""
        pass

    @abc.abstractmethod
    def tool_call(self, request: AgentRequest) -> AgentResponse:
        """Processes a request that mandates tool calling."""
        pass

    @abc.abstractmethod
    def health(self) -> Dict[str, Any]:
        """Checks the health and availability of the provider."""
        pass

    @abc.abstractmethod
    def estimate_cost(self, request: AgentRequest) -> float:
        """Estimates the cost of a given request."""
        pass
