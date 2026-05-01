import logging
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.api.router import router as api_router
from app.core.services.runtime import ProductionRuntime
from app.core.services.matcher import AdvancedMatcher
from app.core.services.engine import BehaviorEngine
from app.infrastructure.adapters.redis_state import RedisStateStore
from app.transports.mock_mq import MockMQTransport
from app.infrastructure.persistence.models import Base

# --- Configuration ---
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/mq_virtualizer"
# Falling back to sqlite for demo if postgres is not available
DATABASE_URL_SQLITE = "sqlite+aiosqlite:///./virtulize.db"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VirtulizeMQ")

# --- Database Setup ---
engine_db = create_async_engine(DATABASE_URL_SQLITE, echo=False)
async_session = sessionmaker(engine_db, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with async_session() as session:
        yield session

# --- Core App Initialization ---
app = FastAPI(title="Virtulize MQ Enterprise Platform")

# Components
state_store = RedisStateStore()
matcher = AdvancedMatcher()
behavior_engine = BehaviorEngine(state_store=state_store)
transport = MockMQTransport()

# Runtime Engine
runtime = ProductionRuntime(transport, matcher, behavior_engine)

# API Routes
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
    logger.info("Initializing Enterprise Virtulize MQ Runtime...")
    
    # Connect transport
    transport.connect()
    
    # Create tables if using sqlite (for enterprise we use Alembic)
    async with engine_db.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database initialized.")

@app.on_event("shutdown")
async def shutdown_event():
    await engine_db.dispose()
    logger.info("Platform shutting down.")
