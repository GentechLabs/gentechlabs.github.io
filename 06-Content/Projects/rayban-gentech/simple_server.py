"""
Gentech Simple Server — No JavaScript, just HTML forms.
Works on Ray-Ban Meta limited browser.
"""
import os
import sys
import json
import time
import asyncio
from pathlib import Path
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

# Load env
def load_env(path):
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip("\"'")
            if k and v:
                os.environ.setdefault(k, v)

for env_path in [
    "/root/.hermes/profiles/gentech/.env",
    "/root/.hermes/.env",
]:
    load_env(env_path)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
HOME_CHANNEL = os.environ.get("TELEGRAM_HOME_CHANNEL", "-1003863540828")
PORT = int(os.environ.get("BRIDGE_PORT", "8765"))
HERMES_PROFILE = os.environ.get("HERMES_PROFILE", "gentech")

app = FastAPI(title="Gentech Ray-Ban")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store messages in memory
messages = []

async def ask_hermes(message: str) -> str:
    """Send message to Hermes and get response."""
    cmd = ["hermes", "-p", HERMES_PROFILE, "chat", "-q", message, "-Q"]
    
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={**os.environ, "HERMES_YOLO_MODE": "1"},
        )
        
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)
        output = stdout.decode().strip()
        
        # Parse response
        if output.startswith("session_id:"):
            lines = output.split("\n", 1)
            return lines[1].strip() if len(lines) > 1 else "(no response)"
        return output or "(no response)"
        
    except asyncio.TimeoutError:
        return "⏰ Response timed out."
    except Exception as e:
        return f"❌ Error: {str(e)}"


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the simple HTML form."""
    html_path = Path(__file__).parent / "simple.html"
    if html_path.exists():
        return HTMLResponse(html_path.read_text())
    return HTMLResponse("<h1>Gentech</h1><p>UI not found.</p>")


@app.post("/send")
async def send_message(message: str = Form(...)):
    """Handle form submission."""
    if not message.strip():
        return RedirectResponse("/", status_code=303)
    
    # Add user message
    messages.append({
        "role": "user",
        "text": message,
        "time": datetime.now().strftime("%H:%M")
    })
    
    # Get response from Hermes
    response = await ask_hermes(message)
    
    # Add bot response
    messages.append({
        "role": "bot",
        "text": response,
        "time": datetime.now().strftime("%H:%M")
    })
    
    # Build HTML response
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gentech</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#000;color:#fff;font-family:system-ui,sans-serif;padding:20px}}
h1{{color:#00ff88;font-size:24px;margin-bottom:20px;text-align:center}}
p{{color:#888;font-size:14px;margin-bottom:15px;text-align:center}}
.chat{{background:#111;border:1px solid #333;border-radius:12px;padding:15px;margin:15px 0}}
.msg{{padding:10px;margin:8px 0;border-radius:8px;font-size:14px;line-height:1.4}}
.user{{background:#00ff88;color:#000;text-align:right}}
.bot{{background:#1a1a2e;border:1px solid #333}}
form{{margin-top:20px}}
input[type=text]{{width:100%;padding:15px;border-radius:24px;border:1px solid #333;background:#111;color:#fff;font-size:16px;margin-bottom:10px}}
input:focus{{border-color:#00ff88;outline:none}}
button{{width:100%;padding:15px;border-radius:24px;border:none;background:#00ff88;color:#000;font-size:18px;font-weight:bold;cursor:pointer}}
button:active{{background:#00cc6a}}
</style>
</head>
<body>
<h1>⚡ GENTECH</h1>
<p>AI Assistant for Meta Ray-Ban</p>

<div class="chat">
"""
    
    # Add all messages
    for msg in messages[-10:]:  # Last 10 messages
        role = msg["role"]
        text = msg["text"]
        time = msg["time"]
        css_class = "user" if role == "user" else "bot"
        html += f'<div class="msg {css_class}">{text}</div>\n'
    
    html += f"""</div>

<form method="POST" action="/send">
<input type="text" name="message" placeholder="Type your message..." required autocomplete="off">
<button type="submit">Send Message</button>
</form>

</body>
</html>"""
    
    return HTMLResponse(html)


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "profile": HERMES_PROFILE,
        "port": PORT,
        "messages": len(messages),
        "time": datetime.utcnow().isoformat(),
    }


if __name__ == "__main__":
    print(f"⚡ Gentech Simple Server")
    print(f"📡 Port: {PORT}")
    print(f"🤖 Profile: {HERMES_PROFILE}")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
