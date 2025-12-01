import sys
import os
import subprocess
import webbrowser
import time
import requests
from pathlib import Path
from threading import Thread
import pystray
from PIL import Image
import shutil
import psutil

# Add src to path
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from utils.port_finder import find_free_port
from utils.resource_resolver import get_resource_path
from utils.logger import configure_logger, get_logger
from utils.gpu_setup import add_nvidia_dll_path

logger = get_logger(__name__)

def run_streamlit_in_thread(port, app_path):
    """Run Streamlit in a separate thread (for frozen app)."""
    try:
        import streamlit.web.cli as stcli
        
        # Mock sys.argv
        sys.argv = [
            "streamlit",
            "run",
            str(app_path),
            "--server.port", str(port),
            "--server.headless", "true",
            "--global.developmentMode", "false"
        ]
        
        # Monkeypatch signal to avoid "signal only works in main thread" error
        import signal
        import threading
        
        def noop_signal(signum, handler):
            pass
            
        if threading.current_thread() is not threading.main_thread():
            signal.signal = noop_signal
        
        stcli.main()
    except Exception as e:
        logger.error(f"Streamlit thread error: {e}")

def cleanup_temp():
    temp_dir = Path("temp")
    if temp_dir.exists():
        try:
            shutil.rmtree(temp_dir)
            logger.info("Temp directory cleaned.")
        except Exception as e:
            logger.error(f"Failed to clean temp: {e}")

def kill_process_tree(pid):
    try:
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
    except psutil.NoSuchProcess:
        pass

def main():
    configure_logger()
    logger.info("Starting AutoSub-AI Launcher...")
    
    # Setup GPU paths
    add_nvidia_dll_path()
    
    # Cleanup old temp
    cleanup_temp()
    
    # Find free port
    try:
        port = find_free_port()
        logger.info(f"Found free port: {port}")
    except Exception as e:
        logger.error(f"Failed to find free port: {e}")
        sys.exit(1)

    # Resolve app path
    app_path = get_resource_path("src/gui/app.py")
    if not app_path.exists():
        logger.error(f"App file not found: {app_path}")
        sys.exit(1)

    server_url = f"http://localhost:{port}"

    process = None

    if getattr(sys, 'frozen', False):
        # Frozen mode: Run in thread because subprocess with sys.executable is tricky
        logger.info("Running in frozen mode (Thread)...")
        t = Thread(target=run_streamlit_in_thread, args=(port, app_path))
        t.daemon = True
        t.start()
    else:
        # Dev mode: Run in subprocess
        logger.info("Running in dev mode (Subprocess)...")
        cmd = [
            sys.executable,
            "-m", "streamlit",
            "run",
            str(app_path),
            "--server.port", str(port),
            "--server.headless", "true",
            "--global.developmentMode", "false"
        ]
        process = subprocess.Popen(cmd)

    # Wait for server
    logger.info(f"Waiting for server at {server_url}...")
    max_retries = 30
    for i in range(max_retries):
        try:
            requests.get(f"{server_url}/_stcore/health")
            logger.info("Server is ready!")
            break
        except requests.ConnectionError:
            time.sleep(1)
    else:
        logger.error("Server failed to start.")
        if process:
            process.terminate()
        sys.exit(1)

    # Open browser
    webbrowser.open(server_url)
    
    # Tray Icon
    def quit_app():
        logger.info("Quitting...")
        if process:
            kill_process_tree(process.pid)
        
        cleanup_temp()
        sys.exit(0)

    image_path = get_resource_path("assets/tray_icon.png")
    if not image_path.exists():
        logger.warning(f"Tray icon not found at {image_path}")
        # Fallback or exit? Just warn.
    else:
        image = Image.open(image_path)
        
        def on_open_browser(icon, item):
            webbrowser.open(server_url)
            
        def on_open_logs(icon, item):
            log_dir = Path("logs").resolve()
            if sys.platform == "win32":
                os.startfile(str(log_dir))
            else:
                logger.info(f"Logs at: {log_dir}")

        def on_exit(icon, item):
            icon.stop()
            quit_app()

        menu = pystray.Menu(
            pystray.MenuItem("브라우저 열기", on_open_browser, default=True),
            pystray.MenuItem("로그 폴더 열기", on_open_logs),
            pystray.MenuItem("종료", on_exit)
        )
        
        icon = pystray.Icon("AutoSub-AI", image, "AutoSub-AI", menu)
        logger.info("Starting tray icon...")
        icon.run() # Blocks here

    # Fallback if tray icon fails or not used
    try:
        if process:
            process.wait()
        else:
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        quit_app()

if __name__ == "__main__":
    main()
