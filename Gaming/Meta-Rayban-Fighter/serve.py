#!/usr/bin/env python3
import http.server
import socketserver
import os

PORT = 8080

Handler = http.server.SimpleHTTPRequestHandler

# Change to project directory
os.chdir('/root/vaults/gentech/Projects/meta-rayban-fighter')

with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"✓ Server running at http://localhost:{PORT}")
    print(f"✓ Ready for Meta Ray-Ban glasses")
    print(f"\nFor Meta glasses, use: http://<YOUR-LOCAL-IP>:{PORT}")
    print(f"\nPress Ctrl+C to stop")
    httpd.serve_forever()