# STT / TTS / LLM Provider Cheat Sheet

**Quick comparison for local multimodal agents. All tested with Pipecat.**

---

## Speech-to-Text (STT)

| Provider | Local/Cloud | Free Tier | Latency | Quality | Setup |
|---|---|---|---|---|---|
| **Whisper.cpp** | Local CPU | 100% free | 0.3–0.8× realtime | Excellent | Download `.bin`, set path |
| **Whisper (OpenAI API)** | Cloud | $0.006/min | ~200ms | Excellent | `OPENAI_API_KEY` |
| **Deepgram** | Cloud | 200 min/mo | ~150ms | Excellent | `DEEPGRAM_API_KEY` |
| **AssemblyAI** | Cloud | 3 hours free | ~300ms | Very Good | `ASSEMBLYAI_API_KEY` |
| **Google STT** | Cloud | 60 min/mo | ~250ms | Good | GCP credentials |

**Recommendation:** Whisper.cpp base/small on CPU (quality vs speed tradeoff). Use cloud only if you need <500ms on long audio.

---

## Text-to-Speech (TTS)

| Provider | Local/Cloud | Free Tier | Latency | Quality | Notes |
|---|---|---|---|---|---|
| **Piper** | Local CPU | 100% free | 0.5–1.2× realtime | Good | English best, other languages OK |
| **Coqui TTS** | Local CPU | 100% free | 1–2× realtime | Good | More models, slower |
| **ElevenLabs** | Cloud | 10k chars/mo | ~200ms | Exceptional | Best voice quality |
| **Cartesia** | Cloud | 5h free trial | ~150ms | Very Good | Low-latency optimized |
| **Play.ht** | Cloud | 5h free trial | ~300ms | Very Good | Large voice library |

**Recommendation:** Piper for local (no API key). ElevenLabs if you already have subscription and need premium voice.

---

## Large Language Models (LLM)

| Provider | Local/Cloud | Free Tier | Cost (cloud) | Context | Speed (CPU) |
|---|---|---|---|---|---|
| **Llama 3.1 8B** (Ollama) | Local | 100% free | N/A | 128k | 8–12 tok/s |
| **Mistral 7B** (Ollama) | Local | 100% free | N/A | 32k | 10–15 tok/s |
| **Phi-3 mini** (Ollama) | Local | 100% free | N/A | 128k | 15–20 tok/s |
| **Claude 3.5 Sonnet** | Cloud | none | $3/1M in, $15/1M out | 200k | ~40 tok/s |
| **GPT-4o** | Cloud | none | $2.50/1M in, $10/1M out | 128k | ~50 tok/s |
| **Grok-2** | Cloud | none | ~$2/1M in, ~$8/1M out | 128k | ~45 tok/s |

**CPU speed notes (32GB machine, no GPU):**
- First token latency: 0.8–1.5s (8B model), 1.5–3s (70B model too slow for real-time)
- Streaming tokens: 8–12/second (8B), 30+/second (70B with GPU)

**Recommendation:** Llama 3.1 8B via Ollama. Best balance of quality/speed/local. Use Claude/OpenAI only if you need advanced reasoning and don't mind $.

---

## Vision Models

| Provider | Local/Cloud | Free Tier | Quality | Notes |
|---|---|---|---|---|
| **LLaVA 7B** (Ollama) | Local CPU | 100% free | Fair–Good | Slow (~5s/image) on CPU |
| **LLaVA 13B** (Ollama + GPU) | Local GPU | 100% free | Good | Needs 12GB+ VRAM |
| **Moondream 2** | Local CPU | 100% free | Fair | Very small, OK for simple captions |
| **GPT-4o** | Cloud | none | Exceptional | $0.005–0.02/image |
| **Claude 3.5 Sonnet** | Cloud | none | Exceptional | $0.003–0.015/image |

**Recommendation:** Cloud vision for production (speed/quality). Local only for experimentation or privacy requirements.

---

## Cost Calculator (per 1,000 conversations, avg 10 turns each)

**All-local (CPU):**
- Electricity: ~$0.02 (2 hours runtime @ $0.10/kWh)
- **Total: ~$0.02**

**Mixed (cloud LLM, local STT/TTS):**
- LLM: Llama 3.1 8B = $0
- STT: Whisper local = $0
- TTS: Piper local = $0
- **Total: ~$0.02**

**All-cloud (high-end):**
- STT: Deepgram 100 min = $0.004 (beyond free)
- LLM: Claude 3.5 Sonnet 10k tokens ≈ $0.35
- TTS: ElevenLabs 5k chars ≈ $0.30
- **Total: ~$0.67 / conversation ≈ $670 / 1000 convos**

**Savings:** Local deployment saves ~$600 per 1k conversations vs. premium cloud.

---

## Quick Decision Tree

```
Need voice agent?
  ├─ Want zero cost? → Local: Whisper.cpp + Ollama + Piper
  ├─ Want best quality? → Cloud: Deepgram + Claude + ElevenLabs
  ├─ Have 32GB RAM, no GPU? → Local 8B models (Llama 3.1) + Whisper small
  └─ Privacy required? → Local everything (no data leaves network)
```

---

**Update this sheet** when you test new providers. Track: setup complexity, actual latency (p50/p95), quality subjective score (1–5), crash rate.
