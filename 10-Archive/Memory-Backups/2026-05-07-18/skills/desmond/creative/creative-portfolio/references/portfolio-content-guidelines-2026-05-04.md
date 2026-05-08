# Portfolio Content & Strategy — Session Reference (2026-05-04)

## Conversation Context
Jordan's portfolio (ProtoJay4789.github.io) got a hero avatar upgrade (emoji → real photo). Team discussed content refinements.

## Jordan's Strategic Direction

### Positioning
- **Primary:** Safety-first engineers who use AI tools efficiently
- **Secondary:** Agent stacks are amplifiers, not replacements
- **Value prop:** Provide value + save money for partners/clients
- **Tone:** Practical builder energy, not speculative AI hype

### Content Structure Preferences
1. **Tagline** — shift from generic founder to:
   "Safety-First Engineers · AI-Amplified Builders · Agent Economy Architects"
2. **Intro paragraph** (hero) — mandatory safety-first + efficiency statement
3. **Team/Agents section** — show who we are and what each delivers
4. **Projects** — top 5–10 active projects only (exclude archived)
5. **Quick Roadmap** — below projects, 3–5 bullet items (next quarter)
6. **Project count** — limit to 5–10 to avoid dilution

### Messaging Do's / Don'ts
- ✅ "AI-amplified", "efficiency-first", "reusable components save budget"
- ✅ "24/7 agent availability → faster iteration"
- ❌ Avoid: "AI-native", "fully autonomous", "agents will replace devs"
- ❌ Avoid: Hype language, speculative claims, "magic" solutions

### Project Showcase Order (proposed)
**Tier 1 — Currently Building:**
1. AgentEscrow — trust-minimized agent payment infrastructure
2. Kite-AI Commerce — Hermes × Kite AI agentic commerce
3. Colosseum Frontier — Solana AI agent battleground (hackathon)

**Tier 2 — Infrastructure/Tooling:**
4. Agent Economy Framework (AAE) — reusable coordination patterns
5. Birdeye Adapter (BIP) — on-chain market data feed
6. Bug Bounty Platforms — security audit discovery
7. Agent Starter Pack — templates/boilerplates (community)

**Tier 3 — Specialized/Research:**
8. VideoAgent — local-first voice/video processing
9. Almanak SDK — backtesting & portfolio valuation
10. Gentech Agency — orchestration layer itself

**Status tagging:**
- 🚧 Building / 🛠️ In progress
- ✅ Built / Deployed
- 🔒 Audit phase
- 📦 Archived (don't show)

### Team Roles (Agents)
- **Desmond** — Creative: docs, social, hackathon writeups, brand voice, visual assets
- **DMOB** — Dev/Research: code quality, technical review, architecture decisions, testing
- **YoYo** — Research/Market: data accuracy, DeFi insights, competitive analysis, metrics
- **Jordan** — Orchestrator: funding, strategy, hackathon leads, partner connections

**Tagline for team card:**
"Each agent is a force-multiplier — together we ship like 4–6 engineers."

---

## Technical Decisions

### GitHub Auth Flow
- Token provided by Jordan: `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`
- Saved to: `/root/vaults/gentech/.env` as `GITHUB_PAT=...`
- Authenticated via: `echo "<token>" | gh auth login --with-token`
- Git helper: `gh` CLI (HTTPS) — preferred over SSH
- SSH key available at `/root/.ssh/hermes-brain-backup` but not loaded

### Portfolio Repo
- Clone location: `/root/portfolio/` (local)
- Remote: `git@github.com:ProtoJay4789/ProtoJay4789.github.io` (gh handles HTTPS)
- Source of truth: `/root/vaults/gentech/06-Content/portfolio-current.html`
- Asset path: `assets/jordan-avatar.png` (Jordan's JinTech headshot)
- Deployment: Copy HTML to repo → commit → push → GitHub Pages auto-deploys

### Current Deployment Status (2026-05-04)
- Commit pushed: `b2c44ce → b10c158` to `main`
- Changes: Avatar image added, CSS updated, fallback emoji retained
- Live URL: https://protojay4789.github.io/

---

## Action Items for Next Session

1. **Content updates (Desmond to implement):**
   - Replace tagline with safety-first phrasing
   - Add 2–3 sentence intro paragraph in hero
   - Add "Gentech Agents" section with roles + value props
   - Build project grid with top 5–10 curated entries (from vault READMEs)
   - Add quick roadmap section (Jordan to provide bullets)
   - Consider adding stats card (GitHub stars, hackathon count) — need numbers from DMOB/YoYo

2. **Team input needed:**
   - DMOB: Validate project descriptions for technical accuracy
   - YoYo: Provide any metrics (stars, followers, placements) and market-facing phrasing
   - Jordan: Confirm project list order + provide roadmap bullets

3. **Style consistency check:** Ensure color palette reverts to **blue primary** (`#3b82f6`) — current deployed uses green (`#22c55e`), which conflicts with brand guide. Plan a follow-up color-correct push.

4. **Token rotation plan:** Current token stored in `.env`; plan to rotate before expiration. Document next rotation date in vault.

---
*Reference for: portfolio content strategy, team messaging, project curation criteria*