import redis
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RedisStateStore:
    def __init__(self, host='localhost', port=6379, db=0):
        try:
            self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
            self.client.ping()
            logger.info("Connected to Redis for state management.")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None

    def get_state(self, session_id: str) -> Dict[str, Any]:
        if not self.client: return {}
        state_data = self.client.get(f"state:{session_id}")
        return json.loads(state_data) if state_data else {}

    def update_state(self, session_id: str, updates: Dict[str, Any]):
        if not self.client: return
        current = self.get_state(session_id)
        current.update(updates)
        self.client.set(f"state:{session_id}", json.dumps(current), ex=3600) # 1 hour TTL
