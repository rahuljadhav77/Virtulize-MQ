import re
import json
import logging
from typing import Any, Optional, List
from app.models.service import MatchCondition, Rule

logger = logging.getLogger(__name__)

class MessageMatcher:
    def __init__(self):
        pass

    def match(self, message: Any, rules: List[Rule]) -> Optional[Rule]:
        """
        Matches an incoming message against a list of rules.
        Returns the first matching rule or None.
        """
        for rule in rules:
            if self._rule_matches(message, rule):
                return rule
        return None

    def _rule_matches(self, message: Any, rule: Rule) -> bool:
        # For simplicity in Phase 1, we assume message is a dict-like object
        # with 'body', 'headers', and 'correlation_id'.
        
        for condition in rule.match:
            if not self._condition_matches(message, condition):
                return False
        return True

    def _condition_matches(self, message: Any, condition: MatchCondition) -> bool:
        value_to_check = ""
        
        if condition.field == 'body':
            value_to_check = message.get('body', '')
        elif condition.field == 'correlation_id':
            value_to_check = message.get('correlation_id', '')
        elif condition.field == 'header':
            if condition.key:
                value_to_check = message.get('headers', {}).get(condition.key, '')
            else:
                return False
        
        if condition.type == 'equals':
            return str(value_to_check) == str(condition.value)
        elif condition.type == 'regex':
            return bool(re.search(condition.value, str(value_to_check)))
        elif condition.type == 'jsonpath':
            try:
                from jsonpath_ng import parse
                json_data = json.loads(value_to_check)
                jsonpath_expr = parse(condition.key)  # In JSONPath mode, 'key' is the path
                matches = jsonpath_expr.find(json_data)
                if matches:
                    # Check if any match equals the condition value
                    return any(str(m.value) == str(condition.value) for m in matches)
            except Exception as e:
                logger.error(f"Error in JSONPath matching: {e}")
                return False
        elif condition.type == 'xpath':
            # XPath matching can be added here
            return False
            
        return False
