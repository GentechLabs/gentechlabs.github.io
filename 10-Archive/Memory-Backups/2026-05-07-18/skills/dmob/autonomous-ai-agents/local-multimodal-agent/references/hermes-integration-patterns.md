# Hermes × Pipecat Integration Patterns

**Three ways to connect Hermes (text agent) with Pipecat (voice/multimodal pipeline).**

---

## Pattern A — Standalone Daemon (Recommended)

**Architecture:**
```
[Telegram] → Hermes → WebSocket → Pipecat Daemon → STT/LLM/TTS
                                    ↓
                              Vault (logs)
```

### Setup

1. **Run Pipecat as WebSocket server:**
```python
# pipecat_server.py
from pipecat.pipeline.pipeline import Pipeline
from pipecat.transports.websocket.fastapi import FastAPIWebsocketTransport

transport = FastAPIWebsocketTransport(
    ws_url="ws://0.0.0.0:7860",
    audio_out_enabled=True,
)
# ... build pipeline with your STT/LLM/TTS
```

2. **Systemd service:**
```ini
# /etc/systemd/system/pipecat-hermes.service
[Unit]
Description=Pipecat Voice Agent
After=network.target ollama.service

[Service]
Type=simple
User=ubuntu
WorkingDir=/opt/pipecat
ExecStart=/usr/bin/python pipecat_server.py
Restart=always
Environment="OLLAMA_HOST=http://localhost:11434"

[Install]
WantedBy=multi-user.target
```

3. **Hermes tool to forward:**
```python
# In Hermes skill
import websockets

async def voice_process(audio_bytes):
    async with websockets.connect('ws://localhost:7860/ws') as ws:
        await ws.send(audio_bytes)
        response = await ws.recv()  # returns audio bytes or JSON {text, audio_url}
    # Write to vault
    vault_write("02-Labs/voice-logs/latest.json", response)
    return response
```

**Pros:** Language-agnostic, can scale independently, easy to restart. **Cons:** Network overhead (localhost OK).

---

## Pattern B — Embedded Library (Tight Coupling)

**Architecture:**
```
Hermes (Python process)
   ↓ import
Pipecat Pipeline (in-process)
   ↓
STT/LLM/TTS services
```

### Setup

```python
# In Hermes core
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineTask
from pipecat.services.whisper.cpp.stt import WhisperCPPSTTService
from pipecat.services.ollama.llm import OllamaLLMService
from pipecat.services.coqui.tts import CoquiTTSService

class HermesVoicePipeline:
    def __init__(self):
        self.stt = WhisperCPPSTTService(model_path="/models/whisper-base.en.bin")
        self.llm = OllamaLLMService(model="llama3.1:8b")
        self.tts = CoquiTTSService()
        self.pipeline = Pipeline([self.stt, self.llm, self.tts])
        self.task = PipelineTask(self.pipeline)

    async def process_voice(self, audio_bytes: bytes) -> bytes:
        # Push audio through pipeline
        await self.task.queue_frames([AudioRawFrame(audio_bytes)])
        result = await self.task.wait_for_finish()
        return result.audio
```

**Pros:** No network, simplest debugging. **Cons:** Hermes crash takes down voice; hard to scale; language lock-in (Python only).

---

## Pattern C — Subprocess Worker (Balanced)

**Architecture:**
```
Hermes → Popen(pipecat_worker.py) → stdin/stdout JSON
```

### Setup

**Worker (`pipecat_worker.py`):**
```python
#!/usr/bin/env python3
import sys, json
from pipecat.pipeline.pipeline import Pipeline
# ... setup pipeline ...

async def main():
    pipeline = build_pipeline()
    task = PipelineTask(pipeline)

    while True:
        line = sys.stdin.readline()
        if not line: break
        request = json.loads(line)
        # request = {"audio_b64": "...", "user_id": "..."}
        audio_bytes = base64.b64decode(request["audio_b64"])
        await task.queue_frames([AudioRawFrame(audio_bytes)])
        result = await task.wait_for_finish()
        response = {
            "text": result.transcript,
            "audio_b64": base64.b64encode(result.audio).decode(),
            "latency_ms": result.latency
        }
        print(json.dumps(response), flush=True)

if __name__ == "__main__":
    asyncio.run(main())
```

**Hermes caller:**
```python
import subprocess, json, base64

worker = subprocess.Popen(
    ["python", "pipecat_worker.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

def voice_call(audio_bytes: bytes):
    payload = {"audio_b64": base64.b64encode(audio_bytes).decode()}
    worker.stdin.write(json.dumps(payload) + "\n")
    worker.stdin.flush()
    response = json.loads(worker.stdout.readline())
    return base64.b64decode(response["audio_b64"])
```

**Pros:** Crash isolation, language-agnostic (worker can be any language). **Cons:** JSON serialization overhead, no streaming (full audio in/out).

---

## Vault Logging Strategy (all patterns)

**File:** `02-Labs/voice-logs/YYYY-MM-DD-hermes-voice.md`

```markdown
## 2026-05-15T14:32:10Z — USER (Telegram @jordan)
"what's the weather in Tokyo?"

## 2026-05-15T14:32:13Z — AGENT
"It's 22°C and partly cloudy in Tokyo right now."

---
metadata:
  stt_model: whisper-base.en
  llm_model: llama3.1:8b (ollama)
  tts_model: piper-en_US-lessac-medium
  latency_ms: 1850
  first_token_ms: 980
  transport: websocket
  pattern: daemon
  vault_entry: 02-Labs/voice-logs/2026-05-15.md
  token_count:
    prompt: 142
    completion: 87
```

**Rotation:** Keep last 30 days in active file, archive to `02-Labs/voice-logs/archive/YYYY-MM.q.md` quarterly.

---

## Tool Bridging to Composio

Pipecat can call external tools during conversation:

```python
from pipecat.tools import tool

@tool("get_stock_price")
async def get_stock_price(symbol: str) -> str:
    """Get current stock price via Composio."""
    # Hermes vault read for Composio API key
    api_key = vault_read("02-Security/keys/composio.json")["api_key"]
    result = await call_composio("finnhub_quote", {"symbol": symbol}, api_key)
    return f"{symbol} is ${result.price}"
```

**Vault lookup pattern:**
```python
import json
def vault_read(path: str):
    with open(f"/root/vaults/gentech/{path}") as f:
        return json.load(f)
```

---

## Pattern Decision Matrix

| Factor | Daemon (A) | Embedded (B) | Subprocess (C) |
|---|---|---|---|
| **Language lock-in** | None | Python only | Any |
| **Latency** | ~2ms (localhost) | ~0ms (in-process) | ~5ms (serialization) |
| **Fault isolation** | High (separate process) | Low (shared crash) | High |
| **Scalability** | Easy (run multiple daemons) | Hard (GIL) | Medium (multiple workers) |
| **Debugging** | Moderate (two logs) | Easy (single process) | Easy (stdin/stdout) |
| **Startup complexity** | Medium (systemd) | Easy (import) | Easy (Popen) |
| **Our recommendation** | ✅ | ❌ (tight coupling) | ⚠️ (overhead) |

---

## Telegram Bridge Implementation (Pattern A)

**Forward Telegram voice → Pipecat → reply with voice:**

1. **Telegram bot webhook** receives voice message (OGG/OPUS)
2. **Convert to PCM:** `ffmpeg -i voice.ogg -f s16le -ac 1 -ar 16000 pipe:1`
3. **Send to Pipecat WebSocket:** `ws://localhost:7860/ws?room=telegram_user123`
4. **Pipecat returns audio:** MP3/OPUS bytes
5. **Telegram sends reply:** `sendVoice(chat_id, audio_bytes)`

**Code sketch:**
```python
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters

async def handle_voice(update: Update, context):
    ogg = await update.message.voice.get_file()
    pcm = subprocess.check_output([
        "ffmpeg", "-i", "pipe:0", "-f", "s16le", "-ac", "1", "-ar", "16000", "pipe:1"
    ], input=await ogg.download_as_bytearray())

    # Send to Pipecat
    audio_response = await voice_call(pcm)  # use pattern A/B/C

    # Send back as voice note
    await update.message.reply_voice(audio_response)
```

---

## Next Steps

1. **Pick pattern** (A for production, B for dev, C for polyglot)
2. **Benchmark** your 32GB machine (see `scripts/benchmark-local-pipeline.py`)
3. **Deploy daemon** (Pattern A) with systemd
4. **Bridge Telegram** → WebSocket
5. **Log to vault** per format above

---

**References:**
- Pipecat transports: https://docs.pipecat.ai/server/transports
- Pipecat services: https://docs.pipecat.ai/api-reference/server/services
