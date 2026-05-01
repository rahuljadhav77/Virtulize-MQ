import re
import json
import logging
from typing import List, Optional, Any, Dict
from lxml import etree
from app.core.domain.models import VirtualRule, MatchCondition, MatchOperator, LogicalOperator

logger = logging.getLogger(__name__)

class AdvancedMatcher:
    def match(self, message: Dict[str, Any], rules: List[VirtualRule], current_state: Dict[str, Any] = None) -> Optional[VirtualRule]:
        # Sort rules by priority (lower number = higher priority)
        sorted_rules = sorted(rules, key=lambda x: x.priority)
        
        for rule in sorted_rules:
            if self._rule_matches(message, rule, current_state):
                return rule
        return None

    def _rule_matches(self, message: Dict[str, Any], rule: VirtualRule, current_state: Dict[str, Any]) -> bool:
        # Check state requirements first if applicable
        if rule.state_required:
            if not current_state: return False
            for k, v in rule.state_required.items():
                if current_state.get(k) != v: return False

        if not rule.conditions:
            return True

        # Evaluate conditions based on logical operators
        # For simplicity, we implement a flat list with AND/OR logic
        # Current implementation: If ANY condition is OR and matches, or if all AND match.
        # Better: Grouping logic. Here we do a sequential evaluation.
        
        results = [self._evaluate_condition(message, c) for c in rule.conditions]
        
        # Simple implementation: All must match (AND) unless specified otherwise? 
        # Let's use a more robust logic:
        match_final = True
        for i, cond in enumerate(rule.conditions):
            res = results[i]
            if i == 0:
                match_final = res
            else:
                if cond.logical_op == LogicalOperator.OR:
                    match_final = match_final or res
                else:
                    match_final = match_final and res
        
        return match_final

    def _evaluate_condition(self, message: Dict[str, Any], condition: MatchCondition) -> bool:
        try:
            target_value = self._get_value_from_msg(message, condition)
            if target_value is None: return False

            op = condition.operator
            expected = condition.value

            if op == MatchOperator.EQUALS:
                return str(target_value) == str(expected)
            elif op == MatchOperator.REGEX:
                return bool(re.search(str(expected), str(target_value)))
            elif op == MatchOperator.GT:
                return float(target_value) > float(expected)
            elif op == MatchOperator.LT:
                return float(target_value) < float(expected)
            elif op == MatchOperator.CONTAINS:
                return str(expected) in str(target_value)
            elif op == MatchOperator.JSONPATH:
                return str(target_value) == str(expected)
            elif op == MatchOperator.XPATH:
                return self._evaluate_xpath(str(target_value), condition)
                
            return False
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False

    def _evaluate_xpath(self, xml_str: str, condition: MatchCondition) -> bool:
        try:
            tree = etree.fromstring(xml_str.encode('utf-8'))
            results = tree.xpath(condition.key)
            if not results:
                return False
            # Check if any result matches the value
            return any(str(r.text).strip() == str(condition.value).strip() if hasattr(r, 'text') else str(r) == str(condition.value) for r in results)
        except Exception:
            return False

    def _get_value_from_msg(self, message: Dict[str, Any], condition: MatchCondition) -> Any:
        field_val = message.get(condition.field, "")
        
        if condition.key and str(condition.key).startswith('$'):
            try:
                json_data = json.loads(field_val)
                jsonpath_expr = parse(condition.key)
                matches = jsonpath_expr.find(json_data)
                return matches[0].value if matches else None
            except:
                return None
        
        if condition.operator == MatchOperator.XPATH and condition.key:
            try:
                root = etree.fromstring(field_val.encode())
                results = root.xpath(condition.key)
                return results[0] if results else None
            except:
                return None

        if condition.field == 'header' and condition.key:
            return message.get('headers', {}).get(condition.key)
            
        return field_val
