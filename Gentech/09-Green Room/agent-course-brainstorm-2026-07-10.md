# Brainstorm — AI Agent Course Triggers for GenTech
> **Source:** freeCodeCamp AI Agents course (Mumshad)
> **Date:** 2026-07-10
> **Status:** Green Room — needs Jordan to pick direction

---

## Idea 1: Agent Guardrail Plugin (Agent Kit)

**The gap:** We ship x402 payments, ERC-8004 identity, MCP tools — but no security layer. Every major crypto hack we've watched (Banker clipboard drainer, Injective npm attack, supply chain compromises) followed the same pattern: a trusted package or input turned malicious. Our Agent Kit installs on people's machines with access to their keys, wallets, and API secrets. We can't ship that without guardrails.

**The build:** An `agent-guard` security middleware plugin for Agent Kit that addresses the attack vectors the industry has already proven:

| Threat | How We've Seen It | Guardrail Response |
|--------|------------------|-------------------|
| **Supply chain compromise** | Injective npm — malicious package version pushed before detection | Package integrity verification, signed releases, checksum pinning |
| **Clipboard/key theft** | Banker malware — intercepted clipboard to drain wallets | Warn on private key exposure in logs/outputs, never write keys to disk unencrypted |
| **Dependency confusion** | PyPI/npm — attacker publishes same-name package to public registry | Dependency allowlisting, install-from-git-only mode for critical packages |
| **Malicious plugin behavior** | Compromised plugin exfiltrates env vars | Plugin sandboxing — restrict filesystem/network/env access per manifest |
| **Output injection** | Agent returns malformed data that executes on client | Output validation against schema (Output Enforcer pattern) |
| **Rate abuse** | Same API key called 10K times/min from different agents | Per-identity rate limiting, billing caps, circuit breaker |
| **Reputation attacks** | Bad agent builds history to appear trustworthy | On-chain reputation verification via ERC-8004 feedback |

**Why us:** No one in the Agent Kit space has security as a first-class feature. Every "agent framework" ships raw tool access and assumes the user manages risk. The Guardrail Plugin is the trust layer — agents that run with guardrails enabled can prove it.

**Effort:** 3-4 days to prototype
**Tag:** #notebooklm #guardrails

---

## Idea 2: Agent Personality Framework

**The gap:** Our Agent Companion needs a personality system for its gaming AI. Gentech and Forge already have distinct "personalities" but they're hardcoded in prompts, not configurable.

**The build:** A personality profile system:
- Profiles: Analyst (precise, data-heavy), Creative (expressive, experimental), Guardian (cautious, approval-heavy)
- Swappable per session or per task
- Stored as ERC-8004 agent metadata (portable across platforms)
- Controls: tone, verbosity, risk tolerance, autonomy level

**Immediate use:** Agent Companion — Player 2 can be "tactical commander" or "chaos gremlin" depending on personality selected

**Product path:** Personality marketplace — agents buy/sell personality profiles as NFTs or ERC-20 tokens

**Effort:** 1 day to spec, 2 days to prototype on Agent Companion
**Tag:** #notebooklm #briefing

---

## Idea 3: Human-in-the-Loop Approval Layer

**The gap:** Q402 has `confirm:true` and `consentToken` but that pattern lives only in payments. What about other agent actions — posting content, deploying contracts, modifying infrastructure?

**The build:** A generalized approval middleware:
- Pre-flight approval for any agent action over a configurable threshold
- Escalation chain: agent decides → human reviews → approves/rejects
- Delivered via Telegram inline buttons (✅ Approve / ❌ Reject)
- Timeout: auto-reject after N minutes
- Audit log on-chain via ERC-8004 feedback

**Already have:** The Telegram delivery infra, the payment consent pattern, Escrow dispute model. This is stitching them together.

**Why it matters:** As agents become more autonomous, the "what if it does something dumb" question gets louder. An explicit approval layer is the answer — and it's a feature enterprise buyers ask for first.

**Effort:** 2 days to wire up Telegram buttons + hook into Agent Kit
**Tag:** #notebooklm #podcast

---

## Idea 4: Structured Output Enforcer (Agent Kit Plugin)

**The gap:** Course emphasises structured outputs. We use MCP with typed tool schemas, but nothing enforces that the *actual output* matches the *declared schema*. One agent's sloppy JSON breaks every downstream consumer.

**The build:** A pydantic-based output validator:
- Declare output schema per tool (we already have this in MCP)
- Validate every output automatically before it leaves the agent
- On mismatch: auto-retry with temperature=0 or log + surface to developer
- Streaming mode: validate chunks as they arrive

**Effort:** Half day — mostly wrapping existing pydantic/mypy patterns into a plugin hook
**Tag:** #notebooklm

---

## Summary

| Idea | Impact | Effort | Ready for |
|------|--------|--------|-----------|
| Guardrail Plugin | High — trust differentiator | 2-3 days | Prototype |
| Personality Framework | Medium — immediate use in Companion | 1-2 days | Spec + prototype |
| Human-in-the-Loop Layer | High — enterprise feature | 2 days | Prototype |
| Output Enforcer | Medium — quality of life | 0.5 day | Ship fast |

**My pick:** Start with the **Output Enforcer** (half day, immediate value) and the **Guardrail Plugin** (differentiated, fills a real gap). Personality and HITL are worth but need more design work.

Jordan — which direction hits for you?
