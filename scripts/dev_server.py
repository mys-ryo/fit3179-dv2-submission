"""Local test server: serves this folder on http://127.0.0.1:8765 and tells the browser not to cache,
so edits to .vg.json and .csv files show up on reload. Run from anywhere: python3 scripts/dev_server.py"""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import functools

root = Path(__file__).resolve().parent.parent


class NoCache(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


ThreadingHTTPServer(("127.0.0.1", 8765), functools.partial(NoCache, directory=str(root))).serve_forever()
