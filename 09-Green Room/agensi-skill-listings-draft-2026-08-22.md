# Agensi Skill Listings — Draft (2026-08-22)

Picked per Agensi's "what actually sells" guide: DevOps, testing, high-stakes repetitive tasks.
70/30 split (we keep 70%). Price in the $3-10 sweet spot.

---

## 1. safe-update-restart — "Safe Production VPS Update & Restart"
- **Price:** $6
- **Category:** DevOps
- **Tags:** devops, deployment, vps, production, restart, update, reliability
- **Description:**
  Never blind-restart a production server again. This skill encodes a full
  backup → controlled window → restart → verify-every-service workflow for
  production VPSes running multiple live APIs, services, and agent gateways
  sharing one environment. It catches the silent failures that blind restarts
  cause — services that don't come back, endpoints that 500, gateways that
  die mid-restart. Includes a fleet-aware restart that survives its own
  gateway restart (restarts others first, defers its own last).
- **Why it sells:** High-stakes (mistakes are expensive) + repetitive (every
  deploy). The exact DevOps pattern Agensi says sells best.

---

## 2. x402-payments — "Build x402 Payment-Gated APIs for AI Agents"
- **Price:** $8
- **Category:** Web3 / Payments
- **Tags:** x402, payments, ai-agents, api, web3, stablecoin, monetization
- **Description:**
  Turn any API into a paid endpoint that AI agents can call and pay for
  per-request with USDC — no bank account, no merchant account, no signup
  friction. Covers the full x402 lifecycle: facilitators (GoPlausible, Naven,
  CDP), HTTP 402 challenge/response, settlement flows, session management,
  and multi-chain payment rails. Includes a working FastAPI reference server
  and a discovery manifest so agents can find and price your services.
- **Why it sells:** x402 is the hottest standard in the agent economy (Linux
  Foundation-backed, 200M+ transactions). High demand, low supply of
  practical how-to skills.

---

## 3. handoff-mesh — "Multi-Agent Communication Layer (Full-Mesh Handoffs)"
- **Price:** $7
- **Category:** Agent Orchestration
- **Tags:** multi-agent, handoff, orchestration, communication, agents, workflow
- **Description:**
  Wire communication between multiple AI agents so any agent can hand work
  to any other — full-mesh handoff folders, a watcher that surfaces open
  handoffs AND recent completions, weekly archive cleanup, and a
  completion-reporting loop so every handoff is handled AND verified. The
  durable "second brain" counterpart to real-time channels. Includes the
  watcher script with tappable Obsidian deep-links.
- **Why it sells:** Multi-agent setups are the fastest-growing need in 2026.
  Most teams have no built-in way for agents to hand off work — this solves
  it out of the box.

---

## 4. output-enforcer — "Validate AI Agent Tool Outputs (Pydantic + Circuit Breaker)"
- **Price:** $5
- **Category:** Testing / Reliability
- **Tags:** validation, pydantic, testing, reliability, agents, circuit-breaker
- **Description:**
  Validate AI agent tool outputs against pydantic schemas with auto-retry,
  disk-backed persistence, and circuit-breaker protection. Hardened for
  production deployments where a malformed output from an LLM tool call can
  take down a pipeline. Catches schema drift, retries transient failures,
  and fails safe.
- **Why it sells:** Testing/validation category — saves hours debugging
  malformed LLM outputs. Framework-agnostic, works with any agent harness.

---

## Notes
- **Free skills first:** Agensi recommends listing 2-3 free skills to build
  reputation, then premium versions. Consider making `output-enforcer` free
  (or a lite version) to drive traffic to the paid x402/handoff skills.
- **Test across 2 agents:** Agensi requires testing each skill on Claude Code
  + one other before listing. Our skills are already Hermes-tested; need a
  Claude Code pass.
- **Promotion:** Reddit (r/AI_Agents, r/devops), dev.to, Discord communities.
