---
title: "Codebase Assessment — HKUDS VideoAgent"
date: 2026-04-28
type: assessment
tags: [video, ai, agents, python, multi-modal, hackathon]
status: ready
---

# Codebase Assessment: VideoAgent (HKUDS)
**Repo:** https://github.com/HKUDS/VideoAgent
**License:** MIT | **Stars:** 636 | **Language:** Python 3.10+

## Overview
An all-in-one agentic framework for video understanding, editing, and remaking. Uses natural language to drive intent analysis → tool selection → workflow generation → execution. Multi-agent system with graph-powered workflow generation.

## Codebase Metrics
| Metric | Value |
|--------|-------|
| Python files | 384 |
| Lines of code | 46,157 |
| Comment lines | 9,868 (14%) |
| YAML configs | 86 files |
| Total files | 737 |

## Architecture
```
environment/
├── agents/
│   ├── base.py          # FunctionRegistry + BaseTool pattern
│   └── multi.py         # MultiAgent orchestrator (Claude for routing)
├── config/
│   ├── config.yml       # LLM API keys (DeepSeek, Claude, GPT, Gemini)
│   ├── intents.yml      # Intent → tool mapping
│   └── llm.py           # OpenAI-compatible clients for all providers
└── roles/               # Individual agent capabilities
    ├── audio_extractor.py
    ├── transcriber.py
    ├── separator.py     # Demucs vocal separation
    ├── voice_generator.py
    ├── vid_editor.py
    ├── vid_preloader.py
    ├── vid_searcher.py
    ├── vid_qa/          # Video Q&A
    ├── vid_summ/        # Video summarization
    ├── vid_rhythm/      # Beat-synced editing
    ├── vid_comm/        # Commentary video
    ├── vid_news/        # News video
    ├── tts/             # Text-to-speech (CosyVoice, Fish-Speech)
    ├── svc/             # Singing voice conversion (Seed-VC)
    ├── cross_talk/      # Cross-cultural comedy adaptation
    ├── stand_up/        # Stand-up comedy adaptation
    └── mixer.py, merge.py, etc.

tools/                   # Bundled ML models
├── CosyVoice/           # TTS model
├── fish-speech/         # TTS model
├── seed-vc/             # Voice conversion
├── DiffSinger/          # Singing synthesis
├── ImageBind/           # Multi-modal embeddings
├── videorag/            # Video RAG system
└── audio-preprocess/    # Fish Audio preprocessing
```

## How It Works
1. **User input** → natural language request
2. **Intent Analysis** (Claude) → maps request to intent categories
3. **Tool Selection** → intents.yml maps intents to agent tools
4. **Graph Planning** (Claude) → generates execution DAG
5. **Execution** → tools run in sequence with feedback loops
6. **Output** → processed video/audio

## Dependencies (Heavy)
- **PyTorch 2.3.1** (CUDA 12.1)
- **Transformers 4.40.1**
- **OpenAI, Claude, Gemini** API clients
- **Demucs** (vocal separation)
- **Whisper** (transcription)
- **MoviePy** (video editing)
- **Gradio** (UI)
- **ONNX Runtime GPU**
- **Neo4j** + **hnswlib** (vector/graph DB)

## API Keys Required
| Provider | Purpose |
|----------|---------|
| DeepSeek | Video remixing, TTS, SVC, stand-up, cross-talk |
| Claude | Agentic graph router (main orchestrator) |
| GPT-4o | Video editing, overview, summarization, QA |
| Gemini | Video captioning and fine-grained understanding |

## Setup Requirements
```bash
# GPU: 8GB+ VRAM minimum
conda create --name videoagent python=3.10
conda activate videoagent
conda install -y -c conda-forge pynini==2.1.5 ffmpeg
pip install -r requirements.txt

# Model downloads (~10GB+ total)
# CosyVoice, fish-speech-1.5, seed-vc, DiffSinger, Whisper large-v3-turbo, ImageBind
```

## Strengths ✅
- Clean agent architecture with FunctionRegistry pattern
- Multi-provider LLM support (not locked to one vendor)
- Intent-driven tool selection — extensible
- Bundled models — self-contained
- MIT licensed — fully open
- Active development (636 stars)

## Concerns / Questions ⚠️
1. **Massive dependency footprint** — PyTorch, multiple ML models, Neo4j. Heavy for a VM.
2. **GPU required** — 8GB+ VRAM. Our VM is CPU-only.
3. **Multi-model inference** — Each feature uses different models. Expensive on API credits.
4. **Chinese-first codebase** — Comments and some configs in Chinese (from HKU)
5. **No tests found** — No test directory visible
6. **Config is plaintext YAML** — API keys in config.yml (no .env pattern)

## Hackathon Fit Assessment
**Rating: ⭐⭐⭐ (3/5)**

- ✅ Multi-agent + natural language = aligns with AAE narrative
- ✅ MIT licensed, can fork and customize
- ✅ Impressive feature set for video creation
- ⚠️ GPU requirement limits our VM testing
- ⚠️ Heavy dependency chain makes deployment complex
- ⚠️ Not blockchain-related — purely ML/video

## Potential Use Cases for GenTech
1. **Content creation pipeline** — Generate travel videos from raw footage
2. **Video summarization** — Process long videos into short clips
3. **Beat-synced editing** — Auto-edit to music rhythm
4. **Cross-cultural adaptation** — Translate/adapt content across languages
5. **Meme video generation** — Quick viral content creation

## Next Steps
- [ ] Set up environment (need GPU VM or cloud GPU)
- [ ] Configure API keys (Claude, GPT, Gemini, DeepSeek)
- [ ] Download required models
- [ ] Test basic features (Q&A, summarization)
- [ ] Identify which features to prioritize for hackathon
