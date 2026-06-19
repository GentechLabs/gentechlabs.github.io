# WURK.FUN MCP Server Install Log

**Date:** 2026-06-18
**Installed by:** Hermes Agent (gentech profile)
**Hermes version:** v0.16.0 (2026.6.5)

## What was done

1. **Checked config** — No existing WURK MCP config in `~/.hermes/profiles/gentech/config.yaml`.
2. **Ran install** — `hermes mcp add wurk --url https://wurkapi.fun/mcp`
   - No authentication required (public API).
   - All 6 tools enabled.
3. **Ran test** — `hermes mcp test wurk`
   - Connection: ✓ (926ms)
   - Transport: HTTP → https://wurkapi.fun/mcp
   - Tools discovered: 6/6

## MCP Tools Installed

| Tool | Description |
|------|-------------|
| `wurk_services` | List all supported WURK growth services + pricing hints (free) |
| `wurk_buy` | Buy any WURK quick service via one unified tool |
| `wurk_job_pay` | Pay for an existing WURK job by ID |
| `wurk_direct_pay` | Send a direct USDC payment to a Solana address |
| `wurk_agent_help` | Agent-to-human (agent help): create a paid micro-task on WURK |
| `wurk_job_status` | Fetch job status + submissions count (free) |

## Manual config (for reference)

If `hermes mcp add` fails, add this to `~/.hermes/profiles/gentech/config.yaml`:

```yaml
mcp:
  wurk:
    transport: http
    url: https://wurkapi.fun/mcp
    auth: none
    enabled: true
    tools:
      - wurk_services
      - wurk_buy
      - wurk_job_pay
      - wurk_direct_pay
      - wurk_agent_help
      - wurk_job_status
```

## Notes

- x402 v2 on Solana — needs PayAI facilitator (Ampersend only does v1 on Base)
- No auth required for MCP connection (payment handled per-tool at runtime)
- MCP session requires initialize handshake (handled by `hermes mcp add`)
- Accept header: `application/json, text/event-stream`
- API base: https://wurkapi.fun
- Skill docs: `~/.hermes/profiles/gentech/skills/gentech-ops/wurk-fun-integration/SKILL.md`

## Status: ✅ INSTALLED & TESTED

---

## Live Test Attempt — Agent-Human Microtask

**Date:** 2026-06-18 17:30 UTC
**Task:** Create agent-help job for GenTech Journal feedback
**Recipients:** 3 humans at $0.025 each = $0.075 total

### Flow Verified:
1. ✅ `wurk_services` — listed 30+ services with pricing
2. ✅ `wurk_agent_help create` — task created, x402 payment challenge received
3. ✅ Payment challenge includes: wallet address, amount (75000 USDC lamports), network (Solana), fee payer info
4. ⏳ **BLOCKED:** No funded Solana wallet. Need ~$5 USDC on Solana to test.

### Payment Details Received:
- Amount: 0.075 USDC (75000 lamports)
- Network: Solana
- Wallet: SAT8g2xU7AFy7eUmNJ9SrM6yLo7LDci13GXJhEz9k
- Fee payer: 2wKuLpR9q6wXYqpwpw8Gr2NvWxKBqM4PPJKiQfoxHDBg4
- Timeout: 60 seconds

### Next Steps:
1. Fund test wallet with $5 USDC on Solana
2. Sign payment with wallet
3. Complete first agent-to-human microtask
4. Document full end-to-end flow
