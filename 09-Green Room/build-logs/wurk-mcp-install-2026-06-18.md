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
