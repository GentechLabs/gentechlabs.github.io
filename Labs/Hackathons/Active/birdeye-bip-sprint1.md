# Birdeye Agent Terminal — Sprint 1 Submission

**GitHub:** https://github.com/Gentech-Labs/birdeye-agent-terminal
**Competition:** Birdeye Data Build in Public Competition (via Superteam Earn)
**Sprint:** 1 (Apr 18–25, 2026)
**Status:** ✅ Repo pushed — need API key for live demo

---

## What We Built

Bloomberg-style CLI terminal for AI agents to query Birdeye Data via x402 pay-per-request.

- `agent.py` — Entry point, interactive mode + CLI commands
- `birdeye_client.py` — Async Birdeye API client with x402 payment tracking
- `terminal_ui.py` — Rich terminal UI (tables, panels, live display)
- `config.py` — Endpoint config + defaults

## Judging Criteria Alignment

| Criteria | Our Play |
|---|---|
| Community Support | X thread (Desmond drafted Apr 21), GitHub stars |
| Product Utility | Real agent workflow — trending + security scan |
| Technical Depth | x402 payment flow, async client, 17 endpoints |
| Presentation | Clean README, demo video (need to record) |

## Remaining for Sprint 1

- [ ] Get Birdeye API key (bds.birdeye.so)
- [ ] Record demo video (screen capture of terminal)
- [ ] Post X thread with demo
- [ ] Submit to Superteam Earn listing

## x402 Integration Status

- ✅ Payment tracking (logs every request + cost)
- ✅ 402 response handler (parses payment info)
- 🔜 Full Solana payment signing (Sprint 2)
- 🔜 MCP server integration (Sprint 2-3)
