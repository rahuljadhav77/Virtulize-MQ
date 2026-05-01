from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from app.core.domain.models import VirtualServiceConfig, InteractionLog
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.persistence.repository import ServiceRepository

router = APIRouter()

# Dependency for DB Session
async def get_db_session():
    from app.main import async_session
    async with async_session() as session:
        yield session

@router.get("/logs")
async def get_logs(limit: int = 50):
    from app.core.services.observability import RECENT_LOGS
    return RECENT_LOGS[-limit:]

@router.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@router.get("/services")
async def get_services(db: AsyncSession = Depends(get_db_session)):
    repo = ServiceRepository(db)
    return await repo.get_all_services()

@router.post("/services")
async def create_service(config_data: dict, db: AsyncSession = Depends(get_db_session)):
    # Flexible Parser logic (kept for ease of use)
    if "rules" in config_data:
        for rule in config_data["rules"]:
            if "rule_name" in rule: rule["name"] = rule.pop("rule_name")
            if "condition" in rule:
                cond = rule.pop("condition")
                if "==" in cond:
                    p = cond.split("==")
                    rule["conditions"] = [{"field": "body", "operator": "equals", "key": f"$.{p[0].strip()}", "value": p[1].strip().strip("'")}]
                else:
                    rule["conditions"] = [{"field": "body", "operator": "contains", "value": cond}]
            if "action" in rule:
                rule["response"] = {"template": rule.pop("action").replace("respond_with:", "").strip().strip("'")}

    try:
        config = VirtualServiceConfig(**config_data)
        repo = ServiceRepository(db)
        await repo.save_service(config)
        
        # Start in runtime
        from app.main import runtime
        runtime.run_service(config)
        
        return {"status": "created", "service": config.service_name}
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.get("/services/{name}")
async def get_service(name: str, db: AsyncSession = Depends(get_db_session)):
    repo = ServiceRepository(db)
    service = await repo.get_service_by_name(name)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@router.delete("/services/{name}")
async def delete_service(name: str, db: AsyncSession = Depends(get_db_session)):
    repo = ServiceRepository(db)
    await repo.delete_service(name)
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
