from sqlalchemy import Column, String, Boolean, JSON, Integer, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class ServiceEntity(Base):
    __tablename__ = "virtual_services"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    type = Column(String(50), default="ibm_mq")
    input_queue = Column(String(255), nullable=False)
    output_queue = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_stateful = Column(Boolean, default=False)
    config_json = Column(JSON, nullable=False) # Store full Pydantic config
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class InteractionLogEntity(Base):
    __tablename__ = "interaction_logs"

    id = Column(Integer, primary_key=True)
    service_name = Column(String(255), nullable=False)
    request_body = Column(JSON)
    response_body = Column(JSON)
    rule_name = Column(String(255))
    correlation_id = Column(String(255))
    latency_ms = Column(Float)
    timestamp = Column(DateTime, server_default=func.now())
