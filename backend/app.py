import sys, os, webbrowser, threading
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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


# ── Static file serving for packaged app ──────────────────
if getattr(sys, 'frozen', False):
    _ROOT = Path(sys._MEIPASS)
else:
    _ROOT = Path(__file__).parent.parent
_FRONTEND_DIST = _ROOT / "frontend" / "dist"
if _FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(_FRONTEND_DIST), html=True), name="static")


# ── Auto-open browser (suppressed in dev mode) ────────────
def _open_browser():
    import time
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:8000")

if os.environ.get("SANDGRAVEL_APP"):
    threading.Thread(target=_open_browser, daemon=True).start()
