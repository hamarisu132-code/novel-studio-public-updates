"""Windows desktop entry point. Build with PyInstaller on Windows."""
import os
import sys
import threading
import socket
import time
import shutil
import sqlite3
from pathlib import Path
from http.server import ThreadingHTTPServer


def resource_dir():
    return Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parent))


def data_dir():
    base = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'NovelStudio'
    base.mkdir(parents=True, exist_ok=True)
    return base


def migrate_legacy():
    target = data_dir() / 'novel_studio.db'
    if target.exists():
        return
    candidates = [Path(sys.executable).resolve().parent / 'data' / 'novel_studio.db',
                  Path(__file__).resolve().parent / 'data' / 'novel_studio.db',
                  Path.cwd() / 'data' / 'novel_studio.db']
    for source in candidates:
        if source.exists():
            # SQLite backup handles WAL mode correctly.
            with sqlite3.connect(source) as old, sqlite3.connect(target) as new:
                old.backup(new)
            break


def main():
    migrate_legacy()
    import server
    import webview
    server.ROOT = resource_dir()
    server.DATA = data_dir()
    server.DB = server.DATA / 'novel_studio.db'
    server.TOKEN_FILE = server.DATA / '.running_token'
    server.init_db()
    server.create_daily_backup()
    httpd = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
    server.SERVER = httpd
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    url = 'http://127.0.0.1:' + str(httpd.server_port)
    try:
        webview.create_window('NOVEL STUDIO', url, width=1360, height=850, min_size=(900, 600))
        webview.start()
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=3)


if __name__ == '__main__':
    main()
