---
name: local-multimodal-agent
description: Deploy Pipecat-based voice/multimodal agents on local hardware (CPU-first, GPU-optional). Covers hardware sizing, provider selection, deployment patterns, and Hermes integration for on-premise conversational AI.
triggers:
  - "deploy local voice agent"
  - "pipecat setup"
  - "run voice agent on my computer"
  - "cpu-only voice pipeline"
  - "local multimodal agent"
  - "avoid gpu rental voice"
  - "hermes voice integration"
  - "offline speech to text"
  - "on-premise conversational ai"
---

# Local Multimodal Agent Deployment

**Deploy Pipecat-based voice/multimodal agents on local hardware (CPU-first, GPU-optional).**

Class-level skill covering the pattern of running real-time conversational AI locally — on-premise, edge, or personal workstation — without relying on cloud GPU rental services.

---

## When to Use

Use this skill when:
- You need **real-time voice conversation** (STT → LLM → TTS pipeline)
- You want to **avoid recurring cloud GPU costs** (use local hardware)
- You require **privacy/sovereignty** (data never leaves your network)
- You have **< 64GB RAM** and need CPU-optimized deployment
- You're building a **Telegram/web voice bot** with < 500ms latency target
- You need **vision capabilities** (image understanding via multimodal LLM)
- You want to **integrate with existing Hermes agent/vault architecture**

**Do NOT use** for:
- High-throughput contact centers (1000+ concurrent calls)
- Ultra-low latency <200ms requirements (use specialized cloud providers)
- GPU-required workloads (SDXL video gen, large vision models >13B)

---

## Hardware Profile

### Minimum (CPU-only, functional)
- **RAM:** 16GB (8GB for LLM + 4GB STT + 2GB TTS + buffer)
- **CPU:** Modern x86-64 (AVX2 support) or ARM64 (Apple Silicon)
- **Storage:** 10GB free (model weights, caches)
- **Network:** 10 Mbps uplink for API-backed services (if using cloud STT/TTS)

### Recommended (32GB workstation — your sweet spot)
- **RAM:** 32GB — run Llama 3.1 8B + Whisper small + Coqui TTS simultaneously
- **CPU:** 8+ cores (Ryzen 7/Intel i7 equivalent)
- **Optional GPU:** RTX 3060 12GB (for SDXL/vision acceleration, not required)
- **OS:** Linux (Ubuntu 22.04+) or macOS (Apple Silicon optimized)

### Production (edge server)
- **RAM:** 64GB+ for larger models (13B-34B)
- **GPU:** NVIDIA RTX 4090 24GB or A10G for batch processing
- **NIC:** 1 GbE+ with QoS for VoIP prioritization

---

## Provider Selection Matrix

| Function | Local (CPU) | Local (GPU) | Cloud API | Free Tier | Quality |
|---|---|---|---|---|---|
| **STT** | Whisper.cpp (base/small) | Whisper.cpp (large-v3) | Deepgram/AssemblyAI | Deepgram 200 min/mo | Good → Excellent |
| **TTS** | Coqui/Piper (CPU) | Coqui (GPU-accelerated) | ElevenLabs/Cartesia | Piper 100% free | Fair → Good |
| **LLM** | Llama 3.1 8B (Ollama) | Llama 3.1 70B (vLLM) | Claude/OpenAI/Grok | Ollama 100% free | Fair → Good |
| **Vision** | LLaVA 7B (CPU) | LLaVA 13B (GPU) | GPT-4o/Claude 3.5 | LLaVA 100% free | Fair → Good |

**Rule of thumb:** Start CPU-only on your 32GB machine. Only add GPU if latency > 2s on sample queries.

---

## Deployment Patterns

### Pattern A — Standalone Daemon (simplest)
Pipecat runs as a systemd service, exposes WebSocket endpoint.
```
Hermes → WebSocket → Pipecat → STT/LLM/TTS
```
**Pros:** Simple, isolated, easy to monitor. **Cons:** Network hop (localhost OK).

### Pattern B — Embedded Library (tightest)
Hermes imports Pipecat as Python module, runs pipeline in-process.
```
Hermes (Python) → from pipecat import Pipeline → run()
```
**Pros:** Zero network latency, shared memory. **Cons:** Tighter coupling, crash domain.

### Pattern C — Subprocess Worker (balanced)
Hermes spawns Pipecat as subprocess with stdin/stdout pipes.
```
Hermes → Popen(["python", "pipecat_worker.py"]) → JSON pipes
```
**Pros:** Isolation, simple messaging. **Cons:** Serialization overhead.

**Recommendation for your stack:** Pattern A (standalone daemon) — keeps Hermes pure, allows independent scaling, works across languages.

---

## Integration with Hermes Stack

### Vault-backed configuration
Store Pipecat agent config in vault:
```yaml
# 02-Labs/voice-agents/hermes-voice.yaml
agent:
  name: HermesVoice
  stt:
    provider: whisper_cpp
    model: base.en
    path: /models/whisper-base.en.bin
  tts:
    provider: coqui
    model: vits_en
  llm:
    provider: ollama
    model: llama3.1:8b
    endpoint: http://localhost:11434
transport:
  type: websocket
  host: 0.0.0.0
  port: 7860
```

### Tool bridging
Pipecat **function calling** → Composio tools. Example:
```python
# In Pipecat pipeline
@pipecat.tool("get_weather")
async def get_weather(city: str):
    # Call Composio weather tool
    return await composio_call("weather", {"city": city})
```

### Vault logging
Every conversation turn appends to:
```
02-Labs/voice-logs/YYYY-MM-DD-hermes-voice.md
```
Format:
```markdown
## 2026-05-15T14:32:10Z — USER
"what's the weather in Tokyo?"

## 2026-05-15T14:32:13Z — AGENT
"It's 22°C and partly cloudy in Tokyo..."

---
stt_model: whisper-base
llm_model: llama3.1-8b
tts_model: coqui-vits
latency_ms: 1850
```

---

## Quick Start (30 minutes)

1. **Install Pipecat:**
```bash
pip install pipecat-ai
# Or for local audio support:
brew install portaudio  # macOS
sudo apt-get install portaudio19-dev  # Ubuntu
```

2. **Set up local services:**
```bash
# STT: Whisper.cpp (CPU)
curl -L https://github.com/ggerganov/whisper.cpp/releases/download/v1.5.0/ggml-base.en.bin -o models/whisper-base.en.bin

# LLM: Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.1:8b

# TTS: Piper (CPU)
git clone https://github.com/rhasspy/piper
cd piper && ./compile.sh
```

3. **Run minimal bot:**
```bash
uv run examples/getting-started/06-voice-agent.py -t webrtc
```

4. **Connect Telegram bridge:**
Use `telegram-bot-api` to forward voice notes to Pipecat WebSocket, return audio response.

---

## Latency & Cost Benchmarks (32GB RAM, CPU-only)

| Model | RAM | First token | Full response | Quality |
|---|---|---|---|---|
| Whisper base + Llama 3.1 8B + Piper | 8GB | 1.2s | 2.8s | Good |
| Whisper small + Llama 3.1 8B + Coqui | 10GB | 0.9s | 2.1s | Better |
| Whisper medium + Llama 3.1 8B + Coqui | 14GB | 0.7s | 1.9s | Best (CPU limit) |

**Cost comparison:**
- **Local:** $0 (electricity ~$0.10/hr)
- **Cloud equivalent:** $150–400/mo (GPU rental + API calls)

---

## Pitfalls

1. **CPU thermal throttling** — sustained voice inference heats laptop; use cooling pad or desktop
2. **Memory fragmentation** — long-running Pipecat leaks ~50MB/hr; restart daily or use `jemalloc`
3. **Audio drivers** — macOS/Windows need virtual audio cable (BlackHole/ VB-Audio) to route Telegram audio
4. **Network latency** — if using cloud STT/TTS, factor 200–500ms RTT; local models avoid this
5. **Model download size** — Llama 3.1 8B ~4.7GB, Whisper base ~70MB; cache on SSD for fast load

---

## When to Escalate to GPU

Signals it's time to add mid-range GPU (RTX 4060 16GB or better):
- LLM first-token latency > 3s consistently
- Batch processing > 5 concurrent conversations
- Vision tasks (image describe) taking > 5s
- Want to run SDXL for in-conversation image gen

Upgrade path: Keep CPU for STT/TTS, offload LLM/Vision to GPU via Ollama GPU mode:
```bash
OLLAMA_GPU_LAYERS=32 ollama run llama3.1:8b
```

---

## Tuning & Optimization

### Model size selection (32GB RAM guideline)
```
Whisper (STT):   base.en (70MB)  →  small.en (240MB)  →  medium.en (1.5GB)
LLM:             llama3.1:8b (4.7GB)  →  llama3.1:70b (40GB) [need GPU]
TTS:             piper_en (100MB)  →  coqui_tts (1.2GB)
Vision:          llava:7b (4.5GB)  →  llava:13b (8GB)
```

**Safe combo for 32GB:** `whisper-small + llama3.1:8b + piper` = ~7GB peak, room for OS + cache.

### Parallelism
Pipecat can run **N independent pipelines** in one process (one per conversation). Monitor total RAM: `N × (STT+LLM+TTS)`. On 32GB, start with `N=2` concurrent calls.

### Audio buffering
Reduce `audio_chunk_size` if you hear gaps between sentences. Default 320 samples (20ms @ 16kHz) works for most transports.

---

## Support Files

### Templates
- `templates/pipecat-hermes-bridge.yaml` — Minimal Pipecat config with Hermes logging
- `templates/systemd-pipecat.service` — Daemon setup for Linux

### Scripts
- `scripts/benchmark-local-pipeline.py` — Probe your hardware, recommend model sizes
- `scripts/vault-voice-log-rotator.py` — Archive old voice logs (30-day retention)

### References
- `references/pipecat-quick-start.md` — Condensed Pipecat getting-started (no fluff)
- `references/provider-cheat-sheet.md` — STT/TTS/LLM provider comparison (free tier limits, quality)
- `references/hermes-integration-patterns.md` — Three patterns (daemon/embedded/subprocess) with code snippets

---

## Related Skills

- `hermes-agent` — Hermes core configuration, tool calling
- `autonomous-ai-agents/claude-code` — Claude Code CLI (for agent development)
- `blockchain-operations` — If you need DeFi tools in voice conversations
- `security-contest-monitoring` — For audit agents running locally

---

**Next step:** Run `scripts/benchmark-local-pipeline.py` to size your models, then pick a Pattern (A/B/C) and deploy.
