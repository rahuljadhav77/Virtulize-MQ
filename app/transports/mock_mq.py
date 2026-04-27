import time
import logging
from typing import Callable, Any, Dict, List
from app.transports.base import BaseTransport

logger = logging.getLogger(__name__)

class MockMQTransport(BaseTransport):
    def __init__(self):
        self.queues: Dict[str, List[Any]] = {}
        self.connected = False

    def connect(self):
        logger.info("Mock MQ: Connected.")
        self.connected = True

    def disconnect(self):
        logger.info("Mock MQ: Disconnected.")
        self.connected = False

    def listen(self, queue_name: str, callback: Callable[[Any], None]):
        logger.info(f"Mock MQ: Listening on {queue_name}...")
        while self.connected:
            if queue_name in self.queues and self.queues[queue_name]:
                message = self.queues[queue_name].pop(0)
                logger.info(f"Mock MQ: Received message on {queue_name}: {message}")
                callback(message)
            time.sleep(1)

    def send(self, queue_name: str, message: Any):
        logger.info(f"Mock MQ: Sending message to {queue_name}: {message}")
        if queue_name not in self.queues:
            self.queues[queue_name] = []
        self.queues[queue_name].append(message)

    def inject_message(self, queue_name: str, body: str, correlation_id: str = "123", headers: Dict = None):
        """Helper to simulate an incoming message from the 'outside'."""
        msg = {
            'body': body,
            'correlation_id': correlation_id,
            'headers': headers or {}
        }
        self.send(queue_name, msg)
