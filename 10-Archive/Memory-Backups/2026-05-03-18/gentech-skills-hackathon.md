---
name: hackathon
description: "End-to-end hackathon workflows for Hermes agents: opportunity tracking, idea research & competitive analysis, tool/resource selection, and project bootstrap (especially Solana/Colosseum). Covers tracking deadlines, vetting ideas with Copilot, choosing sponsor tools, and bootstrapping Anchor projects with mid-event integration."
tags: [hackathon, colosseum, solana, research, bootstrap, integration]
trigger: "When the user is working on a hackathon — researching opportunities, evaluating ideas, selecting tools, or bootstrapping a project (especially Solana/Colosseum). Load this umbrella to access all hackathon-related skill modules."
related_skills:
  - defi  # for DeFi-specific hackathon projects
  - protocol-ecosystem-scan  # pre-hackathon landscape review
version: 1.0.0
author: Gentech
---

# Hackathon Workflows (Umbrella)

This umbrella aggregates the full hackathon lifecycle: discovering and tracking events, researching ideas and competitive landscapes, selecting the right tools and resources, and bootstrapping the project (with special focus on Solana/Colosseum hackathons). Each subsection below is a self-contained skill module; their complete original content lives in `references/`.

> **Consolidated skills:** `hackathon-tracker`, `colosseum-copilot`, `colosseum-resources`, `solana-hackathon-build`.

## Quick Decision Table

| User Intent | Go To Section |
|-------------|---------------|
| "Find/ track upcoming hackathons, deadlines" | [1. Hackathon Tracker](#1-hackathon-tracker-research--vault-integration) |
| "Research an idea, check competitive landscape" | [2. Colosseum Copilot](#2-colosseum-copilot-idea-research--competitive-intel) |
| "Which sponsor tools/SDKs should I use?" | [3. Colosseum Resources](#3-colosseum-resources-tool--resource-advisor) |
| "Bootstrap Solana project, integrate sponsor mid-event" | [4. Solana Hackathon Build](#4-solana-hackathon-build-bootstrap--mid-event-integration) |

---

## 1. Hackathon Tracker (Research + Vault Integration)

**Original skill:** `hackathon-tracker`

Research, evaluate, and add hackathons to the vault tracking system. Covers Devpost/web research, deadline management, and multi-file vault updates.

### Workflow
1. Research the hackathon — Devpost primary; extract name, deadline, prize, tech stack, submission format, team size, location
2. Evaluate fit — AAE narrative alignment, tech stack overlap, timeline conflicts, prize-effort ratio
3. Competitive landscape analysis (via Colosseum Copilot) — identify gaps, avoid crowded spaces
4. Update vault files (roster, active list, command center, detail note) in order
5. Git commit

### Status Emojis
🔴 PRIMARY, 🟡 QUEUED, 🟢 REGISTERED, ⏸️ PAUSED, ⛔ WITHDRAWN, ⚪ FUTURE

### Pitfalls
- Update ALL vault files
- Check for deadline conflicts
- Run competitive analysis BEFORE building

> **Full canonical content:** See `references/hackathon-tracker-full.md` for complete vault file structure, competitive analysis integration, and verification checklist.

---

## 2. Colosseum Copilot (Idea Research + Competitive Intel)

**Original skill:** `colosseum-copilot`

Research Solana/crypto startup opportunities using builder project history, crypto archives, investor theses, and market signals. Answers conversationally by default; runs full 8-step deep research workflow on explicit opt-in ("vet this idea", "deep dive").

### Modes
- **Conversational (default):** Targeted API calls with evidence coverage; cite sources inline; offer deep-dive
- **Deep Dive (explicit):** Full 8-step workflow; activates on "vet this idea", "deep dive", etc.

### Evidence Floors (Conversational)
| Query Type | Required Sources |
|------------|-----------------|
| Pure retrieval | Builder projects |
| Archive retrieval | Archive documents |
| Comparison | Builder projects + archive |
| Evaluative | Builder projects + archive + current landscape |
| Build guidance | Builder projects + archive + incumbent/landscape |

### Quality Checks
- Archive integration rule (at least one archive search)
- Accelerator/winner portfolio checks
- Freshness/temporal anchoring (use `hackathon.startDate`)
- Entity coverage check (address each named entity)
- Landscape check (never claim "nobody" without accelerator check)

### Auth Pre-Flight
Verify `COLOSSEUM_COPILOT_PAT` and `COLOSSEUM_COPILOT_API_BASE`; call `GET /status` first.

### Key Endpoints
`/search/projects`, `/search/archives`, `/projects/by-slug/:slug`, `/archives/:documentId`, `/analyze`, `/compare`, `/clusters/:key`, `/filters`, `/source-suggestions`, `/feedback`.

> **Full canonical content:** See `references/colosseum-copilot-full.md` for auth steps, endpoint docs, error handling, and deep-dive verification checklist.

---

## 3. Colosseum Resources (Tool & Resource Advisor)

**Original skill:** `colosseum-resources`

Solana hackathon resource advisor for Colosseum builders. Recommends sponsor tools, SDKs, RPC providers, wallets, identity, payments, privacy, governance, NFT, game, mobile, DeFi, developer resources.

### Recommendation Workflow
1. Understand the builder's project (core mechanism, user surface, constraints)
2. Pick 2–4 tools/resources from live corpus that fit
3. For each: what it does, why it fits, concrete integration step, docs link, skill install command (if `hasSkill`)

### Data Source
Fetch `https://ColosseumOrg.github.io/hackathon-resources/current.json` before recommending. Includes sponsors, RPC providers, resources, resourceGroups.

### Worked Examples
- Privacy DeFi: Arcium + RPC provider + Squads
- Consumer wallet app: Phantom + MoonPay/Swig + mobile resources
- NFT marketplace: Metaplex + Phantom + RPC provider

### Standards
Never rank sponsors alphabetically; prefer specific matches. If corpus lacks strong match, state it directly.

> **Full canonical content:** See `references/colosseum-resources-full.md` for question guidelines, recommendation standards, and worked examples.

---

## 4. Solana Hackathon Build (Bootstrap + Mid-Event Integration)

**Original skill:** `solana-hackathon-build`

Bootstrap a Solana hackathon project from zero — toolchain install, Anchor project init, smart contract scaffolding, off-chain agent setup, and demo video prep. Also covers mid-hackathon sponsor integration.

### Toolchain Install
```bash
# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"

# Solana CLI
sh -c "$(curl -sSfL https://release.anza.xyz/stable/install)"
export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"

# Anchor
cargo install --git https://github.com/coral-xyz/anchor avm --force
avm install latest && avm use latest
```

### Project Initialization
```bash
anchor init <project-name> --template multiple  # multi-program workspace
```

### Mid-Hackathon Sponsor Integration (5 Layers)
1. Evaluate & Decide (10 min) — complementary vs competing vs parallel; 1-paragraph strategy
2. On-Chain Programs (Rust/Anchor) — add instructions, state fields, errors; update modules
3. Client SDK (TypeScript) — integration module with types + functions; update index header
4. Documentation — submission writeup, social thread, integration strategy doc
5. Tests & Verification — integration test stubs, E2E lifecycle test, `cargo check`

### Pitfalls
- Solana CLI PATH export every session
- Anchor version lock — pin in `Anchor.toml`
- Devnet SOL resets
- PDA collisions — include owner pubkey in seeds
- Interactive CLIs may need piped input (e.g., `agent-starter-pack`)

> **Full canonical content:** See `references/solana-hackathon-build-full.md` for complete Anchor patterns, program architecture, sponsor integration examples (OOBE), and verification checklist.

---

## Related Umbrellas

- **`defi`** — for deeper DeFi LP operations, on-chain reads, security intel (often used alongside hackathon DeFi projects)
- **`protocol-ecosystem-scan`** — useful for pre-hackathon protocol research and competitor mapping

---

## References (Session-Specific Detail)

- `references/hackathon-tracker-full.md`
- `references/colosseum-copilot-full.md`
- `references/colosseum-resources-full.md`
- `references/solana-hackathon-build-full.md`

These preserve the complete original SKILL.md content of each absorbed skill for detailed recovery.