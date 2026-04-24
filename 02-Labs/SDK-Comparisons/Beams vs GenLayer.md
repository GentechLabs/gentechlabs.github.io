# Beams vs GenLayer — SDK Comparison

> **Status:** Draft
> **Date:** 2026-04-19
> **Sources:** docs.beam.cloud, github.com/beam-cloud/beta9, beam.ai, onbeam.com

---

## ⚠️ Ambiguity Note: Multiple "Beam" Platforms

The name "Beams" (or "Beam") maps to **three distinct platforms**. Based on context (AI agent infrastructure/SDK mentioned alongside GenLayer), **Beam Cloud (beam.cloud)** is the most likely match. All three are documented below for completeness.

| Platform | URL | Type | Relevance |
|---|---|---|---|
| **Beam Cloud** | beam.cloud / docs.beam.cloud | AI infra runtime + agent SDK | **⭐ Most likely match** |
| **Beam AI** | beam.ai | Enterprise agentic automation SaaS | Possible — enterprise agent platform |
| **Beam (Blockchain)** | onbeam.com | Sovereign L1 blockchain (gaming) | Unlikely — not AI-focused |

---

## 1. Beam Cloud (beam.cloud) — Primary Match

### Overview

Beam Cloud is an **open-source serverless runtime for AI workloads** (GitHub: `beam-cloud/beta9`, AGPL license). It provides a Pythonic SDK for deploying and scaling AI applications with zero infrastructure overhead. Recently launched a **stateful AI agent framework** with built-in concurrency.

### Architecture

```
┌─────────────────────────────────────────┐
│           Developer (Python SDK)         │
│  @endpoint / @task_queue / @bot          │
├─────────────────────────────────────────┤
│         Beam Cloud Platform              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ Serverless│ │  GPU     │ │ Sandboxes│ │
│  │ Functions │ │ Inference│ │ (isolated│ │
│  │           │ │          │ │  exec)   │ │
│  └──────────┘ └──────────┘ └──────────┘ │
│  ┌──────────────────────────────────┐   │
│  │  Agent Framework (stateful bots)  │   │
│  │  @bot.network / @bot.transition   │   │
│  └──────────────────────────────────┘   │
├─────────────────────────────────────────┤
│         Infrastructure Layer             │
│  Custom container runtime (<1s boot)     │
│  Distributed volumes, GPU pool           │
└─────────────────────────────────────────┘
```

### SDK & Key Features

- **Installation:** `pip install beam-client`
- **Core primitives:**
  - `@endpoint` — serverless inference endpoints with autoscaling
  - `@task_queue` — background task processing (Celery replacement)
  - `@bot` — stateful AI agent framework with transition networks
  - `Sandbox` — isolated containers for LLM-generated code execution
  - `@function` — parallel/concurrent workloads (fan-out to 100s of containers)
  - `@pod` — long-running pods/web services
- **Agent Framework (new):**
  - Stateful agents with `@bot.network`, `@bot.location`, `@bot.transition`
  - Built-in concurrency and session management
  - TypedList inputs/outputs, Pydantic-style schemas
  - Context commands: `confirm()`, `prompt()`, `remember()`, `say()`, `send_file()`, `get_file()`
  - Controllable bot awareness via `expose=False` on transitions
  - Development workflow: `beam serve app.py:bot`
- **Infrastructure:**
  - Sub-second container boot times
  - Scale-to-zero by default
  - GPU support (4090s, H100s, A10G)
  - Distributed volume storage
  - Hot-reloading, webhooks, scheduled jobs
  - Self-hostable (open-source) or managed cloud

### Language & Runtime

- **Python SDK** (primary), TypeScript SDK also available
- Custom container runtime (not WASM)
- Runs on Linux containers

### Consensus & Validation

- **No blockchain component** — centralized/managed infrastructure
- No decentralized validator network
- No consensus mechanism

### Status

- **Production-ready** — live cloud platform with pricing
- Open-source core (AGPL-3.0)
- Self-hostable option available

---

## 2. Beam AI (beam.ai) — Alternative Candidate

### Overview

Beam AI is an **enterprise agentic automation platform** (Y Combinator-backed). Focuses on building, deploying, and managing AI agents for business workflows. Not open-source; SaaS product.

### Key Features

- Agent hub with pre-built templates
- Agentic automation for enterprise workflows
- Task mining and process discovery
- No-code/low-code agent builder
- Enterprise integrations (CRM, ERP, etc.)
- Claims 5,000+ tasks/min throughput
- AWS Marketplace listing

### SDK

- **No public SDK** — primarily a web-based platform
- API-based integrations
- Focused on business process automation, not developer infrastructure

### Status

- Production SaaS
- Enterprise-focused

---

## 3. Beam Blockchain (onbeam.com) — Not a Match

### Overview

Beam is a **sovereign L1 blockchain** focused on gaming, DeFi, and frontier technologies. Has a token, governance, and ecosystem. **Not an AI agent platform.**

---

## Comparison Matrix: Beam Cloud vs GenLayer

| Dimension | **Beam Cloud** | **GenLayer** |
|---|---|---|
| **Primary Purpose** | Serverless AI compute + agent runtime | Intelligent Contracts (AI-powered smart contracts) |
| **Language/SDK** | Python SDK, TypeScript SDK | Python "Intelligent Contracts" on WASM |
| **Runtime** | Custom Linux containers (<1s boot) | GenVM (WASM-based virtual machine) |
| **Agent Model** | Stateful transition-network bots (`@bot`) | AI validator network for subjective consensus |
| **Blockchain** | ❌ None | ✅ zkSync Elastic Chain (EVM-compatible L2) |
| **Consensus** | Centralized/managed | Decentralized AI validators (subjective consensus) |
| **Use Cases** | Inference, sandboxes, background tasks, stateful agents | Dispute resolution, SLA enforcement, subjective judgments |
| **Open Source** | ✅ AGPL-3.0 (self-hostable) | ❌ Not open-source |
| **Network Status** | ✅ Production (live cloud) | ⚠️ Testnet-only (no mainnet) |
| **GPU Support** | ✅ 4090s, H100s, A10G | ❌ Not applicable |
| **Scale-to-Zero** | ✅ Yes | N/A |
| **Concurrency** | ✅ Fan-out to 100s of containers | Limited by validator throughput |
| **Pricing** | Pay-per-use (cloud), free (self-hosted) | TBD (testnet) |
| **Best Fit For** | ML inference, agent orchestration, serverless AI | On-chain subjective logic, decentralized AI judgments |
| **Key Differentiator** | Speed, developer UX, GPU infrastructure | Blockchain integration, subjective consensus |

---

## When to Use Which

### Choose **Beam Cloud** when:
- You need fast, serverless GPU inference
- You want to deploy stateful AI agents with conversation/memory
- You need isolated sandbox environments for LLM-generated code
- You want scale-to-zero economics
- You prefer a Python-first developer experience
- You need self-hosting option (open-source)

### Choose **GenLayer** when:
- Your logic must live on-chain (smart contracts)
- You need subjective consensus (disputes, judgments, human-like evaluation)
- You're building dispute resolution or SLA enforcement systems
- You need EVM compatibility (zkSync L2)
- Your use case benefits from decentralized AI validation

### Key Tension
These platforms solve **different problems**:
- **Beam Cloud** = AI compute infrastructure (where to *run* AI)
- **GenLayer** = AI-powered blockchain contracts (how to *trust* AI decisions on-chain)

They could theoretically be **complementary**: use Beam Cloud for AI agent execution, and GenLayer for on-chain verification/settlement of agent outcomes.

---

## Links

- **Beam Cloud Docs:** https://docs.beam.cloud/
- **Beam Cloud GitHub:** https://github.com/beam-cloud/beta9
- **Beam AI:** https://beam.ai/
- **GenLayer Docs:** https://docs.genlayer.com/
- **GenLayer GitHub:** https://github.com/genlayer-com
