# Nightly Build — 2026-07-18

**Session:** Midnight ET (4:00 AM UTC)
**Agents:** Gentech (VPS)

---

## What Gentech Worked Tonight

### 🔍 #45 — Submit GenTech Plugin to Superpowers → RESEARCHED (not shipped)

**Finding:** The obra/superpowers repo (257k⭐) has a strict AGENTS.md that explicitly forbids agent-submitted PRs — 94% rejection rate. Key rules:
- Third-party/external projects belong in standalone plugins, not core
- PRs must be human-reviewed with the complete diff shown to the human
- Agent-submitted PRs are called out as "slop that's made of lies"
- All PRs must target the `dev` branch, fill the complete template, and identify themselves

**Action taken:** Our plugin repo (`ProtoJay4789/gentech-superpowers`) is already public on GitHub with `.claude-plugin/`, `.codex-plugin/`, and 4 x402 skills. Users can install it directly via:
```
/plugin marketplace add ProtoJay4789/gentech-superpowers
/plugin install gentech-x402
```

**Next:** Jordan should review the plugin repo and, if he wants it in the curated `obra/superpowers-marketplace`, open a human-written PR himself. Agent-submitted PRs would be rejected and damage reputation.

### 🔍 #33 — Pipecat x Voice Agent Integration → RESEARCHED

**Finding:** Pipecat (13.5k⭐, BSD-2-Clause) is a Python framework for real-time voice/multimodal AI agents. Key facts:
- 98.4% Python, 10,842 commits, 263+ contributors, highly active
- Has its own Claude Code skills marketplace at `pipecat-ai/skills`
- Actively encourages community integrations via `COMMUNITY_INTEGRATIONS.md`
- CLI: `uv tool install "pipecat-ai[cli]"`

**Three integration angles identified:**
1. Build an x402 payment processor as a community integration
2. Create a "pay-as-you-speak" voice agent demo
3. Submit to the pipecat-ai/skills marketplace

**Not built:** Requires dedicated build session — would need to install pipecat, understand processor hooks, build x402 middleware.

### Queue Updates
- Updated #45 notes with superpowers guidelines finding
- Updated #33 detail with Pipecat research results
- Timestamp updated

---

## Forge's Morning

From auto-generated handoff (`01-HANDOFFS/gentech-to-forge/2026-07-18-forge-tasks.md`):

**Desktop (9 items):**
- #28 [HIGH] PixelRAG — Visual Search Demo
- #29 [HIGH] Local TTS & Voice Cloning Pipeline
- #31 [MEDIUM] GenTech Character API — Consistent Character Gen
- #33 [HIGH] Voicebox — Open Source ElevenLabs Replacement
- #36 [HIGH] Injective × Agent Kit Integration
- #41 [HIGH] GenTech Journal — Consumer Visual Journal
- #47 [MEDIUM] Prediction Market — Fed Decision Betting
- #49 [URGENT] OKX Hackathon Submission — **DEADLINE PASSED** (Jul 17)
- #50 [HIGH] Sell APIs — Phase 2: Deploy & List

**Cloud (2 in_progress):**
- #35 [HIGH] Q402 × Agent Kit Integration
- #56 [MEDIUM] Chain PR Blitz — Avalanche AI Resources Submit

---

## Jordan Action Items

From auto-generated handoff (`01-HANDOFFS/2026-07-18-jordan-items.md`):

**Needs Action:**
- ~~Vast.ai signup~~ (removed from queue)
- #30 CMC Labs Accelerator Application
- #48 GenLayer — Builder Points + Intelligent Contract
- #44 GenTech Bank — Agent Neobank on Sana
- **#45 Superpowers Plugin** — Jordan review PR submission decision

**Needs Decision:**
- #29 Deploy Subscription Hub to gentechlabs.net — blocked on Q402 API key
- #39 AgentBridge — Deploy to Base Sepolia — needs deployer private key with testnet ETH

---

## Queue Snapshot (after tonight)
- Total: 28 | Shipped: 4 | In Progress: 3 | Pending: 20 | Blocked: 1 | Needs Jordan: 5
- Items shipped tonight: 0 (research-only session)
- Items updated: #33, #45

---

## Blockers & Notes
- Nothing shipped tonight — this was a research/maintenance session
- No high-priority gentech items could be shipped without Jordan input or API keys
- #49 OKX Hackathon deadline already passed — flagged
- #45 Superpowers submission needs human decision
