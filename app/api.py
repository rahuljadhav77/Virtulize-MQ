from fastapi import FastAPI, HTTPException
from typing import List, Dict
from app.models.service import VirtualService

app = FastAPI(title="MQ Virtualizer Control API")

# This will be injected by the main app
virtualizer = None

@app.get("/services")
async def get_services():
    if not virtualizer:
        return []
    return virtualizer.services

@app.post("/services/{name}/toggle")
async def toggle_service(name: str):
    if not virtualizer:
        raise HTTPException(status_code=500, detail="Virtualizer not initialized")
    
    for svc in virtualizer.services:
        if svc.name == name:
            svc.active = not svc.active
            return {"name": svc.name, "active": svc.active}
            
    raise HTTPException(status_code=404, detail="Service not found")

@app.get("/logs")
async def get_logs():
    # In Phase 3, we will return the interaction logs
    if not virtualizer:
        return []
    return getattr(virtualizer, 'interaction_logs', [])

def start_api(v_instance):
    global virtualizer
    virtualizer = v_instance
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
