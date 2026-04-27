from abc import ABC, abstractmethod
from typing import Callable, Any

class BaseTransport(ABC):
    @abstractmethod
    def connect(self):
        """Establish connection to the messaging system."""
        pass

    @abstractmethod
    def disconnect(self):
        """Close connection to the messaging system."""
        pass

    @abstractmethod
    def listen(self, queue_name: str, callback: Callable[[Any], None]):
        """Listen for incoming messages on a specific queue."""
        pass

    @abstractmethod
    def send(self, queue_name: str, message: Any):
        """Send a message to a specific queue."""
        pass
