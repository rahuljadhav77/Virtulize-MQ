from enum import Enum
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

class MatchOperator(str, Enum):
    EQUALS = "equals"
    REGEX = "regex"
    JSONPATH = "jsonpath"
    XPATH = "xpath"
    GT = "gt"
    LT = "lt"
    CONTAINS = "contains"

class LogicalOperator(str, Enum):
    AND = "AND"
    OR = "OR"

class MatchCondition(BaseModel):
    field: str  # 'body', 'header', 'correlation_id'
    operator: MatchOperator
    value: Any
    key: Optional[str] = None  # JSONPath or XPath or Header Name
    logical_op: LogicalOperator = LogicalOperator.AND

class ResponseDefinition(BaseModel):
    template: str
    headers: Dict[str, str] = {}
    delay_ms: int = 0
    status_code: Optional[str] = None
    state_updates: Dict[str, Any] = {}  # Updates for Redis state

class VirtualRule(BaseModel):
    name: str
    priority: int = 100
    conditions: List[MatchCondition]
    response: ResponseDefinition
    state_required: Dict[str, Any] = {}  # Requirements from Redis state

class ServiceType(str, Enum):
    IBM_MQ = "ibm_mq"
    KAFKA = "kafka"
    RABBITMQ = "rabbitmq"

class VirtualServiceConfig(BaseModel):
    service_name: str
    service_type: ServiceType = ServiceType.IBM_MQ
    input_queue: str
    output_queue: str
    active: bool = True
    rules: List[VirtualRule]
    stateful: bool = False
    recording_enabled: bool = False

class InteractionLog(BaseModel):
    id: str
    timestamp: float
    service_name: str
    request_body: str
    request_headers: Dict[str, str]
    correlation_id: str
    matched_rule: Optional[str]
    response_body: Optional[str]
    latency_ms: float
