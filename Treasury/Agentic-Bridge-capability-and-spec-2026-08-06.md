# Agentic Treasury — Cross-Chain Capability Matrix + Agentic Bridge Spec (Aug 6, 2026)

**Source:** Jordan's insight — "the agentic treasury cannot bridge cross-chain; it can
send to my wallet and I convert." Logging what the treasury CAN/CANNOT do, and scoping
the **Agentic Bridge** as a product.

## The three cross-chain things (honest capability map)

| Operation | Treasury CAN do? | Rail | Notes |
|-----------|-----------------|------|-------|
| **Same-chain transfer** | ✅ YES | CDP `transfer()` | Base + Ethereum only (where CDP signs). Confirmed: `transfer(to, amount, token, network)`. |
| **Bridge Base→Solana** | ✅ YES (autonomous) | `solana_bridge_adapter.py` (Across) | Execution-ready, not just dry-run. `depositV3` implemented: approve→SpokePool→deposit→verify receipt. |
| **Bridge Base→Avalanche** | ❌ NO (yet) | — | CDP signs Base/Eth only; no Base→Avax bridge wired. **THIS IS THE GAP.** |
| **Send→user converts→send back** | ✅ YES (manual fallback) | CDP transfer → user EOA | Works for any chain; clunkier. The "learning" moment. |

## The insight (Jordan, verbatim intent)
The treasury is **not chain-native for execution** — it can move money *within* a chain
it signs on, and bridge to chains where we've built a bridge adapter. The product
opportunity: make the treasury **bridge itself**, so "move funds to where the edge is"
is an autonomous act, not a manual wallet hop.

## Why this is a PRODUCT, not just infra
- **Users deposit USDC** → treasury self-manages. If the treasury can't move that USDC
  to the chain where the yield/trade edge lives, it's crippled. Cross-chain mobility IS
  the treasury product.
- **Base→Avalanche is the missing rail.** We have Base→Solana (Across adapter built).
  Avalanche needs: either (a) a native AVX bridge adapter, or (b) Almanak's Safe
  receiving on Avalanche + a Base→Avax USDC bridge.
- **"Portable home chain"** (Jordan, Aug 5) is a selling feature — a treasury that can
  re-home its funds across chains. The bridge is the enabler.

## Agentic Bridge — product shape
- **Core loop:** treasury detects an edge on chain Y → autonomously bridges USDC from
  current home chain X → executes → bridges profit back.
- **Fee model for users (what Jordan asked):** per-bridge fee in USDC, on top of the
  underlying bridge cost. GenTech takes a spread.
- **Underlying bridge providers:** Across (sub-5s, ~0.06-0.10% LP fee + ~0.02% relayer),
  CCTP (Circle, burns/mints — no third-party relayers), deBridge (flat fee, >$50K).

## ⚠️ Native-gas disclaimer (Jordan, Aug 10, 2026) — SHIP THIS
**The bridge moves USDC, NOT native gas.** A bridged USDC landing on a chain with 0 native
gas (AVAX/SOL/ETH) is **stranded** — it cannot pay for the LP entry, swap, or exit tx. This
was a live-verified gap: the AVAX steward wallet sat at 0.000000 AVAX while USDC was ready
to bridge.

**Product rule (must show at/ before bridge time):**
> **"Ensure the destination chain already holds native gas (AVAX/SOL/ETH) to operate."**

**Jordan's operating practice to encode:** keep ~$0.60 native gas buffer on each yield
rail (e.g. ~$0.60 AVAX on Trader Joe) so the rail can always afford entries and exits.
**Self-funding loop is the goal:** once a rail is funded with gas + USDC, the treasury's
yield should be able to top up its own gas going forward — the rail funds itself. Bridge
adapter should (a) check destination native-gas balance before burning, (b) warn if below
the ~$0.60 operating floor, and (c) never claim "ready to trade" on a gas-less destination.

## Real fee data (Across Base→Avalanche route — to verify live)
See the research below. Target: quote `app.across.to/api/suggested-fees` for
Base(8453)→Avalanche(43114), USDC→USDC, to get the actual total cost + time.

## Build path
1. Wire a **Base→Avalanche USDC bridge** (CCTP or Across) — fills the gap.
2. Fold the bridge into the treasury's `bridge()` abstraction (rail-agnostic).
3. Add the **fee-per-bridge** layer for users.
4. Demo it: the treasury moves $X Base→Avalanche, rebalances, reports the full cost.
