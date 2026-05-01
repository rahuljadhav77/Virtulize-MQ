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

# Global buffer for UI real-time updates
RECENT_LOGS = []

class ObservabilityService:
    @staticmethod
    def log_interaction(service_name: str, request: dict, response: dict, rule_name: str, latency: float):
        log_entry = {
            "timestamp": time.time(),
            "service": service_name,
            "rule": rule_name or "NO_MATCH",
            "latency_ms": round(latency * 1000, 2),
            "correlation_id": request.get('correlation_id'),
            "request_preview": str(request.get('body', ''))[:100],
            "response_preview": str(response.get('body', ''))[:100]
        }
        
        RECENT_LOGS.append(log_entry)
        if len(RECENT_LOGS) > 100: RECENT_LOGS.pop(0)

        logger.info(
            "mq_interaction",
            **log_entry
        )
        
        status = "success" if rule_name else "no_match"
        MESSAGE_COUNT.labels(service=service_name, status=status).inc()
        PROCESSING_TIME.labels(service=service_name).observe(latency)

    @staticmethod
    def record_match_latency(service_name: str, latency: float):
        MATCH_LATENCY.labels(service=service_name).observe(latency)
