# Bags.fm Hackathon — Briefing

## Event Details
- **Platform:** DoraHacks
- **URL:** https://dorahacks.io/hackathon/the-bags-hackathon
- **Start:** April 2, 2026 (21:30 UTC)
- **Deadline:** June 1, 2026 (21:30 UTC)
- **Prize:** $1M direct + $3M ongoing support
- **Top 100:** $10K–$100K grants each
- **Registered:** 503 hackers, 41 BUIDLs

## Tracks (by weight)
1. Bags API (9)
2. Fee Sharing (8)
3. AI Agents (7)
4. Claude Skills (6)
5. DeFi (5)
6. Payments (4)
7. Privacy (3)
8. Social Finance (2)
9. Other (1)

## Our Project: Agent Trading Desk

### Concept
Multi-agent trading on Solana via Bags.fm MCP. Scout → Analyze → Trade → Report pipeline.

### Tracks Hit
- Bags API (9) — Direct REST API + SDK integration
- AI Agents (7) — Autonomous scout/analyze/trade pipeline
- DeFi (5) — Liquidity strategy and fee optimization

### Architecture
```
Scout → Analyze → Trade → Report
  │         │        │       │
  ▼         ▼        ▼       ▼
Bags MCP   Hermes   Bags    Hermes
46 tools   agents   swap    output
```

### Status
- [x] Project scaffold created
- [x] Bags SDK installed
- [x] Agent auth flow (Ed25519)
- [x] Scout module (token discovery)
- [x] Trade module (swap execution)
- [x] Main orchestrator pipeline
- [ ] Solana client integration
- [ ] LP monitoring port
- [ ] Demo video
- [ ] Submission writeup

### Competitive Landscape
- bagsflow (⭐21) — Dashboard, not an agent
- Most entries 0-star thin wrappers
- Multi-agent is genuine differentiator

### Reusable Assets
- Agent Escrow Solana (Anchor program, compiles)
- solana_client.py (wallet, tx, tokens)
- AAE LP Signal Spec (supports Solana)
- d5-lp-consolidated.py (chain-agnostic arch)
- MCP server templates (multiple)

## Next Steps
1. Jordan provides API keys (May 8)
2. Test auth flow end-to-end
3. Port LP monitoring to Solana
4. Build demo video
5. Submit

---
*Created: May 8, 2026 | Status: In Progress*
