# Composio Research — Authorized-Proxy Layer for GTA

**Date:** 2026-08-03
**Requested by Jordan:** "Composio has made their main skill open source — could let the agent sign into your accounts."
**Goal:** Assess whether Composio unlocks GTA's authorized-proxy layer (agent signs into and operates a user's accounts).

---

## The critical honest finding (CORRECTED Aug 3 after Jordan shared the repo)

**Jordan was right — the full SDK is open-sourced.** `ComposioHQ/composio` (29.5k★, MIT, active) contains:
- **Python SDK** (`python/`) and **TypeScript SDK** (`ts/`) — fully open, including tool calling, `auth_configs`, `connected_accounts`, MCP support, `tool_router`, provider adapters (OpenAI/Anthropic/Gemini/CrewAI/LangChain etc.)
- Verified locally: cloned `next` branch, MIT license, auth + connected-accounts + tool-router code all present in the repo.

**BUT — and this is the nuance that decides the architecture — the AUTH BACKEND is still their cloud.**
- The SDK defaults to `environment="production"` (Composio's hosted API), and reads `COMPOSIO_BASE_URL` only if set.
- The repo has **no self-hostable server** — no docker-compose, no backend/ dir, no local execution engine.
- So: the **client** is fully self-hostable, but the **server that stores/refreshes OAuth tokens and hosts the tool execution** is not in the open repo.

**Implication for GTA's authorized-proxy layer:**
- The open SDK is far more useful than "just skill docs" (my earlier under-count). We can build the GTA client on it.
- BUT self-hosting the full auth/execution backend still means building the server side ourselves, OR pointing the SDK at Composio's cloud (`COMPOSIO_API_KEY`).

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
