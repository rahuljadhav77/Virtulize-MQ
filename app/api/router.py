from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from app.core.domain.models import VirtualServiceConfig
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

router = APIRouter()

# This would normally use a DB Repository
services_store: Dict[str, VirtualServiceConfig] = {}

@router.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@router.get("/services", response_model=List[VirtualServiceConfig])
async def list_services():
    return list(services_store.values())

@router.post("/services")
async def create_service(config: VirtualServiceConfig):
    services_store[config.service_name] = config
    from app.main import runtime
    runtime.run_service(config)
    return {"status": "created", "service": config.service_name}

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
