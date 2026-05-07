---
name: tool-evaluation-integration
description: "Systematic research, relevance assessment, and architectural integration planning for third-party tools, libraries, and external services into the GenTech agent stack."
version: 1.0.0
author: Gentech + Hermes Agent
license: MIT
metadata:
  hermes:
    tags: ["research", "evaluation", "integration", "third-party", "stack-assessment", "cost-aware", "local-first"]
    homepage: https://github.com/Gentech-Labs/gentech-vault/tree/main/03-Projects/Integrations
related_skills: ["hermes-agent", "research", "agent-coordination"]
---

# Tool Evaluation & Integration Framework

**Purpose:** When Jordan shares bookmarks, repos, or tool ideas, systematically evaluate them against GenTech's active projects and decide whether to integrate, park, or discard — with a strong **cost-aware, local-first** bias.

**Trigger:** User says "check this out", shares a GitHub link, asks "is this relevant?", or presents a tool idea during planning conversations.

---

## Evaluation Matrix

### Step 1: Context Capture
- What is this tool? (one-sentence summary)
- Where did it come from? (bookmark, research, recommendation)
- User's surface question: "Can I use my current subscription?" or "Does this need GPU?" — note the underlying cost/access concern.

### Step 2: Active Projects Check
Match against current GenTech initiatives:

| Project | Status | What would this tool enhance? |
|---------|--------|-------------------------------|
| **AAE / LFJ DeFi** | Ongoing | LP monitoring, Uniswap v4 strategies, on-chain analysis |
| **Solana Frontier Hackathon** | ⏰ May 11 deadline | AgentEscrow program, x402 payments, frontend showcase |
| **Kite AI Hackathon** | ⏰ May 17 deadline | Passport deep-dive, multi-chain identity, SPACE framework |
| **Brain + Governance Layers** | Core infra | Identity verification, autonomous control, audit trails |
| **GenTech Strategies** | Trading | Signals, portfolio tracking, market macro |
| **Travel Agent Premium Tier** | Idea stage | Voice booking, crypto payments, visual destination previews |
| **Local Workstation GPU Farm** | Planning (Wed) | Offload video/voice rendering from cloud |

### Step 3: Integration Fit Assessment
Ask:
- **Direct utility:** Does it solve a pain point we have *right now*?
- **Hackathon boost:** Could it make our demo significantly more impressive?
- **Future-proofing:** Is this a strategic capability worth prototyping?
- **Cost alignment:** Does it respect our preference for CPU/local over paid cloud GPU?
- **Maintenance burden:** Will this add technical debt or complicate our stack?
- **License compatibility:** MIT/Apache/open source? Any restrictions?

### Step 4: Decision Categories

| Verdict | Meaning | Action |
|---------|---------|--------|
| 🚀 **Core** | Essential to our stack | Install, document, integrate immediately |
| 🔧 **Integrate** | Valuable, needs work | Create integration task in Green Room |
| 🅿️ **Park** | Interesting, not now | Add to `02-Labs/skill-watchlist.md` with rationale |
| ❌ **Pass** | Not aligned | Acknowledge, archive reference, move on |

---

## Cost-Aware Local-First Priorities

**GPU/Cloud cost is a first-class constraint.** When evaluating tools:

1. **Check local operation:** Can it run on CPU? Does it need a GPU?
   - If yes on GPU: Is there a quantized/CPU mode? (GGUF, Whisper.cpp, etc.)
   - If no local option: What's the cloud cost per month? Can we prototype with free tier?

2. **Leverage the 32GB workstation:** For video/audio/ML tasks, prefer tools that can run on Jordan's home machine (edge compute) rather than renting cloud GPU.

3. **Free tier before paid:** ElevenLabs Agents, for example — use 15 free minutes for prototype; scale to paid only if traction proven.

**Result:** Most "AI" tools fall into 🔧 Integrate (with local deployment path) or 🅿️ Park (until we need cloud scale).

---

## Action Templates by Verdict

### 🚀 Core → Immediate Integration
1. Add to vault: `03-Projects/Integrations/<tool-name>/`
2. Install/deploy on server or local workstation as appropriate
3. Write a skill wrapper if needed (Hermes skill for the tool)
4. Notify team in Mess Hall with "New core tool: <tool> — now available"

### 🔧 Integrate → Create Task
1. Create handoff in Green Room: "Integrate <tool> with <project>"
2. Specify: evaluation depth, POC scope, success criteria
3. Assign to relevant department (Yoyo = devops/code, DMOB = strategies, Desmond = content/frontend)
4. Set deadline aligned to hackathon or sprint goal

### 🅿️ Park → Watchlist
1. Add to `02-Labs/skill-watchlist.md` with:
   - One-line description
   - Why it's potentially valuable
   - What project would use it
   - Conditions to revisit (e.g., "when travel agent MVP launches")
2. No deployment work; just reference for future planning

### ❌ Pass → Archive
1. Note in Mess Hall: "<tool> not a fit for current stack — [reason]"
2. Add to `10-Archive/evaluated-tools/<tool-name>.md` with brief rationale
3. Close the conversation; don't revisit unless priorities shift

---

## Special Cases

### Voice/Agents Platforms (ElevenLabs, etc.)
- Question: "Is this included in my current subscription?"
- Check pricing page → usually separate product line (Agents vs Creative/TTS)
- Answer in terms: separate billing, credit-based usage, free tier available
- Recommendation: Prototype on free tier; budget only if demo requires sustained runtime

### Knowledge Graph / Code Understanding (Understand-Anything)
- **Fit:** Core for vault navigation + hackathon demos
- **Integration path:** Install on server, point at `/root/vaults/gentech`, expose dashboard at internal URL
- **Skill needed:** Hermes skill to query graph via natural language
- **Urgency:** High — unlocks Brain layer visualization

### Map / Visualization Libraries (mapcn)
- **Fit:** Travel agent 3D tours + strategy dashboards
- **Integration path:** Add to frontend component library, demo with sample location data
- **Dependency:** Requires map provider API key (Mapbox/Google)
- **Urgency:** Medium — polish for travel MVP, optional for hackathons

### Local Compute Node Setup
- **Trigger:** User mentions "run on my computer", "avoid GPU costs"
- **Action:** Plan for Wednesday — create local Hermes profile, sync vault, task queue
- **Use cases:** Video rendering, voice synthesis, ML inference with 32GB RAM
- **Architecture:** Home machine becomes edge worker; server assigns jobs via vault; results commit back

---

## Workflow Capture Pattern

During evaluation, surface these facts:
- Tool name + URL
- License (MIT/Apache/GPL)
- Primary language/runtime (Python, JS, Rust)
- Dependencies (GPU, special hardware, paid API)
- Active development (recent commits, issues/PRs open)
- Community size (stars, forks, Discord)

Store this in a structured note under the integration path for future reference.

---

## Communication Style

**To Jordan:** Concise. State verdict + one-sentence rationale + immediate next step if relevant.
- "🚀 Core — this belongs in our vault as a native skill. Installing now."
- "🔧 Integrate — useful for travel visualizer. Creating Green Room task for Desmond."
- "🅿️ Park — neat but not urgent. Added to watchlist."
- "❌ Pass — requires paid GPU; we'll revisit if budget allows."

Never explain unless asked. The matrix speaks for itself.

---

## Pitfalls

- **Shiny object syndrome:** Don't integrate just because it's cool. Must map to an active project's needs.
- **Over-engineering:** A static map screenshot may suffice for a demo; don't build a full 3D engine unless needed.
- **License traps:** Some "free" tools have commercial-use restrictions. Check LICENSE file.
- **Abandoned repos:** Last commit >6 months ago → high maintenance risk.
- **Documentation debt:** If we adopt it, we must document it in the vault. Factor that cost into the decision.
- **Local node security:** Your home machine becomes an attack surface. Keep it patched, use SSH keys, don't run untrusted code as root.

---

## Related Skills

- `research` — systematic web search and information synthesis
- `agent-coordination` — routing integration tasks to Yoyo/DMOB/Desmond
- `hermes-agent` — spawning local agent instances on the workstation

---

*"Not every tool deserves a place in the stack. Only the ones that move our projects forward."*