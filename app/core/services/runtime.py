import time
import threading
import uuid
import logging
from typing import List, Dict, Any
from app.core.domain.models import VirtualServiceConfig
from app.core.services.matcher import AdvancedMatcher
from app.core.services.engine import BehaviorEngine
from app.core.services.observability import ObservabilityService
from app.transports.base import BaseTransport

logger = logging.getLogger(__name__)

class ProductionRuntime:
    def __init__(self, transport: BaseTransport, matcher: AdvancedMatcher, engine: BehaviorEngine):
        self.transport = transport
        self.matcher = matcher
        self.engine = engine
        self.active_services: Dict[str, threading.Thread] = {}

    def run_service(self, config: VirtualServiceConfig):
        if not config.active:
            return

        def listener_loop():
            self.transport.listen(config.input_queue, lambda msg: self._handle_message(msg, config))

        t = threading.Thread(target=listener_loop, daemon=True)
        t.start()
        self.active_services[config.service_name] = t
        logger.info(f"Production runtime started for service: {config.service_name}")

    def _handle_message(self, message: Dict[str, Any], config: VirtualServiceConfig):
        start_time = time.time()
        
        try:
            # 1. Matching
            match_start = time.time()
            # Session ID could be correlation ID or a specific header
            session_id = message.get('correlation_id', 'default')
            
            # Fetch state for stateful matching
            current_state = {}
            if config.stateful and self.engine.state_store:
                current_state = self.engine.state_store.get_state(session_id)

            rule = self.matcher.match(message, config.rules, current_state)
            ObservabilityService.record_match_latency(config.service_name, time.time() - match_start)

            if rule:
                # 2. Behavior & Response Building
                response = self.engine.generate_response(message, rule, session_id if config.stateful else None)
                
                # 3. Delay simulation
                if response.get('delay_ms', 0) > 0:
                    time.sleep(response['delay_ms'] / 1000.0)
                
                # 4. Sending
                self.transport.send(config.output_queue, response)
                
                # 5. Logging & Metrics
                ObservabilityService.log_interaction(
                    config.service_name, message, response, rule.name, time.time() - start_time
                )
            else:
                logger.warning(f"No match for message in service {config.service_name}")
                ObservabilityService.log_interaction(
                    config.service_name, message, {}, None, time.time() - start_time
                )
        except Exception as e:
            logger.error(f"Critical error in runtime for {config.service_name}: {e}")
