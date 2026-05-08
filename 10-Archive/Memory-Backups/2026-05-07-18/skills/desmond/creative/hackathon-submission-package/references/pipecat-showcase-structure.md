# Pipecat Voice Showcase — Reference Structure

**Source session:** Colosseum Frontier Pipecat hackathon (May 2026)
**Author:** Desmond, Gentech Creative

## Directory Layout

```
Pipecat-Voice-Showcase/
├── README-PIPECAT-GUIDE.md       # Local run guide (CPU-friendly)
├── SUBMISSION-MAIN.md            # Executive summary + 3 project pitches
├── TECHNICAL-WALKTHROUGH.md      # Code-level pipeline details
├── DEMO-VIDEO-SCRIPT.md          # 90-second demo narrative
├── ARCHITECTURE.html             # Interactive SVG diagram (hover states)
├── SOCIAL-THREAD-SERIES.md       # Multi-platform posts (X/LinkedIn/Reddit)
├── PITCH-DECK-SLIDES.md          # 10-slide markdown deck
├── active-handoffs/
│   └── pipecat-hackathon-coordination.md  # DMOB technical review note
└── vault_context/                # Sample resumable sessions (optional)
    └── sample-session-1.json
```

## Three-Project Showcase Pattern

When the stack supports multiple use-cases, build **three distinct demos** to prove versatility:

| Use-Case | Project Name | Core Hook |
|----------|--------------|-----------|
| Enterprise compliance | GuardianVox | Document-aware, multi-turn, Vault-persistent |
| Real-time decision support | TradePulse | Market data, voice-confirmed actions |
| Interactive education | EduFlow | Adaptive feedback, embedded visuals |

**Why it works:** Judges see breadth without needing different tech stacks. Same Pipecat orchestration, three personas.

## Interactive Architecture Diagram (HTML/SVG)

Instead of static images, produce an `ARCHITECTURE.html` with:
- Hoverable component boxes (stroke/fill transition)
- Invisible connectors to keep grid layout clean
- Legend explaining data flow
- Embedded JavaScript for interactivity (no external deps)

**Template path:** `templates/architecture-diagram.html` (copy and modify)

**Key:** Keep SVG viewBox at `1000x700` for consistent scaling; use `#006` fill for boxes, `#7df` arrows for path lines.

## Local-First Deliverable Extensions

When user specifies "CPU-friendly", "local-first", or "no cloud GPU":

1. **README must include:**
   - System requirements table (minimum/recommended CPU, RAM, disk)
   - Performance tuning flags (`--vad-aggressiveness`, `--max-tokens`)
   - Audio device troubleshooting (ALSA vs PulseAudio)
   - One-command installer script (`run_local.sh`)
   - Hardware-specific benchmark section (actual machine tested on)

2. **TECHNICAL-WALKTHROUGH must include:**
   - Component-by-component RAM/CPU breakdown
   - Latency measurements per pipeline stage
   - Memory footprint steady-state after N minutes
   - AVX2/AVX512 vs non-AVX fallbacks

3. **SOCIAL-THREAD-SERIES must include:**
   - Platform-specific timing (when to post)
   - Hardware stats as tweet content ("runs on 8 vCPU, 6GB RAM")
   - Hashtags: `#LocalAI #CPUfriendly #VoiceAI`

## Green Room Coordination for DMOB Review

For submissions with technical pipeline claims, create `active-handoffs/<project>-coordination.md`:

```markdown
# [Project] — Coordination

**Coordination:** Need DMOB review for technical accuracy (Pipecat mechanics, streaming pipeline, architecture claims) before social/brand rollout.

**Deadline:** [Colosseum date]

## 📄 Technical review checklist

- [ ] Streaming latency claims (STT→LLM→TTS numbers)
- [ ] State persistence accuracy (resumability test evidence)
- [ ] Local inference setup correctness (models, quantization)
- [ ] Security/privacy claims (no telemetry)
- [ ] Audio device plumbing (ALSA loopback works as described)

## 🤔 Open questions

1. [Specific technical uncertainty]
2. [Benchmark methodology question]

**Impact:** Social posts won't publish until DMOB signs off.
```

Tag `@DMOB` in Green Room. Wait 1 hour, escalate to HQ if no response.

## Vault Context for Resumable Demos

Create `vault_context/` with JSON session dumps that demo script can reload:

```json
{
  "session_id": "guardian-2026-05-03-001",
  "participant": "legal-team",
  "frames": [
    {
      "frame_id": "f001",
      "user_text": "Read me clause 3.7",
      "agent_text": "Sure, reading clause 3.7 now...",
      "retrieval_refs": ["06-Content/contracts/vendor-agreement.md#clause-3-7"],
      "timestamp": "2026-05-03T22:41:12Z",
      "state_snapshot": {
        "current_doc": "vendor-agreement",
        "current_section": "clause-3-7"
      }
    }
  ]
}
```

Include `--resume` flag in README and demo script (shows mid-conversation restart).

## One-Command Installer Pattern

`run_local.sh` should:
1. Check Python version (`>=3.11`)
2. Create venv at `~/.pipecat-venv/` (optional but recommended)
3. Download Whisper.cpp model (`medium.en` or `small.en`)
4. Pull Ollama Llama3 8B q4 (`ollama pull llama3:8b-instruct-q4_K_M`)
5. Download Piper voice (`en_US-medium`)
6. Install Pipecat + dependencies
7. Launch selected agent

**Non-interactive:** No prompts; fails fast with clear error messages.

## Demo Video Script Timing (90-second format)

| Segment | Duration | Content |
|---------|----------|---------|
| Opener | 0–5s | Pipecat logo → Gentech logo → tagline |
| Demo 1 (GuardianVox) | 6–31s | Legal doc read-back, clause Q&A |
| Demo 2 (TradePulse) | 32–57s | Voice trade, market alert, chart |
| Demo 3 (EduFlow) | 58–82s | Quiz question, adaptive feedback, diagram |
| Outro | 83–90s | All three running simultaneously, CTA |

**Voiceover style:** Natural cadence, lightly edited (no robotic perfection). Use Ear Trumpet for mic capture; noise gate at -35dB.

## Hardware Benchmark Table (copy into README/TECHNICAL)

```markdown
**Machine:** Ryzen 7 5700X, 32GB RAM, no GPU, Ubuntu 22.04

| Component | Model | Quantization | RAM | CPU Cores | Latency |
|-----------|-------|--------------|-----|-----------|---------|
| STT | Whisper.cpp | medium.en | q5_k_m | ~800MB | 2 | 400ms |
| LLM | Ollama Llama3 8B | q4_K_M | ~5GB | 4 | 12 tok/s |
| TTS | Piper | en_US-medium | ~300MB | 1 | 200ms |
| **Total** | — | — | **~6.1GB** | **<8 vCPU** | **~1.2s** round-trip |
```

Adjust for user's actual hardware (Intel i7, Apple Silicon, etc.).

## Pitfalls Specific to Voice/Local Projects

- **ALSA vs PulseAudio:** Default Pipecat uses PulseAudio. For Jordan's Wednesday CPU constraint, force ALSA loopback to avoid 100MB+ RAM overhead. Include `--device hw:0,0` flag in run script.
- **Whisper.cpp model size trade-off:** `medium.en` accurate but slower (400ms latency). `small.en` 2x faster but ~10% less accurate. List both options.
- **Piper voice selection:** `en_US-medium` default; `en_US-rachel` more natural but 20% slower. Cache voices in `~/.local/share/piper/`.
- **Ollama context window:** Default 2048 tokens insufficient for long legal docs. Implement Vault checkpointing at 1500 tokens to persist context and resume.
- **Barge-in handling:** Pipecat's VAD must be tuned (`aggressiveness=3`) to allow natural pauses during clause reading without cutting off agent mid-sentence.
- **Concurrent agents:** Running Guardian + Trade + Edu simultaneously works on 8+ cores. On 4-core machines, reduce `--threads` flags for Whisper and Ollama.
- **Disk I/O for Vault:** Save sessions with `os.chmod(0600)` for privacy; use `aiofiles` for async writes to avoid blocking pipeline.

## When to Use This Extended Pattern

Apply this full structure when:
- Project is for **Colosseum Frontier** or similar hackathon with presentation/demo requirements
- Architecture includes **real-time streaming** (audio, video, or voice)
- User specifies **local-first / CPU-friendly** constraints
- Stack includes **Pipecat** or similar orchestration layer
- Need to demonstrate **stateful conversation** (not just echo-chamber)
- Three distinct **personas** or use-cases exist (compliance, trading, education)

Otherwise, fall back to standard 4-deliverable hackathon-submission-package.