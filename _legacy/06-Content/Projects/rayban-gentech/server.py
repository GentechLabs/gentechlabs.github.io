"""
Gentech Ray-Ban Bridge Server v3
Communicates with Hermes directly via `hermes chat -q`.

Flow:
  1. Ray-Ban browser opens the page
  2. User speaks/types a message
  3. Server runs `hermes chat -q "message"` 
  4. Response displayed on the Ray-Ban display

No Telegram relay. Direct Hermes CLI bridge.
"""
import os
import sys
import json
import time
import asyncio
import secrets
from pathlib import Path
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

# ─── Config ─────────────────────────────────────────────────────────
PORT = int(os.environ.get("BRIDGE_PORT", "8765"))
HERMES_PROFILE = os.environ.get("HERMES_PROFILE", "gentech")

# ─── App ────────────────────────────────────────────────────────────
app = FastAPI(title="Gentech Ray-Ban Bridge")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Hermes CLI bridge ──────────────────────────────────────────────
async def ask_hermes(message: str, session_id: str = None) -> dict:
    """
    Send a message to Hermes and get the response.
    Uses `hermes chat -q` for direct CLI communication.
    """
    cmd = ["hermes", "-p", HERMES_PROFILE, "chat", "-q", message, "-Q"]
    
    if session_id:
        cmd.extend(["--resume", session_id])
    
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={**os.environ, "HERMES_YOLO_MODE": "1"},
        )
        
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=120  # 2 min timeout
        )
        
        output = stdout.decode().strip()
        
        # Parse session_id from output (first line: "session_id: ...")
        new_session_id = session_id
        response_text = output
        
        if output.startswith("session_id:"):
            lines = output.split("\n", 1)
            new_session_id = lines[0].replace("session_id:", "").strip()
            response_text = lines[1].strip() if len(lines) > 1 else ""
        
        return {
            "response": response_text or "(no response)",
            "session_id": new_session_id,
            "ok": True,
        }
        
    except asyncio.TimeoutError:
        return {"response": "⏰ Hermes took too long to respond.", "ok": False, "session_id": session_id}
    except Exception as e:
        return {"response": f"❌ Error: {str(e)}", "ok": False, "session_id": session_id}


# ─── Session tracking ──────────────────────────────────────────────
# Map bridge sessions to hermes session IDs
bridge_sessions: dict = {}  # bridge_token -> {hermes_session, created}


# ─── Routes ────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the Ray-Ban chat form — pure HTML, no JavaScript needed."""
    return HTMLResponse("""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Gentech</title><style>
*{margin:0;padding:0;box-sizing:border-box}body{background:#000;color:#fff;font-family:system-ui,sans-serif;padding:16px;min-height:100vh}
h1{color:#00ff88;font-size:22px;margin-bottom:16px;text-align:center}
p{color:#888;font-size:13px;text-align:center;margin-bottom:12px}
.chat{background:#111;border:1px solid #333;border-radius:12px;padding:12px;margin-bottom:16px}
.msg{padding:10px;margin:6px 0;border-radius:10px;font-size:15px;line-height:1.4;word-wrap:break-word}
.bot{background:#1a1a2e;border:1px solid #333}
form{margin-top:12px}input[type=text]{width:100%;padding:14px;border-radius:24px;border:1px solid #333;background:#111;color:#fff;font-size:16px;margin-bottom:10px}
button{width:100%;padding:14px;border-radius:24px;border:none;background:#00ff88;color:#000;font-size:18px;font-weight:bold;cursor:pointer}
</style></head><body><h1>⚡ GENTECH</h1><p>AI Assistant</p><div class="chat"><div class="msg bot">👋 Type a message below to talk to Gentech.</div></div>
<form method="POST" action="/send"><input type="text" name="message" placeholder="Type your message..." required><button type="submit">Send Message</button></form></body></html>""")


@app.post("/api/session")
async def api_session(request: Request):
    """
    Create a new chat session. Returns a token and starts a Hermes session.
    Body: { "label": "rayban" }
    """
    body = await request.json()
    label = body.get("label", "rayban")
    
    # Create a unique bridge token
    token = secrets.token_urlsafe(32)
    
    # Start a fresh Hermes session with a greeting
    result = await ask_hermes(
        f"You are being accessed via Ray-Ban glasses by {label}. "
        "Greet them briefly — 1-2 sentences max. Keep it casual and friendly."
    )
    
    bridge_sessions[token] = {
        "hermes_session": result.get("session_id"),
        "label": label,
        "created": time.time(),
    }
    
    return {
        "token": token,
        "greeting": result.get("response", "Hey! I'm Gentech. What's up?"),
        "status": "connected",
    }


@app.post("/api/chat")
async def api_chat(request: Request):
    """
    Send a message and get Hermes' response.
    Header: Authorization: Bearer <session_token>
    Body: { "message": "hello" }
    """
    auth = request.headers.get("Authorization", "")
    token = auth.replace("Bearer ", "").strip()
    
    if token not in bridge_sessions:
        raise HTTPException(401, "Invalid session. POST /api/session first.")
    
    body = await request.json()
    message = body.get("message", "").strip()
    if not message:
        raise HTTPException(400, "Empty message")
    
    sess = bridge_sessions[token]
    
    # Ask Hermes with session continuity
    result = await ask_hermes(message, sess.get("hermes_session"))
    
    # Update session ID if Hermes gave us a new one
    if result.get("session_id"):
        sess["hermes_session"] = result["session_id"]
    
    return {
        "response": result.get("response", "No response"),
        "ok": result.get("ok", False),
        "timestamp": time.time(),
    }


@app.post("/api/draw")
async def api_draw(request: Request):
    """
    Accept a handwriting image (base64 PNG) and ask Hermes to read it.
    Body: { "image": "data:image/png;base64,..." }
    """
    auth = request.headers.get("Authorization", "")
    token = auth.replace("Bearer ", "").strip()

    if token not in bridge_sessions:
        raise HTTPException(401, "Invalid session. POST /api/session first.")

    body = await request.json()
    image_data = body.get("image", "")
    if not image_data:
        raise HTTPException(400, "No image data")

    # Save the image to a temp file
    import base64
    import tempfile
    header, encoded = image_data.split(",", 1)
    img_bytes = base64.b64decode(encoded)

    tmp_path = f"/tmp/rayban_draw_{int(time.time())}.png"
    with open(tmp_path, "wb") as f:
        f.write(img_bytes)

    # Ask Hermes to read the handwriting
    sess = bridge_sessions[token]
    prompt = (
        f"A user wrote this by hand on their Ray-Ban smart glasses. "
        f"Read the handwriting in this image and type out exactly what it says. "
        f"If you can read it, respond with just the text they wrote. "
        f"If it's unclear, give your best guess. "
        f"Image saved at: {tmp_path}"
    )

    result = await ask_hermes(prompt, sess.get("hermes_session"))

    if result.get("session_id"):
        sess["hermes_session"] = result["session_id"]

    # Clean up temp file
    try:
        os.unlink(tmp_path)
    except Exception:
        pass

    return {
        "response": result.get("response", "Could not read the drawing"),
        "ok": result.get("ok", False),
        "timestamp": time.time(),
    }


TUNNEL_URL=os.environ.get("GENTECH_TUNNEL_URL", "")

@app.get("/api/config")
async def api_config():
    """Return the current tunnel URL so the frontend can auto-discover it."""
    return {"tunnel_url": TUNNEL_URL, "bridge_port": PORT}




@app.post("/send")
async def send_form(message: str = Form(...)):
    """Handle simple HTML form submission — no JavaScript needed."""
    if not message.strip():
        return RedirectResponse("/", status_code=303)
    result = await ask_hermes(message)
    response = result.get("response", "(no response)")
    return HTMLResponse(f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Gentech</title><style>
*{{margin:0;padding:0;box-sizing:border-box}}body{{background:#000;color:#fff;font-family:system-ui,sans-serif;padding:16px;min-height:100vh}}
h1{{color:#00ff88;font-size:22px;margin-bottom:16px;text-align:center}}
.chat{{background:#111;border:1px solid #333;border-radius:12px;padding:12px;margin-bottom:16px}}
.msg{{padding:10px;margin:6px 0;border-radius:10px;font-size:15px;line-height:1.4;word-wrap:break-word}}
.user{{background:#00ff88;color:#000;text-align:right}}
.bot{{background:#1a1a2e;border:1px solid #333}}
form{{margin-top:12px}}input[type=text]{{width:100%;padding:14px;border-radius:24px;border:1px solid #333;background:#111;color:#fff;font-size:16px;margin-bottom:10px}}
button{{width:100%;padding:14px;border-radius:24px;border:none;background:#00ff88;color:#000;font-size:18px;font-weight:bold;cursor:pointer}}
</style></head><body><h1>⚡ GENTECH</h1><div class="chat"><div class="msg user">{message}</div><div class="msg bot">{response}</div></div>
<form method="POST" action="/send"><input type="text" name="message" placeholder="Type a message..." required><button type="submit">Send</button></form></body></html>""")


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "profile": HERMES_PROFILE,
        "port": PORT,
        "active_sessions": len(bridge_sessions),
        "time": datetime.utcnow().isoformat(),
    }


# ─── Main ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"⚡ Gentech Ray-Ban Bridge v3")
    print(f"📡 Port: {PORT}")
    print(f"🤖 Profile: {HERMES_PROFILE}")
    print(f"🔗 URL: http://0.0.0.0:{PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
