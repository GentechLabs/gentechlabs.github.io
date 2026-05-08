# Pipecat Quick Start (Condensed)

**Goal:** Get a voice bot talking in 15 minutes, CPU-only.

## Prerequisites

- Python 3.10+ with `uv` or `pip`
- PortAudio (audio I/O): `brew install portaudio` (mac) or `sudo apt-get install portaudio19-dev` (ubuntu)
- 8GB+ free RAM

## Installation

```bash
# Using uv (recommended)
uv pip install pipecat-ai

# Or pip
pip install pipecat-ai
```

## Minimal Example (TTS only)

Save as `say.py`:
```python
import os
from pipecat.frames.frames import TTSSpeakFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.transports.websocket.fastapi import FastAPIWebsocketParams
from pipecat.transports.base_transport import TransportParams

async def run():
    tts = CartesiaTTSService(
        api_key=os.getenv("CARTESIA_API_KEY"),
        settings=CartesiaTTSService.Settings(voice="71a7ad14-091c-4e8e-a314-022ece01c121")
    )
    task = PipelineTask(Pipeline([tts]))
    await task.queue_frames([TTSSpeakFrame("Hello world!")])
    await task.wait_for_finish()

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
```

Run:
```bash
export CARTESIA_API_KEY=your_key
python say.py
```

## Full Voice Agent (STT + LLM + TTS)

```bash
# Clone examples
git clone https://github.com/pipecat-ai/pipecat.git
cd pipecat/examples/getting-started

# Run the 6th example (voice agent with function calling)
uv run 06-voice-agent.py -t webrtc
# Opens http://localhost:7860/client/ — click Connect, speak
```

## Cloud vs Local Providers

| Component | Cloud (easiest) | Local (free) |
|---|---|---|
| STT | Deepgram (`DEEPGRAM_API_KEY`) | Whisper.cpp (download `.bin` model) |
| LLM | OpenAI (`OPENAI_API_KEY`) | Ollama (`ollama pull llama3.1:8b`) |
| TTS | ElevenLabs (`ELEVENLABS_API_KEY`) | Piper (`piper --model en_US-lessac-medium`)| 

**Local-only example** (no API keys):
```bash
# 1. Start Ollama
ollama serve &

# 2. Pull model
ollama pull llama3.1:8b

# 3. Run local voice agent (uses Whisper.cpp + Ollama + Piper)
uv run voice/01-simple-voice.py \
  --stt whisper_cpp \
  --llm ollama \
  --tts piper \
  --whisper-model models/whisper-base.en.bin
```

## Transport Options

| Flag (`-t`) | Use case |
|---|---|
| `webrtc` | Direct browser connection (development) |
| `daily` | Daily.co rooms (production video calls) |
| `twilio` | Phone calls via Twilio |
| `ws` | Raw WebSocket (custom clients) |

## Common Gotchas

1. **PortAudio missing:** `pip install pyaudio` fails → install system lib first
2. **Port already in use:** Pipecat defaults to 7860; kill old process (`lsof -i:7860`)
3. **No audio output:** Check system volume, not just browser; TTS plays to stdout if no transport
4. **Ollama not responding:** Ensure `OLLAMA_HOST=http://localhost:11434` env var set

## Next Steps

- Add function calling: see `examples/function-calling/`
- Add vision: see `examples/vision/vision-moondream.py`
- Deploy to production: use `pipecat-cli deploy` or systemd service

---

**TL;DR:** `uv run examples/getting-started/06-voice-agent.py -t webrtc` → open http://localhost:7860/client/ → talk.
