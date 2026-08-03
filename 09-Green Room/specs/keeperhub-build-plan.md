# KeeperHub Agents Onchain Hackathon — Build Plan

**Source:** [DoraHacks page](https://dorahacks.io/hackathon/agents-onchain/detail)
**Date:** 2026-08-03
**Deadline:** Aug 13, 10:00 UTC (~9 days)
**Prize:** $5,000 cash (1st $2K / 2nd $1.2K / 3rd $800) + $1,000 stackable bounties (Best Onboarding UX)
**Status:** ✅ Jordan confirmed GO (Aug 3). Register today.

---

## Why we win

We are NOT starting from zero:
- Shipped the **ETHGlobal Open Agents** entry on the **0G + KeeperHub** stack in May — tooling known.
- Production **x402 gateway** + **GTA arb executor**, both onchain-ready.
- The winning move is **wiring an existing agent to execute real transactions through KeeperHub**, then filming it — not building something new.

## The one hard requirement

Every submission must include a **live transaction link** the agent actually executed through KeeperHub. Judging is weighted toward **working onchain execution over polished demos**. A demo that "almost works" is judged incomplete.

## The KeeperHub stack we plug into (all open source)

- **MCP server / CLI** — agent discovers + calls execution natively (we run Hermes with MCP)
- **x402 / MPP** — pay-per-execution over HTTP, settled onchain, indexed on x402scan.com — **our exact stack**
- **Dual-protocol routing** — auto-select x402 vs MPP
- Smart gas estimation (exponential backoff) + private routing (MEV) + audit trail + **gas sponsorship on Ethereum mainnet**

## Chosen approach

**Agent:** GTA arb executor (already needs onchain execution — no new reasoning layer).
**Execution:** wire through KeeperHub MCP server so the x402/MPP dual-routing + audit trail + gas handling are *shown*, not claimed (those are judging criteria).
**Deliverables:** GitHub repo + 1 demo video of a real transaction executing + tx link. Optional: onboarding-UX bounty (starter template or "where I got stuck" teardown — cheap add).

## Scope (tight, no creep)

1. Register on DoraHacks (Jordan, today).
2. Wire GTA arb executor to KeeperHub MCP (Gentech).
3. Get ONE real transaction executing onchain through KeeperHub (testnet → mainnet if gas sponsorship available).
4. Record demo video (real tx).
5. Assemble submission: GitHub link + video + tx link.

## Judging criteria mapping

| Criterion | How we satisfy |
|---|---|
| Executes onchain via KeeperHub | Live tx link — the core deliverable |
| Use of KeeperHub surfaces | MCP server + x402/MPP routing + audit trail |
| Reliability/observability | Show gas handling, retries, audit trail usage |
| Originality/usefulness | GTA arb executor is a real, runnable agent |
| Integration quality | Clean MCP wiring, documented |

## Risks

- **Live tx requirement** is non-negotiable — must lock a working execution path early, not day 8.
- Gas on mainnet — KeeperHub offers sponsorship; else use a cheap-chain test first.
- Bridge/relay issues (we hit Across relay failures before) — prefer a direct-execution path.

## Action items
- [ ] **Jordan:** register on DoraHacks tonight (desktop — mobile sign-up flagged as better on desktop) (agents-onchain)
- [ ] **Jordan (blocker):** create a `kh_` org API key at app.keeperhub.com → Settings → API Keys → Organisation tab. Paste it here (I'll store it in the secrets vault, never echo it). Headless VPS can't do browser OAuth, so the `kh_` key is the required auth path.
- [ ] **Gentech (after key):** register KeeperHub HTTP MCP server in Hermes with the Bearer key.
- [ ] **Gentech:** wire GTA arb executor → KeeperHub MCP (execute_transfer / execute_contract_call / execute_protocol_action path).
- [ ] **Gentech:** execute one real onchain tx via KeeperHub (proof — the non-negotiable judging requirement). Base USDC (8453) is the cheapest, no-gas path (x402 EIP-3009, facilitator pays gas).
- [ ] **Gentech:** record demo video + assemble submission (GitHub link + video + tx link).
- [ ] **Gentech:** optional — onboarding-UX bounty starter template.

## Setup notes (verified Aug 3)

**Endpoint:** `https://app.keeperhub.com/mcp` — reachable (HTTP 200, 0.16s), OAuth discovery at `/.well-known/oauth-authorization-server` returns 200.
**Hermes HTTP MCP shape** (same as existing ampersend/brickken/wurk entries):
```yaml
keeperhub:
  enabled: true
  url: https://app.keeperhub.com/mcp
  headers:
    Authorization: "Bearer kh_YOUR_KEY"
```
**Key tools** (30+ registered): `execute_transfer`, `execute_contract_call`, `execute_check_and_execute`, `get_direct_execution_status`, `search_protocol_actions`, `execute_protocol_action`, `web3/transfer-funds`, `web3/write-contract`.
**Network field accepts chain IDs as strings:** "1" (Ethereum), "11155111" (Sepolia), "8453" (Base), "42161" (Arbitrum), "137" (Polygon).
**Wallet integration:** write actions require the org's wallet integration (use `get_wallet_integration` to confirm). No per-action walletId field.
**x402 payment (paid workflows):** settle on Base USDC via EIP-3009 `TransferWithAuthorization` — facilitator pays gas, wallet only debits USDC. KeeperHub agentic wallet has server-side hard caps (100 USDC/transfer, 200 USDC/day) — fine for our small proof tx. `agentcash` alternative keeps an unencrypted key file — NOT for real funds.

### MCP wiring cross-reference (awesome-llm-apps)
Cloned at `/root/repos/awesome-llm-apps/`. The `multi_mcp_agent_router` pattern (specialist agents each connected to ONLY the MCP servers they need, routed by intent) is the right shape for wiring GTA → KeeperHub MCP — don't give the arb executor every tool, scope it to the execution tools it needs. See `a2a-trust-layer-deep-dive.md` for the governance layer that gates which agent can call which KeeperHub tool.
