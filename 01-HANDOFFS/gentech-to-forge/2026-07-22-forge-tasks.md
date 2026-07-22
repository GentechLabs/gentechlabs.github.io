# Forge Task List — 2026-07-22

**Comprehensive handoff — supersedes auto-generated version.**
Items sorted by priority. In-progress items from last session included.

---

## 🚨 URGENT — Today's Priority

### [URGENT] #4 — x402 Foundation — Protocol Contributions (medium)
**Status:** ⏳ In Progress — PR not yet submitted
**What:** Multi-facilitator FastAPI example built at `10-Labs/x402-multi-facilitator-example/`. Two PRs already merged this week. Need to submit the third.
**Action:**
1. Re-fork x402-foundation/x402 (previous fork was deleted)
2. Copy `10-Labs/x402-multi-facilitator-example/` into the fork
3. `gh pr create` with PR_README.md as body
4. Join Slack (slack.x402.org) — notifications + further protocol contributions
**Deadline:** This week — we have rare production x402 expertise

### [URGENT] #7 — Cloudflare Gateway — x402 Playground (easy)
**Status:** ⏸️ Blocked on Jordan's waitlist approval
**What:** When approved: deploy our x402 gateway on Cloudflare Workers (withX402() support built-in). Also explore Cloudflare Agents SDK + MCP x402 integration.
**Action:** Monitor waitlist status. When approved, deploy immediately.

---

## 🔥 HIGH Priority

### [HIGH] #3 — Sell APIs to AI Agents — Phase 2: Deploy & List (medium)
**Status:** ▶️ Ready
**What:** 
1. Deploy Rugcheck v2 API to port 8088 (already running)
2. Add Q402 payment middleware
3. List in pay-skills catalog — submit GenTech as a provider directly (PR #154 doesn't exist, PRs jump #153→#155)
4. Build Agent Credit Score API wrapper

### [HIGH] #24 — Q402 × Agent Kit Integration (medium)
**Status:** ⏳ In Progress — Q402 MCP wired, Agent Kit module built
**What:** 
1. Verify Trust Receipt creation (sandbox mode)
2. Test AAE enforcement hooks (max amount, recipient allowlist)
3. Package as Agent Kit module — `10-Labs/gentech_agent_kit.py` already has Q402Client, AAEEnforcement, TrustReceipt classes
4. Flip `Q402_ENABLE_REAL_PAYMENTS=1` to go live when ready
**Note:** Q402 trial key live (q402_live_37..., 2000 credits, 25 days left)

### [HIGH] #8 — Agentic Treasury — Build P2P Causes + Yield Brain (hard)
**Status:** ▶️ Spec complete — build phase
**What:** Build the three pillars: Yield Brain (AAE), Payment Router (x402), P2P Causes (funding platform). Spec at `00-HQ/agentic-treasury-spec.md` (1,460 lines, 61 KB).

### [HIGH] #16 — PixelRAG — Visual Search Demo (medium)
**Status:** ✅ Installed — test demo
**What:** Already installed on lab laptop (RTX 3070). pixelshot CDP renders URLs to screenshot tiles in <1s. Tested on gentechlabs.net + Wikipedia. Run demo against Vanito's Hub + Jordan's Hub. Show output.

---

## 📋 MEDIUM Priority

### [MEDIUM] #38 — Agent Arcade — Build Phase 1 (hard)
**Status:** ▶️ Spec complete — build phase
**What:** Browser-based agent arcade. Spec at `10-Labs/agent-arcade-build-queue.md` (895 lines, 54 KB). MCP game protocol, poker cabinet, ARC token, x402/Q402 payment flow.

### [MEDIUM] #47 — Remotion Video Pipeline — Social Media Engine Extension (medium)
**Status:** ✅ Scaffolded — extend
**What:** Remotion project built with branded video template. 2 renders produced (social.mp4, data-slide.mp4). Files at `gentech-video-pipeline/`. Extend with Social Media Engine cron integration.

### [MEDIUM] #58 — Animate $TREASURY Token Image (easy)
**Status:** ▶️ Ready
**What:** Animate the $TREASURY token image (gold vault door with G logo, dark navy background, gold light rays). Make the gold shine/glow animate around the vault door. Output as short looping MP4 or GIF. Source: https://v3b.fal.media/files/b/0aa334a4/CrD_V2-V1iUoc3EUGlDJQ_nc4Kou0V.png

---

## 🟢 LOW Priority

### [LOW] #27 — Prediction Market — Fed Decision Betting (medium)
**Status:** ✅ Design complete
**What:** Architecture design at `10-Labs/prediction-market-design.md` (10 sections, 12.8K chars). Smart contracts, x402 integration, UI/UX mockups.

---

## 🚫 Blocked Items

| Item | Blocker | Notes |
|------|---------|-------|
| #7 Cloudflare Gateway | Jordan's waitlist | Monitor for approval |
| #35 PixelRAG x Agent Kit | Blocked on #16 PixelRAG demo | After demo works on laptop |

---

## 🤖 Gentech Working (FYI — cloud items, not your lane)

- ✅ #1 Subscription Hub — SHIPPED (Q402 /pay URLs wired)
- #13 Circle Developer Grant — pending (needs hackathon MVP first)
- #25 Superpowers Plugin — pending (needs Jordan's manual PR)
- #10 NVIDIA SkillSpector — pending (low priority)

---

## 📊 Queue Snapshot

**40 total** · 5 shipped · 2 in_progress · 27 pending · 11 blocked · 19 needs_jordan

*Generated 2026-07-22 04:10 UTC — Gentech Nightly Build*
