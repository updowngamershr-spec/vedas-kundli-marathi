# -*- coding: utf-8 -*-
"""
Shivansh Astro-Vastu Professional - Native Desktop Application Shell
- Powered by pywebview (Native Windows Win32 / WebView2 Desktop Shell).
- Zero external browser, zero kiosk mode, zero command prompt.
- Runs embedded local server on open port.
- Clean exit on window close.
"""

import os
import sys
import io
import time
import socket
import threading
import webview
import uvicorn

# Suppress console streams when running windowed
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

from app import app, init_crm_db
from crm_db import get_user_data_root

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

def main():
    init_crm_db()
    port = find_open_port(8088)

    # Start FastAPI backend in background daemon thread
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()

    # Time to allow server bind
    time.sleep(0.8)

    app_url = f"http://127.0.0.1:{port}"
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    ico_path = os.path.join(base_dir, "app_icon.ico")
    if not os.path.exists(ico_path):
        ico_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_icon.ico")
    if not os.path.exists(ico_path):
        ico_path = None

    user_storage = os.path.join(get_user_data_root(), "webview_profile")
    os.makedirs(user_storage, exist_ok=True)

    # Create native Windows Desktop Window - Maximize for authentic Filmora-style desktop suite!
    window = webview.create_window(
        title="Shivansh Astro-Vastu Professional (शिवांश ॲस्ट्रो-वास्तू)",
        url=app_url,
        width=1440,
        height=920,
        min_size=(1024, 700),
        background_color="#1A0F08",
        text_select=False,
    )

    # Start native Windows message loop (blocks until window is closed by user)
    webview.start(
        icon=ico_path,
        storage_path=user_storage,
        private_mode=False
    )
    # Window closed -> exit cleanly
    sys.exit(0)

if __name__ == "__main__":
    main()
