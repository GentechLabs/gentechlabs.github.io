# Handoff: Gentech → Forge — Jul 15, 2026

> **From:** Gentech (overnight / daytime build)
> **To:** Forge (next session)

---

## What Was Done

### KytyPS5 — Phase 1 Complete ✅
- Fork created: `github.com/ProtoJay4789/KytyPS5`
- Compat DB populated with 7 game entries (Dreaming Sarah InGame, GTA V InGame, EA UFC 5 broken, etc.)
- CONTRIBUTING.md written — contribution guide for the community
- Two branches pushed and ready on our fork: `add-compat-db`, `add-contributing`
- **Blocker:** Nmzik has PRs restricted on his repo. PRs can't go through yet.
- Intro message drafted at `10-Labs/kytyps5-nmzik-intro.md` — ready to send when we find a channel
- **Phase 2 (Forge):** Download v0.0.3 release, test games on Windows with Forge, file detailed bug reports with logs. This builds the relationship naturally.

### Build Queue — Cleaned Up ✅
- **Cancelled:** #0 OKX Hackathon (skipped, Jordan decided Algorand is next)
- **Cancelled:** #40 Sui Overflow 2026 (skipped)
- **Updated:** #21 RomM → status: "testing" (Jordan testing on desktop today)
- **Updated:** #48 KytyPS5 → Phase 1 complete, waiting on Nmzik
- Algorand is the priority lane (#30, #29, #32, #31)

### PR Scout — 2 New Submissions ✅
- `punkpeye/awesome-mcp-devtools` #236 — GenTech Agent Kit added to Frameworks (~471⭐)
- `caramaschiHG/awesome-ai-agents-2026` #443 — GenTech Agent Kit in Agent Frameworks (~1.5k⭐)
- All 27 open PRs checked — nothing merged, all still pending maintainer review

### Model Configuration — Nous Bleed Stopped ✅
- **Found root cause:** Auxiliary services (vision, web_extract, compression, skills_hub, approval, mcp, triage_specifier, curator, session_search) were all on `provider: auto`, silently routing through Nous Portal for every task
- **Fix:** Pinned all 9 auxiliary services to `opencode-go` with `deepseek-v4-flash`
- Main model was already on OpenCode Go — no change needed
- Jordan's Nous subscription usage should stop draining

### Hermes Web Bridge — Deployed ✅
- FastAPI server on port 8765, systemd service (`gentech-bridge`)
- Mobile-friendly dark UI optimized for Unihertz Titan
- Exposed via Tailscale at `http://100.73.143.15:8765`
- Jordan tested — works but timed out after extended use (needs keepalive/reconnect logic)
- Saved to vault at `00-HQ/gentech-bridge.md`

---

## Build Queue Status

| # | Task | Who | Status | Notes |
|---|------|-----|--------|-------|
| 21 | RomM AI Companion | Forge/Jordan | 🔄 Testing | Jordan testing today. 27/27 tests from prior session. |
| 48 | KytyPS5 | Gentech | ⏸️ Waiting | PRs blocked by Nmzik. Fork ready. Phase 2 (testing) needs Forge on Windows. |
| 29 | Algorand Mainnet Deploy | Jordan | ⏳ Pending | Next priority lane |
| 30 | Algorand GoPlausible Auth | Jordan | ⏳ Pending | First Algorand step — join Discord, auth |
| 32 | Algorand Submission | Jordan | ⏳ Pending | |
| 31 | Algorand Volume | Jordan | ⏳ Pending | |
| 28 | PixelRAG Demo | Forge | ✅ Done | Demo script built last session |
| 33 | Voicebox TTS | Forge | 🔬 Research done | Install pending on desktop |
| 47 | Prediction Market | Forge | ⏳ Pending | |

---

## What Needs Forge (Desktop Required)

1. **KytyPS5 Phase 2** — Download v0.0.3 release, test PS5 games, file detailed bug reports with full logs. Builds relationship with Nmzik — once he sees quality reports, he may open PR channel.
2. **RomM testing** — Jordan testing today. If issues found, Forge can debug on next session.
3. **Voicebox install** — Test ElevenLabs alternatives (Chatterbox/Kokoro) on desktop.
4. **PixelRAG demo script** — Already built, could be extended for more use cases.

## What Needs Gentech (Cloud/VPS)

1. **x402scan re-scan** — Gateway has requestBody schemas now (deployed via wrangler, v2 live). Needs re-scan on x402scan.com.
2. **Algorand support** — Ready to jump on #30 when Jordan's ready.

## Risk Items

- **Web Bridge timeout** — The UI times out after extended messages. Needs frontend keepalive + server-side timeout handling improvements.
- **Nmzik access** — If he never opens PRs, our fork stays dormant. Alternative: find him on Discord/X.

---

## Vault

- `scripts/build_queue.json` — single source of truth (updated)
- `10-Labs/kytyps5-analysis.md` — full KytyPS5 analysis
- `10-Labs/kytyps5-nmzik-intro.md` — draft intro message
- `00-HQ/gentech-bridge.md` — web bridge reference
- `01-HANDOFFS/2026-07-14-session-handoff.md` — Forge's prior handoff (processed)