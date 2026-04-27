# MQ Service Virtualization Tool

A lightweight, modular tool for virtualizing IBM MQ services. Similar to IBM DevOps Test Virtualization, this tool allows you to intercept MQ messages and return simulated responses based on configurable rules.

## 🚀 Features

- **Protocol Agnostic Core**: Modular transport layer supports Mock MQ (for testing) and real IBM MQ.
- **Advanced Matching**: Match messages using:
  - Exact string match
  - Regular Expressions (Regex)
  - JSONPath
- **Dynamic Responses**:
  - Static response bodies
  - Jinja2 Templating (inject request data into responses)
  - Configurable delays (simulation of latency)
- **Control API**: REST API (FastAPI) to monitor services and toggle them at runtime.
- **Interaction Logging**: Track every request-response pair for audit and debugging.

## 🛠️ Getting Started

### Prerequisites

- Python 3.8+
- (Optional) IBM MQ Client and `pymqi` for real MQ connectivity.

### Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the MVP / Simulation

To run the tool with the `MockTransport` and see the simulation in action:

```bash
python main.py
```

### Configuration

Virtual services are defined in `config/services.yaml`. Example:

```yaml
services:
  - name: "Customer Service"
    input_queue: "CUSTOMER.REQ"
    output_queue: "CUSTOMER.RES"
    rules:
      - name: "Get Balance"
        match:
          - field: "body"
            type: "regex"
            value: "GET_BALANCE"
        response:
          body: '{"status": "SUCCESS", "balance": 5000}'
          delay_ms: 100
```

## 🌐 Control API

Once running, the API is available at `http://localhost:8000`.

- `GET /services`: List all virtual services and their status.
- `POST /services/{name}/toggle`: Enable/Disable a service.
- `GET /logs`: View interaction history.

## 📂 Project Structure

- `app/core/`: Core logic (Matcher, Engine, Config Loader).
- `app/transports/`: Transport implementations (Mock, IBM MQ).
- `app/models/`: Data models for services and rules.
- `app/api.py`: FastAPI implementation.
- `main.py`: Application entry point.
- `config/`: YAML configuration files.
