# Forge Task List — 2026-07-20

**⚠️ SUPERSEDES auto-generated handoff.** Read this first.

---

## 🚨 Critical Discovery — All Ecosystem PRs Were Never Submitted

**The Jul 19 ecosystem PR run failed silently.** All forks (ProtoJay4789/x402, ProtoJay4789/pay-skills, ProtoJay4789/awesome-ai-agents-2026, and 5 ecosystem forks) were deleted or never persisted. The `gh pr create` commands hit API rate limits and were never retried.

**What this means for you:**
- PR #2905 (x402 Compliance Scanner) — code exists at `/root/repos/` but was never submitted
- PR #154 (Pay-Skills) — 12 GenTech services were never listed
- All 7 ecosystem PRs (awesome-web3, awesome-agent-cortex, etc.) — never submitted
- Coinbase AgentKit PR #1375 — never submitted

**Action needed:** Re-fork each upstream repo and re-submit. This is a 15-min job if you batch it.

---

## 🖥️ Desktop — Your Lane

### [URGENT] #7 — Cloudflare Gateway — x402 Playground (easy)
**Status:** ⏳ Waiting on Jordan (on waitlist)
**What:** When approved, deploy our x402 gateway on Cloudflare Workers. Also explore Cloudflare Agents SDK + MCP x402 integration.

### [HIGH] #16 — PixelRAG — Visual Search Demo (medium)
**Status:** ▶️ Ready
**What:** Install on lab laptop (RTX 3070). Test pixelshot CDP. Run demo against Vanito's Hub + Jordan's Hub.
**Blocked by:** Nothing — go for it.

### [HIGH] #3 — Sell APIs Phase 2: Deploy & List (medium)
**Status:** ⏳ Blocked on PR re-submit
**What:** After pay-skills PR is re-submitted and merged, deploy Rugcheck v2 API to port 8088, add Q402 middleware, list in pay-skills catalog.

### [HIGH] #8 — Agentic Treasury — P2P Causes + Yield Brain (hard)
**Status:** ▶️ Ready
**What:** Three pillars: Yield Brain (AAE), Payment Router (x402), P2P Causes (funding platform). Spec at `00-HQ/agentic-treasury-spec.md`.

### [HIGH] #24 — Q402 × Agent Kit Integration (medium)
**Status:** ▶️ Ready
**What:** Q402 trial key live (q402_live_37…, 2000 credits, BNB chain). Test Trust Receipt creation, AAE enforcement hooks, package as Agent Kit module.

### [HIGH] #35 — PixelRAG x Agent Kit Integration (medium)
**Status:** 🚫 Blocked on #16
**What:** After PixelRAG demo works on laptop, build Agent Kit tool wrapper.

### [MEDIUM] #38 — Agent Arcade — Build Phase 1 (hard)
**Status:** ▶️ Ready
**What:** Browser-based agent arcade. Lobby page, poker cabinet (already built), MCP server per game, x402 rebuys, ARC stablecoin. Spec at `10-Labs/agent-arcade-build-queue.md`.

### [MEDIUM] #47 — Remotion Video Pipeline (medium)
**Status:** ▶️ Ready
**What:** Extend Social Media Engine cron with Remotion video rendering. RTX 3070 renders short videos from text drafts.

### [LOW] #27 — Prediction Market — Fed Decision Betting (medium)
**Status:** ▶️ Ready
**What:** Architecture design, smart contracts, UI/UX mockups.

---

## ☁️ Gentech Working (FYI — don't touch)
- #48 Agent Rug 2.0 — Phase 2 shipped tonight (37 new tests, agent identity endpoint)
- #1 Subscription Hub — Blocked on Jordan's wallet address
- #15 Arc x402 Gateway — 15/15 tests pass, blocked on Jordan's RECIPIENT_ADDRESS
- #5 XRPL x402 Skill — Drafted, needs Jordan to fork + submit
- #6 NEAR x402 PR — Drafted, needs Jordan to fork + submit

---

## 🚫 Blocked Items
| Item | Blocker | Unblock Path |
|------|---------|-------------|
| #35 PixelRAG x Agent Kit | #16 PixelRAG Demo | Finish #16 first |
| #2 Pay-Skills PR | Fork deleted | Re-fork + re-submit |
| #37 x402 Scanner PR | Fork deleted | Re-fork + re-submit |
| #28 Chain PR Blitz | All forks deleted | Re-fork all 7 ecosystem repos |

---

## How to use this
1. Pick a **Desktop** item and start working
2. When you hit a stopping point, save a brain note in `11-Mess Hall/agent-brain/`
3. When something ships, update the queue via `scripts/build_queue.json`
4. If you're blocked by Gentech or Jordan, tag it `blocked` + set `blocked_on`

*Generated 2026-07-20 16:39 UTC — Manual (supersedes tick-generated)*
