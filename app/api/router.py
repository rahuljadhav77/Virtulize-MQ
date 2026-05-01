from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from app.core.domain.models import VirtualServiceConfig, InteractionLog
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

router = APIRouter()

# In-memory storage for current session
services_store: Dict[str, VirtualServiceConfig] = {}

@router.get("/logs")
async def get_logs(limit: int = 50):
    from app.core.services.observability import RECENT_LOGS
    return RECENT_LOGS[-limit:]

@router.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@router.get("/services", response_model=List[VirtualServiceConfig])
async def list_services():
    return list(services_store.values())

@router.post("/services")
async def create_service(config_data: dict):
    # Flexible Parser: Handle simplified JSON format provided by users
    if "rules" in config_data:
        for i, rule in enumerate(config_data["rules"]):
            # Map rule_name -> name
            if "rule_name" in rule and "name" not in rule:
                rule["name"] = rule.pop("rule_name")
            
            # Map condition (string) -> conditions (list)
            if "condition" in rule and "conditions" not in rule:
                cond_str = rule.pop("condition")
                # Basic parser for simple "field == 'value'" or "field > value"
                if "==" in cond_str:
                    parts = cond_str.split("==")
                    field_name = parts[0].strip()
                    value = parts[1].strip().strip("'").strip('"')
                    rule["conditions"] = [{
                        "field": "body", 
                        "operator": "equals", 
                        "key": f"$.{field_name}", 
                        "value": value
                    }]
                elif ">" in cond_str:
                    parts = cond_str.split(">")
                    field_name = parts[0].strip()
                    value = float(parts[1].strip())
                    rule["conditions"] = [{
                        "field": "body", 
                        "operator": "gt", 
                        "key": f"$.{field_name}", 
                        "value": value
                    }]
                else:
                    rule["conditions"] = [{"field": "body", "operator": "contains", "value": cond_str}]

            # Map action (string) -> response (object)
            if "action" in rule and "response" not in rule:
                action_str = rule.pop("action")
                template = action_str.replace("respond_with:", "").strip().strip("'").strip('"')
                rule["response"] = {"template": template}

    # Validate with Pydantic after conversion
    try:
        config = VirtualServiceConfig(**config_data)
        services_store[config.service_name] = config
        from app.main import runtime
        runtime.run_service(config)
        return {"status": "created", "service": config.service_name}
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.get("/services/{name}")
async def get_service(name: str):
    if name not in services_store:
        raise HTTPException(status_code=404, detail="Service not found")
    return services_store[name]

@router.delete("/services/{name}")
async def delete_service(name: str):
    if name in services_store:
        del services_store[name]
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Service not found")

@router.post("/test/inject")
async def inject_test_message(queue_name: str, body: str, correlation_id: str = "test-correl"):
    from app.main import transport
    transport.inject_message(queue_name, body, correlation_id=correlation_id)
    return {"status": "injected"}

@router.get("/test/responses")
async def get_test_responses(queue_name: str):
    from app.main import transport
    if queue_name in transport.queues:
        msgs = transport.queues[queue_name]
        transport.queues[queue_name] = [] # Clear after reading
        return msgs
    return []
