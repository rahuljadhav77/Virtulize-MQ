import json
import time
import uuid
import logging
from typing import Any, Dict, Optional
from jinja2 import Environment, FileSystemLoader, BaseLoader, Template
from app.core.domain.models import VirtualRule, ResponseDefinition

logger = logging.getLogger(__name__)

class BehaviorEngine:
    def __init__(self, state_store=None):
        self.state_store = state_store  # Redis adapter
        self.env = Environment(loader=BaseLoader())
        # Add custom filters/globals for templates
        self.env.globals.update({
            'now': lambda: int(time.time()),
            'uuid': lambda: str(uuid.uuid4())
        })
        self.env.filters['format_time'] = lambda t, fmt: time.strftime(fmt, time.localtime(t))

    def generate_response(self, request_msg: Dict[str, Any], rule: VirtualRule, session_id: str = None) -> Dict[str, Any]:
        resp_def = rule.response
        
        # 1. Fetch current state if stateful
        current_state = {}
        if session_id and self.state_store:
            current_state = self.state_store.get_state(session_id)

        # 2. Build context for template
        context = {
            'request': request_msg,
            'headers': request_msg.get('headers', {}),
            'body': request_msg.get('body', ''),
            'state': current_state,
            'correlation_id': request_msg.get('correlation_id', '')
        }
        
        # Try to parse body as JSON for easy access
        try:
            context['json'] = json.loads(request_msg.get('body', '{}'))
        except:
            context['json'] = {}

        # 3. Render body template
        try:
            template = self.env.from_string(resp_def.template)
            rendered_body = template.render(**context)
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            rendered_body = resp_def.template

        # 4. Handle State Updates
        if session_id and self.state_store and resp_def.state_updates:
            # We can also render state updates if they contain templates
            final_updates = {}
            for k, v in resp_def.state_updates.items():
                if isinstance(v, str) and "{{" in v:
                    final_updates[k] = self.env.from_string(v).render(**context)
                else:
                    final_updates[k] = v
            self.state_store.update_state(session_id, final_updates)

        return {
            'body': rendered_body,
            'headers': resp_def.headers,
            'correlation_id': request_msg.get('correlation_id', ''),
            'delay_ms': resp_def.delay_ms
        }
