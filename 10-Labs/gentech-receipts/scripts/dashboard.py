#!/usr/bin/env python3
"""
GenTech Receipts — Dashboard API Server
Serves the dashboard HTML and JSON data API.

Usage:
    python scripts/dashboard.py              # Port 8080, sample data
    python scripts/dashboard.py --port 9090  # Custom port
    python scripts/dashboard.py --data data/latest.json  # Use real data
"""

import json
import os
import sys
import argparse
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Add parent to path for tracker import
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

DATA_DIR = Path(__file__).parent.parent / "data"
DASHBOARD_DIR = Path(__file__).parent.parent / "dashboard"


class DashboardHandler(SimpleHTTPRequestHandler):
    data_file = None

    def do_GET(self):
        if self.path == "/api/data":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            try:
                if self.data_file and os.path.exists(self.data_file):
                    with open(self.data_file) as f:
                        data = json.load(f)
                elif os.path.exists(DATA_DIR / "latest.json"):
                    with open(DATA_DIR / "latest.json") as f:
                        data = json.load(f)
                else:
                    # Generate sample data on the fly
                    sys.path.insert(0, str(DATA_DIR.parent / "scripts"))
                    from tracker import generate_sample_data
                    data = generate_sample_data()

                self.wfile.write(json.dumps(data).encode())
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        # Serve dashboard HTML
        if self.path == "/" or self.path == "":
            self.path = "/dashboard/index.html"

        super().do_GET()

    def log_message(self, format, *args):
        print(f"  [{self.log_date_time_string()}] {args[0]} {args[1]} {args[2]}")


def main():
    parser = argparse.ArgumentParser(description="GenTech Receipts — Dashboard Server")
    parser.add_argument("--port", type=int, default=8080, help="Server port")
    parser.add_argument("--data", help="Path to JSON data file")
    args = parser.parse_args()

    if args.data:
        DashboardHandler.data_file = args.data

    server_addr = ("", args.port)
    httpd = HTTPServer(server_addr, DashboardHandler)

    print("╔══════════════════════════════════════════════════════════╗")
    print("║        GenTech Receipts — Dashboard Server             ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"  Dashboard: http://localhost:{args.port}/")
    print(f"  API:       http://localhost:{args.port}/api/data")
    if args.data:
        print(f"  Data:      {args.data}")
    else:
        print(f"  Data:      Sample (auto-generated)")
    print(f"  Ctrl+C to stop")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.")
        httpd.server_close()


if __name__ == "__main__":
    main()
