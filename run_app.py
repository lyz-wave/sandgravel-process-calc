"""Production launcher for the packaged desktop app."""
import os, sys, traceback, ctypes, time, threading
from pathlib import Path
from datetime import datetime

os.environ["SANDGRAVEL_APP"] = "1"

DESKTOP = Path.home() / "Desktop"
LOG = DESKTOP / "SandGravelCalc_startup.log"

def show_error(title: str, msg: str):
    try:
        ctypes.windll.user32.MessageBoxW(0, msg, title, 0x10)
    except Exception:
        pass

def log(msg: str):
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
    except Exception:
        pass

try:
    log("Starting SandGravelCalc...")

    if getattr(sys, 'frozen', False):
        ROOT = Path(sys._MEIPASS)
        log(f"Frozen mode, MEIPASS={ROOT}")
    else:
        ROOT = Path(__file__).parent
        log(f"Dev mode, ROOT={ROOT}")

    sys.path.insert(0, str(ROOT))

    config_dir = ROOT / "sandgravel_engine" / "config"
    frontend_dir = ROOT / "frontend" / "dist"

    if not config_dir.exists():
        msg = f"Config directory not found:\n{config_dir}"
        log(f"ERROR: {msg}")
        show_error("启动失败", msg)
        sys.exit(1)

    if not (frontend_dir / "index.html").exists():
        msg = f"Frontend index.html not found:\n{frontend_dir}"
        log(f"ERROR: {msg}")
        show_error("启动失败", msg)
        sys.exit(1)

    log("Importing backend...")
    import uvicorn
    from backend.app import app, _app_state as state

    def watchdog(server: uvicorn.Server):
        time.sleep(10)
        while not state["shutdown"]:
            time.sleep(3)
            if time.time() - state["last_hb"] > 30:
                log("Heartbeat timeout (30s), exiting...")
                os._exit(0)
        log("Shutdown signal received, exiting...")
        server.should_exit = True
        time.sleep(0.5)
        os._exit(0)

    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_config=None)
    server = uvicorn.Server(config)
    threading.Thread(target=watchdog, args=(server,), daemon=True).start()

    log("Server starting on http://127.0.0.1:8000")
    server.run()
    log("Server stopped.")

except Exception:
    err = traceback.format_exc()
    log(f"CRASH:\n{err}")
    show_error("砂石工艺计算平台 启动失败", err[:500])
    sys.exit(1)
