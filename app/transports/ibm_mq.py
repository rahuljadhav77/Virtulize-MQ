import logging
try:
    import pymqi
except ImportError:
    pymqi = None

from typing import Callable, Any
from app.transports.base import BaseTransport

logger = logging.getLogger(__name__)

class IBMMQTransport(BaseTransport):
    def __init__(self, queue_manager, channel, host, port):
        self.queue_manager_name = queue_manager
        self.channel = channel
        self.host = host
        self.port = port
        self.qmgr = None

    def connect(self):
        if not pymqi:
            logger.error("pymqi not installed. Cannot connect to IBM MQ.")
            return

        conn_info = f"{self.host}({self.port})"
        logger.info(f"Connecting to MQ Queue Manager: {self.queue_manager_name} at {conn_info}")
        try:
            self.qmgr = pymqi.connect(self.queue_manager_name, self.channel, conn_info)
            logger.info("Successfully connected to IBM MQ.")
        except Exception as e:
            logger.error(f"Failed to connect to IBM MQ: {e}")

    def disconnect(self):
        if self.qmgr:
            self.qmgr.disconnect()
            logger.info("Disconnected from IBM MQ.")

    def listen(self, queue_name: str, callback: Callable[[Any], None]):
        if not self.qmgr:
            logger.error("Not connected to MQ.")
            return

        logger.info(f"Listening on queue: {queue_name}")
        queue = pymqi.Queue(self.qmgr, queue_name)
        
        while True:
            try:
                # Get message with wait
                message_body = queue.get(wait_interval=5000)
                # In a real scenario, you'd extract headers/correlation_id from MQMD
                # This is a simplified wrapper
                msg = {
                    'body': message_body.decode('utf-8'),
                    'correlation_id': 'MQ_CORREL_ID', # Simplified
                    'headers': {}
                }
                callback(msg)
            except pymqi.MQMIError as e:
                if e.comp == pymqi.CMQC.MQCC_FAILED and e.reason == pymqi.CMQC.MQRC_NO_MSG_AVAILABLE:
                    continue
                else:
                    logger.error(f"MQ Error: {e}")
                    break

    def send(self, queue_name: str, message: Any):
        if not self.qmgr:
            logger.error("Not connected to MQ.")
            return

        logger.info(f"Sending message to {queue_name}")
        queue = pymqi.Queue(self.qmgr, queue_name)
        queue.put(message['body'].encode('utf-8'))
        queue.close()
