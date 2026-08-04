# Composio Research — Authorized-Proxy Layer for GTA

**Date:** 2026-08-03
**Requested by Jordan:** "Composio has made their main skill open source — could let the agent sign into your accounts."
**Goal:** Assess whether Composio unlocks GTA's authorized-proxy layer (agent signs into and operates a user's accounts).

---

## The critical honest finding

**Composio open-sourced the SKILL DEFINITIONS, not the core platform.**

- Open source: `composio-community/skills` (GitHub) — the `skills/composio` skill, `awesome-claude-skills`, `awesome-codex-skills`. These are **docs + tool metadata** (what tools exist, how to call them). Free to copy, self-hostable as markdown.
- Still hosted SaaS: the **core value — managed authentication (OAuth flows, refresh tokens), credential storage, and tool execution** — runs on Composio's cloud behind `COMPOSIO_API_KEY`. This is NOT open source.

**Implication for GTA's authorized-proxy layer:**
- If we route user account sign-ins through Composio → user accounts are linked in **Composio's cloud**, executed on their infra, billed per-invocation after free tier.
- If we want truly self-hosted / no-third-party credential custody → we **build the OAuth plumbing ourselves** (the hard part Composio solves).

---

## Two paths to the authorized-proxy layer

### Path A: Composio (managed — fast, cheap to start, vendor-hosted creds)
- **Cost:** FREE tier to start (per-invocation ~$0.0001–0.001 after free). No monthly minimum to trial.
- **Setup:** `pip install composio-core` → `Composio().integrations.link('gmail')` → OAuth browser flow → agent calls `GMAIL_SEND_EMAIL` etc.
- **Pros:** weeks of OAuth work collapses to minutes. Token refresh handled. 500+ tools.
- **Cons:** user credentials live in Composio's cloud; vendor lock-in; per-call cost; can't white-label as "self-hosted."
- **Best for:** quickly proving the authorized-proxy concept + demo.

### Path B: Build OAuth ourselves (self-hosted — full control, real work)
- **Cost:** $0 (developer time only). We already have OAuth experience (Robinhood PKCE flow in `mcp-integration-strategy`).
- **Pros:** credentials never touch a third party (aligns with GTA's self-custody trust model). White-label-able. No per-call fees. We own the "agent as authorized proxy" moat.
- **Cons:** every integration needs its own OAuth + refresh + error handling (the N×M problem). 8–40 hrs per integration.
- **Best for:** the production GTA product (trust = differentiator).

---

## Recommendation

**Hybrid, staged:**
1. **Now / demo:** Use Composio free tier to PROVE the authorized-proxy loop (link one account, agent acts on it). Cheap validation of the concept Jordan wants.
2. **Product:** Build Path B (self-hosted OAuth) for the venues that matter (Coinbase already direct via CDP; Robinhood direct via MCP). We own the trust layer — that's the GTA moat.
3. **Composio's open-sourced skill docs** are still worth mining as free reference material for tool/action schemas.

**Note on Composio's auth model:** Their hosted platform stores end-user OAuth tokens; our GTA granular-permissions model (withdraw = human-confirmed) still applies on top regardless of which path.

---

## What "sign into your accounts" actually requires (honest scope)
- Per platform: OAuth app registration (we already did this for Robinhood) OR the platform's native agent rail (Coinbase CDP ✅, Robinhood MCP).
- Refresh-token lifecycle (Composio handles in Path A; we own in Path B).
- Granular permission mapping (read/trade/move/withdraw) on top.

## Status
🔭 Research done (Aug 3). **Jordan decision needed:** trial Path A (Composio free, fast demo) now, or go straight to Path B (self-hosted OAuth, more build)? Or defer until Robinhood/Coinbase-wallet done tomorrow.
