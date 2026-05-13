"""Production launcher for the packaged desktop app."""
import os, sys, traceback
from pathlib import Path

os.environ["SANDGRAVEL_APP"] = "1"

# Log errors to temp file for debugging packaged exe
LOG = Path(os.environ.get("TEMP", ".")) / "sandgravel_error.log"

try:
    if getattr(sys, 'frozen', False):
        ROOT = Path(sys._MEIPASS)
    else:
        ROOT = Path(__file__).parent

    sys.path.insert(0, str(ROOT))

    # Verify critical paths
    config_dir = ROOT / "sandgravel_engine" / "config"
    frontend_dir = ROOT / "frontend" / "dist"
    if not config_dir.exists():
        raise FileNotFoundError(f"Config dir not found: {config_dir}")
    if not frontend_dir.exists():
        raise FileNotFoundError(f"Frontend dir not found: {frontend_dir}")

    import uvicorn

    class SuppressLogConfig:
        """Minimal log config for --noconsole PyInstaller builds."""
        def __init__(self): pass
        def __call__(self, *a, **kw): pass

    uvicorn.run(
        "backend.app:app",
        host="127.0.0.1",
        port=8000,
        log_config=None,          # suppress console logging
        access_log=False,
    )

except Exception:
    LOG.write_text(traceback.format_exc(), encoding="utf-8")
    raise
