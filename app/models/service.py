from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class MatchCondition:
    field: str  # 'body', 'header', 'correlation_id'
    type: str   # 'equals', 'regex', 'jsonpath', 'xpath'
    value: str
    key: Optional[str] = None  # Specific header key if field is 'header'

@dataclass
class ResponseTemplate:
    body: str
    headers: Dict[str, str] = field(default_factory=dict)
    delay_ms: int = 0

@dataclass
class Rule:
    name: str
    match: List[MatchCondition]
    response: ResponseTemplate

@dataclass
class VirtualService:
    name: str
    input_queue: str
    output_queue: str
    rules: List[Rule]
    active: bool = True
