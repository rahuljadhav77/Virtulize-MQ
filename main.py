import logging
import threading
import time
from app.core.config import ConfigLoader
from app.core.matcher import MessageMatcher
from app.core.engine import ResponseEngine
from app.transports.mock_mq import MockMQTransport

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MQVirtualizer")

class VirtualizerApp:
    def __init__(self, config_path: str):
        self.loader = ConfigLoader(config_path)
        self.matcher = MessageMatcher()
        self.engine = ResponseEngine()
        self.transport = MockMQTransport()  # Using mock for MVP
        self.services = []
        self.interaction_logs = []

    def start(self):
        logger.info("Starting MQ Virtualization Tool...")
        self.services = self.loader.load_services()
        self.transport.connect()

        # Start Control API in a separate thread
        from app.api import start_api
        api_thread = threading.Thread(target=start_api, args=(self,), daemon=True)
        api_thread.start()
        logger.info("Control API started on http://localhost:8000")

        threads = []
        for service in self.services:
            if service.active:
                t = threading.Thread(
                    target=self.transport.listen,
                    args=(service.input_queue, lambda msg, s=service: self.process_message(msg, s)),
                    daemon=True
                )
                t.start()
                threads.append(t)
                logger.info(f"Started virtual service: {service.name} on {service.input_queue}")

        return threads

    def process_message(self, message, service):
        if not service.active:
            return

        logger.info(f"Processing message for service: {service.name}")
        rule = self.matcher.match(message, service.rules)
        
        log_entry = {
            'timestamp': time.time(),
            'service': service.name,
            'request': message,
            'rule': rule.name if rule else None,
            'response': None
        }

        if rule:
            logger.info(f"Matched rule: {rule.name}")
            response = self.engine.generate_response(message, rule)
            
            if response.get('delay_ms', 0) > 0:
                time.sleep(response['delay_ms'] / 1000.0)
            
            self.transport.send(service.output_queue, response)
            log_entry['response'] = response
        else:
            logger.warning(f"No matching rule found for message: {message}")

        self.interaction_logs.append(log_entry)

    def run_simulation(self):
        """Simulate some incoming messages for testing."""
        time.sleep(2)
        logger.info("--- SIMULATION START ---")
        
        # Test Case 1: Match Balance
        self.transport.inject_message("CUSTOMER.REQ", "GET_BALANCE for user 123")
        
        time.sleep(2)
        
        # Test Case 2: Match Approval
        self.transport.inject_message("CUSTOMER.REQ", "Order: orderAmount > 10000")
        
        time.sleep(2)
        
        # Test Case 3: JSONPath + Templating
        self.transport.inject_message("CUSTOMER.REQ", '{"action": "FETCH_ACCOUNT", "account_id": "ACC_888"}')
        
        time.sleep(2)
        
        # Test Case 4: No Match
        self.transport.inject_message("CUSTOMER.REQ", "UNKNOWN MESSAGE")
        
        time.sleep(2)
        logger.info("--- SIMULATION END ---")

if __name__ == "__main__":
    app = VirtualizerApp("config/services.yaml")
    app.start()
    app.run_simulation()
    
    # Keep main thread alive for a bit to see output
    time.sleep(5)
    app.transport.disconnect()
