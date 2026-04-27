from typing import Any, Dict
import json
from jinja2 import Template
from app.models.service import Rule, ResponseTemplate

class ResponseEngine:
    def __init__(self):
        pass

    def generate_response(self, request_message: Any, rule: Rule) -> Dict[str, Any]:
        """
        Generates a response message based on the matched rule.
        Uses Jinja2 for dynamic templating.
        """
        template = rule.response
        
        # Render the body using Jinja2
        try:
            # We assume message body is JSON for template data, if it's not we still pass the raw dict
            context = {
                'request': request_message,
                'body': request_message.get('body', '')
            }
            # Try to parse body as json to make it easier to access in templates
            try:
                context['json'] = json.loads(request_message.get('body', '{}'))
            except:
                context['json'] = {}

            jinja_template = Template(template.body)
            response_body = jinja_template.render(**context)
        except Exception as e:
            response_body = template.body # Fallback to static
        
        return {
            'body': response_body,
            'headers': template.headers,
            'correlation_id': request_message.get('correlation_id', ''),
            'delay_ms': template.delay_ms
        }
