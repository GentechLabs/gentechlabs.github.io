# Ollama + Hermes Integration Setup

**Requested by:** Jordan
**Assigned to:** Dmob
**Priority:** High — this enables 24/7 agent uptime
**Date:** 2026-04-17
**Status:** 🔄 IN PROGRESS — Dmob assigned, pre-switch save running tonight
**Last checked:** 2026-04-18 10:21 PM EDT (pre-switch checkpoint)

## Context
Jordan had an Ollama subscription before. Wants to use Ollama cloud models as a fallback when:
- Nous subscription limits hit around 8pm
- Hermes credits run low
- Need a secondary provider

## Goal
Set up Hermes to use Ollama **cloud models** as a secondary provider alongside Nous. Not replacing — layering. NO local models (VPS can't handle it).

## Setup Steps (from docs.ollama.com/integrations/hermes)

### 1. Check Ollama subscription is active
Jordan confirmed it's active. API key provided (rotate after setup).

### 2. Pick cloud models
Watch this video for model recommendations: https://youtu.be/Af7Fg1m7hRw
"Top AI Models for Hermes Agent (Tier List)" — ranks orchestrators, executors, auxiliary support.

### 3. Configure Hermes to use Ollama Cloud
- In Hermes setup: More providers → Custom endpoint
- API base URL: Ollama cloud endpoint (check docs for exact URL)
- API key: provided by Jordan (ask him for it in Labs if needed — don't store in vault)
- Hermes auto-detects available cloud models

### 4. Recommended Cloud Models (from Ollama)
- **Primary fallback: `qwen3.5:cloud`** — great orchestrator per tier list video
- `kimi-k2.5:cloud` — secondary option
- `glm-5.1:cloud` — secondary option
- `minimax-m2.7:cloud` — secondary option

Start with qwen3.5:cloud as the main fallback. Add others if needed.

## Key Questions for Jordan
1. Does he still have an active Ollama subscription?
2. Which cloud models does he want as fallback?
3. Should this be a secondary provider in Hermes config or a separate instance?

## VPS Constraints
- 16GB RAM total, 4.8GB free, no swap
- Local models not viable — cloud models only
- 160GB storage available

## Reference
- Docs: https://docs.ollama.com/integrations/hermes
- Install: `curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash`
