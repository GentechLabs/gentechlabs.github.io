# Solana as Homebase — Agentic Treasury MVP (Superteam Tranche-2 Deliverable)

**Status:** Spec — BUILDING (Aug 5)
**Grant:** Superteam Earn Agentic Engineering — Tranche 2 unlock (second $100)
**Goal:** A live, working MVP with **Solana integration** + documentable $200 coding subs.

## Why Solana is the homebase
- **USDC settlement is the point** — sub-second, sub-cent, native.
- **Cheaper than bridging** — agents pay on the destination chain directly.
- Matches the tranche-2 requirement: "live MVP + some Solana integration."

### ⭐ The real advantage: the Solana DeFi community
Solana isn't just a fast ledger — it's a **liquidity network with its own builder
communities**. An agentic treasury on Solana can tap into:
- **Meteora** — dynamic liquidity pools + concentrated LP strategies
- **Orca** — the "concentrated liquidity" DEX, tight-range yield
- **Raydium** — the central AMM + staking/farms
- **+ 30 more routed through Jupiter** (Phoenix, Pump.fun, Jito, etc.)

Every one of these is a place where idle USDC earns yield, and a community our
agents can transact with. That's the edge over EVM: **one Solana wallet reaches
the whole ecosystem through Jupiter**, no bridging between DEXs. This is the
story the grant + Arc demo should lead with.

## What already exists (verified, don't rebuild)
| Piece | Location | Status |
|-------|----------|--------|
| **Jupiter swap leg** | `gentech-treasury/scripts/gta_solana_leg.py` | ✅ LIVE quotes verified (SOL $1→0.0134, TAO $1→0.00505) |
| **Solana bridge adapter** | `10-Labs/AAE-Dry-Powder-Vault/agent/solana_bridge_adapter.py` | ✅ Across Base→Solana USDC |
| **solders + solana-py** | venv | ✅ installed |
| **Yield LP engine** | `gentech-treasury/scripts/yield_lp_engine.py` | ✅ Phase A |
| **Close executor** | `gentech-treasury/scripts/gta_close_executor.py` | ✅ Phase B |
| **Regime gate** | `gentech-treasury/scripts/regime_gate.py` | ✅ Phase C |
| **x402 gateway (multi-chain)** | `10-Labs/x402-gateway/server.py` | ✅ Base + Algorand rails |

## The MVP loop (Solana homebase)
```
Agent earns USDC via x402 (any chain)
        ↓
Bridge USDC → Solana (Across adapter, sub-5s)
        ↓
Treasury deploys USDC on Solana yield (Jupiter/routes)
        ↓
Regime gate decides: accumulate (yield) vs trade (SOL/TAO via Jupiter)
        ↓
Agent pays services from Solana wallet (sub-cent gas)
        ↓
Receipt logged (Q402 trust receipt pattern)
```

## What I'm building now (this session)
1. **Solana homebase orchestrator** — `solana_homebase.py`: ties bridge→deploy→yield→pay
   into one command (mirrors the venue-agnostic engine pattern). DRY_RUN by default.
2. **Verify the bridge adapter imports + quotes** cleanly (web3 present?).
3. **Wire the Solana leg into the treasury allocator** so SOL/TAO is a valid deployment target.
4. **Tranche-2 package** — a README + demo script that shows: live Solana quote → (bridged)
   → on-chain proof. This is the video + repo the grant reviewer sees.

## Funding needed to go LIVE (Jordan, from grant)
- Solana wallet gas: **~$2 SOL** (for Jupiter swaps)
- USDC to deploy: **~$20 USDC on Solana** (bridge from grant)
- Test end-to-end: SOL buy, TAO buy, receipt.

## $200 coding-subscription documentation (tranche-2 requirement)
The grant asks for coding subscription receipts totaling $200. Current stack:
- OpenCode Go $10/mo, Ollama Cloud Pro $20/mo, Nous $20/mo, VPS $42/mo = **~$92/mo**.
- **Need $200 total** — document 2-3 months of these (or add dev tools). Jordan to confirm
  which receipts we can upload. This is the "agentic subscriptions" he flagged.

## Repos for the submission
- `github.com/ProtoJay4789/solana-x402-mvp` (MVP)
- `github.com/ProtoJay4789/x402-gateway` (gateway)
- `github.com/ProtoJay4789/agent-economy-solana` (contracts)
- New: `github.com/ProtoJay4789/solana-homebase` (this orchestrator)

## ♻️ Reusable across the Solana lane (strategic value)
This isn't just a grant deliverable — it's a **reusable submission asset** for
every Solana hackathon:
- **Colosseum Solana hackathon** — next window **Sep 28 – Nov 2, 2026** (2026
  schedule; Frontier was Apr 6–May 11, next is Sep 28–Nov 2). The agentic-treasury-
  on-Solana angle fits the agent/DeFi tracks.
- Other Solana hackathons: any that want Solana-integrated AI agents.
- **Why it compounds:** one Solana Homebase MVP = grant tranche-2 unlock + Arc
  demo + Colosseum entry + a live reference product. Built once, submitted many
  times.

### Watch
- **Colosseum registration** for the Sep 28–Nov 2 window — monitor colosseum.com
  for when registration opens. Jordan registered for Frontier earlier (agent track).
