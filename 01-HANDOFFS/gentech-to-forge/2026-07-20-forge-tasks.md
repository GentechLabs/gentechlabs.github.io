# Forge Task List — 2026-07-20

**Comprehensive handoff — supersedes auto-generated version.**
Items you can work on independently — no Jordan needed unless noted.

---

## 🖥️ Desktop — Your Lane (7 items)

### [HIGH] #3 — Sell APIs to AI Agents — Phase 2: Deploy & List (medium)
**Status:** ▶️ Ready (waiting on pay-skills PR #154 merge)
**What:** Phase 2 after pay-skills PR #154 merges. TODO: Deploy Rugcheck v2 API to port 8088, add Q402 payment middleware, list in pay-skills catalog, build Agent Credit Score API wrapper.

### [URGENT] #7 — Cloudflare Gateway — x402 Playground + Deploy GenTech on Workflows (easy)
**Status:** ⏸️ Blocked (Jordan on waitlist)
**What:** When approved: deploy our x402 gateway on Cloudflare Workers (withX402() support built-in). Also explore Cloudflare Agents SDK + MCP x402 integration.

### [HIGH] #8 — Agentic Treasury — Build P2P Causes + Yield Brain (hard)
**Status:** ▶️ Ready
**What:** Build the three pillars: Yield Brain (AAE), Payment Router (x402), P2P Causes (funding platform). Spec at 00-HQ/agentic-treasury-spec.md.

### [HIGH] #16 — PixelRAG — Visual Search Demo (medium)
**Status:** ▶️ Ready
**What:** Install on lab laptop (RTX 3070). Test pixelshot CDP. Run demo against Vanito's Hub + Jordan's Hub. Show output.

### [LOW] #27 — Prediction Market — Fed Decision Betting (medium)
**Status:** ▶️ Ready
**What:** Architecture design. Smart contracts (x402 integration). UI/UX mockups.

### [MEDIUM] #38 — Agent Arcade — Build Phase 1 (hard)
**Status:** ▶️ Ready
**What:** Browser-based agent arcade. Spec at 10-Labs/agent-arcade-build-queue.md. Lobby page, poker cabinet (already built), MCP server per game, x402 rebuys, ARC stablecoin.

### [MEDIUM] #47 — Remotion Video Pipeline — Social Media Engine Extension (medium)
**Status:** ▶️ Ready
**What:** Extend Social Media Engine cron with Remotion video rendering. Forge runs a 7pm cron on RTX 3070: picks up text draft, renders short video via Remotion (React → MP4), delivers to Entertainment group. Needs: Remotion project setup, video template components, cron job on desktop.

---

## ☁️ Cloud Items Forge Can Help With

### [HIGH] #24 — Q402 × Agent Kit Integration (medium)
**Status:** ▶️ Ready — Q402 trial key live (q402_live_37…, 2000 credits, BNB chain)
**What:** (1) Verify Trust Receipt creation, (2) test AAE enforcement hooks, (3) package as Agent Kit module.

### [HIGH] #39 — Dexter-DAO SDK Integration — Evaluate + Plan (medium)
**Status:** ▶️ Ready — Research complete
**What:** @dexterai/x402 v5.4.2 SDK. Key features: Tabs (Solana vaults, passkey-based caps), one-shot x402 across 11 chains, batch settlement (EVM), auto-discovery. Cross-pollination plan:
- Add tab middleware to our Arc x402 gateway
- Add our compliance patterns to their SDK
- Register our APIs on Dexter facilitator for auto-discovery
- **Code ready at:** `/root/dexter-sdk-full/` (Zod validation PR #36)

---

## 🧠 Gentech Working (FYI — don't duplicate)

These are being handled on the cloud side:
- **#1 Subscription Hub** — Waiting on Jordan's wallet address for Q402 payment links
- **#2 Pay-Skills PR #154** — Open, awaiting upstream review (no action since Jul 12)
- **#5 XRPL x402 Skill** — Draft ready, needs Jordan to fork + submit
- **#6 NEAR x402 PR** — Draft ready, needs Jordan to fork + submit
- **#15 Arc x402 Gateway** — 15/15 tests pass, needs Jordan's wallet to deploy
- **#37 x402 Compliance Scanner** — PR #2905 is OPEN and mergeable at x402-foundation/x402
- **#39 Dexter-DAO Integration** — Research complete, plan written
- **#28 Chain PR Blitz** — PR #443 closed (no merge), replacement #455 open

---

## 🚫 Blocked Items

| # | Item | Blocker |
|---|------|---------|
| #7 | Cloudflare Gateway | Jordan on waitlist |
| #14 | Lens AI Integration | Needs Jordan to contact Arclens team |
| #31 | AgentBridge Deploy | Needs funded Base Sepolia deployer key |
| #32 | GenTech Bank | Needs Jordan Sana account |
| #33 | CMC Labs Accelerator | Needs Jordan to submit |
| #34 | GenLayer Builder Points | Needs Jordan account |
| #35 | PixelRAG x Agent Kit | Blocked on #16 (PixelRAG demo) |

---

## How to use this

1. Pick a **Desktop** item and start working
2. When you hit a stopping point, save a brain note in `11-Mess Hall/agent-brain/`
3. When something ships, update the queue via: `assigned_to: gentech, status: shipped`
4. If you're blocked by Gentech or Jordan, tag it `blocked` + set `blocked_on`

---

*Generated 2026-07-20 12:34 UTC — Comprehensive handoff*
