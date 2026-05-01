import requests
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestPlatform")

BASE_URL = "http://localhost:8000/api/v1"

def test_full_workflow():
    logger.info("Starting Production Platform Test (API Mode)...")
    
    # 1. Load Sample Config
    with open('config/production_sample.json', 'r') as f:
        sample_config = json.load(f)

    # 2. Register Service via API
    logger.info("Registering Virtual Service via API...")
    resp = requests.post(f"{BASE_URL}/services", json=sample_config)
    resp.raise_for_status()
    logger.info("Service registered successfully.")

    time.sleep(1)

    # 3. Simulate High Value Order via API Injection
    logger.info("Injecting HIGH VALUE order...")
    high_value_body = json.dumps({
        "order": {
            "id": "ORD-999",
            "amount": 15000
        }
    })
    requests.post(f"{BASE_URL}/test/inject", params={
        "queue_name": "ORDER.REQ",
        "body": high_value_body,
        "correlation_id": "CORREL-999"
    }).raise_for_status()
    
    logger.info("Waiting for processing (simulated delay 1.5s)...")
    time.sleep(3) 

    # 4. Check Responses via API
    resp = requests.get(f"{BASE_URL}/test/responses", params={"queue_name": "ORDER.RES"})
    responses = resp.json()
    if responses:
        response = responses[0]
        logger.info(f"Received Response for High Value: {response}")
        assert "REQUIRES_APPROVAL" in response['body']
        assert "ORD-999" in response['body']
        logger.info("✅ High Value Order Test Passed.")
    else:
        logger.error("❌ No response received for High Value order!")

    # 5. Simulate Standard Order
    logger.info("Injecting STANDARD order...")
    standard_body = json.dumps({
        "order": {
            "id": "ORD-001",
            "amount": 500
        }
    })
    requests.post(f"{BASE_URL}/test/inject", params={
        "queue_name": "ORDER.REQ",
        "body": standard_body,
        "correlation_id": "CORREL-001"
    }).raise_for_status()
    
    time.sleep(1)

    resp = requests.get(f"{BASE_URL}/test/responses", params={"queue_name": "ORDER.RES"})
    responses = resp.json()
    if responses:
        response = responses[0]
        logger.info(f"Received Response for Standard: {response}")
        assert "CONFIRMED" in response['body']
        logger.info("✅ Standard Order Test Passed.")
    else:
        logger.error("❌ No response received for Standard order!")

    # 6. Verify Metrics
    logger.info("Checking Prometheus Metrics...")
    metrics_resp = requests.get(f"{BASE_URL}/metrics")
    if "mq_virtualizer_messages_total" in metrics_resp.text:
        logger.info("✅ Metrics endpoint is serving data correctly.")
    else:
        logger.warning("❌ Metrics endpoint did not contain expected data.")

    logger.info("Test Workflow Completed.")

if __name__ == "__main__":
    try:
        test_full_workflow()
    except Exception as e:
        logger.error(f"Test failed: {e}")
