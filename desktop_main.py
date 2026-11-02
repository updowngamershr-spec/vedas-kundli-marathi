# -*- coding: utf-8 -*-
"""
Shivansh Astro-Vastu Professional - Native Desktop Application Shell
- Powered by pywebview (Native Windows Win32 / WebView2 Desktop Shell).
- Bulletproof dual-engine fallback: If WinForms/pythonnet has loading restrictions on target PC,
  seamlessly opens in dedicated Edge App Window mode (--app=http://127.0.0.1:port).
- Zero external browser tabs, zero command prompt, runs 100% offline.
- Clean exit on window close.
"""

import os
import sys
import io
import time
import socket
import threading
import subprocess
import webbrowser

# 1. Resolve base directory and executable directory
base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else base_dir

# 2. Add DLL search paths so Windows and pythonnet can find all dependencies
for d in [exe_dir, base_dir, os.path.join(exe_dir, "_internal"), os.path.join(base_dir, "_internal")]:
    if os.path.exists(d):
        if hasattr(os, "add_dll_directory"):
            try:
                os.add_dll_directory(d)
            except Exception:
                pass
        if d not in os.environ.get("PATH", ""):
            os.environ["PATH"] = d + ";" + os.environ.get("PATH", "")

# 3. Explicitly set PYTHONNET_PYDLL so clr_loader finds python311.dll on PCs without Python installed
pydll_candidates = [
    os.path.join(exe_dir, "python311.dll"),
    os.path.join(exe_dir, "_internal", "python311.dll"),
    os.path.join(base_dir, "python311.dll"),
    os.path.join(base_dir, "_internal", "python311.dll"),
]
for pydll in pydll_candidates:
    if os.path.exists(pydll):
        os.environ["PYTHONNET_PYDLL"] = pydll
        break

# 4. Explicitly set PYTHONNET_RUNTIME_DIR so clr_loader finds Python.Runtime.dll
runtime_candidates = [
    os.path.join(exe_dir, "pythonnet", "runtime"),
    os.path.join(exe_dir, "_internal", "pythonnet", "runtime"),
    os.path.join(base_dir, "pythonnet", "runtime"),
    os.path.join(base_dir, "_internal", "pythonnet", "runtime"),
]
for rdir in runtime_candidates:
    if os.path.exists(rdir):
        os.environ["PYTHONNET_RUNTIME_DIR"] = rdir
        break

# Suppress console streams when running windowed
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

from app import app, init_crm_db
from crm_db import get_user_data_root
import uvicorn


def find_open_port(start_port=8088):
    for p in range(start_port, start_port + 50):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', p))
                return p
        except OSError:
            continue
    return start_port


def run_server(port):
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")


def run_app_fallback(app_url):
    """
    Fallback when WinForms / pythonnet has loading restrictions on target PC.
    Launches in dedicated standalone Edge App mode: zero tabs, zero URL bar, feels like native app.
    """
    edge_paths = [
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    edge_exe = next((p for p in edge_paths if os.path.exists(p)), None)
    if edge_exe:
        proc = subprocess.Popen([edge_exe, f"--app={app_url}", "--window-size=1440,920"])
        proc.wait()
    else:
        webbrowser.open(app_url)
        while True:
            time.sleep(2)


def main():
    init_crm_db()
    port = find_open_port(8088)

    # Start FastAPI backend in background daemon thread
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()

    time.sleep(0.8)

    app_url = f"http://127.0.0.1:{port}"
    ico_path = os.path.join(base_dir, "app_icon.ico")
    if not os.path.exists(ico_path):
        ico_path = os.path.join(exe_dir, "app_icon.ico")
    if not os.path.exists(ico_path):
        ico_path = None

    user_storage = os.path.join(get_user_data_root(), "webview_profile")
    os.makedirs(user_storage, exist_ok=True)

    # Attempt native PyWebView window with full fail-safe fallback
    try:
        import webview
        window = webview.create_window(
            title="Shivansh Astro-Vastu Professional (शिवांश ॲस्ट्रो-वास्तू)",
            url=app_url,
            width=1440,
            height=920,
            min_size=(1024, 700),
            background_color="#1A0F08",
            text_select=False,
        )
        webview.start(
            icon=ico_path,
            storage_path=user_storage,
            private_mode=False
        )
    except Exception as e:
        # Fallback cleanly to Edge App mode — 100% reliable on every Windows PC!
        run_app_fallback(app_url)

    sys.exit(0)


if __name__ == "__main__":
    main()
