# Virtulize MQ - Production-Grade MQ Service Virtualization Platform

A scalable, configuration-driven backend system for simulating IBM MQ and other messaging services. Designed for enterprise testing environments.

## 📐 Architecture

The platform follows Clean Architecture principles:
- **Domain**: Pydantic models for Rules, Services, and Matchers.
- **Application**: Runtime Engine, Behavior Logic, and Matcher Services.
- **Infrastructure**: Adapters for IBM MQ (via pymqi), Redis (State), and PostgreSQL (Persistence).
- **Control Plane**: FastAPI REST API with Prometheus metrics integration.

## 🚀 Key Features

- **Advanced Matcher**: Support for JSONPath, XPath, Regex, and Priority-based rules with logical operators (AND/OR).
- **Stateful Virtualization**: Session-based state management using Redis.
- **Dynamic Response Builder**: Jinja2 templating with request field injection and helper functions (`now()`, `uuid()`).
- **Observability**: Structured JSON logging and Prometheus metrics out of the box.
- **Container Ready**: Docker and Docker-Compose support for rapid deployment.

## 🛠️ Quick Start

### 1. Local Development
```bash
pip install -r requirements.txt
python -m app.main
```

### 2. Docker Deployment
```bash
docker-compose up --build
```

## 🌐 API Endpoints

- `GET /api/v1/services`: List virtual services.
- `POST /api/v1/services`: Register a new virtual service.
- `GET /api/v1/metrics`: Prometheus metrics.

## 📂 Project Structure

- `app/core/`: Domain models and business logic.
- `app/infrastructure/`: Database and message broker adapters.
- `app/api/`: REST API controllers.
- `docker/`: Deployment manifests.
- `config/`: Sample service definitions.

## 🧾 Sample Rule Definition

```json
{
  "name": "High Value Order",
  "priority": 1,
  "conditions": [
    {
      "field": "body",
      "operator": "gt",
      "key": "$.order.amount",
      "value": 10000
    }
  ],
  "response": {
    "template": "{\"status\": \"PENDING_APPROVAL\", \"id\": \"{{ json.order.id }}\"}",
    "delay_ms": 1500
  }
}
```
