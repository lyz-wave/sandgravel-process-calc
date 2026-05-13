import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="砂石加工系统工艺计算平台", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

from backend.api import balance, equipment, screening, io
app.include_router(balance.router, prefix="/api")
app.include_router(equipment.router, prefix="/api")
app.include_router(screening.router, prefix="/api")
app.include_router(io.router, prefix="/api")


@app.get("/api/options")
async def get_options():
    from sandgravel_engine.io import load_yaml_config
    return {
        "configs": ["option1", "option2"],
        "equipment_types": ["jaw_crusher", "cone_crusher", "vsi", "screen", "sand_recovery"],
    }
