#!/usr/bin/env python3
"""
Mastercard Innovation Challenge 2026 — demo server.

Serves the web prototype (index.html) and wires the RED TEAM (attack
simulator) and BLUE TEAM (pre-execution governance guard) to it.

Run:  python3 demo_server.py [--port 8080]
Then open http://localhost:8080
"""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from red_team import generate_attack, generate_batch
from blue_team import evaluate, evaluate_batch

INDEX_HTML = None
SEED = 42


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send(self, code, body: bytes, ctype="application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        global INDEX_HTML
        path = urlparse(self.path).path

        if path in ("/", "/index.html"):
            if INDEX_HTML is None:
                with open(__file__.rsplit("/", 1)[0] + "/index.html", "rb") as f:
                    INDEX_HTML = f.read()
            self._send(200, INDEX_HTML, "text/html")
            return

        if path == "/api/attack":
            intent = generate_attack()
            self._send(200, json.dumps(intent.to_dict()).encode())
            return

        if path == "/api/attack/batch":
            q = parse_qs(urlparse(self.path).query)
            n = int(q.get("n", ["5"])[0])
            batch = generate_batch(n, seed=SEED)
            self._send(200, json.dumps([i.to_dict() for i in batch]).encode())
            return

        if path == "/api/evaluate":
            # Evaluate pending: since this is stateless, evaluate a fresh batch
            # so the UI always has something to show. A real impl would hold
            # the intent list in memory keyed by session.
            batch = generate_batch(5, seed=SEED)
            verdicts = evaluate_batch(batch)
            self._send(200, json.dumps([v.to_dict() for v in verdicts]).encode())
            return

        if path == "/api/health":
            self._send(200, json.dumps({"ok": True}).encode())
            return

        self._send(404, json.dumps({"error": "not found"}).encode())

    do_POST = do_GET


def main() -> int:
    ap = argparse.ArgumentParser(description="Mastercard demo server")
    ap.add_argument("--port", type=int, default=8080)
    args = ap.parse_args()

    server = ThreadingHTTPServer(("0.0.0.0", args.port), Handler)
    print(f"🎯 Mastercard Challenge demo running at http://localhost:{args.port}")
    print(f"   Red team:  /api/attack, /api/attack/batch?n=5")
    print(f"   Blue team: /api/evaluate")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")
    return 0


if __name__ == "__main__":
    main()
