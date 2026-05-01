import logging
from fastapi import FastAPI
from app.api.router import router as api_router
from app.core.services.runtime import ProductionRuntime
from app.core.services.matcher import AdvancedMatcher
from app.core.services.engine import BehaviorEngine
from app.infrastructure.adapters.redis_state import RedisStateStore
from app.transports.mock_mq import MockMQTransport # Still using mock for demonstration

from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VirtulizeMQ")

app = FastAPI(title="Virtulize MQ Production Platform")

# Initialize components
state_store = RedisStateStore()
matcher = AdvancedMatcher()
engine = BehaviorEngine(state_store=state_store)
transport = MockMQTransport()

runtime = ProductionRuntime(transport, matcher, engine)

app.include_router(api_router, prefix="/api/v1")

# Mount Static UI
import os
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ui_dir = os.path.join(base_dir, "ui")
if os.path.exists(ui_dir):
    app.mount("/ui", StaticFiles(directory=ui_dir, html=True), name="ui")

@app.get("/")
async def root():
    return RedirectResponse(url="/ui/")

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing Virtulize MQ Runtime...")
    transport.connect()
    # In production, we would load services from the DB and start them
    pass

@app.on_event("shutdown")
async def shutdown_event():
    transport.disconnect()
