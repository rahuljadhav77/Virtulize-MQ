import pytest
from app.core.matcher import MessageMatcher
from app.models.service import Rule, MatchCondition, ResponseTemplate

def test_matcher_regex():
    matcher = MessageMatcher()
    rule = Rule(
        name="Test Regex",
        match=[MatchCondition(field="body", type="regex", value="HELLO.*")],
        response=ResponseTemplate(body="WORLD")
    )
    
    msg = {"body": "HELLO THERE"}
    assert matcher.match(msg, [rule]) == rule
    
    msg_no_match = {"body": "BYE"}
    assert matcher.match(msg_no_match, [rule]) is None

def test_matcher_jsonpath():
    matcher = MessageMatcher()
    rule = Rule(
        name="Test JSONPath",
        match=[MatchCondition(field="body", type="jsonpath", key="$.user.id", value="123")],
        response=ResponseTemplate(body="FOUND")
    )
    
    msg = {"body": '{"user": {"id": "123"}}'}
    assert matcher.match(msg, [rule]) == rule
    
    msg_no_match = {"body": '{"user": {"id": "456"}}'}
    assert matcher.match(msg_no_match, [rule]) is None
