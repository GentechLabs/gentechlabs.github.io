# Jordan's Action Items — Orchestrator List

## 🔴 Manual GitHub Forks — API BLOCKED (Aug 2, verified)

GitHub API refuses forks with `403: You cannot fork this repository at this time` — this is the known account restriction, not a rate limit. **Jintech cannot fork by itself.** Manual fork via GitHub web UI (one click each): go to repo page → Fork → create. ~2 minutes total.

- [ ] Fork **XRPLF/xrpl-dev-portal** → https://github.com/XRPLF/xrpl-dev-portal/fork (confirmed exists)
- [ ] Fork **Dexter-DAO/dexter** → ⚠️ name may be stale (API 404) — search GitHub for the current Dexter-DAO repo before forking
- [ ] Fork **near-examples/near-ai-agent-market** → ⚠️ name may be stale (API 404) — search GitHub for the current near AI agent market repo before forking
- [ ] Fork **diegosouzapw/OmniRoute** → https://github.com/diegosouzapw/OmniRoute/fork — needed to submit our **#9251 STREAM_EARLY_EOF breaker fix** (committed `71d2ea3`, tests 13/13 + 27/27 green, ready in /tmp/OmniRoute). Tell Gentech the fork URL → Gentech pushes branch + opens PR "Closes #9251"

Then tell Gentech the fork URLs → Gentech clones, rebrands, pushes.

## ✅ GitHub Sweep results (22:45 UTC Aug 2)

- **King's Gambit pushed** ✅ → https://github.com/ProtoJay4789/kings-gambit-arcade (public, both commits incl. Kimi-2.7 fixes)
- **oh-my-hermes #771** — ❌ NOT ours. mrmixx-max opened PR #771 (18:09 UTC, before our sweep) with the same Windows-compat fix. Contribution is moot — drop or pick a different OHM issue
- **3 forks** — ❌ API-blocked (403), see manual list above

## 🔴 WhatsApp Cloud API — META CREDENTIALS NEEDED (Aug 2)

Goal: finish the WhatsApp integration via Meta's official Business Cloud API so Vanito can talk to Gentech on WhatsApp. Hermes has a native adapter (`hermes whatsapp-cloud` wizard). Infrastructure is PRE-STAGED on the VPS (nginx route `https://gentechlabs.net/whatsapp/webhook` → localhost:8096, env template in `.env`). **Blocked on Jordan creating the Meta app + providing credentials.**

- [ ] Create Meta Business account: business.facebook.com (if not already have one)
- [ ] Create Meta app → use case "Connect with customers through WhatsApp" → developers.facebook.com/apps
- [ ] From App Dashboard → WhatsApp → API Setup, grab: **Phone Number ID** (15-17 digits, NOT the phone number), **Access Token** (starts EAA; for production make a System User permanent token with `business_management`, `whatsapp_business_messaging`, `whatsapp_business_management`)
- [ ] From Settings → Basic: **App Secret** (32-char hex)
- [ ] Add recipient numbers to the dev-mode whitelist (API Setup → To → Manage phone number list) — at least Vanito's number
- [ ] Tell Gentech the values → Gentech runs `hermes whatsapp-cloud` wizard, fills env, configures webhook in Meta dashboard, restarts gateway
- [ ] Optional polish: business phone number display name + profile pic at business.facebook.com/wa/manage/phone-numbers

## Marketplace Scout — Jul 29

| # | Item | Priority | Gate | Notes |
|---|------|----------|------|-------|
| 1 | **Pay-Skills PR #190 — Follow up** | High | Human review | PR to solana-foundation/pay-skills is "mergeable" but awaiting human review. Check status and nudge maintainer. |
| 2 | **Virtuals ACP — Create account** | High | Account creation | Need to register at virtuals.io, create agent profile, list services. |
| 3 | **AgentScan — Complete profile** | Medium | Wallet connection | Registered (#1770) but profile incomplete. Need to fill in agent details. |
| 4 | **Swarms Marketplace — Update listing** | High | Manual edit | Stale listing (defi-lp-monitor, $9.99 one-time). Needs: rename to "GenTech Labs x402 Gateway", enable x402 toggle, update description, add tags. Jordan logs in and edits. |
| 5 | **OKX AI — Resubmit for review** | Medium | Dashboard | A2A node installed. Need to resubmit listing for review. |
| 6 | **Atelier — Update agent profile** | Medium | Dashboard | Add new services (Compliance Scanner, Agent Credit Score, Gaming APIs) to listing. |

## 🟡 Gentech Build Decisions — NEED YOUR GREENLIGHT (Aug 3)

All 21 Gentech cloud items are decision-gated (need a yes/no or config value from you). Grouped by how quick they are to unblock. **Reply with item # + "go" to greenlight, or "skip" to drop.**

**Quick decisions (reply in chat, ~30s each):**
- [ ] **#3** FrameForge — AI Storyboard Service (previs pipeline). GO?
- [ ] **#5** Open Generative AI — Self-Host AI Media Studio. GO?
- [ ] **#8** Agent Warfare — Archetype/Class system. GO?
- [ ] **#9** Agent Warfare — Procedural Map Gen. GO?
- [ ] **#17** ACE-Step UI — Arcade Soundtrack System. GO?
- [ ] **#18** GeoLibre — GIS Data Pipeline for DogFighters. GO?
- [ ] **#21** awesome-mcp-servers — contribute x402/MCP listings. GO?
- [ ] **#26** awesome-selfhosted — audit for stack gaps. GO?

**Needs a config value from you:**
- [ ] **#7** Algorand x402 Challenge — Composite Entry ($100K+500K ALGO). Confirm entry + wallet?
- [ ] **#30** DataHub Agent Hackathon — MCP Context Agent (0.5K). Confirm submission?
- [ ] **#32** Model Strength Score — greenlight the build (score 0-850)? GO?
- [ ] **#22** Syra Marketplace — register x402 services. Confirm scope?

**Needs a fork or external setup (see fork list above):**
- [ ] **#10** ClawWork Integration — GenTech Employee Squad. (needs Multica/ClawWork setup)
- [ ] **#14** EVM Cortex — Fork + extend with x402. (needs fork)
- [ ] **#16** Cesium Flight Sim — Arcade Cabinet. (needs 3D asset decisions)
- [ ] **#23** CockroachDB × AWS — Agentic Memory ($8.75K). (needs signup)
- [ ] **#24** Paymenter x402 — WHMCS/Blesta port. (needs repo choice)

**Already action-gated / waiting on earlier steps:**
- [ ] **#20** AI Job Search — Fork + Jordan profile setup. (needs fork)

**Stale/deadline check needed:**
- [ ] **#1** Keeperhub — verify still active (was urgent)
- [ ] **#6** AI Factory Hackathon (Aug 3-10) — confirm entry
- [ ] **#25** The Great Agent Hackathon — confirm entry
- [ ] **#27** Hippocratic AI Residency — evaluate fit
- [ ] **#29** Gemini XPRIZE — confirm entry + model

**Note:** I'm working the pure-Gentech stuff autonomously (Super Arcade Tennis verified live, GitHub scheduler running). Everything above is genuinely waiting on your call.
