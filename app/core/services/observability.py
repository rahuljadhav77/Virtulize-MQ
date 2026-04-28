import structlog
import time
from prometheus_client import Counter, Histogram, Summary

# Prometheus Metrics
MESSAGE_COUNT = Counter('mq_virtualizer_messages_total', 'Total messages processed', ['service', 'status'])
PROCESSING_TIME = Histogram('mq_virtualizer_processing_seconds', 'Time spent processing message', ['service'])
MATCH_LATENCY = Summary('mq_virtualizer_match_latency_seconds', 'Latency of matching engine', ['service'])

# Structured Logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()

class ObservabilityService:
    @staticmethod
    def log_interaction(service_name: str, request: dict, response: dict, rule_name: str, latency: float):
        logger.info(
            "mq_interaction",
            service=service_name,
            rule=rule_name,
            latency_ms=latency * 1000,
            correlation_id=request.get('correlation_id'),
            status="success" if rule_name else "no_match"
        )
        
        status = "success" if rule_name else "no_match"
        MESSAGE_COUNT.labels(service=service_name, status=status).inc()
        PROCESSING_TIME.labels(service=service_name).observe(latency)

    @staticmethod
    def record_match_latency(service_name: str, latency: float):
        MATCH_LATENCY.labels(service=service_name).observe(latency)
