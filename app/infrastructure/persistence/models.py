from sqlalchemy import Column, Integer, String, Boolean, JSON, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class ServiceDB(Base):
    __tablename__ = "virtual_services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    service_type = Column(String) # ibm_mq, kafka, etc.
    input_queue = Column(String)
    output_queue = Column(String)
    active = Column(Boolean, default=True)
    stateful = Column(Boolean, default=False)
    recording_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    rules = relationship("RuleDB", back_populates="service", cascade="all, delete-orphan")

class RuleDB(Base):
    __tablename__ = "service_rules"

    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("virtual_services.id"))
    name = Column(String)
    priority = Column(Integer, default=100)
    match_conditions = Column(JSON) # Serialized list of conditions
    response_definition = Column(JSON) # Serialized response template
    state_required = Column(JSON)
    
    service = relationship("ServiceDB", back_populates="rules")

class InteractionLogDB(Base):
    __tablename__ = "interaction_logs"

    id = Column(String, primary_key=True)
    timestamp = Column(Float)
    service_name = Column(String, index=True)
    request_body = Column(String)
    request_headers = Column(JSON)
    correlation_id = Column(String, index=True)
    matched_rule = Column(String)
    response_body = Column(String)
    latency_ms = Column(Float)
