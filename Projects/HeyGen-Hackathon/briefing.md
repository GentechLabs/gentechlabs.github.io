# HeyGen Hackathon Brief — May 14–15, 2026

**Event:** Build your Multi-modal AI Business and Scale it with HeyGen, ElevenLabs, Fal and PostHog
**Luma:** https://luma.com/wtd2hyst
**Format:** Hybrid (SF office + virtual)
**Registration:** Free, requires approval, capped at 140 participants

---

## Timeline

| When | What |
|------|------|
| **May 14, 9:00 AM** | Welcome & schedule |
| **May 14, 10:00 AM – 5:00 PM** | Build day (hybrid) |
| **May 15, 10:00 AM** | ⏰ Submission deadline |
| **May 15, 2:00 – 4:30 PM** | Demo day (virtual only) |
| **May 15, 6:00 PM** | Winners announced |

**Build window:** ~24 hours (May 14 10AM → May 15 10AM PDT)

---

## Prizes

- **Grand Prize (Best Overall):** $3,000
- **Best Product:** $1,000
- **Best AI Agent Use Case:** $1,000

---

## Two Tracks

### 1. Product Track
"Build a product or workflow others could use or pay for. Bonus points if it could stand on its own."

### 2. Agent Track ⭐ (our wheelhouse)
"Wire HeyGen into an agent pipeline. Show us your stack, your workflow, and your edge."

---

## Judging Criteria
- Innovation and creativity
- Technical execution
- Quality of HeyGen integration
- Overall impact and usability

---

## Submission Requirements
1. **Working project demo** (live, running)
2. **Written description**
3. **Demo video** (≤5 minutes)
4. No explicit GitHub repo required, but useful for demo
5. One submission per team
6. Project must be **newly created** during build window

---

## HeyGen Toolkit

| Tool | What It Does | API Endpoint |
|------|-------------|--------------|
| **Video Agent** | Prompt-to-video generation | `POST /v3/video-agents` |
| **Avatar IV/V** | Digital twin / photo avatar videos | `POST /v3/videos` |
| **Video Translate** | Translate + lip sync video | `POST /v3/video-translations` |
| **Lipsync** | Lip sync existing video to new audio | `POST /v3/lipsyncs` |
| **TTS (Starfish)** | Text-to-speech | `POST /v3/voices/speech` |
| **Voice Clone** | Clone a voice from audio | `POST /v3/voices/clone` |

**Note:** Hyperframes appears discontinued (404 on docs).

---

## API Details

**Auth:** `X-Api-Key` header
**Base URL:** `https://api.heygen.com`
**Async:** All video generation is async — poll status or use webhooks
**Concurrency:** 10 max concurrent jobs
**Pricing:** Pay-as-you-go, prepaid USD wallet

### Key Rates
- Video Agent: $0.0333/sec
- Photo Avatar IV: $0.05/sec
- Video Translation (speed): $0.0333/sec
- Lipsync (speed): $0.0333/sec
- TTS: $0.000667/sec

**Free tier (UI only):** 3 videos/month, 1 min max, 720p. No free API credits.

---

## Partner Tools (Permitted, Not Required)

- **ElevenLabs** — Advanced TTS, voice cloning
- **Fal.ai** — Image/video generation models
- **PostHog** — Product analytics

---

## Eligibility
- Open to all (online or in-person)
- Excluded: HeyGen employees/family, partner employees, sanctioned jurisdictions
- IP: Participants retain ownership; HeyGen gets royalty-free license for 3 years

---

## AAE Strategy Notes

### Why This Fits Us
1. **Agent Track** = exactly what AAE does (multi-agent pipelines)
2. **HeyGen + ElevenLabs** = video + audio generation for agent content
3. **24-hour build** = intense but doable with prep
4. **$5K total prize pool** = decent ROI for a focused sprint
5. **Virtual participation** = no travel needed from Cincinnati

### Potential Ideas
1. **Agent Content Studio** — Multi-agent pipeline where agents generate video content autonomously (script → TTS → avatar video → translation)
2. **Localized Agent Spokesperson** — Use HeyGen Video Translate to auto-localize agent communications into multiple languages
3. **AI Agent Video Resume** — Agents generate personalized video pitches for job applications (ties into Jordan's job search!)
4. **DeFi Dashboard with Agent Narrator** — Real-time DeFi data + HeyGen avatar explaining market movements

### What We Need
1. **HeyGen API key** — Sign up, add credits ($20-50 should cover demo)
2. **Registration** — Apply at Luma link ASAP (140 cap)
3. **Idea decision** — Pick one, commit fully
4. **Local Hermes setup** — RTX 3070 for faster iteration

### HeyGen GitHub Repos
- `heygen-com/skills` ⭐214 — AI agent skills (avatar creation, video production via v3 API)
- `heygen-com/heygen-cli` ⭐33 — Official CLI for terminal-based video generation
- `BrasD99/HeyGenClone` ⭐998 — Open-source HeyGen clone (reference implementation)

---

## Local GPU Setup (RTX 3070 + 32GB RAM)

**Goal:** Run Hermes locally on Jordan's workstation for faster hackathon iteration

**Capabilities with RTX 3070 (8GB VRAM):**
- Local LLM inference (7B-13B models via llama.cpp/Ollama)
- Image generation (Stable Diffusion, Flux Schnell)
- Whisper for local STT
- Faster dev iteration without VPS latency

**Architecture:**
- Local Hermes instance → connects to VPS agents (YoYo, DMOB, Desmond)
- Local GPU handles compute-heavy tasks
- VPS handles coordination and Telegram

---

*Prepared by Gentech — May 7, 2026*
