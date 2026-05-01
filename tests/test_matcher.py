import pytest
from app.core.services.matcher import AdvancedMatcher
from app.core.domain.models import VirtualRule, MatchCondition, ResponseDefinition, MatchOperator

def test_matcher_regex():
    matcher = AdvancedMatcher()
    rule = VirtualRule(
        name="Test Regex",
        conditions=[MatchCondition(field="body", operator=MatchOperator.REGEX, value="HELLO.*")],
        response=ResponseDefinition(template="WORLD")
    )
    
    msg = {"body": "HELLO THERE"}
    assert matcher.match(msg, [rule]) == rule
    
    msg_no_match = {"body": "BYE"}
    assert matcher.match(msg_no_match, [rule]) is None

def test_matcher_jsonpath():
    matcher = AdvancedMatcher()
    rule = VirtualRule(
        name="Test JSONPath",
        conditions=[MatchCondition(field="body", operator=MatchOperator.JSONPATH, key="$.user.id", value="123")],
        response=ResponseDefinition(template="FOUND")
    )
    
    msg = {"body": '{"user": {"id": "123"}}'}
    assert matcher.match(msg, [rule]) == rule
    
    msg_no_match = {"body": '{"user": {"id": "456"}}'}
    assert matcher.match(msg_no_match, [rule]) is None
